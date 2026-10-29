#!/usr/bin/env bash
# Runs research studies in mrp/research/*.py (or the one named in $1) and publishes each study's output
# folder to the mrp-data branch at mrp/research/<study>/ (report .md, csv, and a cache reused next run).
set -uo pipefail
ONLY="${1:-}"
DATA_BRANCH="${MRP_DATA_BRANCH:-mrp-data}"
WT="$GITHUB_WORKSPACE/../researchwt"
git config --global user.name "predictionbots-mrp"
git config --global user.email "bots@users.noreply.github.com"
if git fetch -q --depth 1 origin "$DATA_BRANCH" 2>/dev/null; then
  git worktree add -q "$WT" "origin/$DATA_BRANCH"
else
  git worktree add -q --orphan -b "$DATA_BRANCH" "$WT"
fi
rc=0
for f in "$GITHUB_WORKSPACE"/mrp/research/*.py; do
  name="$(basename "$f" .py)"
  [ -n "$ONLY" ] && [ "$ONLY" != "$name" ] && continue
  echo "=== study: $name"
  mkdir -p "$WT/mrp/research/$name"
  python "$f" --out "$WT/mrp/research/$name" || rc=1
done
cd "$WT" || exit 1
for i in 1 2 3 4 5; do
  git add -A mrp/research
  git commit -qm "mrp-research $(date -u +%FT%TZ) ${ONLY:-all}" || exit $rc
  git push -q origin "HEAD:$DATA_BRANCH" && exit $rc
  git fetch -q --depth 1 origin "$DATA_BRANCH" && git rebase -q "origin/$DATA_BRANCH" || git reset -q --soft "origin/$DATA_BRANCH"
  sleep $((RANDOM % 20 + 5))
done
exit 1
