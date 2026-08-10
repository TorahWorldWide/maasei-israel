#!/usr/bin/env python3
"""Dump per-deed DB rows and build the risk-ordered queue for the standard pass.

Queue order = data/audit/claims.json (risk desc). Deeds that already have an
enrichment output (/tmp/enrich-out/*.json or applied/) move to the END of the
queue — they only need a metadata top-up, not a fresh harvest.

  python3 scripts/verify/dump_enrich_rows.py            # dump rows + queue
  python3 scripts/verify/dump_enrich_rows.py --topup    # re-dump only the done ones (fresh rows)
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from audit_claims import run_sql  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
CLAIMS = os.path.join(ROOT, "data", "audit", "claims.json")
IN_DIR = "/tmp/enrich-in"
QUEUE = "/tmp/enrich-queue.txt"


def done_ids():
    out = set()
    for pat in ("/tmp/enrich-out/*.json", "/tmp/enrich-out/applied/*.json"):
        for f in glob.glob(pat):
            out.add(os.path.basename(f)[:-5])
    return out


def main():
    topup_only = "--topup" in sys.argv
    order = [e["id"] for e in json.load(open(CLAIMS))["entries"]]
    done = done_ids()

    rows = {r["id"]: r for r in run_sql("select * from public.entries;")}
    os.makedirs(IN_DIR, exist_ok=True)

    ids = [i for i in order if i in done] if topup_only else order
    dumped = 0
    for i in ids:
        if i not in rows:
            print(f"!! {i} in claims but not in DB — skipped")
            continue
        with open(os.path.join(IN_DIR, f"{i}.json"), "w") as f:
            json.dump(rows[i], f, ensure_ascii=False, indent=1, default=str)
        dumped += 1

    if not topup_only:
        fresh = [i for i in order if i not in done and i in rows]
        topup = [i for i in order if i in done and i in rows]
        with open(QUEUE, "w") as f:
            f.write("\n".join(fresh + topup) + "\n")
        print(f"queue: {len(fresh)} fresh + {len(topup)} top-up -> {QUEUE}")
    print(f"rows dumped: {dumped} -> {IN_DIR}")


if __name__ == "__main__":
    main()
