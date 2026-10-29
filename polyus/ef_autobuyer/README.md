# Early Favorite auto-buyer v1 (paper)

Paper only. Reads the live Polymarket US book at 13:00 left, else 12:00 left; buys the favorite if its ask is 80-95c with a limit at ask+1c, filled only against size actually resting on the book.
Updated 2026-10-29T18:35:51Z.

Rounds watched: 547. Entries: 64. Settled: 63.

Win rate: 52/63 = 82.5%

| Stake | Full fill rate | Avg fill | Avg price | Net P&L | Per $ staked |
|---|---|---|---|---|---|
| $50 | 100% | 100% | 0.845 | $-109.96 | -3.49% |
| $100 | 100% | 100% | 0.845 | $-221.37 | -3.51% |
| $250 | 97% | 99% | 0.846 | $-583.34 | -3.73% |

Live $100 fill price minus the backtest's display price: +1.13c average over 60 entries (the backtest edge was about +4.2c, so this gap is what it must survive).

## Last 20 entries

| Window (UTC) | Left | Side | Ask | Depth at ask | $100 fill | Result | P&L $100 |
|---|---|---|---|---|---|---|---|
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
| 10-29T04:45 | 12:00 | Up | 0.89 | 1054 | 100% @ 0.890 | WIN | +11.60 |
| 10-29T13:00 | 13:00 | Up | 0.82 | 353 | 100% @ 0.820 | WIN | +20.70 |
| 10-29T13:15 | 13:00 | Up | 0.85 | 230 | 100% @ 0.850 | WIN | +16.60 |
| 10-29T15:30 | 12:00 | Up | 0.86 | 82 | 100% @ 0.863 | WIN | +14.94 |
| 10-29T15:45 | 12:00 | Up | 0.82 | 570 | 100% @ 0.820 | WIN | +20.70 |
| 10-29T17:45 | 12:00 | Down | 0.89 | 158 | 100% @ 0.890 | WIN | +11.60 |
| 10-29T18:30 | 13:00 | Down | 0.82 | 157 | 100% @ 0.820 | - | +0.00 |

Book reads: 1071, failed: 333, re-tried: 225, median latency 0.04s.
Entries read more than 20 s after their target second: 7 of 64 (avg 30 s late).
