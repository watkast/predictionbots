# X thread — launch post #1 (post from the PredictMeNot account once the site is live; attach the two charts)

1/ We built a bot to buy coins the moment they spike — the most popular idea in retail crypto — then replayed the exact rule over 30 days of Coinbase data. 112 coins. 1,172 spikes.

It loses. Here's the whole thing in two charts. 🧵

[chart: pump-candle-path.png]

2/ The rule: a 5-min candle closes up ≥2% on ≥3× normal volume → buy at the close, trail a 4% stop.

Result: 24% winners. −1.86% per trade after fees. Median trade −3.55%.

3/ The median path AFTER the signal: −0.4% at 15 min, −1.2% at 1 h, −2.3% at 4 h.

The spike candle is, on median, the local top. You are buying the moment everyone who knew something has already finished acting.

4/ Fees decide the sign. Strip Coinbase's 0.9% taker fee out and the gross is −0.1% — a coin flip. Switch to maker orders (0.5%) and the bleed shrinks to −1.1%. You cannot fee-optimize a signal that has no edge.

5/ Every trailing stop loses. Waiting one candle for "confirmation" is worse (−2.0%): confirmation is just a later entry into the same give-back. No hour, no BTC regime, no volume filter flips it.

6/ The only green corner: spikes ≥5% with an 8% trail (+0.3%, n=110) and ≥10% (+3.6%, n=24). Even there the median trade loses ~3% — a fat right tail pays for it. One hop made +212%. A lottery ticket with a slightly positive mean.

[chart: pump-candle-heatmap.png]

7/ Why: three groups make a pump — the people who manufactured it, the people with foreknowledge, and bots that buy 200 ms after an announcement. A +2% candle is the footprint of all three having acted. Buying it makes you the late money by construction.

8/ What we did: retired "buy the spike" as a strategy, kept it as a tiny published lottery ticket, and moved the hunt to moments where the outcome is already decided and the price hasn't noticed — in prediction markets.

Next post: what 4 days of recording Polymarket at 1-second resolution found in the final 3 seconds before settlement.

9/ All of it is public — code, every signal with its forward returns, and our live bots' trades, including the losers:
predictmenot.com
github.com/watkast/predictionbots

We stopped trading and measure instead: fees, bots, and our own full ledger. predictmenot.com
