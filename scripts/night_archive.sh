#!/bin/bash
# Rule 136 on its own lane. Archiving talks to Tomer's PC over one SSH channel
# at 20s per URL, so a batch runs for half an hour; if it shared the apply lock
# every deed a worker finished in that half hour would sit unwritten. It takes
# its own lock instead, and skips any deed whose document has not been applied
# yet — archiving first and applying second would overwrite the archived_url it
# had just written.
exec 9>/tmp/night-arch.lock
flock -n 9 || exit 0
cd /home/ubuntu/maasei-israel || exit 1
export PATH="$PATH:/home/ubuntu/.local/bin"

python3 - /tmp/night-targets.txt > /tmp/night-arch.txt <<'PY'
import sys, glob, os
sys.path.insert(0, "scripts")
from deed_standard import fetch_entries, evaluate
try:
    want = {l.strip() for l in open(sys.argv[1]) if l.strip()}
except OSError:
    want = set()
pending = set()
for pat in ("/tmp/enrich-out/*.json", "/tmp/compliance-out/*.json"):
    for f in glob.glob(pat):
        pending.add(os.path.basename(f).split(".")[0])
for e in fetch_entries():
    if e["id"] in want and e["id"] not in pending and not evaluate(e).get(136):
        print(e["id"])
PY

[ -s /tmp/night-arch.txt ] || exit 0
echo "=== $(date -u +%H:%MZ) archiving $(wc -l < /tmp/night-arch.txt) deeds (routes through Tomer's PC)"
timeout 3000 python3 scripts/archive_deed.py --apply --file /tmp/night-arch.txt 2>&1 | tail -20
