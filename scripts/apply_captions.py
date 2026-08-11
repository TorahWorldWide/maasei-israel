#!/usr/bin/env python3
"""Apply a caption sheet to one deed's audit.image_provenance.

A sheet lives in docs/enrichment/captions/<entry-id>.json and is keyed by the
image's file name — the URLs are long and easy to mistype, the file name is not.

  python3 scripts/apply_captions.py docs/enrichment/captions/<id>.json
  python3 scripts/apply_captions.py docs/enrichment/captions/<id>.json --apply
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit_claims import run_sql  # noqa: E402

FIELDS = ("caption_he", "caption_en", "group", "group_en",
          "credit", "credit_en", "shot_when", "shot_when_en",
          "caption_long_he", "caption_why_long", "license", "license_note")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    sheet = json.load(open(args[0], encoding="utf-8"))
    apply = "--apply" in sys.argv

    rows = run_sql(f"select id, title, audit from entries where id = '{sheet['entry']}'")
    if not rows:
        sys.exit("אין מעש כזה: " + sheet["entry"])
    row = rows[0]
    prov = row["audit"]["image_provenance"]

    unseen = set(sheet["images"])
    for photo in prov:
        fname = photo["url"].rsplit("/", 1)[-1]
        patch = sheet["images"].get(fname)
        if patch is None:
            print(f"  ! ללא עדכון בגיליון: {fname[:70]}")
            continue
        unseen.discard(fname)
        for field in FIELDS:
            if field in patch:
                photo[field] = patch[field]
        print(f"  ~ {patch.get('caption_he', '')[:60]}")

    if unseen:
        sys.exit("שורות בגיליון שאין להן תמונה בדף: " + ", ".join(unseen))

    if not apply:
        print("\n(יבש. הוסף --apply כדי לכתוב)")
        return

    audit = dict(row["audit"], image_provenance=prov)
    # Rule 139 travels with the sheet: the same worker that looked at the page
    # is the one that can say whether it makes a sensitive claim about a living
    # person. An empty list is an answer; a missing key is not, so only a key
    # that is actually present overwrites what is there.
    if "sensitive_claims" in sheet:
        audit["sensitive_claims"] = sheet["sensitive_claims"]
    for key in ("unresolved", "missing", "tried"):
        if key in sheet:
            audit[key] = sheet[key]
    # "archive_failed:<url>" is the archiver's record of a page the Wayback
    # Machine refused, and rule 136 reads it as the naming it asks for. A caption
    # worker never sees it and would drop it by simply not repeating it.
    kept = [u for u in (row["audit"].get("unresolved") or [])
            if isinstance(u, str) and u.startswith("archive_failed:")]
    audit["unresolved"] = list(audit.get("unresolved") or []) + [
        u for u in kept if u not in (audit.get("unresolved") or [])]
    blob = json.dumps(audit, ensure_ascii=False).replace("'", "''")
    run_sql(f"update entries set audit = '{blob}'::jsonb where id = '{row['id']}'")

    back = run_sql(f"select audit->'image_provenance' as p from entries where id = '{row['id']}'")
    checked = 0
    for wrote, photo in zip(back[0]["p"], prov):
        patch = sheet["images"].get(photo["url"].rsplit("/", 1)[-1]) or {}
        for field in FIELDS:
            if field in patch:
                checked += 1
                if wrote.get(field) != patch[field]:
                    sys.exit(f"הכתיבה לא נקלטה — {field} במסד אינו מה שנשלח")
    print(f"\nנכתב ואומת: {checked} שדות ב-{row['title'][:50]}")


if __name__ == "__main__":
    main()
