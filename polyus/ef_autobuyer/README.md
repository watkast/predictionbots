# Early Favorite auto-buyer v1 (paper)

Paper only. Reads the live Polymarket US book at 13:00 left, else 12:00 left; buys the favorite if its ask is 80-95c with a limit at ask+1c, filled only against size actually resting on the book.
Updated 2026-11-02T01:58:01Z.

Rounds watched: 851. Entries: 109. Settled: 109.

Win rate: 91/109 = 83.5%

| Stake | Full fill rate | Avg fill | Avg price | Net P&L | Per $ staked |
|---|---|---|---|---|---|
| $50 | 100% | 100% | 0.844 | $-112.18 | -2.06% |
| $100 | 99% | 100% | 0.844 | $-236.22 | -2.18% |
| $250 | 94% | 98% | 0.845 | $-607.47 | -2.28% |

Live $100 fill price minus the backtest's display price: +1.06c average over 105 entries (the backtest edge was about +4.2c, so this gap is what it must survive).

## Last 20 entries

| Window (UTC) | Left | Side | Ask | Depth at ask | $100 fill | Result | P&L $100 |
|---|---|---|---|---|---|---|---|
| 10-31T11:15 | 13:00 | Up | 0.80 | 323 | 100% @ 0.800 | WIN | +23.61 |
| 10-31T19:15 | 12:00 | Down | 0.80 | 304 | 100% @ 0.800 | WIN | +23.61 |
| 10-31T19:45 | 13:00 | Down | 0.83 | 418 | 100% @ 0.830 | WIN | +19.30 |
| 10-31T20:00 | 12:00 | Up | 0.85 | 138 | 100% @ 0.850 | WIN | +16.60 |
| 11-01T00:00 | 13:00 | Down | 0.81 | 294 | 100% @ 0.810 | WIN | +22.14 |
| 11-01T02:45 | 12:00 | Up | 0.86 | 243 | 100% @ 0.860 | WIN | +15.31 |
| 11-01T04:00 | 12:00 | Down | 0.82 | 2121 | 100% @ 0.820 | WIN | +20.70 |
| 11-01T05:00 | 12:00 | Up | 0.80 | 788 | 100% @ 0.800 | WIN | +23.61 |
| 11-01T05:30 | 12:00 | Up | 0.87 | 157 | 100% @ 0.870 | LOSS | -100.90 |
| 11-01T05:45 | 13:00 | Up | 0.84 | 60 | 50% @ 0.840 | WIN | +9.04 |
| 11-01T07:00 | 13:00 | Down | 0.80 | 232 | 100% @ 0.800 | WIN | +23.61 |
| 11-01T07:15 | 13:00 | Down | 0.94 | 583 | 100% @ 0.940 | WIN | +5.97 |
| 11-01T08:30 | 12:00 | Up | 0.82 | 144 | 100% @ 0.820 | WIN | +20.70 |
| 11-01T11:30 | 13:00 | Down | 0.80 | 1018 | 100% @ 0.800 | WIN | +23.61 |
| 11-01T12:00 | 13:00 | Up | 0.87 | 185 | 100% @ 0.870 | WIN | +14.04 |
| 11-01T12:15 | 13:00 | Down | 0.92 | 1730 | 100% @ 0.920 | WIN | +8.14 |
| 11-01T16:15 | 12:00 | Up | 0.82 | 119 | 100% @ 0.820 | WIN | +20.66 |
| 11-01T23:30 | 12:00 | Up | 0.80 | 41 | 100% @ 0.807 | WIN | +22.62 |
| 11-02T00:00 | 12:00 | Up | 0.82 | 15 | 100% @ 0.829 | LOSS | -101.20 |
| 11-02T01:15 | 13:00 | Down | 0.80 | 3518 | 100% @ 0.800 | LOSS | -101.39 |

Book reads: 1663, failed: 490, re-tried: 447, median latency 0.04s.
Entries read more than 20 s after their target second: 15 of 109 (avg 30 s late).
