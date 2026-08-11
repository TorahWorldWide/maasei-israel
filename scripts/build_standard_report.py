#!/usr/bin/env python3
"""Build the public before/after report for the deed-standard pass.

The other page (build_compare_site.py) puts two versions of a deed side by side,
field by field — it is a working tool. This one answers a different question:
what did the standard actually change, measured, with the real errors named.

  python3 scripts/build_standard_report.py --out /home/ubuntu/maasei-compare/standard

"before" is the earliest snapshot of each deed in docs/enrichment/backups;
"after" is read live from the database. The corrections come from the worker
outputs archived in docs/enrichment/standard-pass — the same files that were
written into the database, so nothing here is retold from memory.
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_claims import run_sql  # noqa: E402
from deed_standard import AUTO_RULES, RULES, evaluate  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BACKUPS = ROOT / "docs" / "enrichment" / "backups"
PASS_OUT = ROOT / "docs" / "enrichment" / "standard-pass"
LIVE = "https://maasei-israel.vercel.app"

PROSE = ["summary_short", "description", "origin_story", "act",
         "ripple", "aftermath", "recognition"]

# Short names, in the order the page shows them. The fifth is the deed that was
# rebuilt in an earlier generation of the pass — it stays on the page as itself.
DEEDS = [
    ("347192a7-eafd-402f-9216-fb7d27795bd2", "הדי לאמאר"),
    ("10da5666-5b73-4e50-b572-ac3a9e077c92", "ורבה־וצלר"),
    ("41f71ed3-5aae-4f2f-a35a-3cb64a9a1283", "עזר מציון"),
    ("4b74f9e1-4d2b-470b-8a57-48f3a57f693f", "UBQ"),
    ("988815b9-3564-4d60-9fcc-3f41bff6de29", "דן שכטמן"),
    ("f0ca86ec-0a88-4963-b340-ad2e4f790c2b", "בית־החולים בטורקיה"),
    ("81bfe740-07d5-4bea-860d-03cb8f27dc68", "דונה גרציה"),
]


def host(url):
    try:
        h = urlparse(url or "").netloc.lower()
        return h[4:] if h.startswith("www.") else h
    except Exception:
        return ""


def is_video(url):
    return bool(re.search(r"youtu\.?be|youtube\.com|vimeo\.com", url or "", re.I))


def provenance(row):
    return row.get("image_provenance") or ((row.get("audit") or {}).get("image_provenance")) or []


# Workers named the credit field four different ways. Any of them is a credit.
CREDIT_KEYS = ("credit", "source", "credit_line", "photographer", "published_in")


def has_credit(prov_item):
    return any((prov_item.get(k) or "").strip() for k in CREDIT_KEYS)


def measure(row):
    cits = row.get("citations") or []
    media = [u for u in (row.get("media_urls") or []) if not is_video(u)]
    prov = provenance(row)
    four = ["origin_story", "aftermath", "recognition"]
    return {
        "std": sum(1 for n in AUTO_RULES if evaluate(row).get(n)),
        "citations": len(cits),
        "domains": len({host(c.get("source_url")) for c in cits if c.get("source_url")}),
        "wiki": sum(1 for c in cits if "wikipedia.org" in (c.get("source_url") or "")),
        "located": sum(1 for c in cits if c.get("locator") and c.get("published")),
        "quoted": sum(1 for c in cits if (c.get("quote") or "").strip()),
        "images": len(media),
        "captioned": len([p for p in prov if (p.get("caption_he") or "").strip() and has_credit(p)]),
        "summary": 1 if (row.get("summary_short") or "").strip() else 0,
        "four": sum(1 for f in four if (row.get(f) or "").strip()) + (1 if row.get("honors") else 0),
        "people": len(row.get("people") or []),
        "location": 1 if row.get("location") else 0,
        "chars": sum(len(row.get(f) or "") for f in PROSE),
    }


def norm_correction(c):
    """Four workers, four key vocabularies. One shape for the page."""
    if isinstance(c, str):
        return {"label": "", "was": c, "now": "", "why": "", "url": ""}
    return {
        "label": c.get("what") if (c.get("before") or c.get("from")) else c.get("field") or "",
        "was": c.get("was") or c.get("before") or c.get("from") or (c.get("what") if not (c.get("before") or c.get("from")) else "") or "",
        "now": c.get("now") or c.get("after") or c.get("to") or "",
        "why": c.get("why") or c.get("basis") or c.get("note") or c.get("reason") or "",
        "url": c.get("evidence_url") or "",
    }


def norm_removal(r):
    if isinstance(r, str):
        return {"what": r, "why": ""}
    return {"what": r.get("what") or r.get("item") or "", "why": r.get("why") or r.get("reason") or ""}


def collect():
    before = {}
    for path in sorted(BACKUPS.glob("pre-standard-pass-*.json")):
        for row in json.loads(path.read_text(encoding="utf-8")):
            before.setdefault(row["id"], row)          # earliest snapshot wins

    ids = ",".join("'" + i + "'" for i, _ in DEEDS)
    after = {r["id"]: r for r in run_sql(f"select * from entries where id in ({ids})")}

    deeds = []
    for did, short in DEEDS:
        b, a = before.get(did, {}), after[did]
        work = {}
        wpath = PASS_OUT / f"{did}.json"
        if wpath.exists():
            work = json.loads(wpath.read_text(encoding="utf-8"))
        deeds.append({
            "id": did,
            "short": short,
            "year": a.get("year"),
            "title_before": b.get("title") or "",
            "title_after": a.get("title") or "",
            "src_before": b.get("source_url") or "",
            "src_after": a.get("source_url") or "",
            "m_before": measure(b),
            "m_after": measure(a),
            "corrections": [norm_correction(c) for c in (work.get("corrections") or [])],
            "removed": [norm_removal(r) for r in (work.get("removed") or [])],
            "disputes": len(work.get("disputes") or []),
            "unresolved": len(work.get("unresolved") or []),
            "delta": len(work.get("content_delta") or []),
            "tried": len(work.get("tried") or []),
            "status": work.get("status") or "",
            "failing": [n for n in AUTO_RULES if not evaluate(a).get(n)],
        })
    return deeds


def totals(deeds, side):
    keys = list(deeds[0][f"m_{side}"])
    return {k: sum(d[f"m_{side}"][k] for d in deeds) for k in keys}


def median(values):
    v = sorted(values)
    return v[len(v) // 2]


# מדד · לפני · אחרי · השורה שמסבירה מה נמדד. Numbers come from the data.
def table_rows(deeds):
    b, a = totals(deeds, "before"), totals(deeds, "after")
    n = len(deeds)
    perfect = sum(1 for d in deeds if d["m_after"]["std"] == len(AUTO_RULES))
    return [
        ("ציון מול התקן", f'{median([d["m_before"]["std"] for d in deeds])}/{len(AUTO_RULES)}',
         f'{median([d["m_after"]["std"] for d in deeds])}/{len(AUTO_RULES)}',
         f'המעש החציוני, מתוך {len(AUTO_RULES)} הכללים שנבדקים במכונה מתוך {len(RULES)}. '
         f'{perfect} מתוך {n} עוברים היום את כולם.', "score"),
        ("מקורות", str(b["citations"]), str(a["citations"]),
         "ציטוטים בכל שבעת המעשים יחד. כל אחד מהם עם קישור גלוי בדף, לחיץ, לא הערת שוליים.", "up"),
        ("דומיינים עצמאיים", str(median([d["m_before"]["domains"] for d in deeds])),
         str(median([d["m_after"]["domains"] for d in deeds])),
         "חמישה אתרים בלתי־תלויים הם הרצפה של התקן. חמישה ציטוטים מאותו אתר אינם חמישה מקורות.", "up"),
        ("ציטוטים מוויקיפדיה", str(b["wiki"]), str(a["wiki"]),
         "ויקיפדיה מותרת כמפת דרכים להערות השוליים שלה, ואסורה כאסמכתא.", "down"),
        ("ציטוט עם מיקום מדויק ותאריך", str(b["located"]), str(a["located"]),
         "עמוד, פסקה או חותם־זמן, ותאריך פרסום — כדי שאפשר יהיה לחזור בדיוק לאותה נקודה.", "up"),
        ("תמונות עם כיתוב וקרדיט", str(b["captioned"]), str(a["captioned"]),
         "תמונה בלי מקור, מועד וכיתוב היא אילוסטרציה. כאן היא צריכה להיות תיעוד.", "up"),
        ("תקציר פותח + “קרא עוד”", f'{b["summary"]}/{n}', f'{a["summary"]}/{n}',
         "הדף נפתח בסיפור בשלוש שורות, וכל השאר נפתח בלחיצה. קודם הדף פתח בקיר טקסט.", "up"),
        ("איך התחיל · מה קרה אחר כך · מה קיבלו · כבוד", f'{b["four"]}/{n * 4}', f'{a["four"]}/{n * 4}',
         "ארבעת השדות שהופכים ערך לסיפור. “לא רלוונטי” עם נימוק נחשב תשובה; שדה ריק לא.", "up"),
        ("אנשים מזוהים בשם", str(b["people"]), str(a["people"]),
         "שם בעברית ובאנגלית ותפקיד — לא “קבוצת חוקרים”.", "up"),
        ("מיקום עם רמת דיוק", f'{b["location"]}/{n}', f'{a["location"]}/{n}',
         "עיר אמיתית עם ציון כמה היא מדויקת, ולא ניחוש שנשמע טוב.", "up"),
        ("שגיאות שנמצאו ותוקנו", "—", str(sum(len(d["corrections"]) for d in deeds)),
         "כל אחת רשומה עם מה היה, מה נכתב במקומו, ומאיזה מקור.", "fix"),
        ("פריטים שנמחקו מהדף", "—", str(sum(len(d["removed"]) for d in deeds)),
         "טענה שלא נמצאה שוב באף מקור נמחקת. היא לא עוברת הלאה בשקט.", "fix"),
        ("מחלוקות שנרשמו במפורש", "0", str(sum(d["disputes"] for d in deeds)),
         "כשהמקורות חלוקים, הדף אומר זאת במקום לבחור בשקט את המספר היפה.", "fix"),
        ("שאלות שנשארו פתוחות", "0", str(sum(d["unresolved"] for d in deeds)),
         "מה שלא הוכרע נרשם כפתוח. זו הסיבה שהמספר הזה גדול מאפס בכוונה.", "fix"),
    ]


FEATURED = [
    {
        "deed": "הדי לאמאר",
        "kicker": "המצאה שלא הייתה",
        "before": "שחקנית הוליווד הדי לאמאר שותפה בהמצאת קפיצת־התדרים שבבסיס ה־Wi‑Fi",
        "after": "הדי לאמאר ואנתייל רשמו פטנט להכוונת טורפדו בקפיצת תדרים, ולא קיבלו עליו אגורה",
        "why": "תיק הפטנט מראה שהתביעה היחידה שניסחה את עקרון קפיצת התדרים נדחתה ב־13.8.1941 "
               "כמכוסה בפטנטים קודמים, ועורכי הדין מחקו אותה. ממציא הבלוטות׳ העיד שלא הכיר את הפטנט, "
               "וה־Wi‑Fi זנח קפיצת תדרים מוקדם. מה שנשאר — פטנט אמיתי, רעיון מקורי, ואפס תמורה — "
               "חזק יותר מהכותרת שנמחקה.",
        "src": "https://patents.google.com/patent/US2292387A/en",
        "src_label": "פטנט US 2,292,387 · Google Patents",
    },
    {
        "deed": "עזר מציון",
        "kicker": "הצלחה שהייתה כישלון",
        "before": "מבצע הגיוס של 1996 למען משה סחייק הוצג כהצלחה: 5,000 תורמים נרשמו.",
        "after": "המבצע לא מצא התאמה. סחייק מת. המאגר נולד מהכישלון הזה.",
        "why": "אתר עזר מציון עצמו כותב: “no match was found among the 5,000 people who participated "
               "in the drive. Sadly, the young man died”. הסוכן הקודם ספר את התורמים ודילג על הסוף. "
               "באותה הזדמנות נמחק מהדף גם מניע אישי שיוחס למייסדים ולא נמצא באף אחד מששת המקורות.",
        "src": "https://www.ezermizion.org/bone-marrow-registry/",
        "src_label": "מאגר מח העצם · עזר מציון",
    },
    {
        "deed": "בית־החולים בטורקיה",
        "kicker": "פועל שלא נעשה",
        "before": "צה”ל הקים בית־חולים שדה בטורקיה וחילץ פצועים מתחת להריסות.",
        "after": "צה”ל פתח מחדש את בית־החולים העירוני נג׳יפ פאזל בקהרמאנמרש, שננטש, וטיפל בו ב־470 פצועים.",
        "why": "שני כתבי־עת שפיטים כותבים במפורש “our personnel re-opened the hospital” ו־"
               "“decided to integrate with an existing hospital”. המשלחת אכן הגיעה עם יכולות של "
               "בית־חולים שדה, אך לא הקימה אותו. מאותו דף נמחק גם המשפט “רחוק מכל מצלמה” — "
               "המבצע תועד בהרחבה בעיתונות הטורקית והבינלאומית.",
        "src": "https://pmc.ncbi.nlm.nih.gov/articles/PMC10450639/",
        "src_label": "Journal of Global Health · PMC",
    },
    {
        "deed": "דן שכטמן",
        "kicker": "מונח שהומצא",
        "before": "“גילה דפוס הפזה שסתר את כל חוקי הגבישנות המקובלים”.",
        "after": "ראה תבנית עקיפה בעלת סימטריה של פי עשרה — סימטריה שגביש מחזורי אינו יכול להחזיק.",
        "why": "“דפוס הפזה” אינו מונח, ו”כל חוקי הגבישנות” הגזמה: מדובר באיסור אחד, ספציפי ומדיד. "
               "בדרך התברר שגם עמוד העובדות של NobelPrize.org שוגה ומדבר על קרני רנטגן — הגילוי נעשה "
               "במיקרוסקופ אלקטרוני, כפי שכתוב בהודעת הפרס של אותו גוף עצמו.",
        "src": "https://www.nobelprize.org/prizes/chemistry/2011/press-release/",
        "src_label": "הודעת הפרס · האקדמיה השוודית למדעים",
    },
]

HTML = """<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>מעשי ישראל — לפני ואחרי התקן</title>
<meta name="description" content="מה השתנה כששבעה מעשים נבנו מחדש מאפס לפי 131 כללי תקן דף המעשה.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Frank+Ruhl+Libre:wght@400;500;700&family=Heebo:wght@300;400;500;700&display=swap" rel="stylesheet">
<style>
:root{
  --navy:#0a1834; --navy-deep:#070f24; --card:#0f234d; --ink:#eaf1ff;
  --dim:#9fb3d9; --gold:#c9a84a; --gold-br:#e6c66e; --sky:#38bdf8;
  --line:rgba(201,168,74,.22); --line-soft:rgba(201,168,74,.12);
  --before:#8ea2c6; --after:#e6c66e; --good:#5fd39a; --warn:#f0a35e;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--navy);color:var(--ink);direction:rtl;text-align:right;
  font:400 16px/1.7 "Heebo",Arial,sans-serif;-webkit-font-smoothing:antialiased;
  background-image:
    radial-gradient(ellipse 80% 50% at 50% -10%,rgba(37,99,235,.22),transparent 60%),
    radial-gradient(ellipse 60% 50% at 50% 110%,rgba(201,168,74,.08),transparent 60%);
  background-attachment:fixed}
h1,h2,h3{font-family:"Frank Ruhl Libre",Georgia,serif;letter-spacing:-.01em;margin:0}
a{color:var(--gold-br);text-decoration:none}
a:hover{text-decoration:underline}
.wrap{max-width:1060px;margin:0 auto;padding:0 20px}
.gold-rule{height:1px;background:linear-gradient(to left,transparent,rgba(201,168,74,.55),transparent)}

/* ── stage ── */
.stage{position:relative;overflow:hidden;padding:74px 0 58px;
  background:radial-gradient(ellipse 120% 80% at 50% 0%,rgba(37,99,235,.18),transparent 55%),
    linear-gradient(to bottom,#070f24 0%,#0a1834 62%,#0a1834 100%)}
.stage::before,.stage::after{content:"";position:absolute;top:-14%;width:34%;height:135%;
  pointer-events:none;filter:blur(26px);opacity:.5}
.stage::before{right:8%;background:linear-gradient(198deg,rgba(230,198,110,.30),transparent 62%);
  transform:rotate(9deg)}
.stage::after{left:8%;background:linear-gradient(162deg,rgba(230,198,110,.30),transparent 62%);
  transform:rotate(-9deg)}
.stage .wrap{position:relative;z-index:2;text-align:center}
.eyebrow{font-size:12.5px;letter-spacing:.22em;color:var(--gold);text-transform:none;margin-bottom:16px}
.stage h1{font-size:clamp(34px,6.4vw,58px);font-weight:700;line-height:1.12}
.stage h1 em{font-style:normal;color:var(--gold-br)}
.lead{max-width:640px;margin:20px auto 0;color:#c8d6f0;font-size:clamp(15px,2.2vw,18px);font-weight:300}
.jump{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-top:30px}
.jump a{border:1px solid var(--line);border-radius:999px;padding:9px 18px;font-size:13.5px;
  color:var(--ink);background:rgba(15,35,77,.55);transition:.18s}
.jump a:hover{border-color:var(--gold);color:var(--gold-br);text-decoration:none;
  box-shadow:0 0 22px rgba(201,168,74,.14)}

/* ── headline numbers ── */
.marquee{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:14px;
  margin:-34px auto 0;position:relative;z-index:5}
.big{background:linear-gradient(180deg,rgba(15,35,77,.96),rgba(10,24,52,.96));
  border:1px solid var(--line);border-radius:18px;padding:20px 18px;text-align:center;
  box-shadow:0 18px 42px rgba(0,0,0,.34)}
.big .n{font-family:"Frank Ruhl Libre",serif;font-size:36px;font-weight:700;color:var(--gold-br);
  line-height:1.1;display:flex;align-items:baseline;justify-content:center;gap:9px}
.big .n s{text-decoration:none;color:var(--before);font-size:20px;font-weight:400;opacity:.85}
.big .n i{font-style:normal;color:var(--dim);font-size:17px}
.big .l{font-size:12.5px;color:var(--dim);margin-top:7px;letter-spacing:.02em}

section{padding:58px 0 0}
.head{display:flex;align-items:baseline;gap:14px;margin-bottom:8px;flex-wrap:wrap}
.head h2{font-size:clamp(23px,3.6vw,31px);font-weight:700}
.head span{color:var(--dim);font-size:14px;font-weight:300}
.sub{color:#c8d6f0;font-weight:300;max-width:720px;margin:14px 0 26px;font-size:15.5px}

/* ── the table ── */
.tbl{border:1px solid var(--line);border-radius:20px;overflow:hidden;
  background:linear-gradient(180deg,rgba(15,35,77,.82),rgba(10,24,52,.82))}
.tr{display:grid;grid-template-columns:1fr 118px 118px;gap:0;
  border-bottom:1px solid var(--line-soft);align-items:center}
.tr:last-child{border-bottom:0}
.tr.h{background:rgba(7,15,36,.7);border-bottom:1px solid var(--line)}
.tr.h b{font:500 12.5px/1.4 "Heebo";color:var(--dim);letter-spacing:.06em;padding:14px 12px;
  text-align:center;display:block}
.tr.h b:first-child{text-align:right;padding-inline-start:22px}
.tr.h b.a{color:var(--gold)}
.tc{padding:15px 12px;text-align:center;font-family:"Frank Ruhl Libre",serif;font-size:23px;font-weight:500}
.tc.b{color:var(--before)}
.tc.a{color:var(--gold-br)}
.tc small{display:block;font-family:"Heebo";font-size:11px;font-weight:400;color:var(--dim);margin-top:2px}
.tk{padding:15px 22px}
.tk b{font-weight:500;font-size:15.5px;display:block}
.tk span{color:var(--dim);font-size:13px;font-weight:300;line-height:1.6;display:block;margin-top:3px}
.tr.down .tc.a{color:var(--good)}
.tr.fix .tc.a{color:var(--sky)}
.tr.score{background:rgba(201,168,74,.05)}
.tr.score .tc{font-size:27px}

/* ── featured errors ── */
.cards{display:grid;gap:18px}
.card{border:1px solid var(--line);border-radius:20px;overflow:hidden;
  background:linear-gradient(180deg,rgba(15,35,77,.86),rgba(10,24,52,.86))}
.card>.top{display:flex;align-items:center;gap:12px;padding:15px 22px;
  border-bottom:1px solid var(--line-soft);flex-wrap:wrap}
.card .kick{font-family:"Frank Ruhl Libre",serif;font-size:19px;font-weight:700;color:var(--gold-br)}
.card .who{font-size:12.5px;color:var(--dim);border:1px solid var(--line);border-radius:999px;padding:3px 11px}
.ba{display:grid;grid-template-columns:1fr 1fr;gap:0}
.ba>div{padding:18px 22px}
.ba>div:first-child{border-inline-end:1px solid var(--line-soft)}
.tag{font-size:11.5px;letter-spacing:.12em;margin-bottom:9px;display:block}
.tag.b{color:var(--before)} .tag.a{color:var(--gold)}
.ba .t{font-size:15px;line-height:1.65}
.ba .b .t{color:#b7c6e2;text-decoration:line-through;text-decoration-color:rgba(240,163,94,.5);
  text-decoration-thickness:1px}
.card .why{padding:16px 22px 20px;border-top:1px solid var(--line-soft);color:#c8d6f0;
  font-size:14.5px;font-weight:300;background:rgba(7,15,36,.35)}
.card .why b{color:var(--ink);font-weight:500}
.card .why .src{display:inline-block;margin-top:10px;font-size:13px}

/* ── per deed ── */
nav.deeds{display:flex;gap:8px;overflow-x:auto;padding-bottom:14px;scrollbar-width:none}
nav.deeds::-webkit-scrollbar{display:none}
nav.deeds button{white-space:nowrap;border:1px solid var(--line);background:rgba(15,35,77,.6);
  color:var(--ink);border-radius:999px;padding:8px 16px;font:400 13.5px "Heebo";cursor:pointer;transition:.16s}
nav.deeds button:hover{border-color:var(--gold)}
nav.deeds button.on{background:var(--gold);border-color:var(--gold);color:#0a1834;font-weight:500}
.panel{border:1px solid var(--line);border-radius:20px;padding:24px;
  background:linear-gradient(180deg,rgba(15,35,77,.82),rgba(10,24,52,.82))}
.titles{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-bottom:20px}
.titles>div{min-width:0}
.titles .t{font-family:"Frank Ruhl Libre",serif;font-size:18px;line-height:1.45}
.titles .b .t{color:var(--before)}
.titles .a .t{color:var(--gold-br)}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0 4px}
.chip{border:1px solid var(--line-soft);background:rgba(7,15,36,.5);border-radius:10px;
  padding:7px 12px;font-size:12.5px;color:var(--dim)}
.chip b{color:var(--gold-br);font-weight:500;font-size:14px}
.chip s{text-decoration:none;color:var(--before);opacity:.8}
h3.mini{font-size:15px;color:var(--gold);margin:26px 0 12px;font-weight:500;
  display:flex;align-items:center;gap:10px}
h3.mini::after{content:"";flex:1;height:1px;background:var(--line-soft)}
.fix{border-inline-start:2px solid rgba(201,168,74,.45);padding:2px 16px;margin-bottom:16px}
.fix .lbl{font-size:12.5px;color:var(--gold);margin-bottom:5px}
.fix .was{color:#b7c6e2;font-size:14.5px}
.fix .was::before{content:"היה · ";color:var(--before);font-size:12px}
.fix .now{font-size:14.5px;margin-top:4px}
.fix .now::before{content:"הפך ל· ";color:var(--gold);font-size:12px}
.fix .why{color:var(--dim);font-size:13px;font-weight:300;margin-top:6px}
.rm{color:#c8d6f0;font-size:14px;margin-bottom:11px;padding-inline-start:16px;position:relative}
.rm::before{content:"✕";position:absolute;inset-inline-start:0;color:var(--warn);font-size:12px;top:3px}
.rm span{color:var(--dim);font-size:12.5px;font-weight:300;display:block}
.open{display:inline-flex;align-items:center;gap:7px;margin-top:22px;border:1px solid var(--line);
  border-radius:999px;padding:9px 18px;font-size:13.5px}
.open:hover{border-color:var(--gold);text-decoration:none}

/* ── honest panel ── */
.honest{border:1px solid rgba(240,163,94,.32);border-inline-start:3px solid var(--warn);
  border-radius:18px;padding:22px 24px;background:rgba(240,163,94,.05)}
.honest h3{font-size:19px;color:var(--warn);margin-bottom:10px}
.honest p{color:#c8d6f0;font-weight:300;font-size:15px;margin:0 0 10px}
.honest ul{margin:12px 0 0;padding-inline-start:20px;color:#c8d6f0;font-weight:300;font-size:14.5px}
.honest li{margin-bottom:7px}

footer{margin-top:70px;padding:34px 0 60px;text-align:center;color:var(--dim);font-size:13.5px}
footer .links{display:flex;gap:22px;justify-content:center;flex-wrap:wrap;margin-bottom:14px;font-size:14px}

@media(max-width:760px){
  .tr{grid-template-columns:1fr 78px 78px}
  .tk{padding:13px 15px}
  .tk span{font-size:12px}
  .tc{font-size:19px;padding:13px 6px}
  .tr.score .tc{font-size:21px}
  .ba,.titles{grid-template-columns:1fr}
  .ba>div:first-child{border-inline-end:0;border-bottom:1px solid var(--line-soft)}
  .panel{padding:18px}
}
</style>
</head>
<body>

<div class="stage">
  <div class="wrap">
    <div class="eyebrow">מעשי ישראל · דוח מעבר</div>
    <h1>אותם שבעה מעשים,<br><em>נבנו מחדש מאפס</em></h1>
    <p class="lead">הדפים האלה נכתבו פעם אחת בידי סוכנים מהירים, ואז נכתבו שוב לפי תקן דף
      המעשה — __RULES__ כללים. הדף הזה מראה מה נמדד, מה תוקן, ומה נמחק בדרך.</p>
    <div class="jump">
      <a href="#table">הטבלה</a>
      <a href="#errors">ארבע שגיאות אמיתיות</a>
      <a href="#deeds">מעש־מעש</a>
      <a href="#honest">מה עוד לא מושלם</a>
    </div>
  </div>
</div>

<div class="wrap">
  <div class="marquee">__MARQUEE__</div>

  <section id="table">
    <div class="head"><h2>מה נמדד</h2><span>שבעת המעשים יחד · נבדק במכונה, לא בהערכה</span></div>
    <p class="sub">כל מספר בטבלה מחושב מהשורה החיה במסד ומהגיבוי שנשמר לפניה. אין כאן דיווח
      עצמי של סוכן: הציון נגזר מ־__AUTO__ הכללים שאפשר להכריע בקוד.</p>
    <div class="tbl">
      <div class="tr h"><b>מדד</b><b>לפני</b><b class="a">אחרי</b></div>
      __TABLE__
    </div>
  </section>

  <section id="errors">
    <div class="head"><h2>ארבע שגיאות אמיתיות</h2><span>מתוך __NFIX__ שתוקנו</span></div>
    <p class="sub">לא דוגמאות להמחשה — אלה ההבדלים שיושבים באתר עכשיו, כל אחד עם המקור
      שהכריע אותו.</p>
    <div class="cards">__FEATURED__</div>
  </section>

  <section id="deeds">
    <div class="head"><h2>מעש־מעש</h2><span>הכותרת, המספרים, וכל תיקון</span></div>
    <p class="sub">שבעה מעשים. שישה מהם נבנו מחדש בפועל לפי התקן המלא; דונה גרציה עברה דור
      קודם של המעבר ונשארת כאן כפי שהיא.</p>
    <nav class="deeds" id="tabs"></nav>
    <div class="panel" id="panel"></div>
  </section>

  <section id="honest">
    <div class="head"><h2>מה עוד לא מושלם</h2></div>
    <div class="honest">
      <h3>הדף הזה לא נכתב כדי לנצח</h3>
      <p>מעש שכל מקורותיו מהללים אותו הוא מעש שלא נבדק. אלה הדברים שנשארו פתוחים אחרי המעבר,
        ומופיעים כאן במכוון:</p>
      <ul>__HONEST__</ul>
    </div>
  </section>

  <footer>
    <div class="gold-rule" style="margin-bottom:26px"></div>
    <div class="links">
      <a href="https://maasei-israel.vercel.app">האתר החי</a>
      <a href="../">השוואת שדה־מול־שדה</a>
    </div>
    <div>נבנה __BUILT__ · המספרים נמדדו מהמסד ברגע הבנייה</div>
  </footer>
</div>

<script id="data" type="application/json">__DATA__</script>
<script>
const D = JSON.parse(document.getElementById('data').textContent);
let cur = 0;
const esc = s => (s==null?'':String(s)).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

function chips(d){
  const rows = [['ציון',            'std',  '/'+D.autoRules],
                ['מקורות',          'citations', ''],
                ['דומיינים',        'domains', ''],
                ['ויקיפדיה',        'wiki', ''],
                ['תמונות עם קרדיט', 'captioned', ''],
                ['אנשים',           'people', '']];
  return rows.map(([l,k,suf])=>{
    const b=d.m_before[k], a=d.m_after[k];
    return `<div class="chip">${l} <b>${a}${suf}</b>${b!==a?` <s>היה ${b}${suf}</s>`:''}</div>`;
  }).join('');
}

function panel(){
  const d = D.deeds[cur];
  const fixes = d.corrections.map(c=>`<div class="fix">
      ${c.label?`<div class="lbl">${esc(c.label)}</div>`:''}
      ${c.was?`<div class="was">${esc(c.was)}</div>`:''}
      ${c.now?`<div class="now">${esc(c.now)}</div>`:''}
      ${c.why?`<div class="why">${esc(c.why)}${c.url?` · <a href="${esc(c.url)}" target="_blank" rel="noopener">המקור</a>`:''}</div>`:''}
    </div>`).join('');
  const rms = d.removed.map(r=>`<div class="rm">${esc(r.what)}
      ${r.why?`<span>${esc(r.why)}</span>`:''}</div>`).join('');
  document.getElementById('panel').innerHTML = `
    <div class="titles">
      <div class="b"><span class="tag b">הכותרת שהייתה</span><div class="t">${esc(d.title_before)}</div></div>
      <div class="a"><span class="tag a">הכותרת היום</span><div class="t">${esc(d.title_after)}</div></div>
    </div>
    <div class="chips">${chips(d)}</div>
    ${fixes?`<h3 class="mini">תוקן · ${d.corrections.length}</h3>${fixes}`:''}
    ${rms?`<h3 class="mini">נמחק מהדף · ${d.removed.length}</h3>${rms}`:''}
    <a class="open" href="${D.live}/deed/${d.id}" target="_blank" rel="noopener">← לדף החי של ${esc(d.short)}</a>`;
}
function tabs(){
  document.getElementById('tabs').innerHTML = D.deeds.map((d,i)=>
    `<button class="${i===cur?'on':''}" data-i="${i}">${esc(d.short)}</button>`).join('');
}
document.getElementById('tabs').addEventListener('click',e=>{
  const b=e.target.closest('button'); if(!b) return;
  cur=+b.dataset.i; tabs(); panel();
});
tabs(); panel();
</script>
</body></html>
"""


def esc(s):
    return (str(s or "").replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def render(deeds, out):
    b, a = totals(deeds, "before"), totals(deeds, "after")
    n = len(deeds)
    nfix = sum(len(d["corrections"]) for d in deeds)
    nrm = sum(len(d["removed"]) for d in deeds)

    marquee = [
        (f'<span dir="ltr">{median([d["m_after"]["std"] for d in deeds])}/{len(AUTO_RULES)}</span>',
         f'היה {median([d["m_before"]["std"] for d in deeds])}', "ציון התקן, המעש החציוני"),
        (str(a["citations"]), f'היו {b["citations"]}', "מקורות עם קישור גלוי"),
        (str(nfix + nrm), "", "שגיאות שתוקנו ופריטים שנמחקו"),
        (str(a["wiki"]), f'היו {b["wiki"]}', "ציטוטים מוויקיפדיה"),
    ]
    marquee_html = "".join(
        f'<div class="big"><div class="n">{v}{f"<s>{was}</s>" if was else ""}</div>'
        f'<div class="l">{lbl}</div></div>' for v, was, lbl in marquee)

    rows_html = "".join(
        f'<div class="tr {cls}"><div class="tk"><b>{esc(k)}</b><span>{esc(note)}</span></div>'
        f'<div class="tc b">{esc(bv)}</div><div class="tc a">{esc(av)}</div></div>'
        for k, bv, av, note, cls in table_rows(deeds))

    feat_html = "".join(f"""<article class="card">
      <div class="top"><span class="kick">{esc(f['kicker'])}</span><span class="who">{esc(f['deed'])}</span></div>
      <div class="ba">
        <div class="b"><span class="tag b">מה שהיה כתוב</span><div class="t">{esc(f['before'])}</div></div>
        <div class="a"><span class="tag a">מה שכתוב היום</span><div class="t">{esc(f['after'])}</div></div>
      </div>
      <div class="why">{esc(f['why'])}
        <a class="src" href="{esc(f['src'])}" target="_blank" rel="noopener">↗ {esc(f['src_label'])}</a></div>
    </article>""" for f in FEATURED)

    partial = [d["short"] for d in deeds if d["status"] == "partial"]
    low = [d for d in deeds if d["m_after"]["std"] < len(AUTO_RULES)]
    honest = [
        f'<li><b>{sum(d["unresolved"] for d in deeds)} שאלות נשארו בלי תשובה</b> ונרשמו ככאלה. '
        f'שדה שכתוב בו “לא הוכרע” הוא תשובה עוברת בתקן; שדה ריק אינו.</li>',
        f'<li><b>{sum(d["disputes"] for d in deeds)} מחלוקות בין מקורות</b> נכתבו בדף כטווח ולא כמספר אחד — '
        'תאריך הבריחה מאושוויץ, גודל המשלחת לטורקיה, כמות ה־CO₂ שנחסכת לטונה.</li>',
    ]
    if partial:
        honest.append(f'<li><b>{len(partial)} מעשים סומנו <span dir="ltr">partial</span></b> '
                      f'({" · ".join(partial)}) — נגמר להם תקציב החיפוש לפני שנסגר '
                      'הכול, ומה שחסר רשום בשורה עצמה.</li>')
    for d in low:
        honest.append(f'<li><b>{esc(d["short"])} עומד על {d["m_after"]["std"]}/{len(AUTO_RULES)}</b> — '
                      'עבר דור קודם של המעבר, לפני שהתקן נסגר. הוא בתור לבנייה מחדש כמו כולם.</li>')
    honest.append('<li><b>אף מעש כאן אינו “פטור”.</b> גם מעש שתוקן חוזר לתור — '
                  'מי שתיקן יכול היה לפספס בדיוק כמו מי שכתב.</li>')

    payload = {
        "live": LIVE, "autoRules": len(AUTO_RULES),
        "deeds": [{k: d[k] for k in
                   ("id", "short", "title_before", "title_after", "m_before", "m_after",
                    "corrections", "removed", "status")} for d in deeds],
    }

    html = (HTML
            .replace("__RULES__", str(len(RULES)))
            .replace("__AUTO__", str(len(AUTO_RULES)))
            .replace("__NFIX__", str(nfix))
            .replace("__MARQUEE__", marquee_html)
            .replace("__TABLE__", rows_html)
            .replace("__FEATURED__", feat_html)
            .replace("__HONEST__", "".join(honest))
            .replace("__BUILT__", datetime.now(timezone.utc).strftime("%d.%m.%Y"))
            .replace("__DATA__", json.dumps(payload, ensure_ascii=False, default=str)))

    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(html, encoding="utf-8")
    print(f"wrote {out/'index.html'}  ({len(html)//1024} KB, {n} deeds, "
          f"{nfix} corrections, {nrm} removals)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/home/ubuntu/maasei-compare/standard")
    args = ap.parse_args()
    render(collect(), Path(args.out))


if __name__ == "__main__":
    main()
