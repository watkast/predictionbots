#!/usr/bin/env bash
# GitHub Actions runner for the Mr. P recorder (same shape as ef-autobuyer.yml):
# record for N minutes, publish to the `mrp-data` branch every 10 minutes, regenerate mrp/REPORT.md.
# Each run writes under mrp/data/<run>/ so back-to-back runs never overwrite each other's hour files.
set -uo pipefail
MINUTES="${1:-335}"
KIT="${KIT:-$GITHUB_WORKSPACE/mrp}"
DATA_BRANCH="${MRP_DATA_BRANCH:-mrp-data}"
export MRP_DATA_DIR="${MRP_DATA_DIR:-$GITHUB_WORKSPACE/mrpdata}"
mkdir -p "$MRP_DATA_DIR"
RUN="run-$(date -u +%Y%m%dT%H%M)-${GITHUB_RUN_ID:-local}"
WT="$GITHUB_WORKSPACE/../datawt"

git config --global user.name "predictionbots-mrp"
git config --global user.email "bots@users.noreply.github.com"
if git fetch -q --depth 1 origin "$DATA_BRANCH" 2>/dev/null; then
  git worktree add -q "$WT" "origin/$DATA_BRANCH"
else
  git worktree add -q --orphan -b "$DATA_BRANCH" "$WT"
fi

publish() {
  (
    cd "$WT" || exit 0
    for i in 1 2 3 4 5; do
      if git fetch -q --depth 1 origin "$DATA_BRANCH" 2>/dev/null; then
        git reset -q --hard "origin/$DATA_BRANCH"
      fi
      mkdir -p "mrp/data/$RUN"
      cp -r "$MRP_DATA_DIR/." "mrp/data/$RUN/"
      # publish gzipped (10x smaller; keeps every blob far below GitHub's 100 MB limit)
      find "mrp/data/$RUN" -name "*.jsonl" -exec gzip -f {} \;
      python "$KIT/mrp_analyze.py" mrp/data --days 7 --csv mrp/windows.csv > mrp/REPORT.txt 2>&1 || true
      {
        echo "# Mr. P — gate report"
        echo
        echo "Updated $(date -u +%FT%TZ) by \`$RUN\` (last 7 days of data). Read-only recorder — it never places orders."
        echo "Kit and docs: \`mrp/README.md\` on the \`mrp\` branch. Per-window detail: \`mrp/windows.csv\`."
        echo
        echo '```'
        cat mrp/REPORT.txt
        echo '```'
      } > mrp/REPORT.md
      git add -A mrp
      git commit -qm "mrp-record $(date -u +%FT%TZ) $RUN" || exit 0
      git push -q origin "HEAD:$DATA_BRANCH" && exit 0
      sleep $((RANDOM % 20 + 5))
    done
  )
}

# --- run with self-update: every publish cycle, if mrp/ changed on main, pull it and restart the scanner
DEADLINE=$(( $(date +%s) + MINUTES * 60 ))
kit_rev() { git -C "$GITHUB_WORKSPACE" rev-parse "${1:-HEAD}:mrp" 2>/dev/null; }
start() {
  local left=$(( DEADLINE - $(date +%s) ))
  [ "$left" -gt 30 ] || return 1
  timeout "$left" python "$KIT/mrp_recorder.py" &
  pid=$!
}
pid=""
start || exit 0
rc=0
while [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; do
  sleep "${MRP_PUBLISH_SECONDS:-600}"
  publish || true
  if git -C "$GITHUB_WORKSPACE" fetch -q --depth 1 origin main 2>/dev/null && [ "$(kit_rev FETCH_HEAD)" != "$(kit_rev HEAD)" ]; then
    echo "[self-update] new mrp/ on main — restarting on $(git -C "$GITHUB_WORKSPACE" rev-parse --short FETCH_HEAD)"
    git -C "$GITHUB_WORKSPACE" checkout -q FETCH_HEAD -- mrp && git -C "$GITHUB_WORKSPACE" reset -q --soft FETCH_HEAD
    pip install -q -r "$GITHUB_WORKSPACE/mrp/requirements.txt" || true
    kill -TERM "$pid" 2>/dev/null; wait "$pid" 2>/dev/null
    start || break
  fi
done
wait "$pid" 2>/dev/null; rc=$?
publish || true
# `timeout` returns 124 when it stopped the scanner on schedule — that is the normal end of a run
if [ "$rc" -eq 124 ] || [ "$rc" -eq 0 ] || [ "$rc" -eq 143 ]; then exit 0; fi
exit "$rc"
