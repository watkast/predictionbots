# Notes for the integration layer (venues / recorder / loaders / paper runner / workflows)

Written by the strategy-suite agent. None of the files below were edited; these
are the interface expectations the new strategies and `pb/sim/backtest.py` have.

## Engine / SimAPI additions (done in pb/sim/engine.py, backwards compatible)

* `SimAPI.fee(market_id) -> FeeSchedule` — strategies use it to require
  spread >= maker fee + edge (sharp_line_maker) and to price taker arbs net of
  fees (complete_set_arb, cross_venue_arb, taker_lag). The live paper runner
  reuses `Engine`, so this works there unchanged.
* `Engine.fill_context: list[dict]` parallel to `Engine.fills` with
  `{"assumed_cross": bool, "touch_depth": float}` — used by the backtest
  report's reality flags. `Engine._fill` gained an `assumed_cross` kwarg.

## Market.meta keys the strategies read (please populate in venue adapters)

| key | used by | source |
|---|---|---|
| `window_open_ts`, `window_close_ts`, `open_price`, `window_secs`, `asset` | mm_crypto_twap, taker_lag | Kalshi 15-min crypto markets: window close is encoded in the ticker (`KXBTC15M-26OCT161315-…`, US/Eastern); `pb.data.feeds.KalshiCryptoWindow.from_market` already falls back to the ticker then to `close_ts - 900`. For Polymarket 5/15-min up/down markets the meta keys are REQUIRED (no ticker convention). `open_price` (the venue's published window-open reference) is optional but avoids relying on the first index print. |
| `ladder_group` | mm_weather_ladder | id shared by all rungs of a KXHIGH*/KXLOW* ladder; falls back to `event_id`, which Kalshi already gives (`event_ticker`) — so nothing to do on Kalshi if `event_id` is populated. |
| `rung_lo` / `rung_hi` (or `floor_strike` / `cap_strike`) | mm_weather_ladder (obs verdict), feeds.open_meteo_fcst_prob | Kalshi market JSON has `floor_strike`/`cap_strike`; please copy them into meta in `kalshi.to_market` (currently only `subtitle` is copied; `parse_rung` can parse "72° to 73°" from the title/subtitle as a fallback). |
| `peak_ts` | mm_weather_ladder | optional expected time of the daily temperature peak (epoch); default `close_ts - peak_offset_h*3600`. |
| `mutually_exclusive` | complete_set_arb | truthy when the markets of an `event_id` are mutually exclusive AND exhaustive. Kalshi events have `mutually_exclusive` in `/events/{ticker}`; Polymarket neg-risk events (`negRisk`) qualify. |
| `pair_id` | cross_venue_arb | id shared by one Kalshi and one Polymarket market with identical resolution semantics. Must be set by whoever links the markets; the strategy will not guess. |
| `category` | endgame_bond, mean_revert_overreaction, backtest fee inference | Polymarket adapter already sets it; for Kalshi a category string (e.g. "weather", "economics") would let `endgame_bond.allow_categories` work beyond the series-prefix allowlist. |
| `fee_type` | pb.sim.backtest.default_fee_for | if `kalshi.to_market` copies `fee_type` from `/series/{ticker}` into meta, the backtester picks maker-fee series correctly without the prefix heuristic. |

## Signals (names already in ARCHITECTURE.md) and their value shapes

* `btc_index` / `eth_index`: float OR `{"price": float, "size": float, "src": str}` (feeds emit the dict; strategies accept both via `feeds.signal_price`).
* `twap60`: `{"asset": "BTC", "twap": float, "src": "polymarket"}`.
* `fcst_prob`: float, `market_id` = rung market. `fcst_members`: `{"n","mean","sd"}` (global).
* `obs_temp_f`, `obs_high_f`: float (global; one NWS station per runner — if several cities run in one process, add a per-city key or run per city).
* `sharp_prob`: `{"p": float, "books": {bk: p}, "commence_ts": float|None}` (also accepts a bare float). `book_prob_<bk>`: float.
* `game_state`: "pre" | "in" | "post" per market.

## Paper runner wiring requests

* `PaperRunner(signals=...)` takes ONE async iterator; `pb.data.feeds` producers
  are separate generators. A small fan-in (`asyncio.Queue` merge) in
  `scripts/paper.py` is needed to run e.g. `coinbase_index()` +
  `polymarket_twap()` together. `feeds.index_with_fallback(primary, factory)`
  provides the Coinbase→Kraken failover.
* `scripts/paper.py --signals coinbase,twap,open_meteo:LAT,LON,open_meteo-bias:X,odds:SPORT,espn:PATH`
  style flags would be the natural CLI; the feeds need `httpx.AsyncClient`
  for HTTP (polling) and `websockets.connect` by default for WS.
* The Odds API needs `ODDS_API_KEY` (already in the secrets list) and a list
  of `feeds.OddsLink(market_id, home_team, away_team, outcome)` built from the
  Kalshi/Polymarket market titles — a team-name matcher against the venue
  title is the piece that is missing.
* NWS requires a User-Agent; `feeds.NWS_USER_AGENT` is set to the repo owner's email.

## Workflows

* `.github/workflows/backtest.yml` (mentioned in ARCHITECTURE.md but not present) should run
  `python scripts/backtest.py --strategy <name> --data data/recorded --params configs/<name>.yaml --report-name <name>`
  per strategy and commit `reports/<name>.md|json`. `--walk-forward N` with the YAML `grid:` section gives OOS numbers.
  Low-fidelity runs via `--kalshi-series KXBTC15M --start … --end …` need `KALSHI_KEY_ID`/PEM in env for `KalshiClient.from_env()`.
* `scripts/backtest.py --synthetic --strategy mm_inventory` is a good ci.yml smoke step (no network).

## Loader note

* `load_recorded` returns `(markets, events)`; `kalshi_history`/`polymarket_history` return `HistoryEvents`. `pb.sim.backtest.DataSpec` handles both; when `HistoryEvents.low_fidelity` is True the backtester forces `maker_requires_through=True` unless `sim.maker_requires_through` is set explicitly.
* The recorder does not currently persist reference signals. A `signals-*.parquet` (ts, name, market_id, value-as-JSON) alongside books/trades would let `scripts/backtest.py --signals` replay the exact feed the paper run saw. `feeds.signals_from_rows` already reads that shape.
