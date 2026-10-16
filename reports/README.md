# Results

Updated 2026-10-16 11:56 UTC. All numbers are PAPER (simulated fills against live books; no fantasy fills: takers only eat resting size, makers only fill on prints through / at the price after queue, or on adverse crossings). Positive pnl here is necessary, not sufficient.

## Paper leaderboard

_No paper runs yet (data/ledger/*.summary.json)._

## Backtests

_No backtest reports yet (reports/*.json from scripts/backtest.py)._

## How to read this

1. A strategy earns a place only with L2 paper days: positive net pnl, maker % high for maker models, no `fill>touch` / high cross-assumed flags, pnl not concentrated in 3 markets.
2. Taker baselines (`taker_lag`, `taker_momentum`) are expected to lose; they calibrate the fee drag.
3. Backtest OOS (`oos*`) rows matter more than in-sample grid rows.
