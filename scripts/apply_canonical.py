#!/usr/bin/env python3
"""Write a canonical page document (rule 166) into entries.

The standard-pass applier only accepts documents carrying location/people/
deed_type, which a canonical rewrite does not touch — it rewrites prose. This
writes the prose columns plus the three that rules 168-169 added: sections,
infobox, canonical_type.

  python3 scripts/apply_canonical.py docs/.../canonical-lamarr.json
  python3 scripts/apply_canonical.py <path> --apply
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apply_standard_pass import jsonb, lit  # noqa: E402
from audit_claims import run_sql  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BACKUPS = ROOT / "docs" / "enrichment" / "backups"

TEXT_FIELDS = [
    "title", "title_en", "description", "description_en",
    "origin_story", "origin_story_en", "act", "act_en",
    "ripple", "ripple_en", "aftermath", "aftermath_en",
    "recognition", "recognition_en", "summary_short", "summary_short_en",
    "canonical_type", "canonical_type_en",
]
JSON_FIELDS = ["sections", "infobox", "honors"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    doc = json.loads(Path(args.path).read_text())
    deed_id = doc.get("deed_id") or doc.get("id")
    if not deed_id:
        sys.exit("document has no deed_id")

    rows = run_sql(f"SELECT * FROM entries WHERE id = {lit(deed_id)}")
    if not rows:
        sys.exit(f"{deed_id} is not in the database")
    row = rows[0]

    sets = {}
    for f in TEXT_FIELDS:
        if doc.get(f):
            sets[f] = lit(doc[f])
    for f in JSON_FIELDS:
        if doc.get(f) is not None:
            sets[f] = jsonb(doc[f])

    # canonical_type is one column, and rule 166 names the types in Hebrew.
    sets.pop("canonical_type_en", None)

    audit = dict(row.get("audit") or {})
    audit["canonical"] = {
        "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "by": doc.get("written_by") or "canonical/opus-5",
        "type": doc.get("canonical_type"),
        "sections": len(doc.get("sections") or []),
        "infobox_rows": len((doc.get("infobox") or {}).get("rows") or []),
    }
    sets["audit"] = jsonb(audit)

    print(f"{row.get('title')}  [{deed_id[:8]}]")
    for col in sorted(sets):
        before = row.get(col)
        size = len(before) if isinstance(before, (list, dict, str)) else ("set" if before else "empty")
        print(f"   {col:<20} was: {size}")

    if not args.apply:
        print("\ndry-run — re-run with --apply")
        return

    BACKUPS.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = BACKUPS / f"pre-canonical-{deed_id[:8]}-{stamp}.json"
    backup.write_text(json.dumps(row, ensure_ascii=False, indent=2))
    print(f"\nbackup: {backup.relative_to(ROOT)}")

    assignments = ", ".join(f"{col} = {val}" for col, val in sets.items())
    run_sql(f"UPDATE entries SET {assignments} WHERE id = {lit(deed_id)};")

    # Rule 125: a write is not done until it has been read back.
    after = run_sql(f"SELECT * FROM entries WHERE id = {lit(deed_id)}")[0]
    from deed_standard import AUTO_RULES, evaluate  # noqa: E402

    result = evaluate(after)
    failed = [n for n in AUTO_RULES if not result.get(n)]
    print(f"sections: {len(after.get('sections') or [])} · "
          f"infobox rows: {len((after.get('infobox') or {}).get('rows') or [])} · "
          f"canonical_type: {after.get('canonical_type')}")
    print(f"{len(AUTO_RULES) - len(failed)}/{len(AUTO_RULES)} AUTO"
          + (f"  נכשל: {failed}" if failed else "  — עובר הכל"))


if __name__ == "__main__":
    main()
