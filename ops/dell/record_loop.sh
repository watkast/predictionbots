#!/usr/bin/env bash
# Always-on runner for the Mr. P recorder on the home box. Same publish/report/self-update loop as mrp/gha_record.sh,
# without the fixed run length. Needs: /etc/predictionbots/env (GITHUB_TOKEN etc.), /opt/predictionbots checkout,
# /opt/predictionbots/.venv. Never places orders.
set -uo pipefail
REPO_DIR="${REPO_DIR:-/opt/predictionbots}"
KIT="$REPO_DIR/mrp"
VENV="$REPO_DIR/.venv"
DATA_BRANCH="${MRP_DATA_BRANCH:-mrp-data}"
export MRP_DATA_DIR="${MRP_DATA_DIR:-/var/lib/predictionbots/mrpdata}"
WT="/var/lib/predictionbots/datawt"
mkdir -p "$MRP_DATA_DIR" "$(dirname "$WT")"
REMOTE="https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_REPO:-watkast/predictionbots}.git"
git -C "$REPO_DIR" remote set-url origin "$REMOTE"
git config --global user.name "predictionbots-dell"
git config --global user.email "bots@users.noreply.github.com"

if [ ! -d "$WT/.git" ] && [ ! -f "$WT/.git" ]; then
  git -C "$REPO_DIR" fetch -q --depth 1 origin "$DATA_BRANCH" && git -C "$REPO_DIR" worktree add -q "$WT" "origin/$DATA_BRANCH"
fi

RUN="run-$(date -u +%Y%m%dT%H%M)-dell"
publish() {
  (
    cd "$WT" || exit 0
    for i in 1 2 3 4 5; do
      git fetch -q --depth 1 origin "$DATA_BRANCH" && git reset -q --hard "origin/$DATA_BRANCH"
      mkdir -p "mrp/data/$RUN"
      cp -r "$MRP_DATA_DIR/." "mrp/data/$RUN/"
      find "mrp/data/$RUN" -name "*.jsonl" -exec gzip -f {} \;
      DAYS="${MRP_REPORT_DAYS:-3}"
      ( ulimit -v 4000000; timeout 600 "$VENV/bin/python" "$KIT/mrp_analyze.py" mrp/data --days "$DAYS" --csv mrp/windows.csv ) > mrp/REPORT.txt 2>&1 || echo "(report skipped: analyzer over memory or time budget)" >> mrp/REPORT.txt
      { echo "# Mr. P — gate report"; echo; echo "Updated $(date -u +%FT%TZ) by \`$RUN\` (last $DAYS days of data). Read-only recorder — it never places orders."; echo; echo '```'; cat mrp/REPORT.txt; echo '```'; } > mrp/REPORT.md
      git add -A mrp
      git commit -qm "mrp-record $(date -u +%FT%TZ) $RUN" || exit 0
      git push -q origin "HEAD:$DATA_BRANCH" && exit 0
      sleep $((RANDOM % 20 + 5))
    done
  )
}
kit_rev() { git -C "$REPO_DIR" rev-parse "${1:-HEAD}:mrp" 2>/dev/null; }
start() { "$VENV/bin/python" "$KIT/mrp_recorder.py" & pid=$!; }
pid=""; start
while true; do
  sleep "${MRP_PUBLISH_SECONDS:-600}"
  publish || true
  if ! kill -0 "$pid" 2>/dev/null; then echo "[loop] recorder exited; restarting"; RUN="run-$(date -u +%Y%m%dT%H%M)-dell"; start; fi
  if git -C "$REPO_DIR" fetch -q --depth 1 origin main 2>/dev/null && [ "$(kit_rev FETCH_HEAD)" != "$(kit_rev HEAD)" ]; then
    echo "[self-update] new mrp/ on main — restarting on $(git -C "$REPO_DIR" rev-parse --short FETCH_HEAD)"
    git -C "$REPO_DIR" checkout -q FETCH_HEAD -- mrp ops && git -C "$REPO_DIR" reset -q --soft FETCH_HEAD
    "$VENV/bin/pip" install -q -r "$KIT/requirements.txt" || true
    kill -TERM "$pid" 2>/dev/null; wait "$pid" 2>/dev/null
    RUN="run-$(date -u +%Y%m%dT%H%M)-dell"; start
  fi
done
