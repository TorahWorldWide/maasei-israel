#!/usr/bin/env python3
"""Write completion-pass output into entries — merging, never rebuilding.

The deeds this touches are finished pages. Everything they already carry was
paid for: archived snapshots, image provenance, the pre-image rule 43 compares
against. So this writer reads the row *at the moment it writes*, changes only
the keys its own document owns, and leaves every other key exactly as it found
it. apply_standard_pass.py rebuilds `audit` from the document and is right to —
it writes pages built from scratch. Running it over a finished page rolls the
archive back (lesson 28ג).

  python3 scripts/apply_completion.py                    # dry-run
  python3 scripts/apply_completion.py --apply --ids <id>
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_claims import run_sql  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = Path("/tmp/completion-out")
BLIND = Path("/tmp/blind")
BACKUPS = ROOT / "docs" / "enrichment" / "backups"
UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")

# Text the worker may rewrite — and only when rule 148 or rule 20 forces it.
TEXT_FIELDS = [
    "title", "title_en", "summary_short", "summary_short_en",
    "description", "description_en", "act", "act_en", "ripple", "ripple_en",
    "origin_story", "origin_story_en", "aftermath", "aftermath_en",
    "recognition", "recognition_en",
]
# audit keys this pass owns. Everything else in audit is somebody else's work.
AUDIT_KEYS = ["state", "the_moment", "discrepancies", "unresolved", "missing",
              "tried", "adversarial_review"]


def lit(value):
    if value is None:
        return "NULL"
    return "'" + str(value).replace("'", "''") + "'"


def jsonb(value):
    return lit(json.dumps(value, ensure_ascii=False)) + "::jsonb"


def merge_citations(existing, incoming):
    """New sources join; a source already on the page keeps what was paid for.

    archived_url is the expensive one — it costs a routed run through Tomer's
    PC — and a worker that re-lists a citation never has it."""
    by_url = {c.get("source_url"): dict(c) for c in existing if c.get("source_url")}
    # One record per source — `by_url` already collapses a repeated url into a
    # single record, so a repeated url in `order` re-emitted the same citation
    # again and again, and the page showed a wall of identical quotes.
    order = list(dict.fromkeys(c.get("source_url") for c in existing
                               if c.get("source_url")))
    for cite in incoming or []:
        url = cite.get("source_url")
        if not url:
            continue
        if url in by_url:
            kept = by_url[url]
            for key, value in cite.items():
                if value and key != "archived_url":
                    kept[key] = value
        else:
            by_url[url] = dict(cite)
            order.append(url)
    return [by_url[u] for u in order]


CAPTION_KEYS = ("caption_he", "caption_en", "caption_long_he", "caption_long_en")


def merge_provenance(existing, blind, captions=None):
    """Rule 149 — the blind description lands beside the image it describes.

    Captions ride along because much of what the adversarial review returns is a
    caption claiming more than its frame holds, and the worker sent to fix one
    must not have to rewrite the provenance record around it."""
    fixed = {c.get("url"): c for c in (captions or []) if c.get("url")}
    out = []
    for item in existing:
        item = dict(item)
        record = blind.get(item.get("url"))
        if record:
            item["image_seen"] = record
        for key, value in (fixed.get(item.get("url")) or {}).items():
            if key in CAPTION_KEYS and value:
                item[key] = value
        out.append(item)
    return out


def merged(doc, row):
    """The row as it will look after the merge — plain Python, no SQL.

    Scoring this before the UPDATE is what turns the dry-run into a real gate:
    a worker whose `numbers` are shaped wrong is caught here, not by a read-back
    taken after the write already landed on a live page."""
    out = dict(row)
    for field, value in owned(doc, row).items():
        out[field] = value
    return out


def owned(doc, row):
    """Only the columns this pass owns, with their merged values."""
    cols = {}
    for field in TEXT_FIELDS:
        if doc.get(field) and doc[field] != row.get(field):
            cols[field] = doc[field]

    if doc.get("numbers") is not None:
        cols["numbers"] = doc["numbers"]
    if doc.get("honors") is not None:
        cols["honors"] = doc["honors"]
    if doc.get("citations"):
        cols["citations"] = merge_citations(row.get("citations") or [],
                                            doc["citations"])

    audit = dict(row.get("audit") or {})
    for key in AUDIT_KEYS:
        if doc.get(key) is not None:
            audit[key] = doc[key]
    # A correction is a record, not a state: append, never replace.
    if doc.get("corrections"):
        audit["corrections"] = (audit.get("corrections") or []) + doc["corrections"]

    blind_path = BLIND / f"{doc['id']}.json"
    blind = json.loads(blind_path.read_text()) if blind_path.exists() else {}
    if blind or doc.get("captions"):
        audit["image_provenance"] = merge_provenance(
            audit.get("image_provenance") or [], blind, doc.get("captions"))

    audit["completion_pass"] = {
        "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "by": "completion-pass/opus-5",
        "rules": doc.get("rules_closed") or [148, 149, 150, 151, 157],
    }
    cols["audit"] = audit
    return cols


def build_update(doc, row):
    return {col: (jsonb(value) if isinstance(value, (dict, list)) else lit(value))
            for col, value in owned(doc, row).items()}


def load_docs(ids, out=None):
    docs = []
    for path in sorted((out or OUT).glob("*.json")):
        if not UUID.match(path.stem):  # a worker's scratch file is not a deed
            continue
        doc = json.loads(path.read_text())
        doc["id"] = path.stem  # the file name is the deed, not a key inside it
        if ids and doc["id"] not in ids:
            continue
        docs.append(doc)
    return docs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--ids", nargs="*")
    ap.add_argument("--dir", help="worker documents to read (default /tmp/completion-out)")
    args = ap.parse_args()

    out = Path(args.dir) if args.dir else OUT
    docs = load_docs(args.ids, out)
    if not docs:
        sys.exit(f"no completion documents in {out}")

    ids = ",".join(lit(d["id"]) for d in docs)
    rows = {r["id"]: r for r in run_sql(f"SELECT * FROM entries WHERE id IN ({ids})")}

    if not args.apply:
        from deed_standard import AUTO_RULES, evaluate  # noqa: E402
        for doc in docs:
            row = rows.get(doc["id"])
            if not row:
                print(f"SKIP {doc['id']} — not in database")
                continue
            before = [n for n in AUTO_RULES if not evaluate(row).get(n)]
            after = [n for n in AUTO_RULES if not evaluate(merged(doc, row)).get(n)]
            total = len(AUTO_RULES)
            print(f"\n{row.get('title')}  [{doc['id'][:8]}]")
            print(f"   {total-len(before)}/{total} -> {total-len(after)}/{total}"
                  + (f"  עדיין נכשל: {after}" if after else "  — יעבור הכל"))
            print(f"   {', '.join(sorted(owned(doc, row)))}")
        print(f"\ndry-run — {len(docs)} deeds. Re-run with --apply")
        return

    BACKUPS.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = BACKUPS / f"pre-completion-{stamp}.json"
    backup.write_text(json.dumps(list(rows.values()), ensure_ascii=False, indent=2))
    print(f"backup: {backup.relative_to(ROOT)} ({len(rows)} rows)")

    written = []
    for doc in docs:
        # Read again, now. Between the dry run and here, night_archive may have
        # filled archived_url; the row above is already a photograph of the past.
        fresh = run_sql(f"SELECT * FROM entries WHERE id = {lit(doc['id'])}")
        if not fresh:
            print(f"SKIP {doc['id']} — not in database")
            continue
        sets = build_update(doc, fresh[0])
        assignments = ", ".join(f"{col} = {val}" for col, val in sets.items())
        run_sql(f"UPDATE entries SET {assignments} WHERE id = {lit(doc['id'])};")
        written.append(doc["id"])
        print(f"written: {fresh[0].get('title')}")

    from deed_standard import AUTO_RULES, evaluate  # noqa: E402
    print(f"\n{len(written)} deeds written. Read-back:")
    ids = ",".join(lit(i) for i in written)
    for row in run_sql(f"SELECT * FROM entries WHERE id IN ({ids})"):
        result = evaluate(row)
        failed = [n for n in AUTO_RULES if not result.get(n)]
        print(f"  {row['title'][:58]}  {len(AUTO_RULES)-len(failed)}/{len(AUTO_RULES)}"
              + (f"  נכשל: {failed}" if failed else "  — עובר הכל"))


if __name__ == "__main__":
    main()
