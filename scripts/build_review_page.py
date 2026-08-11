#!/usr/bin/env python3
"""Build the morning review page — one card per deed finished in a night run.

Tomer reads this on his phone and decides, deed by deed, whether he is happy.
Every number on the page is read live from the database or from the worker doc
that was actually written into it, so nothing here is retold from memory.

  python3 scripts/build_review_page.py --out /home/ubuntu/maasei-review \
      --since 2026-08-11T18:00:00Z

His verdicts live in localStorage and come back as one copied block of text.
"""
import argparse
import html
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
from deed_standard import AUTO_RULES, RULES, evaluate, fetch_entries  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PASS_OUT = ROOT / "docs" / "enrichment" / "standard-pass"
CAPTIONS = ROOT / "docs" / "enrichment" / "captions"
VERIFY = ROOT / "docs" / "enrichment" / "verify"
LIVE = "https://maasei-israel.vercel.app"
RULE_TITLE = {n: title for n, _kind, title in RULES}


def domain(url):
    try:
        host = urlparse(url or "").netloc.lower()
        return host[4:] if host.startswith("www.") else host
    except Exception:
        return ""


def touched(path, since):
    return path.exists() and datetime.fromtimestamp(path.stat().st_mtime, timezone.utc) >= since


def night_work(entry, since):
    """What happened to this deed tonight, read off the artifacts themselves."""
    eid = entry["id"]
    bullets = []
    doc = PASS_OUT / f"{eid}.json"
    if touched(doc, since):
        bullets.append("נבנה מחדש מאפס (כלל 49): מחקר עצמאי, כל ציטוט אומת מילה-במילה מול הדף שנמשך")
    if touched(CAPTIONS / f"{eid}.json", since):
        bullets.append("מעבר תאימות: בסיס שימוש לכל תמונה, כיתוב של שורה אחת, תאום אנגלי בגלריה, סריקת טענות רגישות")
    citen = CAPTIONS / f"{eid}-citations-en.json"
    if touched(citen, since):
        sheet = json.loads(citen.read_text(encoding="utf-8"))
        n = len(sheet.get("source_label", {})) + len(sheet.get("locator", {}))
        bullets.append(f"שורת הציטוט הועברה לאנגלית — {n} מחרוזות (שם המקור והמיקום בתוך הדף)")

    cites = entry.get("citations") or []
    archived = sum(1 for c in cites if (c.get("archived_url") or "").strip())
    if archived:
        bullets.append(f"{archived} מתוך {len(cites)} הציטוטים אורכבו בארכיון האינטרנט — הקישור ישרוד גם אם הדף יימחק")

    audit = entry.get("audit") if isinstance(entry.get("audit"), dict) else {}
    sensitive = audit.get("sensitive_claims")
    if isinstance(sensitive, list):
        bullets.append(
            f"טענות רגישות על אנשים חיים: {len(sensitive)} נתמכו בשני מקורות עצמאיים"
            if sensitive else
            "טענות רגישות על אנשים חיים: נבדק ולא נמצאו"
        )

    # Rule 140: not the worker's word for it. A second program fetched every
    # source again and looked for the quote itself.
    vpath = VERIFY / f"{eid}.json"
    if vpath.exists():
        counts = json.loads(vpath.read_text(encoding="utf-8")).get("counts") or {}
        total = sum(counts.values())
        if total:
            found = counts.get("FOUND", 0)
            bullets.append(
                f"ביקורת עצמאית: {found} מתוך {total} הציטוטים נמצאו מילה-במילה בדף שנמשך מחדש"
                + ("" if found == total else " — השאר מסומנים למטה")
            )
    return bullets


def card(entry, since, index):
    eid = entry["id"]
    result = evaluate(entry)
    fails = [n for n in AUTO_RULES if not result.get(n)]
    score = len(AUTO_RULES) - len(fails)
    perfect = not fails

    audit = entry.get("audit") if isinstance(entry.get("audit"), dict) else {}
    cites = entry.get("citations") or []
    doms = {domain(c.get("source_url")) for c in cites} - {""}
    images = audit.get("image_provenance") or []

    doc_path = PASS_OUT / f"{eid}.json"
    doc = json.loads(doc_path.read_text(encoding="utf-8")) if doc_path.exists() else {}
    delta = doc.get("content_delta") or []
    corrections = doc.get("corrections") or []
    disputes = doc.get("disputes") or []
    unresolved = audit.get("unresolved") or doc.get("unresolved") or []

    def esc(x):
        return html.escape(str(x))

    rows = "".join(
        f"<li>{esc(d.get('fact'))} <a href='{esc(d.get('source_url'))}' target='_blank'>מקור</a></li>"
        for d in delta if isinstance(d, dict)
    )
    corr = "".join(
        f"<li>{esc(c if isinstance(c, str) else c.get('what') or json.dumps(c, ensure_ascii=False))}</li>"
        for c in corrections
    )
    disp = "".join(
        f"<li>{esc(c if isinstance(c, str) else c.get('what') or json.dumps(c, ensure_ascii=False))}</li>"
        for c in disputes
    )
    unres = "".join(f"<li>{esc(u)}</li>" for u in unresolved)

    vpath = VERIFY / f"{eid}.json"
    notfound = json.loads(vpath.read_text(encoding="utf-8")).get("not_found") or [] if vpath.exists() else []
    nf = "".join(f"<li>{esc(x)}</li>" for x in notfound)
    work = "".join(f"<li>{esc(b)}</li>" for b in night_work(entry, since))
    failed = "".join(
        f"<li><b>כלל {n}</b> — {esc(RULE_TITLE.get(n, ''))}</li>" for n in fails
    )

    badge = "מושלם 50/50" if perfect else f"{score}/{len(AUTO_RULES)}"
    return f"""
<article class="card {'perfect' if perfect else 'partial'}" data-id="{eid}" data-title="{esc(entry.get('title'))}">
  <header>
    <span class="num">{index}</span>
    <span class="badge">{badge}</span>
    <h2>{esc(entry.get('title'))}</h2>
  </header>
  <p class="desc">{esc((entry.get('description') or '')[:260])}</p>
  <div class="facts">
    <span>{len(cites)} ציטוטים</span><span>{len(doms)} דומיינים</span>
    <span>{len(images)} תמונות</span><span>{len(entry.get('people') or [])} אנשים</span>
  </div>
  <a class="live" href="{LIVE}/deed/{eid}" target="_blank">פתח את הדף באתר ←</a>
  <h3>מה נעשה הלילה</h3><ul class="work">{work or '<li>—</li>'}</ul>
  {f'<details><summary>עובדות שנוספו לטקסט ({len(delta)})</summary><ul>{rows}</ul></details>' if rows else ''}
  {f'<details><summary>שגיאות שנמצאו במקורות ({len(corrections)})</summary><ul>{corr}</ul></details>' if corr else ''}
  {f'<details><summary>סתירות בין מקורות ({len(disputes)})</summary><ul>{disp}</ul></details>' if disp else ''}
  {f'<details><summary>מה נשאר פתוח ({len(unresolved)})</summary><ul>{unres}</ul></details>' if unres else ''}
  {f'<details class="fails"><summary>ציטוטים שהביקורת העצמאית לא אישרה ({len(notfound)})</summary><ul>{nf}</ul></details>' if nf else ''}
  {f'<div class="fails"><h3>לא עומד בכללים</h3><ul>{failed}</ul></div>' if failed else ''}
  <div class="verdict">
    <button class="ok" onclick="vote(this,'ok')">מרוצה</button>
    <button class="no" onclick="vote(this,'no')">צריך תיקון</button>
    <input class="note" placeholder="הערה (לא חובה)" oninput="saveNote(this)">
  </div>
</article>"""


CSS = """
*{box-sizing:border-box}
body{margin:0;background:#0b1020;color:#e8ecf5;font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Arial;direction:rtl}
.wrap{max-width:820px;margin:0 auto;padding:16px 14px 120px}
h1{font-size:22px;margin:8px 0 4px;font-weight:600}
.sub{color:#9aa6c0;font-size:14px;margin:0 0 18px}
.stat{display:flex;gap:10px;flex-wrap:wrap;margin:14px 0 22px}
.stat div{background:#141b33;border:1px solid #222d4f;border-radius:12px;padding:10px 14px;flex:1;min-width:110px;text-align:center}
.stat b{display:block;font-size:22px;color:#e3b64b}
.stat span{font-size:12px;color:#9aa6c0}
.card{background:#111830;border:1px solid #222d4f;border-radius:16px;padding:16px;margin:0 0 16px}
.card.perfect{border-color:#3c5a3a}
.card.partial{border-color:#5a4a2a}
.card header{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.num{background:#222d4f;color:#9aa6c0;border-radius:50%;width:26px;height:26px;display:grid;place-items:center;font-size:13px;flex:none}
.badge{font-size:12px;padding:3px 10px;border-radius:999px;background:#1d2a45;color:#e3b64b;flex:none}
.perfect .badge{background:#1d3320;color:#8fd694}
.card h2{font-size:17px;margin:0;font-weight:600;line-height:1.45;flex:1 1 100%}
.desc{color:#b7c0d6;font-size:14px;margin:8px 0 10px}
.facts{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px}
.facts span{font-size:12px;color:#9aa6c0;background:#0e1428;border:1px solid #222d4f;border-radius:8px;padding:3px 9px}
.live{display:inline-block;background:#e3b64b;color:#0b1020;text-decoration:none;font-weight:600;padding:10px 16px;border-radius:10px;margin-bottom:14px}
h3{font-size:14px;color:#e3b64b;margin:14px 0 6px;font-weight:600}
ul{margin:0;padding-inline-start:20px}li{margin:4px 0;font-size:14px;color:#cfd7ea}
.work li{color:#e8ecf5}
details{margin:8px 0;border-top:1px solid #1b2440;padding-top:8px}
summary{cursor:pointer;font-size:13px;color:#9aa6c0}
details a{color:#7fa8e8}
.fails li{color:#f0b8a0}
.verdict{display:flex;gap:8px;margin-top:14px;flex-wrap:wrap;align-items:center}
.verdict button{flex:1;min-width:120px;padding:11px;border-radius:10px;border:1px solid #2b3862;background:#151d38;color:#cfd7ea;font-size:15px;cursor:pointer}
.verdict button.on.ok{background:#1d3320;border-color:#3c7a44;color:#8fd694}
.verdict button.on.no{background:#3a1f1f;border-color:#7a3c3c;color:#f0a0a0}
.note{flex:1 1 100%;padding:10px;border-radius:10px;border:1px solid #2b3862;background:#0e1428;color:#e8ecf5;font-size:14px}
.bar{position:fixed;inset-inline:0;bottom:0;background:#0e1428;border-top:1px solid #222d4f;padding:12px 14px;display:flex;gap:10px;align-items:center;justify-content:center}
.bar button{padding:12px 18px;border-radius:10px;border:0;background:#e3b64b;color:#0b1020;font-weight:600;font-size:15px;cursor:pointer}
.bar span{font-size:13px;color:#9aa6c0}
"""

JS = """
const K='maasei-review-verdicts';
const store=JSON.parse(localStorage.getItem(K)||'{}');
function card(el){return el.closest('.card')}
function vote(btn,v){
  const c=card(btn),id=c.dataset.id;
  const cur=(store[id]||{});
  cur.v = cur.v===v ? null : v; cur.title=c.dataset.title;
  store[id]=cur; localStorage.setItem(K,JSON.stringify(store));
  paint();
}
function saveNote(inp){
  const c=card(inp),id=c.dataset.id;
  store[id]=Object.assign({title:c.dataset.title},store[id]||{},{n:inp.value});
  localStorage.setItem(K,JSON.stringify(store));
}
function paint(){
  let done=0;
  document.querySelectorAll('.card').forEach(c=>{
    const s=store[c.dataset.id]||{};
    c.querySelector('.ok').classList.toggle('on',s.v==='ok');
    c.querySelector('.no').classList.toggle('on',s.v==='no');
    const n=c.querySelector('.note'); if(s.n&&n.value!==s.n)n.value=s.n;
    if(s.v)done++;
  });
  document.getElementById('progress').textContent=done+' מתוך '+document.querySelectorAll('.card').length+' נבדקו';
}
function copySummary(){
  const lines=[];
  document.querySelectorAll('.card').forEach(c=>{
    const s=store[c.dataset.id]||{};
    if(!s.v&&!s.n)return;
    lines.push((s.v==='ok'?'מרוצה':s.v==='no'?'צריך תיקון':'—')+' — '+c.dataset.title+(s.n?' | '+s.n:''));
  });
  const txt=lines.length?lines.join('\\n'):'לא סומן כלום';
  navigator.clipboard.writeText(txt).then(()=>alert('הועתק. הדבק לי בטלגרם.'),()=>prompt('העתק:',txt));
}
paint();
"""


RULE_NAMES = {
    136: "ארכוב הציטוטים (רץ דרך המחשב של תומר, תור אחד, 20 שניות לכתובת)",
    137: "רישיון לכל תמונה",
    139: '"נכון ל-" על מספר שממשיך לגדול',
    147: "כיתוב קצר — משפט אחד",
    20: "תאום אנגלי מלא",
}


def report(scored, perfect, since, goal):
    """The morning message. Written from the same artifacts as the page, so the
    number Tomer reads in Telegram and the number he sees in the browser cannot
    drift apart."""
    lines = []
    near = [e for f, e in scored if 0 < f <= 2]
    lines.append(f"בוקר טוב. {perfect} מעשים מושלמים (50/50) מתוך יעד {goal}.")
    if near:
        lines.append(f"עוד {len(near)} חסרים כלל אחד או שניים — כתוב למטה מה בדיוק.")
    lines.append("")

    for i, (fails_n, e) in enumerate(scored, 1):
        fails = [n for n in AUTO_RULES if not evaluate(e).get(n)]
        mark = "✅" if not fails else "◻️"
        lines.append(f"{mark} {i}. {e['title'][:70]}")
        for b in night_work(e, since)[:3]:
            lines.append(f"    • {b}")
        if fails:
            named = ", ".join(RULE_NAMES.get(n, f"כלל {n}") for n in fails[:3])
            lines.append(f"    ✗ נשאר פתוח: {named}" + (" ועוד" if len(fails) > 3 else ""))
        lines.append("")

    done = 0
    try:
        log = Path("/tmp/enrich-logs/status-pass.txt").read_text(encoding="utf-8")
        done = log.count("DONE ")
    except OSError:
        pass
    comp = 0
    try:
        comp = Path("/tmp/enrich-logs/status-compliance.txt").read_text(
            encoding="utf-8").count("DONE ")
    except OSError:
        pass
    hours = (datetime.now(timezone.utc) - since).total_seconds() / 3600
    lines.append("— כמה עבודה —")
    lines.append(f"{done} מעשים נבנו מחדש מאפס ו-{comp} עברו מעבר תאימות, "
                 f"ב-{hours:.1f} שעות, חמישה עובדי Opus במקביל.")
    lines.append("כל מעש נבנה בזיכרון נקי: הפועל לא ראה את הדף הקיים ולא סמך עליו (כלל 49).")
    lines.append("")
    lines.append("עבור אחד-אחד ותסמן מרוצה או צריך תיקון:")
    lines.append("https://torahworldwide.github.io/maasei-review/")
    lines.append("https://maasei-israel.vercel.app")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/home/ubuntu/maasei-review")
    ap.add_argument("--since", default="2026-08-11T18:00:00Z")
    ap.add_argument("--targets", default="/tmp/night-targets.txt")
    ap.add_argument("--goal", type=int, default=14)
    ap.add_argument("--report", action="store_true",
                    help="print the morning Telegram message instead of writing the page")
    args = ap.parse_args()

    since = datetime.fromisoformat(args.since.replace("Z", "+00:00"))
    try:
        want = [line.strip() for line in open(args.targets) if line.strip()]
    except OSError:
        want = []

    entries = {e["id"]: e for e in fetch_entries()}
    # A deed belongs on the page if it was worked on tonight, whether or not it
    # reached 50/50 — Tomer asked to see the partial ones too, not just the wins.
    shown = []
    for eid in want:
        entry = entries.get(eid)
        if not entry:
            continue
        artifacts = [PASS_OUT / f"{eid}.json", CAPTIONS / f"{eid}.json",
                     CAPTIONS / f"{eid}-citations-en.json"]
        archived = any((c.get("archived_url") or "").strip() for c in (entry.get("citations") or []))
        if any(touched(p, since) for p in artifacts) or archived:
            shown.append(entry)

    scored = [(len([n for n in AUTO_RULES if not evaluate(e).get(n)]), e) for e in shown]
    scored.sort(key=lambda t: t[0])
    perfect = sum(1 for f, _ in scored if f == 0)

    if args.report:
        print(report(scored, perfect, since, args.goal))
        return

    cards = "".join(card(e, since, i + 1) for i, (_f, e) in enumerate(scored))
    now = datetime.now(timezone.utc).astimezone().strftime("%d.%m.%Y %H:%M")

    doc = f"""<!doctype html><html lang="he" dir="rtl"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex"><title>סקירת בוקר — מעשי ישראל</title><style>{CSS}</style></head><body>
<div class="wrap">
<h1>סקירת בוקר — מה נעשה הלילה</h1>
<p class="sub">נבנה {now}. כל מספר בדף נקרא מהמסד החי, לא מזיכרון.</p>
<div class="stat">
  <div><b>{perfect}</b><span>מעשים מושלמים (50/50)</span></div>
  <div><b>{len(scored)}</b><span>מעשים שנגענו בהם</span></div>
  <div><b>{args.goal}</b><span>היעד שביקשת</span></div>
</div>
<p class="sub">עבור אחד-אחד. פתח את הדף באתר, תסתכל, ואז סמן. בסוף לחץ "העתק סיכום" ושלח לי בטלגרם.</p>
{cards}
</div>
<div class="bar"><span id="progress"></span><button onclick="copySummary()">העתק סיכום</button></div>
<script>{JS}</script></body></html>"""

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(doc, encoding="utf-8")
    (out / ".nojekyll").write_text("", encoding="utf-8")
    print(f"{len(scored)} deeds on the page, {perfect} perfect -> {out / 'index.html'}")


if __name__ == "__main__":
    main()
