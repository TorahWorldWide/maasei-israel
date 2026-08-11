#!/bin/bash
# One supervisor tick of the night run: take whatever the lanes finished, write
# it, archive it, and print where the target stands. Safe to run at any moment —
# a worker that is still writing has no file yet, and a file already written is
# moved into applied/ so the next tick cannot write it twice.
#
#   scripts/night_apply.sh            # apply + archive + score
#   scripts/night_apply.sh --no-arch  # skip the PC-routed archiving
cd /home/ubuntu/maasei-israel || exit 1
export PATH="$PATH:/home/ubuntu/.local/bin"
TARGETS=/tmp/night-targets.txt
TOUCHED=/tmp/night-touched.txt
: > "$TOUCHED"

echo "=== $(date -u +%H:%MZ) night_apply"

# 1. standard-pass outputs
for f in /tmp/enrich-out/*.json; do
  [ -e "$f" ] || continue
  id="$(basename "$f" .json)"
  case "$id" in *.journal|*.knowledge) continue;; esac
  echo "--- apply standard-pass $id"
  if python3 scripts/apply_standard_pass.py --apply --ids "$id" 2>&1 | tail -4; then
    # The doc that was written into the database is the repo's record of what
    # the deed is made of, and the review page reads it. /tmp does not survive.
    mkdir -p docs/enrichment/standard-pass
    cp "$f" "docs/enrichment/standard-pass/${id}.json"
    [ -s "/tmp/enrich-out/${id}.journal.md" ] && \
      cp "/tmp/enrich-out/${id}.journal.md" "docs/enrichment/standard-pass/${id}.journal.md"
    mv "$f" /tmp/enrich-out/applied/ 2>/dev/null
    echo "$id" >> "$TOUCHED"
  fi
done

# 2. compliance sheets
mkdir -p /tmp/compliance-out/applied
for f in /tmp/compliance-out/*.json; do
  [ -e "$f" ] || continue
  id="$(basename "$f" .json)"
  case "$id" in *.journal) continue;; esac
  echo "--- apply compliance $id"
  cp "$f" "docs/enrichment/captions/${id}.json"
  if python3 scripts/apply_captions.py "docs/enrichment/captions/${id}.json" --apply 2>&1 | tail -3; then
    mv "$f" /tmp/compliance-out/applied/ 2>/dev/null
    echo "$id" >> "$TOUCHED"
  fi
done

# 3. archive rule 136. Not "what this tick touched" but "every target that
# still fails 136" — a deed applied by hand between ticks is then never
# stranded, and a deed already archived costs one cdx lookup to skip.
if [ "$1" != "--no-arch" ]; then
  python3 - "$TARGETS" > /tmp/night-arch.txt <<'PY'
import sys
sys.path.insert(0, "scripts")
from deed_standard import fetch_entries, evaluate
try:
    want = {l.strip() for l in open(sys.argv[1]) if l.strip()}
except OSError:
    want = set()
for e in fetch_entries():
    if e["id"] in want and not evaluate(e).get(136):
        print(e["id"])
PY
  if [ -s /tmp/night-arch.txt ]; then
    echo "--- archive $(wc -l < /tmp/night-arch.txt) deeds still failing 136 (routes through Tomer's PC)"
    timeout 3000 python3 scripts/archive_deed.py --apply --file /tmp/night-arch.txt 2>&1 | tail -20
  fi
fi

# 4. where the target stands
echo "--- scoreboard"
python3 - "$TARGETS" <<'PY'
import sys, json
sys.path.insert(0, "scripts")
from deed_standard import fetch_entries, evaluate, AUTO_RULES
try:
    want = [l.strip() for l in open(sys.argv[1]) if l.strip()]
except OSError:
    want = []
rows = fetch_entries()
full = []
for e in rows:
    r = evaluate(e)
    fails = [n for n in AUTO_RULES if not r.get(n)]
    if not fails:
        full.append(e)
    elif e["id"] in want:
        print(f"  {len(AUTO_RULES)-len(fails)}/{len(AUTO_RULES)}  {e['title'][:52]}  נכשל: {fails}")
print(f"\nעומדים בכל {len(AUTO_RULES)} הבדיקות: {len(full)} מעשים")
for e in full:
    print(f"  50/50  {e['title'][:70]}")
PY
echo "--- lanes"
echo "queue-pass: $(wc -l < /tmp/enrich-queue.txt 2>/dev/null) left | queue-compliance: $(wc -l < /tmp/compliance-queue.txt 2>/dev/null) left"
tail -4 /tmp/enrich-logs/status-pass.txt 2>/dev/null
tail -3 /tmp/enrich-logs/status-compliance.txt 2>/dev/null
pgrep -fc "launch_standard_pass|launch_compliance" | sed 's/^/runners alive: /'
