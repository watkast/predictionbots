# Early Favorite v2 - forward test

Rule (frozen): at 2:00 elapsed (13:00 left), else 3:00, buy the leading side if its ask is 0.80-0.95; $100 per round; hold to settlement; taker fee 0.0695*p*(1-p). Paper only.
Forward test started 2026-10-23T00:00:00Z. Updated 2026-10-26T00:16:52Z.

**Too early to judge: 46 of the ~150 rounds (about a week) needed.**

| | Forward | Backtest (Oct 6-22) |
|---|---|---|
| Rounds | 46 | 272 |
| Win rate | 84.8% | 89.3% |
| Break-even win rate at prices paid | 85.6% | - |
| Average ask | 0.847 | 0.838 |
| Net at $100/round | $-51.62 | $+1,486 |
| Per round | -1.12% | +5.46% |
| Max drawdown | $-332.83 | $-403 |
| Longest losing streak | 2 | 2 |
| Entry timing | 13:00 / 12:00 left | same |

Rounds where the rule did not trigger: 242. Pending (not settled or not fetched yet): 2.

## By day (UTC)

| Day | Net |
|---|---|
| 2026-10-23 | $-138.09 |
| 2026-10-24 | $-72.04 |
| 2026-10-25 | $+158.51 |

## Chart pull at the check (parallel column - not part of the rule)

Pull = EMA 9/21 and Supertrend on BRTI 1-minute candles, as drawn by research/market_pull.pine, read against the favorite. Oct 16-24 (143 rounds): 3/3 with the favorite won 92%, 1/3 won 84%, against won 78%. Small sample; this column is the forward test of that.

| Pull at the check | Rounds | Win rate | Net |
|---|---|---|---|
| with the favorite 3/3 | 35 | 88.6% | $+86.23 |
| with the favorite 1/3 | 11 | 72.7% | $-137.85 |
| against the favorite | 0 | - | $+0.00 |

## Last 20 rounds

| Window (UTC) | Min | Side | Ask | Pull | Result | P&L | Running |
|---|---|---|---|---|---|---|---|
| 10-24 13:30 | 2 | Down | 0.86 | +3 | won | $+15.31 | $-245.28 |
| 10-24 14:15 | 2 | Down | 0.93 | +3 | won | $+7.04 | $-238.24 |
| 10-24 20:00 | 2 | Up | 0.86 | +3 | won | $+15.31 | $-222.93 |
| 10-24 23:30 | 3 | Up | 0.88 | +3 | won | $+12.80 | $-210.13 |
| 10-25 00:00 | 3 | Down | 0.80 | +1 | won | $+23.61 | $-186.52 |
| 10-25 01:00 | 2 | Down | 0.82 | +3 | won | $+20.70 | $-165.82 |
| 10-25 05:45 | 2 | Down | 0.80 | +3 | LOST | $-101.39 | $-267.21 |
| 10-25 08:00 | 2 | Down | 0.80 | +3 | won | $+23.61 | $-243.60 |
| 10-25 10:45 | 2 | Down | 0.92 | +3 | won | $+8.14 | $-235.46 |
| 10-25 11:00 | 2 | Up | 0.93 | +3 | won | $+7.04 | $-228.42 |
| 10-25 11:15 | 3 | Up | 0.87 | +3 | won | $+14.04 | $-214.38 |
| 10-25 14:15 | 3 | Down | 0.85 | +3 | won | $+16.60 | $-197.78 |
| 10-25 15:00 | 3 | Up | 0.84 | +3 | won | $+17.94 | $-179.84 |
| 10-25 15:30 | 2 | Up | 0.80 | +1 | won | $+23.61 | $-156.23 |
| 10-25 16:30 | 3 | Up | 0.85 | +3 | won | $+16.60 | $-139.63 |
| 10-25 20:30 | 3 | Down | 0.83 | +3 | won | $+19.30 | $-120.33 |
| 10-25 21:30 | 3 | Down | 0.82 | +3 | won | $+20.70 | $-99.63 |
| 10-25 21:45 | 2 | Down | 0.88 | +3 | won | $+12.80 | $-86.83 |
| 10-25 22:00 | 2 | Up | 0.89 | +1 | won | $+11.60 | $-75.23 |
| 10-25 22:15 | 3 | Up | 0.80 | +1 | won | $+23.61 | $-51.62 |
