# Results

Updated 2026-10-16 17:39 UTC. All numbers are PAPER (simulated fills against live books; no fantasy fills: takers only eat resting size, makers only fill on prints through / at the price after queue, or on adverse crossings). Positive pnl here is necessary, not sufficient.

## Paper leaderboard

| run | strategy | venue | net pnl $ | ret / max cap | max cap $ | fills | maker % | days | hours | flags |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| complete_set_arb_polymarket | complete_set_arb | polymarket | 0.00 | 0.0% | 0.00 | 0 | 0 | 1 | 5.6 | - |
| endgame_bond_kalshi | endgame_bond | kalshi | 0.00 | 0.0% | 0.00 | 0 | 0 | 1 | 5.6 | - |
| favorite_maker_kalshi_scan | favorite_maker | kalshi | 0.00 | 0.0% | 0.00 | 0 | 0 | 1 | 5.6 | - |
| taker_momentum_kxbtc15m | taker_momentum | kalshi | 0.00 | 0.0% | 0.00 | 0 | 0 | 1 | 5.6 | - |
| taker_lag_kxbtc15m | taker_lag | kalshi | -1.73 | -140.7% | 1.23 | 50 | 0 | 1 | 5.6 | - |
| mm_crypto_twap_kxbtc15m | mm_crypto_twap | kalshi | -2.42 | -9.2% | 26.17 | 40 | 100 | 1 | 5.6 | cross-assumed 100%; fill>touch 100.0 |
| mm_weather_ladder_kxhighny | mm_weather_ladder | kalshi | -7.03 | -78.5% | 8.95 | 6 | 100 | 1 | 5.6 | cross-assumed 100% |
| mm_inventory_kxhigh | mm_inventory | kalshi | -17.87 | -5.9% | 301.73 | 723 | 100 | 1 | 5.6 | cross-assumed 100%; fill>touch 33.333; top3 concentrated |

Per-day equity: `reports/equity_daily.csv` (4 run-days). `ret / max cap` = net pnl over the peak collateral locked. `flags` come from the simulator's reality checks (cross-assumed fills = maker fills inferred from the book crossing us without a print; fill>touch = a fill larger than the resting size at the touch; top3 = pnl concentrated in 3 markets) and from the RiskManager (HALTED = daily-loss / kill file).

## Backtests

_No backtest reports yet (reports/*.json from scripts/backtest.py)._

## How to read this

1. A strategy earns a place only with L2 paper days: positive net pnl, maker % high for maker models, no `fill>touch` / high cross-assumed flags, pnl not concentrated in 3 markets.
2. Taker baselines (`taker_lag`, `taker_momentum`) are expected to lose; they calibrate the fee drag.
3. Backtest OOS (`oos*`) rows matter more than in-sample grid rows.
