# Early Favorite: manual session playbook

The rule (tested on Oct 6-22, 2026; forward test running since Oct 22 08:30 UTC):
at 13:00 left, else 12:00 left, buy the favorite only if its Ask is 80-94c. Then hold to the end.

## Before you start
- Pick one stake and use it every round. No doubling after a loss.
- The test's worst run lost about 5 stakes and its worst day about 3. Keep each stake at 1/8 or less
  of the money set aside for this. With about $425, that is $50 a round.
- Optional: open the **Early Favorite Timer** chart (BTC/USD, 1 minute) for the pings below.

## Each round
1. **13:00 left** (clock :02, :17, :32, :47). Open the BTC Up or Down 15m market.
2. **Find the favorite**: the side priced higher. Tap it and read the **Ask** in the order ticket
   ("Bid xx c, Ask xx c"). Use the Ask, not the percentage on the button.
3. **Ask 80-94c: buy.** Limit at the Ask. Shares = stake / price:

   | Ask | $50 | $100 |
   |---|---|---|
   | 80-84c | 60 | 120 |
   | 85-89c | 57 | 115 |
   | 90-94c | 54 | 108 |

   Not filled in about 15 seconds? Re-read the Ask. Still 80-94c: move the limit to it. Otherwise cancel.
4. **Under 80c or 95c+: wait for 12:00 left** (:03, :18, :33, :48). Pick the favorite again and apply
   the same 80-94c test. Still no: skip the round. Never enter after 12:00 left.
5. **Hold to 0:00. Do nothing.** No sell order, no Cash out, no adding. A win pays $1 a share on its own.

## What to expect
- About 1 round in 4 qualifies: roughly one trade an hour.
- About 1 in 9 trades loses the whole stake. One loss erases about 5-6 wins. Break-even is about
  an 85% win rate; the test ran 89%.
- A normal day has 2-3 losses. The worst test day lost 6 of 25. That is the rule, not a malfunction.

## Chart alerts (Early Favorite Timer)
- Create alert -> Condition: **Early Favorite Timer** -> **Any alert() function call** (says UP or DOWN
  and the estimate). Or pick **EF heads-up**, **EF check 1**, **EF check 2** individually and set
  **Once Per Bar**, not Once Per Bar Close (that fires a minute late).
- Turn on the app notification. Set expiration to open-ended.
- If the HUD target and Polymarket's target differ by more than $5, put the difference in
  "Target offset".
