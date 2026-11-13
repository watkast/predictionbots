# Early Favorite auto-buyer v1 (paper)

Paper only. Reads the live Polymarket US book at 13:00 left, else 12:00 left; buys the favorite if its ask is 80-95c with a limit at ask+1c, filled only against size actually resting on the book.
Updated 2026-11-13T10:57:34Z.

Rounds watched: 1764. Entries: 205. Settled: 205.

Win rate: 167/205 = 81.5%

| Stake | Full fill rate | Avg fill | Avg price | Net P&L | Per $ staked |
|---|---|---|---|---|---|
| $50 | 99% | 99% | 0.841 | $-466.81 | -4.59% |
| $100 | 98% | 99% | 0.841 | $-935.71 | -4.62% |
| $250 | 90% | 96% | 0.842 | $-2,404.94 | -4.91% |

Live $100 fill price minus the backtest's display price: +0.70c average over 201 entries (the backtest edge was about +4.2c, so this gap is what it must survive).

## Last 20 entries

| Window (UTC) | Left | Side | Ask | Depth at ask | $100 fill | Result | P&L $100 |
|---|---|---|---|---|---|---|---|
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
| 11-12T20:45 | 12:00 | Up | 0.80 | 1670 | 100% @ 0.800 | LOSS | -101.90 |
| 11-12T21:15 | 12:00 | Up | 0.80 | 771 | 100% @ 0.800 | WIN | +23.10 |
| 11-13T00:45 | 12:00 | Up | 0.87 | 755 | 100% @ 0.870 | WIN | +13.71 |
| 11-13T01:15 | 13:00 | Up | 0.83 | 861 | 100% @ 0.830 | WIN | +18.87 |
| 11-13T02:30 | 12:00 | Down | 0.81 | 0 | 100% @ 0.820 | WIN | +20.24 |
| 11-13T07:30 | 12:00 | Down | 0.80 | 1358 | 100% @ 0.800 | WIN | +23.10 |
| 11-13T09:30 | 12:00 | Up | 0.83 | 446 | 100% @ 0.830 | WIN | +18.87 |
| 11-13T09:45 | 12:00 | Down | 0.80 | 539 | 100% @ 0.800 | LOSS | -101.90 |

Book reads: 3458, failed: 970, re-tried: 1058, median latency 0.04s.
Entries read more than 20 s after their target second: 22 of 205 (avg 32 s late).
