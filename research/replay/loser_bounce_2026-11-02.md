# The "loser bounce": buy the side that fell early, sell at the first flip — tested on 12 markets

Theory under test (Noah, Nov 2): early in a window one side runs, the other side's price drops to 30–40¢ (sometimes the 20s);
buy that side, wait for the first flip back and sell for ~+20%; one trade a round. Rounds that never flip are rare.

Data: Mr. P recorder, Oct 29 – Nov 2 2026, 1-second CF Benchmarks RTI prints for every coin from Kalshi's index feed
(`mrp/mrp_extract_windows.py`), Polymarket US price to beat and settlement from the gateway. The settlement rule (mean of the
60 prints in the last minute) reproduces every one of the 2,970 settlements across BTC / ETH / SOL / XRP × 5-min / 15-min /
1-hour, so the index paths are exactly what settles these markets.

## 1. The flip statistic is real

Share of rounds where the side leading after the first minute is behind at some later second:

| market | 5-min | 15-min | 1-hour |
|---|---|---|---|
| BTC | 60% (690 rounds) | **72%** (224) | 88% (52) |
| ETH | 63% | 72% | 87% |
| SOL | — | 73% | 92% |
| XRP | — | 71% | 94% |

Most 15-minute rounds flip at least once after minute one. The memory of "never a round that held" is mostly right.

## 2. But the price of the trailing side already contains it — and then some

Where the recorder saw a real quote, the trailing side's ask versus a calibrated settlement model (the same Brownian model the
cockpit uses, σ ×1.3), by the model's own band and the time left — BTC 15-min, 224 rounds:

| time left | model says 20–30% | model says 30–40% | that side actually won |
|---|---|---|---|
| 10–14.5 min | market ask **+9.3¢** above the model (n = 536) | **+5.3¢** (486) | 24% / 38% |
| 5–10 min | +8.0¢ (2,262) | +4.9¢ (2,142) | 38% / 41% |
| 2–5 min | +6.2¢ (2,343) | +3.3¢ (2,292) | 35% / 44% |

The side that just fell is the one everybody wants to buy for the bounce, and the market charges a premium for it: 5–9¢ over
its calibrated chance early in the round. The same holds on ETH (+4 to +7¢) and XRP (+6 to +10¢); SOL is the exception
(roughly fair). The mirror image is the leader trading *below* its chance — which is exactly the discount the cockpit's
strategy buys.

## 3. The strategy, simulated — one trade a round, taker fees both ways

Buy the trailing side the first second its price is in the band (entry window = the first third of the round, after 30 s),
sell at the first second a bid reaches the target, else hold to the bell. Prices = the model proxy (fair value), with real
quotes used wherever one existed within 5 s. P&L per trade in cents per $1 share; the last column is the total on a $20 stake.

BTC 15-min (224 rounds):

| buy band | sell at | trades | sold at target | held & lost | P&L / trade | total @ $20 |
|---|---|---|---|---|---|---|
| 20–30¢ | first flip (50¢) | 212 | 125 | 87 | +3.8¢ | +$652 |
| 20–30¢ | +20% | 212 | 180 | 32 | +3.0¢ | +$507 |
| 30–40¢ | first flip | 213 | 152 | 61 | +0.2¢ | +$24 |
| 30–40¢ | +20% | 213 | 172 | 41 | −1.0¢ | −$127 |
| 35–45¢ | first flip | 204 | 159 | 45 | −1.0¢ | −$104 |
| 40–48¢ | +20% | 196 | 156 | 40 | −0.7¢ | −$59 |

Those are *fair-price* numbers. Add the measured premium (the trailing side costs 5–9¢ more than the model in these bands
early in the round) and every cell is negative: the best one, 20–30¢ sold at the flip, goes from +3.8¢ to about −4¢ a trade.
Not one held position won at the bell in any configuration — a side that never flipped never settled in its favor.

Other markets, same best-looking cell (20–30¢, sell at the first flip), fair-price proxy:

| market | trades | P&L / trade | held & lost | premium the market adds |
|---|---|---|---|---|
| ETH 15-min | 205 | +2.0¢ | 86 | +4.6 to +7.0¢ |
| XRP 15-min | 206 | +2.2¢ | 88 | +6.3 to +9.5¢ |
| SOL 15-min | 97 | −5.7¢ | 51 | ≈ 0 |
| BTC 5-min | 508 | −3.4¢ | 274 | +6.4¢ |
| ETH 5-min | 497 | −2.4¢ | 268 | +8.7¢ |
| BTC 1-hour | 51 | +5.2¢ | 17 | +7.3¢ (few quotes) |
| ETH / XRP 1-hour | 48 / 51 | +5.9¢ / +4.5¢ | 15 / 17 | +10 to +18¢ |
| SOL 1-hour | 25 | −6.8¢ | 13 | — |

5-minute markets lose even at fair prices (the flip rate is lower: 60%, and there is no time for the bounce). The hourly
markets look best at fair prices (flip rate 88–94%) but the market's premium on the trailing side there is the largest of all,
so the net is negative too. 30–40¢ is nowhere a sweet spot; the +20% target is worse than selling at the flip everywhere,
because it sells the winners early and keeps the losers.

## Verdict

No sweet spot. The theory's premise is true — the early leader flips in 7 rounds out of 10 — but the payoff is asymmetric
(+15–25¢ when it flips, −25–40¢ when it doesn't) and the market prices the trailing side 5–9¢ *above* its true chance early
in the round, precisely because it is the bounce everyone is waiting for. Buying it is paying a premium for a coin flip. The
profitable side of the same observation is the one the cockpit already trades: the leader, priced *below* its chance for a
few seconds, bought at a discount and sold when the market overpays.

Caveats: 4–5 days of data; early-round quotes are sparse (the premium is measured where quotes existed, ~1,000–2,500
samples per band); the fair-price proxy is the cockpit's model, which calibrates well on BTC 15-min (60–65% → 60%
realized) and was not re-calibrated per coin.

Re-run: `python3 mrp/mrp_extract_windows.py <data dir> fams/` then `node research/replay/bounce.js fams/btc15m.json 900 BTC`.
