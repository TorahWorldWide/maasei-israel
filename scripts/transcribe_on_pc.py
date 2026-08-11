#!/usr/bin/env python3
"""Transcript for a YouTube video, fetched through Tomer's PC (rule 62).

YouTube blocks this VM's datacenter IP in both yt-dlp and youtube_transcript_api.
The requirement does not drop because of that: the residential IP on his PC is not
blocked, so the whole route runs there over Tailscale SSH.

  python3 scripts/transcribe_on_pc.py <id-or-url> [<id-or-url> ...]

Layer 1+2 (caption track) covers ~70% in one round trip. Whatever comes back
`needs_whisper` goes to layer 3, faster-whisper on the RTX 4060, at ~10x realtime.
Both layers live on the PC and are documented in the `youtube-content` skill; this
driver exists so a worker runs one command instead of re-deriving the SSH calls and
falling into the traps that skill lists.

Results append to docs/enrichment/transcripts/whisper-all.jsonl, one object per line:
{"id","ok","method","lang","kind","chars","text","title","channel","upload_date"}.

`kind` decides what you may do with the text: `manual` is human-written and quotable;
`auto` and `asr` are machine output — good for checking a claim, never quoted verbatim.
"""
import argparse
import base64
import json
import re
import subprocess
import sys
from pathlib import Path

PC = "tomer@100.78.91.21"
KEY = str(Path.home() / ".ssh" / "id_ed25519")
REMOTE = r"C:\Users\tomer"
OUT = Path(__file__).resolve().parent.parent / "docs/enrichment/transcripts/whisper-all.jsonl"
VID = re.compile(r"[A-Za-z0-9_-]{11}")
# large-v3 at int8_float16 needs ~1.5GB, and yt_whisper_pc.py steps down to medium
# and then small on its own. Below this there is not even room for small.
MIN_FREE_MIB = 1200


def ssh(command, timeout, capture_stdout=True):
    """One SSH call. Keepalive is mandatory: on a long layer-3 batch nothing crosses
    the channel while a video transcribes, and a dropped idle connection takes the
    remote process down with it."""
    argv = ["ssh", "-i", KEY, "-o", "ConnectTimeout=15",
            "-o", "ServerAliveInterval=20", "-o", "ServerAliveCountMax=200",
            PC, command]
    return subprocess.run(argv, timeout=timeout, text=True, encoding="utf-8",
                          errors="replace",
                          stdout=subprocess.PIPE if capture_stdout else None,
                          stderr=subprocess.PIPE)


def parse_jsonl(text):
    """yt-dlp's progress bar writes to stdout, so \\r-terminated chunks land between
    the JSON lines."""
    out = []
    for line in re.split(r"[\r\n]+", text or ""):
        line = line.strip()
        if line.startswith("{"):
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def free_vram_mib():
    r = ssh("nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits", 60)
    used, total = (int(x) for x in r.stdout.strip().splitlines()[0].split(","))
    return total - used


def captions(ids):
    """Layers 1+2 — one call for the whole batch, the extractor is reused."""
    cmd = (f"set PYTHONIOENCODING=utf-8 && python {REMOTE}\\yt_transcripts_pc.py "
           + " ".join(ids))
    return parse_jsonl(ssh(cmd, timeout=60 * len(ids) + 120).stdout)


def whisper(ids):
    """Layer 3 — audio download + GPU transcription, ~10x realtime.

    Output is redirected on the Windows side and read back as base64: piping it
    through the console mangles Hebrew into '?????', and piping ssh through grep
    silently buffers the whole batch away."""
    free = free_vram_mib()
    if free < MIN_FREE_MIB:
        sys.exit(f"GPU busy — {free} MiB free, need {MIN_FREE_MIB}. The PC is Tomer's; "
                 f"if he is playing, wait rather than compete for the card.")
    print(f"[layer 3] {len(ids)} video(s), {free} MiB VRAM free", file=sys.stderr)

    ssh(f'cmd /c "python {REMOTE}\\yt_whisper_pc.py {" ".join(ids)} '
        f'> {REMOTE}\\wh.jsonl 2> {REMOTE}\\wh.log"',
        timeout=3600, capture_stdout=False)
    r = ssh('powershell -Command "[Convert]::ToBase64String('
            f"[IO.File]::ReadAllBytes('{REMOTE}\\wh.jsonl'))\"", 300)
    return parse_jsonl(base64.b64decode(r.stdout.strip()).decode("utf-8", "replace"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("videos", nargs="+", help="YouTube ids or URLs")
    ap.add_argument("--no-whisper", action="store_true",
                    help="captions only; do not occupy the GPU")
    args = ap.parse_args()

    ids, seen = [], set()
    for v in args.videos:
        m = VID.search(v.rsplit("/", 1)[-1].replace("watch?v=", ""))
        if not m:
            sys.exit(f"not a YouTube id or URL: {v}")
        if m.group() not in seen:
            seen.add(m.group())
            ids.append(m.group())

    rows = captions(ids)
    done = {r["id"] for r in rows if r.get("ok")}
    pending = [i for i in ids if i not in done]
    print(f"[layers 1+2] {len(done)}/{len(ids)} from caption tracks", file=sys.stderr)

    if pending and not args.no_whisper:
        rows += whisper(pending)

    rows = {r["id"]: r for r in rows}
    with OUT.open("a", encoding="utf-8") as f:
        for r in rows.values():
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    for vid in ids:
        r = rows.get(vid, {})
        if r.get("ok"):
            print(f"\n=== {vid} · {r.get('kind')} · {r.get('lang')} · "
                  f"{r.get('chars')} chars · {r.get('title','')}\n{r.get('text','')}")
        else:
            print(f"\n=== {vid} — FAILED: {r.get('errors') or 'no result'}\n"
                  "רשום transcript: \"unavailable\" ומה נוסה ב-tried (כלל 62).")

    print(f"\nנשמר ב-{OUT}", file=sys.stderr)
    return 0 if all(rows.get(v, {}).get("ok") for v in ids) else 1


if __name__ == "__main__":
    sys.exit(main())
