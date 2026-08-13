#!/bin/bash
# Rule 149's blind pass is the slow, serial part of each lane. It is also
# resumable, so running it ahead of the workers costs nothing and buys wall time.
cd /home/ubuntu/maasei-israel || exit 1
export PATH="$PATH:/home/ubuntu/.local/bin"
LOG=/tmp/enrich-logs/status-blind.txt
while read -r id; do
  [ -z "$id" ] && continue
  timeout 2400 python3 scripts/describe_images.py "$id" >/tmp/enrich-logs/blind-$id.log 2>&1
  n=$(python3 -c "import json;print(len(json.load(open('/tmp/blind/$id.json'))))" 2>/dev/null || echo 0)
  echo "BLIND $id $n images $(date -u +%H:%M)" >> "$LOG"
done < "$1"
echo "BLIND-PRERUN DONE $(date -u +%H:%M)" >> "$LOG"
