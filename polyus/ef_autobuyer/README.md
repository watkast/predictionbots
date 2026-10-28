# Early Favorite auto-buyer v1 (paper)

Paper only. Reads the live Polymarket US book at 13:00 left, else 12:00 left; buys the favorite if its ask is 80-95c with a limit at ask+1c, filled only against size actually resting on the book.
Updated 2026-10-28T02:07:28Z.

Rounds watched: 394. Entries: 42. Settled: 42.

Win rate: 35/42 = 83.3%

| Stake | Full fill rate | Avg fill | Avg price | Net P&L | Per $ staked |
|---|---|---|---|---|---|
| $50 | 100% | 100% | 0.839 | $-38.29 | -1.82% |
| $100 | 100% | 100% | 0.840 | $-77.33 | -1.84% |
| $250 | 100% | 100% | 0.841 | $-203.88 | -1.94% |

Live $100 fill price minus the backtest's display price: +0.79c average over 42 entries (the backtest edge was about +4.2c, so this gap is what it must survive).

## Last 20 entries

| Window (UTC) | Left | Side | Ask | Depth at ask | $100 fill | Result | P&L $100 |
|---|---|---|---|---|---|---|---|
| 10-26T14:45 | 12:00 | Up | 0.81 | 1296 | 100% @ 0.810 | WIN | +22.14 |
| 10-26T20:00 | 13:00 | Down | 0.81 | 3035 | 100% @ 0.810 | WIN | +22.14 |
| 10-26T20:30 | 12:00 | Up | 0.83 | 2465 | 100% @ 0.830 | LOSS | -101.18 |
| 10-26T21:00 | 12:00 | Up | 0.91 | 652 | 100% @ 0.910 | WIN | +9.26 |
| 10-26T23:00 | 12:00 | Down | 0.88 | 1836 | 100% @ 0.880 | WIN | +12.80 |
| 10-27T05:00 | 12:00 | Up | 0.83 | 1158 | 100% @ 0.830 | WIN | +19.30 |
| 10-27T05:45 | 12:00 | Up | 0.87 | 1435 | 100% @ 0.870 | WIN | +14.04 |
| 10-27T06:00 | 12:00 | Down | 0.81 | 116 | 100% @ 0.811 | WIN | +22.05 |
| 10-27T06:15 | 12:00 | Down | 0.80 | 89 | 100% @ 0.803 | WIN | +23.18 |
| 10-27T06:30 | 12:00 | Up | 0.83 | 205 | 100% @ 0.830 | LOSS | -101.18 |
| 10-27T07:15 | 12:00 | Up | 0.85 | 173 | 100% @ 0.850 | WIN | +16.60 |
| 10-27T07:45 | 12:00 | Up | 0.83 | 723 | 100% @ 0.830 | WIN | +19.30 |
| 10-27T10:45 | 13:00 | Up | 0.92 | 124 | 100% @ 0.920 | WIN | +8.14 |
| 10-27T11:00 | 13:00 | Up | 0.86 | 1437 | 100% @ 0.860 | WIN | +15.31 |
| 10-27T12:15 | 13:00 | Up | 0.80 | 2088 | 100% @ 0.800 | WIN | +23.61 |
| 10-27T14:00 | 13:00 | Down | 0.80 | 1848 | 100% @ 0.800 | LOSS | -101.39 |
| 10-27T16:15 | 12:00 | Up | 0.86 | 2685 | 100% @ 0.860 | WIN | +15.31 |
| 10-27T19:00 | 12:00 | Up | 0.84 | 1949 | 100% @ 0.840 | WIN | +17.94 |
| 10-27T21:30 | 13:00 | Up | 0.84 | 142 | 100% @ 0.840 | WIN | +17.94 |
| 10-27T22:15 | 12:00 | Up | 0.81 | 615 | 100% @ 0.810 | WIN | +22.14 |

Book reads: 778, failed: 263, re-tried: 144, median latency 0.04s.
Entries read more than 20 s after their target second: 5 of 42 (avg 29 s late).
