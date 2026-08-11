#!/usr/bin/env python3
"""Generate the worker brief for one deed of a standard pass.

Every worker in a run must receive the same instructions, or the run measures
the briefs instead of the deeds. The brief is assembled from the canonical
document — never retyped — so a rule that changes there reaches the next worker
without anyone remembering to copy it.

  python3 scripts/standard_pass_brief.py <deed-id>            # print it
  python3 scripts/standard_pass_brief.py <deed-id> --write    # /tmp/briefs/<id>.md
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_claims import run_sql  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "DEED-STANDARD.md"
BRIEFS = Path("/tmp/briefs")

# Chapters the worker is judged on. Design (ט) and the company's own operating
# rules live elsewhere — a worker handed all 128 rules reads none of them.
WORKER_CHAPTERS = [
    "פרק 0 — הכללים שמעל הכל",
    "פרק א — מקורות, לב האתר",
    "פרק ב — תמונות",
    "פרק ג — סרטונים",
    "פרק ד — תוכן",
    "פרק ה — כותרות",
    "פרק ו — מטא-נתונים",
    "פרק ז — כשלא מצליחים: מנגנון העצירה",
    "פרק י — מה אסור",
]
# Process rules that bind the worker itself, pulled in by number from פרק ח.
WORKER_PROCESS_RULES = [33, 81, 87, 89, 122, 125]

# Prose sections the worker needs verbatim. A numbered row says *that* a field
# must be filled; these say *what belongs in it*, they carry no rule number, and
# so the row scraper below cannot see them.
WORKER_SECTIONS = [
    "מילון פרשנות לפי קטגוריה — כללים 64–67",
    # Rules 38-40 and 123 say "from the closed list below" — and the list is
    # prose. A worker told to obey a list it was never shown invents one.
    "סוג המעשה — רשימה סגורה",
    "מיקום — עד כמה מדויק",
    # Rule 130 is the one field written after everything else. The row says the
    # sentence count; this says what makes a summary worth reading.
    "130 — התקציר נכתב אחרון, ונקרא ראשון",
]

ROW_FIELDS = [
    "id", "title", "year", "description", "act", "ripple",
    "source_url", "source_label", "media_url", "media_urls", "citations",
]


def rule_rows():
    """Every `| N | requirement | test | kind | when |` row, with its chapter."""
    rows, chapter = [], ""
    for line in DOC.read_text().splitlines():
        if line.startswith("## "):
            chapter = line[3:].strip()
        m = re.match(r"^\|\s*(\d+)\s*\|(.+)$", line)
        if m:
            cells = [c.strip() for c in m.group(2).split("|")]
            rows.append({
                "n": int(m.group(1)), "chapter": chapter,
                "requirement": cells[0], "test": cells[1] if len(cells) > 1 else "",
                "kind": cells[2] if len(cells) > 2 else "",
            })
    return rows


def section_text(title):
    """One `### title` block from the document, verbatim, heading included."""
    lines, taking = [], False
    for line in DOC.read_text().splitlines():
        if line.startswith("### "):
            if taking:
                break
            taking = line[4:].strip() == title
        elif line.startswith("## ") and taking:
            break
        if taking:
            lines.append(line)
    if not lines:
        sys.exit(f"section not found in {DOC.name}: {title!r}")
    return "\n".join(lines).rstrip()


def rules_section():
    rows = rule_rows()
    by_chapter = {}
    for r in rows:
        if r["chapter"] in WORKER_CHAPTERS:
            by_chapter.setdefault(r["chapter"], []).append(r)

    out = []
    for chapter in WORKER_CHAPTERS:
        if chapter not in by_chapter:
            continue
        out.append(f"\n### {chapter}\n")
        for r in sorted(by_chapter[chapter], key=lambda x: x["n"]):
            out.append(f"{r['n']}. {r['requirement']}  \n   מבחן: {r['test']}")

    for title in WORKER_SECTIONS:
        out.append("\n" + section_text(title))

    out.append("\n### כללי עבודה שחלים עליך\n")
    for r in sorted((r for r in rows if r["n"] in WORKER_PROCESS_RULES), key=lambda x: x["n"]):
        out.append(f"{r['n']}. {r['requirement']}  \n   מבחן: {r['test']}")
    return "\n".join(out)


def lit(v):
    return "'" + str(v).replace("'", "''") + "'"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("deed_id")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--budget", default="1.2M טוקנים")
    args = ap.parse_args()

    rows = run_sql(f"SELECT * FROM entries WHERE id = {lit(args.deed_id)}")
    if not rows:
        sys.exit(f"deed {args.deed_id} not found")
    row = rows[0]
    current = {f: row.get(f) for f in ROW_FIELDS}

    # Rule 81: the worker must see what is already on the site, or it will
    # research a deed that already has a page under a different title.
    titles = [r["title"] for r in run_sql(
        "SELECT title FROM entries WHERE status = 'approved' ORDER BY title")]

    brief = f"""# בנייה מחדש של מעש — לפי תקן דף המעשה

אתה בונה **מחדש מאפס** את דף המעש הזה. הטקסט הקיים נכתב על ידי סוכן קודם
שטעה והמציא. הוא **רמז לכיוון בלבד** — לא מקור, ולא בסיס. כל טענה, שם, שנה
וציטוט מאומתים מחדש מול מקור חיצוני חי, או נמחקים.

## המעש כפי שהוא היום (לא לסמוך עליו)

```json
{json.dumps(current, ensure_ascii=False, indent=2, default=str)}
```

## התקן — {len([r for r in rule_rows() if r['chapter'] in WORKER_CHAPTERS])} כללים שאתה נמדד עליהם
{rules_section()}

## מה אתה מחזיר

קובץ JSON יחיד ב-`/tmp/enrich-out/{args.deed_id}.json`. **אתה לא כותב למסד
הנתונים** — יש כותב אחד בלבד, `scripts/apply_standard_pass.py`.

השדות: `id`, `title`, `title_en`, `title_reasoning`, `year`,
`description`, `description_en`, `origin_story`, `origin_story_en`,
`act`, `act_en`, `ripple`, `ripple_en`, `aftermath`, `aftermath_en`,
`recognition`, `recognition_en`, `summary_short`, `summary_short_en`,
`source_url`, `source_label`,
`source_label_en`, `citations[]`, `honors[]`, `media_urls[]`,
`image_provenance[]`, `videos[]`, `location`, `people[]`, `deed_type[]`,
`actor_type`, `beneficiary[]`, `dedup`, `lead_image_basis`,
`content_delta[]`, `removed[]`, `corrections[]`, `disputes[]`,
`unresolved[]`, `missing[]`, `tried[]`, `domains_covered`,
`spinoff_leads[]`, `person_notes[]`, `redirects[]`, `notes`, `status`.

`status` הוא אחד מ-`complete` / `partial` / `exhausted` — לפי פרק ז.

## יומן עבודה (כלל 87)

`/tmp/enrich-out/{args.deed_id}.journal.md` — מה חיפשת, מה נפל, מה הכרעת ולמה.

## תקציב (כלל 33)

{args.budget}. כשנגמר — מסיימים את מה שביד, מסמנים `partial` ומפרטים
ב-`missing`. לא ממציאים כדי לסגור פינה.

## מה כבר קיים באתר (כלל 81 — סריקת כפילויות)

{chr(10).join('- ' + t for t in titles)}

אם המעש שלך הוא כפילות של אחד מהם — **אל תמחק ואל תתעלם**: רשום את המזהה
ב-`merged_from` והסבר ב-`notes`.
"""

    if args.write:
        BRIEFS.mkdir(parents=True, exist_ok=True)
        path = BRIEFS / f"{args.deed_id}.md"
        path.write_text(brief)
        print(f"wrote {path}  ({len(brief) // 1024} KB)")
    else:
        print(brief)


if __name__ == "__main__":
    main()
