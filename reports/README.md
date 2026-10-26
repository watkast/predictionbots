# Results

Updated 2026-10-26 12:52 UTC. All numbers are PAPER (simulated fills against live books; no fantasy fills: takers only eat resting size, makers only fill on prints through / at the price after queue, or on adverse crossings). Positive pnl here is necessary, not sufficient.

## Paper leaderboard

**Final table.** The whole matrix was retired on 2026-10-26 (configs/paper_matrix.yaml `retired:`): after 7 paper days every maker model lost or never filled, both taker baselines lost as designed and ORACLE-LAG lost heavily. The paper / record / backtest schedules are off (workflow_dispatch only). The one live line of research is Early Favorite: data branch `polyus/early_favorite/` (forward tracker) and `polyus/ef_autobuyer/` (live-book fills).

| run | strategy | venue | net pnl $ | ret / max cap | max cap $ | fills | maker % | days | hours | flags |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| endgame_bond_kalshi | endgame_bond | kalshi | 0.00 | 0.0% | 0.00 | 0 | 0 | 9 | 116.7 | - |
| favorite_maker_kalshi_scan | favorite_maker | kalshi | 0.00 | 0.0% | 0.00 | 0 | 0 | 9 | 116.7 | - |
| taker_momentum_kxbtc15m | taker_momentum | kalshi | 0.00 | 0.0% | 0.00 | 0 | 0 | 7 | 83.3 | - |
| mm_weather_ladder_kxhighny | mm_weather_ladder | kalshi | -3.57 | -6.1% | 58.25 | 238 | 100 | 9 | 116.7 | - |
| mm_crypto_twap_kxbtc15m | mm_crypto_twap | kalshi | -21.40 | -52.1% | 41.10 | 89 | 100 | 6 | 66.7 | top3 concentrated |
| mm_inventory_kxhigh | mm_inventory | kalshi | -54.58 | -18.1% | 301.73 | 1177 | 100 | 9 | 116.7 | top3 concentrated |
| complete_set_arb_polymarket | complete_set_arb | polymarket | -60.26 | -28.2% | 213.32 | 69 | 0 | 9 | 116.7 | risk-rejected > accepted |
| taker_lag_kxbtc15m | taker_lag | kalshi | -262.06 | -1033.8% | 25.35 | 8317 | 0 | 6 | 61.1 | fill>touch 99.0 |
| oracle_lag_poly_btc15m | oracle_lag | polymarket | -636.30 | -120.9% | 526.11 | 101 | 22 | 6 | 72.2 | risk-rejected > accepted |
| mm_inventory_poly_crypto15m | mm_inventory | polymarket | -711.46 | -910.8% | 78.11 | 2690 | 100 | 8 | 94.4 | cross-assumed 100%; fill>touch 40.0; HALTED daily_loss -50.06 < -50.00; risk-rejected > accepted |
| oracle_lag_kxbtc15m | oracle_lag | kalshi | -1505.40 | -501.8% | 300.00 | 308 | 84 | 6 | 61.1 | fill>touch 5.093; HALTED daily_loss -300.39 < -300.00 |

Per-day equity: `reports/equity_daily.csv` (55 run-days). `ret / max cap` = net pnl over the peak collateral locked. `flags` come from the simulator's reality checks (cross-assumed fills = maker fills inferred from the book crossing us without a print; fill>touch = a fill larger than the resting size at the touch; top3 = pnl concentrated in 3 markets) and from the RiskManager (HALTED = daily-loss / kill file).

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
