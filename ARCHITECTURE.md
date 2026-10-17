# predictionbots — architecture

Goal: net-positive automated trading on Kalshi and Polymarket, evaluated ONLY
with liquidity-realistic simulation (no fill that the real book could not have
given), then paper-traded live from GitHub Actions, then (user decision) real.

DraftKings / Betr have no trading APIs. They enter as *reference signals*
(sharp odds via an odds aggregator / ESPN) that strategies quote around.

## Package layout

```
pb/core/types.py      Book, Level, Trade, Order, Fill, Market, enums (YES-leg convention)
pb/core/fees.py       Kalshi & Polymarket fee schedules (maker/taker, rebates)
pb/sim/engine.py      Engine, SimAPI, Strategy, Signal, Settlement, Result
pb/sim/synthetic.py   synthetic generator (CI only, never for evaluation)
pb/strategies/        one module per model; each class is @register'ed in base.REGISTRY
pb/venues/            kalshi.py, polymarket.py: REST/WS clients, auth, normalisation to core types
pb/data/              recorder (WS + signals -> parquet), historical loaders (-> events), reference feeds,
                      odds_link (team-name matcher: Odds-API events <-> Kalshi/Polymarket markets)
pb/live/              paper runner (same Strategy interface, live books), risk manager (risk.py), ledger
scripts/              CLI entry points (record, backtest, paper, paper_matrix, report, dashboard, replay_check, dev.sh)
configs/              per-strategy params YAML + paper_matrix.yaml (the paper runs)
.github/workflows/    record.yml, paper.yml, backtest.yml, ci.yml
data/                 parquet (recorded + downloaded), gitignored except small samples
reports/              markdown/JSON results committed by workflows; voided.yaml = runs excluded from totals
```

## Conventions (do not break)

* All prices are YES probabilities in [0,1]. NO orders are expressed as YES
  orders at 1-p with the opposite action. Venue adapters convert.
* `Book.bids` sorted best-first (desc), `Book.asks` best-first (asc).
* `Trade.taker_action == BUY` means the taker bought YES (lifted the ask).
* Timestamps are epoch seconds (float).
* A strategy implements `pb.sim.engine.Strategy` and only uses `SimAPI`
  (`book`, `market`, `position`, `open_orders`, `place`, `cancel`, `cancel_all`,
  `schedule`, `log`, `now`). The live paper runner exposes the same API.
  The paper runner rolls markets mid-run (`Engine.add_market` / `remove_market`);
  a strategy that filters on a `markets` set or caches per-market state
  overrides `on_market_added(api, market)` / `on_market_removed(api, market_id)`
  (no-op defaults on the base class).
* Orders default `post_only=True` for maker strategies. Taker strategies use
  `TIF.IOC` and must size against `Book.depth_within`.
* Events for the Engine: `Book | Trade | Signal | Settlement`, replayed in ts order.
  Historical loaders produce iterators of these.
* Fees: `fee_for(market_id) -> FeeSchedule`; venue adapters build it from
  series/category metadata (`pb.core.fees.kalshi_schedule`, `polymarket_schedule`).
* Reference feeds publish `Signal(ts, name, market_id|None, value)`; names:
  `btc_index`, `eth_index`, `twap60`, `fcst_prob` (weather model P(YES)),
  `sharp_prob` (de-vigged sharp sportsbook P(YES)), `book_prob_<bookmaker>`.
* No network in unit tests: mock HTTP/WS. Network-dependent code gets a
  `scripts/smoke_live.py` that the `ci.yml` workflow runs on GitHub (which has
  internet), never locally.
* Secrets via env: `KALSHI_KEY_ID`, `KALSHI_PRIVATE_KEY_PEM` (or `KALSHI_PRIVATE_KEY_B64`),
  `POLY_PRIVATE_KEY`, `POLY_FUNDER`, `ODDS_API_KEY`. Paper mode needs none for
  public data (Kalshi public REST works unauthenticated for market data; WS needs auth).

## Simulator guarantees (pb/sim/engine.py)

* Taker: walks recorded levels, fills <= resting size, consumes it, latency applied.
* Maker: fills only from prints at/through our price after queue-ahead is consumed;
  book crossing our price without a print = assumed filled (adverse).
  `maker_requires_through=True` for low-fidelity (candle+tape) datasets.
* Cancel latency; position caps; settlement at result; mark at mid
  (`RiskManager` marks the daily-loss check at bid/ask against the position).
* `Result.summary()` → net/gross pnl, fees, fills, maker ratio, drawdown,
  max capital at risk, per-market win rate.
