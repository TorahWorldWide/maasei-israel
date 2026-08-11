#!/usr/bin/env python3
"""Wayback save-page-now, run from Tomer's home address — rule 136.

This file lives on his PC. The VM's datacenter address is what Wayback throttles
(429) and what some origins refuse outright (520); his residential address is not,
the same reason YouTube downloads route through here (rule 62). The driver is
`scripts/archive_source.py` on the VM, which copies this file over before each run.

  python wayback_save_pc.py --b64 <urlsafe-b64 of a json list of urls> [--delay 20]

Urls arrive base64-encoded so that `&` in a query string cannot break cmd.exe.
Prints one json object per line: {"url", "archived_url", "error"}.
"""
import argparse
import base64
import json
import time
import urllib.error
import urllib.request

SAVE = "https://web.archive.org/save/"
AGENT = {"User-Agent": "maasei-israel/1.0 (+https://maasei-israel.vercel.app)"}


def save(url, timeout):
    req = urllib.request.Request(SAVE + url, headers=AGENT)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            final = r.geturl()
    except urllib.error.HTTPError as e:
        return None, f"http {e.code}"
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"
    if "/web/" in final:
        return final, None
    return None, "save returned no snapshot url"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--b64", required=True)
    ap.add_argument("--delay", type=float, default=20.0)
    ap.add_argument("--timeout", type=float, default=180.0)
    args = ap.parse_args()

    urls = json.loads(base64.urlsafe_b64decode(args.b64.encode()).decode())
    for i, url in enumerate(urls):
        if i:
            time.sleep(args.delay)
        snapshot, err = save(url, args.timeout)
        print(json.dumps({"url": url, "archived_url": snapshot, "error": err}), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
