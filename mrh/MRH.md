# Mr. H — Coinbase hopper, PAPER

Updated 2026-11-11T01:30:34Z · scans 978 · universe 110 coins (USD pairs with ≥ $100k 24-h volume) · fees 0.9% taker each way · start $4.00

## Books (one position at a time, all-in every hop)

| profile | bankroll | vs start | peak | hops | win % | avg net/hop | fees paid | open |
|---|---|---|---|---|---|---|---|---|
| aggressive | $2.29 | -42.7% | $4.00 | 16 | 19% | -3.46% | $0.897 | LIGHTER-USD @ 3.391 |
| standard | $2.46 | -38.4% | $4.00 | 18 | 17% | -2.57% | $1.048 | RSR-USD @ 0.001647 |
| aggressive_swap | $1.81 | -54.8% | $4.02 | 32 | 22% | -2.33% | $1.767 | — |

## Signal forward returns (every signal, whether or not a book took it)

| profile | signals | scored | median +15m | median +1h | median +4h | % beat 1.8% at +1h | median 4%-trail hop net | max run-up (med) | max drawdown (med) |
|---|---|---|---|---|---|---|---|---|---|
| aggressive | 158 | 122 | -0.53% | -1.03% | -3.20% | 27% | -4.29% | +6.27% | -8.61% |
| standard | 168 | 134 | -0.37% | -0.26% | -1.18% | 17% | -2.20% | +2.87% | -4.26% |

## Aggressive signals by BTC regime (BTC's own move in the hour before the signal)

| BTC 1h | signals | median +1h | median 4%-trail hop net | % beat 1.8% at +1h |
|---|---|---|---|---|
| ≤ −0.5% (downdraft) | 7 | +4.04% | -1.09% | 57% |
| −0.5% … +0.5% (flat) | 92 | -2.17% | -4.96% | 24% |
| ≥ +0.5% (bid under the market) | 11 | +1.51% | -0.47% | 36% |

## Verdict

**Not yet.** Needs 40 scored aggressive signals (122 so far) and 30 closed aggressive hops (16 so far) before this says anything. Until then every number above is noise.

## Last 20 hops

| time (UTC) | book | coin | in | out | held | net | reason | bankroll |
|---|---|---|---|---|---|---|---|---|
| 11-10T11:10 | aggressive | NCT | 0.01058 | 0.00995 | 35 m | -7.64% | trail | $2.54 |
| 11-10T11:10 | aggressive_swap | NCT | 0.01058 | 0.00995 | 35 m | -7.64% | trail | $2.63 |
| 11-10T11:35 | aggressive | RITUAL | 0.03787 | 0.038 | 25 m | -1.45% | trail | $2.50 |
| 11-10T11:35 | aggressive_swap | RITUAL | 0.03787 | 0.038 | 25 m | -1.45% | trail | $2.59 |
| 11-10T12:05 | standard | TON | 1.1051 | 1.074 | 565 m | -4.56% | trail | $2.70 |
| 11-10T13:20 | aggressive | MEZO | 0.004355 | 0.004191 | 10 m | -5.49% | trail | $2.37 |
| 11-10T13:20 | standard | MEZO | 0.004355 | 0.004191 | 10 m | -5.49% | trail | $2.55 |
| 11-10T13:20 | aggressive_swap | MEZO | 0.004355 | 0.004191 | 10 m | -5.49% | trail | $2.45 |
| 11-10T14:30 | standard | CAP | 0.10837 | 0.11146 | 45 m | +1.01% | trail | $2.57 |
| 11-10T14:35 | aggressive | MEZO | 0.004251 | 0.00413 | 55 m | -4.59% | trail | $2.26 |
| 11-10T14:35 | aggressive_swap | MEZO | 0.004251 | 0.00413 | 55 m | -4.59% | trail | $2.34 |
| 11-10T17:47 | aggressive_swap | LIGHTER | 3.391 | 3.372 | 188 m | -2.34% | swap | $2.28 |
| 11-10T18:05 | aggressive_swap | RSC | 0.04827 | 0.0482 | 17 m | -1.93% | trail | $2.24 |
| 11-10T18:10 | standard | LIGHTER | 3.391 | 3.335 | 210 m | -3.41% | trail | $2.49 |
| 11-10T19:10 | aggressive_swap | MEZO | 0.004292 | 0.00408 | 40 m | -6.64% | trail | $2.09 |
| 11-10T22:20 | aggressive_swap | XCN | 0.003297 | 0.003264 | 150 m | -2.77% | swap | $2.03 |
| 11-10T22:50 | aggressive_swap | RITUAL | 0.03559 | 0.03409 | 30 m | -5.93% | trail | $1.91 |
| 11-11T00:30 | aggressive_swap | RITUAL | 0.03657 | 0.03812 | 85 m | +2.37% | trail | $1.96 |
| 11-11T01:05 | standard | USELESS | 0.13553 | 0.13817 | 390 m | +0.12% | trail | $2.49 |
| 11-11T01:15 | aggressive_swap | NCT | 0.00971 | 0.00913 | 15 m | -7.66% | trail | $1.81 |

## Last 15 signals

| time (UTC) | profile | coin | impulse | vol× | >2h high | spread | taken | +1h | +4h |
|---|---|---|---|---|---|---|---|---|---|
| 11-10T21:55 | standard | RITUAL | +2.1% | 3.0 | y | 0.11% | in_position | … | … |
| 11-10T22:00 | aggressive | CAP | +2.4% | 3.7 | n | 0.29% | in_position | … | … |
| 11-10T22:00 | standard | RITUAL | +1.0% | 7.8 | y | 0.08% | in_position | … | … |
| 11-10T22:20 | aggressive | RITUAL | +2.3% | 5.3 | n | 0.11% | in_position | … | … |
| 11-10T22:25 | aggressive | NCT | +2.0% | 3.7 | n | 0.53% | in_position | … | … |
| 11-10T22:35 | aggressive | MEZO | +3.2% | 4.1 | n | 0.20% | in_position | … | … |
| 11-10T23:05 | aggressive | RITUAL | +5.9% | 9.8 | n | 0.08% | in_position | … | … |
| 11-10T23:10 | aggressive | RITUAL | +10.6% | 36.2 | y | 0.08% | in_position | … | … |
| 11-10T23:10 | standard | RITUAL | +10.6% | 36.2 | y | 0.08% | in_position | … | … |
| 11-11T00:05 | aggressive | RITUAL | +2.1% | 6.6 | n | 0.10% | in_position | … | … |
| 11-11T00:15 | standard | PUMP | +1.1% | 16.7 | y | 0.08% | in_position | … | … |
| 11-11T01:00 | aggressive | NCT | +2.8% | 3.7 | n | 0.10% | in_position | … | … |
| 11-11T01:05 | standard | RSC | +1.4% | 4.0 | y | 1.22% | spread | … | … |
| 11-11T01:30 | standard | RSR | +1.7% | 7.2 | y | 0.12% | y | … | … |
| 11-11T01:30 | standard | NEAR | +1.7% | 9.6 | y | 0.02% | in_position | … | … |
