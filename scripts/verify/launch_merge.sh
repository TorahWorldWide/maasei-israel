#!/bin/bash
cd /home/ubuntu/maasei-israel
run() {
  n="$1"; slug="$2"
  claude -p "אתה סוכן מיזוג בפרויקט 'מעשי ישראל'.

קרא קודם כל את התדריך המלא: /tmp/merge-rows/BRIEF.md — הוא מגדיר בדיוק מה לעשות, מה אסור, ומה התוצר. פעל לפיו מילה במילה.

הקבוצה שלך: **${n}_${slug}**
הקלט שלך: /tmp/merge-rows/${n}_${slug}.json
הרקע: /home/ubuntu/maasei-israel/docs/merge-proposals/batch-2.md (הסעיף של הקבוצה שלך)
דוגמת זהב: /home/ubuntu/maasei-israel/docs/merge-proposals/icq.md

התוצרים שאתה חייב לכתוב:
1. /home/ubuntu/maasei-israel/docs/merge-proposals/final/${n}_${slug}.md
2. /tmp/merge-out/${n}_${slug}.json

דגשים קריטיים:
- ויקיפדיה = מפת דרכים למקורות, לא מקור. source_url הראשי חייב להיות לא-ויקיפדיה.
- כל ציטוט חייב להימצא מילה-במילה בדף שמשכת בפועל. ציטוט לא מאומת = אל תשתמש בו. אל תמציא ולא תשחזר מהזיכרון.
- אל תיגע במסד, אל תריץ SQL, אל תעשה git commit.
- כתוב את קובץ ה-JSON מיד כשסיימת, לפני שאתה כותב סיכום.
סיים בדיווח קצר (עד 250 מילים)." \
  --permission-mode bypassPermissions --model claude-fable-5 \
  > /tmp/merge-logs/${n}_${slug}.log 2>&1
  echo "DONE ${n}_${slug} rc=$?" >> /tmp/merge-logs/status.txt
}
run 2 ezer-mizion &
run 5 zaka &
run 7 tevel &
run 9 israaid-italy &
wait
echo "ALL DONE $(date)" >> /tmp/merge-logs/status.txt
