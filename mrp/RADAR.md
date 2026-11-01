# Mr. P — sports radar

Updated 2026-11-01T21:18:41Z by `run-20261101T2008-41326096177` (last 7 days). Read-only scanner of every sports market on Polymarket US and Kalshi — it never places orders.
Kit: `mrp/mrp_sports_radar.py` on the `mrp` branch. Raw tape: `mrp/radar/<run>/`.

# Sports radar report

records 4,611,374 | 2026-10-29 21:17Z → 21:17Z | runs 22 | pairs matched 1459 | errors {'radar': 19, 'sp.k.series_poll:KXATPEXACTMATCH': 10, 'sp.k.series_poll:KXATPMATCH': 10, 'sp.k.series_poll:KXATPSETWINNER': 10, 'sp.k.series_poll:KXAUTBUNDESTOTAL': 4, 'sp.k.series_poll:KXEFLL11H': 6, 'sp.k.series_poll:KXEFLL11HSPREAD': 10, 'sp.k.series_poll:KXHNLTOTAL': 6, 'sp.k.series_poll:KXLALIGABTTS': 9, 'sp.k.series_poll:KXLALIGASCORE': 6, 'sp.k.series_poll:KXLALIGASPREAD': 8, 'sp.k.always:KXNFLGAME': 6, 'sp.k.series_poll:KXATPCHALLENGERMATCH': 7, 'sp.k.series_poll:KXEFLL11HBTTS': 10, 'sp.k.series_poll:KXLALIGA2H': 6, 'sp.k.series_poll:KXCS2MAP': 6, 'sp.k.series_poll:KXEFLL11HTOTAL': 8, 'sp.k.series_poll:KXLALIGA2HBTTS': 8, 'sp.k.series_poll:KXLALIGA2HSPREAD': 6, 'sp.k.series_poll:KXLALIGA2HTOTAL': 4, 'sp.k.series_poll:KXLALIGACORNERS': 8, 'sp.k.series_poll:KXLALIGAGAME': 6, 'sp.k.series_poll:KXLALIGAGOAL': 6, 'sp.k.series_poll:KXAUTBUNDESGAME': 2, 'sp.k.series_poll:KXCZEFLTOTAL': 7, 'sp.k.series_poll:KXELITESERIENTOTAL': 2, 'sp.k.series_poll:KXEREDIVISIETOTAL': 2, 'sp.k.always:KXNCAAFGAME': 7, 'sp.k.series_poll:KXLIGUE11HBTTS': 3, 'sp.k.series_poll:KXLIGUE11HSCORE': 4, 'sp.k.series_poll:KXLIGUE11H': 4, 'sp.k.series_poll:KXLIGUE11HSPREAD': 1}

## Catalogue (latest inventory, 20:14Z)

Polymarket US sports events 4334 of 5822 active events; Kalshi near-term sports markets 2040 in 560 events; calls so far {'pm': 45, 'k': 894}; MB {'pm': 158517858, 'k': 78665026}

| venue | sport / league / type | markets | two-sided | med spread | vol 24h |
|---|---|---|---|---|---|
| pm | football / nfl / futures | 4117 | 63% | 0.010 | 0 |
| pm | football / cfb / futures | 1608 | 79% | 0.010 | 0 |
| pm | basketball / nba / futures | 1422 | 64% | 0.030 | 0 |
| pm | ice-hockey / nhl / futures | 779 | 98% | 0.010 | 0 |
| pm | basketball / wcbb / basketball_team_full_game_winner | 653 | 32% | 0.450 | 0 |
| pm | basketball / cbb / basketball_team_full_game_winner | 635 | 27% | 0.040 | 0 |
| k | KXNCAAFGAME / College Football Game | 484 | 100% | 0.100 | 472878 |
| pm | golf / worlwide / futures | 469 | 25% | 0.499 | 0 |
| pm | soccer / epl / futures | 435 | 86% | 0.010 | 0 |
| pm | basketball / cbb / futures | 317 | 85% | 0.010 | 0 |
| pm | tennis / utr / tennis_match_winner | 288 | 18% | 0.430 | 0 |
| pm | soccer / ucl / futures | 276 | 77% | 0.010 | 0 |
| pm | baseball / mlb / futures | 264 | 25% | 0.001 | 0 |
| pm | football / cfb / football_team_full_game_winner | 211 | 89% | 0.080 | 0 |
| pm | tennis / itfme / tennis_match_winner | 173 | 28% | 0.010 | 0 |
| pm | macro /  / futures | 150 | 74% | 0.010 | 0 |
| pm | soccer / lal / futures | 146 | 65% | 0.010 | 0 |
| pm | boxing / boxing / futures | 145 | 0% | - | 0 |
| pm | table-tennis / setkameua / table_tennis_match_winner | 144 | 53% | 0.100 | 0 |
| pm | mma / ufc / futures | 142 | 80% | 0.010 | 0 |
| pm | motorsports / f1 / futures | 137 | 20% | 0.011 | 0 |
| pm | tennis / itfwo / tennis_match_winner | 127 | 27% | 0.045 | 0 |
| pm | tennis / atp / tennis_match_winner | 125 | 63% | 0.020 | 0 |
| pm | basketball / nba / basketball_team_full_game_winner | 109 | 73% | 0.270 | 0 |
| pm | tennis / atp / futures | 107 | 40% | 0.010 | 0 |
| pm | soccer / sea / futures | 86 | 83% | 0.010 | 0 |
| pm | tennis / wta / futures | 79 | 42% | 0.020 | 0 |
| pm | soccer / bun / futures | 79 | 82% | 0.010 | 0 |
| pm | soccer / lg1 / futures | 77 | 84% | 0.010 | 0 |
| pm | golf / vidamexi / futures | 66 | 12% | 0.003 | 0 |
| pm | motorsports / nascar / futures | 63 | 48% | 0.020 | 0 |
| pm | soccer / j2 / soccer_team_full_time_winner | 60 | 67% | 0.030 | 0 |
| pm | tennis / atpdb / tennis_match_winner | 60 | 25% | 0.430 | 0 |
| k | KXNFLGAME / NFL Game | 56 | 100% | 0.010 | 59181104 |
| pm | soccer / uecl / soccer_team_full_time_winner | 55 | 98% | 0.030 | 0 |
| pm | table-tennis / czechligapro / table_tennis_match_winner | 55 | 15% | 0.470 | 0 |
| pm | soccer / ucl / soccer_team_full_time_winner | 54 | 100% | 0.010 | 0 |
| pm | soccer / uel / soccer_team_full_time_winner | 54 | 100% | 0.020 | 0 |
| pm | soccer / mls / futures | 53 | 89% | 0.010 | 0 |
| pm | golf / masttour / futures | 52 | 100% | 0.498 | 0 |
| pm | golf / simmbank / futures | 51 | 0% | - | 0 |
| pm | tennis / wta / tennis_match_winner | 50 | 92% | 0.010 | 0 |
| pm | soccer / acle / soccer_team_full_time_winner | 48 | 58% | 0.030 | 0 |
| pm | technology /  / futures | 42 | 74% | 0.010 | 0 |
| pm | football / nfl / football_team_full_game_winner | 41 | 68% | 0.010 | 0 |
| pm | soccer / sea / soccer_team_full_time_winner | 39 | 100% | 0.010 | 0 |
| pm | soccer / lmx / futures | 36 | 22% | 0.050 | 0 |
| pm | soccer / uel / futures | 36 | 3% | 0.150 | 0 |
| pm | soccer / uecl / futures | 36 | 0% | - | 0 |
| pm | soccer / lal / soccer_team_full_time_winner | 36 | 100% | 0.010 | 0 |
| pm | soccer / ligpor / soccer_team_full_time_winner | 36 | 69% | 0.040 | 0 |
| pm | soccer / ekst / soccer_team_full_time_winner | 36 | 61% | 0.060 | 0 |
| pm | soccer / serca / soccer_team_full_time_winner | 36 | 44% | 0.480 | 0 |
| pm | soccer / eflch / soccer_team_full_time_winner | 36 | 100% | 0.020 | 0 |
| pm | ice-hockey / nhl / hockey_team_full_game_winner | 35 | 97% | 0.010 | 0 |
| pm | soccer / lg1 / soccer_team_full_time_winner | 33 | 100% | 0.020 | 0 |
| pm | soccer / bel1 / soccer_team_full_time_winner | 33 | 55% | 0.055 | 0 |
| pm | soccer / epl / soccer_team_full_time_winner | 33 | 100% | 0.010 | 0 |
| pm | soccer / tff1 / soccer_team_full_time_winner | 33 | 39% | 0.480 | 0 |
| pm | soccer / alsv / soccer_team_full_time_winner | 33 | 64% | 0.050 | 0 |

## Opportunities

| kind | distinct | hits | max margin $/contract | max persistence | fresh-BBO still open |
|---|---|---|---|---|---|
| decided_k | 868 | 64315 | 0.9893 | 69 min | 0/0 |
| decided_pm | 22 | 469 | 0.9947 | 28 min | 160/469 |
| decided_pm_closed | 13 | 140 | 0.9893 | 30 min | 0/140 |
| dutch_k | 16 | 480 | 0.1744 | 140 min | 0/0 |
| dutch_k_sell | 3 | 6 | 0.0107 | 0 min | 0/0 |
| dutch_pm | 62 | 3010 | 0.5316 | 50 min | 0/0 |
| implication_k | 8256 | 478305 | 0.9786 | 141 min | 0/0 |
| lag_k_settled | 195 | 32705 | 0.9947 | 273 min | 27154/31684 |
| lag_k_settled_closed | 161 | 2451 | 0.9947 | 272 min | 0/2451 |

Top by persistence × hits:

- **lag_k_settled** esports — BILIBILI GAMING vs. Hanwha Life Esports — bid 0.42 ask 0.43 buy_yes @ 0.43 | margin 0.5732 | 117 min, 1186 hits | fresh bbo 0.42/0.43 depth 12/14 | score - NS
- **lag_k_settled** basketball — Ulm Basketball vs. Baskets Oldenburg — bid 0.99 ask - sell_yes @ 0.99 | margin 0.9893 | 273 min, 941 hits | score 81-65 FT
- **lag_k_settled** basketball — Basketball Lowen Braunschweig vs. Wurzburg Baskets — bid 0.01 ask 0.02 sell_yes @ 0.01 | margin 0.4130 | 227 min, 817 hits | fresh bbo 0.01/0.02 depth 1/18 | score 60-88 Q4
- **lag_k_settled** football — North Alabama vs. Central Arkansas — bid 0.99 ask - sell_yes @ 0.995 | margin 0.9947 | 212 min, 757 hits | fresh bbo 0.99/- depth 13/0 | score 14-9 FT
- **lag_k_settled** esports — SEIJI ESPORTS vs. ZANSIDE GAMING — bid 0.20 ask 0.30 sell_yes @ 0.2 | margin 0.1985 | 120 min, 485 hits | fresh bbo 0.20/0.30 depth 7/8 | score - NS
- **lag_k_settled** soccer — Al Shabab Saudi Club vs. Al Ahli Saudi Club — bid 0.51 ask 0.52 sell_yes @ 0.51 | margin 0.5027 | 120 min, 479 hits | fresh bbo 0.51/0.52 depth 20/23 | score 1-0 19'
- **lag_k_settled** soccer — Al Shabab Saudi Club vs. Al Ahli Saudi Club — bid 0.23 ask 0.24 sell_yes @ 0.23 | margin 0.2273 | 120 min, 479 hits | fresh bbo 0.23/0.24 depth 19/60 | score 1-0 19'
- **lag_k_settled** soccer — Al Shabab Saudi Club vs. Al Ahli Saudi Club — bid 0.24 ask 0.25 buy_yes @ 0.25 | margin 0.7370 | 120 min, 479 hits | fresh bbo 0.24/0.25 depth 11/27 | score 1-0 19'
- **lag_k_settled** esports — BC.Game Esports vs. Metizport — bid 0.06 ask 0.18 sell_yes @ 0.06 | margin 0.9573 | 120 min, 477 hits | fresh bbo 0.15/0.25 depth 6/21 | score 1-1 Map 3
- **lag_k_settled** darts — Scott Campbell vs. Andy Baetens — bid 0.28 ask 0.37 buy_yes @ 0.37 | margin 0.9786 | 105 min, 447 hits | fresh bbo 0.28/0.37 depth 6/7 | score 0-0 
- **lag_k_settled** esports — Nova Esports vs. Any Questions Gaming — bid 0.96 ask - sell_yes @ 0.96 | margin 0.9573 | 61 min, 460 hits | fresh bbo 0.96/- depth 19/0 | score 1-0 Map 2
- **implication_k** 🔒  — 26OCT30DENPHX — | margin 0.1008 | 135 min, 358 hits | score - 
- **implication_k** 🔒  — 26OCT30DENPHX — | margin 0.1249 | 135 min, 358 hits | score - 
- **implication_k** 🔒  — 26OCT30DENPHX — | margin 0.1304 | 135 min, 358 hits | score - 
- **implication_k** 🔒  — 26OCT30DENPHX — | margin 0.1259 | 135 min, 358 hits | score - 
- **implication_k** 🔒  — 26OCT30DENPHX — | margin 0.1196 | 135 min, 358 hits | score - 
- **implication_k** 🔒  — 26OCT30DENPHX — | margin 0.1138 | 135 min, 358 hits | score - 
- **implication_k** 🔒  — 26OCT30DENPHX — | margin 0.1095 | 135 min, 358 hits | score - 
- **implication_k** 🔒  — 26OCT30DENPHX — | margin 0.1273 | 135 min, 356 hits | score - 
- **implication_k** 🔒  — 26OCT30DENPHX — | margin 0.1168 | 134 min, 341 hits | score - 
- **implication_k** 🔒  — 26OCT30DENPHX — | margin 0.0750 | 131 min, 342 hits | score - 
- **lag_k_settled** darts — Scott Robertson vs. Andy Baetens — bid 0.04 ask 0.20 sell_yes @ 0.04 | margin 0.5127 | 95 min, 377 hits | fresh bbo 0.04/0.20 depth 3/2 | score 2-3 LIVE
- **lag_k_settled** esports — World Squad vs. CIS Squad — bid - ask 0.01 buy_yes @ 0.01 | margin 0.9893 | 77 min, 390 hits | fresh bbo -/0.01 depth 0/13 | score 0-0 Game 1
- **lag_k_settled** soccer — AC Milan vs. FC Internazionale Milano — bid 0.44 ask 0.45 sell_yes @ 0.44 | margin 0.7163 | 108 min, 353 hits | fresh bbo 0.44/0.45 depth 25/33 | score 2-1 1H
- **lag_k_settled** soccer — AC Milan vs. FC Internazionale Milano — bid 0.26 ask 0.27 sell_yes @ 0.26 | margin 0.2563 | 108 min, 353 hits | fresh bbo 0.26/0.27 depth 23/55 | score 2-1 1H

## Live paper trades (no orders; Kalshi prices, taker fees)

Ledger L2-2026-11-01 (earlier ledgers excluded: L1)

**Total closed P&L: $-344.91 on $1078.91 staked (-32.0%)**

| rule | entries | closed | winners | staked | P&L | ROI |
|---|---|---|---|---|---|---|
| R1 anchor [ncaaf] | 26 | 26 | 11 | $262.99 | $-34.99 | -13% |
| R1 anchor [nfl] | 3 | 2 | 1 | $20.30 | $-1.30 | -6% |
| R2 q1cheap [ncaaf] | 37 | 37 | 2 | $194.50 | $-142.50 | -73% |
| R2 q1cheap [nfl] | 5 | 2 | 0 | $10.50 | $-10.50 | -100% |
| R3 blowout [ncaaf] | 16 | 16 | 1 | $339.32 | $-197.32 | -58% |
| R4 halftime [ncaaf] | 19 | 19 | 6 | $95.24 | $+9.76 | +10% |
| R6 decided [other] | 10 | 8 | 8 | $156.05 | $+31.95 | +20% |

| time (UTC) | rule | game | team | entry | contracts | why | result |
|---|---|---|---|---|---|---|---|
| 20:27 | R6 decided | LV Raiders vs. NY Jets | Both teams to score in every quarter | 0.78 | 25 | both scored 35-30 | kalshi settled: 1.00, $+5.20 |
| 18:48 | R1 anchor | MIN Vikings vs. DET Lions | Minnesota | 0.45 | 22 | pregame dog (mid 0.38) leads 6-3 in Q2, ask 0.45 | final score (pending Kalshi settlement): 0.00, $-10.28 |
| 18:46 | R1 anchor | TEN Titans vs. CIN Bengals | Tennessee | 0.35 | 28 | pregame dog (mid 0.12) leads 13-0 in Q2, ask 0.35 | open |
| 18:41 | R1 anchor | LV Raiders vs. NY Jets | Las Vegas | 0.51 | 19 | pregame dog (mid 0.47) leads 7-6 in Q2, ask 0.51 | final score (pending Kalshi settlement): 1.00, $+8.98 |
| 18:31 | R2 q1cheap | ARI Cardinals vs. DAL Cowboy | Arizona | 0.17 | 29 | Q1 ask 0.17, score 0-0 | open |
| 18:24 | R2 q1cheap | CLE Browns vs. PIT Steelers | Cleveland | 0.20 | 25 | Q1 ask 0.20, score 0-0 | final score (pending Kalshi settlement): 0.00, $-5.28 |
| 18:17 | R2 q1cheap | BAL Ravens vs. BUF Bills | Baltimore | 0.20 | 25 | Q1 ask 0.20, score 0-7 | open |
| 18:07 | R2 q1cheap | TEN Titans vs. CIN Bengals | Tennessee | 0.15 | 33 | Q1 ask 0.15, score 0-0 | open |
| 18:03 | R2 q1cheap | IND Colts vs. JAC Jaguars | Indianapolis | 0.19 | 26 | Q1 ask 0.19, score 0-0 | final score (pending Kalshi settlement): 0.00, $-5.22 |
| 16:06 | R6 decided | Adolfo Daniel Vallejo vs. Lo | Lorenzo Sonego | 0.67 | 29 | ended 3-6, 6-4, 6-7(5-7) | kalshi settled: 1.00, $+9.12 |
| 15:39 | R6 decided | Rocco Valente vs. Ryo Tabata | Ryo Tabata | 0.99 | 20 | ended 2-6, 6-3, 3-6 | kalshi settled: 1.00, $+0.19 |
| 09:26 | R6 decided | Lilli Tagger vs. Harriet Dar | Lilli Tagger | 0.96 | 18 | set 1 final 6-4 | kalshi settled: 1.00, $+0.67 |
| 05:20 | R3 blowout | Oregon State vs. Fresno Stat | Oregon St. | 0.09 | 222 | down 22 in Q3, ask 0.09 | final score (pending Kalshi settlement): 0.00, $-21.25 |
| 04:34 | R3 blowout | Texas State vs. Boise State | Texas St. | 0.08 | 250 | down 18 in Q3, ask 0.08 | final score (pending Kalshi settlement): 0.00, $-21.29 |
| 03:51 | R1 anchor | Oregon State vs. Fresno Stat | Fresno St. | 0.35 | 28 | pregame dog (mid 0.33) leads 3-7 in Q2, ask 0.35 | final score (pending Kalshi settlement): 1.00, $+17.75 |
| 03:12 | R1 anchor | Northern Illinois vs. UNLV | Northern Illinois | 0.38 | 26 | pregame dog (mid 0.07) leads 14-10 in Q2, ask 0.38 | final score (pending Kalshi settlement): 0.00, $-10.31 |
| 02:37 | R6 decided | Texas Stars vs. Chicago Wolv | Over 2.5 goals scored | 0.85 | 23 | score 3-4 total 7 > 2.5 | kalshi settled: 1.00, $+3.24 |
| 02:33 | R2 q1cheap | Northern Illinois vs. UNLV | Northern Illinois | 0.08 | 62 | Q1 ask 0.08, score 0-0 | final score (pending Kalshi settlement): 0.00, $-5.28 |
| 02:29 | R4 halftime | Grambling State vs. Texas So | Texas Southern | 0.33 | 15 | Grambling St. rose +0.120 at halftime; fade it | final score (pending Kalshi settlement): 1.00, $+9.82 |
| 02:21 | R2 q1cheap | Texas State vs. Boise State | Texas St. | 0.19 | 26 | Q1 ask 0.19, score 0-0 | final score (pending Kalshi settlement): 0.00, $-5.22 |
| 02:06 | R4 halftime | Lamar vs. UT Rio Grande Vall | UT Rio Grande Valley | 0.03 | 166 | Lamar rose +0.065 at halftime; fade it | final score (pending Kalshi settlement): 0.00, $-5.32 |
| 01:53 | R3 blowout | Ohio State vs. USC | Ohio St. | 0.11 | 181 | down 17 in Q3, ask 0.11 | final score (pending Kalshi settlement): 0.00, $-21.15 |
| 01:13 | R1 anchor | Grambling State vs. Texas So | Texas Southern | 0.48 | 20 | pregame dog (mid 0.36) leads 0-3 in Q2, ask 0.48 | final score (pending Kalshi settlement): 1.00, $+10.05 |
| 01:03 | R1 anchor | Eastern Kentucky vs. Tarleto | Eastern Kentucky | 0.39 | 25 | pregame dog (mid 0.11) leads 17-14 in Q3, ask 0.39 | final score (pending Kalshi settlement): 0.00, $-10.17 |
| 00:57 | R4 halftime | Eastern Kentucky vs. Tarleto | Tarleton St. | 0.73 | 6 | Eastern Kentucky rose +0.055 at halftime; fade it | final score (pending Kalshi settlement): 1.00, $+1.54 |
| 00:32 | R6 decided | Texas Stars vs. Chicago Wolv | Over 0.5 goals scored | 0.94 | 21 | score 2-1 total 3 > 0.5 | open |
| 00:32 | R6 decided | Texas Stars vs. Chicago Wolv | Over 1.5 goals scored | 0.75 | 26 | score 2-1 total 3 > 1.5 | open |
| 00:22 | R2 q1cheap | Lamar vs. UT Rio Grande Vall | UT Rio Grande Valley | 0.19 | 26 | Q1 ask 0.19, score 7-3 | final score (pending Kalshi settlement): 0.00, $-5.22 |
| 00:18 | R1 anchor | Ohio State vs. USC | USC | 0.47 | 21 | pregame dog (mid 0.32) leads 3-14 in Q2, ask 0.47 | final score (pending Kalshi settlement): 1.00, $+10.76 |
| 23:53 | R1 anchor | Clemson vs. Florida State | Clemson | 0.39 | 25 | pregame dog (mid 0.35) leads 10-7 in Q2, ask 0.39 | final score (pending Kalshi settlement): 1.00, $+14.83 |
| 23:10 | R2 q1cheap | Eastern Kentucky vs. Tarleto | Eastern Kentucky | 0.13 | 38 | Q1 ask 0.13, score 0-0 | final score (pending Kalshi settlement): 0.00, $-5.24 |
| 22:08 | R4 halftime | Marist vs. San Diego | San Diego | 0.65 | 7 | Marist rose +0.090 at halftime; fade it | kalshi settled: 1.00, $+2.34 |
| 21:59 | R4 halftime | Southeastern Louisiana vs. E | Southeastern Louisiana | 0.70 | 7 | East Texas A&M rose +0.080 at halftime; fade it | kalshi settled: 0.00, $-5.00 |
| 21:43 | R6 decided | SC Cambuur-Leeuwarden vs. Go | Over 3.5 goals scored | 0.97 | 20 | score 4-0 total 4 > 3.5 | kalshi settled: 1.00, $+0.56 |
| 21:34 | R3 blowout | Idaho vs. Portland State | Portland St. | 0.15 | 133 | down 17 in Q2, ask 0.15 | kalshi settled: 0.00, $-21.14 |
| 21:18 | R3 blowout | Northern Arizona vs. Souther | Southern Utah | 0.10 | 200 | down 17 in Q3, ask 0.10 | kalshi settled: 0.00, $-21.26 |
| 21:18 | R4 halftime | Delaware State vs. Norfolk S | Norfolk St. | 0.92 | 5 | Delaware St. rose +0.120 at halftime; fade it | final score (pending Kalshi settlement): 0.00, $-4.63 |
| 21:05 | R3 blowout | Eastern Illinois vs. UT Mart | Tennessee-Martin | 0.16 | 125 | down 18 in Q3, ask 0.16 | kalshi settled: 0.00, $-21.18 |
| 20:50 | R3 blowout | UC Davis vs. Weber State | UC Davis | 0.08 | 250 | down 20 in Q3, ask 0.08 | final score (pending Kalshi settlement): 0.00, $-21.29 |
| 20:49 | R4 halftime | Houston Christian vs. Stephe | Houston Christian | 0.02 | 250 | Stephen F. Austin rose +0.050 at halftime; fade it | kalshi settled: 0.00, $-5.34 |

### Score reaction speed (live, 15 s): share of the 3-minute move done by +15 s / +30 s / +60 s

- 26NOV01MINDET 0-0: 80% / 80% / 50%
- 26NOV01TENCIN 21-23: 0% / 25% / 25%
- 26NOV01TENCIN 21-23: -0% / -0% / 25%
- 26NOV01MINDET 13-12: 0% / 0% / 100%
- 26NOV01MINDET 13-12: -0% / -0% / 100%
- 26NOV01LVNYJ 35-33: -0% / -0% / 12%
- 26NOV01LVNYJ 35-33: 0% / 0% / 13%
- 26NOV01MINDET 15-12: -0% / -0% / -0%
- 26NOV01MINDET 15-12: 0% / 0% / 0%
- 26NOV01TENCIN 27-23: -14% / -14% / -14%
- 26NOV01LVNYJ 38-33: -0% / 109% / 109%
- 26NOV01LVNYJ 38-33: 0% / 110% / 110%
- 26NOV01TENCIN 28-29: 43% / 43% / 57%
- 26NOV01TENCIN 28-29: 33% / 33% / 50%
- 26NOV01ARIDAL 24-27: 0% / 0% / 0%
- 26NOV01ARIDAL 24-27: -0% / -0% / -0%
- 26NOV01TENCIN 34-29: 0% / 0% / 100%
- 26NOV01TENCIN 34-29: -0% / -0% / 120%
- 26NOV01ARIDAL 24-30: -0% / -0% / 17%
- 26NOV01ARIDAL 24-30: 0% / 0% / 15%

## Bot latency map: seconds from the score to Kalshi repricing a decided market

| sport | series | decided | median s to reprice | <= 15 s | <= 60 s | never (closed/timeout) | cheapest ask seen | resting bid @0.97: contracts / $ | @0.99: contracts / $ |
|---|---|---|---|---|---|---|---|---|---|
| soccer | KXELITESERIENTOTAL | 1513 | 782 | 26 | 94 | 0 | - | 0 / $0.00 | 33 / $0.33 |
| soccer | KXIDNSLTOTAL | 1469 | 1144 | 9 | 32 | 0 | 0.96 | 0 / $0.00 | 82 / $0.82 |
| soccer | KXALLSVENSKANTOTAL | 1261 | 891 | 9 | 34 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXEREDIVISIETOTAL | 1183 | 413 | 36 | 120 | 0 | - | 0 / $0.00 | 337 / $3.38 |
| soccer | KXLIGAFTOTAL | 1112 | 1971 | 1 | 12 | 0 | 0.98 | 0 / $0.00 | 0 / $0.00 |
| soccer | KXSERIECTOTAL | 1051 | 1323 | 12 | 41 | 0 | 0.97 | 0 / $0.00 | 165 / $1.65 |
| soccer | KXBELGIANPLTOTAL | 1041 | 458 | 19 | 68 | 0 | 0.89 | 763 / $22.89 | 763 / $7.63 |
| tennis | KXATPSETWINNER | 854 | 46 | 166 | 434 | 0 | - | 0 / $0.00 | 306 / $3.06 |
| soccer | KXAUTBUNDESTOTAL | 846 | 405 | 18 | 70 | 0 | 0.01 | 490 / $14.70 | 523 / $5.23 |
| soccer | KXDENSUPERLIGATOTAL | 773 | 662 | 11 | 44 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| tennis | KXWTASETWINNER | 694 | 46 | 126 | 362 | 0 | - | 0 / $0.00 | 155 / $1.56 |
| soccer | KXTHAIL1TOTAL | 550 | 727 | 4 | 17 | 0 | 0.96 | 0 / $0.00 | 0 / $0.00 |
| soccer | KXHUNNB1TOTAL | 543 | 1882 | 4 | 14 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXBUNDESLIGA2TOTAL | 514 | 258 | 8 | 35 | 0 | - | 0 / $0.00 | 586 / $5.86 |
| tennis | KXATPCHALLENGERMATCH | 490 | 186 | 27 | 90 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXECULPTOTAL | 417 | 1342 | 1 | 5 | 0 | 0.93 | 0 / $0.00 | 0 / $0.00 |
| soccer | KXCZEFNLTOTAL | 277 | 428 | 2 | 12 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXTFF1LIGTOTAL | 252 | 1052 | 3 | 11 | 1 | 0.88 | 1148 / $34.44 | 1148 / $11.48 |
| soccer | KXHNLTOTAL | 251 | 1129 | 2 | 8 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXMYSLTOTAL | 223 | 528 | 2 | 8 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXKLEAGUETOTAL | 192 | 556 | 3 | 12 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| tennis | KXATPEXACTMATCH | 162 | 226 | 6 | 15 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXLALIGA2TOTAL | 152 | 1820 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXLIGAEXPTOTAL | 152 | 1691 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXCZEFLTOTAL | 125 | 409 | 4 | 6 | 0 | 0.47 | 76 / $2.29 | 76 / $0.76 |
| tennis | KXATPMATCH | 116 | 211 | 6 | 18 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| football | KXNFLGAME | 116 | 2566 | 0 | 0 | 0 | - | 0 / $0.00 | 295 / $2.94 |
| soccer | KXCHLLDPTOTAL | 102 | 443 | 2 | 8 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXALLSVENSKANBTTS | 95 | 737 | 1 | 4 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXALLSVENSKANSPREAD | 95 | 468 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXSERIECSPREAD | 76 | 5590 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXBUNDESLIGA2SPREAD | 72 | 228 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXMLSTOTAL | 57 | 1113 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXDENSUPERLIGASPREAD | 38 | 1891 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXSUPERLIGTOTAL | 38 | 378 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXSCOCUPTOTAL | 35 | 2799 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXIDNSLBTTS | 22 | 595 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXEREDIVISIEBTTS | 21 | 167 | 1 | 4 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXBUNDESLIGA2BTTS | 19 | 236 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXSLGREECETOTAL | 19 | 2918 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXEREDIVISIESPREAD | 4 | 763 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXELITESERIENBTTS | 4 | 5122 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXDENSUPERLIGABTTS | 3 | 1100 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| football | KXNFLEQBTTS | 1 | - | 0 | 0 | 1 | 0.54 | 10 / $0.30 | 10 / $0.10 |

Latency counts from when OUR score feed changed (Polymarket's feed lags reality, so true bot speed is faster). Resting-bid columns: contracts that sellers dumped below that price after the decision, and the profit a resting bid there would have made (maker fee ignored).

## Decided-state engine (contracts the live score already settled, still trading)

2864 contracts decided while active; 868 had a price leaving > 0.4c after fees; 722 of those were mispriced AFTER the score was stable (lock tier)

| sport | game | contract | decided | reason | max margin | mispriced for | lock margin | lock depth |
|---|---|---|---|---|---|---|---|---|
| ice-hockey | UTA Mammoth vs. PIT Penguins | KXNHL2PTOTAL-26OCT29UTAPIT-3 | YES | score 2-1 total 3 > 2.5 | 0.989 | 1496s | 0.989 | 4410 |
| ice-hockey | UTA Mammoth vs. PIT Penguins | KXNHL2PTOTAL-26OCT29UTAPIT-2 | YES | score 2-1 total 3 > 1.5 | 0.989 | 1496s | 0.989 | 2532 |
| ice-hockey | CBJ Blue Jackets vs. CAR Hurrica | KXNHL2PTOTAL-26OCT29CBJCAR-2 | YES | score 0-2 total 2 > 1.5 | 0.989 | 1189s | 0.989 | 1318 |
| ice-hockey | WPG Jets vs. TBL Lightning | KXNHL2PTOTAL-26OCT29WPGTB-5 | YES | score 1-5 total 6 > 4.5 | 0.989 | 832s | 0.989 | 3384 |
| basketball | CLE Cavaliers vs. ATL Hawks | KXNBA1QTOTAL-26OCT29CLEATL-51 | YES | score 35-27 total 62 > 50.5 | 0.989 | 271s | 0.989 | 22419 |
| basketball | CLE Cavaliers vs. ATL Hawks | KXNBA1QTOTAL-26OCT29CLEATL-49 | YES | score 35-27 total 62 > 48.5 | 0.989 | 271s | 0.989 | 15273 |
| basketball | CLE Cavaliers vs. ATL Hawks | KXNBA1QTOTAL-26OCT29CLEATL-47 | YES | score 35-27 total 62 > 46.5 | 0.989 | 271s | 0.989 | 14103 |
| basketball | SAC Kings vs. NO Pelicans | KXNBA1QTOTAL-26OCT29SACNOP-64 | YES | score 50-50 total 100 > 63.5 | 0.989 | 877s | 0.989 | 3409 |
| basketball | SAC Kings vs. NO Pelicans | KXNBA1QTOTAL-26OCT29SACNOP-62 | YES | score 50-50 total 100 > 61.5 | 0.989 | 877s | 0.989 | 3957 |
| basketball | SAC Kings vs. NO Pelicans | KXNBA1QTOTAL-26OCT29SACNOP-60 | YES | score 50-50 total 100 > 59.5 | 0.989 | 877s | 0.989 | 7982 |
| basketball | SAC Kings vs. NO Pelicans | KXNBA1QTOTAL-26OCT29SACNOP-58 | YES | score 50-50 total 100 > 57.5 | 0.989 | 877s | 0.989 | 1353 |
| basketball | SAC Kings vs. NO Pelicans | KXNBA1QTOTAL-26OCT29SACNOP-56 | YES | score 50-50 total 100 > 55.5 | 0.989 | 877s | 0.989 | 261 |
| basketball | CLE Cavaliers vs. ATL Hawks | KXNBA1QTOTAL-26OCT29CLEATL-53 | YES | score 35-27 total 62 > 52.5 | 0.989 | 254s | 0.989 | 22011 |
| basketball | SAC Kings vs. NO Pelicans | KXNBA1QTOTAL-26OCT29SACNOP-66 | YES | score 50-50 total 100 > 65.5 | 0.989 | 830s | 0.989 | 4297 |
| basketball | SAC Kings vs. NO Pelicans | KXNBA1QTOTAL-26OCT29SACNOP-68 | YES | score 50-50 total 100 > 67.5 | 0.989 | 785s | 0.989 | 3293 |
| ice-hockey | CHI Blackhawks vs. DET Red Wings | KXNHL2PTOTAL-26OCT29CHIDET-2 | YES | score 1-1 total 2 > 1.5 | 0.989 | 1367s | 0.989 | 5464 |
| basketball | SAC Kings vs. NO Pelicans | KXNBA1QTOTAL-26OCT29SACNOP-70 | YES | score 50-50 total 100 > 69.5 | 0.989 | 725s | 0.989 | 3436 |
| basketball | SAC Kings vs. NO Pelicans | KXNBA1QTOTAL-26OCT29SACNOP-72 | YES | score 50-50 total 100 > 71.5 | 0.989 | 695s | 0.989 | 1350 |
| basketball | SAC Kings vs. NO Pelicans | KXNBA1QTOTAL-26OCT29SACNOP-74 | YES | score 50-50 total 100 > 73.5 | 0.989 | 634s | 0.989 | 7436 |
| basketball | CLE Cavaliers vs. ATL Hawks | KXNBA2HSPREAD-26OCT29CLEATL-ATL3 | YES | ended 111-114 margin 3 vs 2.5 | 0.989 | 274s | 0.989 | 8180 |
| basketball | CLE Cavaliers vs. ATL Hawks | KXNBA2HSPREAD-26OCT29CLEATL-ATL2 | YES | ended 111-114 margin 3 vs 1.5 | 0.989 | 274s | 0.989 | 8174 |
| basketball | CLE Cavaliers vs. ATL Hawks | KXNBA2HTOTAL-26OCT29CLEATL-140 | YES | score 111-114 total 225 > 139.5 | 0.989 | 274s | 0.989 | 9451 |
| basketball | CLE Cavaliers vs. ATL Hawks | KXNBA2HTOTAL-26OCT29CLEATL-138 | YES | score 111-114 total 225 > 137.5 | 0.989 | 274s | 0.989 | 9079 |
| basketball | CLE Cavaliers vs. ATL Hawks | KXNBA2HTOTAL-26OCT29CLEATL-136 | YES | score 111-114 total 225 > 135.5 | 0.989 | 274s | 0.989 | 7472 |
| basketball | CLE Cavaliers vs. ATL Hawks | KXNBA4QSPREAD-26OCT29CLEATL-CLE4 | NO | ended 111-114 margin -3 vs 3.5 | 0.989 | 274s | 0.989 | 8188 |

## Close / settlement latency (how clunky each venue is after the final whistle)

Kalshi: settlement_ts − close_time per series (negative = settled before the scheduled close)

| series | n | median | p90 |
|---|---|---|---|
| KXESOCCERGAME eSoccer Game | 4077 | 4.0 min | 4.1 min |
| KXNCAAFSPREAD College Football Spread | 2387 | 4.0 min | 4.1 min |
| KXNCAAFTOTAL College Football Total Points | 1733 | 4.0 min | 4.1 min |
| KXNHLGOAL NHL Goalscorer | 1639 | 3.0 min | 3.1 min |
| KXNFLPASSYDSPRECISE Pass Yards Precise | 1297 | 4.0 min | 4.1 min |
| KXNCAAFTEAMTOTAL College Football Team Total Po | 1253 | 4.0 min | 4.1 min |
| KXNHLPTS Pro Hockey Points | 1114 | 3.0 min | 3.1 min |
| KXNBA3PT NBA Player Threes | 1093 | 2.0 min | 2.1 min |
| KXNCAAF1HSPREAD College Football 1st Half Spre | 1092 | 4.0 min | 4.1 min |
| KXNBA3PTPROT NBA Player Threes Protected | 1017 | 2.5 min | 2.6 min |
| KXNBAREB NBA Player Rebounds | 1005 | 2.0 min | 2.1 min |
| KXNBAREBPROT NBA Player Rebounds Protected | 965 | 2.5 min | 2.6 min |
| KXLIGAPROMATCH Russia Liga Pro Match | 946 | 4.0 min | 4.1 min |
| KXNHLFIRSTGOAL NHL First Goal | 895 | 6.0 min | 6.0 min |
| KXNBAPTS NBA Player Points | 884 | 2.0 min | 2.1 min |
| KXNBAPTSPROT NBA Player Points Protected | 842 | 2.5 min | 2.6 min |
| KXNHLAST Pro Hockey Assists | 823 | 6.0 min | 6.1 min |
| KXNBATEAMTOTAL NBA Team Total | 821 | 2.5 min | 2.6 min |
| KXNBAAST NBA Player Assists | 819 | 2.0 min | 2.1 min |
| KXNBAASTPROT NBA Player Assists Protected | 808 | 2.5 min | 2.6 min |
| KXNCAAF1HTOTAL College Football 1st Half Tota | 728 | 4.0 min | 4.1 min |
| KXNCAAF2HSPREAD College Football 2nd Half Spre | 720 | 4.0 min | 4.1 min |
| KXNBASPREAD NBA Spread | 616 | 1.8 min | 1.8 min |
| KXNBATOTAL NBA Total | 612 | 1.8 min | 1.8 min |
| KXEBASKETBALLGAME eBasketball Game | 534 | 4.0 min | 4.1 min |
| KXNCAAF2HTOTAL College Football 2nd Half Tota | 477 | 4.0 min | 4.1 min |
| KXNBA1HTEAMTOTAL NBA 1st Half Team Total | 440 | 2.5 min | 2.6 min |
| KXNBASTL NBA Player Steals | 407 | 2.0 min | 2.1 min |
| KXNBA1HTOTAL NBA 1st Half Total | 380 | 2.5 min | 2.6 min |
| KXNBA1HSPREAD NBA 1st Half Spread | 380 | 2.5 min | 2.6 min |
| KXCS2MAP Counter-Strike 2 Map Winner  | 368 | 3.0 min | 3.0 min |
| KXNCAAF2QTOTAL College Football 2nd Quarter T | 363 | 4.0 min | 4.1 min |
| KXNCAAF3QTOTAL College Football 3rd Quarter T | 363 | 4.0 min | 4.1 min |
| KXNCAAF4QTOTAL College Football 4th Quarter T | 363 | 4.0 min | 4.1 min |
| KXNBA2HTOTAL NBA 2nd Half Total | 361 | 2.5 min | 2.6 min |
| KXNBA2HSPREAD NBA 2nd Half Spread | 361 | 2.5 min | 2.6 min |
| KXBUNDESLIGAGOAL Goalscorer | 361 | 6.0 min | 6.1 min |
| KXNCAAF2QSPREAD College Football 2nd Quarter S | 358 | 4.0 min | 4.1 min |
| KXNBAPRA NBA Player Points + Rebounds + | 356 | 2.5 min | 2.6 min |
| KXEPLGOAL EPL Goalscorer | 356 | 6.0 min | 6.1 min |

## Participant fingerprint (per sport; 60 s snapshots)

change% = share of scan cycles (60 s) where the best quote moved; react = median minutes from a score change to the next quote move (humans: slow, bursty, round sizes; bots: constant cadence, odd/constant sizes, instant reaction)

| venue | sport | markets | snapshots | two-sided | med spread | change% | react (min) | round sizes | med size |
|---|---|---|---|---|---|---|---|---|---|
| pm | soccer | 1770 | 263373 | 87% | 0.020 | 19% | 0.5 (n=4196) | - | - |
| pm | tennis | 1322 | 119163 | 92% | 0.010 | 23% | 0.5 (n=62619) | - | - |
| pm | esports | 3341 | 88136 | 76% | 0.030 | 19% | 0.5 (n=18264) | - | - |
| pm | table-tennis | 1522 | 61768 | 95% | 0.020 | 30% | 0.5 (n=30776) | - | - |
| pm | basketball | 748 | 58346 | 83% | 0.050 | 25% | 0.5 (n=10610) | - | - |
| pm | football | 483 | 30200 | 72% | 0.005 | 17% | 1.1 (n=1093) | - | - |
| pm | climate | 215 | 10748 | 75% | 0.040 | 20% | - (n=0) | - | - |
| pm | ice-hockey | 102 | 10201 | 86% | 0.060 | 15% | 0.7 (n=552) | - | - |
| pm | motorsports | 159 | 7808 | 42% | 0.050 | 13% | - (n=0) | - | - |
| pm | cricket | 9 | 4107 | 95% | 0.030 | 10% | 1.0 (n=600) | - | - |
| pm | misc | 47 | 3778 | 93% | 0.010 | 12% | - (n=0) | - | - |
| pm | golf | 159 | 3733 | 3% | 0.040 | 3% | - (n=0) | - | - |
| pm | beach-volleyball | 57 | 3054 | 86% | 0.010 | 23% | 0.5 (n=1681) | - | - |
| pm | darts | 42 | 1349 | 92% | 0.090 | 28% | 0.5 (n=170) | - | - |
| pm | mma | 14 | 759 | 95% | 0.020 | 4% | - (n=0) | - | - |
| pm | baseball | 2 | 408 | 95% | 0.060 | 22% | 0.5 (n=11) | - | - |
| pm | rugby | 20 | 359 | 73% | 0.450 | 23% | - (n=0) | - | - |
| pm | macro | 83 | 354 | 0% | - | 2% | - (n=0) | - | - |
| pm | boxing | 4 | 165 | 95% | 0.030 | 56% | - (n=0) | - | - |
| pm | pickleball | 13 | 115 | 66% | 0.270 | 11% | - (n=0) | - | - |
| k | KXNCAAFGAME College Football Game | 704 | 646268 | 98% | 0.030 | 1% | - | 8% | 118 |
| k | KXNBA3PT NBA Player Threes | 1132 | 138778 | 82% | 0.080 | 17% | - | 24% | 27 |
| k | KXNFLGAME NFL Game | 58 | 136537 | 100% | 0.010 | 1% | - | 3% | 126998 |
| k | KXCS2MAP Counter-Strike 2 Map Win | 484 | 106693 | 93% | 0.510 | 6% | - | 19% | 110 |
| k | KXNCAAFTEAMTOTAL College Football Team To | 1319 | 103824 | 84% | 0.020 | 2% | - | 27% | 230 |
| k | KXNCAAFSPREAD College Football Spread | 2707 | 79139 | 62% | 0.040 | 3% | - | 16% | 129 |
| k | KXNBAAST NBA Player Assists | 974 | 71565 | 82% | 0.070 | 16% | - | 25% | 23 |
| k | KXNBAPTS NBA Player Points | 970 | 68885 | 80% | 0.050 | 22% | - | 22% | 39 |
| k | KXESOCCERGAME eSoccer Game | 4371 | 68387 | 26% | 0.500 | 6% | - | 24% | 22 |
| k | KXNBAREB NBA Player Rebounds | 1052 | 67441 | 79% | 0.090 | 19% | - | 21% | 35 |
| k | KXNHLGOAL NHL Goalscorer | 1639 | 56021 | 55% | 0.070 | 13% | - | 23% | 50 |
| k | KXNCAAFTOTAL College Football Total P | 1942 | 52914 | 59% | 0.170 | 5% | - | 18% | 132 |
| k | KXNBA3PTPROT NBA Player Threes Protec | 1087 | 50382 | 37% | 0.150 | 2% | - | 19% | 37 |
| k | KXNCAAF1H College Football 1st Hal | 1056 | 43337 | 90% | 0.760 | 1% | - | 31% | 200 |
| k | KXNBA1HTEAMTOTAL NBA 1st Half Team Total | 484 | 39695 | 61% | 0.270 | 12% | - | 22% | 90 |
| k | KXNCAAF1HSPREAD College Football 1st Hal | 1106 | 35085 | 60% | 0.040 | 3% | - | 32% | 180 |
| k | KXNBA1HTOTAL NBA 1st Half Total | 418 | 33036 | 71% | 0.040 | 9% | - | 24% | 100 |
| k | KXNBA1HSPREAD NBA 1st Half Spread | 418 | 31793 | 71% | 0.040 | 8% | - | 17% | 122 |
| k | KXATPSETWINNER ATP Set Winner | 220 | 31758 | 92% | 0.030 | 4% | - | 11% | 175 |
| k | KXNBAREBPROT NBA Player Rebounds Prot | 1005 | 26865 | 30% | 0.170 | 4% | - | 18% | 50 |
| k | KXNBAASTPROT NBA Player Assists Prote | 941 | 26518 | 32% | 0.140 | 2% | - | 22% | 100 |
| k | KXNFLRECYDS Pro Football Receiving Y | 1382 | 25761 | 91% | 0.040 | 6% | - | 32% | 100 |
| k | KXNBA2HSPREAD NBA 2nd Half Spread | 380 | 24593 | 75% | 0.130 | 25% | - | 28% | 192 |
| k | KXWTASETWINNER WTA Set Winner | 272 | 24533 | 74% | 0.040 | 4% | - | 25% | 114 |
| k | KXLIGAMXSCORE Correct Score | 270 | 23806 | 55% | 0.020 | 3% | - | 13% | 799 |
| k | KXNBA2HTOTAL NBA 2nd Half Total | 380 | 23624 | 76% | 0.160 | 23% | - | 25% | 105 |
| k | KXNBAPTSPROT NBA Player Points Protec | 873 | 22624 | 33% | 0.430 | 2% | - | 17% | 162 |
| k | KXNCAAF1HTOTAL College Football 1st Hal | 728 | 22316 | 58% | 0.040 | 4% | - | 17% | 110 |
| k | KXNBA2QSPREAD NBA 2nd Quarter Spread | 260 | 19633 | 72% | 0.050 | 8% | - | 18% | 162 |
| k | KXATPCHALLENGERMATCH Challenger ATP  | 252 | 19621 | 87% | 0.010 | 8% | - | 5% | 622 |
| k | KXNEXTTEAMNHL Next Team NHL | 230 | 18860 | 0% | 0.130 | 0% | - | 23% | 341 |
| k | KXNBA2QTOTAL NBA 2nd Quarter Total | 260 | 18302 | 70% | 0.060 | 8% | - | 35% | 174 |
| k | KXNBAPRA NBA Player Points + Rebo | 363 | 16598 | 67% | 0.310 | 19% | - | 10% | 8 |
| k | KXNBA3QSPREAD NBA 3rd Quarter Spread | 260 | 16403 | 74% | 0.050 | 9% | - | 35% | 150 |
| k | KXNBA1QTOTAL NBA 1st Quarter Total | 260 | 16318 | 66% | 0.050 | 9% | - | 22% | 140 |
| k | KXNFLREC Pro Football Player Rece | 851 | 16126 | 81% | 0.040 | 6% | - | 29% | 100 |
| k | KXNBA1QSPREAD NBA 1st Quarter Spread | 260 | 16077 | 65% | 0.050 | 7% | - | 28% | 150 |
| k | KXNHLFIRSTGOAL NHL First Goal | 935 | 15891 | 19% | 0.020 | 4% | - | 14% | 101 |
| k | KXNBASTL NBA Player Steals | 425 | 14541 | 65% | 0.290 | 15% | - | 13% | 1 |
| k | KXNBA3QTOTAL NBA 3rd Quarter Total | 260 | 14530 | 72% | 0.050 | 9% | - | 35% | 145 |

## Schema notes (raw keys seen)

- polymarket: active, archived, category, chatChannel, closed, combos, createdAt, description, elapsed, endDate, ended, eventState, featureAvailability, fixtureId, gameId, hidden, id, insiderTradingRules, live, marketCounts, marketGroups, markets, metadata, participants, payoutEstimateMessage, payoutEstimateTime, period, primaryTag, score, seriesSlug, slug, sortType, sportradarGameId, startDate, startTime, streamProvider, streamRequiresAuth, tags, teams, ticker, title, updatedAt
- kalshi: can_close_early, close_time, created_time, custom_strike, early_close_condition, event_ticker, exchange_index, expected_expiration_time, expiration_time, expiration_value, last_price_dollars, latest_expiration_time, market_type, no_ask_dollars, no_bid_dollars, no_sub_title, notional_value_dollars, occurrence_datetime, open_interest_fp, open_time, previous_price_dollars, previous_yes_ask_dollars, previous_yes_bid_dollars, price_level_structure, price_ranges, primary_participant_key, result, rules_primary, rules_secondary, settlement_bounds_type, settlement_timer_seconds, settlement_value_dollars, status, strike_type, ticker, title, updated_time, volume_24h_fp, volume_fp, yes_ask_dollars, yes_ask_size_fp, yes_bid_dollars, yes_bid_size_fp, yes_sub_title

