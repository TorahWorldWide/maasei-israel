#!/usr/bin/env python3
"""Stage-0 migration for DEED-STANDARD.md: add the seven missing columns.

Additive only (ADD COLUMN IF NOT EXISTS) — no data is touched. Goes through the
Supabase Management API because PostgREST+anon returns fake-success on writes.
Verifies by reading information_schema back AND fetching one row via PostgREST.

  python3 scripts/migrate_standard_columns.py           # dry-run: show plan + current schema
  python3 scripts/migrate_standard_columns.py --apply   # run migration + verify
"""
import json
import sys

sys.path.insert(0, __import__("os").path.dirname(__file__))
from audit_claims import run_sql  # noqa: E402

# Shapes match what scripts/deed_standard.py evaluates:
#   27 location jsonb {country,city,lat,lng,precision}
#   28 audit    jsonb {state,at,by,checked[],unresolved[]}
#   37 people   jsonb [{name_he,name_en},...]
#   38 deed_type   text[]  (closed list, one or more)
#   39 actor_type  text    (single value)
#   40 beneficiary text[]  (one or more)
#      dedup    jsonb   (title/keyword fingerprint for the approval screen)
COLUMNS = [
    ("location", "jsonb"),
    ("people", "jsonb"),
    ("deed_type", "text[]"),
    ("actor_type", "text"),
    ("beneficiary", "text[]"),
    ("audit", "jsonb"),
    ("dedup", "jsonb"),
]

MIGRATION = "ALTER TABLE public.entries\n  " + ",\n  ".join(
    f"ADD COLUMN IF NOT EXISTS {name} {typ}" for name, typ in COLUMNS
) + ";"

SCHEMA_SQL = (
    "SELECT column_name, data_type FROM information_schema.columns "
    "WHERE table_schema='public' AND table_name='entries' ORDER BY ordinal_position;"
)


def main():
    apply = "--apply" in sys.argv

    before = run_sql(SCHEMA_SQL)
    have = {c["column_name"] for c in before}
    missing = [n for n, _ in COLUMNS if n not in have]
    count = run_sql("SELECT count(*) AS n FROM public.entries;")[0]["n"]
    print(f"rows: {count}")
    print(f"columns now: {len(have)}; missing standard columns: {missing or 'none'}")

    if not apply:
        print("\n-- dry-run. SQL that --apply would run:\n" + MIGRATION)
        return

    if not missing:
        print("nothing to do")
        return

    run_sql(MIGRATION)

    after = {c["column_name"] for c in run_sql(SCHEMA_SQL)}
    still = [n for n, _ in COLUMNS if n not in after]
    count2 = run_sql("SELECT count(*) AS n FROM public.entries;")[0]["n"]
    if still:
        sys.exit(f"FAILED — columns still missing after migration: {still}")
    if count2 != count:
        sys.exit(f"FAILED — row count changed {count} -> {count2}")
    print(f"OK — all {len(COLUMNS)} columns present, row count unchanged ({count2})")


if __name__ == "__main__":
    main()
