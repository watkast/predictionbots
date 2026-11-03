#!/usr/bin/env bash
# GitHub Actions runner for Mr. E (scripts/mre_live.js): run for N minutes, publish mre/{MRE.md,state.json,live.jsonl} to the
# `mrp-data` branch every 10 minutes, carry state over between runs, re-dispatch while mre/LIVE_ON exists on main.
set -uo pipefail
MINUTES="${1:-335}"; MODE="${2:-live}"; START=$(date +%s)
DATA_BRANCH="${MRP_DATA_BRANCH:-mrp-data}"
SUB="${MRE_SUB:-mre}"; TAIL_BRANCH="${MRE_TAIL_BRANCH:-mre-live-tail}"; WORKFLOW="${MRE_WORKFLOW:-mre-live.yml}"   # one market per instance (ETH = mre, BTC = mre-btc)
export MRE_DIR="${MRE_DIR:-$GITHUB_WORKSPACE/mredata}"
mkdir -p "$MRE_DIR"
WT="$GITHUB_WORKSPACE/../mrewt"
git config --global user.name "predictionbots-mrp"
git config --global user.email "bots@users.noreply.github.com"
if git fetch -q --depth 1 origin "$DATA_BRANCH" 2>/dev/null; then
  git worktree add -q "$WT" "origin/$DATA_BRANCH"
  [ -f "$WT/$SUB/state.json" ] && cp "$WT/$SUB/state.json" "$MRE_DIR/state.json"
  [ -f "$WT/$SUB/live.jsonl" ] && cp "$WT/$SUB/live.jsonl" "$MRE_DIR/live.jsonl"
  [ -f "$WT/$SUB/snaps.jsonl" ] && tail -n 30000 "$WT/$SUB/snaps.jsonl" > "$MRE_DIR/snaps.jsonl"
else
  git worktree add -q --orphan -b "$DATA_BRANCH" "$WT"
fi
if [ "$MODE" = "audit" ]; then   # read-only reconciliation of the account against both Mr. E logs; places nothing
  git fetch -q --depth 1 origin "$DATA_BRANCH" && git show "origin/$DATA_BRANCH:mre/live.jsonl" > /tmp/mre_eth.jsonl 2>/dev/null; git show "origin/$DATA_BRANCH:mre-btc/live.jsonl" > /tmp/mre_btc.jsonl 2>/dev/null
  AUDIT_LOGS=/tmp/mre_eth.jsonl,/tmp/mre_btc.jsonl node scripts/mre_audit.js; exit 0
fi
publish() {
  ( cd "$WT" || exit 0
    for i in 1 2 3 4 5; do
      if git fetch -q --depth 1 origin "$DATA_BRANCH" 2>/dev/null; then git reset -q --hard "origin/$DATA_BRANCH"; fi
      mkdir -p "$SUB"; cp "$MRE_DIR"/MRE.md "$MRE_DIR"/state.json "$MRE_DIR"/live.jsonl "$MRE_DIR"/snaps.jsonl "$SUB"/ 2>/dev/null
      git add -A "$SUB"; git commit -qm "$SUB $(date -u +%FT%TZ) $MODE" || exit 0
      git push -q origin "HEAD:$DATA_BRANCH" && exit 0
      sleep $((RANDOM % 20 + 5))
    done )
}
TAILWT="$GITHUB_WORKSPACE/../mretailwt"
git worktree add -q --orphan -b "$TAIL_BRANCH" "$TAILWT" 2>/dev/null || true
tail_loop() { local last=""; while true; do sleep 15; [ -f "$MRE_DIR/tail.jsonl" ] || continue; local sum; sum=$(md5sum "$MRE_DIR/tail.jsonl" | cut -c1-32); [ "$sum" = "$last" ] && continue
  ( cd "$TAILWT" && cp "$MRE_DIR/tail.jsonl" tail.jsonl && git add tail.jsonl && git commit -q --amend -m "live tail" 2>/dev/null || git commit -q -m "live tail" ) >/dev/null 2>&1 || continue
  ( cd "$TAILWT" && git push -q --force origin "HEAD:$TAIL_BRANCH" ) >/dev/null 2>&1 && last="$sum"; done; }
tail_loop & TAILER=$!
FLAG=""; [ "$MODE" = "dry" ] && FLAG="--dry"
MRE_MINUTES="$MINUTES" node scripts/mre_live.js $FLAG &
BOT=$!
trap 'kill -TERM $BOT 2>/dev/null; wait $BOT; kill $TAILER 2>/dev/null; publish; exit 0' TERM INT
while kill -0 $BOT 2>/dev/null; do
  for i in $(seq 1 60); do kill -0 $BOT 2>/dev/null || break; sleep 10; done
  publish
done
wait $BOT; RC=$?
kill $TAILER 2>/dev/null
publish
if [ "$MODE" = "live" ] && [ $(( $(date +%s) - START )) -gt 300 ] && git fetch -q origin main && git cat-file -e "origin/main:$SUB/LIVE_ON" 2>/dev/null; then
  curl -sS -X POST -H "Authorization: Bearer ${GH_TOKEN:-}" -H "Accept: application/vnd.github+json" \
    "https://api.github.com/repos/${GITHUB_REPOSITORY}/actions/workflows/$WORKFLOW/dispatches" \
    -d "{\"ref\":\"main\",\"inputs\":{\"minutes\":\"335\",\"mode\":\"live\"}}" && echo "next run dispatched"
else
  echo "not chaining (mode=$MODE)"
fi
exit $RC
