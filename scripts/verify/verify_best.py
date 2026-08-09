#!/usr/bin/env python3
"""Definitive quote verifier: for each quote, try every fetch route until the quote is found verbatim.
A quote is only reported as failing if NO route contains it."""
import sys, re, json, os, hashlib, glob
sys.path.insert(0, "/tmp")
from fetchit import curl, to_text

TRANS = {"‘": "'", "’": "'", "“": '"', "”": '"', "׳": "'", "״": '"',
         "–": "-", "—": "-", "−": "-", " ": " ", "‎": "", "‏": "", "​": "", "­": ""}
CACHE = "/tmp/vbest-cache"
os.makedirs(CACHE, exist_ok=True)
ROUTES = [("direct", "{u}"), ("wb24", "https://web.archive.org/web/2024/{u}"),
          ("jina", "https://r.jina.ai/{u}"),
          ("wb18", "https://web.archive.org/web/2018/{u}"),
          ("wb17", "https://web.archive.org/web/20170101/{u}")]


def norm(s):
    for a, b in TRANS.items():
        s = s.replace(a, b)
    s = re.sub(r"[֑-ׇ]", "", s)
    # wiki footnote/edit markers land mid-sentence and break verbatim matching
    s = re.sub(r"\[\s*(\d+|edit|citation needed|דרוש מקור)\s*\]", " ", s, flags=re.I)
    s = re.sub(r"\s+", " ", s)
    # stripped link tags leave a stray space before closing punctuation
    s = re.sub(r"\s+([,.;:!?%)\]])", r"\1", s)
    s = re.sub(r"([(\[])\s+", r"\1", s)
    return s.strip().lower()


def frac_of(q, p):
    q, p = norm(q), norm(p)
    if q in p:
        return 1.0, ""
    words = [w for w in q.split() if len(w) > 1]
    if not words:
        return 0.0, ""
    best, bi, bj = 0, 0, 0
    for i in range(len(words)):
        for j in range(len(words), i + best, -1):
            if " ".join(words[i:j]) in p:
                if j - i > best:
                    best, bi, bj = j - i, i, j
                break
    return round(best / len(words), 2), " ".join(words[bi:bj])[:110]


def best_check(url, q):
    top, tsnip, troute = 0.0, "", None
    for name, tpl in ROUTES:
        pdf = url.lower().split("?")[0].endswith(".pdf") and name != "jina"
        key = os.path.join(CACHE, hashlib.sha1((name + url).encode()).hexdigest())
        out = key + (".pdf" if pdf else ".html")
        if not (os.path.exists(out) and os.path.getsize(out) > 500):
            curl(tpl.format(u=url), out)
        if not os.path.exists(out) or os.path.getsize(out) < 200:
            continue
        f, snip = frac_of(q, to_text(out, pdf))
        if f > top:
            top, tsnip, troute = f, snip, name
        if f == 1.0:
            break
    return top, tsnip, troute


files = sys.argv[1:] or sorted(glob.glob("/tmp/merge-out/*.json"))
grand = {"FOUND": 0, "PARTIAL": 0, "FAIL": 0}
fails = []
for f in files:
    d = json.load(open(f))
    qs = [(c.get("source_url", ""), c.get("quote", "")) for c in d["update"].get("citations", [])]
    qs += [(v.get("source_url", ""), v.get("quote", "")) for v in d.get("verified_quotes", [])]
    seen = set()
    print(f"\n=== {os.path.basename(f)} ===", flush=True)
    for url, q in qs:
        if not q or (url, q) in seen:
            continue
        seen.add((url, q))
        top, snip, route = best_check(url, q)
        st = "FOUND" if top == 1.0 else ("PARTIAL" if top >= 0.9 else "FAIL")
        grand[st] += 1
        if st != "FOUND":
            fails.append((os.path.basename(f), st, top, route, url, q, snip))
        print(f"  [{st:7s} {top:4.2f} {str(route):6s}] {url[:52]:52s} | {q[:44]}", flush=True)
print("\n===== FINAL =====")
print(grand)
for x in fails:
    print(f"\n{x[0]} | {x[1]} {x[2]} (best route {x[3]})\n  {x[4]}\n  QUOTE: \"{x[5][:200]}\"\n  MATCHED: \"{x[6]}\"")
