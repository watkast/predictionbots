# Early Favorite auto-buyer v1 (paper)

Paper only. Reads the live Polymarket US book at 13:00 left, else 12:00 left; buys the favorite if its ask is 80-95c with a limit at ask+1c, filled only against size actually resting on the book.
Updated 2026-11-12T17:33:54Z.

Rounds watched: 1709. Entries: 197. Settled: 197.

Win rate: 161/197 = 81.7%

| Stake | Full fill rate | Avg fill | Avg price | Net P&L | Per $ staked |
|---|---|---|---|---|---|
| $50 | 99% | 99% | 0.841 | $-423.86 | -4.34% |
| $100 | 97% | 99% | 0.842 | $-849.80 | -4.37% |
| $250 | 90% | 96% | 0.843 | $-2,169.42 | -4.61% |

Live $100 fill price minus the backtest's display price: +0.81c average over 193 entries (the backtest edge was about +4.2c, so this gap is what it must survive).

## Last 20 entries

| Window (UTC) | Left | Side | Ask | Depth at ask | $100 fill | Result | P&L $100 |
|---|---|---|---|---|---|---|---|
| 11-10T19:45 | 12:00 | Up | 0.82 | 63 | 100% @ 0.825 | WIN | +19.58 |
| 11-10T20:00 | 12:00 | Down | 0.80 | 862 | 100% @ 0.800 | LOSS | -101.90 |
| 11-10T21:00 | 13:00 | Up | 0.80 | 3460 | 100% @ 0.800 | WIN | +23.10 |
| 11-11T01:00 | 12:00 | Down | 0.83 | 980 | 100% @ 0.830 | WIN | +18.87 |
| 11-11T01:30 | 12:00 | Up | 0.81 | 80 | 100% @ 0.814 | WIN | +21.15 |
| 11-11T05:30 | 12:00 | Up | 0.80 | 180 | 100% @ 0.800 | WIN | +23.10 |
| 11-11T07:15 | 12:00 | Up | 0.85 | 1449 | 100% @ 0.850 | WIN | +16.22 |
| 11-11T08:15 | 12:00 | Down | 0.85 | 745 | 100% @ 0.850 | WIN | +16.22 |
| 11-11T12:15 | 12:00 | Up | 0.87 | 163 | 100% @ 0.870 | WIN | +13.71 |
| 11-11T23:00 | 12:00 | Up | 0.85 | 660 | 100% @ 0.850 | LOSS | -101.42 |
| 11-11T23:15 | 12:00 | Up | 0.89 | 1305 | 100% @ 0.890 | WIN | +11.31 |
| 11-12T00:15 | 12:00 | Up | 0.83 | 809 | 100% @ 0.830 | WIN | +18.87 |
| 11-12T04:30 | 12:00 | Down | 0.81 | 701 | 100% @ 0.810 | WIN | +21.65 |
| 11-12T05:00 | 13:00 | Down | 0.81 | 705 | 100% @ 0.810 | WIN | +21.65 |
| 11-12T06:00 | 12:00 | Up | 0.86 | 934 | 100% @ 0.860 | WIN | +14.95 |
| 11-12T07:00 | 13:00 | Up | 0.86 | 7 | 100% @ 0.869 | WIN | +13.78 |
| 11-12T09:00 | 13:00 | Down | 0.89 | 1254 | 100% @ 0.890 | WIN | +11.31 |
| 11-12T09:30 | 12:00 | Up | 0.83 | 65 | 100% @ 0.835 | WIN | +18.25 |
| 11-12T16:30 | 12:00 | Down | 0.88 | 1530 | 100% @ 0.880 | WIN | +12.50 |
| 11-12T16:45 | 12:00 | Up | 0.86 | 11 | 100% @ 0.869 | WIN | +13.82 |

Book reads: 3349, failed: 959, re-tried: 1042, median latency 0.04s.
Entries read more than 20 s after their target second: 22 of 197 (avg 32 s late).
