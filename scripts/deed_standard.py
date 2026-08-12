#!/usr/bin/env python3
"""Score every deed against docs/DEED-STANDARD.md.

The registry below holds every rule of the standard — not only the ones a
script can decide. Rules that need a network fetch, a reader's judgment, a UI
check or a run-time procedure are listed with the place they are enforced, so
the document and the code hold the same list and `--verify-doc` can prove it.

Passing every automated rule means the fields are full. It does not mean the
page is true: ten deeds at a full score carried 56 findings, five of them
severe. That is why the summary prints two numbers, not one.

  python3 scripts/deed_standard.py             # summary
  python3 scripts/deed_standard.py --list      # the full numbered list
  python3 scripts/deed_standard.py --failing 3 # which deeds fail rule 3
  python3 scripts/deed_standard.py --fields    # rule 152 — fields the site hides
  python3 scripts/deed_standard.py --verify-doc
  python3 scripts/deed_standard.py --json out.json
"""
import argparse
import json
import re
import sys
import urllib.request
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "DEED-STANDARD.md"
SRC = ROOT / "src"
YOUTUBE = re.compile(r"youtu\.?be|youtube\.com", re.I)
HEBREW = re.compile(r"[֐-׿]")
IMAGE_EXT = re.compile(r"\.(jpe?g|png|webp|gif)(\?|$)", re.I)
NOT_RELEVANT = re.compile(r"^\s*(לא רלוונטי|לא רלבנטי|not relevant|n/?a)\b[\s—–:,.-]*", re.I)
# A sentence break is terminal punctuation followed by space or end of text, so
# "11.8" and "2,292,387" do not split.
SENTENCE_SPLIT = re.compile(r"(?<=[.!?…])\s+")
# "Dr. Bracha Zisser" is one sentence, not two. Terminal punctuation after a
# title, an initial or a common abbreviation is not a sentence break, and a
# caption should not have to be written badly to satisfy the counter.
ABBREVIATION = re.compile(
    r"\b(?:[A-Z]|Mr|Mrs|Ms|Dr|Prof|Sr|Jr|St|Mt|Rev|Gen|Col|Sgt|Lt|Capt"
    r"|vs|etc|et al|e\.g|i\.e|cf|approx|no|vol|pp|ed|est"
    r"|Inc|Ltd|Co|Univ|Dept|U\.S|U\.K|a\.m|p\.m)\.\s",
    re.I)
HONOR_WORDS = re.compile(r"כבוד|honors?|פרס|הנצחה|על שמ", re.I)


def count_sentences(text):
    return len([x for x in SENTENCE_SPLIT.split(ABBREVIATION.sub("_ ", text or ""))
                if x.strip()])

AUTO, AUTO_EYE, NET, EYE, UI, PROC = "auto", "auto+eye", "net", "eye", "ui", "proc"
KIND_SYMBOL = {AUTO: "🤖", AUTO_EYE: "🤖 + 👁", NET: "🌐", EYE: "👁", UI: "🖥", PROC: "📋"}

DEED_TYPES = {
    "המצאה מדעית",
    "רפואה והצלת חיים",
    "חסד וצדקה",
    "חילוץ ואסון טבע",
    "חינוך",
    "זכויות אדם",
}
TRANSCRIPT_SOURCES = {"youtube_tool", "secondary_tool", "whisper_gpu"}
LEAD_IMAGE_BASIS = {"verified_portrait", "contemporary_artifact"}
DEED_STATES = {"complete", "partial", "exhausted"}
IMAGE_LICENSES = {"public_domain", "cc", "press", "owner_permission", "under_review"}
ARCHIVE_FAILED = re.compile(r"archive_failed:\s*(\S+)")
# Rule 147 — a caption is one short line, not a paragraph. The Hebrew line is
# the one Tomer reads on a phone; English runs longer for the same sentence.
CAPTION_MAX = {"caption_he": 80, "caption_en": 95, "group": 45, "group_en": 60}
# The short line is the default, not a ceiling on meaning: an image whose reason
# for being on the page is missing from the page text (rule 58) may buy the
# context back in caption_why_long. A group heading never gets that exemption.
CAPTION_MAX_LONG = {"caption_he": 200, "caption_en": 240}
LONG_CAPTIONS_PER_PAGE = 2
# Rule 148 — every numeral a reader sees is a claim. A thousands separator and
# a decimal point belong to the number; anything else ends it.
NUMERAL = re.compile(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?")
URL_IN_TEXT = re.compile(r"https?://\S+")
NUMBER_FIELDS = ("title", "summary_short", "description", "act", "ripple")
# The two expressions the checker can redo by itself. A year on its own is a
# legitimate end of a span ("1948 to 1967"); an age needs the whole date.
AGE_EXPR = re.compile(r"^age\((\d{4}-\d{2}-\d{2}),(\d{4}-\d{2}-\d{2})\)$")
YEARS_EXPR = re.compile(r"^years_between\((\d{4}(?:-\d{2}-\d{2})?),(\d{4}(?:-\d{2}-\d{2})?)\)$")
NUMBER_KINDS = {"quoted", "computed"}
# Rule 152 — the fields the standard requires a worker to fill because the
# reader is meant to see them. A field nobody renders is not content, it is
# bookkeeping, and demanding it is a rule that enforces nothing.
CONTENT_FIELDS = [
    "title", "description", "act", "ripple", "origin_story", "aftermath",
    "recognition", "honors", "summary_short",
    "caption_he", "caption_long_he", "group", "credit",
]

# (number, kind, title). The auto ones also appear in CHECKS below.
RULES = [
    # פרק 0 — הכללים שמעל הכל
    (49, AUTO_EYE, "אפס־אמון בקיים — הדף נבנה מחדש מאפס"),
    (50, NET, "מבחן הבולשיט — כל מקור מחזיק"),
    (51, AUTO, "אין פריט בלי הוכחה"),
    (52, AUTO, "מה שלא אומת נרשם כפתוח"),
    # פרק א — מקורות
    (1, AUTO, "מקור ראשי שאינו ויקיפדיה"),
    (2, AUTO, "5 דומיינים עצמאיים ומעלה"),
    (3, AUTO, "ציטוט אחד לפחות לכל מקור"),
    (4, NET, "כל ציטוט מילה־במילה בדף החי"),
    (5, EYE, "מקורות ממוינים לפי רלוונטיות"),
    (6, AUTO, "מיקום מדויק בכל ציטוט"),
    (7, EYE, "סופרלטיב נשען על מקור עצמאי"),
    (53, EYE, "ויקיפדיה כמפת דרכים בלבד"),
    (54, EYE, "כל מקור נפתח ונקרא לעומק"),
    (128, AUTO_EYE, "לינק מקור גלוי על כל כרטיס"),
    (55, AUTO, "מיזוג = קריאה מחדש ועדכון התוכן"),
    (133, PROC, "יומן ידע — כל ממצא נכתב ברגע שנמצא, עם ציטוט ולינק"),
    (134, EYE, "שדות הדף נכתבים מהיומן בלבד"),
    (135, PROC, "היומן הוא append-only"),
    (136, AUTO, "ארכוב ברגע הציטוט — סנפשוט לכל מקור"),
    # פרק ב — תמונות
    (8, AUTO, "5 תמונות ומעלה"),
    (9, AUTO, "כל תמונה היא קובץ ישיר"),
    (11, NET, "כל קישור תמונה חי"),
    (12, NET, "מקור, צלם, שנה ומקום פרסום"),
    (17, EYE, "התמונה מתעדת את המעש עצמו"),
    (44, AUTO, "כיתוב עברי לכל תמונה"),
    (45, EYE, "כותרת קבוצה לתמונות מאותו סוג"),
    (46, EYE, "תמונה חריגה מקבלת כיתוב משלה"),
    (47, EYE, "שתי תמונות של אותו מושא — אותה קביעה"),
    (56, EYE, "ספציפיות מנצחת תמונה גנרית"),
    (57, AUTO_EYE, "כלל הדיוקן — בסיס התמונה הראשית מוצהר"),
    (132, EYE, "סיפור על אדם — התמונה שלו ראשונה"),
    (58, EYE, "קוהרנטיות גלריה–טקסט"),
    (59, UI, "לחיצה על תמונה מובילה למקור (רשות)"),
    (60, AUTO, "אין סרטון? תמונות מספיקות"),
    (61, UI, "תמונות וסרטונים באזורים נפרדים"),
    (137, AUTO, "בסיס שימוש מוצהר לכל תמונה"),
    (153, EYE, "תמונה שדורשת גילוי נאות — הגילוי בכיתוב הגלוי או שהיא יוצאת"),
    (146, EYE, "תמונות מקפיצות עין — עד 2 סריקות טקסט לדף"),
    (147, AUTO, "כיתוב = שורה אחת קצרה כברירת מחדל, חריגה בנימוק"),
    (161, EYE, "הכיתוב לא טוען טענה סיבתית שסותרת את תאריך הצילום"),
    (149, AUTO_EYE, "הכיתוב נכתב מהתמונה שנפתחה, לא משם הקובץ"),
    # פרק ג — סרטונים
    (10, AUTO, "עד 5 סרטונים"),
    (13, NET, "כל סרטון מתנגן בהטמעה"),
    (14, EYE, "סרטון־על אחד מסומן עם נימוק"),
    (15, EYE, "המעש הוא הנושא המרכזי בסרטון"),
    (16, EYE, "תמליל נמשך ונקרא לכל סרטון"),
    (48, AUTO, "שורת משנה לכל סרטון"),
    (62, AUTO, "שרשרת נפילה לתמלול מתועדת"),
    (63, UI, "חצים לניווט בין הסרטונים"),
    (144, PROC, "תמליל שנמשך נשמר ביומן הידע"),
    # פרק ד — תוכן
    (18, AUTO_EYE, "שנה קיימת — ושהיא שנת המעשה"),
    (19, AUTO, "חלק א׳ + חלק ב׳ מלאים"),
    (20, AUTO, "תרגום אנגלי מלא"),
    (21, EYE, "אין סתירה פנימית במספרים"),
    (148, AUTO_EYE, "מבחן המספרים — כל מספר בדף נשען על ציטוט או על חישוב שנרשם"),
    (22, EYE, "אין אגדה"),
    (157, AUTO_EYE, "הרגע — הסצנה שעליה הדף מסתובב — מזוהה לפני הכתיבה"),
    (29, EYE, "הטקסט נכתב אחרי כל המקורות"),
    (30, EYE, "מקורות חלוקים — כותבים את הטווח"),
    (31, EYE, "מקור בן־הזמן גובר על מאוחר"),
    (32, AUTO, "תאריך פרסום לכל מקור"),
    (42, AUTO_EYE, "כל נכס שנאסף מזין את הטקסט"),
    (43, AUTO, "הטקסט באמת השתנה"),
    (64, AUTO, "סיפור מקור"),
    (65, AUTO, "מה קרה אחר כך"),
    (66, AUTO, "מה קיבל/ה העושה"),
    (67, AUTO, "כבוד על שמם"),
    (130, AUTO_EYE, "תקציר־טריילר, 3–10 משפטים, בלי סתירה לכאורה"),
    (138, EYE, "מספר מצטבר נכתב עם השנה שלו"),
    (139, AUTO_EYE, "רף כפול לטענה רגישה על אדם חי"),
    (155, EYE, "הדף הקנוני הוא אמת המידה לסגנון"),
    (156, EYE, "העובדה נושאת את הגאווה — בלי סופרלטיבים בפרוזה"),
    (158, EYE, "ארבעת מבחני הכישלון: החלפה · הקראה · סיפור לחבר · שליחה"),
    (160, AUTO_EYE, "תיקון עובדתי מתקן את שתי השפות — ומספר תואם בין השתיים"),
    (162, EYE, "עובדה מפוצצת חייבת הקשר בהישג יד"),
    (68, EYE, "חומר ביוגרפי שלא שייך — בצד"),
    (69, UI, "עברית או אנגלית, לא מעורבב"),
    (70, UI, "ברירת מחדל לפי מדינת הגולש"),
    (71, UI, "טקסט קומפקטי"),
    (152, AUTO, "אין שדה תוכן שהאתר לא מציג"),
    # פרק ה — כותרות
    (23, EYE, "הכותרת מדויקת ולא מנופחת"),
    (72, EYE, "כל מילה בכותרת שורדת מול המקור"),
    (73, AUTO_EYE, "נוסחת הכותרת, 6–12 מילים"),
    (74, AUTO, "בלי קליקבייט וסימני קריאה"),
    (75, AUTO, "title_reasoning קיים"),
    (76, UI, "כותרת · סרטון · הסבר מלא מתחת"),
    (127, AUTO_EYE, "שינוי כותרת = הפניה מהכתובת הישנה"),
    # פרק ו — מטא־נתונים
    (24, NET, "המעש אינו כפול"),
    (25, AUTO, "קטגוריה"),
    (26, AUTO, "תיוג תקופה נגזר מהשנה"),
    (27, AUTO, "מיקום עם רמת דיוק"),
    (28, AUTO, "עבר ביקורת מתועדת"),
    (37, AUTO, "שמות האנשים במעש"),
    (151, AUTO_EYE, "פרס מאומת מול הגוף המעניק"),
    (38, AUTO, "תג סוג המעשה"),
    (39, AUTO, "תג מי עשה"),
    (40, AUTO, "תג למי זה עזר"),
    (77, AUTO, "מעש נוסף של אותו אדם נרשם כליד"),
    (78, UI, "בחירה מרובה של טווחי מאות"),
    (79, AUTO, "תג מדינה"),
    (80, EYE, "התאמה חלקית מחייבת קריאה לעומק"),
    (81, PROC, "סריקת כפילויות קיימות באתר"),
    # פרק ז — מנגנון העצירה
    (33, PROC, "תקציב טוקנים קשיח לכל מעש"),
    (34, AUTO, "תוצר נכתב תמיד, גם חלקי"),
    (35, AUTO, "מה חסר נרשם במפורש"),
    (36, AUTO, "מה כבר נוסה נרשם"),
    (150, AUTO, "פער מוכר חוסם פרסום — complete דורש אפס פתוחים"),
    # פרק ח — תהליך עבודה
    (82, PROC, "התקן הוא שער כניסה, לא תיקון בדיעבד"),
    (83, PROC, "התקן חל גם על מעשים עתידיים"),
    (84, PROC, "פיילוט של 5 לפני ריצה על הכל"),
    (85, PROC, "תצוגת לפני/אחרי שנראית כמו האתר"),
    (86, PROC, "מודל העובדים: Opus 5.0"),
    (87, PROC, "כל סוכן כותב יומן עבודה"),
    (88, PROC, "טעות נחסמת בקוד, לא מתוקנת שוב"),
    (89, PROC, "לאט ומושלם"),
    (90, PROC, "אין מכסת מעשים — התקרה היא טוקנים"),
    (91, PROC, "כמעט גמור? לסיים, ואז דף חלק"),
    (92, PROC, "החברה רצה כל יום, לבד"),
    (93, PROC, "שבת — מזריחה עד זריחה"),
    (94, PROC, "טיימר לחלון חידוש המכסה"),
    (95, PROC, "רשימות מוכנות כמקור לידים"),
    (96, PROC, "חתני נובל כמאגר לידים"),
    (97, PROC, "לא לעשות עבודה שלא התבקשה"),
    (98, PROC, "בשלב דיבורים לא מבצעים כלום"),
    (99, PROC, "מבינים ומקבלים אישור לפני עבודה"),
    (100, PROC, "מדווחים בזמן אמת מה עושים ואיך"),
    (101, PROC, "כל הודעה מסתיימת בקישור לאתר"),
    (140, AUTO_EYE, "ביקורת־פתע אדברסרית — המדגם נגזר מאחוז אי־ההסכמה"),
    (154, PROC, "הבודק מקבל את הראיות עצמן; 'לא נבדק' אינו 'עבר'"),
    (159, EYE, "בודק הקול — מודל טרי מדווח איפה השתעמם ואיפה התגאה"),
    (141, PROC, "תוכן מהרשת הוא נתונים, לא הוראות"),
    (145, PROC, "דחיפה בלי אימות דיפלוי אינה גמורה"),
    (163, PROC, "חוקר וכותב הם שני תפקידים, שתי ריצות, שני תדריכים"),
    (164, EYE, "היומן חייב לענות על שאלות־הקורא, או לרשום 'לא נמצא'"),
    (165, EYE, "הכותב כותב מן היומן בלבד; פער חוזר כשאלה לחוקר"),
    # פרק ט — עיצוב ואתר
    (102, UI, "דף הבית הוא תיאטרון"),
    (103, UI, "בלי נקודות ניווט — מונה"),
    (104, UI, "בלי וילונות"),
    (105, UI, "מרווח צדדי בלי להעמיס"),
    (131, UI, "הדף נפתח בתקציר, קרא עוד פותח את המלא"),
    (106, UI, "חלון נפרד לצלילה + מנוע חיפוש"),
    (107, UI, "ממשק שמחזיק 1000+ מעשים"),
    (108, UI, "השראה מריפוזיטוריז מובילים"),
    (109, UI, "תפאורה מגניבה, יפה וממלכתית"),
    (110, UI, "פלטה כחול עמוק, מובייל־first"),
    (129, UI, "מוטיבים יהודיים ברמז — לא קיטש, לא צעקה"),
    (111, UI, "טופס הגשה ציבורי"),
    (112, UI, "תומר מאשר, ורק אז הבוט"),
    (113, UI, "הבוט מצביע על הכפילות ושואל"),
    (114, UI, "אישור מפורש לפרסום בלי תמונות"),
    (115, UI, "גם אדם וגם בוט בודקים"),
    (116, UI, "כפתור מצאתי טעות"),
    (117, UI, "חלק א׳/ב׳ לא יוצאים מהמסך באנגלית"),
    (118, UI, "מפת עולם — אחרי המיקומים"),
    (119, UI, "קו זמן נדחה"),
    (120, PROC, "להוסיף עוד ועוד מעשים תמיד"),
    (121, PROC, "דחיפות השקה"),
    (142, UI, "נגישות — alt, ניגודיות, ניווט מקלדת"),
    (143, UI, "מטא־תגי שיתוף — og מהתקציר ומהתמונה"),
    # פרק י — מה אסור
    (122, PROC, "אסור למחוק כפילויות — ממזגים"),
    (123, AUTO, "תגים שנדחו במפורש"),
    (124, UI, "פיצ'רים שנדחו במפורש"),
    (125, PROC, "אסור לכתוב למסד ב-PostgREST anon"),
    (126, UI, "אל תיגע בצבעים — מושהה עד עבודת התפאורה"),
]

KINDS = {n: k for n, k, _ in RULES}
TITLES = {n: t for n, _, t in RULES}


def env():
    out = {}
    for line in (ROOT / ".env.local").read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            out[k] = v.strip().strip('"').strip("'")
    return out


def fetch_entries():
    e = env()
    url = f"{e['NEXT_PUBLIC_SUPABASE_URL']}/rest/v1/entries?select=*&limit=1000"
    key = e["NEXT_PUBLIC_SUPABASE_ANON_KEY"]
    req = urllib.request.Request(url, headers={"apikey": key, "Authorization": f"Bearer {key}"})
    return json.load(urllib.request.urlopen(req))


def domain(url):
    m = re.search(r"https?://([^/]+)", url or "")
    return m.group(1).replace("www.", "").lower() if m else ""


def media(entry):
    """Every media url on the deed, split into videos and images."""
    urls = []
    if entry.get("media_url"):
        urls.append(entry["media_url"])
    for item in entry.get("media_urls") or []:
        if isinstance(item, str):
            urls.append(item)
        elif isinstance(item, dict) and item.get("url"):
            urls.append(item["url"])
    videos = [u for u in urls if YOUTUBE.search(u)]
    images = [u for u in urls if not YOUTUBE.search(u)]
    return videos, images


def numerals(text):
    """Every number a reader sees, separators stripped so 13,484 and 13484 are
    the same number. Digits inside a url are part of an address, not a claim."""
    return {n.replace(",", "") for n in NUMERAL.findall(URL_IN_TEXT.sub(" ", str(text or "")))}


def digits(value):
    """A number as the checker compares it — the way it is written is not it."""
    return str("" if value is None else value).replace(",", "").strip()


# Rule 160. Spelled-out numbers, because the bug that produced the rule was
# spelled out in both languages: "בגיל שמונה-עשרה" against "at nineteen". A
# check that only read digits would have walked straight past it.
HE_ONES = {"אחת": 1, "אחד": 1, "שתיים": 2, "שניים": 2, "שתי": 2, "שני": 2,
           "שלוש": 3, "שלושה": 3, "ארבע": 4, "ארבעה": 4, "חמש": 5, "חמישה": 5,
           "שש": 6, "שישה": 6, "שבע": 7, "שבעה": 7, "שמונה": 8,
           "תשע": 9, "תשעה": 9}
HE_TEN = {"עשר", "עשרה"}
HE_TENS = {"עשרים": 20, "שלושים": 30, "ארבעים": 40, "חמישים": 50, "שישים": 60,
           "שבעים": 70, "שמונים": 80, "תשעים": 90, "מאה": 100, "מאתיים": 200}
EN_ONES = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
           "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
           "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
           "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19}
EN_TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60,
           "seventy": 70, "eighty": 80, "ninety": 90, "hundred": 100}
WORD_SPLIT = re.compile(r"[^\w֐-׿]+")


def spelled_numbers(text, hebrew):
    """The numbers a reader hears in prose that never shows a digit.

    Handles the two compounds either language builds: unit+ten ("שמונה עשרה",
    "eighteen") and tens+unit ("חמישים וחמש", "fifty-five"). A decade said as
    a period ("שנות התשעים", "the 1990s") yields the century form too, so the
    two languages can meet."""
    ones, tens = (HE_ONES, HE_TENS) if hebrew else (EN_ONES, EN_TENS)
    words = [w.lower() for w in WORD_SPLIT.split(str(text or "")) if w]
    if hebrew:
        # Hebrew glues its prepositions on: כאחד-עשר is still eleven.
        words = [w[1:] if w[:1] in "ובכלמהש" and (w[1:] in ones or w[1:] in tens
                                                  or w[1:] in HE_TEN) else w
                 for w in words]
    decade = hebrew and any(w.startswith("שנות") for w in words)
    found, i = set(), 0
    while i < len(words):
        word, nxt = words[i], words[i + 1] if i + 1 < len(words) else ""
        if hebrew and word in ones and nxt in HE_TEN:
            found.add(10 + ones[word])       # שמונה עשרה
            i += 2
            continue
        if hebrew and word in HE_TEN:        # עשרה ימים
            found.add(10)
        elif word in tens:
            if nxt in ones:
                found.add(tens[word] + ones[nxt])   # חמישים וחמש / fifty-five
                i += 2
                continue
            found.add(tens[word])
            # "שנות התשעים" and "the 1990s" are the same decade. English says
            # a decade in digits, so only the Hebrew needs the century added.
            if decade:
                found.add(1900 + tens[word])
        elif word in ones:
            found.add(ones[word])
        i += 1
    return found


HE_SCALE = re.compile(r"(\d[\d,\.]*)\s*(אלפי|אלף|אלפים|מיליון|מיליוני)")
SCALE_ZEROS = {"אלפי": "000", "אלף": "000", "אלפים": "000",
               "מיליון": "000000", "מיליוני": "000000"}


def scaled(text):
    """Hebrew writes the big round numbers half in digits — "18 אלף" — where
    English writes "18,000". Without this the two look like different facts."""
    return HE_SCALE.sub(
        lambda m: m.group(1).replace(",", "") + SCALE_ZEROS[m.group(2)],
        str(text or ""))


def language_parity(entry):
    """Rule 160 — a number that is on the page in one language is on the page
    in the other. Returns the fields whose two versions disagree.

    The pair is compared as values, not as spellings: 18, "שמונה-עשרה" and
    "eighteen" are one number. A number that appears in only one of the two is
    not reported — a sentence may legitimately be split or joined in
    translation. Only a value that contradicts is."""
    off = []
    for field in ("title", "description", "summary_short", "act", "ripple",
                  "origin_story", "aftermath", "recognition"):
        he_text, en_text = entry.get(field), entry.get(field + "_en")
        if not (he_text or "").strip() or not (en_text or "").strip():
            continue
        he = {int(n) for n in numerals(scaled(he_text)) if n.isdigit()}
        en = {int(n) for n in numerals(en_text) if n.isdigit()}
        he |= spelled_numbers(he_text, True)
        en |= spelled_numbers(en_text, False)
        # Ten to ninety-nine. Under ten the two languages differ for reasons of
        # grammar and not of fact — Hebrew counts "שני הממציאים" where English
        # says "neither inventor" — and the grammar buries the signal. Above
        # ninety-nine a translation legitimately reshapes figures. Measured on
        # 201 deeds: the whole range flags 24 of them, this window flags 3.
        for value in sorted((he ^ en) & set(range(10, 100))):
            near = {value - 1, value + 1} & (en if value in he else he)
            if near:
                off.append(f"{field}: {value} ↔ {near.pop()}")
    return off


def age(born, died):
    """Full calendar age. A birthday that has not come round yet does not count:
    Montefiore, 1784-10-24 to 1885-07-28, died at 100, and the page said 101."""
    a, b = date.fromisoformat(born), date.fromisoformat(died)
    return b.year - a.year - ((b.month, b.day) < (a.month, a.day))


def years_between(start, end):
    """A span in whole years. Two full dates measure the span exactly; a bare
    year on either side can only be counted in years."""
    if len(start) > 4 and len(end) > 4:
        return age(start, end)
    return int(end[:4]) - int(start[:4])


def recompute(expr):
    """The arithmetic this checker can redo. None means the form is unsupported
    — which is not the same as wrong, and is reported separately."""
    written = re.sub(r"\s+", "", expr or "")
    for pattern, fn in ((AGE_EXPR, age), (YEARS_EXPR, years_between)):
        m = pattern.match(written)
        if m:
            return fn(m.group(1), m.group(2))
    return None


def check_numbers(entry):
    """Rule 148. Returns (pass, the computations this could not redo).

    Every numeral in the prose has to be traceable to a quote or to a sum the
    checker can do again. What it cannot decide is whether the quote says the
    same thing about the number that the page says — 470 patients evaluated in
    an ER is not 470 earthquake wounded, and both sentences hold "470". That
    half is why the rule is 🤖 + 👁: this guarantees the quote exists and
    carries the number, so a reviewer can read it beside as_written."""
    numbers = entry.get("numbers")
    if not isinstance(numbers, list):
        return False, []

    ok = True
    covered = set()
    unverified = []
    for item in numbers:
        if not isinstance(item, dict) or item.get("kind") not in NUMBER_KINDS:
            ok = False
            continue
        value = digits(item.get("value"))
        covered.add(value)
        covered |= numerals(item.get("as_written"))
        quote = (item.get("quote") or "").strip()
        if item.get("kind") == "quoted":
            # Token match, not substring: 470 must not be satisfied by 4,700.
            if not quote or not (item.get("citation_url") or "").strip():
                ok = False
            elif value not in numerals(quote):
                ok = False
            continue
        inputs = item.get("inputs")
        if not isinstance(inputs, list) or len(inputs) < 2 or not all(
            isinstance(i, dict) and (i.get("quote") or "").strip()
            and (i.get("citation_url") or "").strip() for i in inputs
        ) or not (item.get("expr") or "").strip():
            ok = False
            continue
        again = recompute(item.get("expr"))
        if again is None:
            unverified.append((item.get("value"), item.get("expr")))
        elif digits(again) != value:
            ok = False

    on_the_page = set()
    for field in NUMBER_FIELDS:
        on_the_page |= numerals(entry.get(field))
    # The deed's own year is the page's subject, not a claim inside it. Only a
    # four-digit year: a deed set in the year 132 must not swallow "132 people".
    year = digits(entry.get("year"))
    if len(year) == 4:
        on_the_page.discard(year)
    return ok and not (on_the_page - covered), unverified


_HIDDEN_FIELDS = None


def field_coverage():
    """Rule 152 — the required content fields no component ever reads.

    A field counts as displayed when a component takes it off an object:
    `p.caption_he`, `e["title"]`. The bare word is not enough, because "group"
    is also a Tailwind class. The type declaration in src/lib/data.ts is not a
    component either: caption_long_he was declared there, filled on 11 pages,
    checked by rule 147 — and rendered nowhere."""
    files = [p for d in ("components", "app") for p in (SRC / d).rglob("*")
             if p.suffix in (".ts", ".tsx")]
    text = "\n".join(p.read_text(errors="replace") for p in files)
    return [f for f in CONTENT_FIELDS
            if not re.search(r"""[.\[]\s*["'`]?""" + f + r"\b", text)]


def fields_are_shown():
    """Rule 152 is a fact about the repo, not about one deed — read it once."""
    global _HIDDEN_FIELDS
    if _HIDDEN_FIELDS is None:
        if not SRC.is_dir():
            print("אזהרה: אין תיקיית src — כלל 152 לא נבדק", file=sys.stderr)
            _HIDDEN_FIELDS = []
        else:
            _HIDDEN_FIELDS = field_coverage()
    return not _HIDDEN_FIELDS


def evaluate(entry):
    """Every AUTO / AUTO_EYE rule, decided from the database alone."""
    cites = entry.get("citations") or []
    videos, images = media(entry)
    domains = {domain(c.get("source_url", "")) for c in cites}
    domains.discard("")
    real_domains = {d for d in domains if "wikipedia.org" not in d}

    def filled(*fields):
        return all((entry.get(f) or "").strip() for f in fields)

    def reasoned(field):
        """Filled — and if the answer is "not relevant", it carries a reason.

        A rescue mission usually has no personal recognition and no award in its
        name. Saying so is a legitimate answer; saying only "לא רלוונטי" is not,
        because it cannot be told apart from never having looked."""
        value = (entry.get(field) or "").strip()
        if not value:
            return False
        if NOT_RELEVANT.match(value):
            return len(NOT_RELEVANT.sub("", value).strip()) >= 20
        return True


    english_pairs = ["title", "description", "act", "ripple",
                     "origin_story", "aftermath", "recognition", "summary_short"]
    english_ok = all(
        not (entry.get(f) or "").strip() or (entry.get(f + "_en") or "").strip()
        for f in english_pairs
    )
    # The citation line is on the screen too: the quote, the source label and
    # the locator. All three stayed Hebrew in English mode until 11.8.
    def hebrew_paired(item, he_field, en_field):
        he = (item.get(he_field) or "").strip()
        if not he or not HEBREW.search(he):
            return True
        return bool((item.get(en_field) or "").strip())

    hebrew_quotes_translated = all(
        hebrew_paired(c, "quote", "quote_en")
        and hebrew_paired(c, "source_label", "source_label_en")
        and hebrew_paired(c, "locator", "locator_en")
        for c in cites
    )

    audit = entry.get("audit") if isinstance(entry.get("audit"), dict) else {}
    rebuild = audit.get("rebuild") if isinstance(audit.get("rebuild"), dict) else {}
    provenance = audit.get("image_provenance") or []

    # Rule 20 reaches the gallery too: a caption, a group heading and a credit
    # line are on the screen exactly like the body text is, and stayed Hebrew
    # in English mode until 11.8.
    def paired(item, he_field, en_field):
        he = (item.get(he_field) or "").strip()
        en = (item.get(en_field) or "").strip()
        if not he:
            return True
        return bool(en) and not HEBREW.search(en)

    gallery_translated = all(
        paired(p, "caption_he", "caption_en")
        and paired(p, "group", "group_en")
        and paired(p, "credit", "credit_en")
        and (not HEBREW.search(str(p.get("shot_when") or ""))
             or paired(p, "shot_when", "shot_when_en"))
        for p in provenance
    )

    # Rule 20 reaches the honours list too — it is on the screen like every
    # other line. It was missed until 12.8 because the check walks the fields
    # it knows by name, and `honors` is the one list whose items were written
    # in a dozen different shapes, so no field name covered it.
    def honor_paired(item):
        if isinstance(item, str):
            return not HEBREW.search(item)
        if not isinstance(item, dict):
            return True
        he = next((str(item[k]) for k in ("he", "what", "name", "name_he")
                   if str(item.get(k) or "").strip()), "")
        en = next((str(item[k]) for k in ("en", "what_en", "name_en")
                   if str(item.get(k) or "").strip()), "")
        if not HEBREW.search(he):
            return True
        return bool(en) and not HEBREW.search(en)

    honors_translated = all(honor_paired(h) for h in (entry.get("honors") or []))

    def one_short_line(item):
        argued = bool((item.get("caption_why_long") or "").strip())
        for field, limit in CAPTION_MAX.items():
            text = (item.get(field) or "").strip()
            if not text:
                continue
            sentences = count_sentences(text)
            if argued and field in CAPTION_MAX_LONG:
                if len(text) > CAPTION_MAX_LONG[field] or sentences > 2:
                    return False
                continue
            if len(text) > limit or sentences > 1:
                return False
        return True

    # A page with no captions at all fails rule 44, not this one — 147 judges
    # the captions that exist.
    argued_long = sum(1 for p in provenance if (p.get("caption_why_long") or "").strip())
    captions_are_trailers = (argued_long <= LONG_CAPTIONS_PER_PAGE
                             and all(one_short_line(p) for p in provenance))
    captioned = {p.get("url") for p in provenance if (p.get("caption_he") or "").strip()}

    def opened(item):
        """Rule 149 — somebody looked at the picture before writing about it.

        A caption guessed from a file name called a night-time recovery of
        remains "the delegation under both flags raised side by side". blind is
        the worker's word that it described the bytes and not the name; the
        checker can require the flag, and a false flag is a lie, not a bug."""
        record = item.get("image_seen") if isinstance(item.get("image_seen"), dict) else {}
        return (record.get("blind") is True
                and all((record.get(f) or "").strip()
                        for f in ("described_at", "by", "description")))

    described = {p.get("url") for p in provenance if opened(p)}
    unresolved = [str(u) for u in (audit.get("unresolved") or [])]
    # Rule 136: a page that could not be archived is a legitimate answer only
    # when it is named. "archive_failed:<url>" in unresolved is that naming.
    archive_failed = {m.group(1) for u in unresolved for m in [ARCHIVE_FAILED.search(u)] if m}
    licensed = {p.get("url") for p in provenance if p.get("license") in IMAGE_LICENSES}
    under_review = {p.get("url") for p in provenance if p.get("license") == "under_review"}
    unresolved_text = " ".join(unresolved)
    sensitive = audit.get("sensitive_claims")
    video_entries = audit.get("videos") or []
    summary = (entry.get("summary_short") or "").strip()
    summary_sentences = count_sentences(summary)
    honors = entry.get("honors")
    honors_reason = any(
        HONOR_WORDS.search(str(u)) for u in (audit.get("unresolved") or [])
    )

    def verified_honor(item):
        """Rule 151 — the awarding body says so, in its own words. A bare
        string is the old shape and fails: it was never verified."""
        return (isinstance(item, dict)
                and all(str(item.get(f) or "").strip()
                        for f in ("name", "awarding_body", "source_url", "quote"))
                and "wikipedia.org" not in domain(item.get("source_url")))

    discrepancies = audit.get("discrepancies")
    # Rule 150 — the worker that found the gap may not be the one that closes
    # it. A page whose own audit says the source and the title disagree was
    # published because the writer decided the two "complement each other".
    closed_by_another = all(
        d.get("found_by") != d.get("closed_by")
        for d in (discrepancies if isinstance(discrepancies, list) else [])
        if isinstance(d, dict) and d.get("found_by") and d.get("closed_by")
    )
    gaps_ok = isinstance(discrepancies, list) and closed_by_another
    if audit.get("state") == "complete":
        gaps_ok = gaps_ok and discrepancies == [] and not unresolved and not under_review
    moment = audit.get("the_moment")
    review = (audit.get("adversarial_review")
              if isinstance(audit.get("adversarial_review"), dict) else {})
    numbers_ok, _ = check_numbers(entry)
    delta = audit.get("content_delta")
    pre = audit.get("pre") if isinstance(audit.get("pre"), dict) else {}
    title = entry.get("title") or ""
    deed_types = entry.get("deed_type") or []

    return {
        # פרק 0
        49: bool(rebuild.get("from_scratch")) and bool(rebuild.get("at")),
        51: bool(entry.get("source_url")) and bool(cites),
        52: isinstance(audit.get("unresolved"), list),
        # מקורות
        1: bool(entry.get("source_url")) and "wikipedia.org" not in (entry.get("source_url") or ""),
        2: len(real_domains) >= 5,
        3: len(cites) >= len(real_domains) and len(cites) > 0,
        6: all((c.get("locator") or "").strip() for c in cites) if cites else False,
        55: bool(delta) if audit.get("merged_from") else True,
        128: bool(entry.get("source_url")) and bool((entry.get("source_label") or "").strip()),
        136: all(
            (c.get("archived_url") or "").strip() or (c.get("source_url") or "") in archive_failed
            for c in cites
        ) if cites else False,
        # תמונות
        8: len(images) >= 5,
        9: all(IMAGE_EXT.search(u) for u in images) if images else False,
        44: bool(images) and all(u in captioned for u in images),
        147: captions_are_trailers,
        149: bool(images) and all(u in described for u in images),
        137: bool(images) and all(u in licensed for u in images) and all(
            str(u) in unresolved_text for u in under_review
        ),
        57: audit.get("lead_image_basis") in LEAD_IMAGE_BASIS,
        60: len(images) >= 5 if not videos else True,
        # סרטונים
        10: len(videos) <= 5,
        48: bool(video_entries) and all(
            (v.get("video_provenance") or "").strip() for v in video_entries
        ) if videos else True,
        62: bool(video_entries) and all(
            v.get("transcript_source") in TRANSCRIPT_SOURCES for v in video_entries
        ) if videos else True,
        # תוכן
        18: bool(entry.get("year")),
        148: numbers_ok,
        160: not language_parity(entry),
        157: isinstance(moment, str) and len(moment.strip()) >= 40,
        152: fields_are_shown(),
        19: filled("act", "ripple"),
        20: (english_ok and hebrew_quotes_translated and gallery_translated
             and honors_translated),
        32: all((c.get("published") or "").strip() for c in cites) if cites else False,
        42: bool(delta),
        43: bool(pre) and any(
            (pre.get(f) or "") != (entry.get(f) or "") for f in ("description", "act", "ripple")
        ),
        64: filled("origin_story"),
        65: filled("aftermath"),
        66: reasoned("recognition"),
        67: isinstance(honors, list) and (bool(honors) or honors_reason),
        # An empty list passes here — whether an empty list is honest is rule
        # 67's question. 151 judges the honors that are on the page.
        151: isinstance(honors, list) and all(verified_honor(h) for h in honors),
        130: 3 <= summary_sentences <= 10,
        # An empty list is an answer — "I looked and found none". A missing key
        # cannot be told apart from never having asked, and so it fails.
        139: isinstance(sensitive, list) and all(
            len({domain(s) for s in (c.get("sources") or [])} - {""}) >= 2
            for c in sensitive if isinstance(c, dict)
        ),
        # כותרות
        73: 6 <= len([w for w in title.split() if any(c.isalnum() for c in w)]) <= 12,
        74: "!" not in title,
        75: filled("title_reasoning"),
        127: bool(audit.get("redirects")) if (pre.get("title") or title) != title else True,
        # מטא־נתונים
        25: bool(entry.get("categories") or entry.get("category")),
        26: bool(entry.get("year")),
        27: isinstance(entry.get("location"), dict) and bool(entry["location"].get("precision")),
        28: bool(audit),
        37: bool(entry.get("people")),
        38: bool(deed_types),
        39: bool(entry.get("actor_type")),
        40: bool(entry.get("beneficiary")),
        77: isinstance(audit.get("spinoff_leads"), list),
        79: isinstance(entry.get("location"), dict) and bool(entry["location"].get("country")),
        123: bool(deed_types) and set(deed_types) <= DEED_TYPES,
        # מנגנון העצירה
        34: audit.get("state") in DEED_STATES,
        35: isinstance(audit.get("missing"), list),
        36: isinstance(audit.get("tried"), list) and (
            bool(audit.get("tried")) if audit.get("state") == "exhausted" else True
        ),
        150: gaps_ok,
        # תהליך עבודה
        140: isinstance(review.get("findings"), list) and all(
            (review.get(f) or "").strip() for f in ("at", "by", "verdict")
        ),
    }


AUTO_RULES = sorted(n for n, k, _ in RULES if k in (AUTO, AUTO_EYE))


def print_list():
    print(f"תקן דף המעשה — {len(RULES)} כללים\n")
    for n, kind, title in sorted(RULES):
        print(f"{n:>4}  {KIND_SYMBOL[kind]:<7} {title}")
    counts = Counter(k for _, k, _ in RULES)
    print("\nלפי סוג: " + " · ".join(
        f"{KIND_SYMBOL[k]} {counts[k]}" for k in (AUTO, AUTO_EYE, NET, EYE, UI, PROC)
    ))
    print(f"נבדקים אוטומטית כאן: {len(AUTO_RULES)}")


def print_fields():
    """Rule 152 — which required content fields the site actually shows."""
    if not SRC.is_dir():
        print("אין תיקיית src — אי אפשר לבדוק מה האתר מציג")
        return 1
    hidden = field_coverage()
    for field in CONTENT_FIELDS:
        print(f"  {'✗' if field in hidden else '✓'}  {field}")
    if hidden:
        print(f"\nשדות שהתקן דורש והאתר לא מציג: {', '.join(hidden)}")
        return 1
    print(f"\nכל {len(CONTENT_FIELDS)} שדות התוכן מגיעים למסך.")
    return 0


def verify_doc():
    """The document and this registry must hold the same rules."""
    doc_rules = {}
    for line in DOC.read_text().splitlines():
        cells = [c.strip() for c in line.split("|")]
        if len(cells) >= 6 and cells[1].isdigit():
            doc_rules[int(cells[1])] = cells[4]

    problems = []
    for n in sorted(set(doc_rules) | set(KINDS)):
        if n not in KINDS:
            problems.append(f"{n}: במסמך ולא בקוד")
        elif n not in doc_rules:
            problems.append(f"{n}: בקוד ולא במסמך")
        elif doc_rules[n] != KIND_SYMBOL[KINDS[n]]:
            problems.append(f"{n}: סוג שונה — מסמך {doc_rules[n]!r}, קוד {KIND_SYMBOL[KINDS[n]]!r}")

    missing_checks = [n for n in AUTO_RULES if n not in evaluate({})]
    problems += [f"{n}: מסומן אוטומטי ואין לו בדיקה" for n in missing_checks]

    if problems:
        print("אי־התאמות בין המסמך לקוד:")
        for p in problems:
            print("  " + p)
        return 1
    print(f"תקין — {len(doc_rules)} כללים במסמך, {len(RULES)} בקוד, אותה רשימה בדיוק.")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true", help="print the full numbered standard")
    ap.add_argument("--verify-doc", action="store_true", help="check code against the document")
    ap.add_argument("--failing", type=int, help="list deeds failing this rule")
    ap.add_argument("--fields", action="store_true", help="rule 152 — fields the site hides")
    ap.add_argument("--json", help="write the full per-deed report here")
    args = ap.parse_args()

    if args.list:
        return print_list()
    if args.fields:
        return print_fields()
    if args.verify_doc:
        return verify_doc()

    entries = fetch_entries()
    results = {e["id"]: evaluate(e) for e in entries}

    if args.failing:
        n = args.failing
        if n not in AUTO_RULES:
            print(f"כלל {n} — {TITLES.get(n, '?')}: {KIND_SYMBOL[KINDS[n]]}, לא נבדק כאן")
            return
        bad = [e for e in entries if not results[e["id"]][n]]
        print(f"כלל {n} — {TITLES[n]}: {len(bad)} נכשלים")
        for e in bad[:40]:
            print(f"  {e['id']}  {e['title'][:60]}")
        if len(bad) > 40:
            print(f"  ... ועוד {len(bad) - 40}")
        if n == 148:
            # A computation in a form this script cannot redo is not a failure,
            # but nobody should be able to mistake it for a verified one.
            unchecked = [(e["id"], v, x) for e in entries for v, x in check_numbers(e)[1]]
            print(f"\nחישובים שהבודק לא יודע לחזור עליהם: {len(unchecked)}")
            for deed_id, value, expr in unchecked[:20]:
                print(f"  {deed_id}  {value} = {expr}")
        return

    total = len(entries)
    print(f"תקן דף המעשה — {total} מעשים · {len(AUTO_RULES)} כללים נבדקים אוטומטית "
          f"(מתוך {len(RULES)})\n")
    print(f"{'#':>4}  {'כלל':<40} {'שדות מלאים':>10}  {'נכשלים':>7}")
    for n in AUTO_RULES:
        ok = sum(1 for r in results.values() if r[n])
        print(f"{n:>4}  {TITLES[n]:<40} {ok:>10}  {total - ok:>7}")

    # Two numbers, never one. A full score says no field was left blank; it
    # says nothing about whether what is in the fields is true. Only a hostile
    # reader says that, and rule 140 is where the reader signs.
    full_fields = sum(1 for r in results.values() if all(r.values()))
    verified = sum(1 for r in results.values() if r[140])
    print(f"\nשדות מלאים בכל הבדיקות האוטומטיות: {full_fields} מתוך {total}")
    print(f"אומת — עבר ביקורת אדברסרית (כלל 140): {verified} מתוך {total}")
    scores = Counter(sum(r.values()) for r in results.values())
    print("התפלגות ניקוד (מתוך %d): %s" % (len(AUTO_RULES), dict(sorted(scores.items()))))

    if args.json:
        Path(args.json).write_text(
            json.dumps(
                {e["id"]: {"title": e["title"], "checks": results[e["id"]]} for e in entries},
                ensure_ascii=False,
                indent=1,
            )
        )
        print(f"\nדוח מלא: {args.json}")


if __name__ == "__main__":
    sys.exit(main())
