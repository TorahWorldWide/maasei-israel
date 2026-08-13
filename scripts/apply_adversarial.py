#!/usr/bin/env python3
"""Write an adversarial review into the deed it judged — rule 140, and 150 after it.

The review itself lands in `audit.adversarial_review`: that is the reader's
signature, and it is the only thing on the page that can say "verified" rather
than "the fields are full". Its severe and moderate findings become open
`discrepancies` carrying `found_by` and no `closed_by` — because the finder may
not close its own gap, and a page with an open gap is `partial` until somebody
else closes it.

  python3 scripts/apply_adversarial.py                 # dry-run
  python3 scripts/apply_adversarial.py --apply --ids <id>
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_claims import run_sql  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = Path("/tmp/adversarial-out")
BACKUPS = ROOT / "docs" / "enrichment" / "backups"
UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
BY = "adversarial-review/opus-5"
OPENS = {"severe", "moderate"}


def lit(value):
    if value is None:
        return "NULL"
    return "'" + str(value).replace("'", "''") + "'"


def jsonb(value):
    return lit(json.dumps(value, ensure_ascii=False)) + "::jsonb"


def gaps_from(findings, now):
    return [
        {
            "what": f.get("what"),
            "where": f.get("where"),
            "severity": f.get("severity"),
            "evidence": f.get("evidence"),
            "source_url": f.get("source_url"),
            "found_by": BY,
            "found_at": now,
        }
        for f in findings if f.get("severity") in OPENS
    ]


def build_update(doc, row):
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    audit = dict(row.get("audit") or {})
    findings = doc.get("findings") or []
    audit["adversarial_review"] = {
        "at": now,
        "by": BY,
        "verdict": doc.get("verdict") or "",
        "claims_checked": doc.get("claims_checked"),
        "findings": findings,
        "held": doc.get("held") or [],
    }
    # A gap the review just opened joins the ones already open; a gap it repeats
    # is not a second gap.
    existing = [d for d in (audit.get("discrepancies") or []) if isinstance(d, dict)]
    known = {(d.get("what"), d.get("where")) for d in existing}
    fresh = [g for g in gaps_from(findings, now) if (g["what"], g["where"]) not in known]
    audit["discrepancies"] = existing + fresh
    open_gaps = [d for d in audit["discrepancies"] if not d.get("closed_by")]
    if open_gaps and audit.get("state") == "complete":
        audit["state"] = "partial"
        audit["missing"] = sorted(set((audit.get("missing") or [])
                                      + [f"פער פתוח מביקורת אדברסרית: {d['what']}"
                                         for d in open_gaps]))
    return {"audit": jsonb(audit)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--ids", nargs="*")
    args = ap.parse_args()

    docs = []
    for path in sorted(OUT.glob("*.json")):
        if not UUID.match(path.stem):
            continue
        if args.ids and path.stem not in args.ids:
            continue
        doc = json.loads(path.read_text())
        doc["id"] = path.stem
        docs.append(doc)
    if not docs:
        sys.exit("no adversarial reviews in /tmp/adversarial-out")

    ids = ",".join(lit(d["id"]) for d in docs)
    rows = {r["id"]: r for r in run_sql(f"SELECT * FROM entries WHERE id IN ({ids})")}

    if not args.apply:
        for doc in docs:
            row = rows.get(doc["id"])
            if not row:
                print(f"SKIP {doc['id']} — not in database")
                continue
            findings = doc.get("findings") or []
            by_severity = {s: sum(1 for f in findings if f.get("severity") == s)
                           for s in ("severe", "moderate", "minor")}
            print(f"{row['title'][:52]}  בדק {doc.get('claims_checked')} טענות  "
                  f"ממצאים {by_severity}")
        print(f"\ndry-run — {len(docs)} reviews. Re-run with --apply")
        return

    BACKUPS.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    (BACKUPS / f"pre-adversarial-{stamp}.json").write_text(
        json.dumps(list(rows.values()), ensure_ascii=False, indent=2))

    written = []
    for doc in docs:
        fresh = run_sql(f"SELECT * FROM entries WHERE id = {lit(doc['id'])}")
        if not fresh:
            continue
        sets = build_update(doc, fresh[0])
        assignments = ", ".join(f"{c} = {v}" for c, v in sets.items())
        run_sql(f"UPDATE entries SET {assignments} WHERE id = {lit(doc['id'])};")
        written.append(doc["id"])
        print(f"written: {fresh[0]['title'][:58]}")

    from deed_standard import AUTO_RULES, evaluate  # noqa: E402
    ids = ",".join(lit(i) for i in written)
    print(f"\n{len(written)} reviews written. Read-back:")
    for row in run_sql(f"SELECT * FROM entries WHERE id IN ({ids})"):
        result = evaluate(row)
        failed = [n for n in AUTO_RULES if not result.get(n)]
        print(f"  {row['title'][:58]}  {len(AUTO_RULES)-len(failed)}/{len(AUTO_RULES)}"
              + (f"  נכשל: {failed}" if failed else "  — עובר הכל"))


if __name__ == "__main__":
    main()
