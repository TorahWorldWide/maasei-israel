#!/bin/bash
# Rule 145 — a push is not a deploy. Push, then watch Vercel until the build
# that carries this commit is READY, and fail loudly if it is not.
#
#   scripts/push_and_verify.sh
#
# On 11.8 two builds fell over a font error on Vercel and nobody noticed for
# hours: git said "pushed", the site kept serving the previous build, and the
# only evidence was a page that did not change. This script is that evidence.
set -u
cd /home/ubuntu/maasei-israel || exit 1
PROJECT=prj_BWctQtWM3ATtieWDFceCXk7fb701
TOKEN="$(cat /home/ubuntu/.hermes/.vercel_token)"
TRIES="${1:-40}"   # 40 x 20s = ~13 minutes

git push origin HEAD || exit 1
sha="$(git rev-parse HEAD)"
echo "pushed $sha — waiting for Vercel"

for _ in $(seq 1 "$TRIES"); do
  sleep 20
  state=$(curl -s -H "Authorization: Bearer $TOKEN" \
    "https://api.vercel.com/v6/deployments?projectId=$PROJECT&limit=10" \
  | python3 -c "
import json,sys
sha=sys.argv[1]
for d in json.load(sys.stdin).get('deployments',[]):
    if (d.get('meta') or {}).get('githubCommitSha') == sha:
        print(d.get('readyState') or d.get('state'), d.get('url'))
        break
" "$sha")
  [ -z "$state" ] && { echo "  no deployment for this commit yet"; continue; }
  echo "  $state"
  case "$state" in
    READY*)  echo "READY — $state"; exit 0;;
    ERROR*|CANCELED*) echo "DEPLOY FAILED — $state"; exit 1;;
  esac
done
echo "TIMEOUT — deployment never reached READY"
exit 1
