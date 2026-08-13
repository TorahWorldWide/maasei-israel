#!/usr/bin/env python3
"""Dump what a completion worker needs for one deed, and nothing else.

The deed already passes the research rules. What it fails is the rules that
entered the standard after it was written — 148 numbers, 150 gaps, 151 honors,
157 the moment — plus rule 20 where the English half is short. Handing the
worker the whole row would invite it to rewrite research that is verified.

The numerals the page shows are computed here rather than left to the worker to
find: a worker that has to hunt for its own targets misses the one in the
title. Every quote already on the page comes along, because most numbers are
already sitting in a verified quote and covering them costs no network at all.

  python3 scripts/completion_context.py <deed-id> --write  # /tmp/completion/<id>.context.json
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_claims import run_sql  # noqa: E402
from deed_standard import NUMBER_FIELDS, digits, numerals, language_parity  # noqa: E402

OUT = Path("/tmp/completion")


def uncovered_numerals(row):
    """Rule 148 — every numeral the reader sees, minus the deed's own year."""
    seen = set()
    for field in NUMBER_FIELDS:
        seen |= numerals(row.get(field))
    year = digits(row.get("year"))
    if len(year) == 4:
        seen.discard(year)
    covered = set()
    for item in (row.get("numbers") or []):
        if isinstance(item, dict):
            covered.add(digits(item.get("value")))
            covered |= numerals(item.get("as_written"))
    return sorted(seen - covered, key=lambda n: (-len(n), n))


def where(row, numeral):
    """The fields a numeral appears in — the worker fixes text, not a set."""
    return [f for f in NUMBER_FIELDS if numeral in numerals(row.get(f))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("deed_id")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    rows = run_sql(
        "select id, title, title_en, year, summary_short, summary_short_en, "
        "description, description_en, act, act_en, ripple, ripple_en, "
        "origin_story, origin_story_en, aftermath, aftermath_en, "
        "recognition, recognition_en, honors, numbers, citations, media_urls, audit "
        "from entries where id = '" + args.deed_id.replace("'", "") + "'"
    )
    if not rows:
        sys.exit("no such deed")
    row = rows[0]
    audit = row.get("audit") or {}
    provenance = audit.get("image_provenance") or []

    context = {
        "entry": row["id"],
        "title": row.get("title"),
        "title_en": row.get("title_en"),
        "year": row.get("year"),
        # Rule 148 — the whole job, precomputed. Empty means the rule is already
        # satisfied and the worker writes numbers: [] and moves on.
        "numerals_to_cover": [
            {"value": n, "fields": where(row, n)} for n in uncovered_numerals(row)
        ],
        "text": {f: row.get(f) for f in NUMBER_FIELDS if row.get(f)},
        "text_en": {f + "_en": row.get(f + "_en")
                    for f in NUMBER_FIELDS if row.get(f + "_en")},
        # Most numbers are already inside a verified quote. Covering one from
        # here costs nothing; going to the network for it costs budget.
        "quotes_on_the_page": [
            {"source_url": c.get("source_url"), "label": c.get("source_label"),
             "quote": c.get("quote"), "quote_en": c.get("quote_en"),
             "locator": c.get("locator"), "published": c.get("published")}
            for c in (row.get("citations") or [])
        ],
        "honors": row.get("honors"),
        "numbers": row.get("numbers"),
        "state": audit.get("state"),
        "unresolved": audit.get("unresolved") or [],
        "missing": audit.get("missing") or [],
        "tried": audit.get("tried") or [],
        "discrepancies": audit.get("discrepancies"),
        "the_moment": audit.get("the_moment"),
        "images_under_review": [p.get("url") for p in provenance
                                if p.get("license") == "under_review"],
        "images": [{"url": p.get("url"), "caption_he": p.get("caption_he"),
                    "caption_en": p.get("caption_en")} for p in provenance],
        # Rule 160/20 — fields whose two languages disagree on a number.
        "language_parity_off": language_parity(row),
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
