# Mr. P — sports radar

Updated 2026-11-10T03:05:02Z by `run-20261109T2241-42714120638` (last 7 days). Read-only scanner of every sports market on Polymarket US and Kalshi — it never places orders.
Kit: `mrp/mrp_sports_radar.py` on the `mrp` branch. Raw tape: `mrp/radar/<run>/`.

# Sports radar report

records 4,667,522 | 2026-11-07 03:01Z → 03:01Z | runs 14 | pairs matched 1606 | errors {'radar': 4, 'sp.stream': 8}

## Catalogue (latest inventory, 01:50Z)

Polymarket US sports events 4623 of 5612 active events; Kalshi near-term sports markets 6609 in 696 events; calls so far {'pm': 2268, 'k': 10223}; MB {'pm': 3438200753, 'k': 5684777149}

| venue | sport / league / type | markets | two-sided | med spread | vol 24h |
|---|---|---|---|---|---|
| pm | football / nfl / futures | 3773 | 59% | 0.010 | 0 |
| pm | football / cfb / futures | 1550 | 37% | 0.010 | 0 |
| pm | basketball / nba / futures | 1447 | 52% | 0.040 | 0 |
| pm | ice-hockey / nhl / futures | 779 | 92% | 0.010 | 0 |
| pm | basketball / cbb / basketball_team_full_game_winner | 772 | 17% | 0.030 | 0 |
| pm | basketball / wcbb / basketball_team_full_game_winner | 743 | 14% | 0.070 | 0 |
| k | KXNCAAFGAME / College Football Game | 516 | 100% | 0.080 | 411425 |
| pm | golf / austcham / futures | 499 | 1% | 0.047 | 0 |
| pm | soccer / epl / futures | 437 | 86% | 0.010 | 0 |
| k | KXNBAREB / NBA Player Rebounds | 435 | 100% | 0.040 | 444998 |
| k | KXNBA3PT / NBA Player Threes | 426 | 100% | 0.030 | 470897 |
| k | KXNBAREBPROT / NBA Player Rebounds Protected | 425 | 100% | 0.910 | 5667 |
| k | KXNBA3PTPROT / NBA Player Threes Protected | 418 | 100% | 0.890 | 29504 |
| pm | basketball / cbb / futures | 396 | 88% | 0.010 | 0 |
| k | KXNBAPTS / NBA Player Points | 375 | 100% | 0.030 | 1081526 |
| k | KXNBAPTSPROT / NBA Player Points Protected | 353 | 100% | 0.890 | 54172 |
| k | KXNBAAST / NBA Player Assists | 290 | 100% | 0.040 | 349857 |
| pm | soccer / ucl / futures | 285 | 79% | 0.010 | 0 |
| k | KXNBAASTPROT / NBA Player Assists Protected | 282 | 100% | 0.900 | 15213 |
| pm | table-tennis / setkameua / table_tennis_match_winner | 263 | 87% | 0.250 | 0 |
| pm | tennis / utr / tennis_match_winner | 262 | 14% | 0.410 | 0 |
| k | KXNBAPRA / NBA Player Points + Rebounds + Assists | 259 | 100% | 0.060 | 124520 |
| k | KXNBAPRAPROT / Pts + Reb + Ast Protected | 257 | 100% | 1.000 | 306 |
| k | KXNFLFFWEEKLEAD / Weekly Fantasy Football Leader | 252 | 100% | 0.050 | 1332 |
| pm | football / cfb / football_team_full_game_winner | 247 | 83% | 0.090 | 0 |
| pm | tennis / itfme / tennis_match_winner | 242 | 55% | 0.040 | 0 |
| pm | golf / dpworlch / futures | 200 | 2% | 0.089 | 0 |
| pm | tennis / itfwo / tennis_match_winner | 182 | 68% | 0.020 | 0 |
| k | KXNCAAMB1H / Men's College Basketball 1st Half Winner | 168 | 100% | 0.030 | 4339 |
| k | KXNFLFFWEEKTOP / Weekly Fantasy Football Top Players | 167 | 100% | 0.150 | 2119 |
| k | KXNBASTL / NBA Player Steals | 156 | 100% | 0.080 | 67271 |
| pm | mma / ufc / futures | 148 | 81% | 0.010 | 0 |
| pm | soccer / lal / futures | 147 | 48% | 0.010 | 0 |
| pm | boxing / boxing / futures | 145 | 0% | - | 0 |
| pm | soccer / unl / soccer_team_full_time_winner | 132 | 86% | 0.020 | 0 |
| pm | macro /  / futures | 122 | 69% | 0.010 | 0 |
| pm | basketball / nba / basketball_team_full_game_winner | 112 | 84% | 0.235 | 0 |
| k | KXNBA1HTEAMTOTAL / NBA 1st Half Team Total | 110 | 100% | 0.095 | 7327 |
| pm | golf / lpga / futures | 108 | 0% | - | 0 |
| pm | tennis / atp / tennis_match_winner | 100 | 92% | 0.010 | 0 |
| k | KXNBARACE / NBA Race to Points | 96 | 100% | 0.905 | 1429 |
| k | KXNBA1HSPREAD / NBA 1st Half Spread | 95 | 100% | 0.010 | 181882 |
| k | KXNBA1HTOTAL / NBA 1st Half Total | 95 | 100% | 0.010 | 148180 |
| pm | soccer / afcq / soccer_team_full_time_winner | 90 | 87% | 0.040 | 0 |
| pm | soccer / sea / futures | 88 | 85% | 0.010 | 0 |
| pm | macro / usgas / futures | 86 | 64% | 0.010 | 0 |
| k | KXNBA2D / NBA Player Double Double | 86 | 100% | 0.155 | 86444 |
| pm | tennis / atp / futures | 83 | 35% | 0.010 | 0 |
| pm | soccer / bun / futures | 80 | 84% | 0.010 | 0 |
| pm | soccer / lg1 / futures | 79 | 86% | 0.010 | 0 |
| pm | tennis / wta / futures | 75 | 44% | 0.020 | 0 |
| pm | baseball / mlb / futures | 72 | 60% | 0.001 | 0 |
| pm | esports / cs2 / esports_match_winner | 71 | 65% | 0.155 | 0 |
| k | KXNBA2QSPREAD / NBA 2nd Quarter Spread | 65 | 100% | 0.020 | 16725 |
| k | KXNBA2QTOTAL / NBA 2nd Quarter Total | 65 | 100% | 0.020 | 15472 |
| pm | macro / usdsl / futures | 63 | 2% | 0.190 | 0 |
| pm | table-tennis / czechligapro / table_tennis_match_winner | 63 | 17% | 0.460 | 0 |
| pm | tennis / atpdb / tennis_match_winner | 58 | 41% | 0.380 | 0 |
| k | KXNBA1H / NBA 1st Half Winner | 57 | 100% | 0.050 | 206632 |
| k | KXNBA2Q / NBA 2nd Quarter Winner | 54 | 100% | 0.960 | 15434 |

## Opportunities

| kind | distinct | hits | max margin $/contract | max persistence | fresh-BBO still open |
|---|---|---|---|---|---|
| decided_k | 172 | 1552 | 0.9893 | 35 min | 0/0 |
| decided_pm | 18 | 351 | 0.9891 | 11 min | 220/351 |
| decided_pm_closed | 10 | 156 | 0.9891 | 18 min | 0/156 |
| dutch_k | 6 | 105 | 0.0203 | 14 min | 0/0 |
| dutch_pm | 59 | 3093 | 0.3987 | 50 min | 0/0 |
| implication_k | 30 | 430 | 0.7784 | 33 min | 0/0 |
| lag_k_settled | 201 | 30489 | 0.9945 | 321 min | 24188/28269 |
| lag_k_settled_closed | 166 | 2786 | 0.9973 | 202 min | 0/2786 |

Top by persistence × hits:

- **lag_k_settled** basketball — KTP Basket Kotka vs. Lahti Basketball — bid 0.99 ask - sell_yes @ 0.99 | margin 0.9891 | 321 min, 1291 hits | fresh bbo 0.99/- depth 7/0 | score 100-81 VFT
- **lag_k_settled** esports — DarkZero Esports vs. Sharper Esport — bid 0.78 ask 0.83 sell_yes @ 0.78 | margin 0.7848 | 227 min, 1244 hits | fresh bbo 0.78/0.83 depth 10/9 | score 0-0 Map 1
- **lag_k_settled** basketball — Baskets Bonn vs. Basketball Lowen Braunschweig — bid 0.99 ask - sell_yes @ 0.99 | margin 0.9891 | 203 min, 915 hits | score 97-87 FT
- **lag_k_settled** basketball — Western Carolina vs. UNC Asheville — bid 0.99 ask - sell_yes @ 0.99 | margin 0.9891 | 262 min, 570 hits | fresh bbo 0.99/- depth 14/0 | score 83-75 FT
- **lag_k_settled** football — Michigan State vs. Michigan — bid 0.78 ask 0.78 sell_yes @ 0.775 | margin 0.7848 | 180 min, 616 hits | fresh bbo 0.78/0.78 depth 65/34 | score 9-0 End Q3
- **lag_k_settled** football — Iowa vs. Northwestern — bid 0.91 ask 0.91 sell_yes @ 0.905 | margin 0.8968 | 149 min, 641 hits | fresh bbo 0.91/0.91 depth 76/18 | score 14-0 HT
- **lag_k_settled** football — Western Illinois vs. Eastern Illinois — bid 0.63 ask - sell_yes @ 0.63 | margin 0.9945 | 96 min, 694 hits | fresh bbo 0.63/- depth 11/0 | score 44-23 FT
- **lag_k_settled** football — Alabama State vs. Texas Southern — bid 0.99 ask - sell_yes @ 0.995 | margin 0.9945 | 123 min, 486 hits | fresh bbo 0.99/- depth 11/0 | score 34-31 FT
- **lag_k_settled** soccer — Manchester United FC vs. Aston Villa FC — bid 0.48 ask 0.49 buy_yes @ 0.49 | margin 0.5265 | 121 min, 479 hits | fresh bbo 0.48/0.49 depth 36/40 | score 0-0 
- **lag_k_settled** soccer — Manchester United FC vs. Aston Villa FC — bid 0.24 ask 0.25 sell_yes @ 0.24 | margin 0.2322 | 121 min, 479 hits | fresh bbo 0.24/0.25 depth 18/41 | score 0-0 
- **lag_k_settled** soccer — Manchester United FC vs. Aston Villa FC — bid 0.28 ask 0.29 sell_yes @ 0.28 | margin 0.2801 | 121 min, 479 hits | fresh bbo 0.28/0.29 depth 25/49 | score 0-0 
- **lag_k_settled** basketball — Maxima Roma vs. Pallacanestro Cantu — bid 0.81 ask 0.85 sell_yes @ 0.81 | margin 0.8700 | 116 min, 460 hits | fresh bbo 0.81/0.85 depth 19/9 | score 6-7 Q1
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
- **lag_k_settled** football — Temple vs. Navy — bid 0.01 ask 0.01 sell_yes @ 0.01 | margin 0.0592 | 118 min, 285 hits | fresh bbo -/0.01 depth 0/48 | score 14-35 Q3
- **lag_k_settled** basketball — NO Pelicans vs. LA Clippers — bid 0.52 ask 0.53 sell_yes @ 0.52 | margin 0.4963 | 81 min, 319 hits | fresh bbo 0.52/0.53 depth 28/27 | score - NS
- **lag_k_settled** football — Kentucky vs. Tennessee — bid 0.01 ask 0.01 sell_yes @ 0.005 | margin 0.3381 | 102 min, 294 hits | fresh bbo -/0.01 depth 0/92 | score 6-27 Q4

## Live paper trades (no orders; Kalshi prices, taker fees)

Ledger L2-2026-11-01 (earlier ledgers excluded: none)

**Total closed P&L: $-439.95 on $1742.95 staked (-25.2%)**

| rule | entries | closed | winners | staked | P&L | ROI |
|---|---|---|---|---|---|---|
| R1 anchor [ncaaf] | 54 | 54 | 28 | $544.38 | $-22.38 | -4% |
| R1 anchor [nfl] | 6 | 6 | 1 | $60.54 | $-45.54 | -75% |
| R2 q1cheap [ncaaf] | 42 | 42 | 6 | $219.99 | $-58.99 | -27% |
| R2 q1cheap [nfl] | 9 | 9 | 0 | $47.28 | $-47.28 | -100% |
| R3 blowout [ncaaf] | 23 | 23 | 1 | $487.42 | $-306.42 | -63% |
| R3 blowout [nfl] | 1 | 1 | 0 | $21.08 | $-21.08 | -100% |
| R4 halftime [ncaaf] | 27 | 27 | 16 | $133.42 | $+12.58 | +9% |
| R6 decided [other] | 13 | 13 | 13 | $228.85 | $+49.15 | +21% |

| time (UTC) | rule | game | team | entry | contracts | why | result |
|---|---|---|---|---|---|---|---|
| 01:16 | R6 decided | Fayetteville State (W) vs. N | Coastal Carolina | 0.87 | 22 | ended 56-60 | kalshi settled: 1.00, $+2.69 |
| 01:16 | R6 decided | Fayetteville State (W) vs. N | Coastal Carolina wins by over 3.5 points | 0.76 | 26 | ended 56-60 margin 4 vs 3.5 | kalshi settled: 1.00, $+5.91 |
| 01:16 | R6 decided | Fayetteville State (W) vs. N | Over 112.5 points | 0.98 | 1 | score 56-60 total 116 > 112.5 | kalshi settled: 1.00, $+0.02 |
| 01:31 | R2 q1cheap | TB Buccaneers vs. CHI Bears | Tampa Bay | 0.19 | 26 | Q1 ask 0.19, score 0-0 | final score (pending Kalshi settlement): 0.00, $-5.22 |
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

### Score reaction speed (live, 15 s): share of the 3-minute move done by +15 s / +30 s / +60 s

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
- 26NOV08TBCHI 13-24: 33% / 33% / 33%
- 26NOV08TBCHI 22-24: 25% / 25% / 25%
- 26NOV08TBCHI 22-24: 20% / 20% / 20%
- 26NOV08TBCHI 24-24: 0% / 0% / 0%
- 26NOV08TBCHI 24-24: -0% / -0% / -0%

## Bot latency map: how long a decided Kalshi market stays mispriced

| sport | series | markets | already priced | mispriced then fixed | median s mispriced | closed/timeout | contradictions | cheapest ask (size) | resting @0.97 contracts / $ | settled right / wrong |
|---|---|---|---|---|---|---|---|---|---|---|
| football | KXNCAAFGAME | 161 | 158 | 0 | - | 0 | 3 | - | 0 / $0.00 | 155 / 0 |
| basketball | KXNCAAWBTOTAL | 105 | 105 | 0 | - | 0 | 0 | - | 0 / $0.00 | 83 / 0 |
| soccer | KXSERIECTOTAL | 73 | 63 | 10 | 21 | 0 | 0 | 0.85 (48) | 0 / $0.00 | 73 / 0 |
| football | KXNCAAFTOTAL | 68 | 63 | 5 | 2 | 0 | 0 | 0.62 (1974) | 0 / $0.00 | 68 / 0 |
| soccer | KXMLSTOTAL | 60 | 60 | 0 | - | 0 | 0 | - | 0 / $0.00 | 32 / 0 |
| basketball | KXNCAAMBTOTAL | 51 | 41 | 3 | 187 | 7 | 0 | 0.65 (500) | 70 / $2.10 | 51 / 0 |
| tennis | KXATPSETWINNER | 48 | 48 | 0 | - | 0 | 0 | - | 0 / $0.00 | 48 / 0 |
| soccer | KXBUNDESLIGA2TOTAL | 48 | 43 | 4 | 8 | 1 | 0 | 0.01 (14030) | 11015 / $330.45 | 47 / 1 |
| basketball | KXNCAAMBSPREAD | 48 | 38 | 2 | 1123 | 8 | 0 | 0.48 (1000) | 8 / $0.25 | 32 / 3 |
| soccer | KXTHAIL1TOTAL | 45 | 43 | 2 | 21 | 0 | 0 | 0.93 (0) | 0 / $0.00 | 45 / 0 |
| soccer | KXBELGIANPLTOTAL | 45 | 44 | 1 | 7 | 0 | 0 | 0.94 (1009) | 0 / $0.00 | 45 / 0 |
| soccer | KXELITESERIENTOTAL | 42 | 40 | 1 | 26 | 0 | 1 | 0.75 (200) | 11 / $0.34 | 42 / 0 |
| football | KXNCAAFSPREAD | 41 | 41 | 0 | - | 0 | 0 | - | 0 / $0.00 | 41 / 0 |
| soccer | KXCHNSLTOTAL | 41 | 39 | 2 | 1011 | 0 | 0 | 0.47 (3506) | 722 / $21.67 | 41 / 0 |
| soccer | KXLIGAMXTOTAL | 38 | 36 | 1 | 242 | 1 | 0 | 0.60 (7) | 7233 / $216.99 | 38 / 0 |
| soccer | KXIDNSLTOTAL | 36 | 34 | 2 | 158 | 0 | 0 | 0.87 (10) | 0 / $0.00 | 36 / 0 |
| tennis | KXATPCHALLENGERMATCH | 36 | 36 | 0 | - | 0 | 0 | - | 0 / $0.00 | 36 / 0 |
| soccer | KXAUTBUNDESTOTAL | 33 | 31 | 0 | - | 0 | 2 | - | 0 / $0.00 | 33 / 0 |
| soccer | KXEKSTRAKLASATOTAL | 30 | 27 | 3 | 27 | 0 | 0 | 0.60 (58) | 27 / $0.82 | 25 / 0 |
| soccer | KXALLSVENSKANTOTAL | 30 | 30 | 0 | - | 0 | 0 | - | 0 / $0.00 | 30 / 0 |
| soccer | KXHUNNB1TOTAL | 29 | 27 | 2 | 25 | 0 | 0 | 0.95 (7) | 0 / $0.00 | 29 / 0 |
| soccer | KXAPFDDHTOTAL | 28 | 28 | 0 | - | 0 | 0 | - | 0 / $0.00 | 27 / 0 |
| soccer | KXEREDIVISIETOTAL | 26 | 25 | 0 | - | 1 | 0 | 0.65 (20) | 0 / $0.00 | 25 / 1 |
| soccer | KXECULPTOTAL | 26 | 26 | 0 | - | 0 | 0 | - | 0 / $0.00 | 26 / 0 |
| football | KXNFLGAME | 26 | 22 | 3 | 52 | 0 | 1 | 0.66 (0) | 0 / $0.00 | 18 / 0 |
| soccer | KXTFF1LIGTOTAL | 22 | 20 | 2 | 2 | 0 | 0 | 0.83 (9000) | 0 / $0.00 | 22 / 0 |
| soccer | KXMLSSPREAD | 22 | 22 | 0 | - | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
| soccer | KXKLEAGUETOTAL | 21 | 21 | 0 | - | 0 | 0 | - | 0 / $0.00 | 21 / 0 |
| soccer | KXJLEAGUE1HTOTAL | 21 | 18 | 3 | 20 | 0 | 0 | 0.91 (20) | 51 / $1.54 | 21 / 0 |
| soccer | KXJLEAGUE1H | 21 | 21 | 0 | - | 0 | 0 | - | 0 / $0.00 | 21 / 0 |
| soccer | KXDIMAYORTOTAL | 21 | 20 | 1 | 1 | 0 | 0 | 0.72 (0) | 0 / $0.00 | 16 / 0 |
| soccer | KXCZEFLTOTAL | 20 | 20 | 0 | - | 0 | 0 | - | 0 / $0.00 | 20 / 0 |
| soccer | KXJ2LEAGUETOTAL | 18 | 18 | 0 | - | 0 | 0 | - | 0 / $0.00 | 18 / 0 |
| soccer | KXCZEFNLTOTAL | 18 | 18 | 0 | - | 0 | 0 | - | 0 / $0.00 | 18 / 0 |
| soccer | KXBRASILEIROBTOTAL | 17 | 16 | 0 | - | 1 | 0 | 0.01 (61246) | 3818 / $114.53 | 14 / 1 |
| soccer | KXLIGAPORTUGALTOTAL | 17 | 16 | 1 | 4 | 0 | 0 | 0.98 (4594) | 0 / $0.00 | 17 / 0 |
| soccer | KXJ2LEAGUEGAME | 16 | 16 | 0 | - | 0 | 0 | - | 0 / $0.00 | 16 / 0 |
| soccer | KXMLSGAME | 16 | 16 | 0 | - | 0 | 0 | - | 0 / $0.00 | 9 / 0 |
| soccer | KXLIGAEXPTOTAL | 16 | 16 | 0 | - | 0 | 0 | - | 0 / $0.00 | 16 / 0 |
| soccer | KXHNLTOTAL | 15 | 15 | 0 | - | 0 | 0 | - | 0 / $0.00 | 15 / 0 |
| soccer | KXMLS1H | 15 | 15 | 0 | - | 0 | 0 | - | 0 / $0.00 | 15 / 0 |
| soccer | KXCHLLDPTOTAL | 15 | 15 | 0 | - | 0 | 0 | - | 0 / $0.00 | 14 / 0 |
| soccer | KXLIGAFTOTAL | 14 | 11 | 3 | 32 | 0 | 0 | 0.14 (169) | 189 / $5.66 | 14 / 0 |
| soccer | KXDENSUPERLIGATOTAL | 13 | 13 | 0 | - | 0 | 0 | - | 0 / $0.00 | 13 / 0 |
| basketball | KXABASPREAD | 12 | 12 | 0 | - | 0 | 0 | - | 0 / $0.00 | 12 / 0 |
| soccer | KXMLS1HTOTAL | 12 | 12 | 0 | - | 0 | 0 | - | 0 / $0.00 | 12 / 0 |
| soccer | KXJLEAGUETOTAL | 11 | 11 | 0 | - | 0 | 0 | - | 0 / $0.00 | 11 / 0 |
| soccer | KXBUNDESLIGASPREAD | 11 | 11 | 0 | - | 0 | 0 | - | 0 / $0.00 | 11 / 0 |
| basketball | KXABATOTAL | 11 | 11 | 0 | - | 0 | 0 | - | 0 / $0.00 | 11 / 0 |
| soccer | KXARGPREMDIVTOTAL | 11 | 10 | 0 | - | 1 | 0 | 0.82 (977) | 382 / $11.46 | 11 / 0 |
| soccer | KXMLSBTTS | 11 | 10 | 1 | 2 | 0 | 0 | 0.75 (500) | 0 / $0.00 | 10 / 0 |
| soccer | KXJ2LEAGUESPREAD | 10 | 10 | 0 | - | 0 | 0 | - | 0 / $0.00 | 10 / 0 |
| tennis | KXWTASETWINNER | 10 | 10 | 0 | - | 0 | 0 | - | 0 / $0.00 | 10 / 0 |
| soccer | KXBUNDESLIGATOTAL | 10 | 10 | 0 | - | 0 | 0 | - | 0 / $0.00 | 10 / 0 |
| soccer | KXBULFLTOTAL | 10 | 10 | 0 | - | 0 | 0 | - | 0 / $0.00 | 10 / 0 |
| soccer | KXLALIGA2TOTAL | 8 | 6 | 2 | 2 | 0 | 0 | 0.84 (75) | 0 / $0.00 | 8 / 0 |
| esports | KXCS2GAME | 8 | 8 | 0 | - | 0 | 0 | - | 0 / $0.00 | 8 / 0 |
| basketball | KXNCAAMBGAME | 8 | 7 | 0 | - | 1 | 0 | 0.77 (2310) | 4777 / $143.31 | 6 / 0 |
| basketball | KXNCAAWBGAME | 8 | 8 | 0 | - | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| soccer | KXJLEAGUE1HBTTS | 7 | 6 | 1 | 79 | 0 | 0 | 0.95 (1) | 3 / $0.09 | 7 / 0 |
| basketball | KXNCAAFTOTAL | 7 | 0 | 0 | - | 7 | 0 | 0.61 (609) | 0 / $0.00 | 7 / 0 |
| soccer | KXUAEPLTOTAL | 6 | 6 | 0 | - | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| soccer | KXBUNDESLIGA1HTOTAL | 6 | 6 | 0 | - | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| soccer | KXSUPERLIGTOTAL | 6 | 6 | 0 | - | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| soccer | KXKLEAGUE1HTOTAL | 6 | 6 | 0 | - | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| soccer | KXBUNDESLIGAWTOTAL | 6 | 6 | 0 | - | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| soccer | KXSVK1LTOTAL | 5 | 5 | 0 | - | 0 | 0 | - | 0 / $0.00 | 5 / 0 |
| soccer | KXSERIECBTTS | 5 | 5 | 0 | - | 0 | 0 | - | 0 / $0.00 | 5 / 0 |
| soccer | KXCHNSLBTTS | 5 | 4 | 0 | - | 1 | 0 | 0.12 (11) | 361 / $10.82 | 4 / 1 |
| soccer | KXEKSTRAKLASASPREAD | 5 | 5 | 0 | - | 0 | 0 | - | 0 / $0.00 | 0 / 0 |
| basketball | KXKBLGAME | 4 | 4 | 0 | - | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
| tennis | KXATPCHALLENGERDOUBLES | 4 | 4 | 0 | - | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
| esports | KXCS2TOTALMAPS | 4 | 4 | 0 | - | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
| soccer | KXALLSVENSKANSPREAD | 4 | 4 | 0 | - | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
| soccer | KXMLS1HBTTS | 4 | 4 | 0 | - | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
| soccer | KXJLEAGUESPREAD | 4 | 4 | 0 | - | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
| soccer | KXEPLSPREAD | 4 | 4 | 0 | - | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
| basketball | KXJBLEAGUEGAME | 4 | 4 | 0 | - | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
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
| tennis | KXATPEXACTMATCH | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXJLEAGUEGAME | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXJLEAGUEBTTS | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| tennis | KXWTADOUBLES | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXBUNDESLIGA1HBTTS | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| esports | KXCS2SPREAD | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| basketball | KXAUTBSLGAME | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| basketball | KXABAGAME | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| basketball | KXACBTOTAL | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXLIGUE2TOTAL | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXBELGIANPLBTTS | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXBRASILEIROB1H | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| ice-hockey | KXAHLGAME | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXKLEAGUE1HBTTS | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| esports | KXDOTA2GAME | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXBUNDESLIGA2BTTS | 2 | 1 | 1 | 4 | 0 | 0 | 0.90 (24) | 8 / $0.24 | 2 / 0 |
| soccer | KXROML1TOTAL | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXELITESERIENBTTS | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| basketball | KXBBSERIEATOTAL | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXCOPADOBRASILTOTAL | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| basketball | KXNBAGAME | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| tennis | KXATPMATCH | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| basketball | KXNCAAFGAME | 1 | 0 | 0 | - | 1 | 0 | 0.79 (3984) | 0 / $0.00 | 1 / 0 |
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

1923 contracts decided while active; 172 had a price leaving > 0.4c after fees; 38 of those were mispriced AFTER the score was stable (lock tier)

| sport | game | contract | decided | reason | max margin | mispriced for | lock margin | lock depth |
|---|---|---|---|---|---|---|---|---|
| soccer | FC Dallas vs. Colorado Rapids SC | KXMLSBTTS-26NOV07DALCOL-BTTS | YES | both scored 1-1 | 0.634 | 2126s | 0.354 | 2557 |
| basketball | North Dakota State vs. San Franc | KXNCAAFTOTAL-26NOV07NIUSJSU-49 | YES | score 61-70 total 131 > 48.5 | 0.373 | 274s | 0.373 | 609 |
| basketball | Minot State (W) vs. North Dakota | KXNCAAMBSPREAD-26NOV08NDSUCSB-CSB2 | NO | ended 68-84 margin -16 vs 1.5 | 0.373 | 276s | 0.373 | 2173 |
| basketball | Fayetteville State (W) vs. North | KXNCAAMBTOTAL-26NOV09SCUSCCAR-142 | NO | ended total 116 <= 141.5 | 0.334 | 97s | 0.334 | 1968 |
| basketball | North Dakota State vs. San Franc | KXNCAAFTOTAL-26NOV07NIUSJSU-46 | YES | score 61-70 total 131 > 45.5 | 0.305 | 274s | 0.305 | 1655 |
| soccer | Uthai Thani FC vs. Chiangrai Uni | KXTHAIL1TOTAL-26NOV07UTHCHI-4 | YES | score 2-2 total 4 > 3.5 | 0.305 | 362s | 0.305 | 1350 |
| basketball | Fayetteville State (W) vs. North | KXNCAAMBSPREAD-26NOV09SCUSCCAR-CCAR13 | NO | ended 56-60 margin 4 vs 12.5 | 0.276 | 97s | 0.276 | 2276 |
| basketball | North Dakota State vs. San Franc | KXNCAAFTOTAL-26NOV07NIUSJSU-43 | YES | score 61-70 total 131 > 42.5 | 0.246 | 274s | 0.246 | 404 |
| basketball | Fayetteville State (W) vs. North | KXNCAAMBTOTAL-26NOV09SCUSCCAR-145 | NO | ended total 116 <= 144.5 | 0.237 | 97s | 0.237 | 2306 |
| basketball | Minot State (W) vs. North Dakota | KXNCAAMBSPREAD-26NOV08NDSUCSB-CSB6 | NO | ended 68-84 margin -16 vs 5.5 | 0.227 | 276s | 0.227 | 2000 |
| basketball | Fayetteville State (W) vs. North | KXNCAAMBSPREAD-26NOV09SCUSCCAR-CCAR4 | YES | ended 56-60 margin 4 vs 3.5 | 0.227 | 97s | 0.227 | 2334 |
| football | Northern Illinois vs. San Jose S | KXNCAAFGAME-26NOV07NIUSJSU-SJSU | YES | ended 19-30 | 0.198 | 74s | 0.198 | 3984 |
| soccer | SC Cambuur-Leeuwarden vs. PSV | KXEREDIVISIETOTAL-26NOV08CAMPSV-7 | YES | score 2-5 total 7 > 6.5 | 0.179 | 531s | 0.179 | 58 |
| basketball | North Dakota State vs. San Franc | KXNCAAFTOTAL-26NOV07NIUSJSU-40 | YES | score 61-70 total 131 > 39.5 | 0.170 | 274s | 0.170 | 14 |
| basketball | Fayetteville State (W) vs. North | KXNCAAMBTOTAL-26NOV09SCUSCCAR-148 | NO | ended total 116 <= 147.5 | 0.170 | 97s | 0.170 | 1000 |
| basketball | Fayetteville State (W) vs. North | KXNCAAMBSPREAD-26NOV09SCUSCCAR-CCAR16 | NO | ended 56-60 margin 4 vs 15.5 | 0.151 | 97s | 0.151 | 1000 |
| basketball | Fayetteville State (W) vs. North | KXNCAAMBTOTAL-26NOV09SCUSCCAR-150 | NO | ended total 116 <= 149.5 | 0.132 | 97s | 0.132 | 1000 |
| basketball | Minot State (W) vs. North Dakota | KXNCAAMBSPREAD-26NOV08NDSUCSB-CSB11 | NO | ended 68-84 margin -16 vs 10.5 | 0.122 | 276s | 0.122 | 1000 |
| basketball | Fayetteville State (W) vs. North | KXNCAAMBGAME-26NOV09SCUSCCAR-CCAR | YES | ended 56-60 | 0.122 | 97s | 0.122 | 5940 |
| basketball | North Dakota State vs. San Franc | KXNCAAFTOTAL-26NOV07NIUSJSU-37 | YES | score 61-70 total 131 > 36.5 | 0.113 | 274s | 0.113 | 450 |
| basketball | Fayetteville State (W) vs. North | KXNCAAMBTOTAL-26NOV09SCUSCCAR-152 | NO | ended total 116 <= 151.5 | 0.094 | 97s | 0.094 | 571 |
| tennis | James Duckworth vs. Cameron Norr | KXATPEXACTMATCH-26NOV09DUCNOR-NOR21 | YES | ended 5-7, 0-6 | 0.989 | 60s | - | 0 |
| football | Temple vs. Navy | KXNCAAFGAME-26NOV07TEMNAVY-TEM | NO | ended 35-42 | 0.957 | 616s | - | 0 |
| football | Temple vs. Navy | KXNCAAFGAME-26NOV07TEMNAVY-NAVY | YES | ended 35-42 | 0.957 | 616s | - | 0 |
| football | Western Kentucky vs. Middle Tenn | KXNCAAFGAME-26NOV07WKUMTU-WKU | NO | ended 42-45 | 0.957 | 2509s | - | 0 |

## Close / settlement latency (how clunky each venue is after the final whistle)

Kalshi: settlement_ts − close_time per series (negative = settled before the scheduled close)

| series | n | median | p90 |
|---|---|---|---|
| KXNFLPASSYDSPRECISE Pass Yards Precise | 11495 | 4.1 min | 4.1 min |
| KXESOCCERGAME eSoccer Game | 3770 | 4.0 min | 4.1 min |
| KXNCAAFSPREAD College Football Spread | 2411 | 4.0 min | 4.1 min |
| KXNCAAMBTOTAL Men's College Basketball Total | 2079 | 4.0 min | 4.1 min |
| KXNCAAFTOTAL College Football Total Points | 1739 | 4.0 min | 4.1 min |
| KXNCAAMBSPREAD Men's College Basketball Sprea | 1620 | 1.8 min | 1.8 min |
| KXNBA3PT NBA Player Threes | 1429 | 2.0 min | 2.1 min |
| KXNCAAFTEAMTOTAL College Football Team Total Po | 1329 | 4.0 min | 4.1 min |
| KXNCAAWBTOTAL Women's College Basketball Tot | 1324 | 2.5 min | 2.6 min |
| KXNBAREB NBA Player Rebounds | 1246 | 2.0 min | 2.1 min |
| KXNHLGOAL NHL Goalscorer | 1240 | 3.0 min | 3.1 min |
| KXNBAREBPROT NBA Player Rebounds Protected | 1228 | 2.6 min | 2.6 min |
| KXNBA3PTPROT NBA Player Threes Protected | 1193 | 2.6 min | 2.6 min |
| KXNFLRECYDS Pro Football Receiving Yards | 1184 | 2.0 min | 2.1 min |
| KXNBAPTS NBA Player Points | 1176 | 2.0 min | 2.1 min |
| KXNBAPTSPROT NBA Player Points Protected | 1125 | 2.6 min | 2.6 min |
| KXNFLRECYDSPROT Receiving Yards Protected | 1111 | 6.0 min | 6.1 min |
| KXNCAAF1HSPREAD College Football 1st Half Spre | 1079 | 4.0 min | 4.1 min |
| KXNBAAST NBA Player Assists | 999 | 2.0 min | 2.1 min |
| KXNFLREC Pro Football Player Receptions | 979 | 2.0 min | 2.1 min |
| KXNBATEAMTOTAL NBA Team Total | 962 | 2.5 min | 2.6 min |
| KXNFLTOTALPRECISE Total Precise | 944 | 4.0 min | 4.1 min |
| KXNBAASTPROT NBA Player Assists Protected | 905 | 2.6 min | 2.6 min |
| KXLIGAPROMATCH Russia Liga Pro Match | 882 | 4.0 min | 4.1 min |
| KXNFLRECPROT Receptions Protected | 876 | 6.0 min | 6.1 min |
| KXNHLPTS Pro Hockey Points | 858 | 3.0 min | 3.1 min |
| KXNBAPRA NBA Player Points + Rebounds + | 855 | 2.5 min | 2.6 min |
| KXNBAPRAPROT Pts + Reb + Ast Protected | 831 | 2.6 min | 2.6 min |
| KXNBASPREAD NBA Spread | 807 | 1.8 min | 1.8 min |
| KXNCAAF1HTOTAL College Football 1st Half Tota | 743 | 4.0 min | 4.1 min |
| KXNHLFIRSTGOAL NHL First Goal | 743 | 6.0 min | 6.0 min |
| KXNCAAF2HSPREAD College Football 2nd Half Spre | 717 | 4.0 min | 4.1 min |
| KXNBATOTAL NBA Total | 696 | 1.8 min | 1.8 min |
| KXNHLAST Pro Hockey Assists | 695 | 6.0 min | 6.1 min |
| KXNFLRSHYDS Pro Football Rushing Yards | 600 | 2.0 min | 2.1 min |
| KXMLSGOAL Goalscorer | 579 | 6.0 min | 6.1 min |
| KXNFLRSHYDSPROT Rushing Yards Protected | 521 | 6.0 min | 6.1 min |
| KXNCAAWBSPREAD Women's College Basketball Spr | 517 | 1.8 min | 1.8 min |
| KXNBASTL NBA Player Steals | 498 | 2.0 min | 2.1 min |
| KXNCAAF2HTOTAL College Football 2nd Half Tota | 483 | 4.0 min | 4.1 min |

## Participant fingerprint (per sport; 60 s snapshots)

change% = share of scan cycles (60 s) where the best quote moved; react = median minutes from a score change to the next quote move (humans: slow, bursty, round sizes; bots: constant cadence, odd/constant sizes, instant reaction)

| venue | sport | markets | snapshots | two-sided | med spread | change% | react (min) | round sizes | med size |
|---|---|---|---|---|---|---|---|---|---|
| pm | soccer | 1452 | 240093 | 84% | 0.020 | 19% | 0.7 (n=3613) | - | - |
| pm | tennis | 1791 | 112505 | 92% | 0.010 | 23% | 0.6 (n=56908) | - | - |
| pm | esports | 3312 | 84154 | 80% | 0.020 | 18% | 0.6 (n=16880) | - | - |
| pm | basketball | 811 | 64453 | 74% | 0.030 | 20% | 0.6 (n=13889) | - | - |
| pm | table-tennis | 1565 | 47322 | 94% | 0.010 | 28% | 0.5 (n=26510) | - | - |
| pm | football | 130 | 22552 | 91% | 0.005 | 20% | 1.4 (n=1122) | - | - |
| pm | climate | 216 | 11016 | 66% | 0.050 | 30% | - (n=0) | - | - |
| pm | motorsports | 166 | 9270 | 44% | 0.050 | 16% | - (n=0) | - | - |
| pm | cricket | 19 | 5835 | 86% | 0.040 | 8% | 0.7 (n=1157) | - | - |
| pm | ice-hockey | 58 | 5249 | 83% | 0.050 | 14% | 0.7 (n=263) | - | - |
| pm | beach-volleyball | 65 | 2849 | 91% | 0.010 | 20% | 0.6 (n=1320) | - | - |
| pm | macro | 241 | 2221 | 47% | 0.040 | 16% | - (n=0) | - | - |
| pm | boxing | 38 | 1150 | 83% | 0.060 | 26% | 7.2 (n=5) | - | - |
| pm | mma | 18 | 1116 | 34% | 0.010 | 2% | - (n=0) | - | - |
| pm | baseball | 2 | 406 | 89% | 0.050 | 20% | 0.6 (n=23) | - | - |
| pm | darts | 30 | 318 | 99% | 0.080 | 18% | 0.5 (n=30) | - | - |
| pm | pickleball | 15 | 290 | 81% | 0.200 | 25% | - (n=0) | - | - |
| pm | technology | 48 | 146 | 30% | 0.155 | 66% | - (n=0) | - | - |
| k | KXNCAAFGAME College Football Game | 748 | 873585 | 98% | 0.200 | 6% | - | 6% | 14 |
| k | KXNFLPASSYDSPRECISE Pass Yards Precise | 16856 | 170416 | 0% | 0.390 | 12% | - | 42% | 1 |
| k | KXNBA3PT NBA Player Threes | 1816 | 170262 | 78% | 0.060 | 18% | - | 32% | 30 |
| k | KXNFLGAME NFL Game | 56 | 128810 | 99% | 0.010 | 2% | - | 2% | 127021 |
| k | KXCS2MAP Counter-Strike 2 Map Win | 522 | 118988 | 96% | 0.450 | 6% | - | 24% | 102 |
| k | KXNBAAST NBA Player Assists | 1334 | 100732 | 81% | 0.060 | 19% | - | 30% | 30 |
| k | KXNBAPTS NBA Player Points | 1616 | 89794 | 78% | 0.040 | 23% | - | 29% | 44 |
| k | KXDOTA2MAP Dota 2 Map Winner | 372 | 85867 | 96% | 0.410 | 6% | - | 15% | 21 |
| k | KXNBAREB NBA Player Rebounds | 1852 | 80017 | 74% | 0.070 | 21% | - | 29% | 32 |
| k | KXNBA3PTPROT NBA Player Threes Protec | 1774 | 70077 | 46% | 0.130 | 4% | - | 17% | 25 |
| k | KXNBAPRA NBA Player Points + Rebo | 1151 | 64039 | 81% | 0.090 | 23% | - | 21% | 15 |
| k | KXESOCCERGAME eSoccer Game | 3906 | 55166 | 24% | 0.880 | 5% | - | 24% | 37 |
| k | KXNCAAFSPREAD College Football Spread | 3042 | 54771 | 50% | 0.030 | 3% | - | 17% | 335 |
| k | KXNCAAF1HSPREAD College Football 1st Hal | 1163 | 51340 | 76% | 0.030 | 12% | - | 33% | 260 |
| k | KXNCAAFTEAMTOTAL College Football Team To | 1401 | 49791 | 71% | 0.020 | 4% | - | 45% | 259 |
| k | KXNBA1HTEAMTOTAL NBA 1st Half Team Total | 638 | 40555 | 72% | 0.240 | 17% | - | 33% | 132 |
| k | KXNBAASTPROT NBA Player Assists Prote | 1280 | 39058 | 44% | 0.140 | 4% | - | 15% | 25 |
| k | KXNCAAMBTOTAL Men's College Basketball | 3157 | 38178 | 34% | 0.070 | 9% | - | 37% | 100 |
| k | KXNCAAF1H College Football 1st Hal | 1113 | 36750 | 86% | 0.950 | 2% | - | 65% | 500 |
| k | KXNBAPTSPROT NBA Player Points Protec | 1489 | 36433 | 47% | 0.070 | 6% | - | 14% | 50 |
| k | KXNBAREBPROT NBA Player Rebounds Prot | 1776 | 35127 | 40% | 0.140 | 5% | - | 17% | 35 |
| k | KXNCAAFTOTAL College Football Total P | 2167 | 34400 | 46% | 0.050 | 3% | - | 22% | 302 |
| k | KXNBA1HSPREAD NBA 1st Half Spread | 551 | 31684 | 71% | 0.030 | 11% | - | 15% | 200 |
| k | KXNCAAMBSPREAD Men's College Basketball | 2507 | 31208 | 37% | 0.080 | 8% | - | 36% | 122 |
| k | KXNBA1HTOTAL NBA 1st Half Total | 551 | 31078 | 70% | 0.040 | 11% | - | 30% | 113 |
| k | KXLIGAMXSCORE Correct Score | 270 | 30094 | 54% | 0.020 | 4% | - | 17% | 950 |
| k | KXNCAAF1HTOTAL College Football 1st Hal | 770 | 27537 | 66% | 0.030 | 12% | - | 43% | 348 |
| k | KXNBA2HSPREAD NBA 2nd Half Spread | 589 | 26758 | 63% | 0.100 | 18% | - | 39% | 100 |
| k | KXNBA2HTOTAL NBA 2nd Half Total | 589 | 26052 | 69% | 0.130 | 18% | - | 42% | 111 |
| k | KXNFLRECYDS Pro Football Receiving Y | 2037 | 24112 | 17% | 0.040 | 28% | - | 21% | 100 |
| k | KXNBAPRAPROT Pts + Reb + Ast Protecte | 1153 | 24057 | 24% | 0.680 | 3% | - | 38% | 44 |
| k | KXMLSSCORE Correct Score | 450 | 23344 | 42% | 0.020 | 11% | - | 19% | 2000 |
| k | KXNFLRECYDSPROT Receiving Yards Protecte | 1913 | 21784 | 10% | 0.785 | 16% | - | 15% | 9 |
| k | KXNCAAF2HSPREAD College Football 2nd Hal | 717 | 21670 | 58% | 0.120 | 12% | - | 35% | 60 |
| k | KXNCAAWBTOTAL Women's College Basketba | 1824 | 21502 | 19% | 0.470 | 12% | - | 19% | 6 |
| k | KXNBASTL NBA Player Steals | 620 | 21260 | 74% | 0.080 | 17% | - | 27% | 20 |
| k | KXNBA2QSPREAD NBA 2nd Quarter Spread | 377 | 19752 | 68% | 0.030 | 14% | - | 25% | 168 |
| k | KXNFLTOTALPRECISE Total Precise | 1976 | 19608 | 0% | - | 0% | - | 0% | - |
| k | KXATPCHALLENGERMATCH Challenger ATP  | 342 | 19513 | 89% | 0.010 | 7% | - | 3% | 822 |
| k | KXNBA2QTOTAL NBA 2nd Quarter Total | 377 | 18629 | 68% | 0.040 | 13% | - | 37% | 99 |

## Schema notes (raw keys seen)

- polymarket: active, archived, category, chatChannel, closed, combos, createdAt, description, elapsed, endDate, ended, eventState, fixtureId, hidden, id, insiderTradingRules, live, marketCounts, marketGroups, markets, metadata, participants, payoutEstimateMessage, payoutEstimateTime, period, primaryTag, score, seriesSlug, slug, sortType, sportradarGameId, startDate, startTime, streamProvider, streamRequiresAuth, tags, teams, ticker, title, updatedAt
- kalshi: can_close_early, close_time, created_time, custom_strike, early_close_condition, event_ticker, exchange_index, expected_expiration_time, expiration_time, expiration_value, last_price_dollars, latest_expiration_time, market_type, no_ask_dollars, no_bid_dollars, no_sub_title, notional_value_dollars, occurrence_datetime, open_interest_fp, open_time, previous_price_dollars, previous_yes_ask_dollars, previous_yes_bid_dollars, price_level_structure, price_ranges, result, rules_primary, rules_secondary, settlement_bounds_type, settlement_timer_seconds, settlement_ts, settlement_value_dollars, status, strike_type, ticker, title, updated_time, volume_24h_fp, volume_fp, yes_ask_dollars, yes_ask_size_fp, yes_bid_dollars, yes_bid_size_fp, yes_sub_title

