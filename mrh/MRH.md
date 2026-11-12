# Mr. H — Coinbase hopper, PAPER

Updated 2026-11-12T05:00:36Z · scans 1268 · universe 110 coins (USD pairs with ≥ $100k 24-h volume) · fees 0.9% taker each way · start $4.00

## Books (one position at a time, all-in every hop)

| profile | bankroll | vs start | peak | hops | win % | avg net/hop | fees paid | open |
|---|---|---|---|---|---|---|---|---|
| aggressive | $2.00 | -50.1% | $4.00 | 21 | 19% | -3.40% | $1.086 | RITUAL-USD @ 0.043 |
| standard | $2.30 | -42.6% | $4.00 | 24 | 21% | -2.10% | $1.311 | RITUAL-USD @ 0.0461 |
| aggressive_swap | $0.99 | -75.3% | $4.02 | 44 | 18% | -3.02% | $2.059 | — |

## Signal forward returns (every signal, whether or not a book took it)

| profile | signals | scored | median +15m | median +1h | median +4h | % beat 1.8% at +1h | median 4%-trail hop net | max run-up (med) | max drawdown (med) |
|---|---|---|---|---|---|---|---|---|---|
| aggressive | 204 | 161 | -0.93% | -1.87% | -4.11% | 25% | -4.70% | +6.16% | -8.77% |
| standard | 214 | 167 | -0.37% | -0.43% | -1.07% | 16% | -2.51% | +3.01% | -4.50% |

## Aggressive signals by BTC regime (BTC's own move in the hour before the signal)

| BTC 1h | signals | median +1h | median 4%-trail hop net | % beat 1.8% at +1h |
|---|---|---|---|---|
| ≤ −0.5% (downdraft) | 7 | +4.04% | -1.09% | 57% |
| −0.5% … +0.5% (flat) | 129 | -2.17% | -5.01% | 22% |
| ≥ +0.5% (bid under the market) | 13 | +0.74% | -1.68% | 31% |

## Verdict

**Not yet.** Needs 40 scored aggressive signals (161 so far) and 30 closed aggressive hops (21 so far) before this says anything. Until then every number above is noise.

## Last 20 hops

| time (UTC) | book | coin | in | out | held | net | reason | bankroll |
|---|---|---|---|---|---|---|---|---|
| 11-11T05:30 | standard | RITUAL | 0.03879 | 0.03722 | 75 m | -5.77% | trail | $2.29 |
| 11-11T05:30 | aggressive_swap | RITUAL | 0.03879 | 0.03722 | 75 m | -5.77% | trail | $1.54 |
| 11-11T05:45 | aggressive_swap | FORTH | 0.14901 | 0.14285 | 15 m | -5.85% | trail | $1.45 |
| 11-11T07:50 | standard | XCN | 0.00342 | 0.003902 | 20 m | +12.05% | trail | $2.57 |
| 11-11T07:55 | aggressive_swap | RITUAL | 0.03382 | 0.03261 | 75 m | -5.31% | trail | $1.37 |
| 11-11T08:15 | aggressive_swap | XCN | 0.004219 | 0.003955 | 5 m | -7.94% | trail | $1.26 |
| 11-11T08:40 | aggressive | LIGHTER | 3.391 | 3.368 | 1080 m | -2.46% | trail | $2.20 |
| 11-11T09:15 | standard | USELESS | 0.13922 | 0.13507 | 75 m | -4.72% | trail | $2.45 |
| 11-11T12:25 | aggressive_swap | TON | 1.1634 | 1.1919 | 220 m | +0.61% | swap | $1.27 |
| 11-11T12:30 | aggressive_swap | FORTH | 0.13809 | 0.13164 | 5 m | -6.38% | trail | $1.19 |
| 11-11T14:20 | standard | TON | 1.1858 | 1.2097 | 265 m | +0.19% | trail | $2.45 |
| 11-11T15:10 | aggressive | TON | 1.1634 | 1.2009 | 385 m | +1.37% | trail | $2.23 |
| 11-11T15:10 | aggressive_swap | TON | 1.2182 | 1.2009 | 160 m | -3.19% | trail | $1.15 |
| 11-11T21:10 | aggressive | MEZO | 0.004304 | 0.00414 | 25 m | -5.53% | trail | $2.11 |
| 11-11T21:10 | aggressive_swap | MEZO | 0.004304 | 0.00414 | 25 m | -5.53% | trail | $1.09 |
| 11-11T21:45 | aggressive | MEZO | 0.004167 | 0.004073 | 15 m | -4.01% | trail | $2.02 |
| 11-11T21:45 | aggressive_swap | MEZO | 0.004167 | 0.004073 | 15 m | -4.01% | trail | $1.05 |
| 11-12T02:40 | aggressive | RITUAL | 0.03951 | 0.03807 | 68 m | -5.37% | trail | $1.92 |
| 11-12T02:40 | aggressive_swap | RITUAL | 0.03951 | 0.03807 | 68 m | -5.37% | trail | $0.99 |
| 11-12T04:25 | standard | FLR | 0.005467 | 0.00536 | 825 m | -3.71% | trail | $2.36 |

## Last 15 signals

| time (UTC) | profile | coin | impulse | vol× | >2h high | spread | taken | +1h | +4h |
|---|---|---|---|---|---|---|---|---|---|
| 11-11T21:30 | aggressive | MEZO | +2.6% | 3.2 | n | 0.05% | y | -4.9% | -7.2% |
| 11-11T21:35 | aggressive | MEZO | +4.0% | 3.4 | n | 0.18% | in_position | -8.6% | -11.1% |
| 11-11T21:35 | standard | FLR | +1.1% | 7.2 | y | 0.09% | in_position | … | … |
| 11-11T23:05 | aggressive | FORTH | +6.1% | 7.6 | n | 2.55% | spread | … | … |
| 11-12T01:32 | aggressive | RITUAL | +6.6% | 16.8 | y | 0.10% | y | … | … |
| 11-12T01:32 | standard | RITUAL | +6.6% | 16.8 | y | 0.10% | in_position | … | … |
| 11-12T01:55 | aggressive | MEZO | +2.1% | 6.2 | n | 0.82% | spread | … | … |
| 11-12T03:50 | aggressive | RITUAL | +4.4% | 7.4 | y | 1.57% | spread | … | … |
| 11-12T03:50 | standard | RITUAL | +4.4% | 7.4 | y | 1.57% | spread | … | … |
| 11-12T03:55 | standard | RITUAL | +1.2% | 7.7 | y | 0.05% | in_position | … | … |
| 11-12T04:05 | aggressive | RITUAL | +3.6% | 8.5 | y | 0.02% | y | … | … |
| 11-12T04:05 | standard | RITUAL | +3.6% | 8.5 | y | 0.02% | in_position | … | … |
| 11-12T04:10 | aggressive | RITUAL | +2.7% | 6.6 | n | 0.09% | in_position | … | … |
| 11-12T04:50 | aggressive | RITUAL | +5.7% | 4.7 | y | 0.39% | in_position | … | … |
| 11-12T04:50 | standard | RITUAL | +5.7% | 4.7 | y | 0.39% | y | … | … |
