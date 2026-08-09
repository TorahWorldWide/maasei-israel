#!/usr/bin/env python3
"""Score every deed against docs/DEED-STANDARD.md.

Only the criteria that can be decided from the database live here. Criteria that
need a network fetch (are the images alive?) or a reader's judgment (is the year
the year of the deed or the year of the article?) are listed in the standard as
gates that run elsewhere — this script never guesses at them.

  python3 scripts/deed_standard.py            # summary
  python3 scripts/deed_standard.py --failing 3 # which deeds fail criterion 3
  python3 scripts/deed_standard.py --json out.json
"""
import argparse
import json
import re
import sys
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
YOUTUBE = re.compile(r"youtu\.?be|youtube\.com", re.I)
HEBREW = re.compile(r"[֐-׿]")
IMAGE_EXT = re.compile(r"\.(jpe?g|png|webp|gif)(\?|$)", re.I)


def env():
    out = {}
    for line in (ROOT / ".env.local").read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            out[k] = v.strip().strip('"').strip("'")
    return out


def fetch_entries():
    e = env()
    url = f"{e['NEXT_PUBLIC_SUPABASE_URL']}/rest/v1/entries?select=*&limit=1000"
    key = e["NEXT_PUBLIC_SUPABASE_ANON_KEY"]
    req = urllib.request.Request(url, headers={"apikey": key, "Authorization": f"Bearer {key}"})
    return json.load(urllib.request.urlopen(req))


def domain(url):
    m = re.search(r"https?://([^/]+)", url or "")
    return m.group(1).replace("www.", "").lower() if m else ""


def media(entry):
    """Every media url on the deed, split into videos and images."""
    urls = []
    if entry.get("media_url"):
        urls.append(entry["media_url"])
    for item in entry.get("media_urls") or []:
        if isinstance(item, str):
            urls.append(item)
        elif isinstance(item, dict) and item.get("url"):
            urls.append(item["url"])
    videos = [u for u in urls if YOUTUBE.search(u)]
    images = [u for u in urls if not YOUTUBE.search(u)]
    return videos, images


# Each check returns True (meets the standard) or False. Keyed by the criterion
# number in docs/DEED-STANDARD.md so the doc and the code can't drift apart.
def evaluate(entry):
    cites = entry.get("citations") or []
    videos, images = media(entry)
    domains = {domain(c.get("source_url", "")) for c in cites}
    domains.discard("")
    real_domains = {d for d in domains if "wikipedia.org" not in d}

    def filled(*fields):
        return all((entry.get(f) or "").strip() for f in fields)

    english_pairs = ["title", "description", "act", "ripple"]
    english_ok = all(
        not (entry.get(f) or "").strip() or (entry.get(f + "_en") or "").strip()
        for f in english_pairs
    )
    hebrew_quotes_translated = all(
        not HEBREW.search(c.get("quote") or "") or (c.get("quote_en") or "").strip()
        for c in cites
    )

    return {
        1: bool(entry.get("source_url")) and "wikipedia.org" not in (entry.get("source_url") or ""),
        2: len(real_domains) >= 5,
        3: len(cites) >= len(real_domains) and len(cites) > 0,
        6: all((c.get("locator") or "").strip() for c in cites) if cites else False,
        8: len(images) >= 5,
        9: all(IMAGE_EXT.search(u) for u in images) if images else False,
        10: len(videos) <= 5,
        18: bool(entry.get("year")),
        19: filled("act", "ripple"),
        20: english_ok and hebrew_quotes_translated,
        25: bool(entry.get("categories") or entry.get("category")),
        28: bool(entry.get("audit")),
        32: all((c.get("published") or "").strip() for c in cites) if cites else False,
    }


TITLES = {
    1: "מקור ראשי שאינו ויקיפדיה",
    2: "5 דומיינים עצמאיים ומעלה",
    3: "ציטוט אחד לפחות לכל מקור",
    6: "מיקום מדויק בכל ציטוט",
    8: "5 תמונות ומעלה",
    9: "כל תמונה היא קובץ ישיר",
    10: "עד 5 סרטונים",
    18: "שנה קיימת",
    19: "חלק א׳ + חלק ב׳ מלאים",
    20: "תרגום אנגלי מלא",
    25: "קטגוריה",
    28: "עבר ביקורת מתועדת",
    32: "תאריך פרסום לכל מקור",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--failing", type=int, help="list deeds failing this criterion")
    ap.add_argument("--json", help="write the full per-deed report here")
    args = ap.parse_args()

    entries = fetch_entries()
    results = {e["id"]: evaluate(e) for e in entries}

    if args.failing:
        n = args.failing
        bad = [e for e in entries if not results[e["id"]][n]]
        print(f"קריטריון {n} — {TITLES[n]}: {len(bad)} נכשלים")
        for e in bad[:40]:
            print(f"  {e['id']}  {e['title'][:60]}")
        if len(bad) > 40:
            print(f"  ... ועוד {len(bad) - 40}")
        return

    total = len(entries)
    print(f"תקן דף המעשה — {total} מעשים\n")
    print(f"{'#':>3}  {'קריטריון':<28} {'עומדים':>8}  {'נכשלים':>8}")
    passes = Counter()
    for n in sorted(TITLES):
        ok = sum(1 for r in results.values() if r[n])
        passes[n] = ok
        print(f"{n:>3}  {TITLES[n]:<28} {ok:>8}  {total - ok:>8}")

    perfect = sum(1 for r in results.values() if all(r.values()))
    print(f"\nעומדים בכל התקן: {perfect} מתוך {total}")
    scores = Counter(sum(r.values()) for r in results.values())
    print("התפלגות ניקוד (מתוך %d): %s" % (len(TITLES), dict(sorted(scores.items()))))

    if args.json:
        Path(args.json).write_text(
            json.dumps(
                {e["id"]: {"title": e["title"], "checks": results[e["id"]]} for e in entries},
                ensure_ascii=False,
                indent=1,
            )
        )
        print(f"\nדוח מלא: {args.json}")


if __name__ == "__main__":
    sys.exit(main())
