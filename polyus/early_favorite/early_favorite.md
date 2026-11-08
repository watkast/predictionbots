# Early Favorite v2 - forward test

Rule (frozen): at 2:00 elapsed (13:00 left), else 3:00, buy the leading side if its ask is 0.80-0.95; $100 per round; hold to settlement; taker fee 0.0695*p*(1-p). Paper only.
Forward test started 2026-10-23T00:00:00Z. Updated 2026-11-08T23:42:07Z.

**Losing: forward win rate is below break-even at the prices paid.**

| | Forward | Backtest (Oct 6-22) |
|---|---|---|
| Rounds | 265 | 272 |
| Win rate | 82.6% | 89.3% |
| Break-even win rate at prices paid | 84.8% | - |
| Average ask | 0.838 | 0.838 |
| Net at $100/round | $-707.67 | $+1,486 |
| Per round | -2.67% | +5.46% |
| Max drawdown | $-947.43 | $-403 |
| Longest losing streak | 5 | 2 |
| Entry timing | 13:00 / 12:00 left | same |

Rounds where the rule did not trigger: 1339. Pending (not settled or not fetched yet): 19.

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
| 2026-11-08 | $+61.65 |

## Chart pull at the check (parallel column - not part of the rule)

Pull = EMA 9/21 and Supertrend on BRTI 1-minute candles, as drawn by research/market_pull.pine, read against the favorite. Oct 16-24 (143 rounds): 3/3 with the favorite won 92%, 1/3 won 84%, against won 78%. Small sample; this column is the forward test of that.

| Pull at the check | Rounds | Win rate | Net |
|---|---|---|---|
| with the favorite 3/3 | 204 | 84.3% | $-221.93 |
| with the favorite 1/3 | 50 | 80.0% | $-222.55 |
| against the favorite | 11 | 63.6% | $-263.19 |

## Cut at 5:00 left (parallel column - not part of the rule)

What if the position were sold at 5:00 left whenever the favorite's bid is under 45c (sold 2c under the bid, taker fee)? Backtest Oct 6-22: about +$150-220 over holding on 272 trades, under 1% of the money staked and found in-sample. This is its forward test; the traded rule stays hold-to-settlement.

| | Hold (the rule) | Cut under 45c at 5:00 left |
|---|---|---|
| Rounds with a 5:00-left price | 265 | same |
| Positions cut | - | 28 (23 would have lost, 5 would have won) |
| Net at $100/round | $-707.67 | $-666.71 (+40.96) |

## Last 20 rounds

| Window (UTC) | Min | Side | Ask | Pull | Result | P&L | Running |
|---|---|---|---|---|---|---|---|
| 11-07 15:45 | 2 | Down | 0.81 | +3 | won | $+22.14 | $-832.90 |
| 11-07 16:45 | 3 | Down | 0.81 | +3 | won | $+22.14 | $-810.76 |
| 11-07 17:00 | 3 | Up | 0.83 | +3 | won | $+19.30 | $-791.46 |
| 11-07 22:30 | 2 | Up | 0.81 | +3 | won | $+22.14 | $-769.32 |
| 11-08 01:15 | 3 | Down | 0.81 | +1 | won | $+22.14 | $-747.18 |
| 11-08 03:00 | 3 | Up | 0.81 | +3 | won | $+22.14 | $-725.04 |
| 11-08 03:45 | 2 | Up | 0.80 | +3 | won | $+23.61 | $-701.43 |
| 11-08 04:45 | 2 | Down | 0.80 | +3 | won | $+23.61 | $-677.82 |
| 11-08 07:45 | 2 | Up | 0.93 | +3 | won | $+7.04 | $-670.78 |
| 11-08 08:15 | 3 | Down | 0.82 | +3 | won | $+20.70 | $-650.08 |
| 11-08 09:00 | 2 | Down | 0.81 | +1 | won | $+22.14 | $-627.94 |
| 11-08 10:30 | 2 | Down | 0.82 | +3 | LOST | $-101.25 | $-729.19 |
| 11-08 13:15 | 2 | Up | 0.81 | +3 | LOST | $-101.32 | $-830.51 |
| 11-08 14:30 | 2 | Up | 0.81 | +3 | won | $+22.14 | $-808.37 |
| 11-08 16:30 | 2 | Down | 0.81 | +3 | won | $+22.14 | $-786.23 |
| 11-08 18:15 | 2 | Up | 0.80 | +3 | won | $+23.61 | $-762.62 |
| 11-08 19:30 | 2 | Up | 0.86 | +3 | won | $+15.31 | $-747.31 |
| 11-08 21:45 | 2 | Down | 0.88 | +3 | won | $+12.80 | $-734.51 |
| 11-08 22:00 | 2 | Up | 0.88 | -1 | won | $+12.80 | $-721.71 |
| 11-08 23:15 | 3 | Up | 0.87 | +3 | won | $+14.04 | $-707.67 |
