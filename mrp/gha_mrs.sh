#!/usr/bin/env bash
# GitHub Actions runner for Mr. S (mrp/mrs_live.py): run N minutes, publish mrs/{MRS.md,state.json,live.jsonl} to the
# `mrp-data` branch every 5 minutes, carry state between runs, re-dispatch itself while mrs/LIVE_ON exists on main.
set -uo pipefail
MINUTES="${1:-335}"; MODE="${2:-live}"; START=$(date +%s)
DATA_BRANCH="${MRP_DATA_BRANCH:-mrp-data}"; SUB=mrs
export MRS_DIR="${MRS_DIR:-$GITHUB_WORKSPACE/mrsdata}" MRS_MODE="$MODE"
mkdir -p "$MRS_DIR"
WT="$GITHUB_WORKSPACE/../mrswt"
git config --global user.name "predictionbots-mrp"
git config --global user.email "bots@users.noreply.github.com"
if git fetch -q --depth 1 origin "$DATA_BRANCH" 2>/dev/null; then
  git worktree add -q "$WT" "origin/$DATA_BRANCH"
  [ -f "$WT/$SUB/state.json" ] && cp "$WT/$SUB/state.json" "$MRS_DIR/state.json"
  [ -f "$WT/$SUB/live.jsonl" ] && tail -n 20000 "$WT/$SUB/live.jsonl" > "$MRS_DIR/live.jsonl"
else
  git worktree add -q --orphan -b "$DATA_BRANCH" "$WT"
fi
publish() {
  ( cd "$WT" || exit 0
    for i in 1 2 3 4 5; do
      if git fetch -q --depth 1 origin "$DATA_BRANCH" 2>/dev/null; then git reset -q --hard "origin/$DATA_BRANCH"; fi
      mkdir -p "$SUB"; cp "$MRS_DIR"/MRS.md "$MRS_DIR"/state.json "$MRS_DIR"/live.jsonl "$SUB"/ 2>/dev/null
      git add -A "$SUB"; git commit -qm "$SUB $(date -u +%FT%TZ) $MODE" || exit 0
      git push -q origin "HEAD:$DATA_BRANCH" && exit 0
      sleep $((RANDOM % 20 + 5))
    done )
}
FLAG=""; [ "$MODE" = "dry" ] && FLAG="--dry"
python mrp/mrs_live.py --minutes "$MINUTES" $FLAG &
BOT=$!
trap 'kill -TERM $BOT 2>/dev/null; wait $BOT; publish; exit 0' TERM INT
while kill -0 $BOT 2>/dev/null; do
  for i in $(seq 1 30); do kill -0 $BOT 2>/dev/null || break; sleep 10; done
  publish
done
wait $BOT; RC=$?
publish
if [ "$MODE" = "live" ] && [ $(( $(date +%s) - START )) -gt 300 ] && git fetch -q origin main && git cat-file -e "origin/main:$SUB/LIVE_ON" 2>/dev/null; then
  curl -sS -X POST -H "Authorization: Bearer ${GH_TOKEN:-}" -H "Accept: application/vnd.github+json" \
    "https://api.github.com/repos/${GITHUB_REPOSITORY}/actions/workflows/mrs-live.yml/dispatches" \
    -d '{"ref":"main","inputs":{"minutes":"335","mode":"live"}}' && echo "next run dispatched"
else
  echo "not chaining (mode=$MODE)"
fi
exit $RC
