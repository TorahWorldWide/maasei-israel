#!/bin/bash
# Queue runner for stage 6 — closing what the adversarial review opened.
# A fresh worker per deed, and never the one that found the gap (rule 150).
#
#   nohup scripts/verify/launch_fix.sh 2 >/dev/null 2>&1 &
#
# Queue: /tmp/fix-queue.txt. Progress: tail /tmp/enrich-logs/status-fix.txt
cd /home/ubuntu/maasei-israel || exit 1
LANES="${1:-2}"
Q=/tmp/fix-queue.txt
LOCK=/tmp/fix-queue.lock
LOGS=/tmp/enrich-logs
ST="$LOGS/status-fix.txt"
mkdir -p /tmp/fix /tmp/fix-out "$LOGS"
touch "$LOCK"

pop()     { flock "$LOCK" bash -c "head -n1 '$Q'; sed -i '1d' '$Q'"; }
requeue() { flock "$LOCK" bash -c "echo '$1' >> '$Q'"; }

lane() {
  n="$1"
  while :; do
    id="$(pop)"
    [ -z "$id" ] && break
    if [ -s "/tmp/fix-out/${id}.json" ]; then
      echo "SKIP $id already-done $(date +%H:%M)" >> "$ST"; continue
    fi
    ctx="/tmp/fix/${id}.context.json"
    python3 scripts/fix_context.py "$id" --write >/dev/null 2>&1
    if [ ! -s "$ctx" ]; then
      echo "NOGAPS $id $(date +%H:%M)" >> "$ST"; continue
    fi
    timeout 3600 claude -p "קורא עוין עבר על דף באתר 'מעשי ישראל' ורשם ממצאים נגדו. אתה נשלח לסגור אותם — לא כתבת את הדף ולא כתבת את הביקורת.

התדריך שלך: /home/ubuntu/maasei-israel/scripts/verify/FIX-BRIEF.md — קרא אותו במלואו לפני שאתה מתחיל.
ההקשר שלך: ${ctx}
התוצר שלך: /tmp/fix-out/${id}.json
היומן שלך: /tmp/fix-out/${id}.journal.md

לכל ממצא בדיוק שתי תשובות כשרות: תיקנתי, או הממצא שגוי והנה הראיה שמשכתי בעצמי. אל תסגור ממצא בלי אחת מהשתיים. תיקון עובדתי הוא תמיד זוג — עברית ואנגלית. כתוב את ה-JSON מיד כשסיימת, לפני סיכום. דווח עד 150 מילים." \
      --permission-mode bypassPermissions --model claude-opus-5 \
      > "$LOGS/fix-${id}.log" 2>&1
    rc=$?
    if [ -s "/tmp/fix-out/${id}.json" ] && \
       python3 -c "import json;json.load(open('/tmp/fix-out/${id}.json'))" 2>/dev/null; then
      j=nojournal; [ -s "/tmp/fix-out/${id}.journal.md" ] && j=journal-ok
      echo "DONE $id rc=$rc out-ok $j $(date +%H:%M)" >> "$ST"
    elif grep -qiE "usage limit|rate.?limit|429|overloaded|quota" "$LOGS/fix-${id}.log"; then
      echo "LIMIT lane$n $id sleeping-30m $(date +%H:%M)" >> "$ST"
      requeue "$id"
      sleep 1800
    elif [ ! -f "$LOGS/fretry-${id}" ]; then
      touch "$LOGS/fretry-${id}"
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
