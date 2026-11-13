#!/usr/bin/env bash
# push_data.sh BRANCH BASE [TRIES]
# Push HEAD to BRANCH. When the push is rejected because the branch moved, replay ONLY this job's own commits (the
# ones after BASE) onto the branch's new tip, and try again.
#
# Why not `git rebase origin/BRANCH`, which every job used until 13 Nov 2026: the archive job rebuilds data branches
# without their history (scripts/archive_release.py prune). After that, a job that had checked out the old tip and
# ran `git rebase origin/BRANCH` would replay the entire old history onto the new one, and push every archived file
# straight back. `--onto NEW BASE` replays only what this job committed.
#
# BASE is the commit the job's checkout started from: run `base=$(git rev-parse HEAD)` before the job commits.
set -uo pipefail
branch="${1:?branch}"; base="${2:?base commit}"; tries="${3:-5}"
for i in $(seq 1 "$tries"); do
  if git push -q origin "HEAD:$branch"; then exit 0; fi
  if ! git fetch -q origin "$branch"; then sleep 7; continue; fi
  new=$(git rev-parse FETCH_HEAD)
  if git rebase -q --onto "$new" "$base"; then
    base="$new"
  else
    git rebase --abort 2>/dev/null
    echo "push_data: could not replay this job's commits onto $branch (try $i)"
  fi
  sleep $((RANDOM % 15 + 5))
done
echo "push_data: push to $branch failed after $tries tries"
exit 1
