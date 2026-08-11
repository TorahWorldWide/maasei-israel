#!/bin/bash
# Queue runner for the compliance pass — rules 137/147/20/139 on deeds whose
# research is already done and verified. Workers = Opus 5.0. Detached.
#
#   nohup scripts/verify/launch_compliance.sh 2 >/dev/null 2>&1 &
#
# Queue: /tmp/compliance-queue.txt. Progress: tail /tmp/enrich-logs/status-compliance.txt
cd /home/ubuntu/maasei-israel || exit 1
LANES="${1:-2}"
Q=/tmp/compliance-queue.txt
LOCK=/tmp/compliance-queue.lock
LOGS=/tmp/enrich-logs
ST="$LOGS/status-compliance.txt"
mkdir -p /tmp/compliance /tmp/compliance-out "$LOGS"
touch "$LOCK"

pop()     { flock "$LOCK" bash -c "head -n1 '$Q'; sed -i '1d' '$Q'"; }
requeue() { flock "$LOCK" bash -c "echo '$1' >> '$Q'"; }

lane() {
  n="$1"
  while :; do
    id="$(pop)"
    [ -z "$id" ] && break
    if [ -s "/tmp/compliance-out/${id}.json" ]; then
      echo "SKIP $id already-done $(date +%H:%M)" >> "$ST"; continue
    fi
    ctx="/tmp/compliance/${id}.context.json"
    [ -s "$ctx" ] || python3 scripts/compliance_context.py "$id" --write >/dev/null 2>&1
    if [ ! -s "$ctx" ]; then
      echo "NOCTX $id $(date +%H:%M)" >> "$ST"; continue
    fi
    timeout 2700 claude -p "אתה סוכן בפרויקט 'מעשי ישראל'. אתה מריץ **מעבר תאימות** על מעש אחד שכבר עבר מחקר מלא.

התדריך שלך: /home/ubuntu/maasei-israel/scripts/verify/COMPLIANCE-BRIEF.md — קרא אותו במלואו לפני שאתה נוגע ברשת.
ההקשר שלך: ${ctx}
התוצר שלך: /tmp/compliance-out/${id}.json
היומן שלך: /tmp/compliance-out/${id}.journal.md

ארבעת הכללים: 137 רישיון לכל תמונה מתוך רשימה סגורה · 147 כיתוב = שורה אחת קצרה · 20 תאום אנגלי לכל שדה עברי בגלריה · 139 sensitive_claims. הכל מפורט בתדריך. אל תשנה טקסט, ציטוטים או מקורות — הם אומתו כבר. כתוב את ה-JSON מיד כשסיימת, לפני סיכום. דווח עד 120 מילים." \
      --permission-mode bypassPermissions --model claude-opus-5 \
      > "$LOGS/compliance-${id}.log" 2>&1
    rc=$?
    if [ -s "/tmp/compliance-out/${id}.json" ] && \
       python3 -c "import json;json.load(open('/tmp/compliance-out/${id}.json'))" 2>/dev/null; then
      j=nojournal; [ -s "/tmp/compliance-out/${id}.journal.md" ] && j=journal-ok
      echo "DONE $id rc=$rc out-ok $j $(date +%H:%M)" >> "$ST"
    elif grep -qiE "usage limit|rate.?limit|429|overloaded|quota" "$LOGS/compliance-${id}.log"; then
      echo "LIMIT lane$n $id sleeping-30m $(date +%H:%M)" >> "$ST"
      requeue "$id"
      sleep 1800
    elif [ ! -f "$LOGS/cretry-${id}" ]; then
      touch "$LOGS/cretry-${id}"
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
