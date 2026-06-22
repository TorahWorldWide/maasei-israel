# מעשי ישראל — Autonomous Company Scripts

These are the 0-LLM-token "hands" of the autonomous company that grows the site
toward 1000+ verified entries. The agent (cron `maasei-company-shift`) only
spends tokens on web search + judgment; everything below is plain Python that
talks to Supabase directly. The Supabase management token is read at runtime
from `~/.hermes/maasei_company/config.json` (chmod 600, NOT in this repo).

These files are a committed BACKUP/record. The live copies the cron actually
runs live in `~/.hermes/scripts/` on the VM.

## The accuracy stack (Tomer's iron rule: 1 false entry = mission failure)

Three independent layers ensure no false or broken entry reaches the site:

1. **`maasei_verify.py`** — citation verifier. Downloads each source and checks
   the claimed quote appears in it *word for word*. Three verdicts:
   - `ok` — quote found → entry allowed
   - `suspect` — source readable but quote NOT found → possible fabrication, BLOCKED
   - `unverifiable` — source blocks bots (Cloudflare/Incapsula 200-challenge,
     403, or <500-char stub) → flagged for human check, not falsely accused
   Modes: `--url+--quote` (single), `--json '<entries>'` (staging gate),
   `--audit` (re-check the whole live DB).

2. **`maasei_insert.py`** — the insert gate. With `MAASEI_CHECK_LINKS=1` it
   fetches every `source_url` and REJECTS an entry whose source is genuinely
   DEAD (404/410/DNS-fail). A source that merely blocks bots (403) is allowed.
   Also enforces: non-YouTube source required, video de-dup, category coercion.

3. **`maasei_linkcheck.py`** — the link-rot watchdog. Walks every live
   `source_url` and reports DEAD (404) vs BLOCKED (403, alive). `--watch` is
   silent unless something is actually dead (used by the weekly `maasei-linkrot-watchdog`
   no_agent cron). `--persist` writes results to a `link_health` table.

## The scale engine (toward 1000+)

- **`maasei_leads.py`** — leads backlog. Harvest pre-made lists (Wikipedia,
  Reddit, articles) into a `leads` table cheaply, then verification shifts pull
  and prove them instead of re-searching. `--fetch-list` reads a page (0 search
  tokens), `--add` banks candidates (auto-dedupe vs leads/ledger/entries),
  `--next N` atomically claims leads, `--mark` updates status, `--stats`,
  `--release-stale`.
- **`maasei_ledger.py`** — the manager's notebook; marks topics done/rejected so
  the company never researches the same deed twice.

## Cost discipline (cap tokens, not video count)

- **`maasei_budget.py`** — token governor. `--gate` tells a shift whether it may
  run and its per-shift call ceiling (also enforces a per-day ceiling so runaway
  days burn ~0 tokens). `--record` logs each shift; `--report` shows cadence;
  `--set` adjusts budgets. Defaults: 18 calls/shift, 40 calls/day.

## Historian

- **`maasei_overview.py`** — periodically writes the big-picture "state of the
  nation" summary (`overview` table) that grows as deeds accumulate.

## Crons (on the VM, not here)

- `maasei-company-shift` — daily 02:00 Israel time. Budget gate → leads/ledger →
  research → verify → insert(link-gate) → record → Hebrew report (or [SILENT]).
- `maasei-linkrot-watchdog` — weekly Sunday. Silent unless a source died.
