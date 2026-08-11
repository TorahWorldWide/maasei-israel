#!/usr/bin/env python3
"""Apply enrichment results to the live Maasei Israel DB.

Reads /tmp/enrich-out/<deed-id>.json (written by the enrichment agents, see
ENRICH-BRIEF.md) and writes the verified sources, images and videos onto the
row. The audit trail the DB has no column for (image provenance, unresolved
points, corrections) is written to docs/enrichment/<id>.json so it survives
a /tmp wipe and stays reviewable in git.

Column mapping:
  master video          -> media_url  (+ media_type = video_embed)
  other videos + images -> media_urls (videos first, images after)
  citations             -> citations  (v2: incl. locator/published/quote_en)
  source_url/_label     -> the primary NON-wikipedia source
  corrections[year]     -> year
  location/people/deed_type/actor_type/beneficiary -> their columns (v2)
  audit                 -> written here from status/missing/tried/unresolved

Closed lists are validated here; an off-list tag is dropped with a warning
(the criterion keeps failing, the review pass fixes it) — never invented.

Dry-run by default. Pass --apply to actually write.
"""
import sys, os, json, glob, datetime

DEED_TYPES = {"המצאה מדעית", "רפואה והצלת חיים", "חסד וצדקה",
              "חילוץ ואסון טבע", "חינוך", "זכויות אדם"}
ACTOR_TYPES = {"אדם יחיד", "ארגון", 'צה"ל', "המדינה", "חברה מסחרית"}
BENEFICIARIES = {"לעם ישראל", "לזרים", "לאנושות כולה"}
PRECISIONS = {"exact", "city", "region", "country"}

sys.path.insert(0, "/home/ubuntu/.hermes/scripts")
from maasei_insert import load_config, run_sql

IN_DIR = "/tmp/enrich-out"
BACKUP = os.path.expanduser("~/.hermes/maasei-backups/enrich")
AUDIT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "enrichment")
MAX_IMAGES = 10
MAX_VIDEOS = 5


def sql(q, cfg):
    ok, res = run_sql(q, cfg)
    if not ok:
        raise RuntimeError(f"SQL failed: {res}")
    return res


def esc(s):
    return str(s).replace("'", "''")


def jsonlit(obj):
    return "'" + esc(json.dumps(obj, ensure_ascii=False)) + "'::jsonb"


def is_image(url):
    return not ("youtube.com" in url or "youtu.be" in url)


def arraylit(vals):
    return "ARRAY[" + ",".join("'" + esc(v) + "'" for v in vals) + "]::text[]"


def standard_sets(enr, stamp, warn):
    """SET clauses for the v2 standard fields. Only touches fields the agent
    actually returned, so v1 outputs apply cleanly with none of them."""
    sets = []
    loc = enr.get("location")
    if isinstance(loc, dict) and loc.get("precision"):
        if loc["precision"] in PRECISIONS:
            sets.append(f"location = {jsonlit(loc)}")
        else:
            warn(f"location.precision '{loc['precision']}' off-list — dropped")
    if enr.get("people"):
        sets.append(f"people = {jsonlit(enr['people'])}")
    dt = [t for t in (enr.get("deed_type") or []) if t in DEED_TYPES]
    bad = [t for t in (enr.get("deed_type") or []) if t not in DEED_TYPES]
    if bad:
        warn(f"deed_type off-list dropped: {bad}")
    if dt:
        sets.append(f"deed_type = {arraylit(dt)}")
    at = enr.get("actor_type")
    if at:
        if at in ACTOR_TYPES:
            sets.append(f"actor_type = '{esc(at)}'")
        else:
            warn(f"actor_type '{at}' off-list — dropped")
    bn = [b for b in (enr.get("beneficiary") or []) if b in BENEFICIARIES]
    badb = [b for b in (enr.get("beneficiary") or []) if b not in BENEFICIARIES]
    if badb:
        warn(f"beneficiary off-list dropped: {badb}")
    if bn:
        sets.append(f"beneficiary = {arraylit(bn)}")

    # v1 outputs (no status field) predate the standard fields — say so honestly
    v1 = "status" not in enr
    audit = {
        "state": "partial" if v1 else enr.get("status", "partial"),
        "at": stamp,
        "by": "sonnet-pass-1+verify_best" if v1 else "opus5-standard-pass+verify_best",
        "checked": ["citations-verbatim", "images-live"],
        "missing": (["locator", "published", "location", "people", "tags"]
                    if v1 else enr.get("missing", [])),
        "tried": enr.get("tried", []),
        "unresolved": enr.get("unresolved", []),
    }
    sets.append(f"audit = {jsonlit(audit)}")
    return sets


def build_media(enr, existing_urls):
    """Return (media_url, media_type, media_urls).

    Videos come first in media_urls because DeedPageBody feeds them to the
    carousel; images after it fall through to the collage.
    """
    videos = enr.get("videos") or []
    master = next((v for v in videos if v.get("master")), videos[0] if videos else None)
    others = [v["url"] for v in videos if v is not master][: MAX_VIDEOS - 1]

    images = [u for u in (enr.get("media_urls") or []) if is_image(u)]
    for u in existing_urls:
        if is_image(u) and u not in images:
            images.append(u)
    images = images[:MAX_IMAGES]

    if master:
        return master["url"], "video_embed", others + images
    return None, None, images


def main():
    apply = "--apply" in sys.argv
    cfg = load_config()
    os.makedirs(BACKUP, exist_ok=True)
    os.makedirs(AUDIT, exist_ok=True)
    files = sorted(glob.glob(f"{IN_DIR}/*.json"))
    print(f"{'APPLYING' if apply else 'DRY RUN'} — {len(files)} deeds\n")
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    for path in files:
        enr = json.load(open(path))
        did = enr["id"]
        rows = sql(f"select * from entries where id = '{esc(did)}';", cfg)
        if not rows:
            print(f"  !! {did[:8]} not found in DB — skipped")
            continue
        row = rows[0]

        with open(f"{BACKUP}/{did}.before-{stamp}.json", "w") as f:
            json.dump(row, f, ensure_ascii=False, indent=2, default=str)

        existing = row.get("media_urls") or []
        if isinstance(existing, str):
            existing = json.loads(existing)
        media_url, media_type, media_urls = build_media(enr, existing)

        warnings = []
        warn = lambda m: warnings.append(m)  # noqa: E731
        sets = [
            f"source_url = '{esc(enr['source_url'])}'",
            f"source_label = '{esc(enr['source_label'])}'",
            f"citations = {jsonlit(enr['citations'])}",
            f"media_urls = {jsonlit(media_urls)}",
        ]
        if media_url:
            sets.append(f"media_url = '{esc(media_url)}'")
            sets.append(f"media_type = '{media_type}'")
        for c in enr.get("corrections") or []:
            if c.get("field") == "year" and c.get("to"):
                sets.append(f"year = {int(c['to'])}")
        sets += standard_sets(enr, stamp, warn)
        for w in warnings:
            print(f"     !! {w}")

        domains = enr.get("domains_covered", 0)
        n_img = len([u for u in media_urls if is_image(u)])
        gaps = []
        if domains < 5:
            gaps.append(f"{domains} domains")
        if n_img < 5:
            gaps.append(f"{n_img} images")
        flag = f"  [SHORT: {', '.join(gaps)}]" if gaps else ""
        print(f"  {did[:8]} {row['title'][:40]}{flag}")
        print(f"     {len(enr['citations'])} citations · "
              f"{len([u for u in media_urls if is_image(u)])} images · "
              f"{len(enr.get('videos') or [])} videos"
              f"{' · master set' if media_url else ''}")

        with open(os.path.join(AUDIT, f"{did}.json"), "w") as f:
            json.dump({
                "id": did,
                "title": row["title"],
                "applied_at": stamp,
                "domains_covered": domains,
                "image_provenance": enr.get("image_provenance", []),
                "videos": enr.get("videos", []),
                "corrections": enr.get("corrections", []),
                "unresolved": enr.get("unresolved", []),
            }, f, ensure_ascii=False, indent=2)

        if apply:
            sql(f"update entries set {', '.join(sets)} where id = '{esc(did)}';", cfg)

    print("\nDONE." if apply else "\nDry run only — pass --apply to write.")


if __name__ == "__main__":
    main()
