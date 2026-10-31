# Early Favorite auto-buyer v1 (paper)

Paper only. Reads the live Polymarket US book at 13:00 left, else 12:00 left; buys the favorite if its ask is 80-95c with a limit at ask+1c, filled only against size actually resting on the book.
Updated 2026-10-31T07:31:07Z.

Rounds watched: 693. Entries: 88. Settled: 88.

Win rate: 74/88 = 84.1%

| Stake | Full fill rate | Avg fill | Avg price | Net P&L | Per $ staked |
|---|---|---|---|---|---|
| $50 | 100% | 100% | 0.846 | $-71.11 | -1.62% |
| $100 | 100% | 100% | 0.846 | $-144.67 | -1.64% |
| $250 | 95% | 99% | 0.847 | $-415.19 | -1.91% |

Live $100 fill price minus the backtest's display price: +1.08c average over 86 entries (the backtest edge was about +4.2c, so this gap is what it must survive).

## Last 20 entries

| Window (UTC) | Left | Side | Ask | Depth at ask | $100 fill | Result | P&L $100 |
|---|---|---|---|---|---|---|---|
| 10-29T21:45 | 12:00 | Down | 0.80 | 310 | 100% @ 0.800 | WIN | +23.61 |
| 10-29T23:00 | 12:00 | Down | 0.81 | 1809 | 100% @ 0.810 | WIN | +22.14 |
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

Book reads: 1358, failed: 402, re-tried: 328, median latency 0.04s.
Entries read more than 20 s after their target second: 11 of 88 (avg 29 s late).
