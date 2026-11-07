# Early Favorite v2 - forward test

Rule (frozen): at 2:00 elapsed (13:00 left), else 3:00, buy the leading side if its ask is 0.80-0.95; $100 per round; hold to settlement; taker fee 0.0695*p*(1-p). Paper only.
Forward test started 2026-10-23T00:00:00Z. Updated 2026-11-07T20:53:00Z.

**Losing: forward win rate is below break-even at the prices paid.**

| | Forward | Backtest (Oct 6-22) |
|---|---|---|
| Rounds | 248 | 272 |
| Win rate | 82.3% | 89.3% |
| Break-even win rate at prices paid | 84.8% | - |
| Average ask | 0.839 | 0.838 |
| Net at $100/round | $-791.46 | $+1,486 |
| Per round | -3.19% | +5.46% |
| Max drawdown | $-947.43 | $-403 |
| Longest losing streak | 5 | 2 |
| Entry timing | 13:00 / 12:00 left | same |

Rounds where the rule did not trigger: 1249. Pending (not settled or not fetched yet): 19.

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
| 2026-11-07 | $-21.60 |

## Chart pull at the check (parallel column - not part of the rule)

Pull = EMA 9/21 and Supertrend on BRTI 1-minute candles, as drawn by research/market_pull.pine, read against the favorite. Oct 16-24 (143 rounds): 3/3 with the favorite won 92%, 1/3 won 84%, against won 78%. Small sample; this column is the forward test of that.

| Pull at the check | Rounds | Win rate | Net |
|---|---|---|---|
| with the favorite 3/3 | 190 | 84.2% | $-248.64 |
| with the favorite 1/3 | 48 | 79.2% | $-266.83 |
| against the favorite | 10 | 60.0% | $-275.99 |

## Cut at 5:00 left (parallel column - not part of the rule)

What if the position were sold at 5:00 left whenever the favorite's bid is under 45c (sold 2c under the bid, taker fee)? Backtest Oct 6-22: about +$150-220 over holding on 272 trades, under 1% of the money staked and found in-sample. This is its forward test; the traded rule stays hold-to-settlement.

| | Hold (the rule) | Cut under 45c at 5:00 left |
|---|---|---|
| Rounds with a 5:00-left price | 248 | same |
| Positions cut | - | 26 (22 would have lost, 4 would have won) |
| Net at $100/round | $-791.46 | $-696.44 (+95.02) |

## Last 20 rounds

| Window (UTC) | Min | Side | Ask | Pull | Result | P&L | Running |
|---|---|---|---|---|---|---|---|
| 11-06 07:00 | 3 | Down | 0.91 | +3 | won | $+9.26 | $-793.52 |
| 11-06 09:00 | 3 | Up | 0.84 | +3 | won | $+17.94 | $-775.58 |
| 11-06 09:30 | 2 | Up | 0.81 | +3 | LOST | $-101.32 | $-876.90 |
| 11-06 12:30 | 3 | Down | 0.84 | +1 | won | $+17.94 | $-858.96 |
| 11-06 13:30 | 2 | Down | 0.83 | +3 | won | $+19.30 | $-839.66 |
| 11-06 14:00 | 3 | Down | 0.84 | +3 | won | $+17.94 | $-821.72 |
| 11-06 18:30 | 3 | Up | 0.81 | +3 | won | $+22.14 | $-799.58 |
| 11-06 22:00 | 3 | Up | 0.90 | +3 | won | $+10.42 | $-789.16 |
| 11-06 22:45 | 2 | Down | 0.83 | +3 | won | $+19.30 | $-769.86 |
| 11-07 01:00 | 2 | Up | 0.81 | +3 | won | $+22.14 | $-747.72 |
| 11-07 02:45 | 3 | Up | 0.81 | +3 | LOST | $-101.32 | $-849.04 |
| 11-07 03:00 | 3 | Up | 0.82 | +3 | won | $+20.70 | $-828.34 |
| 11-07 03:15 | 3 | Down | 0.83 | +3 | won | $+19.30 | $-809.04 |
| 11-07 04:45 | 2 | Down | 0.80 | +3 | LOST | $-101.39 | $-910.43 |
| 11-07 09:15 | 3 | Down | 0.81 | +3 | won | $+22.14 | $-888.29 |
| 11-07 09:30 | 3 | Down | 0.84 | +3 | won | $+17.94 | $-870.35 |
| 11-07 13:45 | 2 | Up | 0.86 | +3 | won | $+15.31 | $-855.04 |
| 11-07 15:45 | 2 | Down | 0.81 | +3 | won | $+22.14 | $-832.90 |
| 11-07 16:45 | 3 | Down | 0.81 | +3 | won | $+22.14 | $-810.76 |
| 11-07 17:00 | 3 | Up | 0.83 | +3 | won | $+19.30 | $-791.46 |
