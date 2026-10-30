# Early Favorite auto-buyer v1 (paper)

Paper only. Reads the live Polymarket US book at 13:00 left, else 12:00 left; buys the favorite if its ask is 80-95c with a limit at ask+1c, filled only against size actually resting on the book.
Updated 2026-10-30T03:08:11Z.

Rounds watched: 580. Entries: 72. Settled: 72.

Win rate: 61/72 = 84.7%

| Stake | Full fill rate | Avg fill | Avg price | Net P&L | Per $ staked |
|---|---|---|---|---|---|
| $50 | 100% | 100% | 0.845 | $-29.44 | -0.82% |
| $100 | 100% | 100% | 0.845 | $-60.71 | -0.84% |
| $250 | 97% | 99% | 0.846 | $-186.61 | -1.04% |

Live $100 fill price minus the backtest's display price: +0.98c average over 71 entries (the backtest edge was about +4.2c, so this gap is what it must survive).

## Last 20 entries

| Window (UTC) | Left | Side | Ask | Depth at ask | $100 fill | Result | P&L $100 |
|---|---|---|---|---|---|---|---|
| 10-28T20:30 | 12:00 | Up | 0.84 | 108 | 100% @ 0.841 | LOSS | -101.11 |
| 10-28T21:45 | 13:00 | Up | 0.81 | 661 | 100% @ 0.810 | WIN | +22.14 |
| 10-28T22:00 | 12:00 | Down | 0.92 | 74 | 100% @ 0.923 | WIN | +7.80 |
| 10-28T22:30 | 13:00 | Up | 0.85 | 2274 | 100% @ 0.850 | WIN | +16.60 |
| 10-28T23:00 | 13:00 | Down | 0.85 | 2160 | 100% @ 0.850 | LOSS | -101.04 |
| 10-29T04:45 | 12:00 | Up | 0.89 | 1054 | 100% @ 0.890 | WIN | +11.60 |
| 10-29T13:00 | 13:00 | Up | 0.82 | 353 | 100% @ 0.820 | WIN | +20.70 |
| 10-29T13:15 | 13:00 | Up | 0.85 | 230 | 100% @ 0.850 | WIN | +16.60 |
| 10-29T15:30 | 12:00 | Up | 0.86 | 82 | 100% @ 0.863 | WIN | +14.94 |
| 10-29T15:45 | 12:00 | Up | 0.82 | 570 | 100% @ 0.820 | WIN | +20.70 |
| 10-29T17:45 | 12:00 | Down | 0.89 | 158 | 100% @ 0.890 | WIN | +11.60 |
| 10-29T18:30 | 13:00 | Down | 0.82 | 157 | 100% @ 0.820 | WIN | +20.70 |
| 10-29T19:30 | 12:00 | Up | 0.86 | 1047 | 100% @ 0.860 | WIN | +15.31 |
| 10-29T20:00 | 13:00 | Down | 0.85 | 132 | 100% @ 0.850 | WIN | +16.60 |
| 10-29T20:45 | 12:00 | Down | 0.86 | 81 | 100% @ 0.863 | WIN | +14.92 |
| 10-29T21:15 | 12:00 | Up | 0.83 | 608 | 100% @ 0.830 | WIN | +19.30 |
| 10-29T21:45 | 12:00 | Down | 0.80 | 310 | 100% @ 0.800 | WIN | +23.61 |
| 10-29T23:00 | 12:00 | Down | 0.81 | 1809 | 100% @ 0.810 | WIN | +22.14 |
| 10-29T23:45 | 12:00 | Down | 0.87 | 318 | 100% @ 0.870 | WIN | +14.04 |
| 10-30T01:45 | 12:00 | Down | 0.87 | 282 | 100% @ 0.870 | WIN | +14.04 |

Book reads: 1135, failed: 346, re-tried: 243, median latency 0.04s.
Entries read more than 20 s after their target second: 7 of 72 (avg 30 s late).
