#!/usr/bin/env python3
"""Build the standalone before/after review site for a standard-pass batch.

  python3 scripts/build_compare_site.py \
      --before docs/enrichment/backups/pre-standard-pass-<stamp>.json \
      --out /home/ubuntu/maasei-compare

"before" is the backup apply_standard_pass.py writes; "after" is read live from
the database, so the page always shows what is actually published.
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_claims import run_sql  # noqa: E402
from deed_standard import AUTO_RULES, evaluate  # noqa: E402


def domain(url):
    try:
        host = urlparse(url).netloc.lower()
        return host[4:] if host.startswith("www.") else host
    except Exception:
        return ""


def is_video(url):
    return "youtube.com" in url or "youtu.be" in url or "vimeo.com" in url


PROSE_FIELDS = ["description", "origin_story", "act", "ripple", "aftermath", "recognition"]


def metrics(row):
    cits = row.get("citations") or []
    media = row.get("media_urls") or []
    return {
        "citations": len(cits),
        "domains": len({domain(c.get("source_url", "")) for c in cits if c.get("source_url")}),
        "images": len([u for u in media if not is_video(u)]),
        "people": len(row.get("people") or []),
        "videos": len(((row.get("audit") or {}).get("videos")) or []),
        "location": 1 if row.get("location") else 0,
        "honors": len(row.get("honors") or []),
        "chars": sum(len(row.get(f) or "") for f in PROSE_FIELDS),
    }


def build_payload(before_rows, after_rows):
    before = {r["id"]: r for r in before_rows}
    deeds = []
    for row in after_rows:
        prev = before.get(row["id"], {})
        changed = [
            f for f in row
            if json.dumps(row[f], ensure_ascii=False, sort_keys=True, default=str)
            != json.dumps(prev.get(f), ensure_ascii=False, sort_keys=True, default=str)
        ]
        # The page now carries deeds from more than one generation of the pass.
        # Without the score, an early deed and a finished one look alike.
        after_result = evaluate(row)
        deeds.append({
            "id": row["id"],
            "title": row.get("title") or "",
            "year": row.get("year"),
            "before": prev,
            "after": row,
            "changed": changed,
            "m_before": dict(metrics(prev), std=sum(
                1 for n in AUTO_RULES if evaluate(prev).get(n))),
            "m_after": dict(metrics(row), std=sum(
                1 for n in AUTO_RULES if after_result.get(n))),
            "std_total": len(AUTO_RULES),
            "failing": [n for n in AUTO_RULES if not after_result.get(n)],
        })
    deeds.sort(key=lambda d: d["title"])
    return {"built": datetime.now(timezone.utc).isoformat(timespec="seconds"), "deeds": deeds}


HTML = """<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>מעשי ישראל — לפני ואחרי</title>
<style>
:root{
  --bg:#f5f5f7; --card:#fff; --ink:#1d1d1f; --dim:#6e6e73; --line:#e3e3e6;
  --before:#a1a1a6; --after:#0071e3; --good:#1d8a4e; --warn:#b25000;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font:16px/1.55 -apple-system,BlinkMacSystemFont,"SF Pro Text","Segoe UI",Arial,sans-serif;
  -webkit-font-smoothing:antialiased}
header{position:sticky;top:0;z-index:20;background:rgba(245,245,247,.86);
  backdrop-filter:saturate(180%) blur(20px);border-bottom:1px solid var(--line)}
.wrap{max-width:1180px;margin:0 auto;padding:0 18px}
h1{font-size:20px;font-weight:600;margin:14px 0 10px;letter-spacing:-.01em}
h1 small{font-weight:400;color:var(--dim);font-size:13px;margin-inline-start:8px}
nav{display:flex;gap:8px;overflow-x:auto;padding-bottom:12px;scrollbar-width:none}
nav::-webkit-scrollbar{display:none}
nav button{white-space:nowrap;border:1px solid var(--line);background:var(--card);color:var(--ink);
  border-radius:999px;padding:7px 14px;font-size:13.5px;cursor:pointer;transition:.15s}
nav button:hover{border-color:#c9c9cf}
nav button.on{background:var(--ink);color:#fff;border-color:var(--ink)}
main{max-width:1180px;margin:0 auto;padding:20px 18px 60px}
.scoreboard{display:grid;grid-template-columns:repeat(auto-fit,minmax(118px,1fr));gap:10px;margin-bottom:22px}
.tile{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:12px 14px}
.tile .lbl{font-size:11.5px;color:var(--dim);letter-spacing:.02em}
.tile .val{font-size:22px;font-weight:600;margin-top:4px;display:flex;align-items:baseline;gap:7px}
.tile .was{font-size:13px;color:var(--before);font-weight:400}
.tile .up{font-size:12px;color:var(--good);font-weight:500}
.modes{display:flex;gap:6px;margin:0 0 16px}
.modes button{flex:0 0 auto;border:1px solid var(--line);background:var(--card);border-radius:9px;
  padding:6px 13px;font-size:13px;cursor:pointer;color:var(--dim)}
.modes button.on{background:var(--ink);color:#fff;border-color:var(--ink)}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:16px;align-items:start}
.cols.single{grid-template-columns:1fr}
.pane{background:var(--card);border:1px solid var(--line);border-radius:18px;overflow:hidden}
.pane>h2{margin:0;padding:12px 18px;font-size:13px;font-weight:600;letter-spacing:.03em;
  border-bottom:1px solid var(--line);display:flex;justify-content:space-between;align-items:center}
.pane.b>h2{color:var(--before)} .pane.a>h2{color:var(--after)}
.pane>h2 em{font-style:normal;font-size:11.5px;color:var(--dim);font-weight:400}
.body{padding:6px 18px 18px}
section{padding:14px 0;border-bottom:1px solid #f0f0f2}
section:last-child{border-bottom:0}
.k{font-size:11.5px;color:var(--dim);letter-spacing:.03em;margin-bottom:6px;
  display:flex;align-items:center;gap:7px}
.chg{background:#e8f2ff;color:var(--after);border-radius:5px;padding:1px 6px;font-size:10.5px}
.txt{font-size:15px;white-space:pre-wrap}
.empty{color:#c4c4c8;font-size:14px;font-style:italic}
.imgs{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:12px}
figure{margin:0}
figure img{width:100%;height:104px;object-fit:cover;border-radius:10px;background:#eaeaec;display:block;
  border:1px solid var(--line)}
figcaption{font-size:11.5px;color:var(--dim);margin-top:5px;line-height:1.45}
figcaption .cred{color:#a1a1a6;font-size:10.5px;display:block;margin-top:2px}
figcaption .flag{color:var(--warn);display:block;margin-top:2px}
ol.src{margin:0;padding-inline-start:20px;font-size:13.5px}
ol.src li{margin-bottom:11px}
ol.src .lbl{font-weight:500}
ol.src .q{color:var(--dim);display:block;margin-top:2px}
ol.src .meta{color:#a1a1a6;font-size:11.5px;display:block;margin-top:2px}
ul.honors{margin:0;padding-inline-start:20px;font-size:14px}
ul.honors li{margin-bottom:6px}
a{color:var(--after);text-decoration:none}
a:hover{text-decoration:underline}
.vid{border:1px solid var(--line);border-radius:12px;padding:10px 12px;margin-bottom:10px}
.vid .t{font-size:14px;font-weight:500}
.vid .c{font-size:11.5px;color:var(--dim);margin-top:3px}
.pills{display:flex;flex-wrap:wrap;gap:6px}
.pill{background:#f2f2f4;border-radius:7px;padding:3px 9px;font-size:12.5px;color:#3a3a3c}
.decide{background:#fff;border:1px solid var(--line);border-left:3px solid var(--warn);
  border-radius:14px;padding:16px 18px;margin-bottom:14px}
.decide h3{margin:0 0 6px;font-size:15px}
.decide p{margin:0 0 8px;font-size:14px;color:#3a3a3c}
.decide .opts{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:10px}
.decide .opts img{width:100%;height:150px;object-fit:contain;background:#f2f2f4;border-radius:10px}
@media(max-width:820px){
  .cols{grid-template-columns:1fr}
  .decide .opts{grid-template-columns:1fr}
}
</style>
</head>
<body>
<header><div class="wrap">
  <h1>מעשי ישראל — לפני ואחרי <small id="stamp"></small></h1>
  <nav id="tabs"></nav>
</div></header>
<main>
  <div class="scoreboard" id="score"></div>
  <div class="modes">
    <button data-mode="both" class="on">זה לצד זה</button>
    <button data-mode="before">רק לפני</button>
    <button data-mode="after">רק אחרי</button>
  </div>
  <div class="cols" id="cols"></div>
  <div id="decisions" style="margin-top:34px"></div>
</main>
<script id="data" type="application/json">__DATA__</script>
<script id="decisions-data" type="application/json">__DECISIONS__</script>
<script>
const DATA = JSON.parse(document.getElementById('data').textContent);
const DECISIONS = JSON.parse(document.getElementById('decisions-data').textContent);
let cur = 0, mode = 'both';
document.getElementById('stamp').textContent = 'עודכן ' + DATA.built.replace('T',' ').replace('+00:00',' UTC');

const esc = s => (s==null?'':String(s)).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const host = u => { try { return new URL(u).hostname.replace(/^www\\./,''); } catch(e){ return ''; } };

function tabs(){
  document.getElementById('tabs').innerHTML = DATA.deeds.map((d,i)=>
    `<button class="${i===cur?'on':''}" data-i="${i}">${esc(d.title.slice(0,42))}</button>`).join('');
}
function score(){
  const d = DATA.deeds[cur];
  const rows = [['מקורות','citations'],['דומיינים','domains'],['תמונות','images'],
                ['סרטונים','videos'],['אנשים','people'],['מיקום','location'],
                ['כבוד','honors'],['תווים','chars']];
  const sb = d.m_before.std||0, sa = d.m_after.std||0, st = d.std_total;
  const stdTile = `<div class="tile"><div class="lbl">תקן${d.failing.length?
      ` · נכשל ב-${d.failing.join(', ')}`:' · עובר הכל'}</div>
    <div class="val" style="color:${sa===st?'var(--good)':'var(--warn)'}">${sa}/${st}
    ${sa>sb?`<span class="up">+${sa-sb}</span>`:''}<span class="was">היה ${sb}</span></div></div>`;
  document.getElementById('score').innerHTML = stdTile + rows.map(([lbl,k])=>{
    const b = d.m_before[k]||0, a = d.m_after[k]||0;
    const up = a>b ? `<span class="up">+${a-b}</span>` : '';
    return `<div class="tile"><div class="lbl">${lbl}</div>
      <div class="val">${a}${up}<span class="was">היה ${b}</span></div></div>`;
  }).join('');
}
function sect(key, label, changed, inner){
  const flag = changed.includes(key) ? '<span class="chg">שונה</span>' : '';
  return `<section><div class="k">${label}${flag}</div>${inner}</section>`;
}
function txt(v){ return v ? `<div class="txt">${esc(v)}</div>` : `<div class="empty">— ריק —</div>`; }

function pane(d, side){
  const r = side==='after' ? d.after : d.before;
  const ch = side==='after' ? d.changed : [];
  const prov = ((r.audit||{}).image_provenance)||[];
  const provOf = u => prov.find(p=>p.url===u) || null;
  const isVid = u => /youtube\\.com|youtu\\.be|vimeo\\.com/.test(u);
  const imgs = (r.media_urls||[]).filter(u=>!isVid(u));
  const mediaVids = (r.media_urls||[]).filter(isVid);
  const imgHtml = imgs.length ? `<div class="imgs">` + imgs.map(u=>{
      const p = provOf(u);
      return `<figure><a href="${esc(u)}" target="_blank"><img loading="lazy" src="${esc(u)}"></a>
        <figcaption>${p&&p.caption_he?esc(p.caption_he):'<span class="empty">ללא כיתוב</span>'}
        ${p&&p.credit?`<span class="cred">${esc(p.credit)}${p.shot_when?' · '+esc(p.shot_when):''}</span>`:''}
        ${p&&p.warning?`<span class="flag">⚠ ${esc(p.warning)}</span>`:''}</figcaption></figure>`;
    }).join('') + `</div>` : `<div class="empty">— אין תמונות —</div>`;

  const cits = (r.citations||[]);
  const citHtml = cits.length ? `<ol class="src">` + cits.map(c=>
      `<li><span class="lbl">${esc(c.source_label||host(c.source_url))}</span>
       <a href="${esc(c.source_url)}" target="_blank">↗</a>
       ${c.quote?`<span class="q">"${esc(c.quote)}"</span>`:''}
       <span class="meta">${esc(host(c.source_url))}${c.published?' · '+esc(c.published):''}${c.locator?' · '+esc(c.locator):''}</span></li>`
    ).join('') + `</ol>` : `<div class="empty">— אין מקורות —</div>`;

  const meta = (((r.audit||{}).videos)||[]);
  const ytid = u => (u.match(/(?:v=|youtu\\.be\\/|embed\\/)([A-Za-z0-9_-]{11})/)||[])[1]||'';
  const vidHtml = mediaVids.length ? mediaVids.map(u=>{
      const v = meta.find(m=>ytid(m.url)===ytid(u)) || {};
      const id = ytid(u);
      return `<div class="vid"><div style="display:flex;gap:11px;align-items:flex-start">
       ${id?`<a href="${esc(u)}" target="_blank"><img src="https://i.ytimg.com/vi/${id}/mqdefault.jpg"
          style="width:112px;height:63px;object-fit:cover;border-radius:7px;display:block"></a>`:''}
       <div style="flex:1;min-width:0">
        <div class="t"><a href="${esc(u)}" target="_blank">${esc(v.title||u)}</a></div>
        <div class="c">${esc(v.channel||'')}${v.transcript?' · תמליל: '+esc(v.transcript):
          '<span style="color:#b25000"> · ללא כיתוב מקור</span>'}</div>
       </div></div></div>`;
    }).join('') : `<div class="empty">— אין סרטונים —</div>`;

  const loc = r.location;
  const locHtml = loc ? `<div class="txt">${esc([loc.city,loc.country].filter(Boolean).join(', '))}
      <span class="empty" style="font-style:normal;color:#a1a1a6">· דיוק: ${esc(loc.precision||'')}</span></div>` :
      `<div class="empty">— אין מיקום —</div>`;

  const ppl = (r.people||[]);
  const pplHtml = ppl.length ? `<div class="pills">` + ppl.map(p=>
      `<span class="pill">${esc(p.name_he||p.name_en)}${p.role_he?' — '+esc(p.role_he):''}</span>`).join('') + `</div>`
    : `<div class="empty">— לא מזוהים —</div>`;

  const tags = [].concat(r.deed_type||[], r.beneficiary||[], r.actor_type?[r.actor_type]:[]);
  const tagHtml = tags.length ? `<div class="pills">`+tags.map(t=>`<span class="pill">${esc(t)}</span>`).join('')+`</div>`
    : `<div class="empty">— ריק —</div>`;

  const honors = (r.honors||[]);
  const honorsHtml = honors.length ? `<ul class="honors">` + honors.map(h=>
      `<li>${h.source?`<a href="${esc(h.source)}" target="_blank">${esc(h.what)}</a>`:esc(h.what)}${h.year?` <span class="empty" style="font-style:normal;color:#a1a1a6">· ${esc(String(h.year))}</span>`:''}</li>`
    ).join('') + `</ul>` : `<div class="empty">— אין —</div>`;

  const label = side==='after' ? 'אחרי' : 'לפני';
  const sub = side==='after' ? 'המצב החי באתר' : 'כפי שהיה לפני המעבר';
  return `<div class="pane ${side==='after'?'a':'b'}">
    <h2>${label}<em>${sub}</em></h2>
    <div class="body">
      ${sect('title','כותרת',ch,txt(r.title))}
      ${sect('description','תיאור',ch,txt(r.description))}
      ${sect('origin_story','איך זה התחיל',ch,txt(r.origin_story))}
      ${sect('act','מה נעשה',ch,txt(r.act))}
      ${sect('ripple','ההשפעה',ch,txt(r.ripple))}
      ${sect('aftermath','מה קרה אחר כך',ch,txt(r.aftermath))}
      ${sect('recognition','מה קיבלו על זה',ch,txt(r.recognition))}
      ${sect('honors','כבוד על שמם ('+(r.honors||[]).length+')',ch,honorsHtml)}
      ${sect("media_urls","תמונות ("+imgs.length+")",ch,imgHtml)}
      ${sect("audit","סרטונים ("+mediaVids.length+")",ch,vidHtml)}
      ${sect('citations','מקורות ('+cits.length+')',ch,citHtml)}
      ${sect('location','מיקום',ch,locHtml)}
      ${sect('people','אנשים',ch,pplHtml)}
      ${sect('deed_type','סיווג',ch,tagHtml)}
    </div></div>`;
}

function render(){
  tabs(); score();
  const d = DATA.deeds[cur];
  const cols = document.getElementById('cols');
  cols.className = 'cols' + (mode==='both' ? '' : ' single');
  cols.innerHTML = mode==='both' ? pane(d,'before')+pane(d,'after')
                 : mode==='before' ? pane(d,'before') : pane(d,'after');
  const mine = DECISIONS.filter(x=>x.deed_id===d.id);
  document.getElementById('decisions').innerHTML = mine.length ? '<h1 style="font-size:17px">החלטות שממתינות לך</h1>' +
    mine.map(x=>`<div class="decide"><h3>${esc(x.title)}</h3><p>${esc(x.body)}</p>
      ${x.options?`<div class="opts">${x.options.map(o=>
        `<div>${o.img?`<img src="${esc(o.img)}">`:''}<div class="k" style="margin-top:6px">${esc(o.label)}</div>
         <div class="txt" style="font-size:13.5px">${esc(o.text||'')}</div></div>`).join('')}</div>`:''}
      </div>`).join('') : '';
}
document.getElementById('tabs').addEventListener('click',e=>{
  const b=e.target.closest('button'); if(!b)return; cur=+b.dataset.i; render(); window.scrollTo({top:0,behavior:'smooth'});
});
document.querySelector('.modes').addEventListener('click',e=>{
  const b=e.target.closest('button'); if(!b)return;
  mode=b.dataset.mode;
  document.querySelectorAll('.modes button').forEach(x=>x.classList.toggle('on',x===b));
  render();
});
render();
</script>
</body></html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", required=True)
    ap.add_argument("--decisions", default=None, help="JSON file with pending decisions")
    ap.add_argument("--overlay", action="append", default=[],
                    help="JSON of proposed field changes, merged into the after side "
                         "without touching the live row. Repeatable.")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    before_rows = json.loads(Path(args.before).read_text(encoding="utf-8"))
    ids = ",".join("'" + r["id"] + "'" for r in before_rows)
    after_rows = run_sql(f"select * from entries where id in ({ids})")

    for path in args.overlay:
        patch = json.loads(Path(path).read_text(encoding="utf-8"))
        target = next(r for r in after_rows if r["id"] == patch["id"])
        for field in ("description", "act", "ripple",
                      "description_en", "act_en", "ripple_en"):
            if patch.get(field):
                target[field] = patch[field]
        if patch.get("new_citations"):
            target["citations"] = (target.get("citations") or []) + patch["new_citations"]

    payload = build_payload(before_rows, after_rows)
    decisions = json.loads(Path(args.decisions).read_text(encoding="utf-8")) if args.decisions else []

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    html = (HTML
            .replace("__DATA__", json.dumps(payload, ensure_ascii=False, default=str))
            .replace("__DECISIONS__", json.dumps(decisions, ensure_ascii=False)))
    (out / "index.html").write_text(html, encoding="utf-8")
    (out / ".nojekyll").write_text("", encoding="utf-8")
    print(f"wrote {out/'index.html'}  ({len(html)//1024} KB, {len(payload['deeds'])} deeds)")


if __name__ == "__main__":
    main()
