# Early Favorite v2 - forward test

Rule (frozen): at 2:00 elapsed (13:00 left), else 3:00, buy the leading side if its ask is 0.80-0.95; $100 per round; hold to settlement; taker fee 0.0695*p*(1-p). Paper only.
Forward test started 2026-10-23T00:00:00Z. Updated 2026-11-13T07:54:05Z.

**Losing: forward win rate is below break-even at the prices paid.**

| | Forward | Backtest (Oct 6-22) |
|---|---|---|
| Rounds | 350 | 272 |
| Win rate | 84.3% | 89.3% |
| Break-even win rate at prices paid | 84.8% | - |
| Average ask | 0.838 | 0.838 |
| Net at $100/round | $-244.75 | $+1,486 |
| Per round | -0.70% | +5.46% |
| Max drawdown | $-947.43 | $-403 |
| Longest losing streak | 5 | 2 |
| Entry timing | 13:00 / 12:00 left | same |

Rounds where the rule did not trigger: 1668. Pending (not settled or not fetched yet): 20.

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
| 2026-11-02 | $-313.40 |
| 2026-11-03 | $+1.61 |
| 2026-11-04 | $+170.62 |
| 2026-11-05 | $-245.84 |
| 2026-11-06 | $-82.11 |
| 2026-11-07 | $+0.54 |
| 2026-11-08 | $+83.79 |
| 2026-11-09 | $+187.96 |
| 2026-11-10 | $-266.21 |
| 2026-11-11 | $+106.52 |
| 2026-11-12 | $+335.89 |
| 2026-11-13 | $+76.62 |

## Chart pull at the check (parallel column - not part of the rule)

Pull = EMA 9/21 and Supertrend on BRTI 1-minute candles, as drawn by research/market_pull.pine, read against the favorite. Oct 16-24 (143 rounds): 3/3 with the favorite won 92%, 1/3 won 84%, against won 78%. Small sample; this column is the forward test of that.

| Pull at the check | Rounds | Win rate | Net |
|---|---|---|---|
| with the favorite 3/3 | 268 | 85.5% | $+99.93 |
| with the favorite 1/3 | 65 | 83.1% | $-83.85 |
| against the favorite | 17 | 70.6% | $-260.83 |

## Cut at 5:00 left (parallel column - not part of the rule)

What if the position were sold at 5:00 left whenever the favorite's bid is under 45c (sold 2c under the bid, taker fee)? Backtest Oct 6-22: about +$150-220 over holding on 272 trades, under 1% of the money staked and found in-sample. This is its forward test; the traded rule stays hold-to-settlement.

| | Hold (the rule) | Cut under 45c at 5:00 left |
|---|---|---|
| Rounds with a 5:00-left price | 350 | same |
| Positions cut | - | 29 (24 would have lost, 5 would have won) |
| Net at $100/round | $-244.75 | $-167.06 (+77.69) |

## Last 20 rounds

| Window (UTC) | Min | Side | Ask | Pull | Result | P&L | Running |
|---|---|---|---|---|---|---|---|
| 11-12 09:00 | 2 | Down | 0.92 | +3 | won | $+8.14 | $-491.35 |
| 11-12 09:30 | 3 | Up | 0.82 | +3 | won | $+20.70 | $-470.65 |
| 11-12 10:15 | 3 | Up | 0.83 | +3 | won | $+19.30 | $-451.35 |
| 11-12 11:15 | 2 | Down | 0.86 | +3 | won | $+15.31 | $-436.04 |
| 11-12 11:30 | 3 | Down | 0.87 | +3 | won | $+14.04 | $-422.00 |
| 11-12 12:30 | 2 | Up | 0.81 | -1 | won | $+22.14 | $-399.86 |
| 11-12 15:00 | 3 | Down | 0.80 | +3 | won | $+23.61 | $-376.25 |
| 11-12 16:30 | 2 | Down | 0.80 | +3 | won | $+23.61 | $-352.64 |
| 11-12 16:45 | 3 | Up | 0.87 | +1 | won | $+14.04 | $-338.60 |
| 11-12 18:45 | 2 | Down | 0.82 | +3 | won | $+20.70 | $-317.90 |
| 11-12 19:00 | 3 | Down | 0.91 | +3 | won | $+9.26 | $-308.64 |
| 11-12 19:30 | 3 | Down | 0.80 | +3 | won | $+23.61 | $-285.03 |
| 11-12 20:00 | 3 | Down | 0.83 | +1 | won | $+19.30 | $-265.73 |
| 11-12 20:15 | 3 | Down | 0.81 | +3 | won | $+22.14 | $-243.59 |
| 11-12 20:45 | 2 | Up | 0.80 | +3 | LOST | $-101.39 | $-344.98 |
| 11-12 21:15 | 3 | Up | 0.80 | +3 | won | $+23.61 | $-321.37 |
| 11-13 00:45 | 2 | Up | 0.80 | -1 | won | $+23.61 | $-297.76 |
| 11-13 01:15 | 2 | Up | 0.85 | +1 | won | $+16.60 | $-281.16 |
| 11-13 06:30 | 2 | Up | 0.80 | +3 | won | $+23.61 | $-257.55 |
| 11-13 07:30 | 3 | Down | 0.88 | +3 | won | $+12.80 | $-244.75 |
