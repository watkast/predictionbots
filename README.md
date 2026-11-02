# predictionbots

Automated trading research for **Kalshi**, **Polymarket** and **Novig**, evaluated only with a
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

**2026-10-26: the whole paper matrix below is retired.** Seven paper days against live books: every
maker model lost or never filled, both taker baselines lost as designed, ORACLE-LAG lost heavily
(final table in `reports/README.md`; entries kept under `retired:` in `configs/paper_matrix.yaml`;
the paper / record / backtest / carry / bounty schedules are off, `workflow_dispatch` only). The one
live line of research is **Early Favorite** on Polymarket US 15-min BTC: `research/early_favorite_playbook.md`,
`scripts/early_favorite_tracker.py` (forward test, `polyus.yml`), `scripts/ef_autobuyer.py` (live-book
paper fills, `ef-autobuyer.yml`), `research/early_favorite_signal.pine` (the TradingView HUD).
Live cockpit: `research/pm15_copilot.html` **v4.0** — open it at **https://pm15-relay-worker.machwonder.workers.dev/** (the relay
worker serves this file straight from `main`, wrapped with the mobile viewport; Safari → Share → Add to Home Screen). The
claude.ai artifact copy only shows the layout: that origin blocks outbound connections, so neither Coinbase nor the relay
is reachable from it. One
Polymarket US 15-min BTC round at a time. What settles the market was verified on the recorder's own data (2026-10-31):
the final price equals the mean of the 60 one-second CF Benchmarks index prints with timestamps in [T−60, T) to $0.005
(the v1 model's [T−62, T−2) window was off by up to $7.5), and the exchange's public `/v1/asset-prices/history` 1-s series
*is* that 60-print trailing average — its value at T−1 is the settlement, ~1 s after the bell (the API's `settlementPrice`
lands 20 s to several minutes later). The cockpit therefore runs two feeds: Coinbase spot (WebSocket, leads the index by
~1 s: the early warning and every "if BTC holds here" number) and the index series through the relay (the exact PM line,
the exact final price and next target, and a live basis offset index − Coinbase refreshed every second, median ± MAD).
The brain: a red **kill line** (the level BTC must *average* for the rest of the window to flip the result; cushion =
spot → kill line), a **lookahead** (where the PM line reads in 30 s if BTC holds, 32 of those 60 s already known, plus
BTC's last-10-s / 30-s moves), **LOCKED** (cushion beats the biggest move seen for the time left × 1.5 margin + target
error + basis slack — the only 100% on the page), and in a position a one-word verdict **LOCKED / HOLD / SELL / SELL
NOW**: SELL when the fat-tail-adjusted win chance drops under the floor, when a move bigger than noise would reach the
kill line inside the warning window plus your sell latency, or when the live bid pays more than holding is worth; a thin
cushion in the last two minutes is a warning with the exact bid above which selling beats holding, not a blanket sell.
The win chance is the Gaussian settlement model capped by the empirical ladder of one-minute adverse moves (5 days of
Coinbase 1-min bars), with volatility floored at 60% of the 5-day typical minute. It keeps a **lock record** on the device
(every LOCKED call judged against the real settlement; series settlements cross-checked against the API), voice and
sound alerts, a sell-latency setting, a feed watchdog, and `scripts/pm15_copilot_selftest.js` (a headless DOM-stub run
of the whole pipeline across four synthetic rounds). The paper bot trades the page's own discount rule.
**v4 layout:** **STRICT ACTION** at the very top — exactly the trades the replay-tested persona makes and nothing else: one BUY per round (the discounted favorite, first second it qualifies, with the ideal size in shares = base stake × edge ÷ 4¢ clamped to ½–2×, ÷ the ask) and one SELL per position (when the bid beats the math, or SELL NOW), each issued once and frozen for the action window, quiet otherwise; the replay confirms the panel's commands coincide with the persona's decisions (every persona trade has a strict command for the same opportunity; the panel's extra commands are re-arms after a missed fill). Then **DO NOW!** — the instruction, the round clock, a **confidence badge** (always the same number:
the calibrated chance that the side in question wins at the bell — 100% only when LOCKED) and the trade row (side left,
price right) — then **DO NEXT** (the next three things in time order: NEXT / THEN / LATER, each with its moment), the
position bar, the four prices (price to beat, what Polymarket shows, the index, Coinbase; Polymarket colors), the chart,
and at the bottom **NUMBERS**: every metric in one grid, the field name above its value, one metric per cell, no prose.
Under the trade row an **action timer** runs from the moment a BUY / SELL appears: MAX ODDS for your sell latency (8 s), TAKE ACTION until 15 s, then LATE (buys restart on a new price; sells run on through SELL → SELL NOW). Every box keeps its height while the numbers update. Shipped entry/exit defaults come from the replay grid (fitted on
Oct 29–30, held up on Oct 31–Nov 2): buy a side only when the ask leaves ≥ 8¢ after fee vs its calibrated chance, favorite
only, between 14:00 and 5:00 left; harvest-sell only inside the last 5:00 when the bid beats the math by ≥ 5¢; SELL (not
SELL NOW) must stay true for 2 s before it shows; SELL NOW means something only inside the last 2:00 (where the kill line
is real) or on a collapse under 25% — earlier, a discount buy near the target wobbling across 50% is HOLD, not a loss
(that change took the replay from +$922 to +$1,064 and cut sells-within-30-s-of-the-buy from 38 to 3); and one discount
trade a round, which is what the persona did — re-entering the other side after a sell is a coin flip bought twice. Over
all 224 recorded rounds at $20 a trade: **+$1,064, 0 settlement losses, worst round −$19**, positive on every day.
**Replay (2026-11-01):** `scripts/pm15_human_sim.js` runs the page unmodified against recorded rounds and simulates a human
trading only on DO NEXT; `research/replay/pm15_human_sim_2026-11-01.md` has the results over 224 rounds — LOCKED held
224/224 but is never buyable (first lock at a median 8 s left, no asks), the odds are calibrated after a ×1.3 volatility
multiplier, the EF rule breaks even, and the only paying behaviour is buying the favorite at or under the GOOD price early
and selling when the market overpays late (+$215–236 over 224 rounds at $20 a trade, worst round −$12, 0 settlement
losses — promising, not proven).
**Mr. P live (real money, capped):** `scripts/pm15_live.js` runs the cockpit page unmodified in Node — the same brain
the phone shows — with real feeds (Coinbase WebSocket, gateway series and market terms direct, the exchange book over the
authenticated market-data WebSocket) and executes only its STRICT ACTION commands on Polymarket US: one limit BUY of the
discounted favorite per round (sized to the capital cap, cancelled after the action window), one SELL per position (IOC at
the bid; SELL NOW chases a little); every order passes the page's guards (Coinbase fresh, index series fresh, target exact,
book under 3 s). At most `MRP_LIVE_CAPITAL` (default $20) is ever at risk. `--replay` runs the same order path offline against
recorded rounds with a mock exchange (224 rounds → 201 trades, +$1,255 at a $20 cap, 0 settlement losses, worst −$16).
`.github/workflows/mrp-live.yml` runs it hourly back-to-back (~5.6 h per run) while the repo variable **`MRP_LIVE`** is `on`
(Settings → Secrets and variables → Actions → Variables); set it to anything else and no new run trades; cancel the running
job to stop at once (open orders are cancelled on the way out). The progress report is **`mrp/live/LIVE.md` on the
`mrp-data` branch** (every decision, order, fill and settlement in `mrp/live/live.jsonl`), refreshed every 10 minutes.
**Loser-bounce study (Nov 2):** `research/replay/loser_bounce_2026-11-02.md` — buying the side that fell early and selling at
the first flip, tested on BTC / ETH / SOL / XRP × 5-min / 15-min / 1-hour (`mrp/mrp_extract_windows.py` extracts every
family; the 60-print settlement rule reproduces all 2,970 settlements). The flip is real (72% of 15-min rounds) but the
market prices the trailing side 5–9¢ above its chance early in the round; no band or target is positive net of that.
**Mr. E (ETH 15-minute) and its cockpit:** `scripts/mre_live.js` is a separate one-rule bot — rest a 1-share limit buy at
25¢ on both sides, sell the first fill with a resting 30¢ limit, no new buys inside the last 7:00 (resting buys are pulled; the
sell stays until the close and settles if unfilled). `.github/workflows/mre-live.yml` runs it (`mrp/gha_mre.sh`; switch file
`mre/LIVE_ON`), publishing `mre/MRE.md` to `mrp-data` and its terminal tail to the `mre-live-tail` branch. The cockpit is the
same page with the asset in the URL hash: **`https://pm15-relay-worker.machwonder.workers.dev/#eth`** tracks the ETH market
(ETH line, index and spot), shows Mr. E's rule in STRICT ACTION (rest 25¢ · sell at 30¢ · no more buys at 7:00) and Mr. E's
log in the terminal; no hash (or `#btc`) is the BTC page with Mr. P.
`research/pm15_brain.pine` is the TradingView version of the same brain (kill line, lookahead, LOCKED/HOLD/SELL; it
cannot read the index series, so there the target is typed or estimated and the basis is a setting).
`scripts/pm15_relay_worker.js` is the Cloudflare Worker behind that URL: it serves the cockpit at `/` (from GitHub `main`,
60-s edge cache; `?ref=<branch>` for another revision, `?fresh=1` to bypass the cache) and forwards the three read-only
gateway endpoints with CORS (`/v1/market/slug/{slug}`, `/v1/markets/{slug}/book`, `/v1/asset-prices/history` with query
passthrough). Relay budget: each open page makes ≈ 480 requests a round ≈ 32 a minute ≈ 46k a day if it stays on screen around the clock (book every 1 s in the last 2:00, every 3 s from 5:00 to 2:00, every 10 s before; series every 1–2 s in the last 3:00, every 10 s before; market terms every 30 s; the book every 1 s while a BUY / SELL is on screen and every 2 s when a trade is within 3¢ of triggering, capped at 450 book calls a round; nothing while the tab is hidden) against the free tier's 100k/day — one always-on device is fine, two are close to the cap, so check the worker's Metrics tab or move to the $5 Workers Paid plan (10M/month) before running a second screen all day. The worker URL is baked into the page as the default
relay (Settings: blank = that worker, `direct` = no relay). Changing the page needs no worker redeploy; changing the
worker does (paste the file in the Cloudflare dashboard).
Companion chart tool: `research/velocity_reach_vs_target.pine` (TradingView — projects BTC's velocity /
acceleration forward, draws a vertical reach post with a 1m/2m/3m… time ruler up through the target and
marks the tick where the target is hit, in whichever direction the target lies; the target defaults to the round's price-to-beat estimated the
same way as the HUD, the horizon to the time left in the round, and the status / alerts read
"UP-CROSS POSSIBLE in less than 3:42"; a position row (you hold the side that needs the cross) prints BUY +x% more
(spare time) or SELL x% (share of the distance not covered in time), no inputs needed).

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
| `NOVIG_API_KEY`, `NOVIG_SECRET` (or `NOVIG_SECRET_B64`) | Novig key id + PKCS#8 Ed25519 private-key PEM of a **trading** key (`\n`-escaped PEM is fine). Needed for the signed WebSocket (books + tape) and the `sharp_line_maker_novig_nfl` entry; the public `/v3/public/catalog` routes poll without them. `NOVIG_HOST` picks the environment (default `https://api.paper.novig.com`, play money; production `https://api.novig.com`) — keys are per environment |

## Novig (venue 3, paper only)

`pb/venues/novig.py` adapts Novig's v3 API (CFTC-regulated sports exchange; docs read 2026-10-17, every
fact cited in the module docstring). What matters for the strategies:

* Prices are **probabilities** (`"0.665"`) on a 279-price grid (0.001 steps below 0.05 / above 0.95,
  0.005 in between); `qty` is in 1-cent units (100 = one $1 contract). The adapter converts to the
  YES-leg `Book` (every resting order is a *buy* of one outcome, so a NO-outcome bid at p is a YES ask
  at 1-p) and sizes in $1 contracts.
* **Maker pays zero.** Taker fee = `c * P * (1-P) * N`, `c = 0.06` on game markets since 2026-10-15
  (0.03 before), charged **only while the event is live**; pregame fills are free for both sides.
  Makers get a cash credit of 50% of the live taker fee (70% on NFL/NCAAF futures) — ignored by
  default (`include_credit=False`), like Polymarket rebates.
* Every `GOLIVE` voids all resting orders, so `close_ts` is kickoff and `pull_before_close` applies.
* Free **paper environment** (`paper.novig.com`, $10k play money, same API, no location check).
  Production needs KYC + a device geolocation from the Novig app within 3 days (AZ/MI/NV excluded).
* The YES outcome is the home team (from "Away at Home" descriptions), "Over" or "Yes";
  `meta["outcomes"]`/`meta["sport"]` let `pb.data.odds_link` link markets to The Odds API.
* Undocumented and to be verified on the paper WS before trusting a recording: the WS frame envelope
  (how the market id rides on `book`/`trades` objects) and whether a tape row names the taker's outcome.

`python scripts/paper.py --venue novig --strategy sharp_line_maker --novig-league NFL --top 6 --signals odds:nfl,espn:nfl`

DraftKings and Betr: no API, no trading; they only appear as `book_prob_draftkings` etc. in the
odds signal when The Odds API returns them.

`scripts/dev.sh` wraps the common commands (`test`, `smoke`, `paper <entry>`, `matrix`, `report`, `backtest <strategy>`).
