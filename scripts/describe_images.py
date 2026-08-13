#!/usr/bin/env python3
"""Rule 149 — describe every image of a deed blind, before anyone judges a caption.

Blind means the describer gets the bytes and nothing else: no file name, no page
text, no caption to agree with. That is why this runs one fresh process per
image and saves the file under its own sha1 — a caption guessed from a file name
once called a night-time recovery of remains "the delegation under both flags".

  python3 scripts/describe_images.py <deed-id>          # -> /tmp/blind/<deed>.json
  python3 scripts/describe_images.py <deed-id> --force  # redescribe what is done

The output is merged into audit.image_provenance[].image_seen by
apply_completion.py. This script never touches the database.
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_claims import run_sql  # noqa: E402

BLIND = Path("/tmp/blind")
MODEL = "claude-opus-5"
BY = f"describe_images/{MODEL}"
UA = "MaaseiIsrael/1.0 (deed standard rule 149; contact via maasei-israel.vercel.app)"
AVAILABLE = "https://archive.org/wayback/available?url="
COMMONS = ("https://commons.wikimedia.org/w/api.php"
           "?action=query&format=json&prop=imageinfo&iiprop=url%7Csize")
PROMPT = (
    "קרא את קובץ התמונה {path} וכתוב מה רואים בו.\n\n"
    "אין לך שום הקשר על התמונה, וזו הכוונה. אל תנחש מי האנשים, מה האירוע או מתי "
    "צולם — תאר רק את מה שנמצא בפריים: מי או מה נמצא בו, כמה, מה הם עושים, איזה "
    "סוג תמונה זו (צילום/ציור/מסמך/צילום מסך/דיאגרמה), טקסט שקריא בתוך התמונה "
    "(העתק אותו כלשונו), וסימנים ויזואליים לתקופה או למקום אם יש.\n\n"
    "אם משהו אינו ברור — כתוב שאינו ברור. ניחוש הוא הכשל שהכלל הזה נועד למנוע.\n"
    "ענה בעברית, 40–90 מילים, פסקה אחת, בלי כותרות ובלי הקדמה."
)


def suffix(url):
    for ext in (".jpg", ".jpeg", ".png", ".webp", ".gif"):
        if ext in url.lower():
            return ext
    return ".jpg"


def fetch(url):
    """Save under a name that carries no information — the file name is the
    leak this rule exists to close."""
    name = hashlib.sha1(url.encode()).hexdigest()[:16] + suffix(url)
    path = BLIND / name
    if path.exists() and path.stat().st_size > 0:
        return path
    # upload.wikimedia.org rate-limits this datacenter address for hours at a
    # time, so the origin gets one attempt and the fallbacks get patience. Both
    # fallbacks hand back the same photograph the reader sees.
    for index, candidate in enumerate((url, commons_thumb(url), wayback_copy(url))):
        if not candidate:
            continue
        req = urllib.request.Request(candidate, headers={"User-Agent": UA})
        for attempt in range(1 if index == 0 else 4):
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    path.write_bytes(r.read())
                return path
            except urllib.error.HTTPError as err:
                if err.code not in (429, 503):
                    break
                time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"neither origin nor archive served {url}")


def commons_thumb(url):
    """upload.wikimedia.org throttles this address; the Commons API does not,
    and the thumbnail it hands back is served from a path that is not throttled
    either. A scaled copy is enough — rule 149 asks what is in the frame.

    MediaWiki renders a thumbnail only when the width asked for is comfortably
    under the file's own; near it, it hands back the original — which lives on
    the throttled host, so the fetch fails and the image is never described.
    A 830px file answered the original at 640 and a real thumbnail at 320, so
    the ladder walks down until a /thumb/ path comes back.
    """
    if "upload.wikimedia.org" not in url:
        return None
    title = "File:" + urllib.parse.unquote(url.rsplit("/", 1)[-1])
    for width in (1024, 800, 640, 320, 240):
        # A rung that answers nothing is the api having a bad second, not proof
        # the file has no thumbnail. Aborting the ladder there cost two images.
        thumb = (commons_info(title, width) or {}).get("thumburl") or ""
        if "/thumb/" in thumb:
            return thumb
    return None


def commons_info(title, width):
    api = f"{COMMONS}&iiurlwidth={width}&titles=" + urllib.parse.quote(title, safe="")
    try:
        req = urllib.request.Request(api, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=45) as r:
            pages = (json.load(r).get("query") or {}).get("pages") or {}
    except Exception:
        return None
    for page in pages.values():
        for item in page.get("imageinfo") or []:
            return item
    return None


def wayback_copy(url):
    api = AVAILABLE + urllib.parse.quote(url, safe="")
    try:
        req = urllib.request.Request(api, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=45) as r:
            body = json.load(r)
    except Exception:
        return None
    snapshot = ((body.get("archived_snapshots") or {}).get("closest") or {}).get("url")
    # Without the id_ modifier Wayback serves its HTML viewer, and the describer
    # would be handed a web page instead of the photograph.
    return re.sub(r"/web/(\d+)/", r"/web/\1id_/", snapshot) if snapshot else None


def describe(path):
    out = subprocess.run(
        ["claude", "-p", PROMPT.format(path=path),
         "--permission-mode", "bypassPermissions", "--model", MODEL],
        capture_output=True, text=True, timeout=600,
    )
    return out.stdout.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("deed_id")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    rows = run_sql("select id, audit from entries where id = '"
                   + args.deed_id.replace("'", "") + "'")
    if not rows:
        sys.exit("no such deed")
    provenance = (rows[0].get("audit") or {}).get("image_provenance") or []
    urls = [p.get("url") for p in provenance if p.get("url")]
    if not urls:
        sys.exit("no images in audit.image_provenance")

    BLIND.mkdir(parents=True, exist_ok=True)
    out_path = BLIND / f"{args.deed_id}.json"
    seen = json.loads(out_path.read_text()) if out_path.exists() else {}

    for url in urls:
        if url in seen and not args.force:
            print(f"skip  {url[:70]}")
            continue
        try:
            path = fetch(url)
        except Exception as exc:  # a dead link is rule 11's problem, not 149's
            print(f"FETCH-FAIL {url[:60]} — {exc}")
            continue
        text = describe(path)
        if not text:
            print(f"EMPTY {url[:60]}")
            continue
        seen[url] = {
            "described_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "by": BY,
            "description": text,
            "blind": True,
        }
        # Written after every image: a run killed at image seven keeps six.
        out_path.write_text(json.dumps(seen, ensure_ascii=False, indent=1))
        print(f"seen  {url[:60]}\n      {text[:110]}")

    print(f"\n{len(seen)}/{len(urls)} described -> {out_path}")


if __name__ == "__main__":
    main()
