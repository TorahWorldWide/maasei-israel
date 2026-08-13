#!/usr/bin/env python3
"""Assemble a canonical page from the writer's chunk files into one document.

A canonical page is long and bilingual, so a writer that composes it in one
response loses everything if the run dies. The writer therefore saves one file
per section as it finishes it, and this stitches them together.

Expected layout under <dir>:
  fields.json     the prose columns (title, description, act, ripple, ...)
  infobox.json    {"rows": [...]}            — rule 169
  sections/NN-slug.json  {"heading","heading_en","body","body_en"} — rule 168

  python3 scripts/assemble_canonical.py docs/enrichment/canonical/lamarr/v2
"""
import json
import sys
from pathlib import Path

REQUIRED_FIELDS = ["title", "title_en", "description", "description_en",
                   "summary_short", "summary_short_en", "canonical_type"]


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    d = Path(sys.argv[1])

    doc = json.loads((d / "fields.json").read_text())

    infobox_path = d / "infobox.json"
    if infobox_path.exists():
        doc["infobox"] = json.loads(infobox_path.read_text())

    sections = []
    for path in sorted((d / "sections").glob("*.json")):
        sections.append(json.loads(path.read_text()))
    doc["sections"] = sections

    problems = [f for f in REQUIRED_FIELDS if not doc.get(f)]
    if not sections:
        problems.append("sections (empty)")
    # Rule 169: a row without a source is not a row.
    for i, row in enumerate(doc.get("infobox", {}).get("rows", [])):
        for key in ("label", "value", "source"):
            if not row.get(key):
                problems.append(f"infobox row {i} missing {key}")
    # Rule 20: no section may be Hebrew-only.
    for i, s in enumerate(sections):
        if not s.get("body_en"):
            problems.append(f"section {i} has no body_en")

    out = d / "canonical.json"
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=2))

    chars = sum(len(s.get("body", "")) for s in sections)
    print(f"{out}: {len(sections)} sections · {chars} Hebrew chars · "
          f"{len(doc.get('infobox', {}).get('rows', []))} infobox rows")
    for s in sections:
        print(f"   {s.get('heading', '(no heading)')}  [{len(s.get('body', ''))} chars]")
    if problems:
        print("\nINCOMPLETE:")
        for p in problems:
            print(f"   {p}")
        sys.exit(1)
    print("\ncomplete")


if __name__ == "__main__":
    main()
