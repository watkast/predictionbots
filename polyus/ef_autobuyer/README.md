# Early Favorite auto-buyer v1 (paper)

Paper only. Reads the live Polymarket US book at 13:00 left, else 12:00 left; buys the favorite if its ask is 80-95c with a limit at ask+1c, filled only against size actually resting on the book.
Updated 2026-10-29T04:06:58Z.

Rounds watched: 496. Entries: 57. Settled: 57.

Win rate: 46/57 = 80.7%

| Stake | Full fill rate | Avg fill | Avg price | Net P&L | Per $ staked |
|---|---|---|---|---|---|
| $50 | 100% | 100% | 0.844 | $-158.21 | -5.55% |
| $100 | 100% | 100% | 0.844 | $-317.50 | -5.57% |
| $250 | 100% | 100% | 0.845 | $-806.30 | -5.66% |

Live $100 fill price minus the backtest's display price: +1.28c average over 57 entries (the backtest edge was about +4.2c, so this gap is what it must survive).

## Last 20 entries

| Window (UTC) | Left | Side | Ask | Depth at ask | $100 fill | Result | P&L $100 |
|---|---|---|---|---|---|---|---|
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
| 10-28T20:30 | 12:00 | Up | 0.84 | 108 | 100% @ 0.841 | LOSS | -101.11 |
| 10-28T21:45 | 13:00 | Up | 0.81 | 661 | 100% @ 0.810 | WIN | +22.14 |
| 10-28T22:00 | 12:00 | Down | 0.92 | 74 | 100% @ 0.923 | WIN | +7.80 |
| 10-28T22:30 | 13:00 | Up | 0.85 | 2274 | 100% @ 0.850 | WIN | +16.60 |
| 10-28T23:00 | 13:00 | Down | 0.85 | 2160 | 100% @ 0.850 | LOSS | -101.04 |

Book reads: 972, failed: 310, re-tried: 211, median latency 0.04s.
Entries read more than 20 s after their target second: 7 of 57 (avg 30 s late).
