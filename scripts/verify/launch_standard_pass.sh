#!/bin/bash
# Queue-based lane runner for the deed-standard pass. Workers = Opus 5.0
# (Tomer's decision 9.8.2026 — not Sonnet). Detached, disk-first, heartbeat.
#
#   nohup scripts/verify/launch_standard_pass.sh 3 >/dev/null 2>&1 &
#
# Queue: /tmp/enrich-queue.txt (built by dump_enrich_rows.py). Progress:
# tail /tmp/enrich-logs/status-pass.txt. A LIMIT line = lane sleeping 30m on 429.
cd /home/ubuntu/maasei-israel || exit 1
LANES="${1:-3}"
Q=/tmp/enrich-queue.txt
LOCK=/tmp/enrich-queue.lock
LOGS=/tmp/enrich-logs
ST="$LOGS/status-pass.txt"
mkdir -p /tmp/enrich-out /tmp/enrich-out/applied "$LOGS"
touch "$LOCK"

pop()     { flock "$LOCK" bash -c "head -n1 '$Q'; sed -i '1d' '$Q'"; }
requeue() { flock "$LOCK" bash -c "echo '$1' >> '$Q'"; }

lane() {
  n="$1"
  while :; do
    id="$(pop)"
    [ -z "$id" ] && break
    if [ -s "/tmp/enrich-out/${id}.json" ] || [ -s "/tmp/enrich-out/applied/${id}.json" ]; then
      echo "SKIP $id already-done $(date +%H:%M)" >> "$ST"; continue
    fi
    if [ ! -s "/tmp/enrich-in/${id}.json" ]; then
      echo "NOIN $id missing input row $(date +%H:%M)" >> "$ST"; continue
    fi
    timeout 2400 claude -p "אתה סוכן העשרה בפרויקט 'מעשי ישראל'.

קרא קודם כל את התדריך המלא: /home/ubuntu/maasei-israel/scripts/verify/ENRICH-BRIEF.md — הוא מגדיר את היעד, את שדות התקן החדשים (מיקום, אנשים, תגים, locator, published), את התקציב הקשיח, ואת מבנה התוצר. פעל לפיו מילה במילה.

המעש שלך: /tmp/enrich-in/${id}.json (קרא אותו — זו השורה האמיתית מהמסד)
התוצר שלך: /tmp/enrich-out/${id}.json
היומן שלך: /tmp/enrich-out/${id}.journal.md — תוצר שני וחובה, לפי סעיף 'יומן עבודה' בתדריך. כתוב אותו תוך כדי העבודה ולא בסוף מהזיכרון. יומן חסר = המעש לא נגמר.

תזכורות קריטיות:
- חמישה דומיינים שונים, לא חמישה ציטוטים מאותו אתר.
- כל ציטוט חייב להימצא מילה-במילה בדף שמשכת בפועל. לא מצאת = לא משתמש. אל תתפור שני משפטים לציטוט אחד.
- לכל ציטוט: locator + published. לציטוט עברי: quote_en.
- מיקום עם precision כן, עיר מומצאת לא. אנשים עברית+אנגלית. תגים מהרשימות הסגורות בלבד.
- תקציב קשיח: 40 פעולות רשת. נגמר = כתוב partial עם missing+tried. דומיין שחסם = נטוש מיד.
- אל תיגע במסד, אל תריץ SQL, אל תעשה git commit.
- כתוב את קובץ ה-JSON מיד כשסיימת, לפני שאתה כותב סיכום.
דווח עד 150 מילים." \
      --permission-mode bypassPermissions --model claude-opus-5 \
      > "$LOGS/${id}.log" 2>&1
    rc=$?
    if [ -s "/tmp/enrich-out/${id}.json" ] && \
       python3 -c "import json;json.load(open('/tmp/enrich-out/${id}.json'))" 2>/dev/null; then
      j=nojournal; [ -s "/tmp/enrich-out/${id}.journal.md" ] && j=journal-ok
      echo "DONE $id rc=$rc out-ok $j $(date +%H:%M)" >> "$ST"
    elif grep -qiE "usage limit|rate.?limit|429|overloaded|quota" "$LOGS/${id}.log"; then
      echo "LIMIT lane$n $id sleeping-30m $(date +%H:%M)" >> "$ST"
      requeue "$id"
      sleep 1800
    elif [ ! -f "$LOGS/retry-${id}" ]; then
      touch "$LOGS/retry-${id}"
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
