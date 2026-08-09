#!/usr/bin/env python3
"""Apply the five verifier findings to the merge JSONs. Idempotent."""
import json

EZ_WIKI_OLD = "Ezer Mizion, established in 1979, runs the world's largest Jewish Bone Marrow Donor Registry. In 2008, the organization was awarded the Israel Prize for lifetime achievement"
EZ_WIKI_NEW = "Ezer Mizion, established in 1979, runs the world's largest Jewish Bone Marrow Donor Registry."
EZ_PART_OLD = "Ezer Mizion's Bone Marrow Registry has facilitated 6,652 lifesaving transplants."
EZ_PART_NEW = ("Ezer Mizion's Bone Marrow Registry has facilitated 6,652 lifesaving transplants, "
               "saving the lives of patients throughout the world and sparing thousands of people untold anguish.")
ZK_WIKI_OLD = "'חסד של אמת', שהחלה"
ZK_WIKI_NEW = '"חסד של אמת", שהחלה'


def walk(d):
    for c in d["update"].get("citations", []):
        yield c
    for v in d.get("verified_quotes", []):
        yield v


def fix(slug, fn):
    p = f"/tmp/merge-out/{slug}.json"
    d = json.load(open(p))
    n = fn(d)
    json.dump(d, open(p, "w"), ensure_ascii=False, indent=2)
    print(f"{slug}: {n} field(s) changed")


def ezer(d):
    n = 0
    for c in walk(d):
        q = c.get("quote", "")
        if q.startswith(EZ_WIKI_OLD[:60]) and "Israel Prize" in q:
            c["quote"] = EZ_WIKI_NEW
            c["note"] = "trimmed: the Israel Prize sentence is not adjacent in the article; it is sourced separately from the Jewish Virtual Library citation"
            n += 1
        elif EZ_PART_OLD in q:
            c["quote"] = q.replace(EZ_PART_OLD, EZ_PART_NEW)
            n += 1
    return n


def zaka(d):
    n = 0
    for c in walk(d):
        u = c.get("source_url", "")
        if u.rstrip("/") in ("https://www.zaka.org.il", "https://zaka.org.il"):
            c["source_url"] = "https://zaka.org.il/about/"
            n += 1
        if ZK_WIKI_OLD in c.get("quote", ""):
            c["quote"] = c["quote"].replace(ZK_WIKI_OLD, ZK_WIKI_NEW)
            n += 1
    return n


fix("2_ezer-mizion", ezer)
fix("5_zaka", zaka)
print("6_pillcam / 9_israaid-italy: no change (quotes verified genuine; failures were fetch/markup artifacts)")
