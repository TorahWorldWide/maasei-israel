#!/usr/bin/env python3
"""
maasei_insert.py — the autonomous company's hands.

Inserts verified good-deed video entries into the live "מעשי ישראל" Supabase DB,
de-duplicating by YouTube video id so the company never adds the same clip twice.
Keeps the Supabase management token OUT of any LLM prompt (reads it from
~/.hermes/maasei_company/config.json, chmod 600).

USAGE
  python3 maasei_insert.py --stats
      → prints current entry count + existing video ids (0 tokens, for the agent
        to know what already exists / how the site is growing).

  python3 maasei_insert.py '<json-array>'
      → json is a list of entry objects. Inserts the valid, non-duplicate ones.
        Prints a short JSON summary of what was inserted / skipped.

ENTRY OBJECT
  { title, description, category, year, media_type, media_url, source_url,
    source_label, act, ripple, citations:[{quote,source_label,source_url,locator?}],
    title_reasoning, status }

GATES enforced here (defense in depth — the prompt should already enforce them):
  - source_url required and must NOT be a youtube/youtu.be link (a video isn't proof).
  - category coerced to one of the 4 allowed values.
  - duplicate video id → skipped.
  - status coerced to 'approved' or 'pending' (default 'pending' if gates unmet).
"""
import json
import os
import re
import subprocess
import sys
import tempfile

CONFIG = os.path.expanduser("~/.hermes/maasei_company/config.json")
ALLOWED_CATEGORIES = {"חסד", "המצאה מדעית", "תרומה לעולם", "היסטורי"}


def load_config():
    with open(CONFIG) as f:
        return json.load(f)


def run_sql(sql, cfg):
    """Run SQL via the Supabase Management API over IPv4. Returns (ok, parsed_json_or_text)."""
    # Token goes into a curl config file so it never appears inline (masking-safe).
    body = json.dumps({"query": sql}, ensure_ascii=False)
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as bf:
        bf.write(body)
        body_path = bf.name
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as cf:
        cf.write('header = "Authorization: Bearer ' + cfg["mgmt_token"] + '"\n')
        cf.write('header = "Content-Type: application/json"\n')
        cfg_path = cf.name
    try:
        url = f"https://api.supabase.com/v1/projects/{cfg['project_ref']}/database/query"
        out = subprocess.run(
            ["curl", "-s", "-4", "-K", cfg_path, "-X", "POST", url,
             "--data-binary", "@" + body_path, "-w", "\n__HTTP__%{http_code}"],
            capture_output=True, text=True, timeout=90,
        ).stdout
        m = re.search(r"__HTTP__(\d+)\s*$", out)
        code = m.group(1) if m else "000"
        payload = out[: m.start()] if m else out
        try:
            parsed = json.loads(payload) if payload.strip() else []
        except Exception:
            parsed = payload
        return code == "201", parsed
    finally:
        for p in (body_path, cfg_path):
            try:
                os.unlink(p)
            except OSError:
                pass


def yt_id(url):
    m = re.search(r"(?:v=|youtu\.be/|embed/)([A-Za-z0-9_-]{11})", url or "")
    return m.group(1) if m else None


def existing_video_ids(cfg):
    ok, rows = run_sql(
        "select media_url from entries where media_type in "
        "('video_embed','video_upload') and media_url <> '';", cfg)
    ids = set()
    if ok and isinstance(rows, list):
        for r in rows:
            i = yt_id(r.get("media_url", ""))
            if i:
                ids.add(i)
    return ids


def entry_count(cfg):
    ok, rows = run_sql("select count(*)::int as n from entries;", cfg)
    if ok and isinstance(rows, list) and rows:
        return rows[0].get("n")
    return None


def esc(s):
    return str(s).replace("'", "''")


def is_youtube(url):
    return bool(re.search(r"(youtube\.com|youtu\.be)", url or ""))


def build_insert(entries):
    cols = ("title, description, category, year, media_type, media_url, source_url, "
            "source_label, act, ripple, citations, title_reasoning, status")
    rows = []
    for e in entries:
        year = e.get("year")
        year_sql = str(int(year)) if isinstance(year, (int, float)) else "NULL"
        cit = esc(json.dumps(e.get("citations", []), ensure_ascii=False))
        rows.append(
            f"('{esc(e['title'])}', '{esc(e.get('description',''))}', "
            f"'{esc(e['category'])}', {year_sql}, "
            f"'{esc(e.get('media_type','video_embed'))}', '{esc(e['media_url'])}', "
            f"'{esc(e['source_url'])}', '{esc(e.get('source_label',''))}', "
            f"'{esc(e.get('act',''))}', '{esc(e.get('ripple',''))}', "
            f"'{cit}'::jsonb, '{esc(e.get('title_reasoning',''))}', "
            f"'{esc(e.get('status','pending'))}')"
        )
    return f"insert into entries ({cols}) values\n" + ",\n".join(rows) + " returning id, title, status;"


def main():
    cfg = load_config()

    if len(sys.argv) >= 2 and sys.argv[1] == "--stats":
        n = entry_count(cfg)
        ids = existing_video_ids(cfg)
        print(json.dumps({"entry_count": n, "video_count": len(ids),
                          "existing_video_ids": sorted(ids)}, ensure_ascii=False))
        return

    raw = sys.argv[1] if len(sys.argv) >= 2 else sys.stdin.read()
    try:
        entries = json.loads(raw)
    except Exception as ex:
        print(json.dumps({"error": f"bad json: {ex}"}, ensure_ascii=False))
        sys.exit(1)
    if isinstance(entries, dict):
        entries = [entries]

    existing = existing_video_ids(cfg)

    # Optional live-source gate: when MAASEI_CHECK_LINKS=1 (the cron sets this),
    # every entry's source_url is fetched and an entry pointing at a genuinely
    # DEAD source (404/410/DNS-fail) is rejected before it can be inserted. A
    # source that merely blocks bots (403/anti-bot 200) is NOT rejected — it is
    # alive and fine for a human. This is what stops a broken-link entry (like
    # the bad Jonas Salk Wikipedia URL) from ever entering the site again.
    check_links = os.environ.get("MAASEI_CHECK_LINKS") == "1"
    classify_url = None
    if check_links:
        try:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            import maasei_linkcheck as _lc
            classify_url = _lc.classify
        except Exception:
            classify_url = None  # if the checker can't load, don't block inserts

    valid, skipped = [], []
    for e in entries:
        vid = yt_id(e.get("media_url", ""))
        if not e.get("title") or not e.get("media_url"):
            skipped.append({"reason": "missing title/media_url", "title": e.get("title")})
            continue
        if not e.get("source_url") or is_youtube(e.get("source_url", "")):
            skipped.append({"reason": "no independent source (iron rule)", "title": e.get("title")})
            continue
        if vid and vid in existing:
            skipped.append({"reason": "duplicate video", "title": e.get("title")})
            continue
        if classify_url is not None:
            state, detail = classify_url(e["source_url"])
            if state == "DEAD":
                skipped.append({"reason": f"source_url is DEAD ({detail})",
                                "title": e.get("title"), "source_url": e.get("source_url")})
                continue
        if e.get("category") not in ALLOWED_CATEGORIES:
            e["category"] = "חסד"
        # auto-approve only if there is at least one citation; else stage as pending.
        if not e.get("citations"):
            e["status"] = "pending"
        elif e.get("status") not in ("approved", "pending"):
            e["status"] = "approved"
        valid.append(e)
        if vid:
            existing.add(vid)  # prevent dupes within the same batch

    inserted = []
    if valid:
        ok, result = run_sql(build_insert(valid), cfg)
        if ok and isinstance(result, list):
            inserted = result
        else:
            print(json.dumps({"error": "insert failed", "detail": result,
                              "skipped": skipped}, ensure_ascii=False))
            sys.exit(1)

    print(json.dumps({
        "inserted_count": len(inserted),
        "inserted": inserted,
        "skipped_count": len(skipped),
        "skipped": skipped,
        "total_entries_now": entry_count(cfg),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
