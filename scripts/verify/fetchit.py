#!/usr/bin/env python3
"""Robust page fetcher with bot-block fallbacks.

    python3 /tmp/fetchit.py <url> [--grep "phrase"]

Tries, in order: direct curl (browser UA) -> r.jina.ai -> web.archive.org.
PDFs are converted with pdftotext (both -raw and -layout are searched).
Prints the extracted plain text to stdout, or the matching lines with --grep.
Exit code 1 if every route failed.
"""
import subprocess, sys, os, re, html, hashlib

CACHE = "/tmp/fetchit-cache"
os.makedirs(CACHE, exist_ok=True)
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")


SEC_UA = "Maasei Israel Research pipikoko222@gmail.com"


def curl(url, out, extra=None):
    ua = SEC_UA if "sec.gov" in url.lower() else UA
    cmd = ["curl", "-sL", "--max-time", "90", "--compressed", "-A", ua,
           "-H", "Accept-Language: en-US,en;q=0.9,he;q=0.8",
           "-H", "From: pipikoko222@gmail.com", "-o", out, url]
    if extra:
        cmd[1:1] = extra
    try:
        subprocess.run(cmd, capture_output=True, timeout=120)
    except subprocess.TimeoutExpired:
        return False
    return os.path.exists(out) and os.path.getsize(out) > 500


def to_text(path, is_pdf):
    if is_pdf:
        best = ""
        # Default mode too, not only -raw and -layout: on a Hebrew PDF those two
        # hand back the words of a line in visual order, and a quote that is
        # verbatim in the document reads as three words out of four.
        for mode in ("-raw", "-layout", ""):
            t = path + (mode or "-plain") + ".txt"
            subprocess.run([x for x in ["pdftotext", mode, path, t] if x],
                           capture_output=True)
            if os.path.exists(t):
                best += "\n" + open(t, encoding="utf-8", errors="ignore").read()
        return best
    h = open(path, encoding="utf-8", errors="ignore").read()
    h = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", h)
    return html.unescape(re.sub(r"(?s)<[^>]+>", " ", h))


BLOCK_MARKERS = ("cloudflare capcha", "just a moment", "awswafcookie",
                 "undeclared automated tool", "enable javascript and cookies",
                 "429 too many requests", "access denied")


def blocked(txt):
    low = txt[:4000].lower()
    return any(m in low for m in BLOCK_MARKERS) or len(txt.strip()) < 400


def fetch(url):
    key = os.path.join(CACHE, hashlib.sha1(url.encode()).hexdigest())
    is_pdf = url.lower().split("?")[0].endswith(".pdf")
    ext = ".pdf" if is_pdf else ".html"

    routes = [
        ("direct", url, is_pdf),
        ("jina", "https://r.jina.ai/" + url, False),
        ("wayback", "https://web.archive.org/web/2024/" + url, is_pdf),
        ("wayback-old", "https://web.archive.org/web/2018/" + url, is_pdf),
    ]
    for name, u, pdf in routes:
        out = f"{key}.{name}{'.pdf' if pdf else '.html'}"
        if not (os.path.exists(out) and os.path.getsize(out) > 500):
            if not curl(u, out):
                continue
        txt = to_text(out, pdf)
        if not blocked(txt):
            return name, txt
    return None, ""


def main():
    url = sys.argv[1]
    grep = None
    if "--grep" in sys.argv:
        grep = sys.argv[sys.argv.index("--grep") + 1]
    route, txt = fetch(url)
    if not route:
        print(f"__FETCH_FAILED__ every route blocked for {url}", file=sys.stderr)
        sys.exit(1)
    print(f"__ROUTE__ {route}", file=sys.stderr)
    if grep:
        norm = re.sub(r"\s+", " ", txt)
        for m in re.finditer(re.escape(grep), norm, re.I):
            print(norm[max(0, m.start() - 300):m.end() + 300])
            print("---")
    else:
        print(re.sub(r"\n{3,}", "\n\n", txt))


if __name__ == "__main__":
    main()
