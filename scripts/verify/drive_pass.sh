#!/bin/bash
# Carries a finished worker document through the rest of the pipeline on its own.
#
# The stages after the worker are fixed and none of them needs judgement: apply
# the merge, archive the citations the merge added (rule 136 fails until then),
# then hand the deed to a fresh adversarial reader (rule 140). Doing that by
# hand once per deed means 23 rounds of the same three commands, and a deed that
# finishes while nobody is looking waits.
#
#   nohup scripts/verify/drive_pass.sh >/dev/null 2>&1 &
#
# Progress: tail /tmp/enrich-logs/status-drive.txt
#
# One runner at a time, MAX_LANES workers inside it. On 13.8 this raised the
# adversarial and fix runners on top of three completion lanes, and eight Opus
# workers at midday emptied the session quota in an hour — killing the pass and
# the canonical page beside it. The stages are sequential anyway; there is
# nothing to gain by holding a deed's review and its rewrite open at once.
cd /home/ubuntu/maasei-israel || exit 1
export PATH="$PATH:/home/ubuntu/.local/bin"
LOGS=/tmp/enrich-logs
ST="$LOGS/status-drive.txt"
DONE=/tmp/drive-applied.txt
AQ=/tmp/adversarial-queue.txt
CQ=/tmp/completion-queue.txt
MAX_LANES="${MAX_LANES:-3}"
mkdir -p "$LOGS"
touch "$DONE" "$AQ" "$CQ"

runner_alive() {
  ps -eo args --no-headers | grep -qE "[l]aunch_(completion|adversarial|fix)\.sh"
}

idle=0
while :; do
  moved=0
  for path in /tmp/completion-out/*.json; do
    [ -e "$path" ] || continue
    id="$(basename "$path" .json)"
    grep -qx "$id" "$DONE" && continue
    # A file still being written is not a finished document.
    python3 -c "import json,sys;json.load(open('$path'))" 2>/dev/null || continue

    python3 scripts/apply_completion.py --apply --ids "$id" >"$LOGS/drive-apply-$id.log" 2>&1
    score="$(grep -oE '[0-9]+/58.*' "$LOGS/drive-apply-$id.log" | tail -1)"
    python3 scripts/archive_deed.py --apply "$id" >"$LOGS/drive-archive-$id.log" 2>&1
    arch="$(grep -oE '[0-9]+/[0-9]+ archived, [0-9]+ named as failed' "$LOGS/drive-archive-$id.log" | tail -1)"
    echo "$id" >> "$DONE"
    flock /tmp/adversarial-queue.lock bash -c "echo '$id' >> '$AQ'"
    echo "DRIVEN $id  $score  |  $arch  $(date -u +%H:%M)" >> "$ST"
    moved=1
  done

  # A finished review is written the same way and then hands the deed on to the
  # worker that closes what it opened — which may never be the one that found it.
  for path in /tmp/adversarial-out/*.json; do
    [ -e "$path" ] || continue
    id="$(basename "$path" .json)"
    grep -qx "adv:$id" "$DONE" && continue
    python3 -c "import json,sys;json.load(open('$path'))" 2>/dev/null || continue
    python3 scripts/apply_adversarial.py --apply --ids "$id" >"$LOGS/drive-adv-$id.log" 2>&1
    score="$(grep -oE '[0-9]+/58.*' "$LOGS/drive-adv-$id.log" | tail -1)"
    echo "adv:$id" >> "$DONE"
    if python3 scripts/fix_context.py "$id" --write >/dev/null 2>&1; then
      flock /tmp/fix-queue.lock bash -c "echo '$id' >> /tmp/fix-queue.txt"
      echo "REVIEWED $id  $score  -> fix queue  $(date -u +%H:%M)" >> "$ST"
    else
      echo "REVIEWED $id  $score  no open findings  $(date -u +%H:%M)" >> "$ST"
    fi
    moved=1
  done

  # A fix document is the last write a deed gets, and it goes through the same
  # merging writer — pointed at the fix worker's directory.
  for path in /tmp/fix-out/*.json; do
    [ -e "$path" ] || continue
    id="$(basename "$path" .json)"
    grep -qx "fix:$id" "$DONE" && continue
    python3 -c "import json,sys;json.load(open('$path'))" 2>/dev/null || continue
    python3 scripts/apply_completion.py --apply --dir /tmp/fix-out --ids "$id" \
      >"$LOGS/drive-fix-$id.log" 2>&1
    score="$(grep -oE '[0-9]+/58.*' "$LOGS/drive-fix-$id.log" | tail -1)"
    python3 scripts/archive_deed.py --apply "$id" >"$LOGS/drive-fixarchive-$id.log" 2>&1
    echo "fix:$id" >> "$DONE"
    echo "FIXED $id  $score  $(date -u +%H:%M)" >> "$ST"
    moved=1
  done

  # Each runner exits when its own queue runs dry, so a deed appended after that
  # would sit there forever. Start one again whenever work is waiting — one, and
  # only while no other runner holds the quota. Reviews before rewrites: a review
  # closes a deed in a single worker, a rewrite costs a worker and then a review.
  if ! runner_alive; then
    if [ -s "$AQ" ]; then
      nohup scripts/verify/launch_adversarial.sh "$MAX_LANES" >/dev/null 2>&1 &
      echo "ADVERSARIAL-LANES UP ($MAX_LANES) $(date -u +%H:%M)" >> "$ST"
    elif [ -s /tmp/fix-queue.txt ]; then
      nohup scripts/verify/launch_fix.sh "$MAX_LANES" >/dev/null 2>&1 &
      echo "FIX-LANES UP ($MAX_LANES) $(date -u +%H:%M)" >> "$ST"
    elif [ -s "$CQ" ]; then
      nohup scripts/verify/launch_completion.sh "$MAX_LANES" >/dev/null 2>&1 &
      echo "COMPLETION-LANES UP ($MAX_LANES) $(date -u +%H:%M)" >> "$ST"
    fi
  fi

  lanes="$(ps -eo args --no-headers | grep -cE "[l]aunch_(completion|adversarial|fix).sh")"
  queue="$(cat /tmp/completion-queue.txt /tmp/adversarial-queue.txt /tmp/fix-queue.txt 2>/dev/null | grep -c .)"
  if [ "$lanes" -eq 0 ] && [ "$queue" -eq 0 ] && [ "$moved" -eq 0 ]; then
    idle=$((idle + 1))
  else
    idle=0
  fi
  [ "$idle" -ge 3 ] && break
  sleep 60
done
echo "DRIVE DONE $(date -u +%H:%M)" >> "$ST"
