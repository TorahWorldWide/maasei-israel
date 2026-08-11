#!/usr/bin/env python3
"""Dump what a compliance worker needs for one deed, and nothing else.

The deed already passes the research rules. What it fails is the four that were
added to the standard on 11.8 — 137 license, 147 one-line caption, 20 English
gallery, 139 living-person double bar — and all four are decided from the page's
own images and text. Handing the worker the whole row instead would invite it to
rewrite research that is already verified.

  python3 scripts/compliance_context.py <deed-id> --write   # /tmp/compliance/<id>.context.json
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_claims import run_sql  # noqa: E402

OUT = Path("/tmp/compliance")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("deed_id")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    rows = run_sql(
        "select id, title, title_en, description, description_en, act, ripple, "
        "media_urls, audit from entries where id = '" + args.deed_id.replace("'", "") + "'"
    )
    if not rows:
        sys.exit("no such deed")
    row = rows[0]
    audit = row.get("audit") or {}
    context = {
        "entry": row["id"],
        "title": row.get("title"),
        "title_en": row.get("title_en"),
        # The page text is what decides whether an image may buy a long caption
        # under rule 58: an image whose reason is already in the text may not.
        "page_text_he": " ".join(str(row.get(f) or "") for f in ("description", "act", "ripple")),
        "images": [
            {k: p.get(k) for k in
             ("url", "group", "group_en", "caption_he", "caption_en", "caption_long_he",
              "credit", "credit_en", "shot_when", "shot_when_en", "license", "source_page",
              "license_note", "why", "what_is_seen")
             if p.get(k)}
            for p in (audit.get("image_provenance") or [])
        ],
        "unresolved": audit.get("unresolved") or [],
        "missing": audit.get("missing") or [],
        "tried": audit.get("tried") or [],
        "sensitive_claims": audit.get("sensitive_claims"),
    }
    text = json.dumps(context, ensure_ascii=False, indent=2)
    if args.write:
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / f"{row['id']}.context.json").write_text(text, encoding="utf-8")
        print(OUT / f"{row['id']}.context.json")
    else:
        print(text)


if __name__ == "__main__":
    main()
