# Mr. P — sports radar

Updated 2026-11-02T00:32:14Z by `run-20261101T2008-41326096177` (last 7 days). Read-only scanner of every sports market on Polymarket US and Kalshi — it never places orders.
Kit: `mrp/mrp_sports_radar.py` on the `mrp` branch. Raw tape: `mrp/radar/<run>/`.

# Sports radar report

records 4,839,809 | 2026-10-30 00:30Z → 00:30Z | runs 17 | pairs matched 1451 | errors {'radar': 19, 'sp.k.series_poll:KXATPEXACTMATCH': 10, 'sp.k.series_poll:KXATPMATCH': 10, 'sp.k.series_poll:KXATPSETWINNER': 10, 'sp.k.series_poll:KXAUTBUNDESTOTAL': 4, 'sp.k.series_poll:KXEFLL11H': 6, 'sp.k.series_poll:KXEFLL11HSPREAD': 10, 'sp.k.series_poll:KXHNLTOTAL': 6, 'sp.k.series_poll:KXLALIGABTTS': 9, 'sp.k.series_poll:KXLALIGASCORE': 6, 'sp.k.series_poll:KXLALIGASPREAD': 8, 'sp.k.always:KXNFLGAME': 6, 'sp.k.series_poll:KXATPCHALLENGERMATCH': 7, 'sp.k.series_poll:KXEFLL11HBTTS': 10, 'sp.k.series_poll:KXLALIGA2H': 6, 'sp.k.series_poll:KXCS2MAP': 6, 'sp.k.series_poll:KXEFLL11HTOTAL': 8, 'sp.k.series_poll:KXLALIGA2HBTTS': 8, 'sp.k.series_poll:KXLALIGA2HSPREAD': 6, 'sp.k.series_poll:KXLALIGA2HTOTAL': 4, 'sp.k.series_poll:KXLALIGACORNERS': 8, 'sp.k.series_poll:KXLALIGAGAME': 6, 'sp.k.series_poll:KXLALIGAGOAL': 6, 'sp.k.series_poll:KXAUTBUNDESGAME': 2, 'sp.k.series_poll:KXCZEFLTOTAL': 7, 'sp.k.series_poll:KXELITESERIENTOTAL': 2, 'sp.k.series_poll:KXEREDIVISIETOTAL': 2, 'sp.k.always:KXNCAAFGAME': 7, 'sp.k.series_poll:KXLIGUE11HBTTS': 3, 'sp.k.series_poll:KXLIGUE11HSCORE': 4, 'sp.k.series_poll:KXLIGUE11H': 4, 'sp.k.series_poll:KXLIGUE11HSPREAD': 1}

## Catalogue (latest inventory, 23:11Z)

Polymarket US sports events 4504 of 5992 active events; Kalshi near-term sports markets 7000 in 714 events; calls so far {'pm': 2572, 'k': 21513}; MB {'pm': 2961702497, 'k': 4689407579}

| venue | sport / league / type | markets | two-sided | med spread | vol 24h |
|---|---|---|---|---|---|
| pm | football / nfl / futures | 4117 | 61% | 0.010 | 0 |
| pm | football / cfb / futures | 1608 | 79% | 0.010 | 0 |
| pm | basketball / nba / futures | 1422 | 59% | 0.020 | 0 |
| pm | ice-hockey / nhl / futures | 779 | 97% | 0.010 | 0 |
| pm | basketball / wcbb / basketball_team_full_game_winner | 653 | 34% | 0.430 | 0 |
| pm | basketball / cbb / basketball_team_full_game_winner | 635 | 27% | 0.030 | 0 |
| k | KXNCAAFGAME / College Football Game | 484 | 100% | 0.090 | 663048 |
| pm | golf / worlwide / futures | 469 | 25% | 0.499 | 0 |
| pm | soccer / epl / futures | 435 | 86% | 0.010 | 0 |
| pm | basketball / cbb / futures | 317 | 85% | 0.010 | 0 |
| pm | tennis / utr / tennis_match_winner | 288 | 19% | 0.430 | 0 |
| pm | soccer / ucl / futures | 276 | 77% | 0.010 | 0 |
| pm | table-tennis / setkameua / table_tennis_match_winner | 268 | 79% | 0.170 | 0 |
| pm | baseball / mlb / futures | 264 | 25% | 0.001 | 0 |
| pm | football / cfb / football_team_full_game_winner | 211 | 86% | 0.075 | 0 |
| pm | tennis / itfme / tennis_match_winner | 175 | 21% | 0.400 | 0 |
| pm | macro /  / futures | 150 | 73% | 0.010 | 0 |
| pm | soccer / lal / futures | 146 | 66% | 0.010 | 0 |
| pm | boxing / boxing / futures | 145 | 0% | - | 0 |
| pm | mma / ufc / futures | 142 | 80% | 0.010 | 0 |
| pm | tennis / itfwo / tennis_match_winner | 134 | 45% | 0.050 | 0 |
| pm | tennis / atp / tennis_match_winner | 121 | 70% | 0.030 | 0 |
| pm | basketball / nba / basketball_team_full_game_winner | 108 | 73% | 0.270 | 0 |
| pm | tennis / atp / futures | 107 | 40% | 0.010 | 0 |
| pm | soccer / sea / futures | 86 | 83% | 0.010 | 0 |
| pm | tennis / wta / futures | 79 | 42% | 0.020 | 0 |
| pm | soccer / bun / futures | 79 | 82% | 0.010 | 0 |
| pm | soccer / lg1 / futures | 77 | 83% | 0.010 | 0 |
| pm | golf / vidamexi / futures | 66 | 2% | 0.001 | 0 |
| pm | tennis / wta / tennis_match_winner | 62 | 74% | 0.010 | 0 |
| pm | soccer / j2 / soccer_team_full_time_winner | 60 | 67% | 0.030 | 0 |
| pm | tennis / atpdb / tennis_match_winner | 60 | 20% | 0.415 | 0 |
| k | KXMLSGAME / Major League Soccer Game | 60 | 100% | 0.010 | 2027705 |
| pm | soccer / uecl / soccer_team_full_time_winner | 55 | 98% | 0.030 | 0 |
| pm | table-tennis / czechligapro / table_tennis_match_winner | 55 | 20% | 0.390 | 0 |
| pm | soccer / ucl / soccer_team_full_time_winner | 54 | 100% | 0.010 | 0 |
| pm | soccer / uel / soccer_team_full_time_winner | 54 | 100% | 0.020 | 0 |
| pm | soccer / mls / futures | 53 | 85% | 0.010 | 0 |
| k | KXMLSGOAL / Goalscorer | 53 | 100% | 0.890 | 15549 |
| pm | golf / masttour / futures | 52 | 100% | 0.499 | 0 |
| pm | soccer / acle / soccer_team_full_time_winner | 48 | 60% | 0.020 | 0 |
| pm | table-tennis / setkamecz / table_tennis_match_winner | 48 | 62% | 0.170 | 0 |
| k | KXATPCHALLENGERMATCH / Challenger ATP  | 46 | 100% | 0.010 | 874134 |
| k | KXMLS1HSCORE / 1st Half Correct Score | 45 | 100% | 0.020 | 1248 |
| pm | technology /  / futures | 42 | 74% | 0.010 | 0 |
| k | KXNFLGAME / NFL Game | 40 | 100% | 0.010 | 33035220 |
| pm | motorsports / f1 / futures | 38 | 34% | 0.011 | 0 |
| pm | soccer / lmx / futures | 36 | 19% | 0.060 | 0 |
| pm | soccer / uel / futures | 36 | 3% | 0.160 | 0 |
| pm | soccer / uecl / futures | 36 | 0% | - | 0 |
| pm | soccer / sea / soccer_team_full_time_winner | 36 | 100% | 0.010 | 0 |
| pm | soccer / ekst / soccer_team_full_time_winner | 36 | 61% | 0.055 | 0 |
| pm | soccer / serca / soccer_team_full_time_winner | 36 | 44% | 0.480 | 0 |
| pm | soccer / eflch / soccer_team_full_time_winner | 36 | 100% | 0.020 | 0 |
| pm | esports / ebattlesefsa / efootball_team_full_time_winner | 36 | 94% | 0.010 | 0 |
| pm | esports / ebattlesefpl / efootball_team_full_time_winner | 36 | 92% | 0.010 | 0 |
| pm | table-tennis / setkamemd / table_tennis_match_winner | 35 | 6% | 0.010 | 0 |
| pm | football / nfl / football_team_full_game_winner | 33 | 70% | 0.013 | 0 |
| pm | soccer / lal / soccer_team_full_time_winner | 33 | 100% | 0.010 | 0 |
| pm | soccer / epl / soccer_team_full_time_winner | 33 | 100% | 0.010 | 0 |

## Opportunities

| kind | distinct | hits | max margin $/contract | max persistence | fresh-BBO still open |
|---|---|---|---|---|---|
| decided_k | 869 | 67596 | 0.9893 | 169 min | 0/0 |
| decided_pm | 23 | 488 | 0.9947 | 28 min | 182/488 |
| decided_pm_closed | 14 | 144 | 0.9893 | 30 min | 0/144 |
| dutch_k | 15 | 353 | 0.0817 | 140 min | 0/0 |
| dutch_k_sell | 3 | 6 | 0.0107 | 0 min | 0/0 |
| dutch_pm | 66 | 3067 | 0.5316 | 50 min | 0/0 |
| implication_k | 7975 | 464980 | 0.9786 | 141 min | 0/0 |
| lag_k_settled | 188 | 31715 | 0.9973 | 273 min | 26152/30694 |
| lag_k_settled_closed | 157 | 2392 | 0.9973 | 272 min | 0/2392 |

Top by persistence × hits:

- **lag_k_settled** esports — BILIBILI GAMING vs. Hanwha Life Esports — bid 0.42 ask 0.43 buy_yes @ 0.43 | margin 0.5732 | 117 min, 1186 hits | fresh bbo 0.42/0.43 depth 12/14 | score - NS
- **lag_k_settled** basketball — Ulm Basketball vs. Baskets Oldenburg — bid 0.99 ask - sell_yes @ 0.99 | margin 0.9893 | 273 min, 941 hits | score 81-65 FT
- **lag_k_settled** basketball — Basketball Lowen Braunschweig vs. Wurzburg Baskets — bid 0.01 ask 0.02 sell_yes @ 0.01 | margin 0.4130 | 227 min, 817 hits | fresh bbo 0.01/0.02 depth 1/18 | score 60-88 Q4
- **lag_k_settled** football — North Alabama vs. Central Arkansas — bid 0.99 ask - sell_yes @ 0.995 | margin 0.9947 | 212 min, 757 hits | fresh bbo 0.99/- depth 13/0 | score 14-9 FT
- **lag_k_settled** basketball — Grambling State vs. Northern Illinois — bid 0.25 ask 0.28 sell_yes @ 0.25 | margin 0.2466 | 223 min, 521 hits | fresh bbo 0.24/0.25 depth 7/15 | score - NS
- **lag_k_settled** esports — SEIJI ESPORTS vs. ZANSIDE GAMING — bid 0.20 ask 0.30 sell_yes @ 0.2 | margin 0.1985 | 120 min, 485 hits | fresh bbo 0.20/0.30 depth 7/8 | score - NS
- **lag_k_settled** soccer — Al Shabab Saudi Club vs. Al Ahli Saudi Club — bid 0.51 ask 0.52 sell_yes @ 0.51 | margin 0.5027 | 120 min, 479 hits | fresh bbo 0.51/0.52 depth 20/23 | score 1-0 19'
- **lag_k_settled** soccer — Al Shabab Saudi Club vs. Al Ahli Saudi Club — bid 0.23 ask 0.24 sell_yes @ 0.23 | margin 0.2273 | 120 min, 479 hits | fresh bbo 0.23/0.24 depth 19/60 | score 1-0 19'
- **lag_k_settled** soccer — Al Shabab Saudi Club vs. Al Ahli Saudi Club — bid 0.24 ask 0.25 buy_yes @ 0.25 | margin 0.7370 | 120 min, 479 hits | fresh bbo 0.24/0.25 depth 11/27 | score 1-0 19'
- **lag_k_settled** esports — BC.Game Esports vs. Metizport — bid 0.06 ask 0.18 sell_yes @ 0.06 | margin 0.9573 | 120 min, 477 hits | fresh bbo 0.15/0.25 depth 6/21 | score 1-1 Map 3
- **decided_k** 🔒 football — NE Patriots vs. MIA Dolphins — buy_yes @ 0.77 | margin 0.2756 | 169 min, 418 hits | score 24-19 Q4
- **decided_k** 🔒 football — NE Patriots vs. MIA Dolphins — buy_yes @ 0.92 | margin 0.1031 | 169 min, 418 hits | score 24-19 Q4
- **decided_k** 🔒 football — NE Patriots vs. MIA Dolphins — buy_yes @ 0.99 | margin 0.0280 | 169 min, 418 hits | score 24-19 Q4
- **decided_k** 🔒 football — NE Patriots vs. MIA Dolphins — buy_yes @ 0.77 | margin 0.2659 | 111 min, 441 hits | score 24-13 Q4
- **implication_k** 🔒  — 26NOV01NEMIA — | margin 0.6541 | 101 min, 424 hits | score - 
- **lag_k_settled** esports — Nova Esports vs. Any Questions Gaming — bid 0.96 ask - sell_yes @ 0.96 | margin 0.9573 | 61 min, 460 hits | fresh bbo 0.96/- depth 19/0 | score 1-0 Map 2
- **decided_k** football — NE Patriots vs. MIA Dolphins — buy_yes @ 0.2 | margin 0.8201 | 126 min, 390 hits | score 24-19 Q4
- **decided_k** football — NE Patriots vs. MIA Dolphins — buy_yes @ 0.36 | margin 0.6750 | 126 min, 390 hits | score 24-19 Q4
- **decided_k** football — NE Patriots vs. MIA Dolphins — buy_yes @ 0.56 | margin 0.4825 | 126 min, 390 hits | score 24-19 Q4
- **implication_k** 🔒  — 26OCT30DENPHX — | margin 0.1008 | 135 min, 358 hits | score - 
- **implication_k** 🔒  — 26OCT30DENPHX — | margin 0.1249 | 135 min, 358 hits | score - 
- **implication_k** 🔒  — 26OCT30DENPHX — | margin 0.1304 | 135 min, 358 hits | score - 
- **implication_k** 🔒  — 26OCT30DENPHX — | margin 0.1259 | 135 min, 358 hits | score - 
- **implication_k** 🔒  — 26OCT30DENPHX — | margin 0.1196 | 135 min, 358 hits | score - 
- **implication_k** 🔒  — 26OCT30DENPHX — | margin 0.1138 | 135 min, 358 hits | score - 

## Live paper trades (no orders; Kalshi prices, taker fees)

Ledger L2-2026-11-01 (earlier ledgers excluded: L1)

**Total closed P&L: $-334.56 on $1144.56 staked (-29.2%)**

| rule | entries | closed | winners | staked | P&L | ROI |
|---|---|---|---|---|---|---|
| R1 anchor [ncaaf] | 26 | 26 | 11 | $262.99 | $-34.99 | -13% |
| R1 anchor [nfl] | 4 | 3 | 1 | $30.55 | $-11.55 | -38% |
| R2 q1cheap [ncaaf] | 37 | 37 | 2 | $194.50 | $-142.50 | -73% |
| R2 q1cheap [nfl] | 6 | 5 | 1 | $26.24 | $+2.76 | +11% |
| R3 blowout [ncaaf] | 16 | 16 | 1 | $339.32 | $-197.32 | -58% |
| R4 halftime [ncaaf] | 19 | 19 | 6 | $95.24 | $+9.76 | +10% |
| R6 decided [other] | 16 | 10 | 10 | $195.72 | $+39.28 | +20% |

| time (UTC) | rule | game | team | entry | contracts | why | result |
|---|---|---|---|---|---|---|---|
| 23:01 | R6 decided | Houston Dash vs. Portland Th | Over 0.5 1H goals scored | 0.76 | 26 | 1H (0, 1) > 0.5 | open |
| 22:54 | R6 decided | Houston Dash vs. Portland Th | Over 0.5 goals scored | 0.96 | 20 | score 0-1 total 1 > 0.5 | open |
| 22:24 | R1 anchor | NE Patriots vs. MIA Dolphins | Miami | 0.39 | 25 | pregame dog (mid 0.24) leads 3-6 in Q2, ask 0.39 | open |
| 22:23 | R6 decided | NE Patriots vs. MIA Dolphins | Both Teams To Score | 0.72 | 27 | both scored 3-6 | open |
| 21:40 | R6 decided | NE Patriots vs. MIA Dolphins | Over 2.5 goals scored | 0.71 | 28 | score 3-0 total 3 > 2.5 | open |
| 21:40 | R6 decided | NE Patriots vs. MIA Dolphins | Over 1.5 goals scored | 0.89 | 22 | score 3-0 total 3 > 1.5 | open |
| 21:40 | R6 decided | NE Patriots vs. MIA Dolphins | Over 0.5 goals scored | 0.97 | 20 | score 3-0 total 3 > 0.5 | open |
| 21:29 | R2 q1cheap | NE Patriots vs. MIA Dolphins | Miami | 0.19 | 26 | Q1 ask 0.19, score 0-0 | open |
| 20:27 | R6 decided | LV Raiders vs. NY Jets | Both teams to score in every quarter | 0.78 | 25 | both scored 35-30 | kalshi settled: 1.00, $+5.20 |
| 18:48 | R1 anchor | MIN Vikings vs. DET Lions | Minnesota | 0.45 | 22 | pregame dog (mid 0.38) leads 6-3 in Q2, ask 0.45 | final score (pending Kalshi settlement): 0.00, $-10.28 |
| 18:46 | R1 anchor | TEN Titans vs. CIN Bengals | Tennessee | 0.35 | 28 | pregame dog (mid 0.12) leads 13-0 in Q2, ask 0.35 | final score (pending Kalshi settlement): 0.00, $-10.25 |
| 18:41 | R1 anchor | LV Raiders vs. NY Jets | Las Vegas | 0.51 | 19 | pregame dog (mid 0.47) leads 7-6 in Q2, ask 0.51 | final score (pending Kalshi settlement): 1.00, $+8.98 |
| 18:31 | R2 q1cheap | ARI Cardinals vs. DAL Cowboy | Arizona | 0.17 | 29 | Q1 ask 0.17, score 0-0 | final score (pending Kalshi settlement): 1.00, $+23.78 |
| 18:24 | R2 q1cheap | CLE Browns vs. PIT Steelers | Cleveland | 0.20 | 25 | Q1 ask 0.20, score 0-0 | final score (pending Kalshi settlement): 0.00, $-5.28 |
| 18:17 | R2 q1cheap | BAL Ravens vs. BUF Bills | Baltimore | 0.20 | 25 | Q1 ask 0.20, score 0-7 | final score (pending Kalshi settlement): 0.00, $-5.28 |
| 18:07 | R2 q1cheap | TEN Titans vs. CIN Bengals | Tennessee | 0.15 | 33 | Q1 ask 0.15, score 0-0 | final score (pending Kalshi settlement): 0.00, $-5.24 |
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
| 00:32 | R6 decided | Texas Stars vs. Chicago Wolv | Over 0.5 goals scored | 0.94 | 21 | score 2-1 total 3 > 0.5 | kalshi settled: 1.00, $+1.18 |
| 00:32 | R6 decided | Texas Stars vs. Chicago Wolv | Over 1.5 goals scored | 0.75 | 26 | score 2-1 total 3 > 1.5 | kalshi settled: 1.00, $+6.16 |
| 00:22 | R2 q1cheap | Lamar vs. UT Rio Grande Vall | UT Rio Grande Valley | 0.19 | 26 | Q1 ask 0.19, score 7-3 | final score (pending Kalshi settlement): 0.00, $-5.22 |
| 00:18 | R1 anchor | Ohio State vs. USC | USC | 0.47 | 21 | pregame dog (mid 0.32) leads 3-14 in Q2, ask 0.47 | final score (pending Kalshi settlement): 1.00, $+10.76 |
| 23:53 | R1 anchor | Clemson vs. Florida State | Clemson | 0.39 | 25 | pregame dog (mid 0.35) leads 10-7 in Q2, ask 0.39 | final score (pending Kalshi settlement): 1.00, $+14.83 |
| 23:10 | R2 q1cheap | Eastern Kentucky vs. Tarleto | Eastern Kentucky | 0.13 | 38 | Q1 ask 0.13, score 0-0 | final score (pending Kalshi settlement): 0.00, $-5.24 |
| 22:08 | R4 halftime | Marist vs. San Diego | San Diego | 0.65 | 7 | Marist rose +0.090 at halftime; fade it | kalshi settled: 1.00, $+2.34 |

### Score reaction speed (live, 15 s): share of the 3-minute move done by +15 s / +30 s / +60 s

- 26NOV01TENCIN 34-29: -0% / -0% / 120%
- 26NOV01ARIDAL 24-30: -0% / -0% / 17%
- 26NOV01ARIDAL 24-30: 0% / 0% / 15%
- 26NOV01TENCIN 36-35: 14% / 14% / 7%
- 26NOV01TENCIN 36-35: 7% / 7% / -0%
- 26NOV01TENCIN 36-36: -8% / -8% / -8%
- 26NOV01TENCIN 36-36: -8% / -8% / -8%
- 26NOV01ARIDAL 30-30: 0% / 66% / 79%
- 26NOV01ARIDAL 30-30: -0% / 65% / 78%
- 26NOV01KCDEN 13-6: 125% / 125% / 125%
- 26NOV01KCDEN 7-6: -0% / -0% / -0%
- 26NOV01KCDEN 7-6: 0% / 0% / 0%
- 26NOV01KCDEN 23-13: 100% / 100% / 100%
- 26NOV01KCDEN 24-19: -0% / 50% / 75%
- 26NOV01KCDEN 24-19: 0% / 50% / 50%
- 26NOV01KCDEN 24-21: 67% / 67% / 67%
- 26NOV01KCDEN 24-27: 0% / 0% / -14%
- 26NOV01KCDEN 24-27: -0% / -0% / -20%
- 26NOV01KCDEN 24-28: 0% / 13% / 140%
- 26NOV01KCDEN 24-28: -0% / 12% / 125%

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
| soccer | KXMLSTOTAL | 949 | 856 | 13 | 51 | 4 | 0.82 | 188 / $5.63 | 2253 / $22.54 |
| tennis | KXATPSETWINNER | 854 | 46 | 166 | 434 | 0 | - | 0 / $0.00 | 306 / $3.06 |
| soccer | KXAUTBUNDESTOTAL | 846 | 405 | 18 | 70 | 0 | 0.01 | 490 / $14.70 | 523 / $5.23 |
| soccer | KXDENSUPERLIGATOTAL | 773 | 662 | 11 | 44 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| tennis | KXWTASETWINNER | 694 | 46 | 126 | 362 | 0 | - | 0 / $0.00 | 155 / $1.56 |
| soccer | KXBRASILEIROBTOTAL | 616 | 1171 | 3 | 20 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| tennis | KXATPCHALLENGERMATCH | 610 | 180 | 31 | 108 | 0 | - | 0 / $0.00 | 201 / $2.01 |
| soccer | KXTHAIL1TOTAL | 550 | 727 | 4 | 17 | 0 | 0.96 | 0 / $0.00 | 0 / $0.00 |
| soccer | KXHUNNB1TOTAL | 543 | 1882 | 4 | 14 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXBUNDESLIGA2TOTAL | 514 | 258 | 8 | 35 | 0 | - | 0 / $0.00 | 586 / $5.86 |
| soccer | KXECULPTOTAL | 436 | 1359 | 1 | 5 | 0 | 0.93 | 0 / $0.00 | 0 / $0.00 |
| soccer | KXCZEFNLTOTAL | 277 | 428 | 2 | 12 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXTFF1LIGTOTAL | 252 | 1052 | 3 | 11 | 1 | 0.88 | 1148 / $34.44 | 1148 / $11.48 |
| soccer | KXHNLTOTAL | 251 | 1129 | 2 | 8 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| football | KXNFLGAME | 232 | 885 | 0 | 2 | 0 | 0.02 | 0 / $0.00 | 140907 / $1409.08 |
| soccer | KXMYSLTOTAL | 223 | 528 | 2 | 8 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXKLEAGUETOTAL | 192 | 556 | 3 | 12 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXAPFDDHTOTAL | 189 | 1707 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXDIMAYORTOTAL | 186 | 965 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXARGPREMDIVTOTAL | 166 | 826 | 0 | 3 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| tennis | KXATPEXACTMATCH | 162 | 226 | 6 | 15 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXLIGAPORTUGALTOTAL | 153 | 442 | 2 | 8 | 0 | - | 68 / $2.03 | 249 / $2.50 |
| soccer | KXLALIGA2TOTAL | 152 | 1820 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXLIGAEXPTOTAL | 152 | 1691 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXCZEFLTOTAL | 125 | 409 | 4 | 6 | 0 | 0.47 | 76 / $2.29 | 76 / $0.76 |
| tennis | KXATPMATCH | 116 | 211 | 6 | 18 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXMLSBTTS | 103 | 538 | 2 | 8 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXCHLLDPTOTAL | 102 | 443 | 2 | 8 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXALLSVENSKANBTTS | 95 | 737 | 1 | 4 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXALLSVENSKANSPREAD | 95 | 468 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXMLS1HTOTAL | 94 | 244 | 8 | 22 | 3 | 0.61 | 0 / $0.00 | 36 / $0.36 |
| soccer | KXSERIECSPREAD | 76 | 5590 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXBUNDESLIGA2SPREAD | 72 | 228 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXMLSSPREAD | 65 | 590 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXBRASILEIROBBTTS | 57 | 442 | 1 | 4 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| football | KXMLSTOTAL | 54 | 266 | 1 | 4 | 20 | 0.71 | 10741 / $322.20 | 10741 / $107.41 |
| soccer | KXMLS1H | 50 | 633 | 0 | 0 | 2 | 0.63 | 0 / $0.00 | 0 / $0.00 |
| soccer | KXMLSGAME | 39 | 590 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXDENSUPERLIGASPREAD | 38 | 1891 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXSUPERLIGTOTAL | 38 | 378 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXARGNACBTOTAL | 38 | 5169 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXSCOCUPTOTAL | 35 | 2799 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXIDNSLBTTS | 22 | 595 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXEREDIVISIEBTTS | 21 | 167 | 1 | 4 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXBUNDESLIGA2BTTS | 19 | 236 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXSLGREECETOTAL | 19 | 2918 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXMLS1HBTTS | 19 | 626 | 1 | 2 | 1 | 0.78 | 0 / $0.00 | 0 / $0.00 |
| soccer | KXARGNACBBTTS | 19 | 7012 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| football | KXMLSBTTS | 6 | - | 0 | 0 | 6 | 0.72 | 1850 / $55.50 | 1850 / $18.49 |
| soccer | KXEREDIVISIESPREAD | 4 | 763 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXELITESERIENBTTS | 4 | 5122 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXDENSUPERLIGABTTS | 3 | 1100 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| football | KXNFLEQBTTS | 1 | - | 0 | 0 | 1 | 0.54 | 10 / $0.30 | 10 / $0.10 |

Latency counts from when OUR score feed changed (Polymarket's feed lags reality, so true bot speed is faster). Resting-bid columns: contracts that sellers dumped below that price after the decision, and the profit a resting bid there would have made (maker fee ignored).

## Decided-state engine (contracts the live score already settled, still trading)

2927 contracts decided while active; 869 had a price leaving > 0.4c after fees; 722 of those were mispriced AFTER the score was stable (lock tier)

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
| KXNFLPASSYDSPRECISE Pass Yards Precise | 9086 | 4.0 min | 4.1 min |
| KXESOCCERGAME eSoccer Game | 4018 | 4.0 min | 4.1 min |
| KXNCAAFSPREAD College Football Spread | 2387 | 4.0 min | 4.1 min |
| KXNHLGOAL NHL Goalscorer | 1760 | 3.0 min | 3.1 min |
| KXNCAAFTOTAL College Football Total Points | 1733 | 4.0 min | 4.1 min |
| KXNCAAFTEAMTOTAL College Football Team Total Po | 1252 | 4.0 min | 4.1 min |
| KXNHLPTS Pro Hockey Points | 1200 | 3.0 min | 3.1 min |
| KXNBA3PT NBA Player Threes | 1139 | 2.0 min | 2.1 min |
| KXNCAAF1HSPREAD College Football 1st Half Spre | 1092 | 4.0 min | 4.1 min |
| KXNBA3PTPROT NBA Player Threes Protected | 1061 | 2.5 min | 2.6 min |
| KXNBAREB NBA Player Rebounds | 1042 | 2.0 min | 2.1 min |
| KXNFLRECYDS Pro Football Receiving Yards | 1033 | 2.0 min | 2.1 min |
| KXNBAREBPROT NBA Player Rebounds Protected | 1005 | 2.5 min | 2.6 min |
| KXLIGAPROMATCH Russia Liga Pro Match | 936 | 4.0 min | 4.1 min |
| KXNHLFIRSTGOAL NHL First Goal | 925 | 6.0 min | 6.0 min |
| KXNBAPTS NBA Player Points | 918 | 2.0 min | 2.1 min |
| KXNHLAST Pro Hockey Assists | 889 | 6.0 min | 6.1 min |
| KXNBAPTSPROT NBA Player Points Protected | 880 | 2.5 min | 2.6 min |
| KXNBATEAMTOTAL NBA Team Total | 860 | 2.5 min | 2.6 min |
| KXNBAAST NBA Player Assists | 855 | 2.0 min | 2.1 min |
| KXNBAASTPROT NBA Player Assists Protected | 840 | 2.5 min | 2.6 min |
| KXNFLRECYDSPROT Receiving Yards Protected | 823 | 6.0 min | 6.1 min |
| KXNFLTOTALPRECISE Total Precise | 799 | 4.0 min | 4.1 min |
| KXNFLREC Pro Football Player Receptions | 766 | 2.0 min | 2.1 min |
| KXNFLRECPROT Receptions Protected | 742 | 6.0 min | 6.1 min |
| KXNCAAF1HTOTAL College Football 1st Half Tota | 728 | 4.0 min | 4.1 min |
| KXNCAAF2HSPREAD College Football 2nd Half Spre | 720 | 4.0 min | 4.1 min |
| KXNBASPREAD NBA Spread | 649 | 1.8 min | 1.8 min |
| KXNBATOTAL NBA Total | 643 | 1.8 min | 1.8 min |
| KXEBASKETBALLGAME eBasketball Game | 524 | 4.0 min | 4.1 min |
| KXNBA1HTEAMTOTAL NBA 1st Half Team Total | 484 | 2.5 min | 2.6 min |
| KXNCAAF2HTOTAL College Football 2nd Half Tota | 477 | 4.0 min | 4.1 min |
| KXMLSGOAL Goalscorer | 474 | 6.0 min | 6.1 min |
| KXNFLRSHYDSPROT Rushing Yards Protected | 444 | 6.0 min | 6.1 min |
| KXNBASTL NBA Player Steals | 426 | 2.0 min | 2.1 min |
| KXNBA1HTOTAL NBA 1st Half Total | 418 | 2.5 min | 2.6 min |
| KXNBA1HSPREAD NBA 1st Half Spread | 418 | 2.5 min | 2.6 min |
| KXNFLRSHYDS Pro Football Rushing Yards | 405 | 2.0 min | 2.1 min |
| KXNFLTDPROT Pro Football Touchdowns Protec | 399 | 6.0 min | 6.1 min |
| KXNFLTD Pro Football Touchdowns | 384 | 2.0 min | 2.1 min |

## Participant fingerprint (per sport; 60 s snapshots)

change% = share of scan cycles (60 s) where the best quote moved; react = median minutes from a score change to the next quote move (humans: slow, bursty, round sizes; bots: constant cadence, odd/constant sizes, instant reaction)

| venue | sport | markets | snapshots | two-sided | med spread | change% | react (min) | round sizes | med size |
|---|---|---|---|---|---|---|---|---|---|
| pm | soccer | 1758 | 276108 | 87% | 0.020 | 19% | 0.5 (n=4348) | - | - |
| pm | tennis | 1411 | 114416 | 92% | 0.010 | 23% | 0.5 (n=59810) | - | - |
| pm | esports | 3373 | 88005 | 76% | 0.030 | 19% | 0.5 (n=18448) | - | - |
| pm | table-tennis | 1524 | 60710 | 95% | 0.020 | 30% | 0.5 (n=30747) | - | - |
| pm | basketball | 741 | 58386 | 83% | 0.046 | 25% | 0.5 (n=10661) | - | - |
| pm | football | 483 | 26503 | 80% | 0.005 | 17% | 1.1 (n=1118) | - | - |
| pm | climate | 215 | 10641 | 75% | 0.040 | 21% | - (n=0) | - | - |
| pm | ice-hockey | 102 | 10573 | 84% | 0.060 | 14% | 0.7 (n=584) | - | - |
| pm | motorsports | 159 | 8546 | 40% | 0.040 | 14% | - (n=0) | - | - |
| pm | cricket | 9 | 3973 | 95% | 0.030 | 11% | 1.0 (n=593) | - | - |
| pm | misc | 47 | 3778 | 93% | 0.010 | 12% | - (n=0) | - | - |
| pm | beach-volleyball | 63 | 3058 | 86% | 0.010 | 23% | 0.5 (n=1681) | - | - |
| pm | golf | 159 | 2938 | 4% | 0.040 | 3% | - (n=0) | - | - |
| pm | darts | 36 | 1172 | 92% | 0.090 | 29% | 0.5 (n=142) | - | - |
| pm | mma | 14 | 759 | 95% | 0.020 | 4% | - (n=0) | - | - |
| pm | baseball | 2 | 399 | 95% | 0.060 | 22% | 0.5 (n=11) | - | - |
| pm | rugby | 20 | 359 | 73% | 0.450 | 23% | - (n=0) | - | - |
| pm | macro | 83 | 299 | 0% | - | 1% | - (n=0) | - | - |
| pm | boxing | 4 | 165 | 95% | 0.030 | 56% | - (n=0) | - | - |
| pm | pickleball | 13 | 115 | 66% | 0.270 | 11% | - (n=0) | - | - |
| k | KXNCAAFGAME College Football Game | 726 | 655034 | 98% | 0.030 | 1% | - | 8% | 105 |
| k | KXNBA3PT NBA Player Threes | 1404 | 143756 | 82% | 0.080 | 17% | - | 24% | 30 |
| k | KXNFLGAME NFL Game | 58 | 141150 | 99% | 0.010 | 1% | - | 3% | 119155 |
| k | KXNFLPASSYDSPRECISE Pass Yards Precise | 10836 | 113671 | 0% | - | 0% | - | 0% | - |
| k | KXCS2MAP Counter-Strike 2 Map Win | 484 | 107606 | 93% | 0.500 | 6% | - | 19% | 110 |
| k | KXNCAAFTEAMTOTAL College Football Team To | 1319 | 99919 | 83% | 0.020 | 2% | - | 27% | 230 |
| k | KXNCAAFSPREAD College Football Spread | 2707 | 79139 | 62% | 0.040 | 3% | - | 16% | 129 |
| k | KXNBAAST NBA Player Assists | 1063 | 74934 | 82% | 0.070 | 16% | - | 25% | 25 |
| k | KXNBAREB NBA Player Rebounds | 1319 | 71260 | 79% | 0.090 | 19% | - | 21% | 36 |
| k | KXNBAPTS NBA Player Points | 1256 | 70571 | 80% | 0.050 | 21% | - | 22% | 40 |
| k | KXESOCCERGAME eSoccer Game | 4353 | 68739 | 24% | 0.450 | 6% | - | 25% | 33 |
| k | KXNCAAFTOTAL College Football Total P | 1942 | 52914 | 59% | 0.170 | 5% | - | 18% | 132 |
| k | KXNBA3PTPROT NBA Player Threes Protec | 1348 | 52007 | 37% | 0.150 | 2% | - | 20% | 43 |
| k | KXNCAAF1H College Football 1st Hal | 1056 | 43337 | 90% | 0.760 | 1% | - | 31% | 200 |
| k | KXNBA1HTEAMTOTAL NBA 1st Half Team Total | 528 | 41272 | 61% | 0.260 | 11% | - | 22% | 92 |
| k | KXNHLGOAL NHL Goalscorer | 1769 | 39804 | 40% | 0.050 | 13% | - | 22% | 50 |
| k | KXNCAAF1HSPREAD College Football 1st Hal | 1106 | 35085 | 60% | 0.040 | 3% | - | 32% | 180 |
| k | KXNBA1HTOTAL NBA 1st Half Total | 456 | 34411 | 71% | 0.040 | 9% | - | 25% | 100 |
| k | KXNBA1HSPREAD NBA 1st Half Spread | 456 | 33406 | 72% | 0.040 | 8% | - | 17% | 126 |
| k | KXATPSETWINNER ATP Set Winner | 212 | 30966 | 92% | 0.030 | 4% | - | 11% | 178 |
| k | KXNFLRECYDS Pro Football Receiving Y | 1670 | 28656 | 46% | 0.040 | 5% | - | 31% | 100 |
| k | KXNBAREBPROT NBA Player Rebounds Prot | 1253 | 28257 | 30% | 0.170 | 4% | - | 19% | 63 |
| k | KXNBAASTPROT NBA Player Assists Prote | 1020 | 27638 | 31% | 0.140 | 2% | - | 23% | 101 |
| k | KXNBA2HSPREAD NBA 2nd Half Spread | 399 | 24802 | 75% | 0.130 | 25% | - | 28% | 192 |
| k | KXWTASETWINNER WTA Set Winner | 272 | 24533 | 74% | 0.040 | 4% | - | 25% | 114 |
| k | KXNBA2HTOTAL NBA 2nd Half Total | 399 | 23833 | 76% | 0.160 | 23% | - | 25% | 105 |
| k | KXLIGAMXSCORE Correct Score | 270 | 23806 | 55% | 0.020 | 3% | - | 13% | 799 |
| k | KXMLSSCORE Correct Score | 450 | 23656 | 54% | 0.020 | 2% | - | 14% | 1116 |
| k | KXNBAPTSPROT NBA Player Points Protec | 1122 | 23526 | 33% | 0.435 | 2% | - | 18% | 162 |
| k | KXNFLRECYDSPROT Receiving Yards Protecte | 1532 | 22547 | 32% | 0.150 | 1% | - | 11% | 25 |
| k | KXNCAAF1HTOTAL College Football 1st Hal | 728 | 22316 | 58% | 0.040 | 4% | - | 17% | 110 |
| k | KXATPCHALLENGERMATCH Challenger ATP  | 252 | 22016 | 88% | 0.010 | 8% | - | 5% | 620 |
| k | KXNBA2QSPREAD NBA 2nd Quarter Spread | 312 | 20343 | 72% | 0.050 | 8% | - | 18% | 165 |
| k | KXNBA2QTOTAL NBA 2nd Quarter Total | 312 | 18956 | 69% | 0.060 | 8% | - | 36% | 192 |
| k | KXNEXTTEAMNHL Next Team NHL | 230 | 18860 | 0% | 0.130 | 0% | - | 23% | 341 |
| k | KXNFLREC Pro Football Player Rece | 1061 | 18731 | 41% | 0.040 | 6% | - | 28% | 100 |
| k | KXNBAPRA NBA Player Points + Rebo | 483 | 17117 | 67% | 0.300 | 19% | - | 10% | 9 |
| k | KXNBA1QTOTAL NBA 1st Quarter Total | 312 | 17110 | 66% | 0.050 | 8% | - | 24% | 149 |
| k | KXNBA1QSPREAD NBA 1st Quarter Spread | 312 | 17049 | 65% | 0.050 | 7% | - | 28% | 155 |
| k | KXNBA3QSPREAD NBA 3rd Quarter Spread | 273 | 16546 | 74% | 0.050 | 9% | - | 35% | 150 |

## Schema notes (raw keys seen)

- polymarket: active, archived, category, chatChannel, closed, combos, createdAt, description, elapsed, endDate, ended, eventState, featureAvailability, fixtureId, gameId, hidden, id, insiderTradingRules, live, marketCounts, marketGroups, markets, metadata, participants, payoutEstimateMessage, payoutEstimateTime, period, primaryTag, score, seriesSlug, slug, sortType, sportradarGameId, startDate, startTime, streamProvider, streamRequiresAuth, tags, teams, ticker, title, updatedAt
- kalshi: can_close_early, close_time, created_time, custom_strike, early_close_condition, event_ticker, exchange_index, expected_expiration_time, expiration_time, expiration_value, last_price_dollars, latest_expiration_time, market_type, no_ask_dollars, no_bid_dollars, no_sub_title, notional_value_dollars, occurrence_datetime, open_interest_fp, open_time, previous_price_dollars, previous_yes_ask_dollars, previous_yes_bid_dollars, price_level_structure, price_ranges, primary_participant_key, result, rules_primary, rules_secondary, settlement_bounds_type, settlement_timer_seconds, settlement_value_dollars, status, strike_type, ticker, title, updated_time, volume_24h_fp, volume_fp, yes_ask_dollars, yes_ask_size_fp, yes_bid_dollars, yes_bid_size_fp, yes_sub_title

