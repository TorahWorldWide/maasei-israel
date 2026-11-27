"""List the deeds that are below the "finished page" bar and so are hidden from the site.

27.11.2026, Tomer's rule: only finished, full pages may be on the public site.
The bar lives in src/data/ready-bar.json and is applied at runtime by src/lib/ready.ts
(catalog, reel, deed pages, museum pages). This script applies the SAME bar and writes
the list, so unfinished deeds can be finished one by one and then appear by themselves.

    python scripts/not_ready_report.py [--out C:/Users/tomer/Shaked-Work/maasei-not-ready.md]

Reads the old catalog from Supabase (public anon key in .env.local, read only) and the
museum pages from data/museum/. Keep countSentences() in step with src/lib/ready.ts.
"""
import argparse
import datetime as dt
import difflib
import json
import re
import unicodedata
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BAR = json.loads((ROOT / "src" / "data" / "ready-bar.json").read_text(encoding="utf8"))
HIDDEN = {"55c7771e-3d56-4e79-a08b-70f102c2a5fe", "b4a5042d-635a-4704-adcf-0ea35193db13"}  # HIDDEN_ENTRY_IDS in src/lib/data.ts (removed on purpose)
SITE = "https://maasei-israel.vercel.app"
# words that name a kind of deed, not a person or thing (a match on these alone is not the same deed)
GENERIC = {"israeli", "israelis", "israel", "rescue", "earthquake", "hospital", "field", "water", "solar",
           "team", "nobel", "prize", "medical", "doctors", "help", "first", "world", "founding", "founder",
           "children", "refugees", "volunteers", "discovery", "pumps", "africa"}


def count_sentences(text):
    if not text:
        return 0
    return len([s for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) >= 15])


def entry_sentences(e):
    parts = [e.get(k) for k in ("description", "origin_story", "act", "ripple", "aftermath", "recognition")]
    parts += [s.get("body") for s in (e.get("sections") or [])]
    return sum(count_sentences(p) for p in parts)


def museum_ready(doc, has_en):
    c = doc.get("check") or {}
    confirmed = int((c.get("counts") or {}).get("confirmed") or 0)
    passed = c.get("passed") is True or str(c.get("passed")).lower() == "true"
    return passed and confirmed >= BAR["museum_min_confirmed"] and (has_en or not BAR["museum_needs_english"]), confirmed, passed


def env():
    out = {}
    for line in (ROOT / ".env.local").read_text(encoding="utf8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip().strip('"')
    return out


def catalog():
    e = env()
    url, key = e["NEXT_PUBLIC_SUPABASE_URL"], e["NEXT_PUBLIC_SUPABASE_ANON_KEY"]
    req = urllib.request.Request(
        f"{url}/rest/v1/entries?select=*&status=eq.approved&order=created_at.desc",
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf8"))


def norm(t):
    return re.sub(r"[^\w]+", " ", t or "").strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/Users/tomer/Shaked-Work/maasei-not-ready.md")
    ap.add_argument("--museum-dir", default=str(ROOT / "data" / "museum"))
    a = ap.parse_args()
    mdir = Path(a.museum_dir)

    museum, museum_bad = {}, []
    reel = {x["slug"] for x in json.loads((mdir / "reel.json").read_text(encoding="utf8"))["reel"]}
    for f in sorted(mdir.glob("*.json")):
        if f.name.count(".") > 1 or f.name == "reel.json":
            continue
        doc = json.loads(f.read_text(encoding="utf8"))
        if doc.get("schema") != "maasei-museum/1":
            continue
        slug = f.stem
        has_en = (mdir / f"{slug}.en.json").exists()
        ok, confirmed, passed = museum_ready(doc, has_en)
        museum[slug] = doc.get("deed") or doc.get("title") or slug
        if not ok:
            why = []
            if not passed:
                why.append("check not passed")
            if confirmed < BAR["museum_min_confirmed"]:
                why.append(f"{confirmed} confirmed sentences (needs {BAR['museum_min_confirmed']})")
            if BAR["museum_needs_english"] and not has_en:
                why.append(f"no English version ({slug}.en.json)")
            museum_bad.append((slug, museum[slug], confirmed, "; ".join(why), slug in reel))

    titles = {slug: norm(t) for slug, t in museum.items()}

    def twin(title, title_en):
        # 1) the Hebrew deed line is (nearly) the same as the museum page's
        n = norm(title)
        best = max(titles.items(), key=lambda kv: difflib.SequenceMatcher(None, n, kv[1]).ratio(), default=None)
        if best and difflib.SequenceMatcher(None, n, best[1]).ratio() >= 0.6:
            return best[0]
        # 2) the English title names the same people/things as the museum slug (2+ long slug words)
        plain = unicodedata.normalize("NFKD", (title_en or "").lower()).encode("ascii", "ignore").decode()
        words = set(re.findall(r"[a-z0-9]+", plain))
        def score(slug):
            hit = [w for w in slug.split("-") if len(w) >= 4 and w in words]
            return len(hit), len([w for w in hit if w not in GENERIC])
        hits = sorted(((*score(slug), slug) for slug in titles), reverse=True)
        if hits and (hits[0][0] >= 3 or hits[0][1] >= 2) and (len(hits) == 1 or hits[1][0] < hits[0][0]):
            return hits[0][2]
        return None

    entries = [e for e in catalog() if e["id"] not in HIDDEN]
    shown, with_twin, without_twin = [], [], []
    for e in entries:
        n = entry_sentences(e)
        if n >= BAR["catalog_min_sentences"]:
            shown.append(e)
            continue
        t = twin(e["title"], e.get("title_en"))
        (with_twin if t else without_twin).append((e, n, t))

    today = dt.date.today().strftime("%d.%m.%Y")
    L = [
        "# Maasei Israel: deeds not ready for the public site",
        "",
        f"Written {today} by `scripts/not_ready_report.py` (in `C:\\Users\\tomer\\maasei-israel`). Run it again to refresh this file.",
        "",
        "Tomer's rule (27.11.2026): only finished, full pages are on the public site. The bar, in",
        "`src/data/ready-bar.json`, is applied by the site itself (`src/lib/ready.ts`):",
        f"- an old-catalog deed needs **at least {BAR['catalog_min_sentences']} sentences** of text on its page;",
        f"- a museum page needs a **passed check with at least {BAR['museum_min_confirmed']} confirmed sentences**"
        + (" and its **English version**." if BAR["museum_needs_english"] else "."),
        "",
        "Nothing was deleted. A hidden deed is off the catalog and the reel, and its page answers 404;",
        "add `?draft=1` to its address to look at it. **A deed comes back by itself** once it passes the bar",
        "(after the deploy that carries the new text).",
        "",
        f"Now: catalog shows {len(shown)} of {len(entries)} old deeds; reel shows {len(reel) - sum(1 for m in museum_bad if m[4])} of {len(reel)} museum pages.",
        "",
        "## Order of work",
        "1. Section A first: the page is written and checked, only the English translation is missing",
        "   (`museum_line.py` english stage). Smallest step to publish.",
        "2. Section C: old deeds with no museum page (matched by name, so first check `data/museum/` for a page",
        "   under another name). Write a museum page with `scripts/museum/museum_line.py`",
        "   (no Wikipedia as a source). When it passes, add it to `data/museum/reel.json`.",
        "3. Section B needs no writing: the story is already public as a museum page in the reel.",
        "   The thin old card simply stays hidden.",
        "",
        f"## A. Museum pages below the bar ({len(museum_bad)})",
        "",
        "| slug | deed | confirmed | missing | in reel.json |",
        "|---|---|---|---|---|",
    ]
    for slug, deed, conf, why, in_reel in museum_bad:
        L.append(f"| [`{slug}`]({SITE}/museum/{slug}?draft=1) | {deed} | {conf} | {why} | {'yes' if in_reel else 'no'} |")
    L += [
        "",
        f"## C. Old-catalog deeds with no museum page ({len(without_twin)})",
        "",
        "Shortest first is NOT the order; pick by importance. `sentences` = what the page has now.",
        "",
        "| id | deed | sentences |",
        "|---|---|---|",
    ]
    for e, n, _ in sorted(without_twin, key=lambda x: x[0]["title"]):
        L.append(f"| [`{e['id'][:8]}`]({SITE}/deed/{e['id']}?draft=1) | {e['title']} | {n} |")
    L += [
        "",
        f"## B. Old-catalog deeds already told by a museum page ({len(with_twin)})",
        "",
        "| id | deed | sentences | museum page |",
        "|---|---|---|---|",
    ]
    for e, n, t in sorted(with_twin, key=lambda x: x[0]["title"]):
        L.append(f"| [`{e['id'][:8]}`]({SITE}/deed/{e['id']}?draft=1) | {e['title']} | {n} | [`{t}`]({SITE}/museum/{t}) |")
    L += ["", f"## Shown in the catalog ({len(shown)})", ""]
    for e in sorted(shown, key=lambda x: -entry_sentences(x)):
        L.append(f"- {e['title']} ({entry_sentences(e)} sentences)")
    Path(a.out).write_text("\n".join(L) + "\n", encoding="utf8")
    print(f"shown {len(shown)}/{len(entries)}; museum below bar {len(museum_bad)}; "
          f"old with twin {len(with_twin)}; old without twin {len(without_twin)} -> {a.out}")


if __name__ == "__main__":
    main()
