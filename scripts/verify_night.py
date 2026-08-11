#!/usr/bin/env python3
"""Rule 140 — re-fetch every quote of a deed and prove it is really there.

The worker says its quotes are verbatim. This does not believe it: it fetches
each source again through every route verify_best.py knows and reports what it
found. The result is written next to the deed so the review page can show Tomer
a number he did not have to take on trust.

  python3 scripts/verify_night.py <deed-id> [<deed-id> ...]

Writes docs/enrichment/verify/<id>.json — counts plus any quote that failed.
"""
import ast
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PASS_OUT = ROOT / "docs" / "enrichment" / "standard-pass"
OUT = ROOT / "docs" / "enrichment" / "verify"
VERIFIER = ROOT / "scripts" / "verify" / "verify_best.py"


def run(deed_id):
    doc = PASS_OUT / f"{deed_id}.json"
    if not doc.exists():
        return None
    # verify_best.py imports fetchit from /tmp
    # Always overwrite: a fix to the fetcher that never reaches /tmp is a fix
    # that never runs, and the copy there outlives the repo's own file.
    fetchit = ROOT / "scripts" / "verify" / "fetchit.py"
    if fetchit.exists():
        Path("/tmp/fetchit.py").write_bytes(fetchit.read_bytes())

    proc = subprocess.run(
        [sys.executable, str(VERIFIER), str(doc)],
        capture_output=True, text=True, timeout=2400,
    )
    text = proc.stdout
    counts = {}
    for line in text.splitlines():
        if line.strip().startswith("{'FOUND'"):
            counts = ast.literal_eval(line.strip())
    bad = [
        line.strip() for line in text.splitlines()
        if re.search(r"\[(PARTIAL|FAIL|BLOCKED)", line)
    ]
    result = {"entry": deed_id, "counts": counts, "not_found": bad[:20]}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{deed_id}.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    total = sum(counts.values()) or 0
    print(f"{deed_id[:8]} {counts.get('FOUND', 0)}/{total} quotes verbatim"
          + (f" — {len(bad)} not clean" if bad else ""))
    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for arg in sys.argv[1:]:
        try:
            run(arg)
        except Exception as exc:  # a verifier that dies must not stop the night
            print(f"{arg[:8]} verify failed: {exc}")
