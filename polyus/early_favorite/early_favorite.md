# Early Favorite v2 - forward test

Rule (frozen): at 2:00 elapsed (13:00 left), else 3:00, buy the leading side if its ask is 0.80-0.95; $100 per round; hold to settlement; taker fee 0.0695*p*(1-p). Paper only.
Forward test started 2026-10-23T00:00:00Z. Updated 2026-11-01T23:34:26Z.

**Losing: forward win rate is below break-even at the prices paid.**

| | Forward | Backtest (Oct 6-22) |
|---|---|---|
| Rounds | 159 | 272 |
| Win rate | 83.7% | 89.3% |
| Break-even win rate at prices paid | 85.1% | - |
| Average ask | 0.842 | 0.838 |
| Net at $100/round | $-300.74 | $+1,486 |
| Per round | -1.89% | +5.46% |
| Max drawdown | $-627.87 | $-403 |
| Longest losing streak | 3 | 2 |
| Entry timing | 13:00 / 12:00 left | same |

Rounds where the rule did not trigger: 782. Pending (not settled or not fetched yet): 18.

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
| 2026-11-01 | $+118.14 |

## Chart pull at the check (parallel column - not part of the rule)

Pull = EMA 9/21 and Supertrend on BRTI 1-minute candles, as drawn by research/market_pull.pine, read against the favorite. Oct 16-24 (143 rounds): 3/3 with the favorite won 92%, 1/3 won 84%, against won 78%. Small sample; this column is the forward test of that.

| Pull at the check | Rounds | Win rate | Net |
|---|---|---|---|
| with the favorite 3/3 | 120 | 85.8% | $+15.85 |
| with the favorite 1/3 | 35 | 77.1% | $-279.02 |
| against the favorite | 4 | 75.0% | $-37.57 |

## Cut at 5:00 left (parallel column - not part of the rule)

What if the position were sold at 5:00 left whenever the favorite's bid is under 45c (sold 2c under the bid, taker fee)? Backtest Oct 6-22: about +$150-220 over holding on 272 trades, under 1% of the money staked and found in-sample. This is its forward test; the traded rule stays hold-to-settlement.

| | Hold (the rule) | Cut under 45c at 5:00 left |
|---|---|---|
| Rounds with a 5:00-left price | 159 | same |
| Positions cut | - | 16 (13 would have lost, 3 would have won) |
| Net at $100/round | $-300.74 | $-246.86 (+53.88) |

## Last 20 rounds

| Window (UTC) | Min | Side | Ask | Pull | Result | P&L | Running |
|---|---|---|---|---|---|---|---|
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
| 11-01 08:30 | 3 | Up | 0.81 | +3 | won | $+22.14 | $-336.63 |
| 11-01 10:30 | 3 | Down | 0.82 | +3 | won | $+20.70 | $-315.93 |
| 11-01 11:30 | 2 | Down | 0.80 | +3 | won | $+23.61 | $-292.32 |
| 11-01 12:00 | 2 | Up | 0.83 | +3 | won | $+19.30 | $-273.02 |
| 11-01 12:15 | 2 | Down | 0.86 | +3 | won | $+15.31 | $-257.71 |
| 11-01 14:00 | 2 | Down | 0.82 | +1 | LOST | $-101.25 | $-358.96 |
| 11-01 15:30 | 2 | Down | 0.80 | +3 | won | $+23.61 | $-335.35 |
| 11-01 16:15 | 3 | Up | 0.83 | +3 | won | $+19.30 | $-316.05 |
| 11-01 22:15 | 3 | Down | 0.86 | +3 | won | $+15.31 | $-300.74 |
