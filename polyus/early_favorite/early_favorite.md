# Early Favorite v2 - forward test

Rule (frozen): at 2:00 elapsed (13:00 left), else 3:00, buy the leading side if its ask is 0.80-0.95; $100 per round; hold to settlement; taker fee 0.0695*p*(1-p). Paper only.
Forward test started 2026-10-23T00:00:00Z. Updated 2026-10-24T23:12:23Z.

**Too early to judge: 29 of the ~150 rounds (about a week) needed.**

| | Forward | Backtest (Oct 6-22) |
|---|---|---|
| Rounds | 29 | 272 |
| Win rate | 79.3% | 89.3% |
| Break-even win rate at prices paid | 85.7% | - |
| Average ask | 0.848 | 0.838 |
| Net at $100/round | $-222.93 | $+1,486 |
| Per round | -7.69% | +5.46% |
| Max drawdown | $-332.83 | $-403 |
| Longest losing streak | 2 | 2 |
| Entry timing | 13:00 / 12:00 left | same |

Rounds where the rule did not trigger: 159. Pending (not settled or not fetched yet): 1.

## By day (UTC)

| Day | Net |
|---|---|
| 2026-10-23 | $-138.09 |
| 2026-10-24 | $-84.84 |

## Last 20 rounds

| Window (UTC) | Min | Side | Ask | Result | P&L | Running |
|---|---|---|---|---|---|---|
| 10-23 06:00 | 2 | Down | 0.85 | LOST | $-101.04 | $-174.61 |
| 10-23 07:00 | 3 | Down | 0.88 | won | $+12.80 | $-161.81 |
| 10-23 07:30 | 2 | Up | 0.80 | LOST | $-101.39 | $-263.20 |
| 10-23 08:15 | 2 | Up | 0.87 | won | $+14.04 | $-249.16 |
| 10-23 11:00 | 3 | Down | 0.84 | won | $+17.94 | $-231.22 |
| 10-23 14:15 | 2 | Down | 0.90 | won | $+10.42 | $-220.80 |
| 10-23 16:30 | 2 | Up | 0.80 | won | $+23.61 | $-197.19 |
| 10-23 18:45 | 3 | Down | 0.84 | won | $+17.94 | $-179.25 |
| 10-23 22:30 | 2 | Down | 0.90 | won | $+10.42 | $-168.83 |
| 10-23 22:45 | 3 | Down | 0.84 | won | $+17.94 | $-150.89 |
| 10-23 23:45 | 3 | Up | 0.88 | won | $+12.80 | $-138.09 |
| 10-24 01:15 | 2 | Up | 0.81 | won | $+22.14 | $-115.95 |
| 10-24 04:00 | 3 | Up | 0.80 | LOST | $-101.39 | $-217.34 |
| 10-24 07:00 | 3 | Up | 0.82 | won | $+20.70 | $-196.64 |
| 10-24 09:30 | 3 | Up | 0.82 | LOST | $-101.25 | $-297.89 |
| 10-24 10:30 | 3 | Up | 0.85 | won | $+16.60 | $-281.29 |
| 10-24 12:15 | 3 | Up | 0.82 | won | $+20.70 | $-260.59 |
| 10-24 13:30 | 2 | Down | 0.86 | won | $+15.31 | $-245.28 |
| 10-24 14:15 | 2 | Down | 0.93 | won | $+7.04 | $-238.24 |
| 10-24 20:00 | 2 | Up | 0.86 | won | $+15.31 | $-222.93 |
