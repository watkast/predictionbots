---
title: "How a 5-minute Bitcoin market settles on Polymarket US and Kalshi (and why the last seconds aren't free money)"
updated: 2026-11-08
summary: "Up/Down crypto markets settle on the CF Benchmarks index averaged over the final 60 seconds of the window, not on the last print. What that rule means second by second, why the order book is already at 99¢ by then, and what 4,686 recorded windows show about the one-in-a-thousand flip."
faq: ["How does a Polymarket US 5-minute Bitcoin market settle?|Up pays $1 if the CF Benchmarks Bitcoin index, averaged over the last 60 seconds of the five-minute window, is above the price at the open; Down pays $1 otherwise. The settlement value is an average, not the final print.", "Can I buy the winning side in the last seconds?|Not in practice. In 4,686 recorded windows the winning side had no offer at all in 97% of final-second readings, and in a seven-hour live test it was never offered. The winning side is bid at 99¢ by the thousand; the losing side is offered at 1¢.", "How often does the leader in the last 3 seconds lose?|About one window in a thousand: 4 of 4,686 in our recordings, and none of them with a margin above 5 basis points.", "Is a 5-minute crypto market predictable?|Not at that horizon by any method we have tested. Our 30-day replay of the most popular momentum entry rule lost on 76% of trades."]
---

Every five minutes, Polymarket US and Kalshi open a new Bitcoin market with two sides. The rule that decides it is short, and most people never read it:

> **Up** pays $1 if the CF Benchmarks Bitcoin index, **averaged over the last 60 seconds** of the window, is above the index value at the open. **Down** pays $1 otherwise.

Everything about how the market behaves follows from the word *averaged*.

## What the average does to the last minute

The index prints once a second. Sixty prints go into the settlement value. With 30 seconds left, half of them are already in the average and cannot change. With 3 seconds left, 57 of 60 are in. For the outcome to flip in the final three seconds, the index would have to move, in three prints, by more than the whole first 57 prints have moved it away from the open.

In our recordings of 4,686 windows (4–7 November 2026, BTC, ETH, SOL and XRP, 5- and 15-minute), the side leading with three seconds left lost **4 times**: about one in a thousand. None of those four had a margin above 5 basis points at that moment. Above that margin, in our data, the leader never lost.

So the outcome is, for practical purposes, decided before the clock runs out. That is not a flaw in the market; it is the rule working as written.

## Why that is not free money

If the outcome is decided and the winning side were still for sale below $1, you could buy it and collect. People post screenshots claiming exactly that. We believed our own recordings when they showed it, built a bot to take it, and then read the live order book:

- In 97.1% of final-second readings, the winning side had **no offer at all**. Nobody sells a contract about to pay $1.
- In a seven-hour live test across 368 windows, the winning side was offered **zero times**. Five seconds before one close, "Up" (about to win) was bid for 478 contracts at 95¢, 1,150 at 96¢, 550 at 97¢, 1,722 at 98¢ and 18,263 at 99¢, with nothing offered. "Down" was offered at 1¢ by the thousand and bid by nobody.
- The 192 "cheap winners" in our recordings were stale snapshots: the recorder had kept a book from minutes earlier. The same mistake is in every screenshot you will see of this trade.

The one real edge in the last minute belongs to whoever posts the 99¢ bid and carries the one-in-a-thousand flip for a penny. That is a market maker's job, it is fully staffed, and on Polymarket US it is fee-free for them (resting orders pay nothing) while you would pay a taker fee for a cent of upside. [The whole investigation, with the raw books.](/posts/2026-11-08-free-money-that-wasnt.html)

## What the market looks like at the open

At the open the price is near 50¢ by construction: the window has not started, and five-minute moves have no measurable predictability. Our 30-day replay of the most popular rule, buy the coin that is pumping right now, produced 1,172 trades, 24% winners and −1.86% a trade after fees; the signal itself was a coin flip and the fee decided the sign. [That replay, with the data.](/posts/2026-11-08-we-bought-the-pump-candle.html)

So the honest description of a five-minute crypto market is: a coin flip at the open, a decided result in the last minute, and a fee on every click in between. The fee is the only part you can control, which is why the [True Cost calculator](/#truecost) and the [simulator](/simulate.html?venue=pmus) start there.

## The venues' rules, in their words

- Polymarket US: the market's rules text names the CF Benchmarks index and the 60-second average; the settlement value is published with the market when it resolves.
- Kalshi: the crypto 5-minute and 15-minute series settle on the same CF Benchmarks index using a final-minute running average that Kalshi publishes in its own data feed; the series page lists the settlement source.

Both venues can change a rule; the date on this page is when we last checked them.

*Data: `windows.csv` and `mrt/live.jsonl` on the `mrp-data` branch of [github.com/watkast/predictionbots](https://github.com/watkast/predictionbots). Nothing here is investment advice.*
