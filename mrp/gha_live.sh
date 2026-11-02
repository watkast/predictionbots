#!/usr/bin/env bash
# GitHub Actions runner for Mr. P live (scripts/pm15_live.js): trade for N minutes, publish the log, state and LIVE.md
# to the `mrp-data` branch under mrp/live/ every 10 minutes (and at exit), carrying state over between runs.
# Usage: bash mrp/gha_live.sh <minutes> <mode: live|dry>
set -uo pipefail
MINUTES="${1:-335}"; MODE="${2:-live}"
DATA_BRANCH="${MRP_DATA_BRANCH:-mrp-data}"
export MRP_LIVE_DIR="${MRP_LIVE_DIR:-$GITHUB_WORKSPACE/mrplive}"
export MRP_LIVE_CAPITAL="${MRP_LIVE_CAPITAL:-20}"
mkdir -p "$MRP_LIVE_DIR"
WT="$GITHUB_WORKSPACE/../livewt"

git config --global user.name "predictionbots-mrp"
git config --global user.email "bots@users.noreply.github.com"
if git fetch -q --depth 1 origin "$DATA_BRANCH" 2>/dev/null; then
  git worktree add -q "$WT" "origin/$DATA_BRANCH"
  # state carries over: trades, balances, an open position
  [ -f "$WT/mrp/live/state.json" ] && cp "$WT/mrp/live/state.json" "$MRP_LIVE_DIR/state.json"
  [ -f "$WT/mrp/live/live.jsonl" ] && cp "$WT/mrp/live/live.jsonl" "$MRP_LIVE_DIR/live.jsonl"
else
  git worktree add -q --orphan -b "$DATA_BRANCH" "$WT"
fi

publish() {
  (
    cd "$WT" || exit 0
    for i in 1 2 3 4 5; do
      if git fetch -q --depth 1 origin "$DATA_BRANCH" 2>/dev/null; then git reset -q --hard "origin/$DATA_BRANCH"; fi
      mkdir -p mrp/live
      cp "$MRP_LIVE_DIR"/LIVE.md "$MRP_LIVE_DIR"/state.json "$MRP_LIVE_DIR"/live.jsonl mrp/live/ 2>/dev/null
      git add -A mrp/live
      git commit -qm "mrp-live $(date -u +%FT%TZ) $MODE" || exit 0
      git push -q origin "HEAD:$DATA_BRANCH" && exit 0
      sleep $((RANDOM % 20 + 5))
    done
  )
}

FLAG=""; [ "$MODE" = "dry" ] && FLAG="--dry"
MRP_LIVE_MINUTES="$MINUTES" node scripts/pm15_live.js research/pm15_copilot.html $FLAG &
BOT=$!
trap 'kill -TERM $BOT 2>/dev/null; wait $BOT; publish; exit 0' TERM INT
while kill -0 $BOT 2>/dev/null; do
  for i in $(seq 1 60); do kill -0 $BOT 2>/dev/null || break; sleep 10; done
  publish
done
wait $BOT; RC=$?
publish
exit $RC
