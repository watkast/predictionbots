# Early Favorite v2 - forward test

Rule (frozen): at 2:00 elapsed (13:00 left), else 3:00, buy the leading side if its ask is 0.80-0.95; $100 per round; hold to settlement; taker fee 0.0695*p*(1-p). Paper only.
Forward test started 2026-10-23T00:00:00Z. Updated 2026-10-28T01:19:53Z.

**Losing: forward win rate is below break-even at the prices paid.**

| | Forward | Backtest (Oct 6-22) |
|---|---|---|
| Rounds | 77 | 272 |
| Win rate | 80.5% | 89.3% |
| Break-even win rate at prices paid | 85.4% | - |
| Average ask | 0.845 | 0.838 |
| Net at $100/round | $-476.00 | $+1,486 |
| Per round | -6.18% | +5.46% |
| Max drawdown | $-578.08 | $-403 |
| Longest losing streak | 3 | 2 |
| Entry timing | 13:00 / 12:00 left | same |

Rounds where the rule did not trigger: 408. Pending (not settled or not fetched yet): 1.

## By day (UTC)

| Day | Net |
|---|---|
| 2026-10-23 | $-138.09 |
| 2026-10-24 | $-72.04 |
| 2026-10-25 | $+158.51 |
| 2026-10-26 | $-288.77 |
| 2026-10-27 | $-135.61 |

## Chart pull at the check (parallel column - not part of the rule)

Pull = EMA 9/21 and Supertrend on BRTI 1-minute candles, as drawn by research/market_pull.pine, read against the favorite. Oct 16-24 (143 rounds): 3/3 with the favorite won 92%, 1/3 won 84%, against won 78%. Small sample; this column is the forward test of that.

| Pull at the check | Rounds | Win rate | Net |
|---|---|---|---|
| with the favorite 3/3 | 57 | 84.2% | $-153.69 |
| with the favorite 1/3 | 20 | 70.0% | $-322.31 |
| against the favorite | 0 | - | $+0.00 |

## Cut at 5:00 left (parallel column - not part of the rule)

What if the position were sold at 5:00 left whenever the favorite's bid is under 45c (sold 2c under the bid, taker fee)? Backtest Oct 6-22: about +$150-220 over holding on 272 trades, under 1% of the money staked and found in-sample. This is its forward test; the traded rule stays hold-to-settlement.

| | Hold (the rule) | Cut under 45c at 5:00 left |
|---|---|---|
| Rounds with a 5:00-left price | 77 | same |
| Positions cut | - | 8 (7 would have lost, 1 would have won) |
| Net at $100/round | $-476.00 | $-425.00 (+51.00) |

## Last 20 rounds

| Window (UTC) | Min | Side | Ask | Pull | Result | P&L | Running |
|---|---|---|---|---|---|---|---|
| 10-26 23:00 | 3 | Down | 0.90 | +3 | won | $+10.42 | $-340.39 |
| 10-27 01:15 | 3 | Down | 0.88 | +1 | won | $+12.80 | $-327.59 |
| 10-27 05:45 | 3 | Up | 0.87 | +3 | won | $+14.04 | $-313.55 |
| 10-27 06:00 | 2 | Down | 0.80 | +1 | won | $+23.61 | $-289.94 |
| 10-27 06:15 | 3 | Down | 0.82 | +3 | won | $+20.70 | $-269.24 |
| 10-27 06:30 | 2 | Up | 0.81 | +1 | LOST | $-101.32 | $-370.56 |
| 10-27 07:15 | 3 | Up | 0.81 | +1 | won | $+22.14 | $-348.42 |
| 10-27 07:45 | 3 | Up | 0.81 | +1 | won | $+22.14 | $-326.28 |
| 10-27 08:00 | 3 | Up | 0.82 | +3 | won | $+20.70 | $-305.58 |
| 10-27 10:45 | 3 | Up | 0.94 | +3 | won | $+5.97 | $-299.61 |
| 10-27 11:00 | 2 | Up | 0.81 | +1 | won | $+22.14 | $-277.47 |
| 10-27 11:15 | 2 | Down | 0.80 | +3 | won | $+23.61 | $-253.86 |
| 10-27 12:15 | 2 | Up | 0.85 | +3 | won | $+16.60 | $-237.26 |
| 10-27 13:30 | 3 | Down | 0.83 | +3 | LOST | $-101.18 | $-338.44 |
| 10-27 14:15 | 2 | Down | 0.80 | +1 | LOST | $-101.39 | $-439.83 |
| 10-27 15:00 | 3 | Up | 0.82 | +3 | LOST | $-101.25 | $-541.08 |
| 10-27 16:15 | 3 | Up | 0.85 | +1 | won | $+16.60 | $-524.48 |
| 10-27 19:00 | 3 | Up | 0.83 | +3 | won | $+19.30 | $-505.18 |
| 10-27 21:30 | 2 | Up | 0.93 | +3 | won | $+7.04 | $-498.14 |
| 10-27 22:15 | 3 | Up | 0.81 | +3 | won | $+22.14 | $-476.00 |
