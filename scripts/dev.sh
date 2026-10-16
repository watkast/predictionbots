#!/usr/bin/env bash
# Common commands. Usage: scripts/dev.sh <command> [args]
set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PYTHON:-python}

usage() {
  cat <<'EOF'
scripts/dev.sh <command> [args]

  test                      pytest (no network)
  lint                      pyflakes-style check via python -m compileall + ruff if installed
  smoke                     synthetic backtest smoke for every strategy (no network)
  smoke-live                scripts/smoke_live.py (needs internet; CI only)
  backtest <strategy> [..]  scripts/backtest.py over data/recorded with configs/<strategy>.yaml
  walk <strategy> [N]       walk-forward N folds (default 4) with the YAML grid
  record <series> [secs]    record top-3 Kalshi markets of <series> for <secs> (default 600)
  paper <entry> [secs]      one configs/paper_matrix.yaml entry (default 600 s)
  matrix [secs]             every matrix entry sequentially
  list                      list matrix entries
  report                    rebuild reports/README.md + reports/equity_daily.csv
  kill | unkill             create / remove data/KILL (RiskManager halts all paper runs)
  clean                     remove __pycache__, .pytest_cache
EOF
}

cmd=${1:-help}; shift || true
case "$cmd" in
  test)       $PY -m pytest -q "$@" ;;
  lint)       $PY -m compileall -q pb scripts tests && { command -v ruff >/dev/null && ruff check pb scripts tests || true; } ;;
  smoke)
    for s in mm_inventory mm_crypto_twap mm_weather_ladder favorite_maker endgame_bond sharp_line_maker \
             complete_set_arb cross_venue_arb mean_revert_overreaction taker_lag taker_momentum; do
      $PY scripts/backtest.py --strategy "$s" --synthetic --params "configs/$s.yaml" --report-name "smoke-$s" --out /tmp/pb-smoke >/dev/null \
        && echo "ok   $s" || echo "FAIL $s"
    done ;;
  smoke-live) $PY scripts/smoke_live.py ;;
  backtest)   s=$1; shift; $PY scripts/backtest.py --strategy "$s" --data data/recorded --params "configs/$s.yaml" --report-name "$s" "$@" ;;
  walk)       s=$1; n=${2:-4}; $PY scripts/backtest.py --strategy "$s" --data data/recorded --params "configs/$s.yaml" --walk-forward "$n" --report-name "$s-wf" ;;
  record)     $PY scripts/record.py --venue kalshi --kalshi-series "$1" --top 3 --max-seconds "${2:-600}" ;;
  paper)      e=$1; shift; $PY scripts/paper_matrix.py --entry "$e" --duration "${1:-600}" ;;
  matrix)     $PY scripts/paper_matrix.py --all --duration "${1:-3300}" ;;
  list)       $PY scripts/paper_matrix.py --list ;;
  report)     $PY scripts/report.py ;;
  kill)       mkdir -p data && date -u > data/KILL && echo "data/KILL written" ;;
  unkill)     rm -f data/KILL && echo "data/KILL removed" ;;
  clean)      find . -name __pycache__ -type d -prune -exec rm -rf {} + ; rm -rf .pytest_cache ;;
  help|-h|--help) usage ;;
  *) echo "unknown command: $cmd" >&2; usage; exit 2 ;;
esac
