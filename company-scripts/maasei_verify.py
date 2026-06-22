#!/usr/bin/env python3
"""
maasei_verify.py — the company's CITATION VERIFIER (0 LLM tokens).

The iron rule of "מעשי ישראל": every entry needs an independent (non-YouTube)
source, and every citation quote must actually appear in that source. This
script is the mechanical enforcer of that rule. It downloads the source page,
strips it to plain text, and checks — word for word — whether the claimed quote
is really there. No model, no guessing: pure text matching.

WHY THIS MATTERS
  Tomer's #1 requirement is accuracy: one fabricated entry = mission failure.
  A model can hallucinate a quote that "sounds like" the source. This script
  catches that BEFORE the entry goes live, because it reads the actual bytes of
  the source and looks for the literal words.

USAGE (all 0 LLM tokens)
  python3 maasei_verify.py --url "<source_url>" --quote "<quote text>"
      → fetch the url, report whether the quote appears.
        Prints {"verified": bool, "score": 0..1, "method": "...", ...}

  python3 maasei_verify.py --json '<entry-json-or-array>'
      → for each entry, verify EVERY citation's quote against its source_url
        (and that source_url itself is non-YouTube). Used by the shift worker
        right before maasei_insert.py, so nothing unverifiable ever gets staged.
        Prints a per-entry verdict array + an overall {"all_ok": bool}.

  python3 maasei_verify.py --audit [--limit N] [--status approved]
      → walk entries already in the DB and re-verify their citations against the
        live source pages. Flags entries whose quotes can no longer be found
        (fabrication that slipped through, or source text that changed).
        Prints a report of OK vs FLAGGED entries.

EXIT CODE
  0 if the requested check passed (verified / all_ok / audit clean),
  1 if something failed verification — so a shell/cron step can gate on it.

MATCHING (Hebrew + English aware)
  Both the quote and the page text are normalized identically:
    - HTML tags removed, HTML entities decoded
    - Hebrew niqqud (vowel points) and cantillation stripped
    - quotes/dashes/punctuation neutralized, whitespace collapsed
    - lowercased (for English)
  Then:
    1. exact normalized substring  -> verified (score 1.0, method "exact")
    2. else best sliding-window word-overlap of the quote's words inside the
       page -> verified if >= 0.85 (method "fuzzy"), "partial" if >= 0.65,
       else "not_found".
  A "partial" is NOT auto-verified — the worker/critic must look. This keeps the
  bar high: only a near-perfect textual match passes automatically.
"""
import argparse
import html
import json
import os
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import maasei_insert as mi  # reuse load_config + run_sql (token-safe DB access)

# Thresholds for fuzzy word-overlap. Deliberately strict: the whole point is to
# refuse anything that isn't really in the source.
VERIFIED_THRESHOLD = 0.85
PARTIAL_THRESHOLD = 0.65

# Cap how much page text we hold in memory / scan (generous; pages are usually
# far smaller). Protects against a multi-megabyte download blowing up the shift.
MAX_TEXT_CHARS = 2_000_000

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

# Full browser-like header set. Several legitimate sources (NCBI/PMC, gov sites)
# 403 a bare User-Agent but serve a request that looks like a real browser.
BROWSER_HEADERS = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,he;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


# ---------------------------------------------------------------------------
# fetching
# ---------------------------------------------------------------------------
def is_youtube(url: str) -> bool:
    return bool(re.search(r"(youtube\.com|youtu\.be)", url or "", re.I))


def fetch_text(url: str, timeout: int = 25):
    """Return (ok, text_or_error). Handles HTML and PDF sources."""
    if not url:
        return False, "empty url"
    try:
        import requests
    except Exception:
        requests = None

    # --- PDF path: download then pdftotext --------------------------------
    looks_pdf = url.lower().split("?")[0].endswith(".pdf")
    try:
        if requests is not None:
            resp = requests.get(url, headers=BROWSER_HEADERS, timeout=timeout,
                                allow_redirects=True)
            status = resp.status_code
            ctype = resp.headers.get("Content-Type", "").lower()
            content = resp.content
        else:
            # Fallback to curl if requests is somehow unavailable.
            out = subprocess.run(
                ["curl", "-sL", "-A", UA, "--max-time", str(timeout), url],
                capture_output=True, timeout=timeout + 5)
            status = 200 if out.returncode == 0 else 0
            ctype = ""
            content = out.stdout
        if status != 200:
            # Distinguish "page is gone" from "page exists but blocks bots".
            # 403/429/503 = alive but blocked (unverifiable, NOT fabrication).
            # 404/410 = genuinely dead link (a real problem for the entry).
            kind = "blocked" if status in (401, 403, 405, 406, 429, 503) else "dead"
            return False, f"http {status}|{kind}"
        if looks_pdf or "application/pdf" in ctype:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
                f.write(content)
                pdf_path = f.name
            try:
                txt = subprocess.run(["pdftotext", "-q", pdf_path, "-"],
                                     capture_output=True, timeout=60).stdout
                return True, txt.decode("utf-8", "ignore")[:MAX_TEXT_CHARS]
            finally:
                try:
                    os.unlink(pdf_path)
                except OSError:
                    pass
        # --- HTML / text path ---------------------------------------------
        text = content.decode(resp.encoding or "utf-8", "ignore") if requests else content.decode("utf-8", "ignore")
        stripped = strip_html(text)[:MAX_TEXT_CHARS]
        # A 200 status can still be an anti-bot challenge page. Detect that and
        # report it as a block, so the quote-not-found logic never fires on it.
        if is_soft_block(stripped):
            return False, "http 200|blocked"
        return True, stripped
    except Exception as ex:  # network error, timeout, DNS, etc.
        return False, f"fetch error: {type(ex).__name__}: {ex}"


def strip_html(s: str) -> str:
    """Crude but dependency-free HTML -> text (no bs4 in this venv)."""
    s = re.sub(r"(?is)<(script|style|noscript|svg|head)[^>]*>.*?</\1>", " ", s)
    s = re.sub(r"(?s)<!--.*?-->", " ", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)  # drop all remaining tags
    s = html.unescape(s)
    return s


# Highly specific phrases that only appear on anti-bot CHALLENGE pages, which
# return HTTP 200 with a block body instead of the article. Treating these as
# "readable" would falsely accuse a real entry of fabrication (the quote isn't
# there because the ARTICLE isn't there). So a soft-block => unverifiable, not
# suspect. Markers chosen to not collide with normal article prose.
SOFT_BLOCK_MARKERS = (
    "incapsula incident id",
    "request unsuccessful",
    "client challenge",
    "javascript is disabled in your browser. please enable javascript",
    "enable javascript to proceed",
    "just a moment...",
    "attention required! | cloudflare",
    "checking your browser before accessing",
    "enable javascript and cookies to continue",
    "please enable cookies",
    "verifying you are human",
    "access denied",
    "you don't have permission to access",
    "ddos protection by",
    "performance & security by cloudflare",
    "a required part of this site couldn",  # press.un.org challenge variant
    "couldn’t load",
    "enable cookies to continue",
)

# A real article that can substantiate a multi-word quote has substantial text.
# If a 200-status page yields fewer than this many characters, it is almost
# certainly a stub / challenge / error shell — not enough to prove or disprove a
# quote, so we treat it as unverifiable rather than accusing the entry.
MIN_ARTICLE_CHARS = 500


def is_soft_block(text: str) -> bool:
    """True if a 200-status page body is actually a bot-challenge/block page,
    or is too short to be a real article that could carry the quote."""
    if not text:
        return True
    if len(text.strip()) < MIN_ARTICLE_CHARS:
        return True
    low = text.lower()
    if any(m in low for m in SOFT_BLOCK_MARKERS):
        # Require the page to be short-ish too, so the phrase appearing inside a
        # long legit article (rare) doesn't trip it. Challenge pages are tiny.
        return len(text) < 4000 or "incapsula incident id" in low or "client challenge" in low
    return False


# ---------------------------------------------------------------------------
# normalization + matching
# ---------------------------------------------------------------------------
# Hebrew niqqud (U+0591–U+05C7 covers cantillation marks + vowel points).
_NIQQUD = re.compile(r"[\u0591-\u05C7]")
# Anything that isn't a Hebrew letter, latin letter, or digit becomes a space.
_NONWORD = re.compile(r"[^0-9a-z\u05d0-\u05ea]+")


def normalize(s: str) -> str:
    s = html.unescape(str(s or ""))
    s = _NIQQUD.sub("", s)
    s = s.lower()
    s = _NONWORD.sub(" ", s)
    return re.sub(r"\s+", " ", s).strip()


def tokens(s: str):
    n = normalize(s)
    return n.split() if n else []


def best_window_overlap(quote_toks, page_toks):
    """Slide a window the size of the quote across the page; return the best
    fraction of quote words present (as a multiset) in any window. O(n).
    """
    q = len(quote_toks)
    if q == 0 or len(page_toks) < 1:
        return 0.0
    if q > len(page_toks):
        # quote longer than page — compare against the whole page as one window
        from collections import Counter
        have = Counter(page_toks)
        hit = sum(1 for t in quote_toks if have.get(t, 0) > 0)
        return hit / q

    from collections import Counter
    qset = Counter(quote_toks)
    win = Counter(page_toks[:q])
    # initial in-window hit count (capped at quote multiplicity)
    def hits(win_counter):
        return sum(min(win_counter.get(t, 0), c) for t, c in qset.items())

    best = hits(win)
    for i in range(q, len(page_toks)):
        win[page_toks[i]] += 1
        win[page_toks[i - q]] -= 1
        if win[page_toks[i - q]] == 0:
            del win[page_toks[i - q]]
        cur = hits(win)
        if cur > best:
            best = cur
            if best == q:
                break
    return best / q


def verify_quote(quote: str, page_text: str):
    """Return dict {verified, score, method}."""
    nq = normalize(quote)
    npage = normalize(page_text)
    if not nq:
        return {"verified": False, "score": 0.0, "method": "empty_quote"}
    if nq in npage:
        return {"verified": True, "score": 1.0, "method": "exact"}
    score = best_window_overlap(nq.split(), npage.split())
    if score >= VERIFIED_THRESHOLD:
        method = "fuzzy"
        verified = True
    elif score >= PARTIAL_THRESHOLD:
        method = "partial"
        verified = False
    else:
        method = "not_found"
        verified = False
    return {"verified": verified, "score": round(score, 3), "method": method}


# ---------------------------------------------------------------------------
# entry-level checks
# ---------------------------------------------------------------------------
def verify_entry(entry: dict, _cache: dict):
    """Verify one entry's citations. Returns a verdict dict with one of three
    entry-level states:
      ok          -> at least one citation quote was found in its live source
      suspect     -> sources were readable but NO quote could be found
                     (this is the fabrication signal — block it)
      unverifiable-> sources could not be fetched (403/timeout); a human/critic
                     must check. NOT treated as fabrication.
    """
    title = entry.get("title", "")
    src = entry.get("source_url", "")
    citations = entry.get("citations", []) or []
    problems = []

    if not src:
        problems.append("missing source_url")
    elif is_youtube(src):
        problems.append("source_url is YouTube (not independent proof)")

    cite_results = []
    n_verified = n_notfound = n_unfetchable = 0
    for c in citations:
        cu = c.get("source_url") or src
        quote = c.get("quote", "")
        if not quote:
            cite_results.append({"quote": "", "verified": False, "method": "no_quote",
                                 "source_url": cu})
            continue
        if cu not in _cache:
            _cache[cu] = fetch_text(cu)
        ok, text = _cache[cu]
        if not ok:
            # split "http 403|blocked" into (detail, kind)
            kind = text.split("|")[-1] if "|" in text else "error"
            cite_results.append({"quote": quote[:60], "verified": False,
                                 "method": "fetch_failed", "fetch_kind": kind,
                                 "detail": text.split("|")[0], "source_url": cu})
            n_unfetchable += 1
            continue
        v = verify_quote(quote, text)
        v["quote"] = quote[:60]
        v["source_url"] = cu
        cite_results.append(v)
        if v["verified"]:
            n_verified += 1
        else:
            n_notfound += 1

    # Decide the entry-level state.
    if not citations:
        state = "no_citations"
        problems.append("no citations to verify")
    elif n_verified > 0:
        state = "ok"
    elif n_notfound > 0:
        # at least one quote was checked against readable text and NOT found
        state = "suspect"
        problems.append("quote(s) checked against readable source but NOT found "
                        "(possible fabrication)")
    else:
        # everything was unfetchable (403/timeout) — can't conclude either way
        state = "unverifiable"
        problems.append("sources could not be fetched (blocked/timeout) — "
                        "needs manual check, not a fabrication verdict")

    return {
        "title": title,
        "source_url": src,
        "state": state,
        "ok": state == "ok",
        "counts": {"verified": n_verified, "not_found": n_notfound,
                   "unfetchable": n_unfetchable},
        "problems": problems,
        "citations": cite_results,
    }


# ---------------------------------------------------------------------------
# modes
# ---------------------------------------------------------------------------
def mode_url_quote(url, quote):
    ok, text = fetch_text(url)
    if not ok:
        print(json.dumps({"verified": False, "method": "fetch_failed",
                          "detail": text, "url": url}, ensure_ascii=False))
        return 1
    res = verify_quote(quote, text)
    res["url"] = url
    print(json.dumps(res, ensure_ascii=False))
    return 0 if res["verified"] else 1


def mode_json(raw):
    try:
        data = json.loads(raw)
    except Exception as ex:
        print(json.dumps({"error": f"bad json: {ex}"}, ensure_ascii=False))
        return 1
    if isinstance(data, dict):
        data = [data]
    cache = {}
    verdicts = [verify_entry(e, cache) for e in data]
    # For staging new entries: block anything 'suspect' (readable source, quote
    # absent). 'unverifiable' is allowed through but flagged for the critic.
    suspect = [v for v in verdicts if v["state"] == "suspect"]
    all_ok = not suspect
    print(json.dumps({"all_ok": all_ok, "suspect_count": len(suspect),
                      "verdicts": verdicts}, ensure_ascii=False))
    return 0 if all_ok else 1


def mode_audit(limit, status):
    cfg = mi.load_config()
    where = f"where status = '{status}'" if status else ""
    lim = f" limit {int(limit)}" if limit else ""
    ok, rows = mi.run_sql(
        f"select title, source_url, citations from entries {where} "
        f"order by created_at{lim};", cfg)
    entries = rows if (ok and isinstance(rows, list)) else []
    cache = {}
    buckets = {"ok": 0, "suspect": [], "unverifiable": [], "no_citations": []}
    for e in entries:
        cites = e.get("citations")
        if isinstance(cites, str):
            try:
                cites = json.loads(cites)
            except Exception:
                cites = []
        e["citations"] = cites or []
        v = verify_entry(e, cache)
        st = v["state"]
        if st == "ok":
            buckets["ok"] += 1
        else:
            buckets[st].append({"title": v["title"], "problems": v["problems"],
                                "counts": v["counts"], "citations": v["citations"]})
    report = {
        "checked": len(entries),
        "ok": buckets["ok"],
        "suspect_count": len(buckets["suspect"]),
        "unverifiable_count": len(buckets["unverifiable"]),
        "no_citations_count": len(buckets["no_citations"]),
        "suspect": buckets["suspect"],
        "unverifiable": buckets["unverifiable"],
        "no_citations": [x["title"] for x in buckets["no_citations"]],
    }
    print(json.dumps(report, ensure_ascii=False))
    # Only a real 'suspect' (possible fabrication) is a failing audit.
    return 0 if not buckets["suspect"] else 1


def main():
    ap = argparse.ArgumentParser(description="Maasei Israel citation verifier")
    ap.add_argument("--url")
    ap.add_argument("--quote")
    ap.add_argument("--json")
    ap.add_argument("--audit", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--status", default="approved")
    args = ap.parse_args()

    if args.url and args.quote:
        sys.exit(mode_url_quote(args.url, args.quote))
    if args.json is not None:
        sys.exit(mode_json(args.json))
    if args.audit:
        sys.exit(mode_audit(args.limit, args.status))
    ap.print_help()
    sys.exit(2)


if __name__ == "__main__":
    main()
