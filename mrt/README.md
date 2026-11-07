# Mr. T — the terminal sniper

**Question:** in Polymarket US crypto Up/Down markets, the winning side is still offered below $1 in the final seconds
(Mr. P's recorder, Nov 4–7: 168 moments in 3.9 days, median ask 86¢, 10–1,200 contracts). Settlement is the 60-second
average of the CF Benchmarks index, which is all but locked by then — every one of the 7 historical flips needed the
remaining prints to move the index by under 1.5 bps per second. Are those asks **hittable**? Only a live order can say.

**What it does** (`scripts/mrt_sniper.py`, workflow `mrt-live.yml`, report `mrt/MRT.md` on the `mrp-data` branch):
every 100 ms, for each 5- and 15-minute BTC/ETH/SOL/XRP market in its last 5 s — if ≥ 52 of the 60 settlement prints are
in, the leader is clear and the remaining prints would have to average ≥ 6 bps away from the last one to flip it, and the
leader is offered at ≤ 90¢ with ≥ 5 contracts on the live book — send ONE immediate-or-cancel buy for up to 10 contracts
at that ask (one retry if it filled nothing and still qualifies). Hold to settlement. Fees are the exchange's
0.0695·p·(1−p): ~0.3% at 95¢, ~1.4% at 73¢.

**Read the report like this:** *fill rate* is the experiment. The data says the asks exist; only fills say they were real.
A loss at these margins is a logic error (index, leader, or timing), not variance — two in a row halt the bot.

**Caps:** 10 contracts a trade, 60 trades a UTC day, halt on 2 straight losses. Only IOC orders — nothing ever rests, so
cancelling the job leaves nothing on the book. Dials (repo variables): `MRT_SNIPE_T`, `MRT_MIN_MOVE_BPS`, `MRT_MAX_ASK`,
`MRT_MAX_QTY`, `MRT_MIN_QTY`, `MRT_MAX_TRADES_DAY`, `MRT_HALT_LOSSES`.

**Switch:** `mrt/LIVE_ON` on main (checked every minute). **Dry run:** dispatch the workflow with mode `dry` — feeds and
gate only, logs `would_fire` — a free count of live opportunities. Secrets: the repo's existing `POLYMARKET_KEY_ID` /
`POLYMARKET_SECRET_KEY` (orders + book) and `KALSHI_KEY_ID` / `KALSHI_PRIVATE_KEY_PEM` (the index prints).

Where it came from: `mrp/README.md`, `mrp/REPORT.md` and `mrp/windows.csv` on the `mrp-data` branch.
