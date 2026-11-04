# Early Favorite v2 - forward test

Rule (frozen): at 2:00 elapsed (13:00 left), else 3:00, buy the leading side if its ask is 0.80-0.95; $100 per round; hold to settlement; taker fee 0.0695*p*(1-p). Paper only.
Forward test started 2026-10-23T00:00:00Z. Updated 2026-11-04T09:05:12Z.

**Losing: forward win rate is below break-even at the prices paid.**

| | Forward | Backtest (Oct 6-22) |
|---|---|---|
| Rounds | 192 | 272 |
| Win rate | 82.8% | 89.3% |
| Break-even win rate at prices paid | 84.9% | - |
| Average ask | 0.840 | 0.838 |
| Net at $100/round | $-511.65 | $+1,486 |
| Per round | -2.66% | +5.46% |
| Max drawdown | $-843.92 | $-403 |
| Longest losing streak | 5 | 2 |
| Entry timing | 13:00 / 12:00 left | same |

Rounds where the rule did not trigger: 978. Pending (not settled or not fetched yet): 19.

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
| 2026-11-04 | $+100.88 |

## Chart pull at the check (parallel column - not part of the rule)

Pull = EMA 9/21 and Supertrend on BRTI 1-minute candles, as drawn by research/market_pull.pine, read against the favorite. Oct 16-24 (143 rounds): 3/3 with the favorite won 92%, 1/3 won 84%, against won 78%. Small sample; this column is the forward test of that.

| Pull at the check | Rounds | Win rate | Net |
|---|---|---|---|
| with the favorite 3/3 | 142 | 84.5% | $-177.72 |
| with the favorite 1/3 | 42 | 78.6% | $-260.02 |
| against the favorite | 8 | 75.0% | $-73.91 |

## Cut at 5:00 left (parallel column - not part of the rule)

What if the position were sold at 5:00 left whenever the favorite's bid is under 45c (sold 2c under the bid, taker fee)? Backtest Oct 6-22: about +$150-220 over holding on 272 trades, under 1% of the money staked and found in-sample. This is its forward test; the traded rule stays hold-to-settlement.

| | Hold (the rule) | Cut under 45c at 5:00 left |
|---|---|---|
| Rounds with a 5:00-left price | 192 | same |
| Positions cut | - | 18 (15 would have lost, 3 would have won) |
| Net at $100/round | $-511.65 | $-441.49 (+70.16) |

## Last 20 rounds

| Window (UTC) | Min | Side | Ask | Pull | Result | P&L | Running |
|---|---|---|---|---|---|---|---|
| 11-02 22:45 | 2 | Up | 0.82 | +1 | won | $+20.70 | $-632.08 |
| 11-02 23:00 | 2 | Down | 0.84 | +3 | won | $+17.94 | $-614.14 |
| 11-03 00:15 | 3 | Up | 0.89 | +3 | won | $+11.60 | $-602.54 |
| 11-03 03:45 | 2 | Up | 0.83 | +1 | won | $+19.30 | $-583.24 |
| 11-03 04:00 | 2 | Down | 0.81 | +1 | won | $+22.14 | $-561.10 |
| 11-03 04:30 | 2 | Down | 0.80 | -1 | won | $+23.61 | $-537.49 |
| 11-03 05:30 | 3 | Down | 0.80 | +3 | LOST | $-101.39 | $-638.88 |
| 11-03 06:15 | 2 | Up | 0.83 | -1 | won | $+19.30 | $-619.58 |
| 11-03 06:30 | 2 | Up | 0.82 | +3 | won | $+20.70 | $-598.88 |
| 11-03 06:45 | 2 | Down | 0.80 | +3 | won | $+23.61 | $-575.27 |
| 11-03 07:15 | 3 | Up | 0.80 | +3 | won | $+23.61 | $-551.66 |
| 11-03 12:00 | 2 | Down | 0.84 | +3 | LOST | $-101.11 | $-652.77 |
| 11-03 13:30 | 2 | Up | 0.88 | +3 | won | $+12.80 | $-639.97 |
| 11-03 14:00 | 3 | Down | 0.92 | +3 | won | $+8.14 | $-631.83 |
| 11-03 18:30 | 2 | Up | 0.83 | +3 | won | $+19.30 | $-612.53 |
| 11-04 01:00 | 3 | Down | 0.83 | +1 | won | $+19.30 | $-593.23 |
| 11-04 03:00 | 2 | Down | 0.82 | +3 | won | $+20.70 | $-572.53 |
| 11-04 04:45 | 3 | Up | 0.85 | +3 | won | $+16.60 | $-555.93 |
| 11-04 07:30 | 2 | Down | 0.81 | -1 | won | $+22.14 | $-533.79 |
| 11-04 08:45 | 3 | Up | 0.81 | +3 | won | $+22.14 | $-511.65 |
