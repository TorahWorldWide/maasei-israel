#!/usr/bin/env python3
"""Dump every live deed as a compact reading block for the 2026-08-15 triage scan.

The scan reads the page and the sources listed on it — nothing else. Prose is
given in full in Hebrew; English is represented by its title and summary plus a
mechanical parity check, because a translation that matches on numbers and field
coverage does not need a second full read to be triaged.

  python3 scripts/triage_dump.py            # /tmp/triage/batch_NN.md, 25 per file
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_claims import run_sql  # noqa: E402

OUT = Path("/tmp/triage")
BATCH = 25
PROSE = ["summary_short", "description", "act", "ripple", "origin_story",
         "aftermath", "recognition"]
NUM = re.compile(r"\d[\d,.]*")
CAUTION = Path(__file__).resolve().parent.parent / "docs" / "SOURCES-CAUTION.md"


def numbers(text):
    return {n.rstrip(".,") for n in NUM.findall(text or "")}


def main():
    rows = run_sql("""
        select id, title, title_en, year, category, deed_type, actor_type,
               beneficiary, location, people, honors, numbers, status,
               summary_short, description, act, ripple, origin_story, aftermath,
               recognition, summary_short_en, description_en, act_en, ripple_en,
               origin_story_en, aftermath_en, recognition_en,
               citations, source_url, source_label, media_type, media_url,
               media_urls, canonical_type
        from entries order by created_at
    """)
    caution = set()
    if CAUTION.exists():
        caution = set(re.findall(r"[a-z0-9.-]+\.[a-z]{2,}", CAUTION.read_text().lower()))

    OUT.mkdir(exist_ok=True)
    index = []
    for start in range(0, len(rows), BATCH):
        chunk = rows[start:start + BATCH]
        parts = []
        for i, r in enumerate(chunk, start + 1):
            he = " ".join(r.get(f) or "" for f in PROSE)
            en = " ".join(r.get(f + "_en") or "" for f in PROSE)
            miss = [f for f in PROSE if (r.get(f) or "").strip()
                    and not (r.get(f + "_en") or "").strip()]
            only_he = numbers(he) - numbers(en)
            cits = r.get("citations") or []
            domains = [re.sub(r"^https?://(www\.)?([^/]+).*", r"\2", c.get("source_url") or "")
                       for c in cits if isinstance(c, dict)]
            wiki = [d for d in domains if "wikipedia" in d or "wikiwand" in d]
            flagged = [d for d in domains if d in caution]
            media = r.get("media_urls") or ([r["media_url"]] if r.get("media_url") else [])

            b = [f"### [{i}] {r['id']}",
                 f"title_he: {r['title']}",
                 f"title_en: {r.get('title_en') or '— חסר —'}",
                 f"meta: year={r.get('year')} | category={r.get('category')} | "
                 f"deed_type={r.get('deed_type')} | actor_type={r.get('actor_type')} | "
                 f"beneficiary={r.get('beneficiary')} | status={r.get('status')} | "
                 f"canonical_type={r.get('canonical_type') or 'ריק'}",
                 f"mech: citations={len(cits)} | wikipedia_cits={len(wiki)} | "
                 f"caution_domains={sorted(set(flagged)) or '—'} | media={len(media)} | "
                 f"en_missing_fields={miss or '—'} | "
                 f"numbers_he_not_in_en={sorted(only_he)[:12] or '—'} | "
                 f"honors={'yes' if r.get('honors') else 'no'}",
                 ]
            for f in PROSE:
                if (r.get(f) or "").strip():
                    b.append(f"{f}: {r[f].strip()}")
            b.append(f"summary_short_en: {(r.get('summary_short_en') or '— חסר —').strip()}")
            if cits:
                b.append("citations:")
                for j, c in enumerate(cits, 1):
                    if not isinstance(c, dict):
                        b.append(f"  {j}. {c}")
                        continue
                    q = (c.get("quote") or c.get("quote_en") or "").strip().replace("\n", " ")
                    b.append(f"  {j}. [{c.get('source_label') or c.get('source_label_en') or '?'}] "
                             f"{c.get('source_url') or 'ללא קישור'}"
                             f"{' | ארכוב: יש' if c.get('archived_url') else ' | ארכוב: אין'}"
                             f"\n     ציטוט: {q[:400]}")
            else:
                b.append("citations: — אין ציטוטים כלל —")
            parts.append("\n".join(b))

        path = OUT / f"batch_{start // BATCH + 1:02d}.md"
        path.write_text("\n\n".join(parts), encoding="utf-8")
        index.append((path.name, len(chunk), path.stat().st_size))

    for name, n, size in index:
        print(f"{name}: {n} deeds, {size:,} chars")
    print(f"total {len(rows)} deeds")


if __name__ == "__main__":
    main()
