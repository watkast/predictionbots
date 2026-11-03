# Early Favorite auto-buyer v1 (paper)

Paper only. Reads the live Polymarket US book at 13:00 left, else 12:00 left; buys the favorite if its ask is 80-95c with a limit at ask+1c, filled only against size actually resting on the book.
Updated 2026-11-03T05:16:55Z.

Rounds watched: 951. Entries: 123. Settled: 123.

Win rate: 101/123 = 82.1%

| Stake | Full fill rate | Avg fill | Avg price | Net P&L | Per $ staked |
|---|---|---|---|---|---|
| $50 | 100% | 100% | 0.844 | $-235.02 | -3.82% |
| $100 | 99% | 100% | 0.844 | $-482.26 | -3.94% |
| $250 | 93% | 98% | 0.845 | $-1,196.79 | -3.99% |

Live $100 fill price minus the backtest's display price: +1.35c average over 118 entries (the backtest edge was about +4.2c, so this gap is what it must survive).

## Last 20 entries

| Window (UTC) | Left | Side | Ask | Depth at ask | $100 fill | Result | P&L $100 |
|---|---|---|---|---|---|---|---|
| 11-01T12:00 | 13:00 | Up | 0.87 | 185 | 100% @ 0.870 | WIN | +14.04 |
| 11-01T12:15 | 13:00 | Down | 0.92 | 1730 | 100% @ 0.920 | WIN | +8.14 |
| 11-01T16:15 | 12:00 | Up | 0.82 | 119 | 100% @ 0.820 | WIN | +20.66 |
| 11-01T23:30 | 12:00 | Up | 0.80 | 41 | 100% @ 0.807 | WIN | +22.62 |
| 11-02T00:00 | 12:00 | Up | 0.82 | 15 | 100% @ 0.829 | LOSS | -101.20 |
| 11-02T01:15 | 13:00 | Down | 0.80 | 3518 | 100% @ 0.800 | LOSS | -101.39 |
| 11-02T03:45 | 12:00 | Up | 0.82 | 458 | 100% @ 0.820 | LOSS | -101.25 |
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

Book reads: 1859, failed: 557, re-tried: 531, median latency 0.04s.
Entries read more than 20 s after their target second: 17 of 123 (avg 31 s late).
