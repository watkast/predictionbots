# Early Favorite auto-buyer v1 (paper)

Paper only. Reads the live Polymarket US book at 13:00 left, else 12:00 left; buys the favorite if its ask is 80-95c with a limit at ask+1c, filled only against size actually resting on the book.
Updated 2026-10-30T14:06:31Z.

Rounds watched: 624. Entries: 80. Settled: 79.

Win rate: 67/79 = 84.8%

| Stake | Full fill rate | Avg fill | Avg price | Net P&L | Per $ staked |
|---|---|---|---|---|---|
| $50 | 100% | 100% | 0.845 | $-33.12 | -0.84% |
| $100 | 100% | 100% | 0.846 | $-68.64 | -0.87% |
| $250 | 97% | 99% | 0.847 | $-207.28 | -1.06% |

Live $100 fill price minus the backtest's display price: +1.01c average over 80 entries (the backtest edge was about +4.2c, so this gap is what it must survive).

## Last 20 entries

| Window (UTC) | Left | Side | Ask | Depth at ask | $100 fill | Result | P&L $100 |
|---|---|---|---|---|---|---|---|
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
| 10-30T03:30 | 12:00 | Up | 0.87 | 738 | 100% @ 0.870 | WIN | +14.04 |
| 10-30T04:00 | 12:00 | Down | 0.92 | 2295 | 100% @ 0.920 | WIN | +8.14 |
| 10-30T05:00 | 12:00 | Up | 0.86 | 389 | 100% @ 0.860 | WIN | +15.31 |
| 10-30T06:45 | 12:00 | Down | 0.83 | 1004 | 100% @ 0.830 | LOSS | -101.18 |
| 10-30T07:45 | 13:00 | Up | 0.83 | 796 | 100% @ 0.830 | WIN | +19.30 |
| 10-30T10:30 | 13:00 | Up | 0.84 | 45 | 100% @ 0.846 | WIN | +17.11 |
| 10-30T13:30 | 12:00 | Down | 0.82 | 5 | 100% @ 0.830 | WIN | +19.36 |
| 10-30T14:00 | 12:00 | Down | 0.81 | 1001 | 100% @ 0.810 | - | +0.00 |

Book reads: 1221, failed: 363, re-tried: 279, median latency 0.04s.
Entries read more than 20 s after their target second: 10 of 80 (avg 29 s late).
