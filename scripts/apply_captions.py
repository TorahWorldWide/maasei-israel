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
          "credit_en", "shot_when_en", "caption_long_he", "caption_why_long")


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
    blob = json.dumps(audit, ensure_ascii=False).replace("'", "''")
    run_sql(f"update entries set audit = '{blob}'::jsonb where id = '{row['id']}'")

    back = run_sql(f"select audit->'image_provenance' as p from entries where id = '{row['id']}'")
    wrote = [p.get("caption_he") for p in back[0]["p"]]
    want = [sheet["images"][p["url"].rsplit("/", 1)[-1]].get("caption_he") for p in prov]
    if wrote != want:
        sys.exit("הכתיבה לא נקלטה — הכיתובים במסד אינם מה שנשלח")
    print(f"\nנכתב ואומת: {len(wrote)} כיתובים ב-{row['title'][:50]}")


if __name__ == "__main__":
    main()
