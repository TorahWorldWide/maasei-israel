#!/usr/bin/env python3
"""Score every deed against docs/DEED-STANDARD.md.

The registry below holds all 128 rules of the standard — not only the ones a
script can decide. Rules that need a network fetch, a reader's judgment, a UI
check or a run-time procedure are listed with the place they are enforced, so
the document and the code hold the same list and `--verify-doc` can prove it.

  python3 scripts/deed_standard.py             # summary
  python3 scripts/deed_standard.py --list      # the full numbered list
  python3 scripts/deed_standard.py --failing 3 # which deeds fail rule 3
  python3 scripts/deed_standard.py --verify-doc
  python3 scripts/deed_standard.py --json out.json
"""
import argparse
import json
import re
import sys
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "DEED-STANDARD.md"
YOUTUBE = re.compile(r"youtu\.?be|youtube\.com", re.I)
HEBREW = re.compile(r"[֐-׿]")
IMAGE_EXT = re.compile(r"\.(jpe?g|png|webp|gif)(\?|$)", re.I)
NOT_RELEVANT = re.compile(r"^\s*(לא רלוונטי|לא רלבנטי|not relevant|n/?a)\b[\s—–:,.-]*", re.I)
# A sentence break is terminal punctuation followed by space or end of text, so
# "11.8" and "2,292,387" do not split.
SENTENCE_SPLIT = re.compile(r"(?<=[.!?…])\s+")
HONOR_WORDS = re.compile(r"כבוד|honors?|פרס|הנצחה|על שמ", re.I)

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
    # פרק ג — סרטונים
    (10, AUTO, "עד 5 סרטונים"),
    (13, NET, "כל סרטון מתנגן בהטמעה"),
    (14, EYE, "סרטון־על אחד מסומן עם נימוק"),
    (15, EYE, "המעש הוא הנושא המרכזי בסרטון"),
    (16, EYE, "תמליל נמשך ונקרא לכל סרטון"),
    (48, AUTO, "שורת משנה לכל סרטון"),
    (62, AUTO, "שרשרת נפילה לתמלול מתועדת"),
    (63, UI, "חצים לניווט בין הסרטונים"),
    # פרק ד — תוכן
    (18, AUTO_EYE, "שנה קיימת — ושהיא שנת המעשה"),
    (19, AUTO, "חלק א׳ + חלק ב׳ מלאים"),
    (20, AUTO, "תרגום אנגלי מלא"),
    (21, EYE, "אין סתירה פנימית במספרים"),
    (22, EYE, "אין אגדה"),
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
    (130, AUTO_EYE, "תקציר כיף, 3–10 משפטים"),
    (68, EYE, "חומר ביוגרפי שלא שייך — בצד"),
    (69, UI, "עברית או אנגלית, לא מעורבב"),
    (70, UI, "ברירת מחדל לפי מדינת הגולש"),
    (71, UI, "טקסט קומפקטי"),
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
    hebrew_quotes_translated = all(
        not HEBREW.search(c.get("quote") or "") or (c.get("quote_en") or "").strip()
        for c in cites
    )

    audit = entry.get("audit") if isinstance(entry.get("audit"), dict) else {}
    rebuild = audit.get("rebuild") if isinstance(audit.get("rebuild"), dict) else {}
    provenance = audit.get("image_provenance") or []
    captioned = {p.get("url") for p in provenance if (p.get("caption_he") or "").strip()}
    video_entries = audit.get("videos") or []
    summary = (entry.get("summary_short") or "").strip()
    summary_sentences = len([s for s in SENTENCE_SPLIT.split(summary) if s.strip()])
    honors = entry.get("honors")
    honors_reason = any(
        HONOR_WORDS.search(str(u)) for u in (audit.get("unresolved") or [])
    )
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
        # תמונות
        8: len(images) >= 5,
        9: all(IMAGE_EXT.search(u) for u in images) if images else False,
        44: bool(images) and all(u in captioned for u in images),
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
        19: filled("act", "ripple"),
        20: english_ok and hebrew_quotes_translated,
        32: all((c.get("published") or "").strip() for c in cites) if cites else False,
        42: bool(delta),
        43: bool(pre) and any(
            (pre.get(f) or "") != (entry.get(f) or "") for f in ("description", "act", "ripple")
        ),
        64: filled("origin_story"),
        65: filled("aftermath"),
        66: reasoned("recognition"),
        67: isinstance(honors, list) and (bool(honors) or honors_reason),
        130: 3 <= summary_sentences <= 10,
        # כותרות
        73: 6 <= len(title.split()) <= 12,
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
    ap.add_argument("--json", help="write the full per-deed report here")
    args = ap.parse_args()

    if args.list:
        return print_list()
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
        return

    total = len(entries)
    print(f"תקן דף המעשה — {total} מעשים · {len(AUTO_RULES)} כללים נבדקים אוטומטית "
          f"(מתוך {len(RULES)})\n")
    print(f"{'#':>4}  {'כלל':<40} {'עומדים':>7}  {'נכשלים':>7}")
    for n in AUTO_RULES:
        ok = sum(1 for r in results.values() if r[n])
        print(f"{n:>4}  {TITLES[n]:<40} {ok:>7}  {total - ok:>7}")

    perfect = sum(1 for r in results.values() if all(r.values()))
    print(f"\nעומדים בכל הבדיקות האוטומטיות: {perfect} מתוך {total}")
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
