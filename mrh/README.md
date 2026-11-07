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

Both: USD pairs with ≥ $100k 24-h volume, stablecoins/wrappers excluded, spread ≤ 0.6%, one position at a time,
the whole bankroll every hop (compounding), fills at the touch (ask in, bid out), no hard stop, no time stop.

**The real verdict** is the signal table, not the books: every signal is scored with its +15 m / +1 h / +4 h return,
max run-up, max drawdown and what a 4%-trail hop from it would have netted. That is independent of which coin the
single-position book was sitting in. Verdict unlocks at 40 scored aggressive signals and 30 closed aggressive hops.

## Live (real money, hard-capped)

`scripts/mrh_live.py`, run by `.github/workflows/mrh-live.yml` (335-min runs that re-dispatch themselves; the
6-hourly cron is a backstop). The **aggressive** profile with a real key — same universe, same signal, same spread
gate as paper — plus one thing paper cannot do: the 4% trailing stop is **parked on the exchange** as a stop-limit
sell (limit 1.5% under the stop) and re-parked whenever the high-water mark rises. A dump while the runner sleeps,
or in the minute between runs, hits the resting order; the bot's own market sell on the live bid every 5 minutes is
the backstop. Report: `mrh-live/LIVE.md` on the `data` branch, with `live_state.json`, `live_trades.jsonl`, `live_events.jsonl`
(its own directory: the paper job republishes all of `mrh/` every 10 minutes).

The exchange is the truth: every cycle reconciles balances, open orders and fills. A coin bought by hand is adopted
and trailed (entry = last buy fill, else the bid); a stop that filled while the bot slept is booked from its fill.

Guards: `mrh/LIVE_ON` on main and no `mrh/PAUSED` (checked every cycle); one position; 6 hops per UTC day
(`MRH_LIVE_MAX_HOPS_DAY`); $12 per entry (`MRH_LIVE_MAX_USD` — a deposit does not become bot money); halts below
$1.20 total (`MRH_LIVE_FLOOR_USD`, Coinbase's $1 minimum would strand anything smaller); never touches any asset
other than USD and the one coin it holds (dust, LOOM and friends are ignored). USDC is not bankroll — hold USD.
Keep no other open orders on the coin it holds: a hand-placed sell locks the coins and the bot's stop cannot park.

**Setup (once):** a CDP API key at Coinbase Developer Platform with **View + Trade only — no Transfer**, no IP
allowlist (Actions runners rotate IPs). Repo secrets `COINBASE_API_KEY` (the key name,
`organizations/…/apiKeys/…`) and `COINBASE_API_SECRET` (the private key; EC PEM or the newer base64 Ed25519 form —
escaped `\n` is fine). Without the secrets the workflow exits doing nothing.

**Stop:** delete `mrh/LIVE_ON` (or add `mrh/PAUSED`) on main — no new orders from the next cycle; a parked stop stays
on the exchange until it fills or you cancel it. Cancel the running job to stop at once. **Dry run:** dispatch the
workflow with mode `dry` — everything (auth, reconcile, signals) except sending orders.

**Known lies to avoid:** Coinbase's `price_percentage_change_24h` was wrong on 4 of 6 coins checked on Nov 6 —
never used, in paper or live. Paper fills at the touch; live pays the real spread and, on a thin book, real slippage —
irrelevant at $4, not at $400. Going live before the paper verdict means the live book is tuition, not evidence:
read the signal table in MRH.md, not LIVE.md, to decide whether hopping has an edge.

**Pause paper:** commit an empty `mrh/PAUSED` on main (this also stops live).
