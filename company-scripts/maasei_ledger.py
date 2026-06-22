#!/usr/bin/env python3
"""
maasei_ledger.py — the MANAGER's notebook ("פנקס").

The manager's whole job is to NOT repeat work. Before sending a researcher to
investigate a topic, it checks this ledger. Topics we've already covered are
marked DONE so the company never adds a 5th "IDF field hospital in Turkey" again.

The ledger lives in a Supabase table `topics`:
  topic        text  -- canonical topic name, e.g. "צה""ל בית חולים שדה טורקיה 2023"
  status       text  -- 'done' (already on site) | 'rejected' (investigated, failed iron rule) | 'queued' (assigned, not finished)
  entry_title  text  -- which entry covers it (if done)
  note         text  -- why rejected / any manager note
  updated_at   timestamptz

USAGE (all 0 LLM tokens):
  python3 maasei_ledger.py --list
      → prints the whole ledger + the live list of approved entry titles, so the
        manager sees at a glance what's covered.

  python3 maasei_ledger.py --check "<topic words>"
      → fuzzy-checks whether a topic looks already-covered (by the ledger OR by an
        existing entry title). Prints {"covered": bool, "matches":[...]}. The
        manager calls this BEFORE dispatching a researcher.

  python3 maasei_ledger.py --mark '<json>'
      → json = {topic, status, entry_title?, note?}. Upserts a ledger row.
        Call this AFTER a topic is added (status=done) or rejected.
"""
import sys
import os
import json
import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import maasei_insert as mi


def ensure_table(cfg):
    mi.run_sql("""
create table if not exists topics (
  id          uuid primary key default uuid_generate_v4(),
  topic       text not null,
  status      text not null default 'queued',
  entry_title text not null default '',
  note        text not null default '',
  updated_at  timestamptz not null default now()
);
alter table topics enable row level security;
drop policy if exists topics_public_read on topics;
create policy topics_public_read on topics for select using (true);
""", cfg)


def esc(s):
    return str(s).replace("'", "''")


# Normalize Hebrew/English text for fuzzy matching: lowercase, drop punctuation,
# split to a word set so "צה""ל בטורקיה" overlaps "בית חולים שדה בטורקיה".
def words(s):
    import re
    s = re.sub(r"[^\wא-ת ]", " ", str(s).lower())
    return set(w for w in s.split() if len(w) > 2)


def list_all(cfg):
    ensure_table(cfg)
    ok, rows = mi.run_sql("select topic, status, entry_title, note from topics order by updated_at desc;", cfg)
    ledger = rows if (ok and isinstance(rows, list)) else []
    ok2, ents = mi.run_sql("select title, year from entries where status='approved' order by year nulls last;", cfg)
    entries = ents if (ok2 and isinstance(ents, list)) else []
    print(json.dumps({"ledger": ledger, "approved_entries": entries,
                      "ledger_count": len(ledger), "entry_count": len(entries)},
                     ensure_ascii=False))


def check(cfg, query):
    ensure_table(cfg)
    qw = words(query)
    ok, rows = mi.run_sql("select topic, status, entry_title from topics;", cfg)
    ledger = rows if (ok and isinstance(rows, list)) else []
    ok2, ents = mi.run_sql("select title from entries;", cfg)  # incl pending — don't re-add
    entries = ents if (ok2 and isinstance(ents, list)) else []

    matches = []
    # Generic words that shouldn't count toward a "same topic" match on their own.
    STOP = {"ישראלי", "ישראלים", "ישראל", "הישראלי", "הישראלית", "מים", "ילדים",
            "בני", "אדם", "אנשים", "עם", "של", "את", "מקבלים", "עוזר", "עוזרים",
            "ממציא", "יוצר", "מקים", "מקימים"}

    def strong(a, b):
        """True only if the two word-sets share enough DISTINCTIVE words."""
        common = (a & b) - STOP
        if len(common) < 2:
            return False, common
        # require the overlap to be a real chunk of the shorter title, not 2 stray words
        smaller = min(len(a - STOP), len(b - STOP)) or 1
        return (len(common) / smaller) >= 0.5, common

    for r in ledger:
        ok_m, common = strong(qw, words(r["topic"]))
        if ok_m:
            matches.append({"kind": "ledger", "status": r["status"],
                            "topic": r["topic"], "overlap": sorted(common)})
    for e in entries:
        ok_m, common = strong(qw, words(e["title"]))
        if ok_m:
            matches.append({"kind": "entry", "title": e["title"], "overlap": sorted(common)})

    covered = any(
        (m["kind"] == "entry") or (m["kind"] == "ledger" and m["status"] in ("done", "rejected"))
        for m in matches
    )
    print(json.dumps({"covered": covered, "matches": matches}, ensure_ascii=False))


def mark(cfg, payload):
    ensure_table(cfg)
    d = json.loads(payload)
    topic = d["topic"]
    status = d.get("status", "done")
    entry_title = d.get("entry_title", "")
    note = d.get("note", "")
    now = datetime.datetime.utcnow().isoformat() + "Z"
    # naive upsert: delete same-topic rows then insert (topics are short, fine)
    mi.run_sql(f"delete from topics where topic = '{esc(topic)}';", cfg)
    ok, res = mi.run_sql(
        f"insert into topics (topic, status, entry_title, note, updated_at) values "
        f"('{esc(topic)}', '{esc(status)}', '{esc(entry_title)}', '{esc(note)}', '{esc(now)}') "
        f"returning topic, status;", cfg)
    print(json.dumps({"marked": ok, "row": res[0] if (ok and res) else res}, ensure_ascii=False))


def main():
    cfg = mi.load_config()
    if len(sys.argv) >= 2 and sys.argv[1] == "--list":
        list_all(cfg)
    elif len(sys.argv) >= 3 and sys.argv[1] == "--check":
        check(cfg, sys.argv[2])
    elif len(sys.argv) >= 3 and sys.argv[1] == "--mark":
        mark(cfg, sys.argv[2])
    else:
        print("usage: maasei_ledger.py --list | --check '<topic>' | --mark '<json>'")
        sys.exit(2)


if __name__ == "__main__":
    main()
