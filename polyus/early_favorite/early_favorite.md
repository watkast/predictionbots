# Early Favorite v2 - forward test

Rule (frozen): at 2:00 elapsed (13:00 left), else 3:00, buy the leading side if its ask is 0.80-0.95; $100 per round; hold to settlement; taker fee 0.0695*p*(1-p). Paper only.
Forward test started 2026-10-23T00:00:00Z. Updated 2026-10-23T01:28:14Z.

**Too early to judge: 2 of the ~150 rounds (about a week) needed.**

| | Forward | Backtest (Oct 6-22) |
|---|---|---|
| Rounds | 2 | 272 |
| Win rate | 100.0% | 89.3% |
| Break-even win rate at prices paid | 85.4% | - |
| Average ask | 0.845 | 0.838 |
| Net at $100/round | $+34.94 | $+1,486 |
| Per round | +17.47% | +5.46% |
| Max drawdown | $0.00 | $-403 |
| Longest losing streak | 0 | 2 |
| Entry timing | 13:00 / 12:00 left | same |

Rounds where the rule did not trigger: 3. Pending (not settled or not fetched yet): 1.

## By day (UTC)

| Day | Net |
|---|---|
| 2026-10-23 | $+34.94 |

## Last 20 rounds

| Window (UTC) | Min | Side | Ask | Result | P&L | Running |
|---|---|---|---|---|---|---|
| 10-23 00:00 | 3 | Down | 0.81 | won | $+22.14 | $+22.14 |
| 10-23 00:30 | 3 | Up | 0.88 | won | $+12.80 | $+34.94 |
