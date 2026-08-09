#!/usr/bin/env python3
"""Apply the merge results to the live Maasei Israel DB.

For each /tmp/merge-out/<n>_<slug>.json:
  1. back up BOTH rows (survivor + doomed) to /tmp/merge-backup/ as raw JSON
  2. UPDATE the survivor with the merged fields
  3. DELETE the doomed row

Dry-run by default. Pass --apply to actually write.
"""
import sys, os, json, glob, datetime
sys.path.insert(0, "/home/ubuntu/.hermes/scripts")
from maasei_insert import load_config, run_sql

BACKUP = "/tmp/merge-backup"
TEXT_COLS = ["title", "description", "category", "media_type", "media_url", "source_url",
             "source_label", "source_label_en", "act", "ripple", "title_reasoning",
             "title_en", "description_en", "act_en", "ripple_en"]
JSON_COLS = ["citations", "media_urls"]
INT_COLS = ["year"]


def sql(q, cfg):
    ok, res = run_sql(q, cfg)
    if not ok:
        raise RuntimeError(f"SQL failed: {res}")
    return res


def esc(s):
    return str(s).replace("'", "''")


def main():
    apply = "--apply" in sys.argv
    cfg = load_config()
    os.makedirs(BACKUP, exist_ok=True)
    files = sorted(glob.glob("/tmp/merge-out/*.json"))
    print(f"{'APPLYING' if apply else 'DRY RUN'} — {len(files)} groups\n")
    total_before = sql("select count(*) as c from entries;", cfg)[0]["c"]
    print(f"rows before: {total_before}\n")

    for f in files:
        d = json.load(open(f))
        g, slug = d["group"], d["slug"]
        sid, did = d["survivor_id"], d["delete_id"]
        u = d["update"]

        rows = sql(f"select * from entries where id in ('{esc(sid)}','{esc(did)}');", cfg)
        if len(rows) != 2:
            print(f"[{g} {slug}] SKIP — expected 2 rows, DB returned {len(rows)}")
            continue
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        bpath = f"{BACKUP}/{g}_{slug}.before-{stamp}.json"
        json.dump(rows, open(bpath, "w"), ensure_ascii=False, indent=2)

        sets = []
        for c in TEXT_COLS:
            sets.append(f"{c} = '{esc(u.get(c, ''))}'")
        for c in INT_COLS:
            sets.append(f"{c} = {int(u[c])}")
        for c in JSON_COLS:
            sets.append(f"{c} = '{esc(json.dumps(u.get(c, []), ensure_ascii=False))}'::jsonb")
        upd = f"update entries set {', '.join(sets)} where id = '{esc(sid)}';"
        dele = f"delete from entries where id = '{esc(did)}';"

        print(f"[{g} {slug}] backup→{os.path.basename(bpath)} | "
              f"cits={len(u.get('citations', []))} media={len(u.get('media_urls', []))} "
              f"year={u.get('year')} | update {sid[:8]} + delete {did[:8]}")
        if apply:
            sql(upd, cfg)
            sql(dele, cfg)
            chk = sql(f"select id, title, year, jsonb_array_length(citations) as nc, "
                      f"jsonb_array_length(media_urls) as nm from entries where id='{esc(sid)}';", cfg)
            gone = sql(f"select count(*) as c from entries where id='{esc(did)}';", cfg)[0]["c"]
            print(f"        ✓ survivor: {chk[0]['title'][:50]} | cits={chk[0]['nc']} "
                  f"media={chk[0]['nm']} | doomed rows left={gone}")

    total_after = sql("select count(*) as c from entries;", cfg)[0]["c"]
    print(f"\nrows after: {total_after} (delta {total_after - total_before})")


if __name__ == "__main__":
    main()
