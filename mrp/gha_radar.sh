#!/usr/bin/env bash
# GitHub Actions runner for the Mr. P sports radar (same shape as gha_record.sh):
# scan for N minutes, publish to the `mrp-data` branch every 10 minutes under mrp/radar/<run>/,
# regenerate mrp/RADAR.md. Public endpoints only; no secrets needed; never places orders.
set -uo pipefail
MINUTES="${1:-335}"
KIT="${KIT:-$GITHUB_WORKSPACE/mrp}"
DATA_BRANCH="${MRP_DATA_BRANCH:-mrp-data}"
export MRP_DATA_DIR="${MRP_DATA_DIR:-$GITHUB_WORKSPACE/radardata}"
mkdir -p "$MRP_DATA_DIR"
RUN="run-$(date -u +%Y%m%dT%H%M)-${GITHUB_RUN_ID:-local}"
WT="$GITHUB_WORKSPACE/../radarwt"

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
      mkdir -p "mrp/radar/$RUN"
      cp -r "$MRP_DATA_DIR/." "mrp/radar/$RUN/"
      find "mrp/radar/$RUN" -name "*.jsonl" -exec gzip -f {} \;
      python "$KIT/mrp_radar_report.py" mrp/radar --days 7 > mrp/RADAR.body.md 2>&1 || true
      {
        echo "# Mr. P — sports radar"
        echo
        echo "Updated $(date -u +%FT%TZ) by \`$RUN\` (last 7 days). Read-only scanner of every sports market on Polymarket US and Kalshi — it never places orders."
        echo "Kit: \`mrp/mrp_sports_radar.py\` on the \`mrp\` branch. Raw tape: \`mrp/radar/<run>/\`."
        echo
        cat mrp/RADAR.body.md
      } > mrp/RADAR.md
      rm -f mrp/RADAR.body.md
      git add -A mrp
      git commit -qm "mrp-radar $(date -u +%FT%TZ) $RUN" || exit 0
      git push -q origin "HEAD:$DATA_BRANCH" && exit 0
      sleep $((RANDOM % 20 + 5))
    done
  )
}

timeout "$((MINUTES * 60))" python "$KIT/mrp_sports_radar.py" &
pid=$!
while kill -0 "$pid" 2>/dev/null; do
  sleep "${MRP_PUBLISH_SECONDS:-600}"
  publish || true
done
wait "$pid"; rc=$?
publish || true
if [ "$rc" -eq 124 ] || [ "$rc" -eq 0 ]; then exit 0; fi
exit "$rc"
