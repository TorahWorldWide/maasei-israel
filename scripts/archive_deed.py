#!/usr/bin/env python3
"""Fill `citations[].archived_url` for whole deeds — rule 136, in one place.

Archiving is the last step of a deed, not a step inside the worker: the save
runs on Tomer's PC over one ssh channel (rule 136 moved there on 11.8), and five
workers racing for that channel would throttle each other and lose snapshots
that were already paid for. So the workers leave `archived_url` empty and this
runs after `apply_standard_pass.py`, serially, over every citation at once.

A url that cannot be saved is not a hole to be papered over: it is written into
`audit.unresolved` as `archive_failed:<url>`, which is the wording rule 136
accepts as a named failure.

  python3 scripts/archive_deed.py <deed-id> [<deed-id> ...]
  python3 scripts/archive_deed.py --apply <deed-id> ...     # write to the db
  python3 scripts/archive_deed.py --apply --file ids.txt
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from archive_source import archive  # noqa: E402
from audit_claims import run_sql  # noqa: E402

ARCHIVE_FAILED = "archive_failed:"


def lit(value):
    return "'" + str(value).replace("'", "''") + "'"


def jsonb(value):
    return lit(json.dumps(value, ensure_ascii=False)) + "::jsonb"


def load(ids):
    rows = run_sql(
        "select id, title, citations, audit from entries where id in ("
        + ",".join(lit(i) for i in ids) + ")"
    )
    return {r["id"]: r for r in rows}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("deed_id", nargs="*")
    ap.add_argument("--file", help="a file of deed ids, one per line")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--delay", type=float, default=20.0)
    ap.add_argument("--no-pc", action="store_true")
    args = ap.parse_args()

    ids = list(args.deed_id)
    if args.file:
        ids += [l.strip() for l in Path(args.file).read_text().splitlines() if l.strip()]
    if not ids:
        return ap.error("no deed ids")

    rows = load(ids)
    missing = [i for i in ids if i not in rows]
    for i in missing:
        print(f"NOROW {i}")

    # One archive run for every citation of every deed, so a url shared by two
    # deeds is saved once and a burst never reaches the PC twice.
    urls = []
    for i in ids:
        for c in (rows.get(i) or {}).get("citations") or []:
            u = (c.get("source_url") or "").strip()
            if u and u not in urls and not (c.get("archived_url") or "").strip():
                urls.append(u)
    print(f"{len(urls)} urls to archive across {len(rows)} deeds", flush=True)
    if not urls:
        return 0

    records = {r["url"]: r for r in archive(urls, delay=args.delay, use_pc=not args.no_pc)}
    ok = sum(1 for r in records.values() if r["archived_url"])
    print(f"archived {ok}/{len(urls)}", flush=True)

    # Re-read before writing. Saving one batch of urls takes half an hour on the
    # PC's queue, and a caption or translation fix applied during that half hour
    # lives in the same `audit` column this is about to overwrite. Writing the
    # snapshot taken at startup silently reverted such a fix once.
    fresh = load([i for i in ids if i in rows])
    for i in ids:
        row = fresh.get(i) or rows.get(i)
        if not row:
            continue
        cites = row.get("citations") or []
        audit = row.get("audit") if isinstance(row.get("audit"), dict) else {}
        unresolved = [str(u) for u in (audit.get("unresolved") or [])]
        failed = []
        for c in cites:
            u = (c.get("source_url") or "").strip()
            record = records.get(u) or {}
            if record.get("archived_url"):
                c["archived_url"] = record["archived_url"]
            elif u and not (c.get("archived_url") or "").strip():
                failed.append(u)
        for u in failed:
            note = f"{ARCHIVE_FAILED}{u}"
            if note not in unresolved:
                unresolved.append(note)
        audit["unresolved"] = unresolved
        done = sum(1 for c in cites if (c.get("archived_url") or "").strip())
        print(f"{i[:8]} {done}/{len(cites)} archived, {len(failed)} named as failed"
              f"  {(row.get('title') or '')[:45]}")
        if args.apply:
            run_sql(
                f"update entries set citations = {jsonb(cites)}, audit = {jsonb(audit)} "
                f"where id = {lit(i)}"
            )
    if not args.apply:
        print("\ndry run — nothing written. add --apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
