# predictionbots

Automated trading research for **Kalshi** and **Polymarket**, evaluated only with a
liquidity-realistic simulator and then **paper-traded** against live books. There is
no live-money path in this repo. DraftKings / Betr have no trading APIs; they enter
only as reference odds (via The Odds API) that sports strategies quote around.

```
pip install -e .[dev] && pytest                    # 155 tests, no network
python scripts/backtest.py --strategy mm_inventory --synthetic   # CI smoke
python scripts/paper_matrix.py --list              # the paper runs
python scripts/report.py                           # -> reports/README.md
python scripts/replay_check.py --run-id <run_id>  # replay a paper run's recording with/without the RiskManager
```

See `ARCHITECTURE.md` for the package layout and conventions (YES-leg prices,
`Book`/`Trade`/`Signal`/`Settlement` events, one `Strategy` interface for backtest and paper).

## No fantasy fills

The same `pb.sim.engine.Engine` runs backtests and the paper runner, so a paper fill is
never more generous than a backtest fill:

* **Taker** orders walk the recorded levels and fill at most the resting size (and at most
  `taker_depth_cap_frac` of the depth within 5c of the touch), after `order_latency`.
* **Maker** orders join the back of the queue; they fill only from prints at/through our
  price after the queue ahead is consumed. The book crossing our price without a print is
  counted as a fill but flagged (`cross_assumed_fill_frac`) because it is the adverse case.
  Low-fidelity data (candles + tape) forces `maker_requires_through` (prints strictly
  through our price only).
* Cancels have latency; positions and total collateral are capped; unresolved positions
  are marked at mid; settlements pay at the result.
* The RiskManager's daily-loss check marks at the *conservative* side (bid for longs, ask
  for shorts) whenever the book is two-sided, so a position that could only be unwound at
  a loss halts the run before the mid admits it.
* Every report carries **reality flags**: cross-assumed fill share, max fill / touch depth,
  pnl concentration in the top-3 markets, pnl per contract.
* The paper runner adds a `RiskManager` (`pb/live/risk.py`): daily loss halt (cancel all),
  per-market and total capital caps, orders/min, stale-data guard, kill file `data/KILL`.

## Strategies (`pb/strategies/`, params in `configs/<name>.yaml`)

| name | idea | evidence (one line) |
|---|---|---|
| `mm_inventory` | inventory-skewed, VPIN-gated passive MM, any series | makers +1.9c/contract on Kalshi single-name markets (Bartlett & O'Hara 2026); ~70% of active Polymarket makers profitable (TUM 2025) |
| `mm_crypto_twap` | P(up) from spot index + TWAP vs window open; quotes 15-min crypto windows | makers +0.8c/contract on Kalshi crypto/macro; zero maker fee on KXBTC15M; index-lag takers lose after the 7c fee |
| `mm_weather_ladder` | Open-Meteo ensemble P(rung) vs KXHIGH* ladders, sells overpriced rungs | ladder asks sum ~1.05 median; favourite overpricing ~10x larger in the last 1-12 h; zero maker fee |
| `favorite_maker` | rest bids on favourites 0.70-0.97 where calibration says true prob > price, non-sports | favourite-longshot bias robust on Kalshi and Polymarket; >70c contracts small positive post-fee, better as maker |
| `endgame_bond` | bids at 95-99c in the last hours on low-dispute series, never takes | endgame returns T-bill-like with a fat left tail; makers at >70c small positive |
| `sharp_line_maker` | quote around de-vigged Pinnacle/consensus `sharp_prob` on KXNFLGAME etc. | sports mids track de-vigged Pinnacle within 0.1-0.75pt; makers the only profitable cohort; bias reverses in sports |
| `complete_set_arb` | IOC both legs when YES+NO (or a mutually-exclusive set) < 1 - fees | mispricings exist in thin multi-outcome events; taker fees kill most of them (needs >~3.5c gross on a 2-leg set) |
| `cross_venue_arb` | Kalshi vs Polymarket on `pair_id`-linked markets (taker or maker-Kalshi/hedge-Poly) | cross-venue gaps usually < sum of taker fees; maker-leg variant the only form likely to clear; `pair_id` must be set by hand |
| `mean_revert_overreaction` | fade flow-driven jumps as a maker, 4 h time stop | ~29% of >=2c moves round-trip within 4 h; VPIN spikes predict maker losses so size is capped |
| `taker_lag` (baseline) | take when index-implied fair beats the ask by fee + edge | expected to lose: calibrates the fee drag |
| `taker_momentum` (baseline) | take after a 20c move | expected to lose: calibrates the fee drag |

## Reading `reports/README.md`

`scripts/report.py` aggregates `data/ledger/*.summary.json` (paper runs, grouped per
matrix entry) and `reports/*.json` (backtests) into one page plus `reports/equity_daily.csv`
(one row per run-day: realized pnl, fees, cumulative net).

* **Paper leaderboard**: net pnl, return on peak collateral, fills, maker %, days and hours
  running, and `flags`. Runs listed in `reports/voided.yaml` (run_id or glob + reason, e.g. the
  2026-10-16 runs audited in `reports/AUDIT_mm_crypto_twap.md`) are excluded from every total and
  shown in a "Voided runs" section instead. A strategy only counts with multiple L2 paper days, positive net pnl,
  high maker % for maker models, no `fill>touch` / high cross-assumed flags, and pnl not
  concentrated in 3 markets. `HALTED` means the RiskManager tripped.
* **Backtests**: `oos<k>` rows (walk-forward out-of-sample) matter; in-sample grid rows do not.
  `fidelity=low` rows used candle+tape data.
* The taker baselines should be negative; if they are not, suspect the data.

## Paper matrix

`configs/paper_matrix.yaml` lists the runs; `scripts/paper_matrix.py --entry <name> --duration 3300`
runs one, `--all` runs them sequentially. Each run writes `data/ledger/<entry>-<stamp>.{jsonl,summary.json}`
and records every book, trade and reference signal to `data/recorded/<venue>/<day>/{books,trades,markets,signals}-*.parquet`,
so `scripts/backtest.py --data data/recorded` replays exactly what the paper run saw, and
`scripts/replay_check.py --run-id <run_id>` replays it with and without the RiskManager and prints the
delta against the live ledger (one command per audit).

**Market rolling.** The selector is re-run every `roll_secs` (default 60, `--roll-secs`): newly listed
markets (the next KXBTC15M window, the next day's weather ladder) are wired (fees, pollers, WS
subscription), handed to the recorder and to every strategy (`on_market_added`), and quoted; a market
stays until its settlement has been applied, then leaves (`on_market_removed`). So an hour-long
run is continuous instead of one 15-minute window. The ledger logs `market_added` / `market_removed`
and the summary carries `markets` (every market the run touched), `active_markets` and `last_roll`.

Polymarket 5/15-minute up-or-down markets are not in Gamma's top pages by 24h volume; the
`poly_crypto_15m` selector probes the deterministic slugs (`btc-updown-15m-<window open epoch>`, also
`eth`, `5m`) through `/events?slug=` and `/markets?slug=`, falls back to a `startDate`-ordered scan,
and logs what it tried and found. Polymarket US (separate API) is a TODO in `pb/venues/polymarket.py`.

Signal feeds (`--signals`): `coinbase` (Coinbase trades with Kraken failover -> `btc_index`/`eth_index`),
`twap` (Polymarket 60 s TWAP relay -> `twap60`), `openmeteo:LAT,LON[,BIAS]` (ensemble -> `fcst_prob` per rung),
`nws:STATION` (`obs_temp_f`/`obs_high_f`), `odds[:SPORT]` (The Odds API -> `sharp_prob`, `book_prob_<bk>`),
`espn[:SPORT]` (`game_state`). Sports markets are linked to odds events by `pb/data/odds_link.py`
(NFL/NBA/MLB/NHL aliases; `KXNFLGAME-26OCT19DALWAS-DAL` -> Cowboys @ Commanders, YES = Cowboys).

## Environment / secrets

| variable | needed for |
|---|---|
| `KALSHI_KEY_ID`, `KALSHI_PRIVATE_KEY_PEM` (or `KALSHI_PRIVATE_KEY_B64`) | Kalshi WebSocket books and `/historical` endpoints; public REST polling works without them |
| `ODDS_API_KEY` | optional; `sharp_line_maker` paper entry is skipped without it |
| `POLY_PRIVATE_KEY`, `POLY_FUNDER` | not used by paper trading (only by the unused Polymarket order adapter) |

DraftKings and Betr: no API, no trading; they only appear as `book_prob_draftkings` etc. in the
odds signal when The Odds API returns them.

`scripts/dev.sh` wraps the common commands (`test`, `smoke`, `paper <entry>`, `matrix`, `report`, `backtest <strategy>`).
