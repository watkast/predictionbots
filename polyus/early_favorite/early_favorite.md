# Early Favorite v2 - forward test

Rule (frozen): at 2:00 elapsed (13:00 left), else 3:00, buy the leading side if its ask is 0.80-0.95; $100 per round; hold to settlement; taker fee 0.0695*p*(1-p). Paper only.
Forward test started 2026-10-23T00:00:00Z. Updated 2026-11-06T02:23:12Z.

**Losing: forward win rate is below break-even at the prices paid.**

| | Forward | Backtest (Oct 6-22) |
|---|---|---|
| Rounds | 223 | 272 |
| Win rate | 82.5% | 89.3% |
| Break-even win rate at prices paid | 84.9% | - |
| Average ask | 0.840 | 0.838 |
| Net at $100/round | $-668.45 | $+1,486 |
| Per round | -3.00% | +5.46% |
| Max drawdown | $-843.92 | $-403 |
| Longest losing streak | 5 | 2 |
| Entry timing | 13:00 / 12:00 left | same |

Rounds where the rule did not trigger: 1104. Pending (not settled or not fetched yet): 19.

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
| 2026-11-06 | $+19.30 |

## Chart pull at the check (parallel column - not part of the rule)

Pull = EMA 9/21 and Supertrend on BRTI 1-minute candles, as drawn by research/market_pull.pine, read against the favorite. Oct 16-24 (143 rounds): 3/3 with the favorite won 92%, 1/3 won 84%, against won 78%. Small sample; this column is the forward test of that.

| Pull at the check | Rounds | Win rate | Net |
|---|---|---|---|
| with the favorite 3/3 | 167 | 84.4% | $-208.66 |
| with the favorite 1/3 | 46 | 80.4% | $-183.80 |
| against the favorite | 10 | 60.0% | $-275.99 |

## Cut at 5:00 left (parallel column - not part of the rule)

What if the position were sold at 5:00 left whenever the favorite's bid is under 45c (sold 2c under the bid, taker fee)? Backtest Oct 6-22: about +$150-220 over holding on 272 trades, under 1% of the money staked and found in-sample. This is its forward test; the traded rule stays hold-to-settlement.

| | Hold (the rule) | Cut under 45c at 5:00 left |
|---|---|---|
| Rounds with a 5:00-left price | 223 | same |
| Positions cut | - | 22 (18 would have lost, 4 would have won) |
| Net at $100/round | $-668.45 | $-629.18 (+39.27) |

## Last 20 rounds

| Window (UTC) | Min | Side | Ask | Pull | Result | P&L | Running |
|---|---|---|---|---|---|---|---|
| 11-05 01:15 | 2 | Down | 0.80 | +3 | won | $+23.61 | $-418.30 |
| 11-05 01:30 | 3 | Up | 0.83 | +3 | won | $+19.30 | $-399.00 |
| 11-05 03:15 | 3 | Up | 0.81 | +3 | won | $+22.14 | $-376.86 |
| 11-05 03:45 | 2 | Down | 0.81 | +3 | won | $+22.14 | $-354.72 |
| 11-05 04:00 | 3 | Down | 0.81 | +3 | won | $+22.14 | $-332.58 |
| 11-05 06:15 | 2 | Up | 0.84 | +3 | won | $+17.94 | $-314.64 |
| 11-05 06:45 | 2 | Up | 0.88 | +3 | won | $+12.80 | $-301.84 |
| 11-05 07:30 | 2 | Down | 0.90 | +3 | won | $+10.42 | $-291.42 |
| 11-05 09:00 | 2 | Down | 0.80 | +3 | won | $+23.61 | $-267.81 |
| 11-05 10:30 | 2 | Down | 0.85 | +1 | won | $+16.60 | $-251.21 |
| 11-05 13:45 | 2 | Up | 0.80 | +3 | LOST | $-101.39 | $-352.60 |
| 11-05 15:00 | 2 | Down | 0.85 | +3 | won | $+16.60 | $-336.00 |
| 11-05 15:15 | 2 | Up | 0.90 | -1 | LOST | $-100.69 | $-436.69 |
| 11-05 17:30 | 3 | Up | 0.86 | +1 | won | $+15.31 | $-421.38 |
| 11-05 18:00 | 3 | Down | 0.81 | +3 | LOST | $-101.32 | $-522.70 |
| 11-05 18:15 | 2 | Down | 0.80 | -3 | LOST | $-101.39 | $-624.09 |
| 11-05 19:15 | 3 | Up | 0.84 | +3 | LOST | $-101.11 | $-725.20 |
| 11-05 22:45 | 3 | Down | 0.81 | +3 | won | $+22.14 | $-703.06 |
| 11-05 23:00 | 2 | Down | 0.86 | +3 | won | $+15.31 | $-687.75 |
| 11-06 01:15 | 3 | Down | 0.83 | +3 | won | $+19.30 | $-668.45 |
