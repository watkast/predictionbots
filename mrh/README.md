# Mr. H — the Coinbase hopper

**Question:** can $4 hop between coins that are pumping *right now* on Coinbase Advanced and grow, after the
real 0.9% taker fee each way (1.8% per hop)?

## Paper (the verdict)

`scripts/mrh_paper.py`, run by `.github/workflows/mrh-paper.yml` (hourly cron, each run scans for ~5.6 h).
Public endpoints only — no API key. Results on the `data` branch: `mrh/MRH.md` (the report),
`mrh/state.json`, `mrh/trades.jsonl`, `mrh/signals.jsonl`.

| profile | entry | exit |
|---|---|---|
| **aggressive** (the one Noah wants) | one 5-min candle ≥ +2% on ≥ 3× the 2-h median volume | 4% trailing stop from the high-water mark, nothing else |
| **standard** (control) | same, and the candle must close above the prior 2-h high | 3% trail |
| **aggressive_swap** (variant) | aggressive's own signals (logs none of its own) | 4% trail, **and** a coin that has made no new high for 2 h is sold at the bid to take a fresh signal in another coin |

Both: USD pairs with ≥ $100k 24-h volume, stablecoins/wrappers excluded, spread ≤ 0.6%, one position at a time,
the whole bankroll every hop (compounding), fills at the touch (ask in, bid out), no hard stop, no time stop.

**The real verdict** is the signal table, not the books: every signal is scored with its +15 m / +1 h / +4 h return,
max run-up, max drawdown and what a 4%-trail hop from it would have netted. That is independent of which coin the
single-position book was sitting in. Verdict unlocks at 40 scored aggressive signals and 30 closed aggressive hops.
Every signal is also stamped with `hour_utc` and BTC's own 1-h / 2-h move at that moment (`btc_1h`, `btc_2h`); the
report breaks aggressive signals down by BTC regime, because an alt breakout into a market-wide dump is a different
bet from one with a bid under the market. If the regime rows diverge, a BTC gate goes into live; not before.

## Backtest (the same verdict, in minutes)

`scripts/mrh_backtest.py`, run by `.github/workflows/mrh-backtest.yml` (dispatch by hand; `days` default 30,
`top` 0 = whole universe). Replays the signal rule over Coinbase's 5-minute history for every coin in the universe
with the **same** `evaluate` / `forward_score` / `trail_pnl` as paper and live — public endpoints, no key, no orders —
and scores every signal the way the paper table does, plus the net of a hop at a 3 / 4 / 6 / 8 / 12 % trail, a
*continuation* entry (wait one candle, enter only if it held), BTC's 1-h / 2-h regime at the signal, the hour, and a
`fresh` flag (first signal of a spike; the rest are the same event). Verdict in plain words at the top of the
report: `mrh-backtest/BACKTEST.md` on the `data` branch, and the run's Summary page. Paper scores one to three
aggressive signals a day, so this is how the 40-signal question gets answered this week instead of next month.

What it cannot see: the live spread gate (needs a live ticker) — subtract up to 0.6% a hop — and intrabar stop fills
(stops fire on candle closes). Coinbase omits 5-minute candles with no trades, so the thinnest coins' "4 hours" can
be longer.

## Live (real money, hard-capped, maker on every order)

`scripts/mrh_live.py`, run by `.github/workflows/mrh-live.yml` (335-min runs that re-dispatch themselves; the
6-hourly cron is a backstop). The **aggressive** profile with a real key — same universe, same signal, same spread
gate as paper — and **every order is a post-only limit order** (maker 0.5% instead of taker 0.9%: a 1.0% round trip
instead of 1.8%, which on Nov 7 was the entire difference between break-even and the day's loss):

- **Entry:** a post-only buy rests at the best bid for the whole bankroll. If the bid runs away it is re-priced up to
  the bid, never above the signal close × (1 + `MRH_LIVE_ENTRY_CHASE`, 2%); unfilled after `MRH_LIVE_ENTRY_TTL_MIN`
  (15) minutes it is cancelled. We fill on the give-back or we pass — never chase a spike at the ask.
- **Exit:** the 4% trail is watched every `MRH_LIVE_FAST_S` (20) seconds. When the bid touches it (two ticks in a
  row, or one tick 1% under), a post-only sell is posted at the ask and chased *down* to the new ask whenever the
  market leaves it behind. Partial fills are aggregated; the hop books when the last share goes.
- **Two optional exceptions** (the only taker-able orders): a stop-limit parked `MRH_LIVE_DISASTER_GAP` (6%) *under*
  the trail for the minutes nobody is watching between runs (0 parks nothing), and a market **panic** sell if the bid
  is `MRH_LIVE_PANIC_GAP` (3%) under the trail while the maker exit is still resting (0 = never take, unbounded).
- **Swap:** the stale coin is sold maker; the fresh signal is bought (maker) once the sell fills, if it is still
  fresh (15 min) and its spread still passes.

Report: `mrh-live/LIVE.md` on the `data` branch, with `live_state.json`, `live_trades.jsonl`, `live_events.jsonl`
(its own directory). Every hop shows its fee and whether it was maker, mixed or taker. Deposits and withdrawals are
detected and shown separately from P&L.

The exchange is the truth: every cycle reconciles balances, open orders and fills. A coin bought by hand is adopted
and trailed (entry = last buy fill, else the bid); a sell that filled while the bot slept is booked from its fill.

Guards: `mrh/LIVE_ON` on main and no `mrh/PAUSED` (checked every cycle); one position or one resting buy; 6 hops per
UTC day (`MRH_LIVE_MAX_HOPS_DAY`); $200 per entry (`MRH_LIVE_MAX_USD` — the stack goes in whole, up to this); halts
below $1.20 total (`MRH_LIVE_FLOOR_USD`, Coinbase's $1 minimum would strand anything smaller); never touches any
asset other than USD and the one coin it holds (dust, LOOM and friends are ignored). USDC is not bankroll — hold USD.
Keep no other open orders on the coin it holds: a hand-placed sell locks the coins and the bot's orders cannot post.

**Setup (once):** a CDP API key at Coinbase Developer Platform with **View + Trade only — no Transfer**, no IP
allowlist (Actions runners rotate IPs). Repo secrets `COINBASE_API_KEY` (the key name,
`organizations/…/apiKeys/…`) and `COINBASE_API_SECRET` (the private key; EC PEM or the newer base64 Ed25519 form —
escaped `\n` is fine). Without the secrets the workflow exits doing nothing.

**Stop:** delete `mrh/LIVE_ON` (or add `mrh/PAUSED`) on main — no new orders from the next cycle; a resting sell or
parked stop stays on the exchange until it fills or you cancel it. Cancel the running job to stop at once. **Dry run:** dispatch the
workflow with mode `dry` — everything (auth, reconcile, signals) except sending orders.

**Known lies to avoid:** Coinbase's `price_percentage_change_24h` was wrong on 4 of 6 coins checked on Nov 6 —
never used, in paper or live. Paper fills at the touch; live pays the real spread and, on a thin book, real slippage —
irrelevant at $4, not at $400. Going live before the paper verdict means the live book is tuition, not evidence:
read the signal table in MRH.md, not LIVE.md, to decide whether hopping has an edge.

**Pause paper:** commit an empty `mrh/PAUSED` on main (this also stops live).
