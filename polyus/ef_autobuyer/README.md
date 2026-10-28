# Early Favorite auto-buyer v1 (paper)

Paper only. Reads the live Polymarket US book at 13:00 left, else 12:00 left; buys the favorite if its ask is 80-95c with a limit at ask+1c, filled only against size actually resting on the book.
Updated 2026-10-28T20:40:57Z.

Rounds watched: 467. Entries: 53. Settled: 52.

Win rate: 43/52 = 82.7%

| Stake | Full fill rate | Avg fill | Avg price | Net P&L | Per $ staked |
|---|---|---|---|---|---|
| $50 | 100% | 100% | 0.843 | $-80.57 | -3.10% |
| $100 | 100% | 100% | 0.843 | $-161.88 | -3.11% |
| $250 | 100% | 100% | 0.844 | $-416.23 | -3.20% |

Live $100 fill price minus the backtest's display price: +1.31c average over 49 entries (the backtest edge was about +4.2c, so this gap is what it must survive).

## Last 20 entries

| Window (UTC) | Left | Side | Ask | Depth at ask | $100 fill | Result | P&L $100 |
|---|---|---|---|---|---|---|---|
| 10-27T07:45 | 12:00 | Up | 0.83 | 723 | 100% @ 0.830 | WIN | +19.30 |
| 10-27T10:45 | 13:00 | Up | 0.92 | 124 | 100% @ 0.920 | WIN | +8.14 |
| 10-27T11:00 | 13:00 | Up | 0.86 | 1437 | 100% @ 0.860 | WIN | +15.31 |
| 10-27T12:15 | 13:00 | Up | 0.80 | 2088 | 100% @ 0.800 | WIN | +23.61 |
| 10-27T14:00 | 13:00 | Down | 0.80 | 1848 | 100% @ 0.800 | LOSS | -101.39 |
| 10-27T16:15 | 12:00 | Up | 0.86 | 2685 | 100% @ 0.860 | WIN | +15.31 |
| 10-27T19:00 | 12:00 | Up | 0.84 | 1949 | 100% @ 0.840 | WIN | +17.94 |
| 10-27T21:30 | 13:00 | Up | 0.84 | 142 | 100% @ 0.840 | WIN | +17.94 |
| 10-27T22:15 | 12:00 | Up | 0.81 | 615 | 100% @ 0.810 | WIN | +22.14 |
| 10-28T04:30 | 13:00 | Up | 0.81 | 1020 | 100% @ 0.810 | WIN | +22.14 |
| 10-28T07:45 | 13:00 | Up | 0.85 | 758 | 100% @ 0.850 | WIN | +16.60 |
| 10-28T08:00 | 12:00 | Up | 0.89 | 935 | 100% @ 0.890 | WIN | +11.60 |
| 10-28T08:45 | 13:00 | Down | 0.89 | 686 | 100% @ 0.890 | WIN | +11.60 |
| 10-28T13:45 | 12:00 | Down | 0.93 | 1850 | 100% @ 0.930 | WIN | +7.04 |
| 10-28T14:15 | 12:00 | Down | 0.83 | 1092 | 100% @ 0.830 | WIN | +19.30 |
| 10-28T15:30 | 13:00 | Down | 0.89 | 180 | 100% @ 0.890 | WIN | +11.60 |
| 10-28T18:00 | 12:00 | Up | 0.81 | 5 | 100% @ 0.820 | LOSS | -101.25 |
| 10-28T18:45 | 13:00 | Down | 0.84 | 302 | 100% @ 0.840 | WIN | +17.94 |
| 10-28T20:00 | 13:00 | Up | 0.84 | 89 | 100% @ 0.843 | LOSS | -101.09 |
| 10-28T20:30 | 12:00 | Up | 0.84 | 108 | 100% @ 0.841 | - | +0.00 |

Book reads: 917, failed: 296, re-tried: 192, median latency 0.04s.
Entries read more than 20 s after their target second: 7 of 53 (avg 30 s late).
