#!/usr/bin/env bash
# GitHub Actions runner for Mr. P live (scripts/pm15_live.js): trade for N minutes, publish the log, state and LIVE.md
# to the `mrp-data` branch under mrp/live/ every 10 minutes (and at exit), carrying state over between runs.
# Usage: bash mrp/gha_live.sh <minutes> <mode: live|dry>
set -uo pipefail
MINUTES="${1:-335}"; MODE="${2:-live}"; START=$(date +%s)
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

# the live tail for the cockpit's terminal view: tail.jsonl force-pushed as a single-commit branch whenever it changes (≤ every 15 s),
# in its own worktree and process — nothing here touches the bot
TAILWT="$GITHUB_WORKSPACE/../tailwt"; TAIL_BRANCH="${MRP_TAIL_BRANCH:-mrp-live-tail}"
git worktree add -q --orphan -b "$TAIL_BRANCH" "$TAILWT" 2>/dev/null || true
tail_loop() {
  local last=""
  while true; do
    sleep 15
    [ -f "$MRP_LIVE_DIR/tail.jsonl" ] || continue
    local sum; sum=$(md5sum "$MRP_LIVE_DIR/tail.jsonl" | cut -c1-32)
    [ "$sum" = "$last" ] && continue
    ( cd "$TAILWT" && cp "$MRP_LIVE_DIR/tail.jsonl" tail.jsonl && git add tail.jsonl && git commit -q --amend -m "live tail" 2>/dev/null || git commit -q -m "live tail" ) >/dev/null 2>&1 || continue
    ( cd "$TAILWT" && git push -q --force origin "HEAD:$TAIL_BRANCH" ) >/dev/null 2>&1 && last="$sum"
  done
}
tail_loop &
TAILER=$!

FLAG=""; [ "$MODE" = "dry" ] && FLAG="--dry"
MRP_LIVE_MINUTES="$MINUTES" node scripts/pm15_live.js research/pm15_copilot.html $FLAG &
BOT=$!
trap 'kill -TERM $BOT 2>/dev/null; wait $BOT; kill $TAILER 2>/dev/null; publish; exit 0' TERM INT
while kill -0 $BOT 2>/dev/null; do
  for i in $(seq 1 60); do kill -0 $BOT 2>/dev/null || break; sleep 10; done
  publish
done
wait $BOT; RC=$?
kill $TAILER 2>/dev/null
publish
# chain the next run while mrp/LIVE_ON exists on main (and this run was not a crash loop: it lasted over 5 minutes)
if [ "$MODE" = "live" ] && [ $(( $(date +%s) - START )) -gt 300 ] && git fetch -q origin main && git cat-file -e origin/main:mrp/LIVE_ON 2>/dev/null; then
  curl -sS -X POST -H "Authorization: Bearer ${GH_TOKEN:-}" -H "Accept: application/vnd.github+json" \
    "https://api.github.com/repos/${GITHUB_REPOSITORY}/actions/workflows/mrp-live.yml/dispatches" \
    -d "{\"ref\":\"main\",\"inputs\":{\"minutes\":\"335\",\"mode\":\"live\"}}" && echo "next run dispatched"
else
  echo "not chaining (mode=$MODE, LIVE_ON present: $(git cat-file -e origin/main:mrp/LIVE_ON 2>/dev/null && echo yes || echo no))"
fi
exit $RC
