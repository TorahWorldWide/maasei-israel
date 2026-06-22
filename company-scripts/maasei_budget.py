#!/usr/bin/env python3
"""
maasei_budget.py — the company's TOKEN/COST GOVERNOR (0 LLM tokens).

Tomer's hard rule: no limit on how many videos a shift adds, but a FIRM limit on
how many tokens it burns. The expensive operations in a shift are LLM-driven web
searches / page reads. This script does two jobs:

  1. Records each shift (timestamp, calls used, items added) to a local JSON log
     so cadence and spend are visible over time — and so a runaway pattern (many
     shifts in one day) is detectable.

  2. Tells a shift, at the very start, whether it is allowed to run AND what its
     call budget is — enforcing both a per-shift ceiling and a per-day ceiling.
     If today's shifts already used the daily budget, it says STOP so the cron
     burns ~0 tokens that day.

The actual token discipline inside a shift is enforced by the prompt (count your
web_search/web_extract calls, stop at the budget). This script is the persistent
memory + the gate that the prompt checks first.

LOG: ~/.hermes/maasei_company/shiftlog.json
  { "per_shift_call_budget": 18,
    "per_day_call_budget": 40,
    "shifts": [ {at, calls, added, note}, ... ] }

USAGE (0 LLM tokens)
  python3 maasei_budget.py --gate
      → prints {"allow": bool, "shift_budget": N, "day_used": M, "day_budget": K,
                "reason": "..."}. The shift reads this FIRST. allow=false => the
        shift should stop immediately (respond [SILENT]).

  python3 maasei_budget.py --record '<json>'
      → json = {calls:int, added:int, note?}. Append a shift record. Call this
        at the END of a shift so tomorrow's gate sees today's spend.

  python3 maasei_budget.py --report [--days 7]
      → human summary: shifts, total calls, total items added over N days.

  python3 maasei_budget.py --set '<json>'
      → adjust budgets, e.g. {"per_shift_call_budget":25,"per_day_call_budget":60}.
"""
import argparse
import datetime
import json
import os
import sys

LOG = os.path.expanduser("~/.hermes/maasei_company/shiftlog.json")
DEFAULTS = {"per_shift_call_budget": 18, "per_day_call_budget": 40, "shifts": []}


def load():
    try:
        with open(LOG) as f:
            d = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        d = {}
    for k, v in DEFAULTS.items():
        d.setdefault(k, v if not isinstance(v, list) else [])
    return d


def save(d):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    tmp = LOG + ".tmp"
    with open(tmp, "w") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    os.replace(tmp, LOG)


def _today_utc():
    return datetime.datetime.utcnow().strftime("%Y-%m-%d")


def calls_used_today(d):
    today = _today_utc()
    return sum(int(s.get("calls", 0)) for s in d["shifts"]
               if str(s.get("at", "")).startswith(today))


def gate(d):
    day_used = calls_used_today(d)
    day_budget = int(d["per_day_call_budget"])
    shift_budget = int(d["per_shift_call_budget"])
    remaining_today = max(0, day_budget - day_used)
    if remaining_today <= 0:
        out = {"allow": False, "shift_budget": 0, "day_used": day_used,
               "day_budget": day_budget,
               "reason": "daily call budget already spent — stop, respond [SILENT]"}
    else:
        out = {"allow": True,
               "shift_budget": min(shift_budget, remaining_today),
               "day_used": day_used, "day_budget": day_budget,
               "reason": "ok"}
    print(json.dumps(out, ensure_ascii=False))
    return 0 if out["allow"] else 1


def record(d, payload):
    rec = json.loads(payload)
    d["shifts"].append({
        "at": datetime.datetime.utcnow().isoformat() + "Z",
        "calls": int(rec.get("calls", 0)),
        "added": int(rec.get("added", 0)),
        "note": rec.get("note", ""),
    })
    # keep the log bounded
    d["shifts"] = d["shifts"][-500:]
    save(d)
    print(json.dumps({"recorded": True, "total_shifts": len(d["shifts"])},
                     ensure_ascii=False))
    return 0


def report(d, days):
    cutoff = (datetime.datetime.utcnow() - datetime.timedelta(days=days))
    recent = [s for s in d["shifts"]
              if s.get("at", "") >= cutoff.isoformat()]
    print(json.dumps({
        "window_days": days,
        "shifts": len(recent),
        "total_calls": sum(int(s.get("calls", 0)) for s in recent),
        "total_added": sum(int(s.get("added", 0)) for s in recent),
        "per_shift_call_budget": d["per_shift_call_budget"],
        "per_day_call_budget": d["per_day_call_budget"],
    }, ensure_ascii=False))
    return 0


def set_budgets(d, payload):
    upd = json.loads(payload)
    for k in ("per_shift_call_budget", "per_day_call_budget"):
        if k in upd:
            d[k] = int(upd[k])
    save(d)
    print(json.dumps({"per_shift_call_budget": d["per_shift_call_budget"],
                      "per_day_call_budget": d["per_day_call_budget"]},
                     ensure_ascii=False))
    return 0


def main():
    ap = argparse.ArgumentParser(description="Maasei Israel token/cost governor")
    ap.add_argument("--gate", action="store_true")
    ap.add_argument("--record", metavar="JSON")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--set", dest="set_", metavar="JSON")
    args = ap.parse_args()
    d = load()
    if args.gate:
        sys.exit(gate(d))
    if args.record is not None:
        sys.exit(record(d, args.record))
    if args.report:
        sys.exit(report(d, args.days))
    if args.set_ is not None:
        sys.exit(set_budgets(d, args.set_))
    ap.print_help()
    sys.exit(2)


if __name__ == "__main__":
    main()
