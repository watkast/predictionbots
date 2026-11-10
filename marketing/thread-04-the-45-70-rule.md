# X thread — post 3: the "buy at 45¢, sell at 70¢" rule on 689 recorded markets

Attach `site/posts/img/retail-rule-45-70.png` to tweet 1. Link in the last tweet and in a reply.

**1/**
The most-quoted retail rule for 15-minute Bitcoin markets: buy a side at 45¢ or less, sell it at 70¢.

We replayed it on 689 recorded Polymarket US markets with the real order books and the real fees.

−$219 on $2,416 staked. Here's the shape of it.

[chart]

**2/**
Before fees: −$59 (−2.4%). A coin flip with a slight lean the wrong way.
After fees: −$219 (−9.0%).

Fees were $160. Three-quarters of the loss was the cover charge, not the market.

**3/**
Why the curve looks like that:

331 times the side hit 70¢ → sell for about +$3.06.
358 times it never got there → held to settlement → ALL 358 lost, −$3.44 each.

Win small, lose whole. 48% × $3.06 is less than 52% × $3.44 before a cent of fees.

**4/**
"Cheap" was worse. Entered near 40¢: −7% of stake. Near 30¢: −8%. Near 20¢: −35%. Near 10¢: −43%.

Cheap contracts are cheap because the market expects them to lose.

**5/**
Is 689 enough? Average trade −$0.32, standard error $0.13: distinguishable from zero. Not distinguishable from "the fee and nothing else." No detectable edge, a certain cost.

**6/**
Control in the same windows (buy Up at the open, hold): −21%. Bitcoin fell; Up settled in only 42% of windows. That's drift + a 3.5% fee, not a strategy, and it's why every benchmark row ships with a control.

**7/**
Method: the rule as published, our recorder's books, fills only where the book showed size, the fee schedule in force on each trade's date (6.95% → 9.5% on Nov 6). Paper fills aren't real fills; real can be worse.

**8/**
Full post, every trade, the extracted windows and the replay code: predictmenot.com/posts/2026-11-08-the-45-70-rule-on-689-markets

Vendors: publish your rule and we test it. We never need your code or your keys.
