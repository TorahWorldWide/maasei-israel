#!/usr/bin/env python3
"""Build a standalone approval page for a canonical document.

Tomer approves the rewrite before it reaches the database, so the page has to
be readable without touching the site: the article as he will read it, in both
languages, plus the two things the reader never sees and the approver must —
the source under every infobox row, and the questions the writer left open.

Media follows the same rule. A caption stored in a field the page never draws
is dead text, and on 12.8 that is exactly how a real disclaimer stayed hidden
from the reader — so `image_provenance` and `video_provenance` are rendered
here, not merely stored: every image at thumbnail size with its caption under
it, and at full size with the long caption, the licence, and the blind
description (rule 149) that the caption had to be written against. Images and
video sit in separate areas, per rule 61.

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
.engine{background:rgba(15,35,77,.75);border:1px solid rgba(201,168,74,.35);border-inline-start:4px solid #c9a84a;border-radius:12px;padding:12px 16px;margin:18px 0 6px}
.engine h3{margin-top:.2em}
.engine p{color:#e8eefc;font-size:1.02rem;margin-bottom:.2em}
.foot{margin-top:40px;border-top:1px solid rgba(201,168,74,.2);padding-top:14px;font-size:.85rem;color:#9fb0d0}

/* --- media: gallery, lightbox, video (rule 61 keeps the two apart) --- */
.gal{display:grid;grid-template-columns:repeat(auto-fill,minmax(208px,1fr));gap:14px;margin:0 0 22px}
.fig{background:rgba(15,35,77,.6);border:1px solid rgba(201,168,74,.15);border-radius:12px;
     overflow:hidden;display:flex;flex-direction:column}
.fig img{width:100%;height:150px;object-fit:cover;display:block;cursor:zoom-in;background:#08122a}
.fig.lead{grid-column:1/-1}
.fig.lead img{height:auto;max-height:430px;object-fit:contain;background:#08122a}
.fig .cap{padding:9px 12px 4px;font-size:.86rem;color:rgba(219,228,247,.92);flex:1;line-height:1.5}
.fig .meta{padding:0 12px 11px;font-size:.72rem;color:#8ea3c6;line-height:1.6}
.fig .meta a{color:#c9a84a;text-decoration:none;border-bottom:1px dotted rgba(201,168,74,.5)}
.lic{display:inline-block;font-size:.68rem;letter-spacing:.03em;border:1px solid rgba(201,168,74,.45);
     color:#e6c66e;border-radius:999px;padding:1px 8px;margin-inline-end:6px}
.lic.rev{border-color:#d08a5a;color:#e8a97a}
.badge{display:inline-block;font-size:.68rem;background:rgba(201,168,74,.14);color:#e6c66e;
       border-radius:6px;padding:1px 7px;margin-inline-start:6px}
.lb{position:fixed;inset:0;background:rgba(4,10,24,.97);z-index:60;overflow-y:auto;padding:16px 16px 70px}
.lb .inner{max-width:860px;margin:0 auto}
.lb img{max-width:100%;max-height:62vh;object-fit:contain;display:block;margin:0 auto 16px;border-radius:8px}
.lb h4{color:#e6c66e;font-size:1.05rem;margin:0 0 .5em;font-weight:700;line-height:1.45}
.lb p{font-size:.95rem}
.lbbar{display:flex;justify-content:flex-end;gap:10px;margin-bottom:10px;position:sticky;top:0}
.blind{border-inline-start:3px solid #5b7bb5;padding-inline-start:12px;margin:14px 0 0;
       font-size:.85rem;color:#9fb0d0}
.blind b{color:#8fa8d8;display:block;margin-bottom:.35em;font-size:.78rem;letter-spacing:.04em;
         text-transform:uppercase}
.provrow{font-size:.82rem;color:#9fb0d0;margin:3px 0}
.provrow b{color:#c9a84a;font-weight:600}
.vidwrap{background:rgba(15,35,77,.6);border:1px solid rgba(201,168,74,.15);border-radius:12px;
         overflow:hidden;margin:0 0 16px}
.vidwrap video{width:100%;display:block;background:#08122a;max-height:460px}
.vidwrap .cap{padding:10px 14px 4px;font-size:.9rem;color:rgba(219,228,247,.92)}
.vidwrap .meta{padding:0 14px 12px;font-size:.75rem;color:#8ea3c6;line-height:1.65}
.warn{border-inline-start:3px solid #d08a5a;padding-inline-start:12px;margin:10px 0 0;
      font-size:.82rem;color:#e0b394}
"""

JS = """
var T = {
  credit:      {he:'קרדיט', en:'Credit'},
  photographer:{he:'צלם', en:'Photographer'},
  when:        {he:'צולם', en:'Shot'},
  published:   {he:'פורסם ב', en:'Published in'},
  license:     {he:'רישיון', en:'Licence'},
  anchor:      {he:'עוגן בטקסט (58)', en:'Anchor in the text (58)'},
  blind:       {he:'תיאור עיוור — כלל 149',
                en:'Blind description — rule 149'},
  source:      {he:'לעמוד המקור', en:'Source page'},
  archive:     {he:'לצילום בארכיון (136)', en:'Archived snapshot (136)'},
  close:       {he:'סגירה', en:'Close'}
};
function L(k){ var l = document.documentElement.lang; return (T[k]||{})[l] || (T[k]||{}).en || k; }

function setLang(l){
  document.documentElement.lang = l;
  document.documentElement.dir  = (l==='he') ? 'rtl' : 'ltr';
  document.querySelectorAll('[data-l]').forEach(function(e){
    e.classList.toggle('hide', e.getAttribute('data-l') !== l);
  });
  document.getElementById('bhe').classList.toggle('on', l==='he');
  document.getElementById('ben').classList.toggle('on', l==='en');
  var c = document.getElementById('lbclose'); if(c) c.textContent = L('close');
  if(window._lbi !== null && window._lbi !== undefined) drawLb();
}

/* An image opens large with the long caption, the licence and the blind
   description beside it — the three things the approver has to weigh and the
   reader never sees. The source page stays one click away from both sizes. */
window._lbi = null;
function openLb(i){
  window._lbi = i; drawLb();
  document.getElementById('lb').classList.remove('hide');
  document.body.style.overflow = 'hidden';
}
function closeLb(){
  document.getElementById('lb').classList.add('hide');
  document.body.style.overflow = ''; window._lbi = null;
}
function drawLb(){
  var m = MEDIA[window._lbi]; if(!m) return;
  var he = document.documentElement.lang === 'he';
  var head = he ? m.caption_he : (m.caption_en || m.caption_he);
  var body = he ? (m.caption_long_he || m.caption_he)
                : (m.caption_long_en || m.caption_en || m.caption_he);
  var rows = '';
  function row(k, v){ if(v) rows += '<div class="provrow"><b>' + L(k) + ':</b> ' + v + '</div>'; }
  row('credit',       he ? m.credit : (m.credit_en || m.credit));
  row('photographer', m.photographer);
  row('when',         he ? m.shot_when : (m.shot_when_en || m.shot_when));
  row('published',    m.published_in);
  row('license',      (he ? m.license_label_he : m.license_label_en)
                      + (m.license_note ? ' — ' + m.license_note : ''));
  row('anchor',       m.anchor);
  var seen = m.image_seen && m.image_seen.description;
  var blind = seen ? '<div class="blind"><b>' + L('blind') + '</b>' + seen + '</div>' : '';
  document.getElementById('lbin').innerHTML =
      '<img src="' + m.url + '" alt="">'
    + '<h4>' + head + '</h4><p>' + body + '</p>' + rows
    + '<p style="margin-top:12px"><a href="' + m.source_url + '" target="_blank" '
    + 'rel="noopener">' + L('source') + ' ↗</a>'
    + (m.archived_url ? ' · <a href="' + m.archived_url + '" target="_blank" rel="noopener">'
       + L('archive') + ' ↗</a>' : '')
    + '</p>' + blind;
}
document.addEventListener('keydown', function(e){ if(e.key === 'Escape') closeLb(); });
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


LICENSE_LABEL = {
    "public_domain": ("נחלת הכלל", "Public domain"),
    "cc": ("קריאייטיב קומונס", "Creative Commons"),
    "press": ("עיתונות", "Press"),
    "owner_permission": ("אישור בעלים", "Owner permission"),
    "under_review": ("בבדיקה", "Under review"),
}


def licence_pill(img, lang):
    """Rule 137 wants the exact CC variant visible, not the bare word 'cc'."""
    lic = img.get("license") or ""
    note = img.get("license_note") or ""
    if lic == "cc" and note.upper().startswith("CC"):
        text = note.split("—")[0].strip()
    else:
        text = LICENSE_LABEL.get(lic, (lic, lic))[0 if lang == "he" else 1]
    cls = "lic rev" if lic == "under_review" else "lic"
    return f'<span class="{cls}">{esc(text)}</span>'


def figure(img, idx, lead=False):
    def meta(lang):
        credit = img.get("credit") if lang == "he" else (img.get("credit_en") or img.get("credit"))
        when = img.get("shot_when") if lang == "he" else (img.get("shot_when_en") or img.get("shot_when"))
        src_label = "מקור ↗" if lang == "he" else "source ↗"
        bits = [licence_pill(img, lang), esc(credit)]
        if when:
            bits.append("· " + esc(when))
        bits.append(f'· <a href="{esc(img.get("source_url"))}" target="_blank" rel="noopener">{src_label}</a>')
        return " ".join(bits)

    cap = both(esc(img.get("caption_he")), esc(img.get("caption_en") or img.get("caption_he")))
    cls = "fig lead" if lead else "fig"
    return (f'<figure class="{cls}">'
            f'<img src="{esc(img.get("url"))}" loading="lazy" alt="" onclick="openLb({idx})">'
            f'<div class="cap">{cap}</div>'
            f'<div class="meta">{both(meta("he"), meta("en"))}</div>'
            f'</figure>')


def gallery(images):
    """Consecutive images sharing a `group` sit under one heading (rule 45);
    a `group: null` image stands alone with its own caption (rule 46)."""
    out, i = [], 0
    while i < len(images):
        g = images[i].get("group")
        block = [i]
        if g:
            while i + 1 < len(images) and images[i + 1].get("group") == g:
                i += 1
                block.append(i)
            ge = images[block[0]].get("group_en") or g
            out.append(both(f"<h3>{esc(g)}</h3>", f"<h3>{esc(ge)}</h3>"))
        figs = "".join(figure(images[n], n, lead=(n == 0)) for n in block)
        out.append(f'<div class="gal">{figs}</div>')
        i += 1
    return "".join(out)


def video_area(videos):
    """Rule 61: video lives in its own area, never mixed into the image grid."""
    out = []
    for v in videos:
        def meta(lang):
            rows = []
            ch = v.get("channel") if lang == "he" else (v.get("channel_en") or v.get("channel"))
            up = v.get("uploaded_at") if lang == "he" else (v.get("uploaded_at_en") or v.get("uploaded_at"))
            sub = v.get("subject") if lang == "he" else (v.get("subject_en") or v.get("subject"))
            filmed = v.get("filmed_at") if lang == "he" else (v.get("filmed_at_en") or v.get("filmed_at"))
            lab = ({"ch": "ערוץ", "up": "הועלה", "fi": "צולם", "su": "נושא", "src": "לעמוד המקור ↗"}
                   if lang == "he" else
                   {"ch": "Channel", "up": "Uploaded", "fi": "Filmed", "su": "Subject",
                    "src": "Source page ↗"})
            rows.append(licence_pill(v, lang) + esc(v.get("license_note") or ""))
            for key, val in (("ch", ch), ("up", up), ("fi", filmed), ("su", sub)):
                if val:
                    rows.append(f'<b style="color:#c9a84a">{lab[key]}:</b> {esc(val)}')
            rows.append(f'<a href="{esc(v.get("source_url"))}" target="_blank" rel="noopener">{lab["src"]}</a>')
            return "<br>".join(rows)

        badge = ('<span class="badge">סרטון-על · master</span>' if v.get("master") else "")
        cap = both(esc(v.get("caption_he")) + badge,
                   esc(v.get("caption_en") or v.get("caption_he")) + badge)
        longcap = both(paras(v.get("caption_long_he")), paras(v.get("caption_long_en")))
        warns = "".join(f'<div class="warn">{esc(v[k])}</div>'
                        for k in ("transcript_note", "site_note", "master_reason") if v.get(k))
        out.append(f'<div class="vidwrap">'
                   f'<video controls preload="metadata" src="{esc(v.get("url"))}"></video>'
                   f'<div class="cap">{cap}</div>'
                   f'<div class="meta">{both(meta("he"), meta("en"))}</div>'
                   f'</div>'
                   f'<div class="card">{longcap}{warns}</div>')
    return "".join(out)


def media_audit(audit, images, videos):
    """What the approver has to weigh and the reader never sees: why this image
    leads, what was dropped and on what rule, and where the video falls short."""
    lic = {}
    for im in images:
        lic[im.get("license")] = lic.get(im.get("license"), 0) + 1
    breakdown = " · ".join(f'{LICENSE_LABEL.get(k, (k, k))[0]}: {n}' for k, n in sorted(lic.items()))
    rows = [f'<div class="provrow"><b>מאזן:</b> {len(images)} תמונות · '
            f'{len(videos)} סרטונים · {esc(breakdown)}</div>']
    if audit.get("lead_image_basis"):
        rows.append(f'<div class="provrow"><b>בסיס התמונה המובילה:</b> '
                    f'{esc(audit["lead_image_basis"])}</div>')
    for key in ("lead_image_note", "text_image_scans_note", "images_note", "video_note",
                "archive_note"):
        if audit.get(key):
            rows.append(f'<p class="note">{esc(audit[key])}</p>')
    lc = audit.get("link_check") or {}
    if lc.get("method"):
        rows.append(f'<p class="note"><b style="color:#c9a84a">כלל {esc(str(lc.get("rule")))} · '
                    f'{esc(lc.get("result"))}:</b> {esc(lc["method"])}</p>')
    dropped = audit.get("images_dropped") or []
    if dropped:
        rows.append(f'<h3>תמונות שיצאו ({len(dropped)})</h3>')
        for d in dropped:
            name = (d.get("url") or "").rsplit("/", 1)[-1]
            rows.append(f'<div class="q"><b>{esc(name)}</b>'
                        f'<div class="note">{esc(d.get("reason"))}</div></div>')
    return ('<h3>ביקורת מדיה · media audit</h3>'
            f'<div class="card">{"".join(rows)}</div>')


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

    if d.get("engine_sentence"):
        parts.append('<div class="engine">' + both(
            '<h3>משפט המנוע</h3>' + paras(d.get("engine_sentence")),
            '<h3>Engine sentence</h3>' + paras(d.get("engine_sentence_en"))) + '</div>')

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

    images = d.get("image_provenance") or []
    videos = d.get("video_provenance") or []
    if images:
        parts.append(both(f'<h3>תמונות ({len(images)})</h3>',
                          f'<h3>Images ({len(images)})</h3>'))
        parts.append(gallery(images))
    if videos:
        parts.append(both(f'<h3>סרטון ({len(videos)})</h3>',
                          f'<h3>Video ({len(videos)})</h3>'))
        parts.append(video_area(videos))

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

    if images or videos:
        parts.append(media_audit(d.get("audit") or {}, images, videos))

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

    # The lightbox writes these through innerHTML, so they are escaped here rather
    # than trusted; `</` is broken up so a stray tag inside a caption cannot end
    # the script block.
    def clean(img):
        out = {}
        for k, v in img.items():
            if isinstance(v, str):
                out[k] = esc(v)
            elif k == "image_seen" and isinstance(v, dict):
                out[k] = {kk: esc(vv) if isinstance(vv, str) else vv for kk, vv in v.items()}
        label = LICENSE_LABEL.get(img.get("license"), (img.get("license"), img.get("license")))
        out["license_label_he"], out["license_label_en"] = esc(label[0]), esc(label[1])
        return out

    media_json = json.dumps([clean(i) for i in images], ensure_ascii=False).replace("</", "<\\/")
    lightbox = ('<div id="lb" class="lb hide"><div class="inner"><div class="lbbar">'
                '<button id="lbclose" class="btn" onclick="closeLb()">סגירה</button></div>'
                '<div id="lbin"></div></div></div>') if images else ""

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    parts.append(f'<div class="foot">טיוטה לאישור — לא פורסמה לאתר · built {stamp}<br>'
                 f'<a href="https://maasei-israel.vercel.app">maasei-israel.vercel.app</a></div>')

    doc = (f'<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8">'
           f'<meta name="viewport" content="width=device-width,initial-scale=1">'
           f'<title>{esc(d["title"])} — טיוטה לאישור</title><style>{CSS}</style></head><body>'
           f'<div class="bar"><button id="bhe" class="btn on" onclick="setLang(\'he\')">עברית</button>'
           f'<button id="ben" class="btn" onclick="setLang(\'en\')">English</button>'
           f'<span class="tag">טיוטה לאישור · draft for approval</span></div>'
           f'<div class="wrap">{"".join(parts)}</div>{lightbox}'
           f'<script>var MEDIA = {media_json};\n{JS}</script></body></html>')

    out = Path(args.out)
    out.write_text(doc)
    print(f"{out}: {len(doc):,} bytes · {len(d.get('sections') or [])} sections · "
          f"{len(images)} images · {len(videos)} videos")


if __name__ == "__main__":
    main()
