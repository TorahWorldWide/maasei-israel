#!/usr/bin/env python3
"""Dump the nine plan-4 duplicate groups to /tmp/merge-rows/<n>_<slug>.json."""
import json
import os
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from audit_claims import run_sql  # noqa: E402

GROUPS = [
    (1, "yad-sarah", "9cdfb538", "74f8c8ac"),
    (2, "ezer-mizion", "41f71ed3", "db664bcd"),
    (3, "ihud-hatzala", "242965d3", "82e7d021"),
    (4, "zichron-menachem", "3345051f", "378c6e2a"),
    (5, "zaka", "dc4981dc", "be2c23a1"),
    (6, "pillcam", "c1bab11d", "9c2cdce3"),
    (7, "tevel", "3426ff78", "991fe9d2"),
    (8, "israaid-afghanistan", "e6b2739c", "65705b8c"),
    (9, "israaid-italy", "5aab0fea", "310fc0e4"),
]

OUT = "/tmp/merge-rows"


def fetch(prefix):
    rows = run_sql(f"select * from entries where id::text like '{prefix}%'")
    if not isinstance(rows, list) or len(rows) != 1:
        raise SystemExit(f"expected exactly 1 row for {prefix}, got {rows!r}")
    return rows[0]


def main():
    os.makedirs(OUT, exist_ok=True)
    for n, slug, survivor, doomed in GROUPS:
        payload = {
            "group": n,
            "slug": slug,
            "survivor_id_prefix": survivor,
            "doomed_id_prefix": doomed,
            "survivor": fetch(survivor),
            "doomed": fetch(doomed),
        }
        path = f"{OUT}/{n}_{slug}.json"
        with open(path, "w") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
