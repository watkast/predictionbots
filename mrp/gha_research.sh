#!/usr/bin/env bash
# Runs research studies in mrp/research/*.py (or the one named in $1) and publishes each study's output
# folder to the mrp-data branch at mrp/research/<study>/ (report .md, csv, and a cache reused next run).
# Publishing uses the same reset-and-copy loop as the recorder, so concurrent pushes can't drop results.
set -uo pipefail
ONLY="${1:-}"
DATA_BRANCH="${MRP_DATA_BRANCH:-mrp-data}"
WT="$GITHUB_WORKSPACE/../researchwt"
OUT="$GITHUB_WORKSPACE/../researchout"
mkdir -p "$OUT"
git config --global user.name "predictionbots-mrp"
git config --global user.email "bots@users.noreply.github.com"
if git fetch -q --depth 1 origin "$DATA_BRANCH" 2>/dev/null; then
  git worktree add -q "$WT" "origin/$DATA_BRANCH"
else
  git worktree add -q --orphan -b "$DATA_BRANCH" "$WT"
fi
rc=0
names=()
for f in "$GITHUB_WORKSPACE"/mrp/research/*.py; do
  name="$(basename "$f" .py)"
  [ -n "$ONLY" ] && [ "$ONLY" != "$name" ] && continue
  echo "=== study: $name"
  mkdir -p "$OUT/$name"
  [ -d "$WT/mrp/research/$name" ] && cp -r "$WT/mrp/research/$name/." "$OUT/$name/"     # reuse cache
  python "$f" --out "$OUT/$name" || rc=1
  names+=("$name")
  ls -la "$OUT/$name" | head -5
done
cd "$WT" || exit 1
for i in 1 2 3 4 5 6; do
  git fetch -q --depth 1 origin "$DATA_BRANCH" 2>/dev/null && git reset -q --hard "origin/$DATA_BRANCH"
  for name in "${names[@]}"; do
    mkdir -p "mrp/research/$name"
    cp -r "$OUT/$name/." "mrp/research/$name/"
  done
  git add -A mrp/research
  if git diff --cached --quiet; then echo "nothing new to publish"; exit $rc; fi
  git commit -qm "mrp-research $(date -u +%FT%TZ) ${ONLY:-all}"
  if git push -q origin "HEAD:$DATA_BRANCH"; then echo "published"; exit $rc; fi
  echo "push rejected, retrying"
  sleep $((RANDOM % 20 + 5))
done
exit 1
