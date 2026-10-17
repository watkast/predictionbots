# Results

Updated 2026-10-17 23:47 UTC. All numbers are PAPER (simulated fills against live books; no fantasy fills: takers only eat resting size, makers only fill on prints through / at the price after queue, or on adverse crossings). Positive pnl here is necessary, not sufficient.

## Paper leaderboard

| run | strategy | venue | net pnl $ | ret / max cap | max cap $ | fills | maker % | days | hours | flags |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| endgame_bond_kalshi | endgame_bond | kalshi | 0.00 | 0.0% | 0.00 | 0 | 0 | 2 | 33.3 | - |
| favorite_maker_kalshi_scan | favorite_maker | kalshi | 0.00 | 0.0% | 0.00 | 0 | 0 | 2 | 33.3 | - |
| taker_momentum_kxbtc15m | taker_momentum | kalshi | 0.00 | 0.0% | 0.00 | 0 | 0 | 2 | 27.8 | - |
| mm_weather_ladder_kxhighny | mm_weather_ladder | kalshi | -13.72 | -38.0% | 36.05 | 58 | 100 | 2 | 33.3 | - |
| mm_inventory_kxhigh | mm_inventory | kalshi | -21.19 | -7.0% | 301.73 | 957 | 100 | 2 | 33.3 | fill>touch 5.0; top3 concentrated |
| mm_crypto_twap_kxbtc15m | mm_crypto_twap | kalshi | -40.70 | -99.0% | 41.10 | 48 | 100 | 1 | 11.1 | top3 concentrated |
| taker_lag_kxbtc15m | taker_lag | kalshi | -58.96 | -322.5% | 18.28 | 686 | 0 | 1 | 11.1 | fill>touch 49.0; top3 concentrated; HALTED daily_loss -50.09 < -50.00; risk-rejected > accepted |
| complete_set_arb_polymarket | complete_set_arb | polymarket | -77.48 | -36.3% | 213.32 | 20 | 0 | 2 | 33.3 | risk-rejected > accepted |
| mm_inventory_poly_crypto15m | mm_inventory | polymarket | -87.86 | -195.0% | 45.05 | 241 | 100 | 1 | 11.1 | cross-assumed 100%; fill>touch 1.429; HALTED daily_loss -50.06 < -50.00; risk-rejected > accepted |

Per-day equity: `reports/equity_daily.csv` (8 run-days). `ret / max cap` = net pnl over the peak collateral locked. `flags` come from the simulator's reality checks (cross-assumed fills = maker fills inferred from the book crossing us without a print; fill>touch = a fill larger than the resting size at the touch; top3 = pnl concentrated in 3 markets) and from the RiskManager (HALTED = daily-loss / kill file).

### Voided runs

Excluded from every total above (`reports/voided.yaml`); listed so nothing disappears silently.

| run_id | strategy | net pnl $ | fills | day | reason |
|---|---|---:|---:|---|---|
| mm_crypto_twap_kxbtc15m-20261016T1205 | mm_crypto_twap | -2.42 | 40 | 2026-10-16 | reports/AUDIT_mm_crypto_twap.md: pre-fix QuoteManager left untracked (orphan) resting orders and the engine's position cap ignored resting orders; fills are artifacts of that bug, not edge. |
| mm_crypto_twap_kxbtc15m-20261016T1740 | mm_crypto_twap | 0.00 | 0 | 2026-10-16 | reports/AUDIT_mm_crypto_twap.md: same pre-fix code; the selected window closed 5 min after start and the runner never rolled to the next one (0 fills over 5.5 h). |
| mm_crypto_twap_kxbtc15m-20261016T2316 | mm_crypto_twap | 222.90 | 72 | 2026-10-16 | reports/AUDIT_mm_crypto_twap.md: the +$222.90 is one NO settlement on a 440-contract short built by orphan orders (max_inventory was 60); replay of the recorded window on fixed code gives +$0.49. |
| taker_lag_kxbtc15m-20261016T1205 | taker_lag | -1.73 | 50 | 2026-10-16 | reports/AUDIT_mm_crypto_twap.md: fill>touch measurement bug (touch depth read after the take consumed the level -> ratio inf); pre-fix engine; one window per run. |
| taker_lag_kxbtc15m-20261016T1740 | taker_lag | -0.07 | 6 | 2026-10-16 | reports/AUDIT_mm_crypto_twap.md: fill>touch measurement bug (touch depth read after the take); pre-fix engine; one window per run. |
| taker_lag_kxbtc15m-20261016T2316 | taker_lag | 4.49 | 89 | 2026-10-16 | reports/AUDIT_mm_crypto_twap.md: fill>touch measurement bug (touch depth read after the take); pre-fix engine; one window per run. |

## Backtests

_No backtest reports yet (reports/*.json from scripts/backtest.py)._

## How to read this

1. A strategy earns a place only with L2 paper days: positive net pnl, maker % high for maker models, no `fill>touch` / high cross-assumed flags, pnl not concentrated in 3 markets.
2. Taker baselines (`taker_lag`, `taker_momentum`) are expected to lose; they calibrate the fee drag.
3. Backtest OOS (`oos*`) rows matter more than in-sample grid rows.
