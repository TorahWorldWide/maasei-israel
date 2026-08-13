#!/usr/bin/env python3
"""Dump a deed as a hostile reader should meet it — claims, and nothing else.

Rule 140. What the page asserts and what it cites are in; what the workers said
about themselves is out. A reviewer who reads `unresolved` inherits the writer's
own account of where the weak spots are, and then checks exactly there — which
is the opposite of a surprise audit.

  python3 scripts/adversarial_context.py <deed-id> --write
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_claims import run_sql  # noqa: E402

OUT = Path("/tmp/adversarial")
FIELDS = ["title", "title_en", "summary_short", "summary_short_en",
          "description", "description_en", "act", "act_en", "ripple", "ripple_en",
          "origin_story", "origin_story_en", "aftermath", "aftermath_en",
          "recognition", "recognition_en", "year"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("deed_id")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    rows = run_sql("select * from entries where id = '"
                   + args.deed_id.replace("'", "") + "'")
    if not rows:
        sys.exit("no such deed")
    row = rows[0]
    audit = row.get("audit") or {}

    context = {
        "entry": row["id"],
        "live_page": f"https://maasei-israel.vercel.app/deed/{row['id']}",
        "text": {f: row.get(f) for f in FIELDS if row.get(f)},
        "citations": [
            {k: c.get(k) for k in ("source_url", "source_label", "quote", "quote_en",
                                   "locator", "published") if c.get(k)}
            for c in (row.get("citations") or [])
        ],
        "images": [
            {k: p.get(k) for k in ("url", "caption_he", "caption_en", "caption_long_he",
                                   "credit", "shot_when", "source_page") if p.get(k)}
            for p in (audit.get("image_provenance") or [])
        ],
        "honors": row.get("honors"),
        "numbers": row.get("numbers"),
    }
    text = json.dumps(context, ensure_ascii=False, indent=2)
    if args.write:
        OUT.mkdir(parents=True, exist_ok=True)
        path = OUT / f"{row['id']}.context.json"
        path.write_text(text, encoding="utf-8")
        print(path)
    else:
        print(text)


if __name__ == "__main__":
    main()
