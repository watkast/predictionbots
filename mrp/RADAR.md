# Mr. P — sports radar

Updated 2026-11-11T06:44:30Z by `run-20261111T0229-42934934635` (last 7 days). Read-only scanner of every sports market on Polymarket US and Kalshi — it never places orders.
Kit: `mrp/mrp_sports_radar.py` on the `mrp` branch. Raw tape: `mrp/radar/<run>/`.

# Sports radar report

records 4,241,713 | 2026-11-08 06:41Z → 06:41Z | runs 12 | pairs matched 1323 | errors {'radar': 2, 'sp.stream': 14}

## Catalogue (latest inventory, 05:37Z)

Polymarket US sports events 4613 of 5593 active events; Kalshi near-term sports markets 5316 in 748 events; calls so far {'pm': 1955, 'k': 21589}; MB {'pm': 3528847957, 'k': 8141492682}

| venue | sport / league / type | markets | two-sided | med spread | vol 24h |
|---|---|---|---|---|---|
| pm | football / nfl / futures | 4061 | 57% | 0.010 | 0 |
| pm | football / cfb / futures | 1949 | 33% | 0.010 | 0 |
| pm | basketball / nba / futures | 1442 | 51% | 0.020 | 0 |
| pm | basketball / cbb / basketball_team_full_game_winner | 788 | 12% | 0.030 | 0 |
| pm | ice-hockey / nhl / futures | 779 | 91% | 0.010 | 0 |
| pm | basketball / wcbb / basketball_team_full_game_winner | 772 | 12% | 0.070 | 0 |
| k | KXNCAAFGAME / College Football Game | 514 | 100% | 0.080 | 612206 |
| pm | golf / austcham / futures | 508 | 10% | 0.029 | 0 |
| pm | soccer / epl / futures | 437 | 86% | 0.010 | 0 |
| pm | basketball / cbb / futures | 396 | 88% | 0.010 | 0 |
| pm | soccer / ucl / futures | 285 | 79% | 0.010 | 0 |
| pm | table-tennis / setkameua / table_tennis_match_winner | 268 | 97% | 0.170 | 0 |
| pm | football / cfb / football_team_full_game_winner | 244 | 78% | 0.055 | 0 |
| pm | tennis / itfme / tennis_match_winner | 228 | 84% | 0.010 | 0 |
| pm | golf / dpworlch / futures | 200 | 50% | 0.049 | 0 |
| k | KXNBA1HTEAMTOTAL / NBA 1st Half Team Total | 198 | 100% | 0.695 | 15922 |
| pm | tennis / utr / tennis_match_winner | 189 | 23% | 0.140 | 0 |
| pm | tennis / itfwo / tennis_match_winner | 175 | 81% | 0.010 | 0 |
| k | KXNBA1HSPREAD / NBA 1st Half Spread | 171 | 100% | 0.200 | 515093 |
| k | KXNBA1HTOTAL / NBA 1st Half Total | 171 | 100% | 0.320 | 625698 |
| k | KXNBA2HSPREAD / NBA 2nd Half Spread | 171 | 100% | 0.390 | 39866 |
| k | KXNBA2HTOTAL / NBA 2nd Half Total | 171 | 100% | 0.400 | 40440 |
| pm | soccer / unl / soccer_team_full_time_winner | 156 | 87% | 0.020 | 0 |
| pm | mma / ufc / futures | 148 | 78% | 0.010 | 0 |
| pm | soccer / lal / futures | 147 | 48% | 0.010 | 0 |
| pm | boxing / boxing / futures | 145 | 0% | - | 0 |
| pm | soccer / afcq / soccer_team_full_time_winner | 144 | 69% | 0.030 | 0 |
| k | KXNBA2QSPREAD / NBA 2nd Quarter Spread | 117 | 100% | 0.340 | 105516 |
| k | KXNBA3QSPREAD / NBA 3rd Quarter Spread | 117 | 100% | 0.350 | 72011 |
| k | KXNBA3QTOTAL / NBA 3rd Quarter Total | 117 | 100% | 0.350 | 49071 |
| k | KXNBA4QSPREAD / NBA 4th Quarter Spread | 117 | 100% | 0.300 | 1523 |
| k | KXCS2MAP / Counter-Strike 2 Map Winner  | 114 | 100% | 0.365 | 52186 |
| pm | basketball / nba / basketball_team_full_game_winner | 111 | 75% | 0.220 | 0 |
| pm | golf / lpga / futures | 108 | 3% | 0.020 | 0 |
| pm | macro /  / futures | 104 | 69% | 0.010 | 0 |
| k | KXNBA1QSPREAD / NBA 1st Quarter Spread | 104 | 100% | 0.340 | 0 |
| k | KXNBA1QTOTAL / NBA 1st Quarter Total | 104 | 100% | 0.310 | 0 |
| k | KXNBA2QTOTAL / NBA 2nd Quarter Total | 104 | 100% | 0.370 | 121038 |
| pm | tennis / atp / futures | 91 | 42% | 0.010 | 0 |
| k | KXNBA3PT / NBA Player Threes | 90 | 100% | 0.040 | 245976 |
| k | KXNBA3PTPROT / NBA Player Threes Protected | 90 | 100% | 0.760 | 25424 |
| pm | soccer / sea / futures | 88 | 85% | 0.010 | 0 |
| pm | tennis / wta / futures | 83 | 49% | 0.010 | 0 |
| pm | soccer / bun / futures | 80 | 84% | 0.010 | 0 |
| pm | soccer / lg1 / futures | 79 | 85% | 0.010 | 0 |
| k | KXNBAAST / NBA Player Assists | 69 | 100% | 0.040 | 242295 |
| k | KXNBAASTPROT / NBA Player Assists Protected | 68 | 100% | 0.850 | 11951 |
| pm | baseball / mlb / futures | 66 | 64% | 0.001 | 0 |
| pm | macro / usgas / futures | 66 | 71% | 0.010 | 0 |
| k | KXNBA4QTOTAL / NBA 4th Quarter Total | 65 | 100% | 0.260 | 3024 |
| pm | tennis / atp / tennis_match_winner | 59 | 95% | 0.010 | 0 |
| pm | table-tennis / czechligapro / table_tennis_match_winner | 55 | 9% | 0.480 | 0 |
| k | KXNFLGAME / NFL Game | 54 | 100% | 0.010 | 2760697 |
| k | KXATPCHALLENGERDOUBLES / ATP Challenger Doubles Match | 54 | 100% | 0.175 | 382 |
| pm | golf / masttour / futures | 52 | 100% | 0.102 | 0 |
| pm | technology /  / futures | 51 | 75% | 0.010 | 0 |
| pm | table-tennis / setkamecz / table_tennis_match_winner | 48 | 100% | 0.170 | 0 |
| pm | esports / cs2 / esports_match_winner | 47 | 72% | 0.020 | 0 |
| pm | tennis / atpdb / tennis_match_winner | 46 | 61% | 0.015 | 0 |
| pm | soccer / cnl / soccer_team_full_time_winner | 45 | 53% | 0.125 | 0 |

## Opportunities

| kind | distinct | hits | max margin $/contract | max persistence | fresh-BBO still open |
|---|---|---|---|---|---|
| decided_k | 112 | 950 | 0.9893 | 14 min | 0/0 |
| decided_pm | 25 | 500 | 0.9891 | 14 min | 263/500 |
| decided_pm_closed | 12 | 136 | 0.9891 | 18 min | 0/136 |
| dutch_k | 5 | 749 | 0.7327 | 115 min | 0/0 |
| dutch_k_sell | 2 | 4 | 0.0571 | 0 min | 0/0 |
| dutch_pm | 43 | 2192 | 0.2603 | 50 min | 0/0 |
| implication_k | 20 | 79 | 0.2252 | 19 min | 0/0 |
| lag_k_settled | 167 | 24847 | 0.9891 | 321 min | 23323/24308 |
| lag_k_settled_closed | 141 | 2646 | 0.9973 | 70 min | 0/2646 |

Top by persistence × hits:

- **lag_k_settled** basketball — KTP Basket Kotka vs. Lahti Basketball — bid 0.99 ask - sell_yes @ 0.99 | margin 0.9891 | 321 min, 1291 hits | fresh bbo 0.99/- depth 7/0 | score 100-81 VFT
- **lag_k_settled** esports — DarkZero Esports vs. Sharper Esport — bid 0.78 ask 0.83 sell_yes @ 0.78 | margin 0.7848 | 227 min, 1244 hits | fresh bbo 0.78/0.83 depth 10/9 | score 0-0 Map 1
- **dutch_k** 🔒  — Kansas Basketball: Next Head Coach — Σask 0.250 | margin 0.7327 | 115 min, 734 hits | score - 
- **lag_k_settled** esports —  Phantom Academy vs. The Chosen Few — bid 0.64 ask 0.65 sell_yes @ 0.64 | margin 0.6181 | 120 min, 480 hits | fresh bbo 0.64/0.65 depth 14/9 | score - NS
- **lag_k_settled** soccer — Manchester United FC vs. Aston Villa FC — bid 0.48 ask 0.49 buy_yes @ 0.49 | margin 0.5265 | 121 min, 479 hits | fresh bbo 0.48/0.49 depth 36/40 | score 0-0 
- **lag_k_settled** soccer — Manchester United FC vs. Aston Villa FC — bid 0.24 ask 0.25 sell_yes @ 0.24 | margin 0.2322 | 121 min, 479 hits | fresh bbo 0.24/0.25 depth 18/41 | score 0-0 
- **lag_k_settled** soccer — Manchester United FC vs. Aston Villa FC — bid 0.28 ask 0.29 sell_yes @ 0.28 | margin 0.2801 | 121 min, 479 hits | fresh bbo 0.28/0.29 depth 25/49 | score 0-0 
- **lag_k_settled** basketball — Maxima Roma vs. Pallacanestro Cantu — bid 0.81 ask 0.85 sell_yes @ 0.81 | margin 0.8700 | 116 min, 460 hits | fresh bbo 0.81/0.85 depth 19/9 | score 6-7 Q1
- **lag_k_settled** esports — Spirit vs. FUT Esports — bid 0.81 ask 0.82 sell_yes @ 0.81 | margin 0.7954 | 90 min, 349 hits | fresh bbo 0.81/0.82 depth 19/8 | score - NS
- **lag_k_settled** soccer — Club Atletico de Madrid vs. FC Barcelona — bid 0.26 ask 0.27 sell_yes @ 0.26 | margin 0.2513 | 92 min, 338 hits | fresh bbo 0.26/0.27 depth 18/32 | score 0-0 
- **lag_k_settled** soccer — Club Atletico de Madrid vs. FC Barcelona — bid 0.20 ask 0.21 sell_yes @ 0.2 | margin 0.1942 | 92 min, 338 hits | fresh bbo 0.20/0.21 depth 14/20 | score 0-0 
- **lag_k_settled** soccer — Club Atletico de Madrid vs. FC Barcelona — bid 0.53 ask 0.54 buy_yes @ 0.54 | margin 0.4463 | 92 min, 338 hits | fresh bbo 0.52/0.53 depth 21/36 | score 0-0 
- **lag_k_settled** basketball — NO Pelicans vs. LA Clippers — bid 0.52 ask 0.53 sell_yes @ 0.52 | margin 0.4963 | 81 min, 319 hits | fresh bbo 0.52/0.53 depth 28/27 | score - NS
- **lag_k_settled** esports — eBattles: France (R0ge) vs. England (JKey) — bid 0.01 ask 0.02 sell_yes @ 0.01 | margin 0.3284 | 67 min, 270 hits | fresh bbo 0.01/0.02 depth 1/4 | score 1-3 2H
- **lag_k_settled** esports — eBattles: France (R0ge) vs. England (JKey) — bid 0.01 ask 0.08 sell_yes @ 0.01 | margin 0.2417 | 67 min, 270 hits | fresh bbo 0.01/0.08 depth 1/6 | score 1-3 2H
- **lag_k_settled** esports — eBattles: France (d1pseN) vs. England (Upcake22) — bid 0.61 ask 0.62 sell_yes @ 0.61 | margin 0.5874 | 68 min, 267 hits | fresh bbo 0.61/0.62 depth 3/5 | score 2-2 2H
- **lag_k_settled** esports — eBattles: France (R0ge) vs. England (JKey) — bid 0.95 ask 0.99 buy_yes @ 0.99 | margin 0.5467 | 66 min, 266 hits | fresh bbo 0.95/- depth 9/0 | score 1-3 2H
- **lag_k_settled** esports — eBattles: France (d1pseN) vs. England (Upcake22) — bid 0.16 ask 0.17 sell_yes @ 0.16 | margin 0.6697 | 62 min, 267 hits | fresh bbo 0.16/0.17 depth 7/6 | score 2-2 2H
- **lag_k_settled** esports — eBattles: France (d1pseN) vs. England (Upcake22) — bid 0.26 ask 0.27 buy_yes @ 0.27 | margin 0.8272 | 62 min, 267 hits | fresh bbo 0.26/0.27 depth 8/4 | score 2-2 2H
- **lag_k_settled** esports — eBattles: England (Upcake22) vs. Argentina (mko1919) — bid 0.06 ask 0.07 buy_yes @ 0.07 | margin 0.9346 | 66 min, 259 hits | fresh bbo 0.06/0.07 depth 3/9 | score 2-3 2H
- **lag_k_settled** esports — eBattles: England (Upcake22) vs. Argentina (mko1919) — bid 0.60 ask 0.61 sell_yes @ 0.6 | margin 0.8166 | 66 min, 259 hits | fresh bbo 0.01/- depth 1/0 | score 2-3 2H
- **lag_k_settled** esports — eBattles: England (Upcake22) vs. France (d1pseN) — bid 0.03 ask 0.06 sell_yes @ 0.03 | margin 0.2801 | 66 min, 259 hits | fresh bbo 0.03/0.06 depth 2/5 | score 5-2 2H
- **lag_k_settled** esports — eBattles: New Orleans Pelicans (Chime) vs. Indiana Pacers (Knez) — bid 0.95 ask - sell_yes @ 0.95 | margin 0.9455 | 69 min, 255 hits | fresh bbo 0.95/- depth 11/0 | score 78-72 Q4
- **lag_k_settled** esports — eBattles: England (Upcake22) vs. Argentina (mko1919) — bid 0.37 ask 0.39 sell_yes @ 0.37 | margin 0.3479 | 66 min, 257 hits | fresh bbo 0.37/0.38 depth 4/6 | score 2-3 2H
- **lag_k_settled** esports — eBattles: Argentina (d1pseN) vs. France (Uncle) — bid 0.23 ask 0.25 buy_yes @ 0.25 | margin 0.9672 | 65 min, 258 hits | fresh bbo -/0.05 depth 0/4 | score 1-1 2H

## Live paper trades (no orders; Kalshi prices, taker fees)

Ledger L2-2026-11-01 (earlier ledgers excluded: none)

**Total closed P&L: $+34.06 on $210.94 staked (+16.1%)**

| rule | entries | closed | winners | staked | P&L | ROI |
|---|---|---|---|---|---|---|
| R1 anchor [ncaaf] | 1 | 1 | 0 | $9.98 | $-9.98 | -100% |
| R1 anchor [nfl] | 6 | 6 | 1 | $60.54 | $-45.54 | -75% |
| R2 q1cheap [ncaaf] | 2 | 2 | 0 | $10.52 | $-10.52 | -100% |
| R2 q1cheap [nfl] | 9 | 9 | 0 | $47.28 | $-47.28 | -100% |
| R3 blowout [ncaaf] | 1 | 1 | 1 | $21.15 | $+159.85 | +756% |
| R3 blowout [nfl] | 1 | 1 | 0 | $21.08 | $-21.08 | -100% |
| R6 decided [other] | 12 | 3 | 3 | $40.39 | $+8.61 | +21% |

| time (UTC) | rule | game | team | entry | contracts | why | result |
|---|---|---|---|---|---|---|---|
| 02:39 | R3 blowout | Ohio vs. Miami (OH) | Miami (OH) | 0.11 | 181 | down 17 in Q2, ask 0.11 | final score (pending Kalshi settlement): 1.00, $+159.85 |
| 01:59 | R6 decided | Mercer vs. Georgia Southern | Over 139.5 points | 0.95 | 2 | score 71-74 total 145 > 139.5 | open |
| 01:59 | R6 decided | Mercer vs. Georgia Southern | Over 144.5 points | 0.95 | 2 | score 71-74 total 145 > 144.5 | open |
| 01:56 | R6 decided | Mercer vs. Georgia Southern | Over 135.5 points | 0.95 | 2 | score 67-71 total 138 > 135.5 | open |
| 01:56 | R6 decided | Mercer vs. Georgia Southern | Over 132.5 points | 0.95 | 2 | score 67-71 total 138 > 132.5 | open |
| 01:56 | R6 decided | Mercer vs. Georgia Southern | Over 129.5 points | 0.95 | 2 | score 67-71 total 138 > 129.5 | open |
| 01:56 | R6 decided | Mercer vs. Georgia Southern | Over 125.5 points | 0.95 | 2 | score 67-71 total 138 > 125.5 | open |
| 01:56 | R6 decided | Mercer vs. Georgia Southern | Over 120.5 points | 0.95 | 2 | score 67-71 total 138 > 120.5 | open |
| 01:56 | R6 decided | Mercer vs. Georgia Southern | Over 115.5 points | 0.95 | 2 | score 67-71 total 138 > 115.5 | open |
| 01:56 | R6 decided | Mercer vs. Georgia Southern | Over 110.5 points | 0.95 | 2 | score 67-71 total 138 > 110.5 | open |
| 00:51 | R1 anchor | Kent State vs. Bowling Green | Kent St. | 0.57 | 17 | pregame dog (mid 0.38) leads 14-7 in Q2, ask 0.57 | final score (pending Kalshi settlement): 0.00, $-9.98 |
| 00:15 | R2 q1cheap | Kent State vs. Bowling Green | Kent St. | 0.20 | 25 | Q1 ask 0.20, score 0-7 | final score (pending Kalshi settlement): 0.00, $-5.28 |
| 00:03 | R2 q1cheap | Western Michigan vs. Akron | Akron | 0.15 | 33 | Q1 ask 0.15, score 0-0 | final score (pending Kalshi settlement): 0.00, $-5.24 |
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

### Score reaction speed (live, 15 s): share of the 3-minute move done by +15 s / +30 s / +60 s

- 26NOV08GBNE 24-7: 0% / 0% / 0%
- 26NOV08GBNE 24-7: -0% / -0% / -0%
- 26NOV08TBCHI 0-0: -0% / -0% / 50%
- 26NOV08TBCHI 0-0: 0% / 0% / 50%
- 26NOV08TBCHI 13-24: 33% / 33% / 33%
- 26NOV08TBCHI 22-24: 25% / 25% / 25%
- 26NOV08TBCHI 22-24: 20% / 20% / 20%
- 26NOV08TBCHI 24-24: 0% / 0% / 0%
- 26NOV08TBCHI 24-24: -0% / -0% / -0%
- 26NOV09BUFMIN 13-6: 0% / 0% / 0%
- 26NOV10KENTBGSU 27-27: -17% / -17% / -7%
- 26NOV10KENTBGSU 27-27: -17% / -17% / -7%
- 26NOV10KENTBGSU 28-27: 8% / 8% / 51%
- 26NOV10KENTBGSU 28-27: 9% / 9% / 54%
- 26NOV10KENTBGSU 28-33: 27% / 27% / 30%
- 26NOV10KENTBGSU 28-33: 25% / 25% / 28%
- 26NOV10OHIOMOH 17-14: 114% / 114% / 71%
- 26NOV10OHIOMOH 17-14: 115% / 115% / 62%
- 26NOV10OHIOMOH 17-20: -25% / -25% / -25%
- 26NOV10OHIOMOH 17-20: -12% / -12% / -25%

## Bot latency map: how long a decided Kalshi market stays mispriced

| sport | series | markets | already priced | mispriced then fixed | median s mispriced | closed/timeout | contradictions | cheapest ask (size) | resting @0.97 contracts / $ | settled right / wrong |
|---|---|---|---|---|---|---|---|---|---|---|
| basketball | KXNCAAWBTOTAL | 190 | 181 | 0 | - | 9 | 0 | 0.95 (2) | 0 / $0.00 | 155 / 0 |
| basketball | KXNCAAMBTOTAL | 121 | 111 | 3 | 187 | 7 | 0 | 0.65 (500) | 70 / $2.10 | 114 / 0 |
| football | KXNCAAFSPREAD | 71 | 71 | 0 | - | 0 | 0 | - | 0 / $0.00 | 71 / 0 |
| tennis | KXATPCHALLENGERMATCH | 62 | 62 | 0 | - | 0 | 0 | - | 0 / $0.00 | 62 / 0 |
| basketball | KXNCAAMBSPREAD | 48 | 38 | 2 | 1123 | 8 | 0 | 0.48 (1000) | 8 / $0.25 | 32 / 3 |
| soccer | KXCHNSLTOTAL | 41 | 39 | 2 | 1011 | 0 | 0 | 0.47 (3506) | 722 / $21.67 | 41 / 0 |
| soccer | KXELITESERIENTOTAL | 38 | 37 | 1 | 26 | 0 | 0 | 0.75 (200) | 11 / $0.34 | 38 / 0 |
| tennis | KXATPSETWINNER | 36 | 36 | 0 | - | 0 | 0 | - | 0 / $0.00 | 36 / 0 |
| soccer | KXTHAIL1TOTAL | 26 | 24 | 2 | 21 | 0 | 0 | 0.93 (0) | 0 / $0.00 | 26 / 0 |
| football | KXNFLGAME | 26 | 22 | 3 | 52 | 0 | 1 | 0.66 (0) | 0 / $0.00 | 18 / 0 |
| soccer | KXECULPTOTAL | 25 | 25 | 0 | - | 0 | 0 | - | 0 / $0.00 | 25 / 0 |
| basketball | KXNCAAWBSPREAD | 24 | 24 | 0 | - | 0 | 0 | - | 0 / $0.00 | 24 / 0 |
| soccer | KXEREDIVISIETOTAL | 22 | 21 | 0 | - | 1 | 0 | 0.65 (20) | 0 / $0.00 | 21 / 1 |
| soccer | KXBUNDESLIGA2TOTAL | 22 | 18 | 4 | 8 | 0 | 0 | 0.95 (2000) | 0 / $0.00 | 22 / 0 |
| soccer | KXSERIECTOTAL | 21 | 16 | 5 | 34 | 0 | 0 | 0.96 (0) | 0 / $0.00 | 21 / 0 |
| soccer | KXIDNSLTOTAL | 20 | 19 | 1 | 58 | 0 | 0 | 0.91 (5) | 0 / $0.00 | 20 / 0 |
| soccer | KXBELGIANPLTOTAL | 20 | 19 | 1 | 7 | 0 | 0 | 0.94 (1009) | 0 / $0.00 | 20 / 0 |
| football | KXNCAAFTOTAL | 19 | 16 | 3 | 2 | 0 | 0 | 0.62 (1974) | 0 / $0.00 | 19 / 0 |
| soccer | KXAUTBUNDESTOTAL | 19 | 19 | 0 | - | 0 | 0 | - | 0 / $0.00 | 19 / 0 |
| soccer | KXALLSVENSKANTOTAL | 19 | 19 | 0 | - | 0 | 0 | - | 0 / $0.00 | 19 / 0 |
| soccer | KXHUNNB1TOTAL | 17 | 15 | 2 | 25 | 0 | 0 | 0.95 (7) | 0 / $0.00 | 17 / 0 |
| basketball | KXNCAAMBGAME | 16 | 15 | 0 | - | 1 | 0 | 0.77 (2310) | 4777 / $143.31 | 14 / 0 |
| soccer | KXDIMAYORTOTAL | 15 | 14 | 1 | 1 | 0 | 0 | 0.72 (0) | 0 / $0.00 | 10 / 0 |
| soccer | KXAPFDDHTOTAL | 15 | 15 | 0 | - | 0 | 0 | - | 0 / $0.00 | 14 / 0 |
| soccer | KXUCLWTOTAL | 15 | 15 | 0 | - | 0 | 0 | - | 0 / $0.00 | 15 / 0 |
| basketball | KXNCAAWBGAME | 14 | 14 | 0 | - | 0 | 0 | - | 0 / $0.00 | 12 / 0 |
| soccer | KXCZEFNLTOTAL | 13 | 13 | 0 | - | 0 | 0 | - | 0 / $0.00 | 13 / 0 |
| soccer | KXEKSTRAKLASATOTAL | 13 | 12 | 1 | 403 | 0 | 0 | 0.60 (58) | 27 / $0.82 | 8 / 0 |
| soccer | KXKLEAGUETOTAL | 12 | 12 | 0 | - | 0 | 0 | - | 0 / $0.00 | 12 / 0 |
| soccer | KXLIGAPORTUGALTOTAL | 12 | 11 | 1 | 4 | 0 | 0 | 0.98 (4594) | 0 / $0.00 | 12 / 0 |
| soccer | KXDENSUPERLIGATOTAL | 11 | 11 | 0 | - | 0 | 0 | - | 0 / $0.00 | 11 / 0 |
| football | KXNCAAFGAME | 10 | 10 | 0 | - | 0 | 0 | - | 0 / $0.00 | 10 / 0 |
| tennis | KXWTASETWINNER | 10 | 10 | 0 | - | 0 | 0 | - | 0 / $0.00 | 10 / 0 |
| soccer | KXCHLLDPTOTAL | 10 | 10 | 0 | - | 0 | 0 | - | 0 / $0.00 | 9 / 0 |
| soccer | KXLIGAFTOTAL | 9 | 6 | 3 | 32 | 0 | 0 | 0.14 (169) | 189 / $5.66 | 9 / 0 |
| soccer | KXCZEFLTOTAL | 9 | 9 | 0 | - | 0 | 0 | - | 0 / $0.00 | 9 / 0 |
| basketball | KXFIBACHAMPTOTAL | 9 | 9 | 0 | - | 0 | 0 | - | 0 / $0.00 | 9 / 0 |
| soccer | KXJ2LEAGUETOTAL | 8 | 8 | 0 | - | 0 | 0 | - | 0 / $0.00 | 8 / 0 |
| soccer | KXJLEAGUETOTAL | 7 | 7 | 0 | - | 0 | 0 | - | 0 / $0.00 | 7 / 0 |
| soccer | KXBUNDESLIGAWTOTAL | 6 | 6 | 0 | - | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| soccer | KXBULFLTOTAL | 6 | 6 | 0 | - | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| tennis | KXATPEXACTMATCH | 6 | 6 | 0 | - | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| tennis | KXATPCHALLENGERDOUBLES | 6 | 6 | 0 | - | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| basketball | KXEUROCUPTOTAL | 6 | 6 | 0 | - | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| basketball | KXEUROCUPSPREAD | 6 | 6 | 0 | - | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| soccer | KXCHNSLBTTS | 5 | 4 | 0 | - | 1 | 0 | 0.12 (11) | 361 / $10.82 | 4 / 1 |
| soccer | KXSUPERLIGTOTAL | 5 | 5 | 0 | - | 0 | 0 | - | 0 / $0.00 | 5 / 0 |
| soccer | KXEKSTRAKLASASPREAD | 5 | 5 | 0 | - | 0 | 0 | - | 0 / $0.00 | 0 / 0 |
| soccer | KXJLEAGUESPREAD | 4 | 4 | 0 | - | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
| soccer | KXJ2LEAGUESPREAD | 4 | 4 | 0 | - | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
| esports | KXCS2GAME | 4 | 4 | 0 | - | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
| soccer | KXEPLSPREAD | 4 | 4 | 0 | - | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
| soccer | KXBRASILEIROBTOTAL | 4 | 4 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| basketball | KXNBAGAME | 4 | 4 | 0 | - | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
| basketball | KXJBLEAGUEGAME | 4 | 4 | 0 | - | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
| tennis | KXATPMATCH | 4 | 4 | 0 | - | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
| basketball | KXEUROCUPGAME | 4 | 4 | 0 | - | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
| soccer | KXJLEAGUE1H | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXKLEAGUE1HTOTAL | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXTFF1LIGTOTAL | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXEPL1HTOTAL | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXLIGUE1BTTS | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXLALIGA1H | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXJLEAGUE1HTOTAL | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| basketball | KXKBLGAME | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| esports | KXDOTA2GAME | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXSERIECBTTS | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXBUNDESLIGA2BTTS | 2 | 1 | 1 | 4 | 0 | 0 | 0.90 (24) | 8 / $0.24 | 2 / 0 |
| soccer | KXROML1TOTAL | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXELITESERIENBTTS | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXBUNDESLIGATOTAL | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| basketball | KXBBSERIEATOTAL | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXCOPADOBRASILTOTAL | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXJLEAGUE1HBTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXJLEAGUEGAME | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXJ2LEAGUEGAME | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXJLEAGUEBTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXJ2LEAGUEBTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXKLEAGUE1HBTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXIDNSLBTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXTHAIL1BTTS | 1 | 0 | 1 | 29 | 0 | 0 | 0.97 (1) | 0 / $0.00 | 1 / 0 |
| soccer | KXEPL1HBTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXUAEPLTOTAL | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXALLSVENSKANBTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXAUTBUNDESBTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXHNLTOTAL | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXLIGUE1GAME | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXBELGIANPLBTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXLALIGATOTAL | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXLIGAPORTUGALBTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXLIGAMXTOTAL | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXLIGAEXPTOTAL | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXUCLWBTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |

'Already priced' = the book was at 99c+ when we first looked (bots were faster than our score feed). 'Median s mispriced' runs from our decision to the fix. 'Settled right / wrong' checks our certainty against Kalshi's result — any 'wrong' means the score feed or the model failed.

## Decided-state engine (contracts the live score already settled, still trading)

1288 contracts decided while active; 112 had a price leaving > 0.4c after fees; 36 of those were mispriced AFTER the score was stable (lock tier)

| sport | game | contract | decided | reason | max margin | mispriced for | lock margin | lock depth |
|---|---|---|---|---|---|---|---|---|
| basketball | Minot State (W) vs. North Dakota | KXNCAAMBSPREAD-26NOV08NDSUCSB-CSB2 | NO | ended 68-84 margin -16 vs 1.5 | 0.373 | 276s | 0.373 | 2173 |
| basketball | Fayetteville State (W) vs. North | KXNCAAMBTOTAL-26NOV09SCUSCCAR-142 | NO | ended total 116 <= 141.5 | 0.334 | 97s | 0.334 | 1968 |
| basketball | Fayetteville State (W) vs. North | KXNCAAMBSPREAD-26NOV09SCUSCCAR-CCAR13 | NO | ended 56-60 margin 4 vs 12.5 | 0.276 | 97s | 0.276 | 2276 |
| basketball | Fayetteville State (W) vs. North | KXNCAAMBTOTAL-26NOV09SCUSCCAR-145 | NO | ended total 116 <= 144.5 | 0.237 | 97s | 0.237 | 2306 |
| basketball | Minot State (W) vs. North Dakota | KXNCAAMBSPREAD-26NOV08NDSUCSB-CSB6 | NO | ended 68-84 margin -16 vs 5.5 | 0.227 | 276s | 0.227 | 2000 |
| basketball | Fayetteville State (W) vs. North | KXNCAAMBSPREAD-26NOV09SCUSCCAR-CCAR4 | YES | ended 56-60 margin 4 vs 3.5 | 0.227 | 97s | 0.227 | 2334 |
| soccer | SC Cambuur-Leeuwarden vs. PSV | KXEREDIVISIETOTAL-26NOV08CAMPSV-7 | YES | score 2-5 total 7 > 6.5 | 0.179 | 531s | 0.179 | 58 |
| basketball | Fayetteville State (W) vs. North | KXNCAAMBTOTAL-26NOV09SCUSCCAR-148 | NO | ended total 116 <= 147.5 | 0.170 | 97s | 0.170 | 1000 |
| basketball | Fayetteville State (W) vs. North | KXNCAAMBSPREAD-26NOV09SCUSCCAR-CCAR16 | NO | ended 56-60 margin 4 vs 15.5 | 0.151 | 97s | 0.151 | 1000 |
| basketball | Fayetteville State (W) vs. North | KXNCAAMBTOTAL-26NOV09SCUSCCAR-150 | NO | ended total 116 <= 149.5 | 0.132 | 97s | 0.132 | 1000 |
| basketball | Minot State (W) vs. North Dakota | KXNCAAMBSPREAD-26NOV08NDSUCSB-CSB11 | NO | ended 68-84 margin -16 vs 10.5 | 0.122 | 276s | 0.122 | 1000 |
| basketball | Fayetteville State (W) vs. North | KXNCAAMBGAME-26NOV09SCUSCCAR-CCAR | YES | ended 56-60 | 0.122 | 97s | 0.122 | 5940 |
| basketball | Fayetteville State (W) vs. North | KXNCAAMBTOTAL-26NOV09SCUSCCAR-152 | NO | ended total 116 <= 151.5 | 0.094 | 97s | 0.094 | 571 |
| tennis | James Duckworth vs. Cameron Norr | KXATPEXACTMATCH-26NOV09DUCNOR-NOR21 | YES | ended 5-7, 0-6 | 0.989 | 60s | - | 0 |
| tennis | Alex Michelsen vs. Juan Manuel C | KXATPEXACTMATCH-26NOV10MICCER-MIC21 | YES | ended 6-3, 6-2 | 0.989 | 537s | - | 0 |
| basketball | Fayetteville State (W) vs. North | KXNCAAMBSPREAD-26NOV09SCUSCCAR-CCAR19 | NO | ended 56-60 margin 4 vs 18.5 | 0.084 | 97s | 0.084 | 1001 |
| soccer | SC Cambuur-Leeuwarden vs. PSV | KXEREDIVISIETOTAL-26NOV08CAMPSV-4 | YES | score 1-3 total 4 > 3.5 | 0.883 | 531s | - | 0 |
| basketball | Minot State (W) vs. North Dakota | KXNCAAMBSPREAD-26NOV08NDSUCSB-NDSU15 | YES | ended 68-84 margin 16 vs 14.5 | 0.831 | 276s | - | 0 |
| basketball | Fayetteville State (W) vs. North | KXNCAAMBTOTAL-26NOV09SCUSCCAR-128 | NO | ended total 116 <= 127.5 | 0.831 | 97s | - | 0 |
| soccer | SC Cambuur-Leeuwarden vs. PSV | KXEREDIVISIETOTAL-26NOV08CAMPSV-5 | NO | ended total 3 <= 4.5 | 0.820 | 531s | - | 0 |
| basketball | Fayetteville State (W) vs. North | KXNCAAMBTOTAL-26NOV09SCUSCCAR-129 | NO | ended total 116 <= 128.5 | 0.810 | 97s | - | 0 |
| basketball | Fayetteville State (W) vs. North | KXNCAAMBTOTAL-26NOV09SCUSCCAR-123 | NO | ended total 116 <= 122.5 | 0.737 | 97s | - | 0 |
| basketball | Fayetteville State (W) vs. North | KXNCAAMBTOTAL-26NOV09SCUSCCAR-118 | NO | ended total 116 <= 117.5 | 0.706 | 97s | - | 0 |
| basketball | Minot State (W) vs. North Dakota | KXNCAAMBSPREAD-26NOV08NDSUCSB-NDSU10 | YES | ended 68-84 margin 16 vs 9.5 | 0.696 | 276s | - | 0 |
| soccer | 1. FC Magdeburg vs. FC St. Pauli | KXBUNDESLIGA2TOTAL-26NOV08FCMSTP-5 | YES | score 4-1 total 5 > 4.5 | 0.654 | 41s | - | 0 |

## Close / settlement latency (how clunky each venue is after the final whistle)

Kalshi: settlement_ts − close_time per series (negative = settled before the scheduled close)

| series | n | median | p90 |
|---|---|---|---|
| KXNFLPASSYDSPRECISE Pass Yards Precise | 12588 | 4.1 min | 4.1 min |
| KXESOCCERGAME eSoccer Game | 3764 | 4.0 min | 4.1 min |
| KXNCAAMBTOTAL Men's College Basketball Total | 1997 | 4.0 min | 4.1 min |
| KXNCAAMBSPREAD Men's College Basketball Sprea | 1594 | 1.8 min | 1.8 min |
| KXNFLRECYDS Pro Football Receiving Yards | 1334 | 2.0 min | 2.1 min |
| KXNCAAWBTOTAL Women's College Basketball Tot | 1234 | 2.5 min | 2.6 min |
| KXNFLRECYDSPROT Receiving Yards Protected | 1228 | 6.0 min | 6.1 min |
| KXNBA3PT NBA Player Threes | 1210 | 2.0 min | 2.1 min |
| KXNFLTOTALPRECISE Total Precise | 1096 | 4.0 min | 4.1 min |
| KXNBAPTS NBA Player Points | 1051 | 2.0 min | 2.1 min |
| KXNBAREB NBA Player Rebounds | 1049 | 2.0 min | 2.1 min |
| KXNBA3PTPROT NBA Player Threes Protected | 1030 | 2.6 min | 2.6 min |
| KXNFLREC Pro Football Player Receptions | 1029 | 2.0 min | 2.1 min |
| KXNBAREBPROT NBA Player Rebounds Protected | 1023 | 2.6 min | 2.6 min |
| KXNHLGOAL NHL Goalscorer | 981 | 3.0 min | 3.1 min |
| KXNFLRECPROT Receptions Protected | 958 | 6.0 min | 6.1 min |
| KXNBAPTSPROT NBA Player Points Protected | 953 | 2.6 min | 2.6 min |
| KXNBAAST NBA Player Assists | 842 | 2.0 min | 2.1 min |
| KXLIGAPROMATCH Russia Liga Pro Match | 818 | 4.0 min | 4.1 min |
| KXNBAASTPROT NBA Player Assists Protected | 770 | 2.6 min | 2.6 min |
| KXNBAPRA NBA Player Points + Rebounds + | 760 | 2.5 min | 2.6 min |
| KXNBATEAMTOTAL NBA Team Total | 759 | 2.5 min | 2.6 min |
| KXNBAPRAPROT Pts + Reb + Ast Protected | 718 | 2.6 min | 2.6 min |
| KXNHLPTS Pro Hockey Points | 701 | 3.0 min | 3.1 min |
| KXNFLRSHYDS Pro Football Rushing Yards | 658 | 2.0 min | 2.1 min |
| KXNBASPREAD NBA Spread | 609 | 1.8 min | 1.8 min |
| KXNHLFIRSTGOAL NHL First Goal | 591 | 6.0 min | 6.0 min |
| KXNFLRSHYDSPROT Rushing Yards Protected | 574 | 6.0 min | 6.1 min |
| KXNCAAWBSPREAD Women's College Basketball Spr | 561 | 1.8 min | 1.8 min |
| KXITFMATCH ITF Men's Match | 548 | 2.0 min | 2.1 min |
| KXNHLAST Pro Hockey Assists | 541 | 6.0 min | 6.1 min |
| KXNBATOTAL NBA Total | 540 | 1.8 min | 1.8 min |
| KXNFLTDPROT Pro Football Touchdowns Protec | 488 | 6.0 min | 6.1 min |
| KXNFLTD Pro Football Touchdowns | 468 | 2.1 min | 2.1 min |
| KXEBASKETBALLGAME eBasketball Game | 464 | 4.0 min | 4.1 min |
| KXITFWMATCH ITF Women's Match | 444 | 2.0 min | 2.1 min |
| KXNBA1HTEAMTOTAL NBA 1st Half Team Total | 440 | 2.5 min | 2.6 min |
| KXNBASTL NBA Player Steals | 430 | 2.0 min | 2.1 min |
| KXNBA2HTOTAL NBA 2nd Half Total | 380 | 2.5 min | 2.6 min |
| KXNBA2HSPREAD NBA 2nd Half Spread | 380 | 2.5 min | 2.6 min |

## Participant fingerprint (per sport; 60 s snapshots)

change% = share of scan cycles (60 s) where the best quote moved; react = median minutes from a score change to the next quote move (humans: slow, bursty, round sizes; bots: constant cadence, odd/constant sizes, instant reaction)

| venue | sport | markets | snapshots | two-sided | med spread | change% | react (min) | round sizes | med size |
|---|---|---|---|---|---|---|---|---|---|
| pm | tennis | 2191 | 152729 | 93% | 0.010 | 23% | 0.6 (n=79089) | - | - |
| pm | soccer | 744 | 110421 | 83% | 0.020 | 19% | 0.7 (n=1740) | - | - |
| pm | esports | 3213 | 77027 | 78% | 0.020 | 18% | 0.5 (n=15608) | - | - |
| pm | basketball | 709 | 51790 | 68% | 0.020 | 16% | 0.6 (n=10421) | - | - |
| pm | table-tennis | 1607 | 45142 | 94% | 0.010 | 26% | 0.5 (n=24463) | - | - |
| pm | climate | 216 | 10686 | 69% | 0.040 | 31% | - (n=0) | - | - |
| pm | motorsports | 144 | 8280 | 46% | 0.050 | 19% | - (n=0) | - | - |
| pm | cricket | 18 | 4614 | 89% | 0.040 | 8% | 0.7 (n=957) | - | - |
| pm | ice-hockey | 39 | 4564 | 92% | 0.050 | 18% | 0.6 (n=167) | - | - |
| pm | football | 142 | 3840 | 85% | 0.003 | 16% | 2.0 (n=172) | - | - |
| pm | macro | 241 | 3208 | 48% | 0.020 | 11% | - (n=0) | - | - |
| pm | beach-volleyball | 69 | 2539 | 91% | 0.010 | 19% | 0.6 (n=1125) | - | - |
| pm | mma | 5 | 1147 | 39% | 0.380 | 3% | - (n=0) | - | - |
| pm | darts | 55 | 654 | 94% | 0.070 | 14% | 0.5 (n=37) | - | - |
| pm | boxing | 5 | 328 | 88% | 0.050 | 25% | 11.1 (n=2) | - | - |
| pm | technology | 110 | 272 | 16% | 0.155 | 5% | - (n=0) | - | - |
| pm | pickleball | 5 | 96 | 82% | 0.260 | 30% | - (n=0) | - | - |
| pm | baseball | 5 | 77 | 34% | 0.040 | 5% | 1.6 (n=7) | - | - |
| k | KXNCAAFGAME College Football Game | 530 | 763373 | 99% | 0.200 | 6% | - | 6% | 4 |
| k | KXNBA3PT NBA Player Threes | 1416 | 202114 | 81% | 0.050 | 18% | - | 34% | 25 |
| k | KXNFLPASSYDSPRECISE Pass Yards Precise | 16856 | 184254 | 0% | 0.390 | 12% | - | 42% | 1 |
| k | KXNBAAST NBA Player Assists | 1054 | 135963 | 84% | 0.050 | 19% | - | 32% | 27 |
| k | KXNBAPTS NBA Player Points | 1247 | 121955 | 84% | 0.040 | 23% | - | 29% | 42 |
| k | KXNFLGAME NFL Game | 82 | 116304 | 99% | 0.010 | 3% | - | 2% | 54828 |
| k | KXNBAREB NBA Player Rebounds | 1400 | 115317 | 82% | 0.050 | 22% | - | 30% | 29 |
| k | KXCS2MAP Counter-Strike 2 Map Win | 428 | 99414 | 96% | 0.400 | 7% | - | 24% | 124 |
| k | KXNBA3PTPROT NBA Player Threes Protec | 1401 | 85877 | 53% | 0.140 | 4% | - | 16% | 25 |
| k | KXNBAPRA NBA Player Points + Rebo | 897 | 85709 | 86% | 0.080 | 23% | - | 25% | 20 |
| k | KXDOTA2MAP Dota 2 Map Winner | 396 | 59293 | 95% | 0.410 | 6% | - | 15% | 22 |
| k | KXESOCCERGAME eSoccer Game | 3972 | 54702 | 24% | 0.580 | 5% | - | 21% | 30 |
| k | KXNCAAMBTOTAL Men's College Basketball | 2550 | 53390 | 51% | 0.060 | 9% | - | 35% | 110 |
| k | KXNBAASTPROT NBA Player Assists Prote | 1041 | 52839 | 52% | 0.160 | 5% | - | 13% | 21 |
| k | KXNBAPTSPROT NBA Player Points Protec | 1156 | 47962 | 57% | 0.650 | 6% | - | 11% | 25 |
| k | KXNBA1HTEAMTOTAL NBA 1st Half Team Total | 638 | 47163 | 72% | 0.200 | 17% | - | 34% | 250 |
| k | KXNBAREBPROT NBA Player Rebounds Prot | 1358 | 45404 | 53% | 0.140 | 6% | - | 15% | 25 |
| k | KXNCAAFTEAMTOTAL College Football Team To | 1674 | 43436 | 95% | 0.050 | 2% | - | 59% | 100 |
| k | KXNCAAMBSPREAD Men's College Basketball | 1935 | 43279 | 51% | 0.060 | 8% | - | 36% | 179 |
| k | KXNBA1HSPREAD NBA 1st Half Spread | 551 | 38850 | 71% | 0.030 | 12% | - | 15% | 267 |
| k | KXNBA1HTOTAL NBA 1st Half Total | 551 | 38760 | 72% | 0.040 | 13% | - | 27% | 150 |
| k | KXATPCHALLENGERMATCH Challenger ATP  | 408 | 38090 | 90% | 0.010 | 8% | - | 2% | 787 |
| k | KXNHLGOAL NHL Goalscorer | 1102 | 34899 | 31% | 0.070 | 16% | - | 24% | 35 |
| k | KXNCAAWBTOTAL Women's College Basketba | 2103 | 30759 | 31% | 0.460 | 8% | - | 13% | 2 |
| k | KXNBAPRAPROT Pts + Reb + Ast Protecte | 918 | 29348 | 30% | 0.670 | 3% | - | 33% | 25 |
| k | KXNFLRECYDS Pro Football Receiving Y | 2047 | 25825 | 16% | 0.040 | 28% | - | 21% | 100 |
| k | KXNBASTL NBA Player Steals | 469 | 25671 | 78% | 0.080 | 18% | - | 28% | 17 |
| k | KXNBA2QSPREAD NBA 2nd Quarter Spread | 377 | 24514 | 70% | 0.030 | 12% | - | 24% | 150 |
| k | KXNBA2QTOTAL NBA 2nd Quarter Total | 364 | 23744 | 71% | 0.040 | 12% | - | 35% | 100 |
| k | KXNFLRECYDSPROT Receiving Yards Protecte | 1917 | 23368 | 10% | 0.785 | 16% | - | 15% | 9 |
| k | KXNBA3QSPREAD NBA 3rd Quarter Spread | 377 | 23067 | 75% | 0.030 | 15% | - | 49% | 124 |
| k | KXNBA2HSPREAD NBA 2nd Half Spread | 551 | 23060 | 70% | 0.080 | 22% | - | 37% | 247 |
| k | KXNBA3QTOTAL NBA 3rd Quarter Total | 377 | 22367 | 76% | 0.030 | 16% | - | 40% | 174 |
| k | KXNBA2HTOTAL NBA 2nd Half Total | 551 | 22189 | 74% | 0.110 | 22% | - | 47% | 247 |
| k | KXNCAAFSPREAD College Football Spread | 2256 | 21664 | 84% | 0.030 | 3% | - | 29% | 500 |
| k | KXNFLTOTALPRECISE Total Precise | 2128 | 21432 | 0% | - | 0% | - | 0% | - |
| k | KXNBA1QTOTAL NBA 1st Quarter Total | 377 | 20273 | 68% | 0.030 | 10% | - | 30% | 197 |
| k | KXNBA1QSPREAD NBA 1st Quarter Spread | 377 | 20217 | 67% | 0.030 | 9% | - | 32% | 114 |
| k | KXNFLFFWEEKLEAD Weekly Fantasy Football  | 252 | 19391 | 1% | 0.800 | 1% | - | 11% | 126 |
| k | KXITFWMATCH ITF Women's Match | 674 | 18956 | 75% | 0.030 | 10% | - | 7% | 40 |

## Schema notes (raw keys seen)

- polymarket: active, archived, category, chatChannel, closed, combos, createdAt, description, elapsed, endDate, ended, eventState, fixtureId, gameId, hidden, id, insiderTradingRules, live, marketCounts, marketGroups, markets, metadata, participants, payoutEstimateMessage, payoutEstimateTime, period, primaryTag, score, seriesSlug, slug, sortType, sportradarGameId, startDate, startTime, streamProvider, streamRequiresAuth, tags, teams, ticker, title, updatedAt
- kalshi: can_close_early, close_time, created_time, custom_strike, early_close_condition, event_ticker, exchange_index, expected_expiration_time, expiration_time, expiration_value, last_price_dollars, latest_expiration_time, market_type, no_ask_dollars, no_bid_dollars, no_sub_title, notional_value_dollars, occurrence_datetime, open_interest_fp, open_time, previous_price_dollars, previous_yes_ask_dollars, previous_yes_bid_dollars, price_level_structure, price_ranges, result, rules_primary, rules_secondary, settlement_bounds_type, settlement_timer_seconds, settlement_value_dollars, status, strike_type, ticker, title, updated_time, volume_24h_fp, volume_fp, yes_ask_dollars, yes_ask_size_fp, yes_bid_dollars, yes_bid_size_fp, yes_sub_title

