# Early Favorite auto-buyer v1 (paper)

Paper only. Reads the live Polymarket US book at 13:00 left, else 12:00 left; buys the favorite if its ask is 80-95c with a limit at ask+1c, filled only against size actually resting on the book.
Updated 2026-10-31T13:55:33Z.

Rounds watched: 719. Entries: 90. Settled: 90.

Win rate: 75/90 = 83.3%

| Stake | Full fill rate | Avg fill | Avg price | Net P&L | Per $ staked |
|---|---|---|---|---|---|
| $50 | 100% | 100% | 0.845 | $-109.96 | -2.44% |
| $100 | 100% | 100% | 0.845 | $-222.38 | -2.47% |
| $250 | 96% | 99% | 0.846 | $-609.47 | -2.74% |

Live $100 fill price minus the backtest's display price: +1.05c average over 90 entries (the backtest edge was about +4.2c, so this gap is what it must survive).

## Last 20 entries

| Window (UTC) | Left | Side | Ask | Depth at ask | $100 fill | Result | P&L $100 |
|---|---|---|---|---|---|---|---|
| 10-29T23:45 | 12:00 | Down | 0.87 | 318 | 100% @ 0.870 | WIN | +14.04 |
| 10-30T01:45 | 12:00 | Down | 0.87 | 282 | 100% @ 0.870 | WIN | +14.04 |
| 10-30T03:30 | 12:00 | Up | 0.87 | 738 | 100% @ 0.870 | WIN | +14.04 |
| 10-30T04:00 | 12:00 | Down | 0.92 | 2295 | 100% @ 0.920 | WIN | +8.14 |
| 10-30T05:00 | 12:00 | Up | 0.86 | 389 | 100% @ 0.860 | WIN | +15.31 |
| 10-30T06:45 | 12:00 | Down | 0.83 | 1004 | 100% @ 0.830 | LOSS | -101.18 |
| 10-30T07:45 | 13:00 | Up | 0.83 | 796 | 100% @ 0.830 | WIN | +19.30 |
| 10-30T10:30 | 13:00 | Up | 0.84 | 45 | 100% @ 0.846 | WIN | +17.11 |
| 10-30T13:30 | 12:00 | Down | 0.82 | 5 | 100% @ 0.830 | WIN | +19.36 |
| 10-30T14:00 | 12:00 | Down | 0.81 | 1001 | 100% @ 0.810 | WIN | +22.14 |
| 10-30T15:15 | 12:00 | Up | 0.87 | 662 | 100% @ 0.870 | LOSS | -100.90 |
| 10-30T15:45 | 12:00 | Down | 0.90 | 1795 | 100% @ 0.900 | LOSS | -100.69 |
| 10-30T18:15 | 12:00 | Down | 0.82 | 705 | 100% @ 0.820 | WIN | +20.70 |
| 10-30T20:00 | 12:00 | Up | 0.80 | 185 | 100% @ 0.800 | WIN | +23.61 |
| 10-30T22:00 | 12:00 | Up | 0.87 | 226 | 100% @ 0.870 | WIN | +14.04 |
| 10-31T04:00 | 13:00 | Up | 0.83 | 354 | 100% @ 0.830 | WIN | +19.30 |
| 10-31T06:00 | 12:00 | Up | 0.86 | 508 | 100% @ 0.860 | WIN | +15.31 |
| 10-31T06:45 | 12:00 | Up | 0.89 | 5 | 100% @ 0.899 | WIN | +10.47 |
| 10-31T10:00 | 12:00 | Down | 0.81 | 354 | 100% @ 0.810 | LOSS | -101.32 |
| 10-31T11:15 | 13:00 | Up | 0.80 | 323 | 100% @ 0.800 | WIN | +23.61 |

Book reads: 1409, failed: 410, re-tried: 339, median latency 0.04s.
Entries read more than 20 s after their target second: 11 of 90 (avg 29 s late).
