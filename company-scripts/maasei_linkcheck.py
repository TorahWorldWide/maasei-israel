#!/usr/bin/env python3
"""
maasei_linkcheck.py — the company's LINK-ROT WATCHDOG (0 LLM tokens).

Every entry on "מעשי ישראל" rests on its source_url. If a source goes dead
(404/410, domain expired, article pulled), the entry silently loses its proof —
the iron rule is quietly broken and nobody notices. This script walks every
source_url (entry sources + citation sources) and checks each is still alive.

It is careful to tell apart:
  DEAD      -> 404 / 410 / DNS failure / connection refused  (real problem)
  BLOCKED   -> 403 / 429 / 503 / anti-bot challenge page      (alive, just shy)
  OK        -> 200 with real content
A BLOCKED link is NOT reported as broken — those sources (Times of Israel, PMC,
gov sites) are alive and fine for a human, they just refuse bots.

MODES
  python3 maasei_linkcheck.py --check [--status approved] [--limit N]
      → check all source URLs, print a JSON report. Exit 0 if nothing DEAD,
        1 if any DEAD link found.

  python3 maasei_linkcheck.py --watch [--status approved]
      → designed for a no_agent cron: prints a SHORT Hebrew alert ONLY if dead
        links exist; prints NOTHING (silent) when all good. Perfect watchdog.

  python3 maasei_linkcheck.py --persist [--status approved]
      → like --check but also writes results into a `link_health` table so the
        admin UI / a future shift can see which entries need a fresh source.
"""
import argparse
import datetime
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import maasei_insert as mi
import maasei_verify as mv  # reuse fetch_text (browser headers + soft-block aware)


def esc(s):
    return str(s).replace("'", "''")


def collect_urls(cfg, status, limit):
    """Return list of {url, titles:[..]} — each distinct source URL with the
    entries that depend on it (so we report which entries break)."""
    where = f"where status = '{esc(status)}'" if status else ""
    lim = f" limit {int(limit)}" if limit else ""
    ok, rows = mi.run_sql(
        f"select title, source_url, citations from entries {where} "
        f"order by created_at{lim};", cfg)
    rows = rows if (ok and isinstance(rows, list)) else []
    url_map = {}
    for r in rows:
        title = r.get("title", "")
        urls = set()
        if r.get("source_url"):
            urls.add(r["source_url"])
        cites = r.get("citations")
        if isinstance(cites, str):
            try:
                cites = json.loads(cites)
            except Exception:
                cites = []
        for c in (cites or []):
            if c.get("source_url"):
                urls.add(c["source_url"])
        for u in urls:
            url_map.setdefault(u, set()).add(title)
    return {u: sorted(t) for u, t in url_map.items()}


def classify(url):
    """Return (state, detail). state in OK|BLOCKED|DEAD."""
    if mv.is_youtube(url):
        # we still want to know if a media link died; treat like any URL
        pass
    ok, text = mv.fetch_text(url, timeout=25)
    if ok:
        return "OK", ""
    # text looks like "http 404|dead" or "http 403|blocked" or "fetch error: ..."
    if "|" in text:
        detail, kind = text.rsplit("|", 1)
        if kind == "blocked":
            return "BLOCKED", detail
        return "DEAD", detail
    # network-level failures (DNS, refused, timeout) => dead
    return "DEAD", text


def run(cfg, status, limit):
    url_map = collect_urls(cfg, status, limit)
    dead, blocked, ok_n = [], [], 0
    results = []
    for url, titles in url_map.items():
        state, detail = classify(url)
        rec = {"url": url, "state": state, "detail": detail, "entries": titles}
        results.append(rec)
        if state == "DEAD":
            dead.append(rec)
        elif state == "BLOCKED":
            blocked.append(rec)
        else:
            ok_n += 1
    return {
        "checked": len(url_map),
        "ok": ok_n,
        "blocked": len(blocked),
        "dead_count": len(dead),
        "dead": dead,
        "blocked_list": blocked,
        "all_results": results,
    }


def mode_check(cfg, status, limit):
    rep = run(cfg, status, limit)
    rep.pop("all_results", None)
    print(json.dumps(rep, ensure_ascii=False))
    return 0 if rep["dead_count"] == 0 else 1


def mode_watch(cfg, status):
    rep = run(cfg, status, 0)
    if rep["dead_count"] == 0:
        # silent — nothing to report (no_agent cron suppresses empty stdout)
        return 0
    lines = [f"\U0001F517 \u05d0\u05d6\u05d4\u05e8\u05ea \u05e7\u05d9\u05e9\u05d5\u05e8\u05d9\u05dd \u2014 \u05de\u05e2\u05e9\u05d9 \u05d9\u05e9\u05e8\u05d0\u05dc",
             f"{rep['dead_count']} \u05de\u05e7\u05d5\u05e8\u05d5\u05ea \u05de\u05ea\u05d9\u05dd (404/\u05dc\u05d0 \u05e7\u05d9\u05d9\u05dd) \u05de\u05ea\u05d5\u05da {rep['checked']} \u05e9\u05e0\u05d1\u05d3\u05e7\u05d5:"]
    for d in rep["dead"][:10]:
        ent = d["entries"][0] if d["entries"] else "?"
        lines.append(f"\u2022 {ent[:40]} \u2014 {d['detail']}")
        lines.append(f"  {d['url'][:70]}")
    print("\n".join(lines))
    return 1


def ensure_table(cfg):
    mi.run_sql("""
create table if not exists link_health (
  url        text primary key,
  state      text not null,
  detail     text not null default '',
  entries    jsonb not null default '[]'::jsonb,
  checked_at timestamptz not null default now()
);
alter table link_health enable row level security;
drop policy if exists link_health_public_read on link_health;
create policy link_health_public_read on link_health for select using (true);
""", cfg)


def mode_persist(cfg, status, limit):
    ensure_table(cfg)
    rep = run(cfg, status, limit)
    now = datetime.datetime.utcnow().isoformat() + "Z"
    rows = []
    for r in rep["all_results"]:
        ents = esc(json.dumps(r["entries"], ensure_ascii=False))
        rows.append(f"('{esc(r['url'])}', '{esc(r['state'])}', '{esc(r['detail'])}', "
                    f"'{ents}'::jsonb, '{esc(now)}')")
    if rows:
        sql = ("insert into link_health (url, state, detail, entries, checked_at) values\n"
               + ",\n".join(rows) +
               "\non conflict (url) do update set state=excluded.state, "
               "detail=excluded.detail, entries=excluded.entries, "
               "checked_at=excluded.checked_at;")
        mi.run_sql(sql, cfg)
    rep.pop("all_results", None)
    rep["persisted"] = len(rows)
    print(json.dumps(rep, ensure_ascii=False))
    return 0 if rep["dead_count"] == 0 else 1


def main():
    ap = argparse.ArgumentParser(description="Maasei Israel link-rot watchdog")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--watch", action="store_true")
    ap.add_argument("--persist", action="store_true")
    ap.add_argument("--status", default="approved")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    cfg = mi.load_config()
    if args.watch:
        sys.exit(mode_watch(cfg, args.status))
    if args.persist:
        sys.exit(mode_persist(cfg, args.status, args.limit))
    if args.check:
        sys.exit(mode_check(cfg, args.status, args.limit))
    ap.print_help()
    sys.exit(2)


if __name__ == "__main__":
    main()
