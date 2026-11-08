# Mr. P — sports radar

Updated 2026-11-08T00:52:15Z by `run-20261107T2340-42411256890` (last 7 days). Read-only scanner of every sports market on Polymarket US and Kalshi — it never places orders.
Kit: `mrp/mrp_sports_radar.py` on the `mrp` branch. Raw tape: `mrp/radar/<run>/`.

# Sports radar report

records 5,076,800 | 2026-11-05 00:49Z → 00:49Z | runs 12 | pairs matched 1609 | errors {'sp.stream': 17, 'radar': 2}

## Catalogue (latest inventory, 23:51Z)

Polymarket US sports events 4931 of 5855 active events; Kalshi near-term sports markets 3419 in 691 events; calls so far {'pm': 51, 'k': 1098}; MB {'pm': 159003695, 'k': 86506486}

| venue | sport / league / type | markets | two-sided | med spread | vol 24h |
|---|---|---|---|---|---|
| pm | football / nfl / futures | 4106 | 60% | 0.010 | 0 |
| pm | football / cfb / futures | 1610 | 39% | 0.010 | 0 |
| pm | basketball / nba / futures | 1450 | 52% | 0.020 | 0 |
| pm | ice-hockey / nhl / futures | 779 | 92% | 0.010 | 0 |
| pm | basketball / cbb / basketball_team_full_game_winner | 765 | 20% | 0.040 | 0 |
| pm | basketball / wcbb / basketball_team_full_game_winner | 745 | 16% | 0.080 | 0 |
| k | KXNCAAFGAME / College Football Game | 596 | 100% | 0.210 | 52405825 |
| pm | soccer / epl / futures | 437 | 86% | 0.010 | 0 |
| pm | basketball / cbb / futures | 396 | 88% | 0.010 | 0 |
| pm | tennis / utr / tennis_match_winner | 364 | 12% | 0.020 | 0 |
| pm | soccer / ucl / futures | 285 | 79% | 0.010 | 0 |
| pm | tennis / itfme / tennis_match_winner | 262 | 37% | 0.010 | 0 |
| pm | table-tennis / setkameua / table_tennis_match_winner | 252 | 77% | 0.170 | 0 |
| pm | football / cfb / football_team_full_game_winner | 250 | 64% | 0.165 | 0 |
| pm | soccer / lal / futures | 147 | 49% | 0.010 | 0 |
| pm | tennis / itfwo / tennis_match_winner | 146 | 45% | 0.010 | 0 |
| pm | mma / ufc / futures | 145 | 83% | 0.010 | 0 |
| pm | boxing / boxing / futures | 145 | 0% | - | 0 |
| pm | tennis / atp / tennis_match_winner | 136 | 63% | 0.010 | 0 |
| pm | macro /  / futures | 123 | 71% | 0.010 | 0 |
| pm | golf / austcham / futures | 116 | 100% | 0.499 | 0 |
| pm | basketball / nba / basketball_team_full_game_winner | 109 | 94% | 0.260 | 0 |
| pm | motorsports / f1 / futures | 101 | 48% | 0.090 | 0 |
| pm | soccer / sea / futures | 88 | 85% | 0.010 | 0 |
| pm | tennis / atp / futures | 85 | 36% | 0.010 | 0 |
| pm | golf / worlwide / futures | 82 | 18% | 0.002 | 0 |
| pm | soccer / bun / futures | 80 | 84% | 0.010 | 0 |
| pm | soccer / lg1 / futures | 79 | 86% | 0.010 | 0 |
| pm | macro / usgas / futures | 79 | 72% | 0.020 | 0 |
| pm | soccer / unl / soccer_team_full_time_winner | 78 | 99% | 0.040 | 0 |
| pm | golf / lpga / futures | 77 | 4% | 0.222 | 0 |
| pm | tennis / wta / futures | 75 | 44% | 0.010 | 0 |
| pm | baseball / mlb / futures | 72 | 65% | 0.001 | 0 |
| pm | soccer / afcq / soccer_team_full_time_winner | 72 | 56% | 0.460 | 0 |
| pm | golf / abudhabc / futures | 70 | 20% | 0.005 | 0 |
| pm | macro / usdsl / futures | 63 | 8% | 0.140 | 0 |
| pm | tennis / atpdb / tennis_match_winner | 62 | 8% | 0.020 | 0 |
| pm | esports / dota2 / esports_match_winner | 60 | 53% | 0.275 | 0 |
| pm | table-tennis / czechligapro / table_tennis_match_winner | 56 | 11% | 0.470 | 0 |
| k | KXNFLGAME / NFL Game | 56 | 100% | 0.010 | 2015442 |
| pm | esports / cs2 / esports_match_winner | 55 | 75% | 0.080 | 0 |
| pm | technology /  / futures | 52 | 79% | 0.010 | 0 |
| pm | golf / masttour / futures | 52 | 100% | 0.496 | 0 |
| pm | motorsports / nascar / futures | 50 | 38% | 0.020 | 0 |
| pm | table-tennis / setkamecz / table_tennis_match_winner | 48 | 69% | 0.170 | 0 |
| pm | soccer / mls / futures | 42 | 95% | 0.010 | 0 |
| pm | table-tennis / setkamemd / table_tennis_match_winner | 37 | 0% | - | 0 |
| pm | soccer / lmx / futures | 36 | 58% | 0.120 | 0 |
| pm | soccer / uel / futures | 36 | 0% | - | 0 |
| pm | soccer / uecl / futures | 36 | 0% | - | 0 |
| pm | esports / ebattlesefwca / efootball_team_full_time_winner | 36 | 94% | 0.010 | 0 |
| pm | soccer / efl2 / soccer_team_full_time_winner | 36 | 89% | 0.070 | 0 |
| pm | soccer / sercb / soccer_team_full_time_winner | 33 | 70% | 0.030 | 0 |
| pm | soccer / serca / soccer_team_full_time_winner | 33 | 64% | 0.050 | 0 |
| pm | esports / ebattlesefsa / efootball_team_full_time_winner | 33 | 94% | 0.010 | 0 |
| pm | soccer / engnl / soccer_team_full_time_winner | 33 | 76% | 0.070 | 0 |
| pm | mma / ufc / ufc_fight_winner | 32 | 97% | 0.010 | 0 |
| pm | ice-hockey / nhl / hockey_team_full_game_winner | 32 | 97% | 0.010 | 0 |
| pm | esports / ebattlesefpl / efootball_team_full_time_winner | 30 | 100% | 0.010 | 0 |
| pm | football / nfl / football_team_full_game_winner | 29 | 100% | 0.010 | 0 |

## Opportunities

| kind | distinct | hits | max margin $/contract | max persistence | fresh-BBO still open |
|---|---|---|---|---|---|
| decided_k | 209 | 4241 | 0.9893 | 35 min | 0/0 |
| decided_pm | 40 | 2334 | 0.7889 | 62 min | 155/198 |
| decided_pm_closed | 29 | 2435 | 0.7889 | 63 min | 2340/2435 |
| dutch_k | 18 | 209 | 0.0379 | 18 min | 0/0 |
| dutch_pm | 68 | 2721 | 0.5248 | 47 min | 0/0 |
| implication_k | 253 | 3416 | 0.7784 | 33 min | 0/0 |
| lag_k_settled | 201 | 31712 | 0.9947 | 262 min | 23551/27879 |
| lag_k_settled_closed | 172 | 2743 | 0.9947 | 202 min | 128/2743 |

Top by persistence × hits:

- **lag_k_settled** basketball — Baskets Bonn vs. Basketball Lowen Braunschweig — bid 0.99 ask - sell_yes @ 0.99 | margin 0.9891 | 203 min, 915 hits | score 97-87 FT
- **lag_k_settled** football — South Florida vs. East Carolina — bid 0.29 ask 0.30 sell_yes @ 0.295 | margin 0.7008 | 115 min, 796 hits | fresh bbo 0.29/0.30 depth 45/67 | score 10-17 Q4
- **lag_k_settled** basketball — Western Carolina vs. UNC Asheville — bid 0.99 ask - sell_yes @ 0.99 | margin 0.9891 | 262 min, 566 hits | fresh bbo 0.99/- depth 13/0 | score 83-75 FT
- **lag_k_settled** football — Western Illinois vs. Eastern Illinois — bid 0.63 ask - sell_yes @ 0.63 | margin 0.9945 | 96 min, 694 hits | fresh bbo 0.63/- depth 11/0 | score 44-23 FT
- **lag_k_settled** football — Alabama State vs. Texas Southern — bid 0.99 ask - sell_yes @ 0.995 | margin 0.9945 | 123 min, 486 hits | fresh bbo 0.99/- depth 11/0 | score 34-31 FT
- **lag_k_settled** esports — LPH Gaming vs.  Phantom Academy — bid 0.57 ask 0.58 sell_yes @ 0.57 | margin 0.5467 | 120 min, 478 hits | fresh bbo 0.57/0.58 depth 7/8 | score - NS
- **lag_k_settled** basketball — Northern Iowa (W) vs. South Dakota State (W) — bid 0.15 ask 0.16 sell_yes @ 0.15 | margin 0.1379 | 115 min, 458 hits | fresh bbo 0.15/0.16 depth 11/9 | score - NS
- **lag_k_settled** basketball — Washington State (W) vs. Oregon (W) — bid 0.01 ask 0.02 sell_yes @ 0.01 | margin 0.0091 | 115 min, 457 hits | fresh bbo 0.01/0.02 depth 1/16 | score 0-0 NS
- **lag_k_settled** esports — All Gamers vs. Weibo Gaming — bid 0.21 ask 0.51 sell_yes @ 0.21 | margin 0.1942 | 92 min, 463 hits | fresh bbo 0.21/0.51 depth 3/5 | score - NS
- **lag_k_settled** esports — Weibo Gaming vs. Dplus — bid 0.85 ask 0.98 buy_yes @ 0.98 | margin 0.3440 | 108 min, 389 hits | fresh bbo 0.85/0.98 depth 25/2 | score 0-0 Map 1
- **lag_k_settled** football — South Dakota State vs. Northern Iowa — bid 0.99 ask - sell_yes @ 0.995 | margin 0.9945 | 182 min, 304 hits | score 41-15 FT
- **lag_k_settled** tennis — Arcangioli - Cirotte vs. Lizunova - Masiianskaia — bid 0.64 ask 0.69 sell_yes @ 0.64 | margin 0.6800 | 100 min, 385 hits | fresh bbo 0.60/0.62 depth 11/17 | score 1-1:30-30 S1
- **lag_k_settled** football — Southern Illinois vs. Indiana State — bid 0.59 ask 0.61 sell_yes @ 0.595 | margin 0.6027 | 118 min, 328 hits | fresh bbo 0.59/0.61 depth 26/26 | score 0-0 Q1
- **lag_k_settled** basketball — Sacramento State vs. Santa Clara — bid 0.04 ask 0.05 sell_yes @ 0.04 | margin 0.0364 | 118 min, 327 hits | fresh bbo 0.04/0.05 depth 4/10 | score - NS
- **lag_k_settled** football — Iowa vs. Northwestern — bid 0.66 ask 0.66 sell_yes @ 0.655 | margin 0.7113 | 70 min, 360 hits | fresh bbo 0.68/0.68 depth 71/48 | score 0-0 Q1
- **lag_k_settled** football — West Florida vs. North Alabama — bid 0.34 ask 0.35 sell_yes @ 0.345 | margin 0.3332 | 111 min, 311 hits | fresh bbo 0.34/0.35 depth 22/20 | score - NS
- **lag_k_settled** football — Temple vs. Navy — bid 0.01 ask 0.01 sell_yes @ 0.01 | margin 0.0592 | 118 min, 285 hits | fresh bbo -/0.01 depth 0/48 | score 14-35 Q3
- **lag_k_settled** esports — eBattles: Argentina (Totti) vs. England (Tesla) — bid 0.18 ask 0.21 sell_yes @ 0.18 | margin 0.1697 | 76 min, 304 hits | score 3-5 FT
- **lag_k_settled** esports — eBattles: Argentina (Totti) vs. England (Tesla) — bid 0.56 ask 0.59 sell_yes @ 0.56 | margin 0.5429 | 40 min, 304 hits | score 3-5 FT
- **lag_k_settled** esports — eBattles: Argentina (Totti) vs. England (Tesla) — bid 0.21 ask 0.25 buy_yes @ 0.25 | margin 0.7370 | 40 min, 300 hits | score 3-5 FT
- **lag_k_settled** football — Southeast Missouri State vs. Tennessee State — bid 0.99 ask - sell_yes @ 0.995 | margin 0.9945 | 60 min, 279 hits | fresh bbo 0.99/- depth 15/0 | score 33-14 FT
- **lag_k_settled** esports — eBattles: Liverpool (Maki) vs. Arsenal (Krkula) — bid 0.02 ask 0.04 sell_yes @ 0.02 | margin 0.3772 | 66 min, 267 hits | fresh bbo -/0.95 depth 0/3 | score 3-5 2H
- **lag_k_settled** esports — eBattles: Liverpool (Maki) vs. Arsenal (Krkula) — bid 0.18 ask 0.20 sell_yes @ 0.18 | margin 0.2227 | 66 min, 267 hits | fresh bbo 0.01/0.95 depth 1/3 | score 3-5 2H
- **lag_k_settled** esports — eBattles: Liverpool (Maki) vs. Arsenal (Krkula) — bid 0.76 ask 0.99 buy_yes @ 0.99 | margin 0.5670 | 66 min, 267 hits | fresh bbo 0.92/- depth 4/0 | score 3-5 2H
- **lag_k_settled** esports — eBattles: Liverpool (llulle) vs. Arsenal (Animal) — bid 0.26 ask 0.27 sell_yes @ 0.26 | margin 0.6138 | 66 min, 266 hits | fresh bbo 0.26/0.27 depth 9/10 | score 1-1 1H

## Live paper trades (no orders; Kalshi prices, taker fees)

Ledger L2-2026-11-01 (earlier ledgers excluded: none)

**Total closed P&L: $-231.34 on $1768.34 staked (-13.1%)**

| rule | entries | closed | winners | staked | P&L | ROI |
|---|---|---|---|---|---|---|
| R1 anchor [ncaaf] | 51 | 46 | 24 | $463.46 | $-12.46 | -3% |
| R2 q1cheap [ncaaf] | 45 | 34 | 7 | $177.97 | $+16.03 | +9% |
| R2 q1cheap [nfl] | 1 | 1 | 0 | $5.22 | $-5.22 | -100% |
| R3 blowout [ncaaf] | 22 | 18 | 1 | $381.41 | $-200.41 | -53% |
| R4 halftime [ncaaf] | 25 | 23 | 14 | $114.57 | $+20.43 | +18% |
| R6 decided [other] | 42 | 36 | 31 | $625.72 | $-49.72 | -8% |

| time (UTC) | rule | game | team | entry | contracts | why | result |
|---|---|---|---|---|---|---|---|
| 00:48 | R3 blowout | Incarnate Word vs. Southeast | Southeastern Louisiana | 0.13 | 153 | down 18 in Q2, ask 0.13 | open |
| 00:37 | R2 q1cheap | Louisville vs. Georgia Tech | Georgia Tech | 0.17 | 29 | Q1 ask 0.17, score 0-0 | open |
| 00:36 | R2 q1cheap | Incarnate Word vs. Southeast | Southeastern Louisiana | 0.20 | 25 | Q1 ask 0.20, score 14-3 | open |
| 00:21 | R2 q1cheap | Sam Houston vs. Jacksonville | Sam Houston | 0.15 | 33 | Q1 ask 0.15, score 0-0 | open |
| 00:13 | R3 blowout | West Georgia vs. Central Ark | West Georgia | 0.09 | 222 | down 18 in Q3, ask 0.09 | open |
| 00:08 | R2 q1cheap | Abilene Christian vs. Tarlet | Abilene Christian | 0.19 | 26 | Q1 ask 0.19, score 0-6 | open |
| 00:03 | R2 q1cheap | Utah Tech vs. UC Davis | Utah Tech | 0.17 | 29 | Q1 ask 0.17, score 0-0 | open |
| 00:03 | R1 anchor | McNeese vs. Houston Christia | McNeese | 0.62 | 16 | pregame dog (mid 0.43) leads 3-0 in Q3, ask 0.62 | open |
| 23:52 | R4 halftime | West Georgia vs. Central Ark | West Georgia | 0.22 | 22 | Central Arkansas rose +0.040 at halftime; fade it | open |
| 23:50 | R1 anchor | Montana State vs. Idaho Stat | Idaho St. | 0.43 | 23 | pregame dog (mid 0.21) leads 0-3 in Q2, ask 0.43 | open |
| 23:50 | R4 halftime | McNeese vs. Houston Christia | Houston Christian | 0.60 | 8 | McNeese rose +0.055 at halftime; fade it | open |
| 23:23 | R3 blowout | Northern Arizona vs. Cal Pol | Cal Poly | 0.10 | 200 | down 17 in Q2, ask 0.10 | open |
| 23:18 | R2 q1cheap | Boise State vs. Colorado Sta | Colorado St. | 0.15 | 33 | Q1 ask 0.15, score 8-7 | open |
| 23:17 | R3 blowout | Oregon vs. Ohio State | Ohio St. | 0.10 | 200 | down 17 in Q3, ask 0.10 | final score (pending Kalshi settlement): 0.00, $-21.26 |
| 23:12 | R3 blowout | Eastern Washington vs. Idaho | Eastern Washington | 0.14 | 142 | down 18 in Q2, ask 0.14 | open |
| 22:59 | R1 anchor | Missouri State vs. Florida I | Missouri St. | 0.45 | 22 | pregame dog (mid 0.35) leads 6-3 in Q3, ask 0.45 | final score (pending Kalshi settlement): 0.00, $-10.28 |
| 22:58 | R3 blowout | UCF vs. Kansas | Kansas | 0.08 | 250 | down 19 in Q3, ask 0.08 | final score (pending Kalshi settlement): 0.00, $-21.29 |
| 22:58 | R3 blowout | Southeast Missouri State vs. | Tennessee St. | 0.13 | 153 | down 17 in Q3, ask 0.13 | kalshi settled: 0.00, $-21.10 |
| 22:58 | R4 halftime | Stephen F. Austin vs. Lamar | Lamar | 0.73 | 6 | Stephen F. Austin rose +0.170 at halftime; fade it | final score (pending Kalshi settlement): 1.00, $+1.54 |
| 22:45 | R4 halftime | Oregon vs. Ohio State | Ohio St. | 0.58 | 8 | Oregon rose +0.040 at halftime; fade it | final score (pending Kalshi settlement): 0.00, $-4.78 |
| 22:42 | R3 blowout | East Texas A&M vs. Nicholls | Nicholls St. | 0.11 | 181 | down 17 in Q2, ask 0.11 | final score (pending Kalshi settlement): 1.00, $+159.85 |
| 22:39 | R1 anchor | West Georgia vs. Central Ark | West Georgia | 0.38 | 26 | pregame dog (mid 0.17) leads 14-7 in Q2, ask 0.38 | open |
| 22:37 | R4 halftime | Southeast Missouri State vs. | Southeast Missouri St. | 0.71 | 7 | Tennessee St. rose +0.110 at halftime; fade it | kalshi settled: 1.00, $+1.93 |
| 22:37 | R1 anchor | Southeast Missouri State vs. | Tennessee St. | 0.36 | 27 | pregame dog (mid 0.21) leads 3-7 in Q3, ask 0.36 | kalshi settled: 0.00, $-10.16 |
| 22:32 | R2 q1cheap | Eastern Washington vs. Idaho | Eastern Washington | 0.20 | 25 | Q1 ask 0.20, score 3-7 | open |
| 22:22 | R1 anchor | Oregon vs. Ohio State | Oregon | 0.41 | 24 | pregame dog (mid 0.27) leads 16-14 in Q2, ask 0.41 | final score (pending Kalshi settlement): 1.00, $+13.75 |
| 22:17 | R4 halftime | Arkansas-Pine Bluff vs. Gram | Arkansas-Pine Bluff | 0.61 | 8 | Grambling St. rose +0.055 at halftime; fade it | kalshi settled: 1.00, $+2.99 |
| 22:16 | R4 halftime | Mississippi Valley State vs. | Mississippi Valley St. | 0.07 | 71 | Jackson St. rose +0.045 at halftime; fade it | kalshi settled: 0.00, $-5.29 |
| 22:15 | R4 halftime | Florida A&M vs. Alcorn State | Florida A&M | 0.26 | 19 | Alcorn St. rose +0.135 at halftime; fade it | kalshi settled: 0.00, $-5.20 |
| 22:11 | R2 q1cheap | South Alabama vs. Louisiana | South Alabama | 0.19 | 26 | Q1 ask 0.19, score 0-7 | open |
| 22:07 | R2 q1cheap | West Georgia vs. Central Ark | West Georgia | 0.20 | 25 | Q1 ask 0.20, score 0-0 | open |
| 22:06 | R4 halftime | Alabama A&M vs. Prairie View | Prairie View A&M | 0.74 | 6 | Alabama A&M rose +0.080 at halftime; fade it | kalshi settled: 1.00, $+1.48 |
| 22:02 | R2 q1cheap | Northern Arizona vs. Cal Pol | Cal Poly | 0.18 | 27 | Q1 ask 0.18, score 0-0 | open |
| 22:00 | R1 anchor | Louisiana-Monroe vs. Arkansa | Louisiana-Monroe | 0.43 | 23 | pregame dog (mid 0.14) leads 16-14 in Q3, ask 0.43 | final score (pending Kalshi settlement): 1.00, $+12.72 |
| 21:56 | R1 anchor | Vanderbilt vs. Mississippi S | Vanderbilt | 0.55 | 18 | pregame dog (mid 0.42) leads 3-0 in Q2, ask 0.55 | final score (pending Kalshi settlement): 1.00, $+7.79 |
| 21:56 | R4 halftime | Alabama State vs. Texas Sout | Texas Southern | 0.55 | 9 | Alabama St. rose +0.095 at halftime; fade it | kalshi settled: 0.00, $-5.11 |
| 21:42 | R3 blowout | Penn State vs. Washington | Washington | 0.12 | 166 | down 17 in Q2, ask 0.12 | final score (pending Kalshi settlement): 0.00, $-21.15 |
| 21:42 | R3 blowout | Eastern Kentucky vs. Austin  | Eastern Kentucky | 0.08 | 250 | down 17 in Q2, ask 0.08 | final score (pending Kalshi settlement): 0.00, $-21.29 |
| 21:42 | R1 anchor | Stephen F. Austin vs. Lamar | Lamar | 0.62 | 16 | pregame dog (mid 0.24) leads 0-10 in Q2, ask 0.62 | final score (pending Kalshi settlement): 1.00, $+5.82 |
| 21:39 | R1 anchor | UCF vs. Kansas | UCF | 0.47 | 21 | pregame dog (mid 0.34) leads 9-7 in Q2, ask 0.47 | final score (pending Kalshi settlement): 1.00, $+10.76 |

### Score reaction speed (live, 15 s): share of the 3-minute move done by +15 s / +30 s / +60 s

- 26NOV07USAULL 17-28: -0% / -0% / -12%
- 26NOV07MTSTIDST 7-10: 0% / 0% / -89%
- 26NOV07MTSTIDST 7-10: -0% / -0% / -78%
- 26NOV07UTUUCD 7-0: 0% / 0% / 8%
- 26NOV07UTUUCD 7-0: -0% / -0% / 33%
- 26NOV07SFALAM 28-38: -0% / 100% / 100%
- 26NOV07SFALAM 28-38: 0% / 100% / 100%
- 26NOV07USAULL 23-28: 0% / 0% / -14%
- 26NOV07USAULL 23-28: -0% / -0% / -13%
- 26NOV07VANMSST 25-17: -0% / -8% / -8%
- 26NOV07VANMSST 25-17: 0% / -8% / -8%
- 26NOV07UKTENN 3-10: 0% / 0% / 20%
- 26NOV07UKTENN 3-10: -0% / -0% / -0%
- 26NOV07EWUIDHO 17-38: 0% / 0% / 0%
- 26NOV07IWSELA 14-3: -0% / -0% / 55%
- 26NOV07IWSELA 14-3: 0% / 0% / 33%
- 26NOV07MOSUFIU 20-20: -0% / -0% / 0%
- 26NOV07MOSUFIU 20-20: 0% / 0% / 2%
- 26NOV07ACTARL 10-14: -21% / -21% / -14%
- 26NOV07ACTARL 10-14: -14% / -14% / -14%

## Bot latency map: how long a decided Kalshi market stays mispriced

| sport | series | markets | already priced | mispriced then fixed | median s mispriced | closed/timeout | contradictions | cheapest ask (size) | resting @0.97 contracts / $ | settled right / wrong |
|---|---|---|---|---|---|---|---|---|---|---|
| basketball | KXNCAAMBTOTAL | 536 | 499 | 21 | 2 | 13 | 3 | 0.64 (1210) | 0 / $0.00 | 511 / 13 |
| basketball | KXNCAAWBTOTAL | 434 | 430 | 4 | 89 | 0 | 0 | 0.95 (2) | 0 / $0.00 | 434 / 0 |
| basketball | KXNCAAMBSPREAD | 264 | 256 | 0 | - | 8 | 0 | 0.98 (122) | 0 / $0.00 | 263 / 1 |
| football | KXNCAAFGAME | 111 | 108 | 0 | - | 0 | 3 | - | 0 / $0.00 | 103 / 0 |
| basketball | KXNCAAWBSPREAD | 98 | 98 | 0 | - | 0 | 0 | - | 0 / $0.00 | 98 / 0 |
| soccer | KXUECLTOTAL | 75 | 68 | 7 | 4 | 0 | 0 | 0.80 (2054) | 59 / $1.76 | 68 / 0 |
| soccer | KXUELTOTAL | 72 | 66 | 6 | 6 | 0 | 0 | 0.86 (188) | 875 / $26.24 | 66 / 1 |
| soccer | KXMLSTOTAL | 57 | 57 | 0 | - | 0 | 0 | - | 0 / $0.00 | 26 / 0 |
| soccer | KXSERIECTOTAL | 53 | 48 | 5 | 14 | 0 | 0 | 0.85 (48) | 0 / $0.00 | 53 / 0 |
| basketball | KXNCAAWBGAME | 46 | 46 | 0 | - | 0 | 0 | - | 0 / $0.00 | 46 / 0 |
| basketball | KXNCAAMBGAME | 44 | 44 | 0 | - | 0 | 0 | - | 0 / $0.00 | 44 / 0 |
| soccer | KXBUNDESLIGA2TOTAL | 39 | 38 | 0 | - | 1 | 0 | 0.01 (14030) | 11015 / $330.45 | 38 / 1 |
| tennis | KXWTASETWINNER | 38 | 35 | 2 | 739 | 1 | 0 | 0.67 (103) | 359 / $10.78 | 37 / 0 |
| tennis | KXATPSETWINNER | 38 | 38 | 0 | - | 0 | 0 | - | 0 / $0.00 | 38 / 0 |
| basketball | KXEUROLEAGUETOTAL | 37 | 35 | 1 | 3 | 0 | 1 | 0.95 (200) | 0 / $0.00 | 33 / 0 |
| soccer | KXARGPREMDIVTOTAL | 34 | 32 | 0 | - | 2 | 0 | 0.01 (69347) | 37106 / $1113.18 | 33 / 1 |
| soccer | KXUECL1HTOTAL | 33 | 33 | 0 | - | 0 | 0 | - | 0 / $0.00 | 33 / 0 |
| soccer | KXUECLSPREAD | 33 | 33 | 0 | - | 0 | 0 | - | 0 / $0.00 | 33 / 0 |
| soccer | KXBELGIANPLTOTAL | 31 | 31 | 0 | - | 0 | 0 | - | 0 / $0.00 | 31 / 0 |
| soccer | KXTFF1LIGTOTAL | 30 | 28 | 2 | 2 | 0 | 0 | 0.83 (9000) | 0 / $0.00 | 30 / 0 |
| soccer | KXCZEFNLTOTAL | 29 | 29 | 0 | - | 0 | 0 | - | 0 / $0.00 | 29 / 0 |
| soccer | KXAPFDDHTOTAL | 26 | 25 | 1 | 3 | 0 | 0 | 0.98 (114) | 0 / $0.00 | 26 / 0 |
| soccer | KXEKSTRAKLASATOTAL | 24 | 20 | 4 | 26 | 0 | 0 | 0.95 (24) | 0 / $0.00 | 24 / 0 |
| soccer | KXIDNSLTOTAL | 22 | 20 | 1 | 257 | 0 | 1 | 0.87 (10) | 0 / $0.00 | 22 / 0 |
| soccer | KXAUTBUNDESTOTAL | 22 | 18 | 2 | 4 | 0 | 2 | 0.98 (22) | 0 / $0.00 | 22 / 0 |
| football | KXNCAAFTOTAL | 21 | 21 | 0 | - | 0 | 0 | - | 0 / $0.00 | 21 / 0 |
| soccer | KXTHAIL1TOTAL | 19 | 19 | 0 | - | 0 | 0 | - | 0 / $0.00 | 19 / 0 |
| soccer | KXLIGUE2TOTAL | 18 | 17 | 0 | - | 1 | 0 | 0.56 (600) | 48 / $1.44 | 18 / 0 |
| soccer | KXALLSVENSKANTOTAL | 18 | 18 | 0 | - | 0 | 0 | - | 0 / $0.00 | 18 / 0 |
| soccer | KXMLSSPREAD | 18 | 18 | 0 | - | 0 | 0 | - | 0 / $0.00 | 0 / 0 |
| tennis | KXATPCHALLENGERDOUBLES | 16 | 16 | 0 | - | 0 | 0 | - | 0 / $0.00 | 16 / 0 |
| soccer | KXUEL1HTOTAL | 15 | 15 | 0 | - | 0 | 0 | - | 0 / $0.00 | 15 / 0 |
| soccer | KXBRASILEIROTOTAL | 15 | 15 | 0 | - | 0 | 0 | - | 0 / $0.00 | 15 / 0 |
| soccer | KXJLEAGUE1HTOTAL | 15 | 12 | 3 | 20 | 0 | 0 | 0.91 (20) | 51 / $1.54 | 15 / 0 |
| soccer | KXJLEAGUE1H | 15 | 15 | 0 | - | 0 | 0 | - | 0 / $0.00 | 15 / 0 |
| soccer | KXJ2LEAGUEGAME | 15 | 15 | 0 | - | 0 | 0 | - | 0 / $0.00 | 15 / 0 |
| soccer | KXUECLGAME | 14 | 14 | 0 | - | 0 | 0 | - | 0 / $0.00 | 14 / 0 |
| soccer | KXBUNDESLIGAWTOTAL | 14 | 14 | 0 | - | 0 | 0 | - | 27 / $0.82 | 14 / 0 |
| soccer | KXHNLTOTAL | 14 | 14 | 0 | - | 0 | 0 | - | 0 / $0.00 | 14 / 0 |
| soccer | KXBRASILEIROBTOTAL | 12 | 12 | 0 | - | 0 | 0 | - | 0 / $0.00 | 10 / 0 |
| basketball | KXNCAAFTOTAL | 12 | 2 | 0 | - | 10 | 0 | 0.61 (609) | 0 / $0.00 | 7 / 0 |
| basketball | KXEUROLEAGUESPREAD | 12 | 12 | 0 | - | 0 | 0 | - | 0 / $0.00 | 12 / 0 |
| soccer | KXHUNNB1TOTAL | 12 | 12 | 0 | - | 0 | 0 | - | 0 / $0.00 | 12 / 0 |
| basketball | KXABASPREAD | 12 | 12 | 0 | - | 0 | 0 | - | 0 / $0.00 | 12 / 0 |
| soccer | KXUECL1HBTTS | 11 | 11 | 0 | - | 0 | 0 | - | 0 / $0.00 | 11 / 0 |
| soccer | KXCZEFLTOTAL | 11 | 11 | 0 | - | 0 | 0 | - | 0 / $0.00 | 11 / 0 |
| soccer | KXBUNDESLIGASPREAD | 11 | 11 | 0 | - | 0 | 0 | - | 0 / $0.00 | 11 / 0 |
| basketball | KXABATOTAL | 11 | 11 | 0 | - | 0 | 0 | - | 0 / $0.00 | 11 / 0 |
| esports | KXCS2TOTALMAPS | 10 | 10 | 0 | - | 0 | 0 | - | 0 / $0.00 | 9 / 0 |
| soccer | KXUELBTTS | 10 | 8 | 2 | 62 | 0 | 0 | 0.74 (2475) | 3227 / $96.80 | 9 / 1 |
| soccer | KXDIMAYORTOTAL | 10 | 10 | 0 | - | 0 | 0 | - | 0 / $0.00 | 9 / 0 |
| soccer | KXUECLBTTS | 9 | 9 | 0 | - | 0 | 0 | - | 0 / $0.00 | 8 / 0 |
| soccer | KXLIGAMXTOTAL | 9 | 8 | 1 | 242 | 0 | 0 | 0.60 (7) | 1571 / $47.13 | 8 / 0 |
| soccer | KXMLS1HTOTAL | 9 | 9 | 0 | - | 0 | 0 | - | 0 / $0.00 | 9 / 0 |
| ice-hockey | KXAHLGAME | 8 | 8 | 0 | - | 0 | 0 | - | 0 / $0.00 | 8 / 0 |
| soccer | KXLALIGA2TOTAL | 8 | 6 | 2 | 2 | 0 | 0 | 0.84 (75) | 0 / $0.00 | 8 / 0 |
| soccer | KXBUNDESLIGATOTAL | 8 | 8 | 0 | - | 0 | 0 | - | 0 / $0.00 | 8 / 0 |
| soccer | KXMLSGAME | 7 | 7 | 0 | - | 0 | 0 | - | 0 / $0.00 | 0 / 0 |
| soccer | KXBRASILEIRO1H | 6 | 6 | 0 | - | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| tennis | KXATPCHALLENGERMATCH | 6 | 6 | 0 | - | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| soccer | KXUECL1H | 6 | 6 | 0 | - | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| soccer | KXBRASILEIROB1HTOTAL | 6 | 6 | 0 | - | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| soccer | KXKLEAGUETOTAL | 6 | 6 | 0 | - | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| soccer | KXJ2LEAGUESPREAD | 6 | 6 | 0 | - | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| soccer | KXJ2LEAGUETOTAL | 6 | 6 | 0 | - | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| soccer | KXBUNDESLIGA1HTOTAL | 6 | 6 | 0 | - | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| soccer | KXMLSBTTS | 6 | 6 | 0 | - | 0 | 0 | - | 0 / $0.00 | 5 / 0 |
| soccer | KXMLS1H | 6 | 6 | 0 | - | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| soccer | KXUEL1HBTTS | 5 | 5 | 0 | - | 0 | 0 | - | 0 / $0.00 | 5 / 0 |
| soccer | KXLIGAEXPTOTAL | 5 | 5 | 0 | - | 0 | 0 | - | 0 / $0.00 | 5 / 0 |
| soccer | KXEREDIVISIETOTAL | 5 | 5 | 0 | - | 0 | 0 | - | 0 / $0.00 | 5 / 0 |
| soccer | KXROML1TOTAL | 5 | 5 | 0 | - | 0 | 0 | - | 0 / $0.00 | 5 / 0 |
| soccer | KXJLEAGUE1HBTTS | 5 | 4 | 1 | 79 | 0 | 0 | 0.95 (1) | 3 / $0.09 | 5 / 0 |
| soccer | KXUAEPLTOTAL | 5 | 5 | 0 | - | 0 | 0 | - | 0 / $0.00 | 5 / 0 |
| soccer | KXSVK1LTOTAL | 5 | 5 | 0 | - | 0 | 0 | - | 0 / $0.00 | 5 / 0 |
| soccer | KXLIGAFTOTAL | 5 | 5 | 0 | - | 0 | 0 | - | 0 / $0.00 | 5 / 0 |
| soccer | KXLIGAPORTUGALTOTAL | 5 | 5 | 0 | - | 0 | 0 | - | 0 / $0.00 | 5 / 0 |
| soccer | KXCHLLDPTOTAL | 5 | 5 | 0 | - | 0 | 0 | - | 0 / $0.00 | 5 / 0 |
| basketball | KXEUROLEAGUEGAME | 4 | 4 | 0 | - | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
| soccer | KXPERLIGA1TOTAL | 4 | 4 | 0 | - | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
| soccer | KXJLEAGUETOTAL | 4 | 4 | 0 | - | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
| soccer | KXELITESERIENTOTAL | 4 | 3 | 0 | - | 0 | 1 | - | 0 / $0.00 | 4 / 0 |
| soccer | KXBULFLTOTAL | 4 | 4 | 0 | - | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
| soccer | KXALLSVENSKANSPREAD | 4 | 4 | 0 | - | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
| esports | KXCS2GAME | 4 | 4 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| tennis | KXATPEXACTMATCH | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| basketball | KXNCAAFGAME | 3 | 0 | 0 | - | 3 | 0 | 0.79 (144573) | 295 / $8.84 | 3 / 0 |
| soccer | KXEFLCHAMPIONSHIP1H | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXSERIEA1H | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXSERIEA1HTOTAL | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXEFLCHAMPIONSHIPBTTS | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXEFLCHAMPIONSHIPGAME | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXEFLCHAMPIONSHIPTOTAL | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXSERIECBTTS | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXMLS1HBTTS | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| basketball | KXNBAGAME | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| tennis | KXATPMATCH | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| tennis | KXWTAMATCH | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| basketball | KXJBLEAGUEGAME | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXJ2LEAGUEBTTS | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| basketball | KXKBLGAME | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| tennis | KXWTADOUBLES | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXTHAIL1BTTS | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXBUNDESLIGA1HBTTS | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| esports | KXCS2SPREAD | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXDENSUPERLIGATOTAL | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| basketball | KXAUTBSLGAME | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| basketball | KXABAGAME | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| basketball | KXACBTOTAL | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXBRASILEIROB1H | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXTFF1LIGBTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXBUNDESLIGAWBTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXEREDIVISIE1HBTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXLIGUE2BTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXJLEAGUEGAME | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXJLEAGUEBTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXSERIEA1HBTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXSLGREECETOTAL | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXSUPERLIGTOTAL | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXSVNPLTOTAL | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXARGPREMDIVBTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXBELGIANPLBTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXECULPTOTAL | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXBRASILEIROB1HBTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |

'Already priced' = the book was at 99c+ when we first looked (bots were faster than our score feed). 'Median s mispriced' runs from our decision to the fix. 'Settled right / wrong' checks our certainty against Kalshi's result — any 'wrong' means the score feed or the model failed.

## Decided-state engine (contracts the live score already settled, still trading)

2884 contracts decided while active; 209 had a price leaving > 0.4c after fees; 69 of those were mispriced AFTER the score was stable (lock tier)

| sport | game | contract | decided | reason | max margin | mispriced for | lock margin | lock depth |
|---|---|---|---|---|---|---|---|---|
| basketball | North Dakota State vs. San Franc | KXNCAAFTOTAL-26NOV07NIUSJSU-49 | YES | score 61-70 total 131 > 48.5 | 0.373 | 274s | 0.373 | 609 |
| basketball | Cal Poly vs. Arizona | KXNCAAFTOTAL-26NOV07NAUCP-59 | YES | score 48-67 total 115 > 58.5 | 0.354 | 1791s | 0.354 | 300 |
| basketball | Northern Arizona (W) vs. Arizona | KXNCAAMBTOTAL-26NOV06CSNKSU-163 | NO | ended total 131 <= 162.5 | 0.344 | 589s | 0.344 | 1210 |
| basketball | Northern Arizona (W) vs. Arizona | KXNCAAMBTOTAL-26NOV06CSNKSU-156 | NO | ended total 131 <= 155.5 | 0.315 | 589s | 0.315 | 5 |
| tennis | Anastasia Zakharova vs. Lucrezia | KXWTASETWINNER-26NOV06ZAKSTE-2-STE | NO | set 2 final 5-2 | 0.315 | 210s | 0.315 | 289 |
| tennis | Anastasia Zakharova vs. Lucrezia | KXWTASETWINNER-26NOV06ZAKSTE-2-ZAK | YES | set 2 final 5-2 | 0.305 | 210s | 0.305 | 178 |
| basketball | North Dakota State vs. San Franc | KXNCAAFTOTAL-26NOV07NIUSJSU-46 | YES | score 61-70 total 131 > 45.5 | 0.305 | 274s | 0.305 | 1655 |
| soccer | Uthai Thani FC vs. Chiangrai Uni | KXTHAIL1TOTAL-26NOV07UTHCHI-4 | YES | score 2-2 total 4 > 3.5 | 0.305 | 362s | 0.305 | 1350 |
| basketball | Cal Poly vs. Arizona | KXNCAAFTOTAL-26NOV07NAUCP-55 | YES | score 48-67 total 115 > 54.5 | 0.246 | 1791s | 0.246 | 200 |
| basketball | North Dakota State vs. San Franc | KXNCAAFTOTAL-26NOV07NIUSJSU-43 | YES | score 61-70 total 131 > 42.5 | 0.246 | 274s | 0.246 | 404 |
| football | Northern Illinois vs. San Jose S | KXNCAAFGAME-26NOV07NIUSJSU-SJSU | YES | ended 19-30 | 0.198 | 115277s | 0.198 | 144574 |
| basketball | North Dakota State vs. San Franc | KXNCAAFTOTAL-26NOV07NIUSJSU-40 | YES | score 61-70 total 131 > 39.5 | 0.170 | 274s | 0.170 | 14 |
| football | South Dakota State vs. Northern  | KXNCAAFGAME-26NOV07SDSTUNI-UNI | NO | ended 41-15 | 0.151 | 89s | 0.151 | 513 |
| football | South Dakota State vs. Northern  | KXNCAAFGAME-26NOV07SDSTUNI-SDST | YES | ended 41-15 | 0.151 | 89s | 0.151 | 358 |
| basketball | North Dakota State vs. San Franc | KXNCAAFTOTAL-26NOV07NIUSJSU-37 | YES | score 61-70 total 131 > 36.5 | 0.113 | 274s | 0.113 | 450 |
| tennis | Elena Pridankina vs. Alexandra S | KXWTASETWINNER-26NOV05PRISHU-1-SHU | NO | set 1 final 7-6 | 0.989 | 180s | - | 0 |
| tennis | Elena Pridankina vs. Alexandra S | KXWTASETWINNER-26NOV05PRISHU-1-PRI | YES | set 1 final 7-6 | 0.989 | 180s | - | 0 |
| tennis | Nuno Borges vs. Ignacio Buse | KXATPEXACTMATCH-26NOV05BORBUS-BOR21 | YES | ended 6-0, 6-2 | 0.989 | 323s | - | 0 |
| football | Temple vs. Navy | KXNCAAFGAME-26NOV07TEMNAVY-TEM | NO | ended 35-42 | 0.957 | 616s | - | 0 |
| football | Temple vs. Navy | KXNCAAFGAME-26NOV07TEMNAVY-NAVY | YES | ended 35-42 | 0.957 | 616s | - | 0 |
| football | Western Kentucky vs. Middle Tenn | KXNCAAFGAME-26NOV07WKUMTU-WKU | NO | ended 42-45 | 0.957 | 2509s | - | 0 |
| soccer | Hertha BSC vs. VFL Wolfsburg | KXBUNDESLIGA2TOTAL-26NOV07BSCWOB-4 | NO | ended total 3 <= 3.5 | 0.947 | 0s | - | 0 |
| basketball | North Dakota State vs. San Franc | KXNCAAFTOTAL-26NOV07NIUSJSU-73 | YES | score 61-70 total 131 > 72.5 | 0.873 | 274s | - | 0 |
| basketball | Northern Arizona (W) vs. Arizona | KXNCAAMBSPREAD-26NOV06CSNKSU-CSN12 | YES | ended 52-79 margin 27 vs 11.5 | 0.852 | 589s | - | 0 |
| soccer | 1 FC Nuremberg vs. SV Darmstadt  | KXBUNDESLIGA2TOTAL-26NOV07FCND98-3 | NO | ended total 2 <= 2.5 | 0.852 | 90s | - | 0 |

## Close / settlement latency (how clunky each venue is after the final whistle)

Kalshi: settlement_ts − close_time per series (negative = settled before the scheduled close)

| series | n | median | p90 |
|---|---|---|---|
| KXESOCCERGAME eSoccer Game | 4032 | 4.0 min | 4.1 min |
| KXNCAAMBTOTAL Men's College Basketball Total | 2364 | 4.0 min | 4.1 min |
| KXNCAAFSPREAD College Football Spread | 1845 | 4.0 min | 4.1 min |
| KXNCAAMBSPREAD Men's College Basketball Sprea | 1814 | 1.8 min | 1.8 min |
| KXNCAAWBTOTAL Women's College Basketball Tot | 1774 | 2.5 min | 2.6 min |
| KXNBAREB NBA Player Rebounds | 1588 | 2.0 min | 2.1 min |
| KXNBA3PT NBA Player Threes | 1525 | 2.0 min | 2.1 min |
| KXNBA3PTPROT NBA Player Threes Protected | 1498 | 2.6 min | 2.6 min |
| KXNBAREBPROT NBA Player Rebounds Protected | 1466 | 2.6 min | 2.6 min |
| KXNCAAFTOTAL College Football Total Points | 1329 | 4.0 min | 4.1 min |
| KXNBAPTS NBA Player Points | 1269 | 2.0 min | 2.1 min |
| KXNBAPTSPROT NBA Player Points Protected | 1201 | 2.6 min | 2.6 min |
| KXNHLGOAL NHL Goalscorer | 1132 | 3.0 min | 3.1 min |
| KXNBAASTPROT NBA Player Assists Protected | 1077 | 2.6 min | 2.6 min |
| KXNCAAFTEAMTOTAL College Football Team Total Po | 1041 | 4.0 min | 4.1 min |
| KXNBAAST NBA Player Assists | 1004 | 2.0 min | 2.1 min |
| KXNCAAF1HSPREAD College Football 1st Half Spre | 952 | 4.0 min | 4.1 min |
| KXNBAPRA NBA Player Points + Rebounds + | 938 | 2.5 min | 2.6 min |
| KXNBATEAMTOTAL NBA Team Total | 921 | 2.5 min | 2.6 min |
| KXNHLPTS Pro Hockey Points | 917 | 3.0 min | 3.1 min |
| KXLIGAPROMATCH Russia Liga Pro Match | 890 | 4.0 min | 4.1 min |
| KXNCAAWBSPREAD Women's College Basketball Spr | 883 | 1.8 min | 1.8 min |
| KXNBASPREAD NBA Spread | 810 | 1.8 min | 1.8 min |
| KXNHLFIRSTGOAL NHL First Goal | 737 | 6.0 min | 6.0 min |
| KXNBATOTAL NBA Total | 727 | 1.8 min | 1.8 min |
| KXNHLAST Pro Hockey Assists | 691 | 6.0 min | 6.1 min |
| KXNCAAF1HTOTAL College Football 1st Half Tota | 627 | 4.0 min | 4.1 min |
| KXNFLPASSYDSPRECISE Pass Yards Precise | 602 | 4.1 min | 4.1 min |
| KXNBA1HTEAMTOTAL NBA 1st Half Team Total | 572 | 2.5 min | 2.6 min |
| KXNBASTL NBA Player Steals | 524 | 2.0 min | 2.1 min |
| KXEBASKETBALLGAME eBasketball Game | 520 | 4.0 min | 4.1 min |
| KXNBA1HTOTAL NBA 1st Half Total | 494 | 2.5 min | 2.6 min |
| KXNBA1HSPREAD NBA 1st Half Spread | 494 | 2.5 min | 2.6 min |
| KXUECLSCORE Correct Score | 466 | 6.0 min | 6.1 min |
| KXNCAAF2HSPREAD College Football 2nd Half Spre | 463 | 4.0 min | 4.1 min |
| KXUELSCORE Correct Score | 454 | 6.0 min | 6.1 min |
| KXNBAPRAPROT Pts + Reb + Ast Protected | 445 | 2.6 min | 2.6 min |
| KXNBA2HTOTAL NBA 2nd Half Total | 437 | 2.5 min | 2.6 min |
| KXNBA2HSPREAD NBA 2nd Half Spread | 437 | 2.5 min | 2.6 min |
| KXCS2MAP Counter-Strike 2 Map Winner  | 374 | 3.0 min | 3.1 min |

## Participant fingerprint (per sport; 60 s snapshots)

change% = share of scan cycles (60 s) where the best quote moved; react = median minutes from a score change to the next quote move (humans: slow, bursty, round sizes; bots: constant cadence, odd/constant sizes, instant reaction)

| venue | sport | markets | snapshots | two-sided | med spread | change% | react (min) | round sizes | med size |
|---|---|---|---|---|---|---|---|---|---|
| pm | soccer | 1278 | 182580 | 85% | 0.020 | 16% | 0.7 (n=2411) | - | - |
| pm | tennis | 1440 | 125258 | 93% | 0.010 | 25% | 0.5 (n=68039) | - | - |
| pm | esports | 3466 | 84701 | 79% | 0.020 | 18% | 0.5 (n=17209) | - | - |
| pm | basketball | 879 | 68984 | 73% | 0.030 | 18% | 0.6 (n=14730) | - | - |
| pm | table-tennis | 1591 | 47166 | 90% | 0.010 | 25% | 0.5 (n=24910) | - | - |
| pm | golf | 1165 | 37975 | 49% | 0.007 | 18% | - (n=0) | - | - |
| pm | football | 123 | 17739 | 92% | 0.005 | 21% | 1.3 (n=887) | - | - |
| pm | climate | 216 | 11730 | 67% | 0.070 | 28% | - (n=0) | - | - |
| pm | ice-hockey | 84 | 6387 | 86% | 0.060 | 15% | 0.7 (n=295) | - | - |
| pm | cricket | 11 | 4394 | 87% | 0.050 | 9% | 0.8 (n=678) | - | - |
| pm | beach-volleyball | 62 | 2494 | 90% | 0.010 | 22% | 0.5 (n=1308) | - | - |
| pm | macro | 152 | 1891 | 42% | 0.010 | 15% | - (n=0) | - | - |
| pm | mma | 16 | 1369 | 65% | 0.060 | 3% | - (n=0) | - | - |
| pm | boxing | 33 | 763 | 81% | 0.060 | 26% | 7.2 (n=3) | - | - |
| pm | pickleball | 73 | 749 | 75% | 0.190 | 16% | - (n=0) | - | - |
| pm | motorsports | 22 | 396 | 3% | 0.065 | 2% | - (n=0) | - | - |
| pm | baseball | 3 | 309 | 94% | 0.050 | 19% | 0.5 (n=14) | - | - |
| pm | technology | 9 | 18 | 0% | - | 0% | - (n=0) | - | - |
| k | KXNCAAFGAME College Football Game | 742 | 839015 | 99% | 0.080 | 5% | - | 7% | 52 |
| k | KXNBA3PT NBA Player Threes | 1624 | 249477 | 73% | 0.090 | 18% | - | 31% | 35 |
| k | KXNBAAST NBA Player Assists | 1160 | 165091 | 78% | 0.100 | 18% | - | 29% | 26 |
| k | KXNBAPTS NBA Player Points | 1399 | 142712 | 80% | 0.060 | 24% | - | 28% | 40 |
| k | KXNBAREB NBA Player Rebounds | 1963 | 142268 | 79% | 0.080 | 21% | - | 26% | 36 |
| k | KXNCAAFTEAMTOTAL College Football Team To | 1503 | 133753 | 92% | 0.030 | 2% | - | 32% | 210 |
| k | KXNCAAMBTOTAL Men's College Basketball | 2469 | 112256 | 69% | 0.070 | 11% | - | 21% | 100 |
| k | KXNFLGAME NFL Game | 58 | 107574 | 100% | 0.010 | 1% | - | 4% | 95566 |
| k | KXCS2MAP Counter-Strike 2 Map Win | 508 | 94727 | 95% | 0.600 | 5% | - | 26% | 75 |
| k | KXNCAAMBSPREAD Men's College Basketball | 1900 | 88762 | 68% | 0.070 | 11% | - | 25% | 112 |
| k | KXNBA3PTPROT NBA Player Threes Protec | 1574 | 85704 | 44% | 0.170 | 2% | - | 17% | 22 |
| k | KXNCAAWBTOTAL Women's College Basketba | 1819 | 71856 | 44% | 0.390 | 3% | - | 27% | 35 |
| k | KXNBAPRA NBA Player Points + Rebo | 989 | 69562 | 78% | 0.300 | 17% | - | 12% | 5 |
| k | KXNCAAFSPREAD College Football Spread | 2838 | 66370 | 69% | 0.020 | 1% | - | 22% | 550 |
| k | KXNCAAF1HSPREAD College Football 1st Hal | 1291 | 64590 | 84% | 0.040 | 5% | - | 25% | 237 |
| k | KXESOCCERGAME eSoccer Game | 4284 | 62921 | 26% | 0.730 | 5% | - | 23% | 37 |
| k | KXNBAASTPROT NBA Player Assists Prote | 1108 | 61442 | 51% | 0.230 | 3% | - | 12% | 4 |
| k | KXDOTA2MAP Dota 2 Map Winner | 364 | 59303 | 97% | 0.460 | 5% | - | 15% | 40 |
| k | KXNBAREBPROT NBA Player Rebounds Prot | 1889 | 49828 | 50% | 0.160 | 3% | - | 16% | 30 |
| k | KXNBAPTSPROT NBA Player Points Protec | 1276 | 47481 | 55% | 0.180 | 4% | - | 11% | 25 |
| k | KXUECLSCORE Correct Score | 540 | 46773 | 43% | 0.020 | 9% | - | 22% | 1009 |
| k | KXNCAAWBGAME Women's College Basketba | 548 | 45067 | 84% | 0.270 | 6% | - | 16% | 10 |
| k | KXNBA1HTEAMTOTAL NBA 1st Half Team Total | 616 | 45049 | 66% | 0.330 | 16% | - | 35% | 165 |
| k | KXNBA2HSPREAD NBA 2nd Half Spread | 589 | 41454 | 72% | 0.210 | 28% | - | 40% | 60 |
| k | KXUELSCORE Correct Score | 510 | 40966 | 49% | 0.020 | 9% | - | 13% | 2425 |
| k | KXNCAAWBSPREAD Women's College Basketba | 910 | 40778 | 47% | 0.320 | 9% | - | 53% | 30 |
| k | KXNBA2HTOTAL NBA 2nd Half Total | 589 | 39253 | 75% | 0.280 | 25% | - | 44% | 108 |
| k | KXNBA1HTOTAL NBA 1st Half Total | 532 | 38960 | 67% | 0.050 | 14% | - | 26% | 100 |
| k | KXNBA1HSPREAD NBA 1st Half Spread | 532 | 38520 | 67% | 0.050 | 14% | - | 23% | 129 |
| k | KXNCAAF1H College Football 1st Hal | 1113 | 38339 | 89% | 0.830 | 1% | - | 62% | 400 |
| k | KXNCAAFTOTAL College Football Total P | 2022 | 37253 | 68% | 0.030 | 2% | - | 31% | 372 |
| k | KXNCAAF1HTOTAL College Football 1st Hal | 856 | 34879 | 78% | 0.030 | 4% | - | 34% | 225 |
| k | KXNBA3QSPREAD NBA 3rd Quarter Spread | 403 | 28432 | 73% | 0.040 | 20% | - | 61% | 70 |
| k | KXNBA3QTOTAL NBA 3rd Quarter Total | 390 | 28267 | 74% | 0.050 | 21% | - | 51% | 100 |
| k | KXNBA2QSPREAD NBA 2nd Quarter Spread | 364 | 27365 | 69% | 0.040 | 16% | - | 26% | 100 |
| k | KXNBA2QTOTAL NBA 2nd Quarter Total | 364 | 26041 | 69% | 0.050 | 16% | - | 39% | 73 |
| k | KXNCAAMB1H Men's College Basketball | 249 | 25476 | 51% | 0.060 | 3% | - | 44% | 300 |
| k | KXNBA4QTOTAL NBA 4th Quarter Total | 390 | 24951 | 78% | 0.090 | 28% | - | 57% | 74 |
| k | KXNCAAMBGAME Men's College Basketball | 448 | 24861 | 73% | 0.020 | 4% | - | 13% | 376 |
| k | KXNBA4QSPREAD NBA 4th Quarter Spread | 403 | 24183 | 77% | 0.070 | 28% | - | 60% | 60 |

## Schema notes (raw keys seen)

- polymarket: active, archived, category, chatChannel, closed, combos, createdAt, description, elapsed, endDate, ended, eventState, fixtureId, gameId, hidden, id, insiderTradingRules, live, marketCounts, marketGroups, markets, metadata, participants, payoutEstimateMessage, payoutEstimateTime, period, primaryTag, score, seriesSlug, slug, sortType, sportradarGameId, startDate, startTime, streamProvider, streamRequiresAuth, tags, teams, ticker, title, updatedAt
- kalshi: can_close_early, close_time, created_time, custom_strike, early_close_condition, event_ticker, exchange_index, expected_expiration_time, expiration_time, expiration_value, last_price_dollars, latest_expiration_time, market_type, no_ask_dollars, no_bid_dollars, no_sub_title, notional_value_dollars, occurrence_datetime, open_interest_fp, open_time, previous_price_dollars, previous_yes_ask_dollars, previous_yes_bid_dollars, price_level_structure, price_ranges, result, rules_primary, rules_secondary, settlement_bounds_type, settlement_timer_seconds, status, strike_type, subtitle, ticker, title, updated_time, volume_24h_fp, volume_fp, yes_ask_dollars, yes_ask_size_fp, yes_bid_dollars, yes_bid_size_fp, yes_sub_title

