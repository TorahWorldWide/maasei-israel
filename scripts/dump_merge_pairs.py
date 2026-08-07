#!/usr/bin/env python3
"""Dump the plan-4 duplicate groups as compact text for merge review."""
import json
import re
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from audit_claims import run_sql  # noqa: E402

KNOWN = ["9cdfb538", "74f8c8ac", "41f71ed3", "db664bcd", "82e7d021",
         "242965d3", "378c6e2a", "3345051f", "be2c23a1", "dc4981dc"]
HUNTS = ["PillCam", "פילקאם", "קפסול", "Tevel", "תבל", "אפגניסטן", "IsraAID", "איטליה"]


def q(s):
    return "'" + s.replace("'", "''") + "'"


def main():
    cols = run_sql("select column_name from information_schema.columns "
                   "where table_name='entries' order by ordinal_position")
    names = [c["column_name"] for c in cols]
    print("COLUMNS:", ", ".join(names))

    pref = " or ".join(f"id::text like {q(k + '%')}" for k in KNOWN)
    hunt = " or ".join(
        f"title ilike {q('%' + h + '%')} or description ilike {q('%' + h + '%')}"
        for h in HUNTS)
    rows = run_sql(f"select * from entries where ({pref}) or ({hunt}) order by title")
    print(f"ROWS: {len(rows)}\n")
    for r in rows:
        print("=" * 70)
        for k, v in r.items():
            if v in (None, "", [], {}):
                continue
            s = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)
            s = re.sub(r"\s+", " ", s)
            print(f"  {k}: {s}")
    print("=" * 70)


if __name__ == "__main__":
    main()
