# Early Favorite auto-buyer v1 (paper)

Paper only. Reads the live Polymarket US book at 13:00 left, else 12:00 left; buys the favorite if its ask is 80-95c with a limit at ask+1c, filled only against size actually resting on the book.
Updated 2026-11-02T23:07:19Z.

Rounds watched: 929. Entries: 120. Settled: 119.

Win rate: 97/119 = 81.5%

| Stake | Full fill rate | Avg fill | Avg price | Net P&L | Per $ staked |
|---|---|---|---|---|---|
| $50 | 100% | 100% | 0.843 | $-263.28 | -4.42% |
| $100 | 99% | 100% | 0.843 | $-538.40 | -4.54% |
| $250 | 92% | 97% | 0.844 | $-1,333.59 | -4.60% |

Live $100 fill price minus the backtest's display price: +1.05c average over 114 entries (the backtest edge was about +4.2c, so this gap is what it must survive).

## Last 20 entries

| Window (UTC) | Left | Side | Ask | Depth at ask | $100 fill | Result | P&L $100 |
|---|---|---|---|---|---|---|---|
| 11-01T07:15 | 13:00 | Down | 0.94 | 583 | 100% @ 0.940 | WIN | +5.97 |
| 11-01T08:30 | 12:00 | Up | 0.82 | 144 | 100% @ 0.820 | WIN | +20.70 |
| 11-01T11:30 | 13:00 | Down | 0.80 | 1018 | 100% @ 0.800 | WIN | +23.61 |
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
| 11-02T23:00 | 13:00 | Down | 0.91 | 87 | 100% @ 0.912 | - | +0.00 |

Book reads: 1816, failed: 538, re-tried: 505, median latency 0.04s.
Entries read more than 20 s after their target second: 16 of 120 (avg 31 s late).
