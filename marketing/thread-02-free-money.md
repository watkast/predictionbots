# X thread — post 2: "We found free money in our own data. Then we tested it live."

Post from @predictionbots when the site is live. Attach `site/posts/img/free-money-snapshot-vs-live.png` to tweet 1.
Link to the post in tweet 9 only (links in tweet 1 get down-ranked). Reply to our own tweet 1 with the link too.

---

**1/**
Our own data said the winning side of Polymarket's 5-minute Bitcoin markets was still for sale at 70¢ three seconds before the close.

192 times in four days.

We built the bot. Then we read the live order book.

Zero. Here's the mirage, with receipts.

[chart]

**2/**
The setup: these markets settle on the index averaged over the LAST 60 SECONDS. With 3 s left, 57 of 60 prints are in. The outcome is decided.

If the winner is ever offered below $1 at that moment, it's free money. People post screenshots of exactly this.

**3/**
Our recorder stored every book for 4,686 windows (BTC, ETH, SOL, XRP; 5 and 15 min). 18,732 readings of the eventual winner's price in the final 5 seconds.

97.1%: no offer at all. Nobody sells a contract about to pay $1.
1.0%: offered at 90¢ or less. The "free money."

**4/**
So we wrote Mr T: watch the index prints arrive, project the final average, and in the last 5 s buy the decided side if it's offered ≤ 90¢. Dry mode: everything except sending the order.

Two runs across seven hours. 368 windows. 1,840 readings.

**5/**
The winner was offered ZERO times in 1,503 readings.

Here is the raw book 5 s before one close. Bids for "Up" (about to win): 478 @ 95¢, 1,150 @ 96¢, 550 @ 97¢, 1,722 @ 98¢, 18,263 @ 99¢.

Offers: none. The market wasn't asleep. It was 18,000 contracts awake.

**6/**
The embarrassing part. Our first run reported 162 "qualifying" readings: the leader offered at 1¢.

It was a rounding bug. We rounded the projection to cents and on XRP (5 decimals) a tie-break flipped the leader. All 162 were the LOSER at 1¢. Correctly priced. We fixed it, reran, got zero.

**7/**
Then we went back to the 192 snapshot readings. In 190 of them the "winner" was also BID at a median of 37¢.

A side about to pay $1, bid 37 / offered 70, with 3 s left, isn't a market. It's a photo of a market from minutes earlier. The recorder kept stale snapshots. The free money was a timestamp problem.

**8/**
What this means:
• Every "cheap winner" screenshot has this problem until the timestamp is proven.
• The market is efficient exactly where people say it's broken. The 99¢ bid earns a penny to carry a ~1-in-1,000 flip risk. That edge exists; it belongs to market makers; it's fully staffed.
• There is no retail version of this trade.

**9/**
We retired Mr T as a strategy. The code stays as a measurement tool.

Full post, raw books, the CSV, the commit with the bug: predictmenot.com/posts/2026-11-08-free-money-that-wasnt

If you have a live-book window where the winner was really offered below 90¢, open an issue with the timestamp. We'll publish it.

---

## Reddit version (r/algotrading, r/Polymarket): title + first paragraph

**Title:** We thought we found free money in Polymarket's 5-minute markets (192 "cheap winners" in our own recordings). A live order book said zero in 368 windows. Here's the bug and the data.

**Body:** Data-first, no promo. Lead with the 97.1% / 1.0% split, the raw book, the rounding bug, and the stale-snapshot finding. Link the CSV and the commit. One link to the post at the end. Answer every comment with numbers.
