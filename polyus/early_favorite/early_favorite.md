# Early Favorite v2 - forward test

Rule (frozen): at 2:00 elapsed (13:00 left), else 3:00, buy the leading side if its ask is 0.80-0.95; $100 per round; hold to settlement; taker fee 0.0695*p*(1-p). Paper only.
Forward test started 2026-10-23T00:00:00Z. Updated 2026-10-26T23:53:34Z.

**Losing: forward win rate is below break-even at the prices paid.**

| | Forward | Backtest (Oct 6-22) |
|---|---|---|
| Rounds | 58 | 272 |
| Win rate | 81.0% | 89.3% |
| Break-even win rate at prices paid | 85.7% | - |
| Average ask | 0.848 | 0.838 |
| Net at $100/round | $-340.39 | $+1,486 |
| Per round | -5.87% | +5.46% |
| Max drawdown | $-395.95 | $-403 |
| Longest losing streak | 2 | 2 |
| Entry timing | 13:00 / 12:00 left | same |

Rounds where the rule did not trigger: 325. Pending (not settled or not fetched yet): 1.

## By day (UTC)

| Day | Net |
|---|---|
| 2026-10-23 | $-138.09 |
| 2026-10-24 | $-72.04 |
| 2026-10-25 | $+158.51 |
| 2026-10-26 | $-288.77 |

## Chart pull at the check (parallel column - not part of the rule)

Pull = EMA 9/21 and Supertrend on BRTI 1-minute candles, as drawn by research/market_pull.pine, read against the favorite. Oct 16-24 (143 rounds): 3/3 with the favorite won 92%, 1/3 won 84%, against won 78%. Small sample; this column is the forward test of that.

| Pull at the check | Rounds | Win rate | Net |
|---|---|---|---|
| with the favorite 3/3 | 46 | 84.8% | $-101.36 |
| with the favorite 1/3 | 12 | 66.7% | $-239.03 |
| against the favorite | 0 | - | $+0.00 |

## Cut at 5:00 left (parallel column - not part of the rule)

What if the position were sold at 5:00 left whenever the favorite's bid is under 45c (sold 2c under the bid, taker fee)? Backtest Oct 6-22: about +$150-220 over holding on 272 trades, under 1% of the money staked and found in-sample. This is its forward test; the traded rule stays hold-to-settlement.

| | Hold (the rule) | Cut under 45c at 5:00 left |
|---|---|---|
| Rounds with a 5:00-left price | 58 | same |
| Positions cut | - | 6 (5 would have lost, 1 would have won) |
| Net at $100/round | $-340.39 | $-297.31 (+43.08) |

## Last 20 rounds

| Window (UTC) | Min | Side | Ask | Pull | Result | P&L | Running |
|---|---|---|---|---|---|---|---|
| 10-25 15:00 | 3 | Up | 0.84 | +3 | won | $+17.94 | $-179.84 |
| 10-25 15:30 | 2 | Up | 0.80 | +1 | won | $+23.61 | $-156.23 |
| 10-25 16:30 | 3 | Up | 0.85 | +3 | won | $+16.60 | $-139.63 |
| 10-25 20:30 | 3 | Down | 0.83 | +3 | won | $+19.30 | $-120.33 |
| 10-25 21:30 | 3 | Down | 0.82 | +3 | won | $+20.70 | $-99.63 |
| 10-25 21:45 | 2 | Down | 0.88 | +3 | won | $+12.80 | $-86.83 |
| 10-25 22:00 | 2 | Up | 0.89 | +1 | won | $+11.60 | $-75.23 |
| 10-25 22:15 | 3 | Up | 0.80 | +1 | won | $+23.61 | $-51.62 |
| 10-26 00:45 | 3 | Down | 0.82 | +3 | won | $+20.70 | $-30.92 |
| 10-26 04:30 | 3 | Up | 0.85 | +3 | won | $+16.60 | $-14.32 |
| 10-26 07:00 | 3 | Up | 0.81 | +3 | won | $+22.14 | $+7.82 |
| 10-26 09:15 | 3 | Up | 0.93 | +3 | won | $+7.04 | $+14.86 |
| 10-26 10:00 | 3 | Down | 0.81 | +3 | won | $+22.14 | $+37.00 |
| 10-26 11:30 | 2 | Down | 0.82 | +3 | LOST | $-101.25 | $-64.25 |
| 10-26 12:15 | 3 | Down | 0.80 | +3 | LOST | $-101.39 | $-165.64 |
| 10-26 13:00 | 3 | Down | 0.91 | +3 | won | $+9.26 | $-156.38 |
| 10-26 14:30 | 3 | Down | 0.80 | +3 | LOST | $-101.39 | $-257.77 |
| 10-26 20:30 | 3 | Up | 0.83 | +1 | LOST | $-101.18 | $-358.95 |
| 10-26 21:00 | 2 | Up | 0.92 | +3 | won | $+8.14 | $-350.81 |
| 10-26 23:00 | 3 | Down | 0.90 | +3 | won | $+10.42 | $-340.39 |
