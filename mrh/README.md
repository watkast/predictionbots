# Mr. H — the Coinbase hopper (paper)

**Question:** can $4 hop between coins that are pumping *right now* on Coinbase Advanced and grow, after the
real 0.9% taker fee each way (1.8% per hop)?

**How:** `scripts/mrh_paper.py`, run by `.github/workflows/mrh-paper.yml` (hourly cron, each run scans for ~5.6 h).
Public endpoints only — no API key exists for this bot. Results on the `data` branch: `mrh/MRH.md` (the report),
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

**Known lies to avoid:** Coinbase's `price_percentage_change_24h` was wrong on 4 of 6 coins checked on Nov 6 —
never used. The trailing stop is evaluated on the live bid every 5 minutes, so a dump inside a 5-minute window is
exited late; a real $4 bot on a websocket would do better *and* worse (more whipsaws). Stops are conservative
(fire on the observed price, no intrabar fills).

**Pause:** commit an empty `mrh/PAUSED` on main.
