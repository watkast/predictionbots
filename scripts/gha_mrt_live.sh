#!/usr/bin/env bash
# GitHub Actions runner for Mr. T (scripts/mrt_sniper.py): carry state from the `mrp-data` branch, run N minutes, publish
# mrt/{MRT.md,state.json,live.jsonl,trades.jsonl} every 5 minutes, re-dispatch itself while mrt/LIVE_ON exists on main
# (the 6-hourly cron is only a backstop). Mirrors scripts/gha_mrh_live.sh.
set -uo pipefail
MINUTES="${1:-335}"; MODE="${2:-live}"; START=$(date +%s)
DATA_BRANCH="${MRT_DATA_BRANCH:-mrp-data}"; SUB=mrt
OUT="${MRT_DIR:-$GITHUB_WORKSPACE/data/mrt}"
mkdir -p "$OUT"
if [ -z "${POLYMARKET_KEY_ID:-}" ] || [ -z "${POLYMARKET_SECRET_KEY:-}" ]; then
  echo "POLYMARKET_KEY_ID / POLYMARKET_SECRET_KEY not set — Mr. T has nothing to do"; exit 0
fi
WT="$GITHUB_WORKSPACE/../mrtwt"
git config --global user.name "predictionbots-mrt"
git config --global user.email "bots@users.noreply.github.com"
if git fetch -q --depth 1 origin "$DATA_BRANCH" 2>/dev/null; then
  git worktree add -q "$WT" "origin/$DATA_BRANCH"
  for f in state.json live.jsonl trades.jsonl; do
    [ -f "$WT/$SUB/$f" ] && cp "$WT/$SUB/$f" "$OUT/$f"
  done
else
  git worktree add -q --orphan -b "$DATA_BRANCH" "$WT"
fi
publish() {
  ( cd "$WT" || exit 0
    for i in 1 2 3 4 5; do
      if git fetch -q --depth 1 origin "$DATA_BRANCH" 2>/dev/null; then git reset -q --hard "origin/$DATA_BRANCH"; fi
      mkdir -p "$SUB"
      for f in MRT.md state.json live.jsonl trades.jsonl errors.jsonl; do
        [ -f "$OUT/$f" ] && cp "$OUT/$f" "$SUB/$f"
      done
      git add -A "$SUB"; git commit -qm "mrt $(date -u +%FT%TZ) $MODE" || exit 0
      git push -q origin "HEAD:$DATA_BRANCH" && exit 0
      sleep $((RANDOM % 20 + 5))
    done )
}
FLAG=""; [ "$MODE" = "dry" ] && FLAG="--dry"
python scripts/mrt_sniper.py run --out "$OUT" --minutes "$MINUTES" $FLAG &
BOT=$!
trap 'kill -TERM $BOT 2>/dev/null; wait $BOT; publish; exit 0' TERM INT
while kill -0 $BOT 2>/dev/null; do
  for i in $(seq 1 30); do kill -0 $BOT 2>/dev/null || break; sleep 10; done
  publish
done
wait $BOT; RC=$?
publish
if [ "$MODE" = "live" ] && [ "$RC" -eq 0 ] && [ $(( $(date +%s) - START )) -gt 300 ] && git fetch -q origin main \
   && git cat-file -e "origin/main:mrt/LIVE_ON" 2>/dev/null; then
  curl -sS -X POST -H "Authorization: Bearer ${GH_TOKEN:-}" -H "Accept: application/vnd.github+json" \
    "https://api.github.com/repos/${GITHUB_REPOSITORY}/actions/workflows/mrt-live.yml/dispatches" \
    -d '{"ref":"main","inputs":{"minutes":"335","mode":"live"}}' && echo "next run dispatched"
else
  echo "not chaining (mode=$MODE rc=$RC; a crash waits for the 6-hourly cron, not a re-dispatch loop)"
fi
exit $RC
