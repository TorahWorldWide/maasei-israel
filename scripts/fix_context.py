#!/usr/bin/env python3
"""Dump one deed's open findings for the worker sent to close them — stage 6.

Rule 150 forbids the finder from closing its own gap, so this hands a fresh
worker the page and the findings against it, and nothing about who wrote either.
The reviewer's verdict comes along because it says which findings it considers
load-bearing; its `held` list does not, because a worker that reads what already
survived spends its budget re-reading it.

  python3 scripts/fix_context.py <deed-id> --write   # /tmp/fix/<id>.context.json
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_claims import run_sql  # noqa: E402

OUT = Path("/tmp/fix")
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
    review = audit.get("adversarial_review") or {}
    open_gaps = [d for d in (audit.get("discrepancies") or [])
                 if isinstance(d, dict) and not d.get("closed_by")]
    if not open_gaps:
        sys.exit("no open findings")

    context = {
        "entry": row["id"],
        "live_page": f"https://maasei-israel.vercel.app/deed/{row['id']}",
        "verdict": review.get("verdict"),
        "open_findings": open_gaps,
        "findings_full": [f for f in (review.get("findings") or [])
                          if f.get("severity") in ("severe", "moderate", "minor")],
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
        "numbers": row.get("numbers") or [],
        "honors": row.get("honors") or [],
    }
    text = json.dumps(context, ensure_ascii=False, indent=1)
    if args.write:
        OUT.mkdir(parents=True, exist_ok=True)
        path = OUT / f"{row['id']}.context.json"
        path.write_text(text)
        print(path)
    else:
        print(text)


if __name__ == "__main__":
    main()
