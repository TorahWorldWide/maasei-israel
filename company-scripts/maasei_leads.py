#!/usr/bin/env python3
"""
maasei_leads.py — the company's LEADS BACKLOG (the scale engine).

The path to 1000+ entries is NOT searching one topic at a time — it is mining
the lists other people already built (Wikipedia "List of Israeli inventions",
Reddit megathreads, "10 ways Israel helps the world" articles, Nobel-laureate
lists, NGO mission logs) and banking every candidate as a *lead*. A lead is just
"a deed worth researching", not yet verified. Verification shifts then pull
leads from this backlog and run them through maasei_verify + maasei_insert.

This splits the expensive work in two:
  1. HARVEST (rare, cheap): read one list page, bank 10-50 leads at once.
  2. VERIFY (daily): pull a handful of banked leads, prove each, insert.
So a daily shift never wastes tokens re-discovering what to look at.

Leads live in a Supabase table `leads`:
  id              uuid
  title           text  -- short candidate deed, e.g. "Sderot Watergen donation"
  hint            text  -- who/what/when/scope to help the researcher
  category        text  -- best guess: חסד / המצאה מדעית / תרומה לעולם / היסטורי
  source_list_url text  -- the list/article this lead was harvested from
  status          text  -- new | researching | used | rejected | duplicate
  note            text  -- why rejected / researcher notes
  created_at, updated_at

USAGE (all 0 LLM tokens)
  python3 maasei_leads.py --fetch-list "<url>"
      → download a list page and print its cleaned text + extracted links, so
        the agent can read it and pick out candidate deeds. 0 tokens of its own.

  python3 maasei_leads.py --add '<json-array>'
      → json = list of {title, hint?, category?, source_list_url?}. Banks the
        new, non-duplicate leads. Dedupes against existing leads AND against the
        ledger/live entries (so we never queue something already on the site).
        Prints {added, skipped:[{title,reason}]}.

  python3 maasei_leads.py --next [N]
      → return up to N (default 5) 'new' leads to work on AND atomically mark
        them 'researching' so two shifts can't claim the same lead. Prints the
        claimed leads.

  python3 maasei_leads.py --list [--status new] [--limit N]
      → inspect the backlog without claiming anything.

  python3 maasei_leads.py --mark '<json>'
      → json = {title|id, status, note?}. Update a lead after researching it
        (status=used when it became an entry, rejected when it failed the iron
        rule).

  python3 maasei_leads.py --stats
      → counts by status, so the manager sees how deep the backlog is.

  python3 maasei_leads.py --release-stale [--hours 12]
      → reset 'researching' leads older than N hours back to 'new' (a shift that
        crashed mid-research shouldn't strand its claimed leads forever).
"""
import argparse
import datetime
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import maasei_insert as mi      # load_config + run_sql (token-safe)
import maasei_ledger as ml      # words() + dedup helpers
import maasei_verify as mv      # fetch_text + strip_html (browser headers, soft-block aware)

ALLOWED_STATUS = {"new", "researching", "used", "rejected", "duplicate"}


def esc(s):
    return str(s).replace("'", "''")


def ensure_table(cfg):
    mi.run_sql("""
create table if not exists leads (
  id              uuid primary key default uuid_generate_v4(),
  title           text not null,
  hint            text not null default '',
  category        text not null default '',
  source_list_url text not null default '',
  status          text not null default 'new',
  note            text not null default '',
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now()
);
alter table leads enable row level security;
drop policy if exists leads_public_read on leads;
create policy leads_public_read on leads for select using (true);
""", cfg)


# --- harvesting a list page (0 tokens) -------------------------------------
def fetch_list(url):
    ok, text = mv.fetch_text(url, timeout=30)
    if not ok:
        print(json.dumps({"ok": False, "error": text, "url": url}, ensure_ascii=False))
        return 1
    # Also pull anchor texts + hrefs from the RAW html (fetch_text already
    # stripped tags, so re-fetch raw for links). Keep it cheap: one more GET.
    links = []
    try:
        import requests
        raw = requests.get(url, headers=mv.BROWSER_HEADERS, timeout=30).text
        for m in re.finditer(r'<a\s[^>]*href="([^"#]+)"[^>]*>(.*?)</a>', raw, re.I | re.S):
            href, label = m.group(1), mv.strip_html(m.group(2)).strip()
            if label and len(label) > 3:
                links.append({"href": href, "text": label[:120]})
    except Exception:
        pass
    # de-dupe links by text, cap the payload so it stays token-cheap to read
    seen, uniq = set(), []
    for l in links:
        if l["text"] in seen:
            continue
        seen.add(l["text"])
        uniq.append(l)
    print(json.dumps({
        "ok": True,
        "url": url,
        "text": text[:60000],
        "link_count": len(uniq),
        "links": uniq[:400],
    }, ensure_ascii=False))
    return 0


# --- dedup -----------------------------------------------------------------
def existing_lead_titles(cfg):
    ok, rows = mi.run_sql("select title, status from leads;", cfg)
    return rows if (ok and isinstance(rows, list)) else []


def is_duplicate(title, lead_rows, ledger_rows, entry_rows):
    """True if this candidate overlaps an existing lead, ledger topic, or live
    entry (reusing the ledger's distinctive-word overlap test)."""
    qw = ml.words(title)
    for r in lead_rows:
        ok_m, _ = _strong(qw, ml.words(r["title"]))
        if ok_m:
            return True, f"existing lead ({r.get('status')})"
    for r in ledger_rows:
        ok_m, _ = _strong(qw, ml.words(r["topic"]))
        if ok_m and r.get("status") in ("done", "rejected"):
            return True, f"ledger:{r['status']}"
    for r in entry_rows:
        ok_m, _ = _strong(qw, ml.words(r["title"]))
        if ok_m:
            return True, "already a live entry"
    return False, ""


def _strong(a, b):
    """Reuse the ledger's strong-overlap rule for consistency (distinctive-word
    overlap), with extra English stopwords for English list pages."""
    STOP = {"ישראלי", "ישראלים", "ישראל", "הישראלי", "הישראלית", "מים", "ילדים",
            "בני", "אדם", "אנשים", "עם", "של", "את", "מקבלים", "עוזר", "עוזרים",
            "ממציא", "יוצר", "מקים", "מקימים", "the", "and", "for", "with",
            "israel", "israeli", "israelis"}
    common = (a & b) - STOP
    if len(common) < 2:
        return False, common
    smaller = min(len(a - STOP), len(b - STOP)) or 1
    return (len(common) / smaller) >= 0.5, common


def add(cfg, payload):
    ensure_table(cfg)
    try:
        items = json.loads(payload)
    except Exception as ex:
        print(json.dumps({"error": f"bad json: {ex}"}, ensure_ascii=False))
        return 1
    if isinstance(items, dict):
        items = [items]

    lead_rows = existing_lead_titles(cfg)
    ok, ledger = mi.run_sql("select topic, status from topics;", cfg)
    ledger = ledger if (ok and isinstance(ledger, list)) else []
    ok2, ents = mi.run_sql("select title from entries;", cfg)
    ents = ents if (ok2 and isinstance(ents, list)) else []

    valid, skipped = [], []
    seen_now = set()
    for it in items:
        title = (it.get("title") or "").strip()
        if not title:
            skipped.append({"title": "", "reason": "empty title"})
            continue
        key = " ".join(sorted(ml.words(title)))
        if key in seen_now:
            skipped.append({"title": title, "reason": "duplicate within this batch"})
            continue
        dup, why = is_duplicate(title, lead_rows, ledger, ents)
        if dup:
            skipped.append({"title": title, "reason": why})
            continue
        seen_now.add(key)
        valid.append(it)
        lead_rows.append({"title": title, "status": "new"})  # prevent intra-batch dupes

    added = 0
    if valid:
        rows = []
        for it in valid:
            cat = it.get("category", "")
            if cat and cat not in mi.ALLOWED_CATEGORIES:
                cat = ""
            rows.append(
                f"('{esc(it['title'])}', '{esc(it.get('hint',''))}', "
                f"'{esc(cat)}', '{esc(it.get('source_list_url',''))}', 'new', '')")
        sql = ("insert into leads (title, hint, category, source_list_url, status, note) "
               "values\n" + ",\n".join(rows) + " returning id;")
        ok3, res = mi.run_sql(sql, cfg)
        if ok3 and isinstance(res, list):
            added = len(res)
        else:
            print(json.dumps({"error": "insert failed", "detail": res}, ensure_ascii=False))
            return 1
    print(json.dumps({"added": added, "skipped_count": len(skipped),
                      "skipped": skipped}, ensure_ascii=False))
    return 0


def claim_next(cfg, n):
    ensure_table(cfg)
    # Atomic claim: flip up to n 'new' rows to 'researching' and return them.
    sql = f"""
with picked as (
  select id from leads where status = 'new'
  order by created_at limit {int(n)}
  for update skip locked
)
update leads set status = 'researching', updated_at = now()
where id in (select id from picked)
returning id, title, hint, category, source_list_url;
"""
    ok, res = mi.run_sql(sql, cfg)
    leads = res if (ok and isinstance(res, list)) else []
    print(json.dumps({"claimed": len(leads), "leads": leads}, ensure_ascii=False))
    return 0


def list_leads(cfg, status, limit):
    ensure_table(cfg)
    where = f"where status = '{esc(status)}'" if status else ""
    lim = f" limit {int(limit)}" if limit else ""
    ok, rows = mi.run_sql(
        f"select id, title, hint, category, source_list_url, status, note "
        f"from leads {where} order by created_at{lim};", cfg)
    print(json.dumps({"leads": rows if (ok and isinstance(rows, list)) else []},
                     ensure_ascii=False))
    return 0


def mark(cfg, payload):
    ensure_table(cfg)
    d = json.loads(payload)
    status = d.get("status", "used")
    if status not in ALLOWED_STATUS:
        print(json.dumps({"error": f"bad status: {status}"}, ensure_ascii=False))
        return 1
    note = d.get("note", "")
    now = datetime.datetime.utcnow().isoformat() + "Z"
    if d.get("id"):
        cond = f"id = '{esc(d['id'])}'"
    elif d.get("title"):
        cond = f"title = '{esc(d['title'])}'"
    else:
        print(json.dumps({"error": "need id or title"}, ensure_ascii=False))
        return 1
    ok, res = mi.run_sql(
        f"update leads set status='{esc(status)}', note='{esc(note)}', "
        f"updated_at='{esc(now)}' where {cond} returning id, title, status;", cfg)
    print(json.dumps({"marked": ok, "rows": res if isinstance(res, list) else res},
                     ensure_ascii=False))
    return 0


def stats(cfg):
    ensure_table(cfg)
    ok, rows = mi.run_sql(
        "select status, count(*)::int as n from leads group by status order by n desc;", cfg)
    print(json.dumps({"by_status": rows if (ok and isinstance(rows, list)) else []},
                     ensure_ascii=False))
    return 0


def release_stale(cfg, hours):
    ensure_table(cfg)
    ok, res = mi.run_sql(
        f"update leads set status='new', updated_at=now() "
        f"where status='researching' and updated_at < now() - interval '{int(hours)} hours' "
        f"returning id;", cfg)
    n = len(res) if (ok and isinstance(res, list)) else 0
    print(json.dumps({"released": n}, ensure_ascii=False))
    return 0


def main():
    ap = argparse.ArgumentParser(description="Maasei Israel leads backlog")
    ap.add_argument("--fetch-list", dest="fetch_list", metavar="URL")
    ap.add_argument("--add", metavar="JSON")
    ap.add_argument("--next", nargs="?", const=5, type=int, metavar="N")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--status", default="")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--mark", metavar="JSON")
    ap.add_argument("--stats", action="store_true")
    ap.add_argument("--release-stale", dest="release_stale", action="store_true")
    ap.add_argument("--hours", type=int, default=12)
    args = ap.parse_args()

    cfg = mi.load_config()
    if args.fetch_list:
        sys.exit(fetch_list(args.fetch_list))
    if args.add is not None:
        sys.exit(add(cfg, args.add))
    if args.next is not None:
        sys.exit(claim_next(cfg, args.next))
    if args.list:
        sys.exit(list_leads(cfg, args.status, args.limit))
    if args.mark is not None:
        sys.exit(mark(cfg, args.mark))
    if args.stats:
        sys.exit(stats(cfg))
    if args.release_stale:
        sys.exit(release_stale(cfg, args.hours))
    ap.print_help()
    sys.exit(2)


if __name__ == "__main__":
    main()
