#!/usr/bin/env bash
# GitHub Actions runner for the Mr. P recorder: record for N minutes, publish to the `mrp-data` branch every
# 10 minutes, regenerate mrp/REPORT.md, then start the next run. Each run writes under mrp/data/<run>/ so
# back-to-back runs never overwrite each other's hour files.
#
# The order of things is the point (13 Nov 2026: until then about a fifth of every day went unrecorded):
#   1. The recorder starts first. Setting up the branch used to come first, took 9 minutes, and nothing recorded.
#   2. The branch is fetched without blobs and checked out sparse: this run's folder, the report files and the few
#      days the report reads. The whole branch is 5 GB and grows 0.3 GB a day; the full checkout this replaces
#      was on its way to filling the runner's disk.
#   3. When the recorder stops, the run asks GitHub for its successor at once. The "hourly" schedule fires every
#      6 to 9 hours on this repo, so waiting for it left the recorder off for 1 to 5 hours at most handoffs.
#   4. The closing publish skips the report and only has to copy, compress and push, so it lands before the job's
#      time limit (the old one was killed mid-push and lost the last minutes) and the successor is not kept waiting.
# Stop the recorder: cancel the run (a cancelled run starts no successor) and disable the workflow.
set -uo pipefail

main() {   # everything runs from inside a function: the self-update below rewrites this file while it is running
  MINUTES="${1:-335}"
  KIT="${KIT:-$GITHUB_WORKSPACE/mrp}"
  DATA_BRANCH="${MRP_DATA_BRANCH:-mrp-data}"
  export MRP_DATA_DIR="${MRP_DATA_DIR:-$GITHUB_WORKSPACE/mrpdata}"
  mkdir -p "$MRP_DATA_DIR"
  RUN="run-$(date -u +%Y%m%dT%H%M)-${GITHUB_RUN_ID:-local}"
  WT="${MRP_WT:-$GITHUB_WORKSPACE/../datawt}"
  DAYS="${MRP_REPORT_DAYS:-3}"
  PUBLISH_S="${MRP_PUBLISH_SECONDS:-600}"
  LAST_FULL_S="${MRP_LAST_FULL_SECONDS:-720}"   # no full publish this close to the end: the closing one carries it
  T0=$(date +%s)
  DEADLINE=$(( T0 + ${MRP_RUN_SECONDS:-$(( MINUTES * 60 ))} ))

  # --- 1. record first
  kit_rev() { git -C "$GITHUB_WORKSPACE" rev-parse "${1:-HEAD}:mrp" 2>/dev/null; }
  alive() { [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; }
  start() {
    local left=$(( DEADLINE - $(date +%s) ))
    [ "$left" -gt 30 ] || return 1
    timeout -k 30 "$left" python "$KIT/mrp_recorder.py" &
    pid=$!
  }
  pid=""
  start || exit 0
  echo "[run] $RUN: recorder started $(( $(date +%s) - T0 )) s into the script, stops in $(( (DEADLINE - $(date +%s)) / 60 )) min"

  # --- 2. the branch: blobless and sparse (the same shape as scripts/gha_mrt_live.sh)
  git config --global user.name "predictionbots-mrp"
  git config --global user.email "bots@users.noreply.github.com"
  sparse_patterns() {   # what this run writes, and what the report reads (mrp_analyze.py keeps day folders by name)
    echo "/mrp/REPORT.md"; echo "/mrp/REPORT.txt"; echo "/mrp/windows.csv"; echo "/mrp/data/$RUN/"
    local d
    for d in $(seq 0 $(( ${DAYS%.*} + 1 ))); do echo "/mrp/data/*/$(date -u -d "-$d day" +%F)/"; done
  }
  fetched=""
  for i in 1 2 3; do   # a network blip here used to send the run down the new-branch path below
    if git fetch -q --depth 1 --filter=blob:none origin "$DATA_BRANCH" 2>/dev/null; then fetched=1; break; fi
    sleep 5
  done
  if [ -n "$fetched" ]; then
    git worktree add -q --no-checkout "$WT" "origin/$DATA_BRANCH"
    sparse_patterns | git -C "$WT" sparse-checkout set --no-cone --stdin
    git -C "$WT" checkout -q "origin/$DATA_BRANCH"
  else
    git worktree add -q --orphan -b "$DATA_BRANCH" "$WT"
  fi
  echo "[setup] branch ready $(( $(date +%s) - T0 )) s into the script: $(du -sh "$WT" 2>/dev/null | cut -f1) checked out, $(df -h --output=avail "$WT" 2>/dev/null | tail -1 | tr -d ' ') free on the disk"

  publish() {   # publish [fast]: copy this run's files in, regenerate the report unless fast, commit, push
    local fast="${1:-}"
    (
      cd "$WT" || { echo "[publish] the branch checkout at $WT is missing"; exit 1; }
      for i in 1 2 3 4 5; do
        # a full publish that lost a push race does not start over once the recorder has stopped: the closing one is next
        [ "$i" = 1 ] || [ -n "$fast" ] || alive || exit 0
        local t1; t1=$(date +%s)
        if git fetch -q --depth 1 --filter=blob:none origin "$DATA_BRANCH" 2>/dev/null; then
          git reset -q --hard "origin/$DATA_BRANCH"
        fi
        mkdir -p "mrp/data/$RUN"
        cp -r "$MRP_DATA_DIR/." "mrp/data/$RUN/"
        # gzipped (10x smaller; keeps every blob far below GitHub's 100 MB limit). -n leaves the copy's timestamp out
        # of the header, so an hour file that is finished compresses to the same bytes every time and is pushed once.
        find "mrp/data/$RUN" -name "*.jsonl" -exec gzip -n -f {} \;
        local t2; t2=$(date +%s)
        if [ -z "$fast" ]; then
          # bounded: the analyzer streams since v2.1 (~300 MB and ~30 s for 2 days); the limits stay as a backstop
          ( ulimit -v 4000000; timeout 600 python "$KIT/mrp_analyze.py" mrp/data --days "$DAYS" --csv mrp/windows.csv ) > mrp/REPORT.txt 2>&1 || echo "(report skipped: analyzer over memory or time budget)" >> mrp/REPORT.txt
          {
            echo "# Mr. P — gate report"
            echo
            echo "Updated $(date -u +%FT%TZ) by \`$RUN\` (last $DAYS days of data). Read-only recorder — it never places orders."
            echo "Kit and docs: \`mrp/README.md\` on the \`mrp\` branch. Per-window detail: \`mrp/windows.csv\`."
            echo
            echo '```'
            cat mrp/REPORT.txt
            echo '```'
          } > mrp/REPORT.md
        fi
        local t3; t3=$(date +%s)
        # named paths, all inside the sparse checkout: `git add -A mrp` would also reach the folders left out of it
        git add -A -- "mrp/data/$RUN" || { echo "[publish] git add refused mrp/data/$RUN (is it outside the sparse checkout?)"; exit 1; }
        local f; for f in mrp/REPORT.md mrp/REPORT.txt mrp/windows.csv; do [ -e "$f" ] && git add -- "$f"; done
        git commit -qm "mrp-record $(date -u +%FT%TZ) $RUN" || exit 0
        if git push -q origin "HEAD:$DATA_BRANCH"; then
          echo "[publish] ${fast:-full}: files $(( t2 - t1 )) s, report $(( t3 - t2 )) s, push $(( $(date +%s) - t3 )) s (try $i)"
          exit 0
        fi
        sleep $((RANDOM % 20 + 5))
      done
      echo "[publish] ${fast:-full}: not pushed after 5 tries"
      exit 1
    )
  }

  handoff() {   # ask GitHub for the next run now: it waits in the concurrency group until this job ends, then starts
    [ -n "${GITHUB_ACTIONS:-}" ] || { echo "[handoff] not on Actions: nothing to start"; return 0; }
    [ "${MRP_CHAIN:-on}" = "on" ] || { echo "[handoff] off (MRP_CHAIN=${MRP_CHAIN:-})"; return 0; }
    local ran=$(( $(date +%s) - T0 ))
    if [ "$ran" -lt "${MRP_CHAIN_MIN_SECONDS:-1200}" ]; then
      echo "[handoff] this run lasted $ran s: a short or broken run starts no successor (the schedule restarts the recorder)"; return 0
    fi
    local api="${GITHUB_API_URL:-https://api.github.com}/repos/${GITHUB_REPOSITORY:-}/actions/workflows/${MRP_WORKFLOW:-mrp-record.yml}"
    local waiting
    waiting=$(curl -sS -m 30 -H "Authorization: Bearer ${GH_TOKEN:-}" -H "Accept: application/vnd.github+json" "$api/runs?per_page=30" 2>/dev/null \
      | python -c '
import json, os, sys
try:
    runs = json.load(sys.stdin)["workflow_runs"]
    print(sum(1 for r in runs if r.get("status") != "completed" and str(r.get("id")) != os.environ.get("GITHUB_RUN_ID", "")))
except Exception:
    print("?")' 2>/dev/null)
    case "$waiting" in
      0|"?"|"") ;;   # none waiting, or the question failed: ask for one (a second request only replaces the first)
      *) echo "[handoff] a run is already waiting behind this one ($waiting): nothing to start"; return 0 ;;
    esac
    local i code
    for i in 1 2 3 4 5 6; do   # GitHub answers 204; a 5xx once ended Mr E's chain silently (4 Nov), so retry
      code=$(curl -sS -m 30 -o /tmp/mrp_dispatch.out -w '%{http_code}' -X POST -H "Authorization: Bearer ${GH_TOKEN:-}" \
        -H "Accept: application/vnd.github+json" "$api/dispatches" -d "{\"ref\":\"${MRP_CHAIN_REF:-main}\"}" 2>/dev/null)
      if [ "$code" = "204" ]; then echo "[handoff] next run requested (try $i)"; return 0; fi
      echo "[handoff] try $i: HTTP $code $(head -c 200 /tmp/mrp_dispatch.out 2>/dev/null)"
      sleep "${MRP_CHAIN_RETRY_SECONDS:-10}"
    done
    echo "::warning title=recorder handoff failed::the next run was not requested; the schedule restarts the recorder when GitHub next fires it"
    return 1
  }

  nap() {   # nap SECONDS: sleep while the recorder runs; false as soon as it has stopped
    local until=$(( $(date +%s) + $1 ))
    while [ "$(date +%s)" -lt "$until" ]; do alive || return 1; sleep "${MRP_POLL_SECONDS:-5}"; done
    alive
  }

  # --- run with self-update: every publish cycle, if mrp/ changed on main, pull it and restart the scanner
  rc=0
  while nap "$PUBLISH_S"; do
    if [ $(( DEADLINE - $(date +%s) )) -gt "$LAST_FULL_S" ]; then publish || true; fi
    if git -C "$GITHUB_WORKSPACE" fetch -q --depth 1 origin main 2>/dev/null && [ "$(kit_rev FETCH_HEAD)" != "$(kit_rev HEAD)" ]; then
      echo "[self-update] new mrp/ on main — restarting on $(git -C "$GITHUB_WORKSPACE" rev-parse --short FETCH_HEAD)"
      git -C "$GITHUB_WORKSPACE" checkout -q FETCH_HEAD -- mrp && git -C "$GITHUB_WORKSPACE" reset -q --soft FETCH_HEAD
      pip install -q -r "$GITHUB_WORKSPACE/mrp/requirements.txt" || true
      kill -TERM "$pid" 2>/dev/null; wait "$pid" 2>/dev/null; pid=""
      start || break
    fi
  done
  if [ -n "$pid" ]; then wait "$pid" 2>/dev/null; rc=$?; fi
  echo "[run] recorder stopped (exit $rc) $(( ($(date +%s) - T0) / 60 )) min into the script"

  # --- 3 and 4. the successor first (one request), then the last minutes of data
  handoff || true
  if ! publish fast; then   # the one publish that must land: say so loudly (error-watch opens a ticket on a red run)
    echo "::error title=recorder data not published::the closing publish of $RUN failed; its last minutes are not on $DATA_BRANCH"
    return 1
  fi
  # `timeout` returns 124 when it stopped the recorder on schedule: that is the normal end of a run
  case "$rc" in 0|124|143) return 0 ;; *) return "$rc" ;; esac
}

main "$@"
exit $?
