# Early Favorite auto-buyer v1 (paper)

Paper only. Reads the live Polymarket US book at 13:00 left, else 12:00 left; buys the favorite if its ask is 80-95c with a limit at ask+1c, filled only against size actually resting on the book.
Updated 2026-11-04T04:47:49Z.

Rounds watched: 1028. Entries: 130. Settled: 130.

Win rate: 107/130 = 82.3%

| Stake | Full fill rate | Avg fill | Avg price | Net P&L | Per $ staked |
|---|---|---|---|---|---|
| $50 | 99% | 99% | 0.844 | $-240.42 | -3.72% |
| $100 | 98% | 99% | 0.844 | $-496.14 | -3.86% |
| $250 | 92% | 97% | 0.845 | $-1,237.03 | -3.93% |

Live $100 fill price minus the backtest's display price: +1.25c average over 127 entries (the backtest edge was about +4.2c, so this gap is what it must survive).

## Last 20 entries

| Window (UTC) | Left | Side | Ask | Depth at ask | $100 fill | Result | P&L $100 |
|---|---|---|---|---|---|---|---|
| 11-02T07:00 | 12:00 | Up | 0.83 | 5 | 100% @ 0.840 | LOSS | -101.12 |
| 11-02T07:45 | 12:00 | Down | 0.81 | 184 | 100% @ 0.810 | LOSS | -101.32 |
| 11-02T10:00 | 12:00 | Down | 0.83 | 738 | 100% @ 0.830 | WIN | +19.30 |
| 11-02T11:45 | 12:00 | Down | 0.86 | 1398 | 100% @ 0.860 | WIN | +15.31 |
| 11-02T13:15 | 12:00 | Down | 0.81 | 190 | 100% @ 0.810 | WIN | +22.14 |
| 11-02T14:30 | 12:00 | Up | 0.87 | 962 | 100% @ 0.870 | WIN | +14.04 |
| 11-02T17:45 | 13:00 | Down | 0.80 | 106 | 100% @ 0.801 | LOSS | -101.37 |
| 11-02T22:15 | 13:00 | Up | 0.88 | 136 | 100% @ 0.880 | WIN | +12.80 |
| 11-02T22:45 | 12:00 | Up | 0.83 | 720 | 100% @ 0.830 | WIN | +19.30 |
| 11-02T23:00 | 13:00 | Down | 0.91 | 87 | 100% @ 0.912 | WIN | +9.03 |
| 11-03T00:15 | 13:00 | Up | 0.82 | 119 | 100% @ 0.820 | WIN | +20.67 |
| 11-03T03:45 | 12:00 | Up | 0.93 | 1351 | 100% @ 0.930 | WIN | +7.04 |
| 11-03T04:30 | 12:00 | Down | 0.82 | 9 | 100% @ 0.829 | WIN | +19.40 |
| 11-03T06:15 | 12:00 | Up | 0.86 | 207 | 100% @ 0.860 | WIN | +15.31 |
| 11-03T06:45 | 12:00 | Down | 0.83 | 582 | 100% @ 0.830 | WIN | +19.30 |
| 11-03T12:00 | 13:00 | Down | 0.84 | 638 | 100% @ 0.840 | LOSS | -101.11 |
| 11-03T13:30 | 13:00 | Up | 0.82 | 5 | 16% @ 0.827 | WIN | +3.09 |
| 11-03T14:00 | 12:00 | Down | 0.82 | 1388 | 100% @ 0.820 | WIN | +20.70 |
| 11-03T21:45 | 12:00 | Down | 0.82 | 1475 | 100% @ 0.820 | WIN | +20.70 |
| 11-04T03:00 | 12:00 | Down | 0.92 | 1092 | 100% @ 0.920 | WIN | +8.14 |

Book reads: 2010, failed: 603, re-tried: 590, median latency 0.04s.
Entries read more than 20 s after their target second: 18 of 130 (avg 31 s late).
