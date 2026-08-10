#!/usr/bin/env python3
"""Two caption defects Tomer caught by eye on the 2026-08-10 pilot.

1. Key drift: three agents wrote the caption under three different names
   (`caption_he`, `note`, nothing). The site reads `caption_he`, so two entries
   rendered "ללא כיתוב" even though the text existed. Normalise `note` in.
2. Doña Gracia: Gracianasimedal.jpg and Nezi.jpg are the same Pastorino medal —
   the 1908 engraving is a line copy of it. One was captioned as the niece with
   a warning, the other as the heroine with none. Both depict the niece.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit_claims import run_sql  # noqa: E402

GRACIA = "81bfe740-07d5-4bea-860d-03cb8f27dc68"
NO_PORTRAIT = "לא דיוקן מאומת של דונה גרסיה — לא ידוע על דיוקן מהחיים שלה עצמה."

GRACIA_FIX = {
    "Gracianasimedal.jpg": {
        "caption_he": "מדליית ארד, איטליה של המאה ה-16 (מיוחסת לפסטורינו דה' פסטוריני). "
                      "הכתובת מימין — A·Æ·XVIII — אומרת שהמצולמת בת 18, ולכן זו גרציה נשיא "
                      "הצעירה, אחייניתה וכלתה של דונה גרסיה, ולא דונה גרסיה עצמה שהייתה אז "
                      "כבת ארבעים.",
        "warning": NO_PORTRAIT,
    },
    "Nezi.jpg": {
        "caption_he": "תחריט קו מספר היסטוריה משנת 1908 — העתק מצויר של אותה מדליה בדיוק: "
                      "אותו פרופיל שמאלה, אותה מסגרת חרוזים, אותה כתובת עברית ואותו A·Æ·XVIII. "
                      "לכן גם הוא מתאר את גרציה נשיא הצעירה.",
        "warning": NO_PORTRAIT,
    },
}


def main():
    apply = "--apply" in sys.argv
    rows = run_sql("select id, title, audit from entries where audit ? 'image_provenance'")
    for row in rows:
        prov = row["audit"]["image_provenance"]
        changed = []
        for photo in prov:
            fname = photo["url"].rsplit("/", 1)[-1]
            if "note" in photo and "caption_he" not in photo:
                photo["caption_he"] = photo.pop("note")
                changed.append(f"{fname}: note→caption_he")
            if row["id"] == GRACIA and fname in GRACIA_FIX:
                photo.update(GRACIA_FIX[fname])
                changed.append(f"{fname}: כיתוב מתוקן (אותה מדליה)")
        if not changed:
            print(f"= {row['title'][:45]} — ללא שינוי")
            continue
        print(f"~ {row['title'][:45]}")
        for c in changed:
            print(f"    {c}")
        if apply:
            audit = dict(row["audit"], image_provenance=prov)
            blob = json.dumps(audit, ensure_ascii=False).replace("'", "''")
            run_sql(f"update entries set audit = '{blob}'::jsonb where id = '{row['id']}'")

    missing = [r["title"] for r in rows
               if any("caption_he" not in p and "note" not in p
                      for p in r["audit"]["image_provenance"])]
    if missing:
        print("\nעדיין ללא כיתוב בכלל (התקן לא דרש אותו):")
        for t in missing:
            print("  -", t[:60])
    if not apply:
        print("\n(יבש. הוסף --apply כדי לכתוב)")


if __name__ == "__main__":
    main()
