# Mr. P — sports radar

Updated 2026-11-09T03:38:18Z by `run-20261108T2321-42533654996` (last 7 days). Read-only scanner of every sports market on Polymarket US and Kalshi — it never places orders.
Kit: `mrp/mrp_sports_radar.py` on the `mrp` branch. Raw tape: `mrp/radar/<run>/`.

# Sports radar report

records 5,030,472 | 2026-11-06 03:35Z → 03:35Z | runs 15 | pairs matched 1750 | errors {'radar': 5, 'sp.stream': 2}

## Catalogue (latest inventory, 02:28Z)

Polymarket US sports events 4492 of 5423 active events; Kalshi near-term sports markets 5549 in 574 events; calls so far {'pm': 1529, 'k': 21346}; MB {'pm': 3355061036, 'k': 7267455003}

| venue | sport / league / type | markets | two-sided | med spread | vol 24h |
|---|---|---|---|---|---|
| pm | football / nfl / futures | 4091 | 55% | 0.010 | 0 |
| pm | football / cfb / futures | 1550 | 37% | 0.010 | 0 |
| pm | basketball / nba / futures | 1445 | 52% | 0.030 | 0 |
| pm | ice-hockey / nhl / futures | 779 | 91% | 0.010 | 0 |
| pm | basketball / cbb / basketball_team_full_game_winner | 741 | 19% | 0.040 | 0 |
| pm | basketball / wcbb / basketball_team_full_game_winner | 722 | 11% | 0.120 | 0 |
| k | KXNCAAFGAME / College Football Game | 512 | 100% | 0.110 | 475536 |
| pm | golf / austcham / futures | 470 | 25% | 0.499 | 0 |
| pm | soccer / epl / futures | 437 | 86% | 0.010 | 0 |
| pm | basketball / cbb / futures | 396 | 88% | 0.010 | 0 |
| pm | tennis / utr / tennis_match_winner | 308 | 10% | 0.400 | 0 |
| pm | soccer / ucl / futures | 285 | 79% | 0.010 | 0 |
| pm | table-tennis / setkameua / table_tennis_match_winner | 266 | 85% | 0.250 | 0 |
| pm | football / cfb / football_team_full_game_winner | 221 | 81% | 0.095 | 0 |
| pm | tennis / itfme / tennis_match_winner | 209 | 41% | 0.010 | 0 |
| pm | tennis / itfwo / tennis_match_winner | 155 | 39% | 0.010 | 0 |
| pm | soccer / lal / futures | 147 | 50% | 0.010 | 0 |
| pm | mma / ufc / futures | 145 | 81% | 0.010 | 0 |
| pm | boxing / boxing / futures | 145 | 0% | - | 0 |
| pm | macro /  / futures | 123 | 71% | 0.010 | 0 |
| pm | tennis / atp / tennis_match_winner | 121 | 94% | 0.010 | 0 |
| pm | basketball / nba / basketball_team_full_game_winner | 107 | 87% | 0.270 | 0 |
| pm | soccer / unl / soccer_team_full_time_winner | 102 | 88% | 0.030 | 0 |
| pm | soccer / sea / futures | 88 | 85% | 0.010 | 0 |
| pm | tennis / atp / futures | 83 | 35% | 0.010 | 0 |
| pm | soccer / bun / futures | 80 | 84% | 0.010 | 0 |
| pm | soccer / lg1 / futures | 79 | 86% | 0.010 | 0 |
| pm | tennis / wta / futures | 75 | 44% | 0.020 | 0 |
| pm | baseball / mlb / futures | 72 | 65% | 0.001 | 0 |
| pm | soccer / afcq / soccer_team_full_time_winner | 72 | 56% | 0.460 | 0 |
| pm | macro / usgas / futures | 66 | 71% | 0.010 | 0 |
| k | KXNBA1HTEAMTOTAL / NBA 1st Half Team Total | 66 | 100% | 0.085 | 23480 |
| pm | macro / usdsl / futures | 63 | 8% | 0.170 | 0 |
| pm | tennis / atpdb / tennis_match_winner | 59 | 34% | 0.390 | 0 |
| k | KXNBA1HSPREAD / NBA 1st Half Spread | 57 | 100% | 0.010 | 297426 |
| k | KXNBA1HTOTAL / NBA 1st Half Total | 57 | 100% | 0.010 | 238728 |
| pm | esports / dota2 / esports_match_winner | 54 | 54% | 0.170 | 0 |
| pm | esports / cs2 / esports_match_winner | 53 | 70% | 0.020 | 0 |
| pm | technology /  / futures | 52 | 77% | 0.010 | 0 |
| pm | golf / masttour / futures | 52 | 100% | 0.410 | 0 |
| pm | table-tennis / czechligapro / table_tennis_match_winner | 52 | 15% | 0.445 | 0 |
| pm | table-tennis / setkamecz / table_tennis_match_winner | 48 | 75% | 0.250 | 0 |
| k | KXNBA1H / NBA 1st Half Winner | 45 | 100% | 0.090 | 143904 |
| k | KXNBA1Q / NBA 1st Quarter Winner | 42 | 100% | 0.170 | 62741 |
| pm | soccer / mls / futures | 39 | 92% | 0.010 | 0 |
| pm | soccer / lmx / futures | 36 | 58% | 0.120 | 0 |
| pm | soccer / uel / futures | 36 | 0% | - | 0 |
| pm | soccer / uecl / futures | 36 | 0% | - | 0 |
| pm | soccer / sercc / soccer_team_full_time_winner | 36 | 50% | 0.265 | 0 |
| pm | soccer / efl2 / soccer_team_full_time_winner | 36 | 72% | 0.060 | 0 |
| pm | table-tennis / setkamemd / table_tennis_match_winner | 36 | 8% | 0.390 | 0 |
| pm | motorsports / f1 / futures | 35 | 63% | 0.001 | 0 |
| pm | soccer / ligaf / soccer_team_full_time_winner | 33 | 42% | 0.480 | 0 |
| pm | soccer / engnl / soccer_team_full_time_winner | 33 | 100% | 0.060 | 0 |
| k | KXLIGAMXGAME / Liga MX Game | 33 | 100% | 0.530 | 1712131 |
| k | KXNFLGAME / NFL Game | 32 | 100% | 0.010 | 17883900 |
| k | KXLIGAMXGOAL / Goalscorer | 32 | 100% | 0.060 | 18416 |
| pm | soccer / sercb / soccer_team_full_time_winner | 30 | 40% | 0.480 | 0 |
| pm | ice-hockey / nhl / hockey_team_full_game_winner | 30 | 100% | 0.010 | 0 |
| pm | soccer / serca / soccer_team_full_time_winner | 30 | 33% | 0.480 | 0 |

## Opportunities

| kind | distinct | hits | max margin $/contract | max persistence | fresh-BBO still open |
|---|---|---|---|---|---|
| decided_k | 193 | 2933 | 0.9573 | 35 min | 0/0 |
| decided_pm | 18 | 311 | 0.9891 | 11 min | 177/311 |
| decided_pm_closed | 9 | 153 | 0.9891 | 18 min | 0/153 |
| dutch_k | 12 | 195 | 0.0252 | 18 min | 0/0 |
| dutch_pm | 67 | 3483 | 0.3987 | 50 min | 0/0 |
| implication_k | 93 | 764 | 0.7784 | 33 min | 0/0 |
| lag_k_settled | 222 | 35268 | 0.9947 | 321 min | 28117/33048 |
| lag_k_settled_closed | 191 | 3052 | 0.9973 | 202 min | 0/3052 |

Top by persistence × hits:

- **lag_k_settled** basketball — KTP Basket Kotka vs. Lahti Basketball — bid 0.99 ask - sell_yes @ 0.99 | margin 0.9891 | 321 min, 1291 hits | fresh bbo 0.99/- depth 7/0 | score 100-81 VFT
- **lag_k_settled** basketball — Baskets Bonn vs. Basketball Lowen Braunschweig — bid 0.99 ask - sell_yes @ 0.99 | margin 0.9891 | 203 min, 915 hits | score 97-87 FT
- **lag_k_settled** football — South Florida vs. East Carolina — bid 0.29 ask 0.30 sell_yes @ 0.295 | margin 0.7008 | 115 min, 796 hits | fresh bbo 0.29/0.30 depth 45/67 | score 10-17 Q4
- **lag_k_settled** basketball — Western Carolina vs. UNC Asheville — bid 0.99 ask - sell_yes @ 0.99 | margin 0.9891 | 262 min, 570 hits | fresh bbo 0.99/- depth 14/0 | score 83-75 FT
- **lag_k_settled** football — Michigan State vs. Michigan — bid 0.78 ask 0.78 sell_yes @ 0.775 | margin 0.7848 | 180 min, 616 hits | fresh bbo 0.78/0.78 depth 65/34 | score 9-0 End Q3
- **lag_k_settled** football — Iowa vs. Northwestern — bid 0.91 ask 0.91 sell_yes @ 0.905 | margin 0.8968 | 149 min, 641 hits | fresh bbo 0.91/0.91 depth 76/18 | score 14-0 HT
- **lag_k_settled** football — Western Illinois vs. Eastern Illinois — bid 0.63 ask - sell_yes @ 0.63 | margin 0.9945 | 96 min, 694 hits | fresh bbo 0.63/- depth 11/0 | score 44-23 FT
- **lag_k_settled** football — Alabama State vs. Texas Southern — bid 0.99 ask - sell_yes @ 0.995 | margin 0.9945 | 123 min, 486 hits | fresh bbo 0.99/- depth 11/0 | score 34-31 FT
- **lag_k_settled** soccer — Manchester United FC vs. Aston Villa FC — bid 0.48 ask 0.49 buy_yes @ 0.49 | margin 0.5265 | 121 min, 479 hits | fresh bbo 0.48/0.49 depth 36/40 | score 0-0 
- **lag_k_settled** soccer — Manchester United FC vs. Aston Villa FC — bid 0.24 ask 0.25 sell_yes @ 0.24 | margin 0.2322 | 121 min, 479 hits | fresh bbo 0.24/0.25 depth 18/41 | score 0-0 
- **lag_k_settled** soccer — Manchester United FC vs. Aston Villa FC — bid 0.28 ask 0.29 sell_yes @ 0.28 | margin 0.2801 | 121 min, 479 hits | fresh bbo 0.28/0.29 depth 25/49 | score 0-0 
- **lag_k_settled** esports — LPH Gaming vs.  Phantom Academy — bid 0.57 ask 0.58 sell_yes @ 0.57 | margin 0.5467 | 120 min, 478 hits | fresh bbo 0.57/0.58 depth 7/8 | score - NS
- **lag_k_settled** basketball — Maxima Roma vs. Pallacanestro Cantu — bid 0.81 ask 0.85 sell_yes @ 0.81 | margin 0.8700 | 116 min, 460 hits | fresh bbo 0.81/0.85 depth 19/9 | score 6-7 Q1
- **lag_k_settled** basketball — Northern Iowa (W) vs. South Dakota State (W) — bid 0.15 ask 0.16 sell_yes @ 0.15 | margin 0.1379 | 115 min, 458 hits | fresh bbo 0.15/0.16 depth 11/9 | score - NS
- **lag_k_settled** basketball — Washington State (W) vs. Oregon (W) — bid 0.01 ask 0.02 sell_yes @ 0.01 | margin 0.0091 | 115 min, 457 hits | fresh bbo 0.01/0.02 depth 1/16 | score 0-0 NS
- **lag_k_settled** esports — All Gamers vs. Weibo Gaming — bid 0.21 ask 0.51 sell_yes @ 0.21 | margin 0.1942 | 92 min, 463 hits | fresh bbo 0.21/0.51 depth 3/5 | score - NS
- **lag_k_settled** football — Southern Illinois vs. Indiana State — bid 0.99 ask - sell_yes @ 0.995 | margin 0.9945 | 118 min, 414 hits | fresh bbo 0.99/- depth 14/0 | score 37-20 FT
- **lag_k_settled** football — South Dakota State vs. Northern Iowa — bid 0.99 ask - sell_yes @ 0.995 | margin 0.9945 | 182 min, 304 hits | score 41-15 FT
- **lag_k_settled** tennis — Arcangioli - Cirotte vs. Lizunova - Masiianskaia — bid 0.64 ask 0.69 sell_yes @ 0.64 | margin 0.6800 | 100 min, 385 hits | fresh bbo 0.60/0.62 depth 11/17 | score 1-1:30-30 S1
- **lag_k_settled** football — Louisville vs. Georgia Tech — bid 0.97 ask 0.97 sell_yes @ 0.97 | margin 0.9945 | 107 min, 350 hits | fresh bbo 0.97/0.97 depth 49/5 | score 27-10 HT
- **lag_k_settled** basketball — Sacramento State vs. Santa Clara — bid 0.04 ask 0.05 sell_yes @ 0.04 | margin 0.0364 | 118 min, 327 hits | fresh bbo 0.04/0.05 depth 4/10 | score - NS
- **lag_k_settled** soccer — Club Atletico de Madrid vs. FC Barcelona — bid 0.26 ask 0.27 sell_yes @ 0.26 | margin 0.2513 | 92 min, 338 hits | fresh bbo 0.26/0.27 depth 18/32 | score 0-0 
- **lag_k_settled** soccer — Club Atletico de Madrid vs. FC Barcelona — bid 0.20 ask 0.21 sell_yes @ 0.2 | margin 0.1942 | 92 min, 338 hits | fresh bbo 0.20/0.21 depth 14/20 | score 0-0 
- **lag_k_settled** soccer — Club Atletico de Madrid vs. FC Barcelona — bid 0.53 ask 0.54 buy_yes @ 0.54 | margin 0.4463 | 92 min, 338 hits | fresh bbo 0.52/0.53 depth 21/36 | score 0-0 
- **lag_k_settled** football — West Florida vs. North Alabama — bid 0.34 ask 0.35 sell_yes @ 0.345 | margin 0.3332 | 111 min, 311 hits | fresh bbo 0.34/0.35 depth 22/20 | score - NS

## Live paper trades (no orders; Kalshi prices, taker fees)

Ledger L2-2026-11-01 (earlier ledgers excluded: none)

**Total closed P&L: $-530.01 on $1848.01 staked (-28.7%)**

| rule | entries | closed | winners | staked | P&L | ROI |
|---|---|---|---|---|---|---|
| R1 anchor [ncaaf] | 55 | 55 | 28 | $554.80 | $-32.80 | -6% |
| R1 anchor [nfl] | 6 | 6 | 1 | $60.54 | $-45.54 | -75% |
| R2 q1cheap [ncaaf] | 46 | 46 | 6 | $240.84 | $-79.84 | -33% |
| R2 q1cheap [nfl] | 9 | 8 | 0 | $42.06 | $-42.06 | -100% |
| R3 blowout [ncaaf] | 23 | 23 | 1 | $487.42 | $-306.42 | -63% |
| R3 blowout [nfl] | 1 | 1 | 0 | $21.08 | $-21.08 | -100% |
| R4 halftime [ncaaf] | 27 | 27 | 16 | $133.42 | $+12.58 | +9% |
| R6 decided [other] | 18 | 17 | 14 | $307.86 | $-14.86 | -5% |

| time (UTC) | rule | game | team | entry | contracts | why | result |
|---|---|---|---|---|---|---|---|
| 01:31 | R2 q1cheap | TB Buccaneers vs. CHI Bears | Tampa Bay | 0.19 | 26 | Q1 ask 0.19, score 0-0 | open |
| 22:59 | R1 anchor | GB Packers vs. NE Patriots | Green Bay | 0.65 | 15 | pregame dog (mid 0.40) leads 24-14 in Q2, ask 0.65 | final score (pending Kalshi settlement): 1.00, $+5.01 |
| 22:09 | R3 blowout | GB Packers vs. NE Patriots | New England | 0.14 | 142 | down 17 in Q2, ask 0.14 | final score (pending Kalshi settlement): 0.00, $-21.08 |
| 21:57 | R2 q1cheap | GB Packers vs. NE Patriots | New England | 0.20 | 25 | Q1 ask 0.20, score 14-0 | final score (pending Kalshi settlement): 0.00, $-5.28 |
| 21:43 | R2 q1cheap | HOU Texans vs. LA Chargers | Los Angeles C | 0.20 | 25 | Q1 ask 0.20, score 10-3 | final score (pending Kalshi settlement): 0.00, $-5.28 |
| 21:26 | R2 q1cheap | ARI Cardinals vs. SEA Seahaw | Arizona | 0.20 | 25 | Q1 ask 0.20, score 0-0 | final score (pending Kalshi settlement): 0.00, $-5.28 |
| 21:26 | R2 q1cheap | LV Raiders vs. SF 49ers | Las Vegas | 0.20 | 25 | Q1 ask 0.20, score 0-0 | final score (pending Kalshi settlement): 0.00, $-5.28 |
| 19:51 | R1 anchor | DEN Broncos vs. CAR Panthers | Carolina | 0.44 | 22 | pregame dog (mid 0.40) leads 13-14 in Q3, ask 0.44 | final score (pending Kalshi settlement): 0.00, $-10.06 |
| 19:49 | R1 anchor | CLE Browns vs. NO Saints | Cleveland | 0.43 | 23 | pregame dog (mid 0.39) leads 6-3 in Q3, ask 0.43 | final score (pending Kalshi settlement): 0.00, $-10.28 |
| 18:52 | R1 anchor | NY Giants vs. PHI Eagles | Philadelphia | 0.48 | 20 | pregame dog (mid 0.41) leads 6-8 in Q2, ask 0.48 | final score (pending Kalshi settlement): 0.00, $-9.95 |
| 18:42 | R1 anchor | DAL Cowboys vs. IND Colts | Indianapolis | 0.38 | 26 | pregame dog (mid 0.36) leads 3-7 in Q2, ask 0.38 | final score (pending Kalshi settlement): 0.00, $-10.31 |
| 18:39 | R1 anchor | LA Rams vs. WAS Commanders | Washington | 0.48 | 20 | pregame dog (mid 0.34) leads 3-9 in Q2, ask 0.48 | final score (pending Kalshi settlement): 0.00, $-9.95 |
| 18:36 | R2 q1cheap | DEN Broncos vs. CAR Panthers | Carolina | 0.19 | 26 | Q1 ask 0.19, score 10-0 | final score (pending Kalshi settlement): 0.00, $-5.22 |
| 18:10 | R2 q1cheap | DET Lions vs. MIA Dolphins | Miami | 0.19 | 26 | Q1 ask 0.19, score 0-0 | final score (pending Kalshi settlement): 0.00, $-5.22 |
| 18:09 | R2 q1cheap | CLE Browns vs. NO Saints | Cleveland | 0.20 | 25 | Q1 ask 0.20, score 0-0 | final score (pending Kalshi settlement): 0.00, $-5.28 |
| 18:03 | R2 q1cheap | NY Jets vs. KC Chiefs | New York J | 0.19 | 26 | Q1 ask 0.19, score 0-0 | final score (pending Kalshi settlement): 0.00, $-5.22 |
| 05:17 | R1 anchor | West Virginia vs. Texas Tech | West Virginia | 0.58 | 17 | pregame dog (mid 0.12) leads 48-41 in Q3, ask 0.58 | final score (pending Kalshi settlement): 0.00, $-10.15 |
| 04:45 | R3 blowout | Wyoming vs. UNLV | UNLV | 0.13 | 153 | down 17 in Q2, ask 0.13 | final score (pending Kalshi settlement): 0.00, $-21.10 |
| 04:31 | R4 halftime | Hawai'i vs. UTEP | Hawai'i | 0.74 | 6 | UTEP rose +0.030 at halftime; fade it | final score (pending Kalshi settlement): 1.00, $+1.48 |
| 04:29 | R1 anchor | Texas State vs. Oregon State | Texas St. | 0.56 | 17 | pregame dog (mid 0.37) leads 14-7 in Q2, ask 0.56 | final score (pending Kalshi settlement): 1.00, $+7.19 |
| 04:23 | R1 anchor | Wyoming vs. UNLV | Wyoming | 0.63 | 15 | pregame dog (mid 0.40) leads 10-7 in Q2, ask 0.63 | final score (pending Kalshi settlement): 1.00, $+5.31 |
| 03:02 | R2 q1cheap | Hawai'i vs. UTEP | UTEP | 0.17 | 29 | Q1 ask 0.17, score 0-0 | final score (pending Kalshi settlement): 0.00, $-5.22 |
| 02:36 | R2 q1cheap | West Virginia vs. Texas Tech | West Virginia | 0.16 | 31 | Q1 ask 0.16, score 0-0 | final score (pending Kalshi settlement): 0.00, $-5.25 |
| 01:54 | R4 halftime | Abilene Christian vs. Tarlet | Tarleton St. | 0.85 | 5 | Abilene Christian rose +0.085 at halftime; fade it | final score (pending Kalshi settlement): 1.00, $+0.71 |
| 01:29 | R1 anchor | Oklahoma vs. Florida | Oklahoma | 0.49 | 20 | pregame dog (mid 0.39) leads 3-0 in Q2, ask 0.49 | final score (pending Kalshi settlement): 1.00, $+9.85 |
| 01:29 | R3 blowout | Georgia vs. Ole Miss | Ole Miss | 0.08 | 250 | down 21 in Q2, ask 0.08 | final score (pending Kalshi settlement): 0.00, $-21.29 |
| 01:18 | R6 decided | Northern Colorado (W) vs. Te | Both Teams To Score | 0.78 | 25 | both scored 4-11 | kalshi settled: 1.00, $+5.20 |
| 01:13 | R2 q1cheap | Iowa vs. Northwestern | Northwestern | 0.20 | 25 | Q1 ask 0.20, score 7-0 | final score (pending Kalshi settlement): 0.00, $-5.28 |
| 01:13 | R1 anchor | Air Force vs. Army | Air Force | 0.51 | 19 | pregame dog (mid 0.39) leads 3-0 in Q2, ask 0.51 | final score (pending Kalshi settlement): 1.00, $+8.98 |
| 01:05 | R2 q1cheap | Georgia vs. Ole Miss | Ole Miss | 0.20 | 25 | Q1 ask 0.20, score 7-0 | final score (pending Kalshi settlement): 0.00, $-5.28 |
| 00:53 | R1 anchor | Utah Tech vs. UC Davis | Utah Tech | 0.50 | 20 | pregame dog (mid 0.14) leads 7-0 in Q2, ask 0.50 | final score (pending Kalshi settlement): 0.00, $-10.35 |
| 00:48 | R3 blowout | Incarnate Word vs. Southeast | Southeastern Louisiana | 0.13 | 153 | down 18 in Q2, ask 0.13 | final score (pending Kalshi settlement): 0.00, $-21.10 |
| 00:37 | R2 q1cheap | Louisville vs. Georgia Tech | Georgia Tech | 0.17 | 29 | Q1 ask 0.17, score 0-0 | final score (pending Kalshi settlement): 0.00, $-5.22 |
| 00:36 | R2 q1cheap | Incarnate Word vs. Southeast | Southeastern Louisiana | 0.20 | 25 | Q1 ask 0.20, score 14-3 | final score (pending Kalshi settlement): 0.00, $-5.28 |
| 00:21 | R2 q1cheap | Sam Houston vs. Jacksonville | Sam Houston | 0.15 | 33 | Q1 ask 0.15, score 0-0 | final score (pending Kalshi settlement): 0.00, $-5.24 |
| 00:13 | R3 blowout | West Georgia vs. Central Ark | West Georgia | 0.09 | 222 | down 18 in Q3, ask 0.09 | final score (pending Kalshi settlement): 0.00, $-21.25 |
| 00:08 | R2 q1cheap | Abilene Christian vs. Tarlet | Abilene Christian | 0.19 | 26 | Q1 ask 0.19, score 0-6 | final score (pending Kalshi settlement): 0.00, $-5.22 |
| 00:03 | R2 q1cheap | Utah Tech vs. UC Davis | Utah Tech | 0.17 | 29 | Q1 ask 0.17, score 0-0 | final score (pending Kalshi settlement): 0.00, $-5.22 |
| 00:03 | R1 anchor | McNeese vs. Houston Christia | McNeese | 0.62 | 16 | pregame dog (mid 0.43) leads 3-0 in Q3, ask 0.62 | final score (pending Kalshi settlement): 1.00, $+5.82 |
| 23:52 | R4 halftime | West Georgia vs. Central Ark | West Georgia | 0.22 | 22 | Central Arkansas rose +0.040 at halftime; fade it | final score (pending Kalshi settlement): 0.00, $-5.10 |

### Score reaction speed (live, 15 s): share of the 3-minute move done by +15 s / +30 s / +60 s

- 26NOV08CLENO 13-16: 0% / 0% / 0%
- 26NOV08CLENO 13-16: -0% / -0% / -0%
- 26NOV08DALIND 20-20: -0% / -0% / -0%
- 26NOV08DALIND 20-20: 0% / 0% / 0%
- 26NOV08CLENO 16-23: 0% / 0% / 0%
- 26NOV08CLENO 16-23: -0% / -0% / -0%
- 26NOV08DALIND 20-23: -0% / -0% / -0%
- 26NOV08DALIND 20-23: 0% / 0% / 0%
- 26NOV08DALIND 26-23: -0% / -20% / -40%
- 26NOV08DALIND 26-23: 0% / -17% / -17%
- 26NOV08DALIND 27-23: -20% / -20% / -20%
- 26NOV08DALIND 27-23: 0% / 0% / 0%
- 26NOV08CLENO 22-23: -17% / -17% / -17%
- 26NOV08CLENO 22-23: -20% / -20% / -20%
- 26NOV08GBNE 7-0: -0% / -0% / -0%
- 26NOV08GBNE 7-0: 0% / 0% / 0%
- 26NOV08GBNE 24-7: 0% / 0% / 0%
- 26NOV08GBNE 24-7: -0% / -0% / -0%
- 26NOV08TBCHI 0-0: -0% / -0% / 50%
- 26NOV08TBCHI 0-0: 0% / 0% / 50%

## Bot latency map: how long a decided Kalshi market stays mispriced

| sport | series | markets | already priced | mispriced then fixed | median s mispriced | closed/timeout | contradictions | cheapest ask (size) | resting @0.97 contracts / $ | settled right / wrong |
|---|---|---|---|---|---|---|---|---|---|---|
| football | KXNCAAFGAME | 161 | 158 | 0 | - | 0 | 3 | - | 0 / $0.00 | 155 / 0 |
| basketball | KXNCAAWBTOTAL | 131 | 131 | 0 | - | 0 | 0 | - | 0 / $0.00 | 109 / 0 |
| football | KXNCAAFTOTAL | 86 | 81 | 5 | 2 | 0 | 0 | 0.62 (1974) | 0 / $0.00 | 86 / 0 |
| soccer | KXSERIECTOTAL | 74 | 64 | 10 | 21 | 0 | 0 | 0.85 (48) | 0 / $0.00 | 74 / 0 |
| soccer | KXBUNDESLIGA2TOTAL | 61 | 56 | 4 | 8 | 1 | 0 | 0.01 (14030) | 11015 / $330.45 | 60 / 1 |
| soccer | KXMLSTOTAL | 60 | 60 | 0 | - | 0 | 0 | - | 0 / $0.00 | 32 / 0 |
| soccer | KXBELGIANPLTOTAL | 51 | 50 | 1 | 7 | 0 | 0 | 0.94 (1009) | 0 / $0.00 | 51 / 0 |
| basketball | KXNCAAMBTOTAL | 48 | 44 | 0 | - | 4 | 0 | 0.64 (1210) | 0 / $0.00 | 24 / 4 |
| soccer | KXTHAIL1TOTAL | 45 | 43 | 2 | 21 | 0 | 0 | 0.93 (0) | 0 / $0.00 | 45 / 0 |
| soccer | KXIDNSLTOTAL | 42 | 39 | 2 | 158 | 0 | 1 | 0.87 (10) | 0 / $0.00 | 42 / 0 |
| tennis | KXATPSETWINNER | 42 | 42 | 0 | - | 0 | 0 | - | 0 / $0.00 | 42 / 0 |
| soccer | KXCZEFNLTOTAL | 42 | 42 | 0 | - | 0 | 0 | - | 0 / $0.00 | 42 / 0 |
| soccer | KXELITESERIENTOTAL | 42 | 40 | 1 | 26 | 0 | 1 | 0.75 (200) | 11 / $0.34 | 42 / 0 |
| soccer | KXAUTBUNDESTOTAL | 41 | 37 | 2 | 4 | 0 | 2 | 0.98 (22) | 0 / $0.00 | 41 / 0 |
| football | KXNCAAFSPREAD | 41 | 41 | 0 | - | 0 | 0 | - | 0 / $0.00 | 41 / 0 |
| soccer | KXCHNSLTOTAL | 41 | 39 | 2 | 1011 | 0 | 0 | 0.47 (3506) | 722 / $21.67 | 41 / 0 |
| basketball | KXNCAAMBSPREAD | 40 | 35 | 0 | - | 5 | 0 | 0.60 (500) | 0 / $0.00 | 24 / 3 |
| soccer | KXLIGAMXTOTAL | 38 | 36 | 1 | 242 | 1 | 0 | 0.60 (7) | 7233 / $216.99 | 38 / 0 |
| soccer | KXEKSTRAKLASATOTAL | 37 | 32 | 5 | 27 | 0 | 0 | 0.60 (58) | 27 / $0.82 | 32 / 0 |
| soccer | KXALLSVENSKANTOTAL | 37 | 37 | 0 | - | 0 | 0 | - | 0 / $0.00 | 37 / 0 |
| soccer | KXTFF1LIGTOTAL | 33 | 31 | 2 | 2 | 0 | 0 | 0.83 (9000) | 0 / $0.00 | 33 / 0 |
| soccer | KXARGPREMDIVTOTAL | 29 | 27 | 0 | - | 2 | 0 | 0.01 (69347) | 37106 / $1113.18 | 28 / 1 |
| soccer | KXHUNNB1TOTAL | 29 | 27 | 2 | 25 | 0 | 0 | 0.95 (7) | 0 / $0.00 | 29 / 0 |
| soccer | KXEREDIVISIETOTAL | 27 | 26 | 0 | - | 1 | 0 | 0.65 (20) | 0 / $0.00 | 26 / 1 |
| soccer | KXDIMAYORTOTAL | 27 | 26 | 1 | 1 | 0 | 0 | 0.72 (0) | 0 / $0.00 | 22 / 0 |
| soccer | KXECULPTOTAL | 26 | 26 | 0 | - | 0 | 0 | - | 0 / $0.00 | 26 / 0 |
| football | KXNFLGAME | 24 | 21 | 2 | 61 | 0 | 1 | 0.72 (0) | 0 / $0.00 | 16 / 0 |
| soccer | KXAPFDDHTOTAL | 23 | 23 | 0 | - | 0 | 0 | - | 0 / $0.00 | 22 / 0 |
| basketball | KXEUROLEAGUETOTAL | 22 | 22 | 0 | - | 0 | 0 | - | 0 / $0.00 | 22 / 0 |
| soccer | KXMLSSPREAD | 22 | 22 | 0 | - | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
| soccer | KXBRASILEIROBTOTAL | 21 | 20 | 0 | - | 1 | 0 | 0.01 (61246) | 3818 / $114.53 | 18 / 1 |
| soccer | KXKLEAGUETOTAL | 21 | 21 | 0 | - | 0 | 0 | - | 0 / $0.00 | 21 / 0 |
| soccer | KXJLEAGUE1HTOTAL | 21 | 18 | 3 | 20 | 0 | 0 | 0.91 (20) | 51 / $1.54 | 21 / 0 |
| soccer | KXJLEAGUE1H | 21 | 21 | 0 | - | 0 | 0 | - | 0 / $0.00 | 21 / 0 |
| tennis | KXWTASETWINNER | 20 | 18 | 2 | 739 | 0 | 0 | 0.67 (103) | 359 / $10.78 | 19 / 0 |
| soccer | KXBUNDESLIGAWTOTAL | 20 | 20 | 0 | - | 0 | 0 | - | 27 / $0.82 | 20 / 0 |
| soccer | KXCZEFLTOTAL | 20 | 20 | 0 | - | 0 | 0 | - | 0 / $0.00 | 20 / 0 |
| soccer | KXLIGUE2TOTAL | 18 | 17 | 0 | - | 1 | 0 | 0.56 (600) | 48 / $1.44 | 18 / 0 |
| soccer | KXJ2LEAGUETOTAL | 18 | 18 | 0 | - | 0 | 0 | - | 0 / $0.00 | 18 / 0 |
| soccer | KXLIGAPORTUGALTOTAL | 17 | 16 | 1 | 4 | 0 | 0 | 0.98 (4594) | 0 / $0.00 | 17 / 0 |
| soccer | KXJ2LEAGUEGAME | 16 | 16 | 0 | - | 0 | 0 | - | 0 / $0.00 | 16 / 0 |
| soccer | KXMLSGAME | 16 | 16 | 0 | - | 0 | 0 | - | 0 / $0.00 | 9 / 0 |
| soccer | KXLIGAEXPTOTAL | 16 | 16 | 0 | - | 0 | 0 | - | 0 / $0.00 | 16 / 0 |
| soccer | KXHNLTOTAL | 15 | 15 | 0 | - | 0 | 0 | - | 0 / $0.00 | 15 / 0 |
| soccer | KXMLS1H | 15 | 15 | 0 | - | 0 | 0 | - | 0 / $0.00 | 15 / 0 |
| soccer | KXCHLLDPTOTAL | 15 | 15 | 0 | - | 0 | 0 | - | 0 / $0.00 | 14 / 0 |
| soccer | KXLIGAFTOTAL | 14 | 11 | 3 | 32 | 0 | 0 | 0.14 (169) | 189 / $5.66 | 14 / 0 |
| soccer | KXDENSUPERLIGATOTAL | 13 | 13 | 0 | - | 0 | 0 | - | 0 / $0.00 | 13 / 0 |
| basketball | KXNCAAFTOTAL | 12 | 2 | 0 | - | 10 | 0 | 0.61 (609) | 0 / $0.00 | 9 / 3 |
| basketball | KXNCAAWBGAME | 12 | 12 | 0 | - | 0 | 0 | - | 0 / $0.00 | 10 / 0 |
| basketball | KXEUROLEAGUESPREAD | 12 | 12 | 0 | - | 0 | 0 | - | 0 / $0.00 | 12 / 0 |
| basketball | KXABASPREAD | 12 | 12 | 0 | - | 0 | 0 | - | 0 / $0.00 | 12 / 0 |
| soccer | KXMLS1HTOTAL | 12 | 12 | 0 | - | 0 | 0 | - | 0 / $0.00 | 12 / 0 |
| soccer | KXJLEAGUETOTAL | 11 | 11 | 0 | - | 0 | 0 | - | 0 / $0.00 | 11 / 0 |
| soccer | KXBUNDESLIGASPREAD | 11 | 11 | 0 | - | 0 | 0 | - | 0 / $0.00 | 11 / 0 |
| basketball | KXABATOTAL | 11 | 11 | 0 | - | 0 | 0 | - | 0 / $0.00 | 11 / 0 |
| soccer | KXMLSBTTS | 11 | 10 | 1 | 2 | 0 | 0 | 0.75 (500) | 0 / $0.00 | 10 / 0 |
| ice-hockey | KXAHLGAME | 10 | 10 | 0 | - | 0 | 0 | - | 0 / $0.00 | 10 / 0 |
| soccer | KXJ2LEAGUESPREAD | 10 | 10 | 0 | - | 0 | 0 | - | 0 / $0.00 | 10 / 0 |
| soccer | KXBUNDESLIGATOTAL | 10 | 10 | 0 | - | 0 | 0 | - | 0 / $0.00 | 10 / 0 |
| soccer | KXBULFLTOTAL | 10 | 10 | 0 | - | 0 | 0 | - | 0 / $0.00 | 10 / 0 |
| tennis | KXATPCHALLENGERMATCH | 10 | 10 | 0 | - | 0 | 0 | - | 0 / $0.00 | 10 / 0 |
| soccer | KXLALIGA2TOTAL | 8 | 6 | 2 | 2 | 0 | 0 | 0.84 (75) | 0 / $0.00 | 8 / 0 |
| esports | KXCS2GAME | 8 | 8 | 0 | - | 0 | 0 | - | 0 / $0.00 | 8 / 0 |
| soccer | KXROML1TOTAL | 7 | 7 | 0 | - | 0 | 0 | - | 0 / $0.00 | 7 / 0 |
| soccer | KXJLEAGUE1HBTTS | 7 | 6 | 1 | 79 | 0 | 0 | 0.95 (1) | 3 / $0.09 | 7 / 0 |
| basketball | KXNCAAMBGAME | 7 | 7 | 0 | - | 0 | 0 | - | 0 / $0.00 | 5 / 0 |
| soccer | KXUAEPLTOTAL | 6 | 6 | 0 | - | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| soccer | KXBUNDESLIGA1HTOTAL | 6 | 6 | 0 | - | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| soccer | KXSUPERLIGTOTAL | 6 | 6 | 0 | - | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| soccer | KXKLEAGUE1HTOTAL | 6 | 6 | 0 | - | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| esports | KXCS2TOTALMAPS | 5 | 5 | 0 | - | 0 | 0 | - | 0 / $0.00 | 5 / 0 |
| soccer | KXBRASILEIROTOTAL | 5 | 5 | 0 | - | 0 | 0 | - | 0 / $0.00 | 5 / 0 |
| soccer | KXSVK1LTOTAL | 5 | 5 | 0 | - | 0 | 0 | - | 0 / $0.00 | 5 / 0 |
| soccer | KXSERIECBTTS | 5 | 5 | 0 | - | 0 | 0 | - | 0 / $0.00 | 5 / 0 |
| soccer | KXCHNSLBTTS | 5 | 4 | 0 | - | 1 | 0 | 0.12 (11) | 361 / $10.82 | 4 / 1 |
| soccer | KXEKSTRAKLASASPREAD | 5 | 5 | 0 | - | 0 | 0 | - | 0 / $0.00 | 0 / 0 |
| basketball | KXEUROLEAGUEGAME | 4 | 4 | 0 | - | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
| soccer | KXPERLIGA1TOTAL | 4 | 4 | 0 | - | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
| basketball | KXKBLGAME | 4 | 4 | 0 | - | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
| tennis | KXATPCHALLENGERDOUBLES | 4 | 4 | 0 | - | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
| soccer | KXALLSVENSKANSPREAD | 4 | 4 | 0 | - | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
| soccer | KXMLS1HBTTS | 4 | 4 | 0 | - | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
| soccer | KXJLEAGUESPREAD | 4 | 4 | 0 | - | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
| soccer | KXEPLSPREAD | 4 | 4 | 0 | - | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
| basketball | KXNCAAFGAME | 3 | 0 | 0 | - | 3 | 0 | 0.79 (3984) | 295 / $8.84 | 3 / 0 |
| soccer | KXJ2LEAGUEBTTS | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXTHAIL1BTTS | 3 | 2 | 1 | 29 | 0 | 0 | 0.97 (1) | 0 / $0.00 | 3 / 0 |
| soccer | KXEFLCHAMPIONSHIP1H | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXSERIEA1H | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXSERIEA1HTOTAL | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXEFLCHAMPIONSHIPBTTS | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXEFLCHAMPIONSHIPGAME | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXEFLCHAMPIONSHIPTOTAL | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXBRASILEIROB1HTOTAL | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXEPL1HTOTAL | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXLIGUE1BTTS | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXLALIGA1H | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| tennis | KXWTAMATCH | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| basketball | KXJBLEAGUEGAME | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXJLEAGUEGAME | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXJLEAGUEBTTS | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| tennis | KXWTADOUBLES | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXBUNDESLIGA1HBTTS | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| esports | KXCS2SPREAD | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| basketball | KXAUTBSLGAME | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| basketball | KXABAGAME | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| basketball | KXACBTOTAL | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXBELGIANPLBTTS | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXBRASILEIROB1H | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXKLEAGUE1HBTTS | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| esports | KXDOTA2GAME | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXBUNDESLIGA2BTTS | 2 | 1 | 1 | 4 | 0 | 0 | 0.90 (24) | 8 / $0.24 | 2 / 0 |
| soccer | KXELITESERIENBTTS | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| basketball | KXBBSERIEATOTAL | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXCOPADOBRASILTOTAL | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| basketball | KXNBAGAME | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXTFF1LIGBTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXBUNDESLIGAWBTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXEREDIVISIE1HBTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXLIGUE2BTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXSERIEA1HBTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXSLGREECETOTAL | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXSVNPLTOTAL | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXARGPREMDIVBTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXBRASILEIROB1HBTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| basketball | KXMLSBTTS | 1 | 0 | 0 | - | 1 | 0 | 0.62 (1275) | 1980 / $59.41 | 1 / 0 |
| soccer | KXLIGAMXBTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXIDNSLBTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXEPL1HBTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXALLSVENSKANBTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXAUTBUNDESBTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXLIGUE1GAME | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXLALIGATOTAL | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXLIGAPORTUGALBTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |

'Already priced' = the book was at 99c+ when we first looked (bots were faster than our score feed). 'Median s mispriced' runs from our decision to the fix. 'Settled right / wrong' checks our certainty against Kalshi's result — any 'wrong' means the score feed or the model failed.

## Decided-state engine (contracts the live score already settled, still trading)

2177 contracts decided while active; 193 had a price leaving > 0.4c after fees; 43 of those were mispriced AFTER the score was stable (lock tier)

| sport | game | contract | decided | reason | max margin | mispriced for | lock margin | lock depth |
|---|---|---|---|---|---|---|---|---|
| soccer | FC Dallas vs. Colorado Rapids SC | KXMLSBTTS-26NOV07DALCOL-BTTS | YES | both scored 1-1 | 0.634 | 2126s | 0.354 | 2557 |
| basketball | North Dakota State vs. San Franc | KXNCAAFTOTAL-26NOV07NIUSJSU-49 | YES | score 61-70 total 131 > 48.5 | 0.373 | 274s | 0.373 | 609 |
| basketball | Minot State (W) vs. North Dakota | KXNCAAMBSPREAD-26NOV08NDSUCSB-CSB2 | NO | ended 68-84 margin -16 vs 1.5 | 0.373 | 276s | 0.373 | 2173 |
| basketball | Cal Poly vs. Arizona | KXNCAAFTOTAL-26NOV07NAUCP-59 | YES | score 48-67 total 115 > 58.5 | 0.354 | 1791s | 0.354 | 300 |
| basketball | Northern Arizona (W) vs. Arizona | KXNCAAMBTOTAL-26NOV06CSNKSU-163 | NO | ended total 131 <= 162.5 | 0.344 | 526s | 0.344 | 1210 |
| basketball | Northern Arizona (W) vs. Arizona | KXNCAAMBTOTAL-26NOV06CSNKSU-156 | NO | ended total 131 <= 155.5 | 0.315 | 526s | 0.315 | 5 |
| tennis | Anastasia Zakharova vs. Lucrezia | KXWTASETWINNER-26NOV06ZAKSTE-2-STE | NO | set 2 final 5-2 | 0.315 | 210s | 0.315 | 289 |
| tennis | Anastasia Zakharova vs. Lucrezia | KXWTASETWINNER-26NOV06ZAKSTE-2-ZAK | YES | set 2 final 5-2 | 0.305 | 210s | 0.305 | 178 |
| basketball | North Dakota State vs. San Franc | KXNCAAFTOTAL-26NOV07NIUSJSU-46 | YES | score 61-70 total 131 > 45.5 | 0.305 | 274s | 0.305 | 1655 |
| soccer | Uthai Thani FC vs. Chiangrai Uni | KXTHAIL1TOTAL-26NOV07UTHCHI-4 | YES | score 2-2 total 4 > 3.5 | 0.305 | 362s | 0.305 | 1350 |
| basketball | Cal Poly vs. Arizona | KXNCAAFTOTAL-26NOV07NAUCP-55 | YES | score 48-67 total 115 > 54.5 | 0.246 | 1791s | 0.246 | 200 |
| basketball | North Dakota State vs. San Franc | KXNCAAFTOTAL-26NOV07NIUSJSU-43 | YES | score 61-70 total 131 > 42.5 | 0.246 | 274s | 0.246 | 404 |
| basketball | Minot State (W) vs. North Dakota | KXNCAAMBSPREAD-26NOV08NDSUCSB-CSB6 | NO | ended 68-84 margin -16 vs 5.5 | 0.227 | 276s | 0.227 | 2000 |
| football | Northern Illinois vs. San Jose S | KXNCAAFGAME-26NOV07NIUSJSU-SJSU | YES | ended 19-30 | 0.198 | 74s | 0.198 | 3984 |
| soccer | SC Cambuur-Leeuwarden vs. PSV | KXEREDIVISIETOTAL-26NOV08CAMPSV-7 | YES | score 2-5 total 7 > 6.5 | 0.179 | 531s | 0.179 | 58 |
| basketball | North Dakota State vs. San Franc | KXNCAAFTOTAL-26NOV07NIUSJSU-40 | YES | score 61-70 total 131 > 39.5 | 0.170 | 274s | 0.170 | 14 |
| football | South Dakota State vs. Northern  | KXNCAAFGAME-26NOV07SDSTUNI-UNI | NO | ended 41-15 | 0.151 | 89s | 0.151 | 513 |
| football | South Dakota State vs. Northern  | KXNCAAFGAME-26NOV07SDSTUNI-SDST | YES | ended 41-15 | 0.151 | 89s | 0.151 | 358 |
| basketball | Minot State (W) vs. North Dakota | KXNCAAMBSPREAD-26NOV08NDSUCSB-CSB11 | NO | ended 68-84 margin -16 vs 10.5 | 0.122 | 276s | 0.122 | 1000 |
| basketball | North Dakota State vs. San Franc | KXNCAAFTOTAL-26NOV07NIUSJSU-37 | YES | score 61-70 total 131 > 36.5 | 0.113 | 274s | 0.113 | 450 |
| football | Temple vs. Navy | KXNCAAFGAME-26NOV07TEMNAVY-TEM | NO | ended 35-42 | 0.957 | 616s | - | 0 |
| football | Temple vs. Navy | KXNCAAFGAME-26NOV07TEMNAVY-NAVY | YES | ended 35-42 | 0.957 | 616s | - | 0 |
| football | Western Kentucky vs. Middle Tenn | KXNCAAFGAME-26NOV07WKUMTU-WKU | NO | ended 42-45 | 0.957 | 2509s | - | 0 |
| soccer | Hertha BSC vs. VFL Wolfsburg | KXBUNDESLIGA2TOTAL-26NOV07BSCWOB-4 | NO | ended total 3 <= 3.5 | 0.947 | 0s | - | 0 |
| soccer | Cuiaba EC vs. EC Juventude | KXBRASILEIROBTOTAL-26NOV07CUIJUV-4 | YES | score 1-3 total 4 > 3.5 | 0.915 | 388s | - | 0 |

## Close / settlement latency (how clunky each venue is after the final whistle)

Kalshi: settlement_ts − close_time per series (negative = settled before the scheduled close)

| series | n | median | p90 |
|---|---|---|---|
| KXNFLPASSYDSPRECISE Pass Yards Precise | 11406 | 4.1 min | 4.1 min |
| KXESOCCERGAME eSoccer Game | 3938 | 4.0 min | 4.1 min |
| KXNCAAFSPREAD College Football Spread | 2484 | 4.0 min | 4.1 min |
| KXNCAAMBTOTAL Men's College Basketball Total | 2264 | 4.0 min | 4.1 min |
| KXNCAAFTOTAL College Football Total Points | 1787 | 4.0 min | 4.1 min |
| KXNCAAMBSPREAD Men's College Basketball Sprea | 1768 | 1.8 min | 1.8 min |
| KXNHLGOAL NHL Goalscorer | 1523 | 3.0 min | 3.1 min |
| KXNCAAWBTOTAL Women's College Basketball Tot | 1505 | 2.5 min | 2.6 min |
| KXNCAAFTEAMTOTAL College Football Team Total Po | 1389 | 4.0 min | 4.1 min |
| KXNBA3PT NBA Player Threes | 1374 | 2.0 min | 2.1 min |
| KXNBA3PTPROT NBA Player Threes Protected | 1244 | 2.6 min | 2.6 min |
| KXNBAREBPROT NBA Player Rebounds Protected | 1234 | 2.6 min | 2.6 min |
| KXNBAREB NBA Player Rebounds | 1218 | 2.0 min | 2.1 min |
| KXNFLRECYDS Pro Football Receiving Yards | 1176 | 2.0 min | 2.1 min |
| KXNCAAF1HSPREAD College Football 1st Half Spre | 1142 | 4.0 min | 4.1 min |
| KXNBAPTS NBA Player Points | 1117 | 2.0 min | 2.1 min |
| KXNFLRECYDSPROT Receiving Yards Protected | 1104 | 6.0 min | 6.1 min |
| KXNHLPTS Pro Hockey Points | 1090 | 3.0 min | 3.1 min |
| KXNFLTOTALPRECISE Total Precise | 1065 | 4.0 min | 4.1 min |
| KXNBAPTSPROT NBA Player Points Protected | 1038 | 2.6 min | 2.6 min |
| KXNFLREC Pro Football Player Receptions | 1017 | 2.0 min | 2.1 min |
| KXNBAAST NBA Player Assists | 986 | 2.0 min | 2.1 min |
| KXLIGAPROMATCH Russia Liga Pro Match | 922 | 4.0 min | 4.1 min |
| KXNBAASTPROT NBA Player Assists Protected | 901 | 2.6 min | 2.6 min |
| KXNHLFIRSTGOAL NHL First Goal | 889 | 6.0 min | 6.0 min |
| KXNBATEAMTOTAL NBA Team Total | 885 | 2.5 min | 2.6 min |
| KXNHLAST Pro Hockey Assists | 872 | 6.0 min | 6.1 min |
| KXNFLRECPROT Receptions Protected | 872 | 6.0 min | 6.1 min |
| KXNBAPRA NBA Player Points + Rebounds + | 846 | 2.5 min | 2.6 min |
| KXNBAPRAPROT Pts + Reb + Ast Protected | 806 | 2.6 min | 2.6 min |
| KXNCAAF1HTOTAL College Football 1st Half Tota | 783 | 4.0 min | 4.1 min |
| KXNCAAF2HSPREAD College Football 2nd Half Spre | 717 | 4.0 min | 4.1 min |
| KXNBASPREAD NBA Spread | 712 | 1.8 min | 1.8 min |
| KXNCAAWBSPREAD Women's College Basketball Spr | 681 | 1.8 min | 1.8 min |
| KXNFLRSHYDS Pro Football Rushing Yards | 660 | 2.0 min | 2.1 min |
| KXNBATOTAL NBA Total | 631 | 1.8 min | 1.8 min |
| KXMLSGOAL Goalscorer | 579 | 6.0 min | 6.1 min |
| KXNFLRSHYDSPROT Rushing Yards Protected | 519 | 6.0 min | 6.1 min |
| KXNFLTD Pro Football Touchdowns | 499 | 2.1 min | 2.1 min |
| KXEBASKETBALLGAME eBasketball Game | 498 | 4.0 min | 4.1 min |

## Participant fingerprint (per sport; 60 s snapshots)

change% = share of scan cycles (60 s) where the best quote moved; react = median minutes from a score change to the next quote move (humans: slow, bursty, round sizes; bots: constant cadence, odd/constant sizes, instant reaction)

| venue | sport | markets | snapshots | two-sided | med spread | change% | react (min) | round sizes | med size |
|---|---|---|---|---|---|---|---|---|---|
| pm | soccer | 1611 | 275817 | 84% | 0.020 | 17% | 0.7 (n=4003) | - | - |
| pm | tennis | 1487 | 113453 | 93% | 0.010 | 24% | 0.6 (n=61575) | - | - |
| pm | esports | 3511 | 88354 | 81% | 0.020 | 18% | 0.5 (n=18362) | - | - |
| pm | basketball | 787 | 70780 | 75% | 0.030 | 20% | 0.6 (n=15593) | - | - |
| pm | table-tennis | 1568 | 49503 | 94% | 0.010 | 27% | 0.5 (n=27880) | - | - |
| pm | football | 133 | 22919 | 91% | 0.005 | 20% | 1.4 (n=1137) | - | - |
| pm | climate | 216 | 12000 | 65% | 0.070 | 30% | - (n=0) | - | - |
| pm | motorsports | 166 | 9270 | 44% | 0.050 | 16% | - (n=0) | - | - |
| pm | ice-hockey | 68 | 6800 | 82% | 0.060 | 14% | 0.7 (n=329) | - | - |
| pm | cricket | 15 | 6045 | 86% | 0.050 | 9% | 0.7 (n=1076) | - | - |
| pm | beach-volleyball | 66 | 2869 | 92% | 0.010 | 22% | 0.6 (n=1481) | - | - |
| pm | macro | 147 | 2126 | 48% | 0.020 | 17% | - (n=0) | - | - |
| pm | mma | 16 | 1498 | 49% | 0.040 | 3% | - (n=0) | - | - |
| pm | boxing | 38 | 1090 | 84% | 0.060 | 28% | 7.2 (n=4) | - | - |
| pm | pickleball | 35 | 530 | 80% | 0.180 | 22% | - (n=0) | - | - |
| pm | baseball | 3 | 497 | 90% | 0.050 | 20% | 0.6 (n=25) | - | - |
| pm | darts | 15 | 60 | 100% | 0.150 | 13% | - (n=0) | - | - |
| k | KXNCAAFGAME College Football Game | 750 | 910198 | 99% | 0.160 | 5% | - | 6% | 14 |
| k | KXNBA3PT NBA Player Threes | 1514 | 181618 | 79% | 0.060 | 19% | - | 28% | 29 |
| k | KXNFLPASSYDSPRECISE Pass Yards Precise | 17458 | 165580 | 0% | 0.390 | 12% | - | 42% | 1 |
| k | KXNFLGAME NFL Game | 58 | 142787 | 99% | 0.010 | 2% | - | 3% | 166358 |
| k | KXCS2MAP Counter-Strike 2 Map Win | 498 | 119165 | 96% | 0.470 | 6% | - | 25% | 82 |
| k | KXNBAAST NBA Player Assists | 1148 | 111498 | 81% | 0.080 | 19% | - | 27% | 26 |
| k | KXNBAREB NBA Player Rebounds | 1546 | 101959 | 80% | 0.070 | 21% | - | 27% | 35 |
| k | KXNBAPTS NBA Player Points | 1336 | 88741 | 77% | 0.050 | 24% | - | 26% | 41 |
| k | KXNCAAFSPREAD College Football Spread | 3128 | 86209 | 63% | 0.030 | 2% | - | 20% | 475 |
| k | KXNCAAFTEAMTOTAL College Football Team To | 1463 | 83372 | 81% | 0.020 | 3% | - | 38% | 271 |
| k | KXDOTA2MAP Dota 2 Map Winner | 356 | 83073 | 96% | 0.420 | 5% | - | 16% | 22 |
| k | KXNBAPRA NBA Player Points + Rebo | 977 | 73400 | 83% | 0.160 | 20% | - | 14% | 6 |
| k | KXNBA3PTPROT NBA Player Threes Protec | 1480 | 70894 | 53% | 0.130 | 4% | - | 15% | 25 |
| k | KXNCAAF1HSPREAD College Football 1st Hal | 1227 | 58263 | 78% | 0.030 | 9% | - | 31% | 260 |
| k | KXESOCCERGAME eSoccer Game | 4041 | 57893 | 24% | 0.870 | 5% | - | 23% | 37 |
| k | KXNCAAFTOTAL College Football Total P | 2226 | 49586 | 61% | 0.040 | 2% | - | 28% | 350 |
| k | KXNBA1HTEAMTOTAL NBA 1st Half Team Total | 550 | 44731 | 72% | 0.280 | 16% | - | 30% | 100 |
| k | KXNCAAMBTOTAL Men's College Basketball | 3158 | 43002 | 37% | 0.060 | 12% | - | 27% | 102 |
| k | KXNCAAF1H College Football 1st Hal | 1122 | 41711 | 87% | 0.950 | 2% | - | 65% | 500 |
| k | KXNBAASTPROT NBA Player Assists Prote | 1095 | 41294 | 54% | 0.140 | 4% | - | 13% | 17 |
| k | KXNBAREBPROT NBA Player Rebounds Prot | 1471 | 40029 | 54% | 0.140 | 4% | - | 15% | 25 |
| k | KXNCAAMBSPREAD Men's College Basketball | 2500 | 34955 | 40% | 0.060 | 11% | - | 30% | 152 |
| k | KXNBA1HSPREAD NBA 1st Half Spread | 475 | 34253 | 70% | 0.040 | 11% | - | 16% | 151 |
| k | KXNBA1HTOTAL NBA 1st Half Total | 475 | 34052 | 70% | 0.040 | 11% | - | 29% | 100 |
| k | KXNCAAWBTOTAL Women's College Basketba | 1823 | 31460 | 23% | 0.580 | 5% | - | 27% | 13 |
| k | KXNBAPTSPROT NBA Player Points Protec | 1232 | 31095 | 49% | 0.310 | 4% | - | 11% | 5 |
| k | KXNCAAF1HTOTAL College Football 1st Hal | 815 | 30704 | 68% | 0.030 | 9% | - | 40% | 300 |
| k | KXLIGAMXSCORE Correct Score | 270 | 29880 | 55% | 0.020 | 4% | - | 17% | 950 |
| k | KXNBA2HSPREAD NBA 2nd Half Spread | 475 | 25255 | 62% | 0.110 | 17% | - | 38% | 50 |
| k | KXNBAPRAPROT Pts + Reb + Ast Protecte | 977 | 25136 | 22% | 0.680 | 2% | - | 22% | 15 |
| k | KXNBA2HTOTAL NBA 2nd Half Total | 475 | 24911 | 68% | 0.150 | 17% | - | 42% | 84 |
| k | KXMLSSCORE Correct Score | 450 | 23344 | 42% | 0.020 | 11% | - | 19% | 2000 |
| k | KXNBA2QSPREAD NBA 2nd Quarter Spread | 325 | 21930 | 70% | 0.040 | 13% | - | 24% | 111 |
| k | KXNCAAF2HSPREAD College Football 2nd Hal | 717 | 21670 | 58% | 0.120 | 12% | - | 35% | 60 |
| k | KXNBA2QTOTAL NBA 2nd Quarter Total | 325 | 21144 | 70% | 0.050 | 13% | - | 33% | 75 |
| k | KXNFLRECYDS Pro Football Receiving Y | 1777 | 20705 | 0% | - | 0% | - | 0% | - |
| k | KXNFLTOTALPRECISE Total Precise | 1976 | 20064 | 0% | - | 0% | - | 0% | - |
| k | KXNFLRECYDSPROT Receiving Yards Protecte | 1656 | 19380 | 0% | - | 0% | - | 0% | - |
| k | KXNHLGOAL NHL Goalscorer | 2006 | 19024 | 0% | - | 0% | - | 0% | - |
| k | KXNCAAWBGAME Women's College Basketba | 606 | 18446 | 76% | 0.260 | 8% | - | 20% | 10 |

## Schema notes (raw keys seen)

- polymarket: active, archived, category, chatChannel, closed, combos, createdAt, description, elapsed, endDate, ended, eventState, fixtureId, gameId, hidden, id, insiderTradingRules, live, marketCounts, marketGroups, markets, metadata, participants, payoutEstimateMessage, payoutEstimateTime, period, primaryTag, score, seriesSlug, slug, sortType, sportradarGameId, startDate, startTime, streamProvider, streamRequiresAuth, tags, teams, ticker, title, updatedAt
- kalshi: can_close_early, close_time, created_time, custom_strike, early_close_condition, event_ticker, exchange_index, expected_expiration_time, expiration_time, expiration_value, last_price_dollars, latest_expiration_time, market_type, no_ask_dollars, no_bid_dollars, no_sub_title, notional_value_dollars, occurrence_datetime, open_interest_fp, open_time, previous_price_dollars, previous_yes_ask_dollars, previous_yes_bid_dollars, price_level_structure, price_ranges, result, rules_primary, rules_secondary, settlement_bounds_type, settlement_timer_seconds, status, strike_type, subtitle, ticker, title, updated_time, volume_24h_fp, volume_fp, yes_ask_dollars, yes_ask_size_fp, yes_bid_dollars, yes_bid_size_fp, yes_sub_title

