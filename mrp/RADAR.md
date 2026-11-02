# Mr. P — sports radar

Updated 2026-11-02T02:24:43Z by `run-20261102T0150-41370273713` (last 7 days). Read-only scanner of every sports market on Polymarket US and Kalshi — it never places orders.
Kit: `mrp/mrp_sports_radar.py` on the `mrp` branch. Raw tape: `mrp/radar/<run>/`.

# Sports radar report

records 4,753,883 | 2026-10-30 02:23Z → 02:23Z | runs 18 | pairs matched 1458 | errors {'radar': 19, 'sp.k.series_poll:KXATPEXACTMATCH': 10, 'sp.k.series_poll:KXATPMATCH': 10, 'sp.k.series_poll:KXATPSETWINNER': 10, 'sp.k.series_poll:KXAUTBUNDESTOTAL': 4, 'sp.k.series_poll:KXEFLL11H': 6, 'sp.k.series_poll:KXEFLL11HSPREAD': 10, 'sp.k.series_poll:KXHNLTOTAL': 6, 'sp.k.series_poll:KXLALIGABTTS': 9, 'sp.k.series_poll:KXLALIGASCORE': 6, 'sp.k.series_poll:KXLALIGASPREAD': 8, 'sp.k.always:KXNFLGAME': 6, 'sp.k.series_poll:KXATPCHALLENGERMATCH': 7, 'sp.k.series_poll:KXEFLL11HBTTS': 10, 'sp.k.series_poll:KXLALIGA2H': 6, 'sp.k.series_poll:KXCS2MAP': 6, 'sp.k.series_poll:KXEFLL11HTOTAL': 8, 'sp.k.series_poll:KXLALIGA2HBTTS': 8, 'sp.k.series_poll:KXLALIGA2HSPREAD': 6, 'sp.k.series_poll:KXLALIGA2HTOTAL': 4, 'sp.k.series_poll:KXLALIGACORNERS': 8, 'sp.k.series_poll:KXLALIGAGAME': 6, 'sp.k.series_poll:KXLALIGAGOAL': 6, 'sp.k.series_poll:KXAUTBUNDESGAME': 2, 'sp.k.series_poll:KXCZEFLTOTAL': 7, 'sp.k.series_poll:KXELITESERIENTOTAL': 2, 'sp.k.series_poll:KXEREDIVISIETOTAL': 2, 'sp.k.always:KXNCAAFGAME': 7, 'sp.k.series_poll:KXLIGUE11HBTTS': 3, 'sp.k.series_poll:KXLIGUE11HSCORE': 4, 'sp.k.series_poll:KXLIGUE11H': 4, 'sp.k.series_poll:KXLIGUE11HSPREAD': 1}

## Catalogue (latest inventory, 01:54Z)

Polymarket US sports events 4523 of 6017 active events; Kalshi near-term sports markets 4350 in 407 events; calls so far {'pm': 47, 'k': 590}; MB {'pm': 160640785, 'k': 106008121}

| venue | sport / league / type | markets | two-sided | med spread | vol 24h |
|---|---|---|---|---|---|
| pm | football / nfl / futures | 4117 | 62% | 0.010 | 0 |
| pm | football / cfb / futures | 1608 | 79% | 0.010 | 0 |
| pm | basketball / nba / futures | 1422 | 59% | 0.020 | 0 |
| pm | ice-hockey / nhl / futures | 779 | 97% | 0.010 | 0 |
| pm | basketball / wcbb / basketball_team_full_game_winner | 653 | 33% | 0.430 | 0 |
| pm | basketball / cbb / basketball_team_full_game_winner | 635 | 27% | 0.030 | 0 |
| k | KXNCAAFGAME / College Football Game | 506 | 100% | 0.100 | 731136 |
| pm | golf / worlwide / futures | 469 | 25% | 0.499 | 0 |
| pm | soccer / epl / futures | 435 | 86% | 0.010 | 0 |
| pm | basketball / cbb / futures | 317 | 85% | 0.010 | 0 |
| pm | tennis / utr / tennis_match_winner | 288 | 19% | 0.430 | 0 |
| pm | soccer / ucl / futures | 276 | 78% | 0.010 | 0 |
| pm | table-tennis / setkameua / table_tennis_match_winner | 272 | 81% | 0.170 | 0 |
| pm | baseball / mlb / futures | 264 | 25% | 0.001 | 0 |
| pm | football / cfb / football_team_full_game_winner | 211 | 84% | 0.080 | 0 |
| pm | tennis / itfme / tennis_match_winner | 205 | 35% | 0.140 | 0 |
| pm | macro /  / futures | 150 | 75% | 0.010 | 0 |
| pm | soccer / lal / futures | 146 | 66% | 0.010 | 0 |
| pm | boxing / boxing / futures | 145 | 0% | - | 0 |
| pm | mma / ufc / futures | 142 | 82% | 0.010 | 0 |
| pm | tennis / itfwo / tennis_match_winner | 142 | 65% | 0.010 | 0 |
| pm | tennis / atp / tennis_match_winner | 121 | 79% | 0.010 | 0 |
| pm | tennis / atp / futures | 107 | 40% | 0.010 | 0 |
| pm | basketball / nba / basketball_team_full_game_winner | 107 | 73% | 0.270 | 0 |
| pm | soccer / sea / futures | 86 | 81% | 0.010 | 0 |
| pm | tennis / wta / futures | 79 | 42% | 0.010 | 0 |
| pm | soccer / bun / futures | 79 | 82% | 0.010 | 0 |
| pm | soccer / lg1 / futures | 77 | 83% | 0.010 | 0 |
| pm | tennis / wta / tennis_match_winner | 63 | 75% | 0.010 | 0 |
| pm | soccer / j2 / soccer_team_full_time_winner | 60 | 67% | 0.030 | 0 |
| pm | tennis / atpdb / tennis_match_winner | 60 | 45% | 0.420 | 0 |
| pm | table-tennis / czechligapro / table_tennis_match_winner | 57 | 14% | 0.420 | 0 |
| pm | soccer / uecl / soccer_team_full_time_winner | 55 | 98% | 0.030 | 0 |
| pm | soccer / ucl / soccer_team_full_time_winner | 54 | 100% | 0.010 | 0 |
| pm | soccer / uel / soccer_team_full_time_winner | 54 | 100% | 0.020 | 0 |
| pm | soccer / mls / futures | 53 | 91% | 0.010 | 0 |
| pm | golf / masttour / futures | 52 | 100% | 0.499 | 0 |
| pm | soccer / acle / soccer_team_full_time_winner | 48 | 62% | 0.020 | 0 |
| pm | table-tennis / setkamecz / table_tennis_match_winner | 48 | 85% | 0.170 | 0 |
| pm | technology /  / futures | 42 | 74% | 0.010 | 0 |
| pm | motorsports / f1 / futures | 38 | 34% | 0.011 | 0 |
| pm | soccer / lmx / futures | 36 | 19% | 0.070 | 0 |
| pm | soccer / uel / futures | 36 | 3% | 0.160 | 0 |
| pm | soccer / uecl / futures | 36 | 0% | - | 0 |
| pm | soccer / sea / soccer_team_full_time_winner | 36 | 100% | 0.010 | 0 |
| pm | soccer / ekst / soccer_team_full_time_winner | 36 | 61% | 0.055 | 0 |
| pm | soccer / serca / soccer_team_full_time_winner | 36 | 44% | 0.480 | 0 |
| pm | soccer / eflch / soccer_team_full_time_winner | 36 | 100% | 0.020 | 0 |
| pm | esports / ebattlesefwcb / efootball_team_full_time_winner | 36 | 92% | 0.010 | 0 |
| pm | table-tennis / setkamemd / table_tennis_match_winner | 36 | 6% | 0.360 | 0 |
| k | KXNFLGAME / NFL Game | 34 | 100% | 0.010 | 13079746 |
| pm | soccer / lal / soccer_team_full_time_winner | 33 | 100% | 0.010 | 0 |
| pm | soccer / epl / soccer_team_full_time_winner | 33 | 100% | 0.010 | 0 |
| pm | soccer / ligpor / soccer_team_full_time_winner | 33 | 82% | 0.050 | 0 |
| pm | soccer / tff1 / soccer_team_full_time_winner | 33 | 39% | 0.480 | 0 |
| pm | soccer / alsv / soccer_team_full_time_winner | 33 | 64% | 0.050 | 0 |
| pm | ice-hockey / nhl / hockey_team_full_game_winner | 31 | 100% | 0.010 | 0 |
| pm | football / nfl / football_team_full_game_winner | 30 | 67% | 0.007 | 0 |
| pm | soccer / lg1 / soccer_team_full_time_winner | 30 | 100% | 0.020 | 0 |
| pm | soccer / ecu1 / soccer_team_full_time_winner | 30 | 47% | 0.460 | 0 |

## Opportunities

| kind | distinct | hits | max margin $/contract | max persistence | fresh-BBO still open |
|---|---|---|---|---|---|
| decided_k | 834 | 65951 | 0.9893 | 169 min | 0/0 |
| decided_pm | 23 | 488 | 0.9947 | 28 min | 182/488 |
| decided_pm_closed | 14 | 144 | 0.9893 | 30 min | 0/144 |
| dutch_k | 15 | 87 | 0.0817 | 140 min | 0/0 |
| dutch_k_sell | 3 | 6 | 0.0107 | 0 min | 0/0 |
| dutch_pm | 61 | 2884 | 0.5316 | 50 min | 0/0 |
| implication_k | 7901 | 460111 | 0.9786 | 141 min | 0/0 |
| lag_k_settled | 190 | 33076 | 0.9973 | 273 min | 27517/32055 |
| lag_k_settled_closed | 157 | 2398 | 0.9973 | 272 min | 0/2398 |

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
- **decided_k** soccer — New England Revolution vs. Inter Miami CF — buy_yes @ 0.23 | margin 0.7576 | 126 min, 397 hits | score 2-2 90'
- **lag_k_settled** esports — Nova Esports vs. Any Questions Gaming — bid 0.96 ask - sell_yes @ 0.96 | margin 0.9573 | 61 min, 460 hits | fresh bbo 0.96/- depth 19/0 | score 1-0 Map 2
- **decided_k** football — NE Patriots vs. MIA Dolphins — buy_yes @ 0.2 | margin 0.8201 | 126 min, 390 hits | score 24-19 Q4
- **decided_k** football — NE Patriots vs. MIA Dolphins — buy_yes @ 0.36 | margin 0.6750 | 126 min, 390 hits | score 24-19 Q4
- **implication_k** 🔒  — 26OCT30DENPHX — | margin 0.1008 | 135 min, 344 hits | score - 
- **implication_k** 🔒  — 26OCT30DENPHX — | margin 0.1249 | 135 min, 344 hits | score - 
- **implication_k** 🔒  — 26OCT30DENPHX — | margin 0.1304 | 135 min, 344 hits | score - 
- **implication_k** 🔒  — 26OCT30DENPHX — | margin 0.1259 | 135 min, 344 hits | score - 
- **implication_k** 🔒  — 26OCT30DENPHX — | margin 0.1196 | 135 min, 344 hits | score - 
- **implication_k** 🔒  — 26OCT30DENPHX — | margin 0.1138 | 135 min, 344 hits | score - 

## Live paper trades (no orders; Kalshi prices, taker fees)

Ledger L2-2026-11-01 (earlier ledgers excluded: L1)

**Total closed P&L: $-347.12 on $1199.12 staked (-28.9%)**

| rule | entries | closed | winners | staked | P&L | ROI |
|---|---|---|---|---|---|---|
| R1 anchor [ncaaf] | 26 | 26 | 11 | $262.99 | $-34.99 | -13% |
| R1 anchor [nfl] | 5 | 4 | 1 | $40.72 | $-21.72 | -53% |
| R2 q1cheap [ncaaf] | 37 | 37 | 2 | $194.50 | $-142.50 | -73% |
| R2 q1cheap [nfl] | 6 | 6 | 1 | $31.46 | $-2.46 | -8% |
| R3 blowout [ncaaf] | 16 | 16 | 1 | $339.32 | $-197.32 | -58% |
| R4 halftime [ncaaf] | 19 | 19 | 6 | $95.24 | $+9.76 | +10% |
| R6 decided [other] | 16 | 12 | 12 | $234.89 | $+42.11 | +18% |

| time (UTC) | rule | game | team | entry | contracts | why | result |
|---|---|---|---|---|---|---|---|
| 02:11 | R1 anchor | PHI Eagles vs. WAS Commander | Philadelphia | 0.62 | 16 | pregame dog (mid 0.30) leads 10-3 in Q2, ask 0.62 | open |
| 23:01 | R6 decided | Houston Dash vs. Portland Th | Over 0.5 1H goals scored | 0.76 | 26 | 1H (0, 1) > 0.5 | open |
| 22:54 | R6 decided | Houston Dash vs. Portland Th | Over 0.5 goals scored | 0.96 | 20 | score 0-1 total 1 > 0.5 | open |
| 22:24 | R1 anchor | NE Patriots vs. MIA Dolphins | Miami | 0.39 | 25 | pregame dog (mid 0.24) leads 3-6 in Q2, ask 0.39 | final score (pending Kalshi settlement): 0.00, $-10.17 |
| 22:23 | R6 decided | NE Patriots vs. MIA Dolphins | Both Teams To Score | 0.72 | 27 | both scored 3-6 | open |
| 21:40 | R6 decided | NE Patriots vs. MIA Dolphins | Over 2.5 goals scored | 0.71 | 28 | score 3-0 total 3 > 2.5 | open |
| 21:40 | R6 decided | NE Patriots vs. MIA Dolphins | Over 1.5 goals scored | 0.89 | 22 | score 3-0 total 3 > 1.5 | kalshi settled: 1.00, $+2.27 |
| 21:40 | R6 decided | NE Patriots vs. MIA Dolphins | Over 0.5 goals scored | 0.97 | 20 | score 3-0 total 3 > 0.5 | kalshi settled: 1.00, $+0.56 |
| 21:29 | R2 q1cheap | NE Patriots vs. MIA Dolphins | Miami | 0.19 | 26 | Q1 ask 0.19, score 0-0 | final score (pending Kalshi settlement): 0.00, $-5.22 |
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

### Score reaction speed (live, 15 s): share of the 3-minute move done by +15 s / +30 s / +60 s

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
- 26NOV01PHIWAS 3-0: -0% / -0% / -0%
- 26NOV01PHIWAS 3-0: 0% / 0% / 0%

## Bot latency map: seconds from the score to Kalshi repricing a decided market

| sport | series | decided | median s to reprice | <= 15 s | <= 60 s | never (closed/timeout) | cheapest ask seen | resting bid @0.97: contracts / $ | @0.99: contracts / $ |
|---|---|---|---|---|---|---|---|---|---|
| soccer | KXELITESERIENTOTAL | 1513 | 782 | 26 | 94 | 0 | - | 0 / $0.00 | 33 / $0.33 |
| soccer | KXIDNSLTOTAL | 1469 | 1144 | 9 | 32 | 0 | 0.96 | 0 / $0.00 | 82 / $0.82 |
| football | KXNFLTOTALPRECISE | 1307 | 386 | 35 | 109 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXALLSVENSKANTOTAL | 1261 | 891 | 9 | 34 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXEREDIVISIETOTAL | 1183 | 413 | 36 | 120 | 0 | - | 0 / $0.00 | 337 / $3.38 |
| soccer | KXMLSTOTAL | 1135 | 714 | 20 | 80 | 4 | 0.82 | 188 / $5.63 | 4120 / $41.20 |
| soccer | KXLIGAFTOTAL | 1112 | 1971 | 1 | 12 | 0 | 0.98 | 0 / $0.00 | 0 / $0.00 |
| soccer | KXSERIECTOTAL | 1051 | 1323 | 12 | 41 | 0 | 0.97 | 0 / $0.00 | 165 / $1.65 |
| soccer | KXBELGIANPLTOTAL | 1041 | 458 | 19 | 68 | 0 | 0.89 | 763 / $22.89 | 763 / $7.63 |
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
| soccer | KXDIMAYORTOTAL | 318 | 1348 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXCZEFNLTOTAL | 277 | 428 | 2 | 12 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| football | KXNFLGAME | 276 | 864 | 0 | 2 | 0 | 0.02 | 0 / $0.00 | 140940 / $1409.41 |
| soccer | KXTFF1LIGTOTAL | 252 | 1052 | 3 | 11 | 1 | 0.88 | 1148 / $34.44 | 1148 / $11.48 |
| soccer | KXHNLTOTAL | 251 | 1129 | 2 | 8 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXMYSLTOTAL | 223 | 528 | 2 | 8 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXKLEAGUETOTAL | 192 | 556 | 3 | 12 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXAPFDDHTOTAL | 189 | 1707 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXARGPREMDIVTOTAL | 166 | 826 | 0 | 3 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| tennis | KXATPEXACTMATCH | 162 | 226 | 6 | 15 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXLIGAPORTUGALTOTAL | 153 | 442 | 2 | 8 | 0 | - | 68 / $2.03 | 249 / $2.50 |
| soccer | KXLALIGA2TOTAL | 152 | 1820 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXLIGAEXPTOTAL | 152 | 1691 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXCZEFLTOTAL | 125 | 409 | 4 | 6 | 0 | 0.47 | 76 / $2.29 | 76 / $0.76 |
| soccer | KXMLS1HTOTAL | 121 | 228 | 8 | 28 | 3 | 0.61 | 0 / $0.00 | 36 / $0.36 |
| tennis | KXATPMATCH | 116 | 211 | 6 | 18 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXMLSBTTS | 103 | 538 | 2 | 8 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXCHLLDPTOTAL | 102 | 443 | 2 | 8 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXALLSVENSKANBTTS | 95 | 737 | 1 | 4 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXALLSVENSKANSPREAD | 95 | 468 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXSERIECSPREAD | 76 | 5590 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXBUNDESLIGA2SPREAD | 72 | 228 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXMLSSPREAD | 65 | 590 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXBRASILEIROBBTTS | 57 | 442 | 1 | 4 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| football | KXMLSTOTAL | 56 | 266 | 1 | 4 | 22 | 0.63 | 23789 / $713.66 | 23789 / $237.90 |
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

2876 contracts decided while active; 834 had a price leaving > 0.4c after fees; 694 of those were mispriced AFTER the score was stable (lock tier)

| sport | game | contract | decided | reason | max margin | mispriced for | lock margin | lock depth |
|---|---|---|---|---|---|---|---|---|
| basketball | CLE Cavaliers vs. ATL Hawks | KXNBA2HSPREAD-26OCT29CLEATL-ATL3 | YES | ended 111-114 margin 3 vs 2.5 | 0.989 | 274s | 0.989 | 8180 |
| basketball | CLE Cavaliers vs. ATL Hawks | KXNBA2HSPREAD-26OCT29CLEATL-ATL2 | YES | ended 111-114 margin 3 vs 1.5 | 0.989 | 274s | 0.989 | 8174 |
| basketball | CLE Cavaliers vs. ATL Hawks | KXNBA2HTOTAL-26OCT29CLEATL-140 | YES | score 111-114 total 225 > 139.5 | 0.989 | 274s | 0.989 | 9451 |
| basketball | CLE Cavaliers vs. ATL Hawks | KXNBA2HTOTAL-26OCT29CLEATL-138 | YES | score 111-114 total 225 > 137.5 | 0.989 | 274s | 0.989 | 9079 |
| basketball | CLE Cavaliers vs. ATL Hawks | KXNBA2HTOTAL-26OCT29CLEATL-136 | YES | score 111-114 total 225 > 135.5 | 0.989 | 274s | 0.989 | 7472 |
| basketball | CLE Cavaliers vs. ATL Hawks | KXNBA4QSPREAD-26OCT29CLEATL-CLE4 | NO | ended 111-114 margin -3 vs 3.5 | 0.989 | 274s | 0.989 | 8188 |
| basketball | CLE Cavaliers vs. ATL Hawks | KXNBA4QSPREAD-26OCT29CLEATL-CLE2 | NO | ended 111-114 margin -3 vs 1.5 | 0.989 | 274s | 0.989 | 8687 |
| basketball | CLE Cavaliers vs. ATL Hawks | KXNBA4QSPREAD-26OCT29CLEATL-ATL3 | YES | ended 111-114 margin 3 vs 2.5 | 0.989 | 274s | 0.989 | 21986 |
| basketball | CLE Cavaliers vs. ATL Hawks | KXNBA4QSPREAD-26OCT29CLEATL-ATL2 | YES | ended 111-114 margin 3 vs 1.5 | 0.989 | 274s | 0.989 | 18977 |
| basketball | CLE Cavaliers vs. ATL Hawks | KXNBA4QTOTAL-26OCT29CLEATL-72 | YES | score 111-114 total 225 > 71.5 | 0.989 | 274s | 0.989 | 10950 |
| basketball | CLE Cavaliers vs. ATL Hawks | KXNBA4QTOTAL-26OCT29CLEATL-70 | YES | score 111-114 total 225 > 69.5 | 0.989 | 274s | 0.989 | 11118 |
| basketball | CLE Cavaliers vs. ATL Hawks | KXNBA4QTOTAL-26OCT29CLEATL-68 | YES | score 111-114 total 225 > 67.5 | 0.989 | 274s | 0.989 | 11121 |
| basketball | CLE Cavaliers vs. ATL Hawks | KXNBA4QTOTAL-26OCT29CLEATL-66 | YES | score 111-114 total 225 > 65.5 | 0.989 | 274s | 0.989 | 11117 |
| basketball | CLE Cavaliers vs. ATL Hawks | KXNBA4QTOTAL-26OCT29CLEATL-64 | YES | score 111-114 total 225 > 63.5 | 0.989 | 274s | 0.989 | 11670 |
| basketball | CLE Cavaliers vs. ATL Hawks | KXNBA4QTOTAL-26OCT29CLEATL-62 | YES | score 111-114 total 225 > 61.5 | 0.989 | 274s | 0.989 | 11570 |
| basketball | CLE Cavaliers vs. ATL Hawks | KXNBA4QTOTAL-26OCT29CLEATL-60 | YES | score 111-114 total 225 > 59.5 | 0.989 | 274s | 0.989 | 10304 |
| basketball | CLE Cavaliers vs. ATL Hawks | KXNBA4QTOTAL-26OCT29CLEATL-58 | YES | score 111-114 total 225 > 57.5 | 0.989 | 274s | 0.989 | 9096 |
| basketball | CLE Cavaliers vs. ATL Hawks | KXNBA4QTOTAL-26OCT29CLEATL-56 | YES | score 111-114 total 225 > 55.5 | 0.989 | 274s | 0.989 | 7939 |
| ice-hockey | BUF Sabres vs. ANA Ducks | KXNHL3PTOTAL-26OCT29BUFANA-7 | YES | score 7-6 total 13 > 6.5 | 0.989 | 764s | 0.989 | 3256 |
| ice-hockey | BUF Sabres vs. ANA Ducks | KXNHL3PTOTAL-26OCT29BUFANA-6 | YES | score 7-6 total 13 > 5.5 | 0.989 | 764s | 0.989 | 2597 |
| ice-hockey | OTT Senators vs. LAK Kings | KXNHL3PTOTAL-26OCT29OTTLA-7 | YES | score 5-6 total 11 > 6.5 | 0.989 | 464s | 0.989 | 1420 |
| ice-hockey | OTT Senators vs. LAK Kings | KXNHL3PTOTAL-26OCT29OTTLA-6 | YES | score 5-6 total 11 > 5.5 | 0.989 | 464s | 0.989 | 1319 |
| ice-hockey | OTT Senators vs. LAK Kings | KXNHL3PTOTAL-26OCT29OTTLA-5 | YES | score 5-6 total 11 > 4.5 | 0.989 | 464s | 0.989 | 3626 |
| basketball | NY Knicks vs. PHI 76ers | KXNBA1QTOTAL-26OCT30NYKPHI-60 | YES | score 31-42 total 73 > 59.5 | 0.989 | 420s | 0.989 | 3350 |
| basketball | NY Knicks vs. PHI 76ers | KXNBA1QTOTAL-26OCT30NYKPHI-58 | YES | score 31-42 total 73 > 57.5 | 0.989 | 480s | 0.989 | 10805 |

## Close / settlement latency (how clunky each venue is after the final whistle)

Kalshi: settlement_ts − close_time per series (negative = settled before the scheduled close)

| series | n | median | p90 |
|---|---|---|---|
| KXNFLPASSYDSPRECISE Pass Yards Precise | 12463 | 4.0 min | 4.1 min |
| KXESOCCERGAME eSoccer Game | 4000 | 4.0 min | 4.1 min |
| KXNCAAFSPREAD College Football Spread | 2387 | 4.0 min | 4.1 min |
| KXNCAAFTOTAL College Football Total Points | 1733 | 4.0 min | 4.1 min |
| KXNHLGOAL NHL Goalscorer | 1495 | 3.0 min | 3.1 min |
| KXNFLTOTALPRECISE Total Precise | 1271 | 4.0 min | 4.1 min |
| KXNCAAFTEAMTOTAL College Football Team Total Po | 1233 | 4.0 min | 4.1 min |
| KXNFLRECYDSPROT Receiving Yards Protected | 1173 | 6.0 min | 6.1 min |
| KXNBA3PT NBA Player Threes | 1164 | 2.0 min | 2.1 min |
| KXNFLRECYDS Pro Football Receiving Yards | 1154 | 2.0 min | 2.1 min |
| KXNHLPTS Pro Hockey Points | 1116 | 3.0 min | 3.1 min |
| KXNBA3PTPROT NBA Player Threes Protected | 1085 | 2.5 min | 2.6 min |
| KXNBAREB NBA Player Rebounds | 1057 | 2.0 min | 2.1 min |
| KXNCAAF1HSPREAD College Football 1st Half Spre | 1048 | 4.0 min | 4.1 min |
| KXNBAREBPROT NBA Player Rebounds Protected | 1022 | 2.5 min | 2.6 min |
| KXLIGAPROMATCH Russia Liga Pro Match | 934 | 4.0 min | 4.1 min |
| KXNBAPTS NBA Player Points | 920 | 2.0 min | 2.1 min |
| KXNBATEAMTOTAL NBA Team Total | 890 | 2.5 min | 2.6 min |
| KXNBAPTSPROT NBA Player Points Protected | 883 | 2.5 min | 2.6 min |
| KXNBAAST NBA Player Assists | 863 | 2.0 min | 2.1 min |
| KXNHLAST Pro Hockey Assists | 851 | 6.0 min | 6.1 min |
| KXNFLRECPROT Receptions Protected | 851 | 6.0 min | 6.1 min |
| KXNHLFIRSTGOAL NHL First Goal | 850 | 6.0 min | 6.0 min |
| KXNBAASTPROT NBA Player Assists Protected | 849 | 2.5 min | 2.6 min |
| KXNFLREC Pro Football Player Receptions | 802 | 2.0 min | 2.1 min |
| KXNCAAF2HSPREAD College Football 2nd Half Spre | 720 | 4.0 min | 4.1 min |
| KXNCAAF1HTOTAL College Football 1st Half Tota | 697 | 4.0 min | 4.1 min |
| KXNBASPREAD NBA Spread | 649 | 1.8 min | 1.8 min |
| KXNBATOTAL NBA Total | 643 | 1.8 min | 1.8 min |
| KXNFLRSHYDSPROT Rushing Yards Protected | 546 | 6.0 min | 6.1 min |
| KXEBASKETBALLGAME eBasketball Game | 520 | 4.0 min | 4.1 min |
| KXNFLTDPROT Pro Football Touchdowns Protec | 478 | 6.0 min | 6.1 min |
| KXNCAAF2HTOTAL College Football 2nd Half Tota | 477 | 4.0 min | 4.1 min |
| KXMLSGOAL Goalscorer | 474 | 6.0 min | 6.1 min |
| KXNFLRSHYDS Pro Football Rushing Yards | 454 | 2.0 min | 2.1 min |
| KXNBA1HTEAMTOTAL NBA 1st Half Team Total | 440 | 2.5 min | 2.6 min |
| KXNBASTL NBA Player Steals | 432 | 2.0 min | 2.1 min |
| KXNFLTD Pro Football Touchdowns | 425 | 2.0 min | 2.1 min |
| KXNBA2HTOTAL NBA 2nd Half Total | 399 | 2.5 min | 2.6 min |
| KXNBA2HSPREAD NBA 2nd Half Spread | 399 | 2.5 min | 2.6 min |

## Participant fingerprint (per sport; 60 s snapshots)

change% = share of scan cycles (60 s) where the best quote moved; react = median minutes from a score change to the next quote move (humans: slow, bursty, round sizes; bots: constant cadence, odd/constant sizes, instant reaction)

| venue | sport | markets | snapshots | two-sided | med spread | change% | react (min) | round sizes | med size |
|---|---|---|---|---|---|---|---|---|---|
| pm | soccer | 1749 | 276183 | 87% | 0.020 | 19% | 0.5 (n=4336) | - | - |
| pm | tennis | 1441 | 114626 | 92% | 0.010 | 23% | 0.5 (n=59569) | - | - |
| pm | esports | 3317 | 87981 | 76% | 0.030 | 19% | 0.5 (n=18579) | - | - |
| pm | table-tennis | 1540 | 60771 | 95% | 0.020 | 31% | 0.5 (n=30688) | - | - |
| pm | basketball | 742 | 58218 | 83% | 0.050 | 25% | 0.5 (n=10551) | - | - |
| pm | football | 483 | 25189 | 83% | 0.005 | 17% | 1.1 (n=1099) | - | - |
| pm | climate | 215 | 10774 | 75% | 0.050 | 22% | - (n=0) | - | - |
| pm | ice-hockey | 99 | 10129 | 84% | 0.060 | 15% | 0.7 (n=548) | - | - |
| pm | motorsports | 159 | 8546 | 40% | 0.040 | 14% | - (n=0) | - | - |
| pm | cricket | 9 | 3911 | 95% | 0.030 | 11% | 1.0 (n=590) | - | - |
| pm | misc | 47 | 3778 | 93% | 0.010 | 12% | - (n=0) | - | - |
| pm | beach-volleyball | 67 | 3072 | 85% | 0.010 | 23% | 0.5 (n=1681) | - | - |
| pm | golf | 159 | 2779 | 2% | 0.121 | 2% | - (n=0) | - | - |
| pm | darts | 32 | 1101 | 92% | 0.080 | 29% | 0.5 (n=125) | - | - |
| pm | mma | 14 | 759 | 95% | 0.020 | 4% | - (n=0) | - | - |
| pm | baseball | 2 | 395 | 95% | 0.060 | 21% | 0.5 (n=11) | - | - |
| pm | rugby | 20 | 359 | 73% | 0.450 | 23% | - (n=0) | - | - |
| pm | macro | 83 | 279 | 0% | - | 1% | - (n=0) | - | - |
| pm | boxing | 4 | 165 | 95% | 0.030 | 56% | - (n=0) | - | - |
| pm | pickleball | 13 | 115 | 66% | 0.270 | 11% | - (n=0) | - | - |
| k | KXNCAAFGAME College Football Game | 726 | 652184 | 98% | 0.030 | 1% | - | 8% | 100 |
| k | KXNFLPASSYDSPRECISE Pass Yards Precise | 16856 | 175213 | 0% | 0.390 | 0% | - | 0% | 1 |
| k | KXNFLGAME NFL Game | 58 | 140630 | 99% | 0.010 | 2% | - | 3% | 115719 |
| k | KXNBA3PT NBA Player Threes | 1432 | 137619 | 82% | 0.080 | 16% | - | 24% | 29 |
| k | KXCS2MAP Counter-Strike 2 Map Win | 480 | 107953 | 93% | 0.500 | 6% | - | 19% | 110 |
| k | KXNCAAFSPREAD College Football Spread | 2707 | 79139 | 62% | 0.040 | 3% | - | 16% | 129 |
| k | KXNBAAST NBA Player Assists | 1234 | 70849 | 81% | 0.070 | 15% | - | 25% | 25 |
| k | KXESOCCERGAME eSoccer Game | 4239 | 68771 | 25% | 0.440 | 6% | - | 25% | 33 |
| k | KXNCAAFTEAMTOTAL College Football Team To | 1305 | 67350 | 76% | 0.020 | 2% | - | 25% | 325 |
| k | KXNBAREB NBA Player Rebounds | 1335 | 62878 | 76% | 0.080 | 18% | - | 22% | 36 |
| k | KXNBAPTS NBA Player Points | 1311 | 62409 | 77% | 0.050 | 20% | - | 24% | 42 |
| k | KXNCAAFTOTAL College Football Total P | 1942 | 52914 | 59% | 0.170 | 5% | - | 18% | 132 |
| k | KXNBA3PTPROT NBA Player Threes Protec | 1386 | 50515 | 35% | 0.150 | 2% | - | 21% | 47 |
| k | KXNBA1HTEAMTOTAL NBA 1st Half Team Total | 528 | 37907 | 61% | 0.260 | 12% | - | 22% | 113 |
| k | KXNBA1HTOTAL NBA 1st Half Total | 456 | 31286 | 69% | 0.040 | 9% | - | 24% | 108 |
| k | KXATPSETWINNER ATP Set Winner | 212 | 30966 | 92% | 0.030 | 4% | - | 11% | 178 |
| k | KXNCAAF1H College Football 1st Hal | 1050 | 30306 | 86% | 0.820 | 1% | - | 27% | 133 |
| k | KXNBA1HSPREAD NBA 1st Half Spread | 456 | 30201 | 69% | 0.030 | 8% | - | 15% | 140 |
| k | KXNBAASTPROT NBA Player Assists Prote | 1198 | 26656 | 27% | 0.150 | 2% | - | 22% | 100 |
| k | KXNHLGOAL NHL Goalscorer | 1819 | 26154 | 20% | 0.020 | 10% | - | 20% | 55 |
| k | KXMLSSCORE Correct Score | 450 | 25883 | 53% | 0.020 | 3% | - | 14% | 1238 |
| k | KXNBA2HSPREAD NBA 2nd Half Spread | 456 | 25269 | 74% | 0.130 | 25% | - | 28% | 200 |
| k | KXLIGAMXSCORE Correct Score | 270 | 24788 | 55% | 0.020 | 3% | - | 13% | 800 |
| k | KXNBAREBPROT NBA Player Rebounds Prot | 1288 | 24672 | 24% | 0.540 | 3% | - | 18% | 25 |
| k | KXWTASETWINNER WTA Set Winner | 272 | 24533 | 74% | 0.040 | 4% | - | 25% | 114 |
| k | KXNBA2HTOTAL NBA 2nd Half Total | 456 | 24298 | 75% | 0.160 | 23% | - | 25% | 107 |
| k | KXNCAAF1HSPREAD College Football 1st Hal | 1083 | 23344 | 42% | 0.020 | 8% | - | 30% | 344 |
| k | KXATPCHALLENGERMATCH Challenger ATP  | 274 | 22604 | 88% | 0.010 | 8% | - | 5% | 594 |
| k | KXNBAPTSPROT NBA Player Points Protec | 1221 | 22108 | 27% | 0.640 | 2% | - | 16% | 94 |
| k | KXNFLTOTALPRECISE Total Precise | 2128 | 22039 | 4% | 0.060 | 2% | - | 21% | 2 |
| k | KXNEXTTEAMNHL Next Team NHL | 230 | 18860 | 0% | 0.130 | 0% | - | 23% | 341 |
| k | KXNFLRECYDS Pro Football Receiving Y | 1653 | 18823 | 0% | - | 0% | - | 0% | - |
| k | KXNBA2QSPREAD NBA 2nd Quarter Spread | 312 | 18673 | 71% | 0.050 | 9% | - | 18% | 168 |
| k | KXNFLRECYDSPROT Receiving Yards Protecte | 1776 | 18659 | 12% | 0.740 | 5% | - | 15% | 19 |
| k | KXNBA2QTOTAL NBA 2nd Quarter Total | 312 | 17190 | 67% | 0.050 | 8% | - | 34% | 180 |
| k | KXNBA3QSPREAD NBA 3rd Quarter Spread | 312 | 15940 | 72% | 0.040 | 9% | - | 34% | 153 |
| k | KXNBA1QSPREAD NBA 1st Quarter Spread | 286 | 15084 | 63% | 0.050 | 7% | - | 30% | 161 |
| k | KXNBA1QTOTAL NBA 1st Quarter Total | 286 | 14717 | 63% | 0.050 | 8% | - | 24% | 189 |
| k | KXNBAPRA NBA Player Points + Rebo | 512 | 14391 | 64% | 0.300 | 16% | - | 12% | 10 |
| k | KXNBA3QTOTAL NBA 3rd Quarter Total | 312 | 14301 | 70% | 0.050 | 9% | - | 34% | 144 |

## Schema notes (raw keys seen)

- polymarket: active, archived, category, chatChannel, closed, combos, createdAt, description, elapsed, endDate, ended, eventState, fixtureId, gameId, hidden, id, insiderTradingRules, live, marketCounts, marketGroups, markets, metadata, participants, payoutEstimateMessage, payoutEstimateTime, period, primaryTag, score, seriesSlug, slug, sortType, sportradarGameId, startDate, startTime, streamProvider, streamRequiresAuth, tags, teams, ticker, title, updatedAt
- kalshi: can_close_early, close_time, created_time, custom_strike, early_close_condition, event_ticker, exchange_index, expected_expiration_time, expiration_time, expiration_value, floor_strike, last_price_dollars, latest_expiration_time, market_type, no_ask_dollars, no_bid_dollars, no_sub_title, notional_value_dollars, occurrence_datetime, open_interest_fp, open_time, previous_price_dollars, previous_yes_ask_dollars, previous_yes_bid_dollars, price_level_structure, price_ranges, primary_participant_key, result, rules_primary, rules_secondary, settlement_bounds_type, settlement_timer_seconds, settlement_value_dollars, status, strike_type, ticker, title, updated_time, volume_24h_fp, volume_fp, yes_ask_dollars, yes_ask_size_fp, yes_bid_dollars, yes_bid_size_fp, yes_sub_title

