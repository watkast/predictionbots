# Results

Updated 2026-10-17 04:51 UTC. All numbers are PAPER (simulated fills against live books; no fantasy fills: takers only eat resting size, makers only fill on prints through / at the price after queue, or on adverse crossings). Positive pnl here is necessary, not sufficient.

## Paper leaderboard

| run | strategy | venue | net pnl $ | ret / max cap | max cap $ | fills | maker % | days | hours | flags |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| mm_crypto_twap_kxbtc15m | mm_crypto_twap | kalshi | 220.48 | 101.0% | 218.30 | 112 | 100 | 1 | 16.7 | cross-assumed 100%; top3 concentrated; risk-rejected > accepted |
| taker_lag_kxbtc15m | taker_lag | kalshi | 2.69 | 52.1% | 5.16 | 145 | 0 | 1 | 16.7 | fill>touch inf; top3 concentrated |
| mm_weather_ladder_kxhighny | mm_weather_ladder | kalshi | 0.82 | 3.3% | 24.90 | 25 | 100 | 1 | 16.7 | cross-assumed 100%; fill>touch 2.5 |
| complete_set_arb_polymarket | complete_set_arb | polymarket | 0.00 | 0.0% | 0.00 | 0 | 0 | 1 | 16.7 | risk-rejected > accepted |
| endgame_bond_kalshi | endgame_bond | kalshi | 0.00 | 0.0% | 0.00 | 0 | 0 | 1 | 16.7 | - |
| favorite_maker_kalshi_scan | favorite_maker | kalshi | 0.00 | 0.0% | 0.00 | 0 | 0 | 1 | 16.7 | - |
| taker_momentum_kxbtc15m | taker_momentum | kalshi | 0.00 | 0.0% | 0.00 | 0 | 0 | 1 | 16.7 | - |
| mm_inventory_kxhigh | mm_inventory | kalshi | -17.87 | -5.9% | 301.73 | 726 | 100 | 1 | 16.7 | - |

Per-day equity: `reports/equity_daily.csv` (5 run-days). `ret / max cap` = net pnl over the peak collateral locked. `flags` come from the simulator's reality checks (cross-assumed fills = maker fills inferred from the book crossing us without a print; fill>touch = a fill larger than the resting size at the touch; top3 = pnl concentrated in 3 markets) and from the RiskManager (HALTED = daily-loss / kill file).

## Backtests

_No backtest reports yet (reports/*.json from scripts/backtest.py)._

## How to read this

1. A strategy earns a place only with L2 paper days: positive net pnl, maker % high for maker models, no `fill>touch` / high cross-assumed flags, pnl not concentrated in 3 markets.
2. Taker baselines (`taker_lag`, `taker_momentum`) are expected to lose; they calibrate the fee drag.
3. Backtest OOS (`oos*`) rows matter more than in-sample grid rows.
