#!/usr/bin/env python3
"""
maasei_overview.py — the company's HISTORIAN.

The historian periodically looks at ALL entries and writes the big-picture
"state of the nation" overview: a headline, a narrative, aggregate stats, and a
date range — e.g. "Israel saved ~10,000 lives between 1955 and 2024". It keeps a
changelog and bumps a revision number every time it updates itself.

This script is the historian's HANDS (0 LLM tokens). The thinking (writing the
narrative) is done by the agent; this script just feeds it the corpus and
persists its result.

USAGE
  python3 maasei_overview.py --dump
      → prints ALL entries (title, category, year, act, ripple, source_label,
        citations) as JSON + the CURRENT overview. The agent reads this to write
        the new overview. 0 tokens of its own.

  python3 maasei_overview.py --save '<json>'
      → json = { headline, narrative, stats:{}, date_range, change:"one-line
        summary of what changed this revision" }. Persists it, bumps revision,
        appends {revision, change, at} to the changelog. Prints the saved row.
"""
import json
import os
import sys
import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import maasei_insert as mi  # reuse load_config + run_sql (token-safe)


def esc(s):
    return str(s).replace("'", "''")


def dump(cfg):
    ok, rows = mi.run_sql(
        "select title, description, category, year, act, ripple, source_label, "
        "source_url, citations from entries where status = 'approved' "
        "order by year nulls last, created_at;", cfg)
    entries = rows if (ok and isinstance(rows, list)) else []

    ok2, ov = mi.run_sql(
        "select headline, narrative, stats, date_range, revision, changelog, "
        "updated_at from overview where id = 1;", cfg)
    overview = ov[0] if (ok2 and isinstance(ov, list) and ov) else {}

    # Light aggregate hints (0 tokens) so the agent doesn't have to recompute.
    years = [e["year"] for e in entries if isinstance(e.get("year"), int)]
    by_cat = {}
    for e in entries:
        by_cat[e.get("category", "?")] = by_cat.get(e.get("category", "?"), 0) + 1

    print(json.dumps({
        "entry_count": len(entries),
        "year_min": min(years) if years else None,
        "year_max": max(years) if years else None,
        "by_category": by_cat,
        "current_overview": overview,
        "entries": entries,
    }, ensure_ascii=False))


def save(cfg, payload):
    try:
        data = json.loads(payload)
    except Exception as ex:
        print(json.dumps({"error": f"bad json: {ex}"}, ensure_ascii=False))
        sys.exit(1)

    headline = data.get("headline", "")
    narrative = data.get("narrative", "")
    stats = json.dumps(data.get("stats", {}), ensure_ascii=False)
    date_range = data.get("date_range", "")
    change = data.get("change", "updated overview")
    now = datetime.datetime.utcnow().isoformat() + "Z"

    # Append to changelog and bump revision atomically in SQL.
    sql = f"""
update overview set
  headline   = '{esc(headline)}',
  narrative  = '{esc(narrative)}',
  stats      = '{esc(stats)}'::jsonb,
  date_range = '{esc(date_range)}',
  revision   = revision + 1,
  changelog  = (changelog || jsonb_build_object(
                  'revision', revision + 1,
                  'change', '{esc(change)}',
                  'at', '{esc(now)}')),
  updated_at = now()
where id = 1
returning revision, headline, date_range;
"""
    ok, res = mi.run_sql(sql, cfg)
    if ok and isinstance(res, list):
        print(json.dumps({"saved": True, "row": res[0] if res else None}, ensure_ascii=False))
    else:
        print(json.dumps({"saved": False, "detail": res}, ensure_ascii=False))
        sys.exit(1)


def main():
    cfg = mi.load_config()
    if len(sys.argv) >= 2 and sys.argv[1] == "--dump":
        dump(cfg)
    elif len(sys.argv) >= 3 and sys.argv[1] == "--save":
        save(cfg, sys.argv[2])
    elif len(sys.argv) >= 2 and sys.argv[1] == "--save":
        save(cfg, sys.stdin.read())
    else:
        print("usage: maasei_overview.py --dump | --save '<json>'")
        sys.exit(2)


if __name__ == "__main__":
    main()
