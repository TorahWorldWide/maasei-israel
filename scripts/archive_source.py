#!/usr/bin/env python3
"""Archive a source page and return the snapshot url — rule 136.

A citation is only verifiable while the page it came from is alive. The work is
split across two machines: the availability lookup runs here on the VM, and the
save-page-now request runs on Tomer's PC over Tailscale SSH. Wayback throttles
this VM's datacenter address (429) and some origins refuse it outright (520);
his residential address is not throttled — the same reason YouTube downloads
route through his PC (rule 62). **Every save is a command on his machine, so
report the run in Telegram.** Route and traps: docs/wayback-archive-runbook.md.

  python3 scripts/archive_source.py <url> [<url> ...]
  python3 scripts/archive_source.py --json <url>            # one json object per line
  python3 scripts/archive_source.py --quote "טקסט" <url>    # snapshot holds it?
  python3 scripts/archive_source.py --no-pc <url>           # save from the VM instead

A failure is still a normal answer: the caller records `archive_failed:<url>` in
`unresolved` and moves on. It never invents a url.
"""
import argparse
import base64
import json
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

AVAILABLE = "https://archive.org/wayback/available?url="
CDX = "https://web.archive.org/cdx/search/cdx?output=json&limit=-1&filter=statuscode:200&url="
SAVE = "https://web.archive.org/save/"
AGENT = {"User-Agent": "maasei-israel/1.0 (+https://maasei-israel.vercel.app)"}

PC = "tomer@100.78.91.21"
KEY = str(Path.home() / ".ssh" / "id_ed25519")
LOCAL_PC_SCRIPT = Path(__file__).resolve().parent / "pc" / "wayback_save_pc.py"
REMOTE_PC_SCRIPT = "wayback_save_pc.py"  # relative to C:\Users\tomer — a drive letter breaks scp
SAVE_DELAY = 20.0  # between saves; a burst is throttled even from a home address


def get(url, timeout=60, tries=3):
    """Wayback answers 429 to a burst. Back off rather than calling it a failure."""
    for attempt in range(tries):
        req = urllib.request.Request(url, headers=AGENT)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", "replace"), r.geturl()
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == tries - 1:
                raise
            time.sleep(15 * (attempt + 1))


def existing(url):
    """Latest snapshot, asked of the cdx index first.

    `wayback/available` is the obvious api and it lies: on 11.8 it answered "no
    snapshot" for pmc.ncbi, bbc.com and jpost pages that the cdx index shows are
    captured. A false negative there costs a needless save, and writes
    `archive_failed` over a citation that was archived all along. cdx is the
    authoritative index, so it leads; available stays as the fallback for when
    cdx times out, which it does.
    """
    try:
        body, _ = get(CDX + urllib.parse.quote(url, safe=""), timeout=45)
        rows = json.loads(body or "[]")[1:]
        if rows:
            stamp, original = rows[-1][1], rows[-1][2]
            return f"https://web.archive.org/web/{stamp}/{original}", stamp
        return None, None
    except Exception:
        pass
    try:
        body, _ = get(AVAILABLE + urllib.parse.quote(url, safe=""), timeout=30)
        closest = (json.loads(body).get("archived_snapshots") or {}).get("closest") or {}
    except Exception:
        return None, None
    if closest.get("available") and closest.get("url"):
        return closest["url"].replace("http://web.archive.org", "https://web.archive.org"), closest.get("timestamp")
    return None, None


def vm_save(urls, delay):
    """The old route, kept behind --no-pc for when his PC is off."""
    out = {}
    for i, url in enumerate(urls):
        if i:
            time.sleep(delay)
        try:
            _, final = get(SAVE + url, timeout=180, tries=1)
        except Exception as e:
            out[url] = {"url": url, "archived_url": None, "error": f"{type(e).__name__}: {e}"}
            continue
        out[url] = {"url": url, "archived_url": final if "/web/" in final else None,
                    "error": None if "/web/" in final else "save returned no snapshot url"}
    return out


def pc_reachable():
    try:
        r = subprocess.run(["ssh", "-i", KEY, "-o", "ConnectTimeout=12",
                            "-o", "BatchMode=yes", PC, "echo up"],
                           capture_output=True, text=True, timeout=30)
        return r.returncode == 0
    except Exception:
        return False


def pc_save(urls, delay):
    """Saves run on Tomer's PC. Report this run in Telegram — his standing rule."""
    try:
        subprocess.run(["scp", "-i", KEY, "-o", "ConnectTimeout=15", "-o", "BatchMode=yes",
                        str(LOCAL_PC_SCRIPT), f"{PC}:{REMOTE_PC_SCRIPT}"],
                       check=True, capture_output=True, text=True, timeout=90)
    except Exception as e:
        return {u: {"url": u, "archived_url": None, "error": f"pc unreachable: {e}"} for u in urls}

    token = base64.urlsafe_b64encode(json.dumps(urls).encode()).decode()
    command = (f"set PYTHONIOENCODING=utf-8 && python {REMOTE_PC_SCRIPT} "
               f"--b64 {token} --delay {delay}")
    # Keepalive is mandatory: nothing crosses the channel while a save is pending,
    # and a dropped idle connection takes the remote process down with it.
    argv = ["ssh", "-i", KEY, "-o", "ConnectTimeout=15", "-o", "BatchMode=yes",
            "-o", "ServerAliveInterval=20", "-o", "ServerAliveCountMax=200", PC, command]
    budget = len(urls) * (delay + 180) + 120
    try:
        r = subprocess.run(argv, timeout=budget, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        stdout, stderr = r.stdout, r.stderr
    except subprocess.TimeoutExpired as e:
        stdout = e.stdout.decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        stderr = "ssh timed out"

    out = {}
    for line in (stdout or "").splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            out[record["url"]] = record
    for url in urls:
        out.setdefault(url, {"url": url, "archived_url": None,
                             "error": f"no answer from pc: {(stderr or '').strip()[:200]}"})
    return out


def archive(urls, fresh=False, delay=SAVE_DELAY, use_pc=True):
    records = {}
    pending = []
    for url in urls:
        snapshot, stamp = (None, None) if fresh else existing(url)
        if snapshot:
            records[url] = {"url": url, "archived_url": snapshot, "timestamp": stamp, "how": "existing"}
        else:
            pending.append(url)

    if use_pc and pending and not pc_reachable():
        # His PC sleeps. Writing "archive_failed" because nobody was home names
        # a failure that never happened — and rule 136 accepts that note as the
        # final word. The VM route is throttled and slower, but it is true.
        print("PC unreachable — saving from the VM instead", file=sys.stderr)
        use_pc = False
    saved = (pc_save(pending, delay) if use_pc else vm_save(pending, delay)) if pending else {}
    for url in pending:
        result = saved[url]
        if result["archived_url"]:
            records[url] = {"url": url, "archived_url": result["archived_url"], "timestamp": None,
                            "how": "saved-pc" if use_pc else "saved-vm"}
            continue
        # A save that timed out or answered 429 may still have landed, and the
        # availability lookup may have been throttled on the first pass.
        snapshot, stamp = existing(url)
        if snapshot:
            records[url] = {"url": url, "archived_url": snapshot, "timestamp": stamp, "how": "existing"}
        else:
            records[url] = {"url": url, "archived_url": None, "timestamp": None,
                            "how": "failed", "error": result["error"]}
    return [records[url] for url in urls]


def holds_quote(snapshot, quote):
    try:
        body, _ = get(snapshot, timeout=90, tries=1)
    except Exception:
        return None
    return quote.strip() in body


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url", nargs="+")
    ap.add_argument("--json", action="store_true", help="full record per line instead of the url")
    ap.add_argument("--fresh", action="store_true", help="skip the existing snapshot, try to save")
    ap.add_argument("--quote", help="check that the snapshot still contains this text")
    ap.add_argument("--delay", type=float, default=SAVE_DELAY, help="seconds between saves")
    ap.add_argument("--no-pc", action="store_true", help="save from the VM (his PC is off)")
    args = ap.parse_args()

    records = archive(args.url, fresh=args.fresh, delay=args.delay, use_pc=not args.no_pc)
    if args.quote:
        for record in records:
            if record["archived_url"]:
                record["holds_quote"] = holds_quote(record["archived_url"], args.quote)

    for record in records:
        if args.json:
            print(json.dumps(record, ensure_ascii=False))
        elif record["archived_url"]:
            print(record["archived_url"])
        else:
            # Rule 136: name the failure, do not invent a url.
            print(f"archive_failed:{record['url']}", file=sys.stderr)
    return 0 if all(r["archived_url"] for r in records) else 1


if __name__ == "__main__":
    sys.exit(main())
