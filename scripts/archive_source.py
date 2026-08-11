#!/usr/bin/env python3
"""Archive a source page and return the snapshot url — rule 136.

A citation is only verifiable while the page it came from is alive. This asks
the Wayback Machine for an existing snapshot first (always works), and only
tries to save a new one when there is none. On-demand saving is rate limited
from a datacenter address, so a failure here is a normal answer: the caller
records `archive_failed:<url>` in `unresolved` and moves on.

  python3 scripts/archive_source.py <url>
  python3 scripts/archive_source.py --json <url>
  python3 scripts/archive_source.py --quote "טקסט" <url>   # snapshot holds it?
"""
import argparse
import json
import sys
import urllib.parse
import urllib.request

AVAILABLE = "https://archive.org/wayback/available?url="
SAVE = "https://web.archive.org/save/"
AGENT = {"User-Agent": "maasei-israel/1.0 (+https://maasei-israel.vercel.app)"}


def get(url, timeout=60):
    req = urllib.request.Request(url, headers=AGENT)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode("utf-8", "replace"), r.geturl()


def existing(url):
    try:
        _, body, _ = get(AVAILABLE + urllib.parse.quote(url, safe=""), timeout=30)
        closest = (json.loads(body).get("archived_snapshots") or {}).get("closest") or {}
    except Exception:
        return None, None
    if closest.get("available") and closest.get("url"):
        return closest["url"].replace("http://web.archive.org", "https://web.archive.org"), closest.get("timestamp")
    return None, None


def save(url):
    """Ask for a fresh snapshot. 429/520 from a datacenter IP is expected."""
    try:
        _, _, final = get(SAVE + url, timeout=120)
    except Exception as e:
        return None, str(e)
    if "/web/" in final:
        return final, None
    return None, "save returned no snapshot url"


def archive(url, fresh=False):
    if not fresh:
        snapshot, stamp = existing(url)
        if snapshot:
            return {"url": url, "archived_url": snapshot, "timestamp": stamp, "how": "existing"}
    snapshot, err = save(url)
    if snapshot:
        return {"url": url, "archived_url": snapshot, "timestamp": None, "how": "saved"}
    snapshot, stamp = existing(url)
    if snapshot:
        return {"url": url, "archived_url": snapshot, "timestamp": stamp, "how": "existing"}
    return {"url": url, "archived_url": None, "timestamp": None, "how": "failed", "error": err}


def holds_quote(snapshot, quote):
    try:
        _, body, _ = get(snapshot, timeout=90)
    except Exception:
        return None
    return quote.strip() in body


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--json", action="store_true", help="full record instead of the url")
    ap.add_argument("--fresh", action="store_true", help="skip the existing snapshot, try to save")
    ap.add_argument("--quote", help="check that the snapshot still contains this text")
    args = ap.parse_args()

    record = archive(args.url, fresh=args.fresh)
    if args.quote and record["archived_url"]:
        record["holds_quote"] = holds_quote(record["archived_url"], args.quote)

    if args.json:
        print(json.dumps(record, ensure_ascii=False, indent=2))
    elif record["archived_url"]:
        print(record["archived_url"])
    else:
        # Rule 136: name the failure, do not invent a url.
        print(f"archive_failed:{args.url}", file=sys.stderr)
    return 0 if record["archived_url"] else 1


if __name__ == "__main__":
    sys.exit(main())
