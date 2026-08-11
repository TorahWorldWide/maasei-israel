#!/usr/bin/env python3
"""Fill source_label_en / locator_en on one deed's citations (rule 20).

The sheet maps the exact Hebrew string to its English twin, so the same label
repeated on twenty citations is translated once.

  python3 scripts/apply_citation_en.py docs/enrichment/captions/<id>-citations-en.json [--apply]
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit_claims import run_sql  # noqa: E402

HEBREW = re.compile(r"[֐-׿]")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    sheet = json.load(open(args[0], encoding="utf-8"))
    apply = "--apply" in sys.argv

    rows = run_sql(f"select id, title, citations from entries where id = '{sheet['entry']}'")
    cites = rows[0]["citations"]

    missing = []
    for c in cites:
        for field in ("source_label", "locator"):
            value = (c.get(field) or "").strip()
            if not value or not HEBREW.search(value):
                continue
            english = sheet[field].get(value)
            if not english:
                missing.append(f"{field}: {value}")
                continue
            c[field + "_en"] = english
    if missing:
        sys.exit("אין תרגום בגיליון עבור:\n  " + "\n  ".join(sorted(set(missing))))

    print(f"{len(cites)} ציטוטים תורגמו ב-{rows[0]['title'][:50]}")
    if not apply:
        print("(יבש. הוסף --apply כדי לכתוב)")
        return

    blob = json.dumps(cites, ensure_ascii=False).replace("'", "''")
    run_sql(f"update entries set citations = '{blob}'::jsonb where id = '{rows[0]['id']}'")

    back = run_sql(f"select citations from entries where id = '{rows[0]['id']}'")[0]["citations"]
    left = [c for c in back
            if (HEBREW.search(c.get("source_label") or "") and not (c.get("source_label_en") or "").strip())
            or (HEBREW.search(c.get("locator") or "") and not (c.get("locator_en") or "").strip())]
    if left:
        sys.exit(f"הכתיבה לא נקלטה — {len(left)} ציטוטים עדיין בלי אנגלית")
    print("נכתב ואומת.")


if __name__ == "__main__":
    main()
