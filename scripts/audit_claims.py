#!/usr/bin/env python3
"""Dry defect scanner for every published deed. Zero model tokens, no network.

Reads the live table, extracts each checkable atom (years, quantities,
superlatives, attribution verbs) and flags the defect classes that the
2026-08-07 random audit of 5 entries actually produced. Its job is to decide
*which* entries deserve a model, never to decide whether a claim is true.

Output: data/audit/claims.json + a printed summary.
Read docs/plans/plan-5-accuracy.md before changing the detectors.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict

CFG = os.path.expanduser("~/.hermes/maasei_company/config.json")
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "audit", "claims.json")
TEXT_FIELDS = ("title", "description", "act", "ripple")

# Each detector's weight in the risk score. Tuned so that the four defects the
# random sample produced would all have surfaced in the top decile.
SEVERITY = {
    "no_citation": 5,
    "wiki_only": 4,
    "year_predates_text": 4,
    "num_conflict": 4,
    "year_absent_from_text": 2,
    "decay_number": 2,
    "superlative": 2,
    "myth_verb": 2,
    "he_broken": 1,
}

YEAR_RE = re.compile(r"\b(1[0-9]{3}|20[0-9]{2}|2100)\b")
NUM_UNIT_RE = re.compile(r"(\d[\d,\.]*)\s*(?:מיליון|מיליוני)?\s*([֐-׿]{3,})")
SUPERLATIVES = ("הראשון בעולם", "הראשונה בעולם", "היחיד בעולם", "הגדול ביותר",
                "הגדולה ביותר", "פורץ דרך", "חסר תקדים", "לראשונה בהיסטוריה")
MYTH_VERBS = ("מימן", "מימנה", "הציל את המדינה", "המציא את", "אבי ה", "הבטיח את")
DECAY_WORDS = ("מיליון", "אלף", "מדינות", "כפרים", "מטופלים", "ילדים", "מכשירים",
               "בתי ספר", "עד היום", "כיום", "נכון להיום")


def run_sql(sql):
    cfg = json.load(open(CFG))
    body = json.dumps({"query": sql}, ensure_ascii=False)
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as bf:
        bf.write(body)
        bp = bf.name
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as cf:
        cf.write('header = "Authorization: Bearer ' + cfg["mgmt_token"] + '"\n')
        cf.write('header = "Content-Type: application/json"\n')
        cp = cf.name
    try:
        url = f"https://api.supabase.com/v1/projects/{cfg['project_ref']}/database/query"
        out = subprocess.run(
            ["curl", "-s", "-4", "-K", cp, "-X", "POST", url,
             "--data-binary", "@" + bp, "-w", "\n__HTTP__%{http_code}"],
            capture_output=True, text=True, timeout=90).stdout
        m = re.search(r"__HTTP__(\d+)\s*$", out)
        if not m or m.group(1) != "201":
            sys.exit(f"SQL failed: {out[:400]}")
        return json.loads(out[: m.start()] or "[]")
    finally:
        for p in (bp, cp):
            try:
                os.unlink(p)
            except OSError:
                pass


def blob(e):
    return " ".join(str(e.get(f) or "") for f in TEXT_FIELDS)


def hosts(e):
    urls = [e.get("source_url") or ""] + [c.get("source_url", "") for c in (e.get("citations") or [])]
    return {u.split("/")[2].lower() for u in urls if u.startswith("http")}


def detect(e):
    """Return {flag: evidence}. Evidence is short — it is what a human reads first."""
    flags = {}
    text = blob(e)
    cites = e.get("citations") or []
    hs = hosts(e)

    if not cites:
        flags["no_citation"] = "אין ציטוטים כלל"
    if hs and all("wikipedia.org" in h or "wikimedia.org" in h for h in hs):
        flags["wiki_only"] = "ויקיפדיה בלבד: " + ", ".join(sorted(hs))

    year = e.get("year")
    text_years = sorted({int(y) for y in YEAR_RE.findall(text)})
    if year and text_years:
        # The rasagiline class: the deed itself is dated earlier than the
        # headline year we recorded (approval/publication year, not act year).
        earlier = [y for y in text_years if y < year - 2]
        if earlier:
            flags["year_predates_text"] = f"שנה רשומה {year}, בטקסט מוקדם יותר: {earlier}"
        elif year not in text_years:
            flags["year_absent_from_text"] = f"שנה רשומה {year}, בטקסט: {text_years}"

    # Same noun, two different magnitudes across the entry's own fields.
    by_unit = defaultdict(set)
    for f in TEXT_FIELDS:
        for num, unit in NUM_UNIT_RE.findall(str(e.get(f) or "")):
            by_unit[unit].add(num.rstrip(".").replace(",", ""))
    conflicts = {u: v for u, v in by_unit.items() if len(v) > 1}
    if conflicts:
        flags["num_conflict"] = "; ".join(f"{u}: {sorted(v)}" for u, v in list(conflicts.items())[:3])

    hit = [w for w in SUPERLATIVES if w in text]
    if hit:
        flags["superlative"] = ", ".join(hit)
    hit = [w for w in MYTH_VERBS if w in text]
    if hit:
        flags["myth_verb"] = ", ".join(hit)

    # Self-reported figures decay: the org's page says something else today.
    org_sourced = any(("wikipedia" in h) or (h not in ("", None) and h.count(".") <= 2) for h in hs)
    hit = [w for w in DECAY_WORDS if w in text]
    if hit and org_sourced:
        flags["decay_number"] = ", ".join(hit[:4])

    broken = []
    for f in TEXT_FIELDS:
        t = str(e.get(f) or "")
        m = re.search(r"\b([֐-׿]{3,})\s+\1\b", t)
        if m:
            broken.append(f"כפילות מילה: {m.group(1)}")
        if re.search(r"[֐-׿],[֐-׿]", t):
            broken.append("פסיק בלי רווח")
    if broken:
        flags["he_broken"] = "; ".join(sorted(set(broken))[:3])
    return flags


def main():
    rows = run_sql(
        "select id, title, description, act, ripple, year, category, "
        "source_url, source_label, citations from entries "
        "where status = 'approved' order by year")
    report, counts = [], Counter()
    for e in rows:
        flags = detect(e)
        score = sum(SEVERITY[f] for f in flags)
        counts.update(flags.keys())
        report.append({"id": e["id"], "year": e.get("year"),
                       "title": (e.get("title") or "")[:70],
                       "risk": score, "flags": flags})
    report.sort(key=lambda r: -r["risk"])

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"total": len(rows), "counts": dict(counts), "entries": report},
                  f, ensure_ascii=False, indent=1)

    print(f"{len(rows)} מעשים נסרקו\n")
    for flag, n in counts.most_common():
        print(f"  {n:4}  {flag}  (חומרה {SEVERITY[flag]})")
    clean = sum(1 for r in report if not r["flags"])
    print(f"\n  {clean:4}  נקיים לגמרי בסריקה היבשה")
    print(f"\nעשרת הסיכונים הגבוהים:")
    for r in report[:10]:
        print(f"  {r['risk']:3}  {r['year']}  {r['title'][:52]}")
        for k, v in r["flags"].items():
            print(f"        {k}: {v[:90]}")
    print(f"\n→ {os.path.relpath(OUT)}")


if __name__ == "__main__":
    main()
