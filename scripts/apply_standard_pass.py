#!/usr/bin/env python3
"""Write standard-pass worker output (/tmp/enrich-out/<id>.json) into entries.

Workers never touch the database; they emit JSON. This is the only writer.

  python3 scripts/apply_standard_pass.py              # dry-run: show the diff
  python3 scripts/apply_standard_pass.py --apply      # back up, then write
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_claims import run_sql  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = Path("/tmp/enrich-out")
BACKUPS = ROOT / "docs" / "enrichment" / "backups"

TEXT_FIELDS = [
    "source_url", "source_label", "source_label_en", "actor_type",
    "title", "title_en", "title_reasoning", "year",
    "description", "description_en", "act", "act_en", "ripple", "ripple_en",
    "origin_story", "origin_story_en", "aftermath", "aftermath_en",
    "recognition", "recognition_en", "summary_short", "summary_short_en",
]
ARRAY_FIELDS = ["deed_type", "beneficiary"]

# Copied into audit.pre before the write, so rule 43 can prove the text moved.
PRE_FIELDS = ["title", "description", "act", "ripple", "source_url", "media_url"]


def lit(value):
    if value is None:
        return "NULL"
    return "'" + str(value).replace("'", "''") + "'"


def jsonb(value):
    return lit(json.dumps(value, ensure_ascii=False)) + "::jsonb"


def text_array(values):
    inner = ",".join(lit(v) for v in values)
    return f"ARRAY[{inner}]::text[]" if values else "NULL"


def build_update(doc, row):
    """Map a worker document onto entries columns."""
    sets = {}

    for f in TEXT_FIELDS:
        if doc.get(f):
            sets[f] = lit(doc[f])

    for f in ("citations", "honors", "dedup"):
        if doc.get(f) is not None:
            sets[f] = jsonb(doc[f])

    # media_urls is jsonb holding a flat array of URL strings — the site reads it
    # as string[], so provenance objects go to audit instead of inline here.
    # A worker that filled image_provenance and left media_urls empty vetted nine
    # images and published none of them. The provenance list is the gallery, so
    # take it rather than write a page with no pictures.
    gallery = doc.get("media_urls") or [
        p for p in doc.get("image_provenance") or [] if p.get("url")]
    images = [m["url"] if isinstance(m, dict) else m for m in gallery]
    videos = [v["url"] for v in doc.get("videos") or [] if v.get("url")]
    if images or videos:
        sets["media_urls"] = jsonb(images + videos)
    if images:
        sets["media_url"] = lit(images[0])
        sets["media_type"] = lit("image")

    for f in ("location", "people"):
        if doc.get(f):
            sets[f] = jsonb(doc[f])

    for f in ARRAY_FIELDS:
        if doc.get(f):
            sets[f] = text_array(doc[f])

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    audit = {
        "state": doc.get("status") or "unknown",
        "at": now,
        "by": "standard-pass/opus-5",
        "checked": doc.get("tried") or [],
        "tried": doc.get("tried") or [],
        "unresolved": doc.get("unresolved") or [],
        "missing": doc.get("missing") or [],
        "corrections": doc.get("corrections") or [],
        "image_provenance": doc.get("image_provenance") or [],
        "videos": doc.get("videos") or [],
        "domains_covered": doc.get("domains_covered"),
        # the new standard fields
        "rebuild": {"from_scratch": True, "at": now, "by": "standard-pass/opus-5"},
        # The first write captures the pre-image; later corrections must not
        # overwrite it, or rule 43 would compare the new text against itself.
        "pre": (row.get("audit") or {}).get("pre") or {f: row.get(f) for f in PRE_FIELDS},
        "content_delta": doc.get("content_delta") or [],
        "removed": doc.get("removed") or [],
        "disputes": doc.get("disputes") or [],
        "lead_image_basis": doc.get("lead_image_basis"),
        "spinoff_leads": doc.get("spinoff_leads") or [],
        "redirects": doc.get("redirects") or [],
        "person_notes": doc.get("person_notes") or [],
        # Rule 139: an empty list means the worker looked; a missing key does not.
        "sensitive_claims": doc.get("sensitive_claims") or [],
        "merged_from": doc.get("merged_from") or [],
        "notes": doc.get("notes"),
    }
    sets["audit"] = jsonb(audit)
    return sets


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--ids", nargs="*", help="limit to these deed ids")
    args = ap.parse_args()

    docs = []
    for path in sorted(OUT.glob("*.json")):
        doc = json.loads(path.read_text())
        if not doc.get("id"):
            continue
        if args.ids and doc["id"] not in args.ids:
            continue
        # Only documents from the standard pass carry the new columns.
        if not any(doc.get(f) for f in ("location", "people", "deed_type")):
            continue
        docs.append(doc)

    if not docs:
        sys.exit("no standard-pass documents found in /tmp/enrich-out")

    ids = ",".join(lit(d["id"]) for d in docs)
    rows = {r["id"]: r for r in run_sql(f"SELECT * FROM entries WHERE id IN ({ids})")}

    plans = []
    for doc in docs:
        row = rows.get(doc["id"])
        if not row:
            print(f"SKIP {doc['id']} — not in database")
            continue
        sets = build_update(doc, row)
        plans.append((doc["id"], row.get("title"), sets))
        print(f"\n{row.get('title')}  [{doc['id'][:8]}]")
        for col in sorted(sets):
            before = row.get(col)
            size = len(before) if isinstance(before, (list, dict)) else ("set" if before else "empty")
            print(f"   {col:<16} was: {size}")

    if not args.apply:
        print(f"\ndry-run — {len(plans)} deeds would be written. Re-run with --apply")
        return

    BACKUPS.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = BACKUPS / f"pre-standard-pass-{stamp}.json"
    backup.write_text(json.dumps(list(rows.values()), ensure_ascii=False, indent=2))
    print(f"\nbackup: {backup.relative_to(ROOT)} ({len(rows)} rows)")

    for deed_id, title, sets in plans:
        assignments = ", ".join(f"{col} = {val}" for col, val in sets.items())
        run_sql(f"UPDATE entries SET {assignments} WHERE id = {lit(deed_id)};")
        print(f"written: {title}")

    # Rule 125: a write is not done until it has been read back.
    from deed_standard import AUTO_RULES, evaluate  # noqa: E402

    print(f"\n{len(plans)} deeds written. Read-back:")
    written = ",".join(lit(deed_id) for deed_id, _, _ in plans)
    for row in run_sql(f"SELECT * FROM entries WHERE id IN ({written})"):
        result = evaluate(row)
        failed = [n for n in AUTO_RULES if not result.get(n)]
        ok = len(AUTO_RULES) - len(failed)
        print(f"  {row['title'][:60]}  {ok}/{len(AUTO_RULES)}"
              + (f"  נכשל: {failed}" if failed else "  — עובר הכל"))


if __name__ == "__main__":
    main()
