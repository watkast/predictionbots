# Early Favorite v2 - forward test

Rule (frozen): at 2:00 elapsed (13:00 left), else 3:00, buy the leading side if its ask is 0.80-0.95; $100 per round; hold to settlement; taker fee 0.0695*p*(1-p). Paper only.
Forward test started 2026-10-23T00:00:00Z. Updated 2026-10-25T14:24:47Z.

**Too early to judge: 37 of the ~150 rounds (about a week) needed.**

| | Forward | Backtest (Oct 6-22) |
|---|---|---|
| Rounds | 37 | 272 |
| Win rate | 81.1% | 89.3% |
| Break-even win rate at prices paid | 85.8% | - |
| Average ask | 0.849 | 0.838 |
| Net at $100/round | $-214.38 | $+1,486 |
| Per round | -5.79% | +5.46% |
| Max drawdown | $-332.83 | $-403 |
| Longest losing streak | 2 | 2 |
| Entry timing | 13:00 / 12:00 left | same |

Rounds where the rule did not trigger: 211. Pending (not settled or not fetched yet): 2.

## By day (UTC)

| Day | Net |
|---|---|
| 2026-10-23 | $-138.09 |
| 2026-10-24 | $-72.04 |
| 2026-10-25 | $-4.25 |

## Chart pull at the check (parallel column - not part of the rule)

Pull = EMA 9/21 and Supertrend on BRTI 1-minute candles, as drawn by research/market_pull.pine, read against the favorite. Oct 16-24 (143 rounds): 3/3 with the favorite won 92%, 1/3 won 84%, against won 78%. Small sample; this column is the forward test of that.

| Pull at the check | Rounds | Win rate | Net |
|---|---|---|---|
| with the favorite 3/3 | 29 | 86.2% | $-17.71 |
| with the favorite 1/3 | 8 | 62.5% | $-196.67 |
| against the favorite | 0 | - | $+0.00 |

## Last 20 rounds

| Window (UTC) | Min | Side | Ask | Pull | Result | P&L | Running |
|---|---|---|---|---|---|---|---|
| 10-23 22:30 | 2 | Down | 0.90 | +3 | won | $+10.42 | $-168.83 |
| 10-23 22:45 | 3 | Down | 0.84 | +3 | won | $+17.94 | $-150.89 |
| 10-23 23:45 | 3 | Up | 0.88 | +3 | won | $+12.80 | $-138.09 |
| 10-24 01:15 | 2 | Up | 0.81 | +3 | won | $+22.14 | $-115.95 |
| 10-24 04:00 | 3 | Up | 0.80 | +3 | LOST | $-101.39 | $-217.34 |
| 10-24 07:00 | 3 | Up | 0.82 | +3 | won | $+20.70 | $-196.64 |
| 10-24 09:30 | 3 | Up | 0.82 | +1 | LOST | $-101.25 | $-297.89 |
| 10-24 10:30 | 3 | Up | 0.85 | +3 | won | $+16.60 | $-281.29 |
| 10-24 12:15 | 3 | Up | 0.82 | +3 | won | $+20.70 | $-260.59 |
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
