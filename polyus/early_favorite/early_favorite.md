# Early Favorite v2 - forward test

Rule (frozen): at 2:00 elapsed (13:00 left), else 3:00, buy the leading side if its ask is 0.80-0.95; $100 per round; hold to settlement; taker fee 0.0695*p*(1-p). Paper only.
Forward test started 2026-10-23T00:00:00Z. Updated 2026-11-01T15:07:24Z.

**Losing: forward win rate is below break-even at the prices paid.**

| | Forward | Backtest (Oct 6-22) |
|---|---|---|
| Rounds | 150 | 272 |
| Win rate | 83.3% | 89.3% |
| Break-even win rate at prices paid | 85.2% | - |
| Average ask | 0.843 | 0.838 |
| Net at $100/round | $-358.77 | $+1,486 |
| Per round | -2.39% | +5.46% |
| Max drawdown | $-627.87 | $-403 |
| Longest losing streak | 3 | 2 |
| Entry timing | 13:00 / 12:00 left | same |

Rounds where the rule did not trigger: 726. Pending (not settled or not fetched yet): 19.

## By day (UTC)

| Day | Net |
|---|---|
| 2026-10-23 | $-138.09 |
| 2026-10-24 | $-72.04 |
| 2026-10-25 | $+158.51 |
| 2026-10-26 | $-288.77 |
| 2026-10-27 | $-135.61 |
| 2026-10-28 | $-114.87 |
| 2026-10-29 | $+265.34 |
| 2026-10-30 | $-136.21 |
| 2026-10-31 | $+42.86 |
| 2026-11-01 | $+60.11 |

## Chart pull at the check (parallel column - not part of the rule)

Pull = EMA 9/21 and Supertrend on BRTI 1-minute candles, as drawn by research/market_pull.pine, read against the favorite. Oct 16-24 (143 rounds): 3/3 with the favorite won 92%, 1/3 won 84%, against won 78%. Small sample; this column is the forward test of that.

| Pull at the check | Rounds | Win rate | Net |
|---|---|---|---|
| with the favorite 3/3 | 112 | 84.8% | $-143.43 |
| with the favorite 1/3 | 34 | 79.4% | $-177.77 |
| against the favorite | 4 | 75.0% | $-37.57 |

## Cut at 5:00 left (parallel column - not part of the rule)

What if the position were sold at 5:00 left whenever the favorite's bid is under 45c (sold 2c under the bid, taker fee)? Backtest Oct 6-22: about +$150-220 over holding on 272 trades, under 1% of the money staked and found in-sample. This is its forward test; the traded rule stays hold-to-settlement.

| | Hold (the rule) | Cut under 45c at 5:00 left |
|---|---|---|
| Rounds with a 5:00-left price | 150 | same |
| Positions cut | - | 16 (13 would have lost, 3 would have won) |
| Net at $100/round | $-358.77 | $-304.89 (+53.88) |

## Last 20 rounds

| Window (UTC) | Min | Side | Ask | Pull | Result | P&L | Running |
|---|---|---|---|---|---|---|---|
| 10-30 20:00 | 3 | Up | 0.81 | +3 | won | $+22.14 | $-475.78 |
| 10-30 22:00 | 3 | Up | 0.87 | +1 | won | $+14.04 | $-461.74 |
| 10-31 04:00 | 2 | Up | 0.80 | +1 | won | $+23.61 | $-438.13 |
| 10-31 06:00 | 2 | Up | 0.82 | +3 | won | $+20.70 | $-417.43 |
| 10-31 06:45 | 3 | Up | 0.87 | +3 | won | $+14.04 | $-403.39 |
| 10-31 10:00 | 3 | Down | 0.81 | +3 | LOST | $-101.32 | $-504.71 |
| 10-31 11:15 | 2 | Up | 0.80 | +3 | won | $+23.61 | $-481.10 |
| 10-31 17:45 | 2 | Up | 0.81 | +3 | won | $+22.14 | $-458.96 |
| 10-31 20:00 | 3 | Up | 0.84 | +3 | won | $+17.94 | $-441.02 |
| 10-31 21:00 | 2 | Down | 0.81 | +3 | won | $+22.14 | $-418.88 |
| 11-01 01:45 | 2 | Down | 0.80 | +1 | won | $+23.61 | $-395.27 |
| 11-01 02:00 | 3 | Up | 0.83 | +3 | won | $+19.30 | $-375.97 |
| 11-01 02:45 | 2 | Up | 0.83 | +3 | won | $+19.30 | $-356.67 |
| 11-01 03:45 | 2 | Down | 0.83 | +1 | won | $+19.30 | $-337.37 |
| 11-01 04:00 | 3 | Down | 0.82 | +3 | won | $+20.70 | $-316.67 |
| 11-01 05:00 | 3 | Up | 0.80 | +3 | won | $+23.61 | $-293.06 |
| 11-01 05:30 | 3 | Up | 0.89 | +3 | LOST | $-100.76 | $-393.82 |
| 11-01 05:45 | 2 | Up | 0.86 | +1 | won | $+15.31 | $-378.51 |
| 11-01 06:15 | 2 | Down | 0.89 | +1 | won | $+11.60 | $-366.91 |
| 11-01 07:15 | 2 | Down | 0.92 | +3 | won | $+8.14 | $-358.77 |
