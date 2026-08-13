#!/bin/bash
# Queue runner for the surprise adversarial review — rule 140. One fresh worker
# per deed, no context from the pass that wrote it, whose job is to refute.
#
#   nohup scripts/verify/launch_adversarial.sh 3 >/dev/null 2>&1 &
#
# Queue: /tmp/adversarial-queue.txt. Progress: tail /tmp/enrich-logs/status-adversarial.txt
cd /home/ubuntu/maasei-israel || exit 1
LANES="${1:-3}"
Q=/tmp/adversarial-queue.txt
LOCK=/tmp/adversarial-queue.lock
LOGS=/tmp/enrich-logs
ST="$LOGS/status-adversarial.txt"
mkdir -p /tmp/adversarial /tmp/adversarial-out "$LOGS"
touch "$LOCK"

pop()     { flock "$LOCK" bash -c "head -n1 '$Q'; sed -i '1d' '$Q'"; }
requeue() { flock "$LOCK" bash -c "echo '$1' >> '$Q'"; }

lane() {
  n="$1"
  while :; do
    id="$(pop)"
    [ -z "$id" ] && break
    if [ -s "/tmp/adversarial-out/${id}.json" ]; then
      echo "SKIP $id already-done $(date +%H:%M)" >> "$ST"; continue
    fi
    ctx="/tmp/adversarial/${id}.context.json"
    python3 scripts/adversarial_context.py "$id" --write >/dev/null 2>&1
    if [ ! -s "$ctx" ]; then
      echo "NOCTX $id $(date +%H:%M)" >> "$ST"; continue
    fi
    timeout 3600 claude -p "אתה קורא עוין. לפניך דף אחד באתר 'מעשי ישראל', ואתה מריץ עליו ביקורת־פתע אדברסרית — כלל 140. תפקידך להפריך, לא לאשר.

התדריך שלך: /home/ubuntu/maasei-israel/scripts/verify/ADVERSARIAL-BRIEF.md — קרא אותו במלואו לפני שאתה מתחיל.
ההקשר שלך: ${ctx}
התוצר שלך: /tmp/adversarial-out/${id}.json
היומן שלך: /tmp/adversarial-out/${id}.journal.md

לא כתבת את הדף הזה ואינך ממשיך את מי שכתב. אל תקרא יומנים של עובדים קודמים — לא ב-docs/enrichment ולא ב-/tmp/completion-out ולא ב-/tmp/enrich-out. בדוק בעצמך לפחות חמישה ציטוטים מול המקור החי, את כל המספרים שבכותרת ובתקציר, ואת הדף בשתי השפות. אינך מתקן דבר — אתה רק מדווח. כתוב את ה-JSON מיד כשסיימת, לפני סיכום. דווח עד 150 מילים." \
      --permission-mode bypassPermissions --model claude-opus-5 \
      > "$LOGS/adversarial-${id}.log" 2>&1
    rc=$?
    if [ -s "/tmp/adversarial-out/${id}.json" ] && \
       python3 -c "import json;json.load(open('/tmp/adversarial-out/${id}.json'))" 2>/dev/null; then
      j=nojournal; [ -s "/tmp/adversarial-out/${id}.journal.md" ] && j=journal-ok
      echo "DONE $id rc=$rc out-ok $j $(date +%H:%M)" >> "$ST"
    elif grep -qiE "usage limit|rate.?limit|429|overloaded|quota" "$LOGS/adversarial-${id}.log"; then
      echo "LIMIT lane$n $id sleeping-30m $(date +%H:%M)" >> "$ST"
      requeue "$id"
      sleep 1800
    elif [ ! -f "$LOGS/aretry-${id}" ]; then
      touch "$LOGS/aretry-${id}"
      requeue "$id"
      echo "RETRY $id rc=$rc no-out $(date +%H:%M)" >> "$ST"
    else
      echo "FAIL $id rc=$rc no-out given-up $(date +%H:%M)" >> "$ST"
    fi
  done
  echo "LANE$n EXHAUSTED $(date +%H:%M)" >> "$ST"
}

for i in $(seq 1 "$LANES"); do lane "$i" & done
wait
echo "ALL LANES DONE $(date)" >> "$ST"
