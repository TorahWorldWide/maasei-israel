#!/bin/bash
# Queue-based lane runner for the deed-standard pass. Workers = Opus 5.0
# (Tomer's decision 9.8.2026 — not Sonnet). Detached, disk-first, heartbeat.
#
#   nohup scripts/verify/launch_standard_pass.sh 3 >/dev/null 2>&1 &
#
# Queue: /tmp/enrich-queue.txt (one deed id per line). Progress:
# tail /tmp/enrich-logs/status-pass.txt. A LIMIT line = lane sleeping 30m on 429.
#
# The worker reads /tmp/briefs/<id>.md — generated from DEED-STANDARD.md by
# standard_pass_brief.py, so a rule that changes in the document reaches the
# next worker without anyone remembering to copy it. Optional per-deed hints
# (surviving research from a killed run) go in /tmp/briefs/<id>.hints.md.
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
    brief="/tmp/briefs/${id}.md"
    if [ ! -s "$brief" ]; then
      python3 scripts/standard_pass_brief.py "$id" --write >/dev/null 2>&1
    fi
    if [ ! -s "$brief" ]; then
      echo "NOBRIEF $id could not build brief $(date +%H:%M)" >> "$ST"; continue
    fi
    hints=""
    [ -s "/tmp/briefs/${id}.hints.md" ] && hints="
מחקר ששרד מריצה קודמת שנהרגה: /tmp/briefs/${id}.hints.md — קרא אותו ראשון. הדפים שמופיעים בו כבר נמשכו ויושבים על הדיסק, ומשיכה חוזרת שלהם היא בזבוז תקציב. הם עדיין לא ראיה: ציטוט תקף רק אם מצאת אותו מילה-במילה בקובץ."
    timeout 3600 claude -p "אתה סוכן בפרויקט 'מעשי ישראל'. אתה בונה **מחדש מאפס** מעש אחד לפי תקן דף המעשה.

התדריך המלא שלך: ${brief} — קרא אותו במלואו לפני שאתה נוגע ברשת. הוא מכיל את השורה הנוכחית במסד (רמז בלבד, לא מקור), את כל כללי התקן שאתה נמדד עליהם, את מילון הפרשנות לפי קטגוריה לשדות 64–67, ואת מבנה התוצר. פעל לפיו מילה במילה.${hints}

התוצר שלך: /tmp/enrich-out/${id}.json
היומן שלך: /tmp/enrich-out/${id}.journal.md — תוצר שני וחובה (כלל 87). כתוב אותו תוך כדי העבודה ולא בסוף מהזיכרון. יומן חסר = המעש לא נגמר.

תזכורות קריטיות:
- חמישה דומיינים עצמאיים שונים, לא חמישה ציטוטים מאותו אתר. ויקיפדיה היא מפת דרכים להערות השוליים שלה, לא מקור.
- כל ציטוט חייב להימצא מילה-במילה בדף שמשכת בפועל. לא מצאת = לא משתמש. אל תתפור שני משפטים לציטוט אחד.
- לכל ציטוט: locator + published. **כל שדה עברי בציטוט חייב תאום אנגלי** — quote_en, source_label_en, locator_en (כלל 20 נבדק גם על שורת הציטוט, לא רק על גוף הדף). הכי פשוט: כתוב את ה-locator באנגלית מלכתחילה ומלא locator_en זהה.
- ארבעת השדות origin_story · aftermath · recognition · honors הם לב המעבר הזה. מלא אותם לפי מילון הפרשנות שבתדריך, לפי הקטגוריה של המעש שלך. אין הכרה אישית או פרס על שם? זו תשובה עוברת — כותבים 'לא רלוונטי — <נימוק>' ב-recognition ונימוק מקביל ב-unresolved עבור honors. שדה ריק אינו תשובה, ו'לא רלוונטי' בלי נימוק אינו תשובה.
- כלל 42: מקור שנאסף ולא שינה את הטקסט הוא מקור מבוזבז. כל עובדה חדשה נכנסת לטקסט ונרשמת ב-content_delta עם המקור שממנו באה.
- מיקום עם precision כן, עיר מומצאת לא. אנשים עברית+אנגלית. תגים מהרשימות הסגורות בלבד.
- תקציב קשיח: 40 פעולות רשת. נגמר = כתוב partial עם missing+tried. דומיין שחסם = נטוש מיד.
- אל תריץ archive_source.py (כלל 136). השאר archived_url ריק — הארכוב מרוכז ורץ אחרי הכתיבה למסד, כי יש ערוץ SSH אחד למחשב של תומר, וכמה עובדים שמתחרים עליו מאבדים סנפשוטים ששולמו עליהם.
- שלושת השדות שנוספו לתקן ב-11.8 נבדקים אוטומטית ונופלים בשקט: image_provenance[].license מהרשימה הסגורה בתדריך · sensitive_claims (רשימה ריקה היא תשובה, שדה חסר אינו) · כיתוב של שורה אחת עד 80 תווים, עם caption_long_he לתיאור הארוך.
- אל תיגע במסד, אל תריץ SQL, אל תעשה git commit. יש כותב אחד בלבד והוא apply_standard_pass.py.
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
