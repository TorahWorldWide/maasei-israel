#!/bin/bash
# Queue runner for the completion pass — the rules that entered the standard
# after these pages were already finished: 148, 149, 150, 151, 157 (and the 20
# they drag along). Workers = Opus 5.0 (Tomer's decision 9.8). Detached.
#
#   nohup scripts/verify/launch_completion.sh 3 >/dev/null 2>&1 &
#
# Queue: /tmp/completion-queue.txt. Progress: tail /tmp/enrich-logs/status-completion.txt
#
# Each lane does its deed whole: the blind image descriptions first (rule 149,
# one fresh process per image, no page context), then the worker. Serial inside
# the lane on purpose — the two halves compete for the same quota, and a lane
# that runs them side by side doubles the concurrency nobody accounted for.
cd /home/ubuntu/maasei-israel || exit 1
LANES="${1:-3}"
Q=/tmp/completion-queue.txt
LOCK=/tmp/completion-queue.lock
LOGS=/tmp/enrich-logs
ST="$LOGS/status-completion.txt"
mkdir -p /tmp/completion /tmp/completion-out /tmp/blind "$LOGS"
touch "$LOCK"

pop()     { flock "$LOCK" bash -c "head -n1 '$Q'; sed -i '1d' '$Q'"; }
requeue() { flock "$LOCK" bash -c "echo '$1' >> '$Q'"; }

lane() {
  n="$1"
  while :; do
    id="$(pop)"
    [ -z "$id" ] && break
    if [ -s "/tmp/completion-out/${id}.json" ]; then
      echo "SKIP $id already-done $(date +%H:%M)" >> "$ST"; continue
    fi

    # Rule 149 — the describer must never see the page, so it runs outside the
    # worker and lands on disk before the worker starts.
    timeout 2400 python3 scripts/describe_images.py "$id" \
      > "$LOGS/blind-${id}.log" 2>&1
    echo "BLIND $id $(python3 -c "
import json,sys
try: print(len(json.load(open('/tmp/blind/${id}.json'))))
except Exception: print(0)") images $(date +%H:%M)" >> "$ST"

    ctx="/tmp/completion/${id}.context.json"
    python3 scripts/completion_context.py "$id" --write >/dev/null 2>&1
    if [ ! -s "$ctx" ]; then
      echo "NOCTX $id $(date +%H:%M)" >> "$ST"; continue
    fi

    timeout 3600 claude -p "אתה סוכן בפרויקט 'מעשי ישראל'. אתה מריץ **פאס השלמה** על מעש אחד שכבר עבר מחקר מלא ואומת.

התדריך שלך: /home/ubuntu/maasei-israel/scripts/verify/COMPLETION-BRIEF.md — קרא אותו במלואו לפני שאתה נוגע ברשת.
ההקשר שלך: ${ctx}
התוצר שלך: /tmp/completion-out/${id}.json
היומן שלך: /tmp/completion-out/${id}.journal.md

ארבעה כללים, וזה כל מה שאתה נוגע בו: 148 כל מספר בדף נשען על ציטוט או על חישוב · 157 הרגע שעליו הדף מסתובב · 150 מצב כן ואפס פערים סמויים · 151 כל פרס מאומת מול הגוף המעניק, כאובייקט עם תאום אנגלי. המחקר, הציטוטים והכיתובים שעל הדף כבר אומתו — אל תשכתב אותם. אל תיגע ב-sections וב-infobox: המבנה החדש עדיין לא אושר. כתוב את ה-JSON מיד כשסיימת, לפני סיכום. דווח עד 150 מילים." \
      --permission-mode bypassPermissions --model claude-opus-5 \
      > "$LOGS/completion-${id}.log" 2>&1
    rc=$?
    if [ -s "/tmp/completion-out/${id}.json" ] && \
       python3 -c "import json;json.load(open('/tmp/completion-out/${id}.json'))" 2>/dev/null; then
      j=nojournal; [ -s "/tmp/completion-out/${id}.journal.md" ] && j=journal-ok
      echo "DONE $id rc=$rc out-ok $j $(date +%H:%M)" >> "$ST"
    elif grep -qiE "usage limit|rate.?limit|429|overloaded|quota" "$LOGS/completion-${id}.log"; then
      echo "LIMIT lane$n $id sleeping-30m $(date +%H:%M)" >> "$ST"
      requeue "$id"
      sleep 1800
    elif [ ! -f "$LOGS/kretry-${id}" ]; then
      touch "$LOGS/kretry-${id}"
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
