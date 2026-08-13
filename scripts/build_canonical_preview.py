#!/usr/bin/env python3
"""Build a standalone approval page for a canonical document.

Tomer approves the rewrite before it reaches the database, so the page has to
be readable without touching the site: the article as he will read it, in both
languages, plus the two things the reader never sees and the approver must —
the source under every infobox row, and the questions the writer left open.

  python3 scripts/build_canonical_preview.py \
      docs/enrichment/canonical/lamarr/v2/canonical.json \
      --out /home/ubuntu/maasei-review/lamarr-v2.html
"""
import argparse
import html
import json
from datetime import datetime, timezone
from pathlib import Path

CSS = """
*{box-sizing:border-box}
body{margin:0;background:#0a1834;color:#dbe4f7;font-family:system-ui,'Segoe UI',Arial,sans-serif;line-height:1.75}
.wrap{max-width:760px;margin:0 auto;padding:24px 18px 80px}
h1{font-size:1.65rem;line-height:1.35;color:#e6c66e;margin:.2em 0 .1em;font-weight:800}
h2{font-size:1.25rem;color:#e6c66e;margin:2em 0 .5em;font-weight:700}
h3{font-size:1rem;color:#c9a84a;margin:1.6em 0 .4em;letter-spacing:.04em;text-transform:uppercase}
p{margin:0 0 1em;color:rgba(219,228,247,.86)}
.bar{position:sticky;top:0;z-index:5;background:rgba(10,24,52,.96);border-bottom:1px solid rgba(201,168,74,.25);
     padding:10px 18px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.btn{border:1px solid rgba(201,168,74,.45);background:transparent;color:#e6c66e;border-radius:999px;
     padding:6px 16px;font-size:.85rem;cursor:pointer}
.btn.on{background:#c9a84a;color:#0a1834;font-weight:700}
.tag{font-size:.75rem;color:#9fb0d0}
.lead p:first-child{font-size:1.06rem;color:#e8eefc}
.card{background:rgba(15,35,77,.6);border:1px solid rgba(201,168,74,.15);border-radius:12px;padding:14px 16px;margin:0 0 14px}
table{width:100%;border-collapse:collapse}
td{padding:9px 4px;border-bottom:1px solid rgba(201,168,74,.12);vertical-align:top;font-size:.93rem}
td.k{color:#c9a84a;white-space:nowrap;width:1%;padding-inline-end:14px;font-weight:600}
.src{display:block;margin-top:5px;font-size:.78rem;color:#8ea3c6}
.q{border-inline-start:3px solid #c9a84a;padding-inline-start:12px;margin:0 0 14px;font-size:.93rem}
.note{font-size:.82rem;color:#9fb0d0;margin-top:4px}
a{color:#e6c66e}
.hide{display:none}
.summary{background:rgba(201,168,74,.07);border:1px solid rgba(201,168,74,.2);border-radius:12px;padding:14px 16px;margin:18px 0 26px}
.foot{margin-top:40px;border-top:1px solid rgba(201,168,74,.2);padding-top:14px;font-size:.85rem;color:#9fb0d0}
"""

JS = """
function setLang(l){
  document.documentElement.lang = l;
  document.documentElement.dir  = (l==='he') ? 'rtl' : 'ltr';
  document.querySelectorAll('[data-l]').forEach(function(e){
    e.classList.toggle('hide', e.getAttribute('data-l') !== l);
  });
  document.getElementById('bhe').classList.toggle('on', l==='he');
  document.getElementById('ben').classList.toggle('on', l==='en');
}
"""


def esc(s):
    return html.escape(s or "")


def paras(text, cls=""):
    blocks = [p.strip() for p in (text or "").split("\n") if p.strip()]
    c = f' class="{cls}"' if cls else ""
    return "".join(f"<p{c}>{esc(p)}</p>" for p in blocks)


def both(he_html, en_html):
    return (f'<div data-l="he">{he_html}</div>'
            f'<div data-l="en" class="hide">{en_html}</div>')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    d = json.loads(Path(args.path).read_text())
    rows = (d.get("infobox") or {}).get("rows") or []
    parts = []

    parts.append(both(f"<h1>{esc(d['title'])}</h1>", f"<h1>{esc(d.get('title_en'))}</h1>"))
    parts.append(f'<p class="tag">{esc(d.get("canonical_type"))} · '
                 f'{len(d.get("sections") or [])} sections · {len(rows)} infobox rows · '
                 f'{len(d.get("honors") or [])} honors</p>')

    parts.append('<div class="summary">' + both(
        paras(d.get("summary_short")), paras(d.get("summary_short_en"))) + '</div>')

    if rows:
        def table(lang):
            out = ['<table>']
            for r in rows:
                k = r.get("label") if lang == "he" else (r.get("label_en") or r.get("label"))
                v = r.get("value") if lang == "he" else (r.get("value_en") or r.get("value"))
                out.append(f'<tr><td class="k">{esc(k)}</td><td>{esc(v)}'
                           f'<span class="src">{esc(r.get("source"))}</span></td></tr>')
            out.append('</table>')
            return "".join(out)
        parts.append(both(f'<h3>בקצרה</h3><div class="card">{table("he")}</div>',
                          f'<h3>At a glance</h3><div class="card">{table("en")}</div>'))

    for i, s in enumerate(d.get("sections") or []):
        cls = "lead" if i == 0 else ""
        he = (f"<h2>{esc(s.get('heading'))}</h2>" if s.get("heading") else "") + \
             f'<div class="{cls}">{paras(s.get("body"))}</div>'
        en = (f"<h2>{esc(s.get('heading_en'))}</h2>" if s.get("heading_en") else "") + \
             f'<div class="{cls}">{paras(s.get("body_en"))}</div>'
        parts.append(both(he, en))

    honors = d.get("honors") or []
    if honors:
        def hlist(lang):
            out = []
            for h in honors:
                name = h.get("name") if lang == "he" else (h.get("name_en") or h.get("name"))
                body = h.get("awarding_body") if lang == "he" else (h.get("awarding_body_en") or h.get("awarding_body"))
                note = h.get("note") if lang == "he" else (h.get("note_en") or h.get("note"))
                out.append(f'<div class="q"><b>{esc(name)}</b> · {esc(body)} · {esc(str(h.get("year") or ""))}'
                           f'<span class="src">{esc(h.get("quote"))}<br>'
                           f'<a href="{esc(h.get("source_url"))}">{esc(h.get("source_url"))}</a></span>'
                           + (f'<div class="note">{esc(note)}</div>' if note else "") + '</div>')
            return "".join(out)
        parts.append(both(f'<h3>הוקרות</h3>{hlist("he")}', f'<h3>Honors</h3>{hlist("en")}'))

    qs = d.get("writer_questions") or []
    if qs:
        items = []
        for q in qs:
            if isinstance(q, dict):
                text = q.get("question") or q.get("q") or json.dumps(q, ensure_ascii=False)
                why = q.get("why") or q.get("note") or ""
            else:
                text, why = str(q), ""
            items.append(f'<div class="q">{esc(text)}'
                         + (f'<div class="note">{esc(why)}</div>' if why else "") + '</div>')
        parts.append(f'<h3>שאלות שהכותב השאיר פתוחות · open questions ({len(qs)})</h3>'
                     + "".join(items))

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    parts.append(f'<div class="foot">טיוטה לאישור — לא פורסמה לאתר · built {stamp}<br>'
                 f'<a href="https://maasei-israel.vercel.app">maasei-israel.vercel.app</a></div>')

    doc = (f'<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8">'
           f'<meta name="viewport" content="width=device-width,initial-scale=1">'
           f'<title>{esc(d["title"])} — טיוטה לאישור</title><style>{CSS}</style></head><body>'
           f'<div class="bar"><button id="bhe" class="btn on" onclick="setLang(\'he\')">עברית</button>'
           f'<button id="ben" class="btn" onclick="setLang(\'en\')">English</button>'
           f'<span class="tag">טיוטה לאישור · draft for approval</span></div>'
           f'<div class="wrap">{"".join(parts)}</div><script>{JS}</script></body></html>')

    out = Path(args.out)
    out.write_text(doc)
    print(f"{out}: {len(doc):,} bytes · {len(d.get('sections') or [])} sections")


if __name__ == "__main__":
    main()
