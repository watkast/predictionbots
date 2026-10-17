# Audit: `mm_crypto_twap_kxbtc15m` paper result (+$220.48) and fill attribution

Date: 2026-10-17. Scope: the three paper runs of 2026-10-16 (`data` branch,
`ledger/mm_crypto_twap_kxbtc15m-20261016T{1205,1740,2316}.*`), the recorded
books/signals for `KXBTC15M-26OCT161930-30` (`recorded/kalshi/20261016/books-231*..233*`),
the engine (`pb/sim/engine.py`), paper runner (`pb/live/paper.py`), the strategy and
`QuoteManager` (`pb/strategies/base.py`), the Kalshi adapter, and the Actions run logs.

## Verdict

**Artifact. Not edge.** The +$220 is one settlement on a 440-contract short that the
strategy was never supposed to hold (its own `max_inventory` is 60, the CLI cap was
`--max-position 200`). The position was built by a `QuoteManager` bug that left dozens of
untracked ("orphan") resting orders on the book; the orders were filled by the adverse
cross-assumption, the window happened to settle NO, and the whole run is one 15-minute
window (n = 1). The sibling runs on the same code are -$2.42 (1205) and $0.00 (1740, the
selected window closed 5 minutes after start). Replaying the exact recorded data through
the pre-fix engine without the risk manager's rate limiter gives **-$2,284 on 10,551 fills**;
with the fixes it gives **+$0.49 on 116 fills, max capital $15.66**.

The cross-fill crediting itself is *not* the bug: crossings are credited at our price
(adverse), and the recorded Kalshi book for this market was two-sided, 1c wide, with
thousands of contracts at the touch while we were filled. Fills were not made against empty
levels, closed markets or settled markets in this run. Those guards were missing in the
code, though, and are now in place.

## Where the $222.90 came from (run 20261016T2316)

Ledger: `ledger/mm_crypto_twap_kxbtc15m-20261016T2316.jsonl` (72 fills, all `is_maker`,
all `assumed_cross`), summary `realized = 222.90`, final `contracts = 0`.

| time (UTC) | what | fills | net position after |
|---|---|---|---|
| 23:17:24-36 | 3 asks at 0.57/0.53 crossed (bid came up to 0.57) | 3 x 10 | -30 |
| 23:17:53 | book gapped 0.51/0.52 -> 0.47/0.48 in one 2 s poll; **23 bids** at 0.48-0.50 crossed in one tick | 23 x 10 | +200 |
| 23:18:05 | book flicked back to 0.50/0.51; **26 asks** at 0.48-0.50 (flatten-rule asks joined at the touch, size 20) crossed | 5x10 + 21x20 | -250 |
| 23:18:07 | 1 bid at 0.47 | 10 | -240 |
| 23:22:44 | 7 stale asks at 0.51/0.52 (placed 23:17:45-51, never cancelled) crossed when the bid jumped 0.41 -> 0.56 | 7 x 10 | -310 |
| 23:23:37 | 13 stale asks at 0.54 (placed 23:17:35-45) crossed when the bid jumped 0.45 -> 0.56 | 13 x 10 | -440 |
| 23:28-23:30 | market went to 0.001/none; `GET /markets/{t}` at 23:30:47 returned `result=no` -> `Settlement(0.0)` | | 0, realized +222.90 |

Average short price 0.507 vs fair ~0.50 at the time: zero captured edge; the $222.90 is
`440 x 0.507` paid out because the window settled NO. A YES settlement would have been
about -$217 (and would have tripped the $50 daily-loss halt only after the fact, since
`RiskManager.check()` marks at mid and the mid never moved far before the crash).

Risk summary for the run: `accepted 1332, rejected 2398 (rate_limit)`. The rate limiter is
the only reason the live position stopped at 440: the replay without it reaches 197k
contracts.

## Mechanism (the actual bug)

`pb/strategies/base.py::QuoteManager.set` (pre-fix) decided an order was gone when its id
was not in `api.open_orders()`. An order just placed is *in flight* for
`SimConfig.order_latency` (0.3 s) and is not in `open_orders` yet, so every `set()` call
inside that window placed a second order and forgot the first. `CryptoTwapMM._quote` is
called on every `btc_index` print (recorded ~3.8/s) plus every book poll, so each requote
spawned several duplicates; the duplicates were never cancelled (not tracked, so `pull()`
does not reach them, and `pull_before_close` did not clear them either). Reproduction
(engine, latency 0.3 s, four `set()` calls per book tick, ten ticks): 8 resting orders / 80
contracts for a quote of 10 x 10 before the fix, 2 / 20 after
(`tests/test_strategies_mm.py::test_quote_manager_no_orphans_under_latency`).

Three amplifiers:

1. `Engine._allowed` (engine.py) checked `position + this order` against
   `max_position_per_market`, not `position + resting same-side orders + this order`, so
   `--max-position 200` was meaningless with N resting orders.
2. The flatten rule in `CryptoTwapMM._quote` sizes the reducing side at `2 x size` and
   places it one tick inside the touch; with 20 orphan copies it flipped +200 to -250 in a
   single poll.
3. `Engine.cancel` popped the id after `cancel_latency` without remembering it, so an
   order cancelled before it arrived would still rest (latency ordering made this rare
   here, but it is another orphan source).

## Cross-assumed fills: correct in direction, but under-guarded

`Engine._check_cross_fills` credits a resting BUY at `p` when `best_ask <= p` and a SELL
when `best_bid >= p`, at *our* price, for the *full* remaining size. That is the adverse
case (we are filled exactly when the market has moved through us) and is what happened
here: at 23:17:51 the recorded ask fell to 0.48 with 2,773 contracts, so our bids at
0.48-0.50 would have been hit in reality too. Settlement was taken from Kalshi's
`result="no"` via `to_market -> _result_value` (correct) after `close_ts`.

What was missing (all fixed):

* No size check: a `Level(price, 0)` or a dust level (0.12 contracts, common in the last
  two minutes of these windows) could credit a 10-20 contract fill. The replay after the
  fix still shows `max_fill_to_touch_depth = 83` from exactly such dust crossings; it is
  now *measured* instead of hidden.
* No close/settled guard: books and prints after `close_ts` (Kalshi keeps serving a
  0.001-ask book after the window) could fill resting orders; `_arrive` only checked
  `settled`.
* No trade tape without an API key, so `cross_assumed_fill_frac` was 100% by
  construction and the queue model (`queue_ahead`) never did anything.

## `fill>touch inf` on `taker_lag`

`Engine._fill` read the touch size from the book *after* `_take` had already subtracted the
fill (`lvl.size -= qty` before `_fill`). Any taker fill that consumed a whole level
(fractional Kalshi levels of 0.22, 1.12 contracts in the last minutes) recorded
`touch_depth = 0` -> ratio `inf`. The 1205 run's `100.0` is the same artefact on the maker
side (depth read from the wrong side of the book). This was a measurement bug, not a
fantasy fill; taker fills were depth-limited correctly.

## Why the paper workflow is red

`gh api .../runs/38969386581/jobs`: 10 of 11 jobs succeed; `paper (mm_inventory_poly_crypto15m)`
fails in 28 s. Its log (`ledger/log-mm_inventory_poly_crypto15m-20261016T2316.txt`):
`gamma-api.polymarket.com/markets?...order=volume24hr` -> `no markets` -> `scripts/paper.py`
`return 2` -> `paper_matrix.py` propagates the exit code -> job failure -> workflow
`conclusion=failure` even though `publish` (ledgers + reports) ran with `if: always()`. Same
in run 38934862931. The `--poly-crypto-15m` selector only sees the top-300 markets by 24 h
volume; the 5/15-minute up-or-down markets are not in that page. Not a timeout
(`timeout-minutes: 360`, runs last 5.5 h) and not an exception at shutdown.

## Other findings (not fixed here)

* **One window per 5.5 h run.** `select_kalshi_markets(..., status="open", top=2)` returns
  the single open KXBTC15M window at start; the runner never rolls to the next one. The
  1740 run picked a window closing 5 min later and sat idle for 5 h 25 min. Every
  "16.7 h" of runtime in the leaderboard is ~14 minutes of quoting. Re-select every window
  (or pass `min_secs_to_close` ~ 600 and re-run selection on settlement).
* **Equity mark on one-sided books** marked at `avg_price` (engine.py `equity()`), which
  is why the summary shows `max_drawdown 198.82` on a run that never had a losing mark;
  fixed (`Engine.mark`).
* **`RiskManager` daily-loss check uses the same mid mark**, so a 440-contract position
  at fair cannot trip the $50 limit until it is already lost.
* **Polymarket crypto-15m selector** needs a slug/event-based query; left as is.
* **Cross fills are still credited for the full remaining size** even when the crossing
  level is smaller than our order. With the trade tape now feeding `queue_ahead`, consider
  capping an assumed cross at `max(crossing depth, prints seen)`; flagged, not changed.

## Code changes (this commit)

1. `pb/strategies/base.py` `QuoteManager`: tracks in-flight orders (`_placed_at`,
   `_seen`, `inflight_grace`), drops `rejected-*` ids immediately, and cancels any resting
   order carrying its strategy name that it does not track (orphan sweep) in both `set()`
   and `pull()`.
2. `pb/sim/engine.py`:
   * `_tradable()`: no cross fills, print fills or order arrivals on settled markets or
     after `close_ts`.
   * `_crossing_depth()` / `_check_cross_fills()`: a cross needs opposite-side size > 0 at
     or through our price; that depth is recorded as `touch_depth`.
   * `_take()`: `touch_depth` is the touch size *before* consumption; print fills record
     the print size; `_fill(touch_depth=...)` is explicit.
   * `_allowed()`: position cap includes resting same-side orders.
   * `cancel()`: remembers cancelled ids so an in-flight order never rests after its cancel.
   * `mark()`: settlement -> mid -> the one existing side -> avg price.
3. `pb/live/paper.py` + `pb/venues/kalshi.py`: `trade_pollers` poll
   `GET /markets/trades?ticker=&min_ts=` (`KalshiClient.trades_since`) every `poll_secs`,
   before the book, when there is no authenticated WS; prints are de-duplicated on
   `(ts, price, size, side)` and feed `_maker_fills_from_print`, so cross-assumed fills are
   the fallback, not the rule. Settled markets are no longer polled.
4. `scripts/paper.py` returns 3 for "no markets"; `scripts/paper_matrix.py` reports it as
   skipped instead of failing the workflow.
5. Tests: 13 new (`tests/test_engine.py`, `tests/test_strategies_mm.py`,
   `tests/test_data_and_paper.py`, `tests/test_kalshi.py`, `tests/test_scripts.py`); 144 pass.

## Evidence: replay of the recorded window

`python scripts/backtest.py --strategy mm_crypto_twap --params configs/mm_crypto_twap.yaml
--data <recorded 2026-10-16 23:10-23:59> --markets KXBTC15M-26OCT161930-30 --latency 0.3`
(no RiskManager in backtests):

| code | fills | contracts | net pnl | max capital | cross-assumed | max fill/touch |
|---|---|---|---|---|---|---|
| before | 10,551 | 197,263 | -$2,284.05 | $2,128.97 | 100% | 1000 |
| after | 116 | 1,354 | +$0.49 | $15.66 | 100% (no tape in the recording) | 83 |

The live +$220.48 sits between those two numbers only because the risk gate's
120 orders/min limit rejected 64% of the strategy's submissions. Treat the leaderboard
entry as void and re-run the matrix on the fixed code before reading any number from it.
