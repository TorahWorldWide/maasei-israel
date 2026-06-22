#!/bin/bash
# Weekly link-rot watchdog wrapper for the no_agent cron.
# Runs the link checker in --watch mode: prints a short Hebrew alert ONLY if a
# source has gone DEAD (404/410), and prints nothing when all links are healthy
# (empty stdout => the cron stays silent). Zero LLM tokens.
exec python3 "$HOME/.hermes/scripts/maasei_linkcheck.py" --watch --status approved
