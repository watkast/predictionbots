# Mr. P — sports radar

Updated 2026-11-02T11:39:13Z by `run-20261102T0816-41411803521` (last 7 days). Read-only scanner of every sports market on Polymarket US and Kalshi — it never places orders.
Kit: `mrp/mrp_sports_radar.py` on the `mrp` branch. Raw tape: `mrp/radar/<run>/`.

# Sports radar report

records 4,660,962 | 2026-10-30 11:38Z → 11:38Z | runs 22 | pairs matched 1460 | errors {'radar': 18, 'sp.k.series_poll:KXATPEXACTMATCH': 10, 'sp.k.series_poll:KXATPMATCH': 10, 'sp.k.series_poll:KXATPSETWINNER': 10, 'sp.k.series_poll:KXAUTBUNDESTOTAL': 4, 'sp.k.series_poll:KXEFLL11H': 6, 'sp.k.series_poll:KXEFLL11HSPREAD': 10, 'sp.k.series_poll:KXHNLTOTAL': 6, 'sp.k.series_poll:KXLALIGABTTS': 9, 'sp.k.series_poll:KXLALIGASCORE': 6, 'sp.k.series_poll:KXLALIGASPREAD': 8, 'sp.k.always:KXNFLGAME': 7, 'sp.k.series_poll:KXATPCHALLENGERMATCH': 7, 'sp.k.series_poll:KXEFLL11HBTTS': 10, 'sp.k.series_poll:KXLALIGA2H': 6, 'sp.k.series_poll:KXCS2MAP': 6, 'sp.k.series_poll:KXEFLL11HTOTAL': 8, 'sp.k.series_poll:KXLALIGA2HBTTS': 8, 'sp.k.series_poll:KXLALIGA2HSPREAD': 6, 'sp.k.series_poll:KXLALIGA2HTOTAL': 4, 'sp.k.series_poll:KXLALIGACORNERS': 8, 'sp.k.series_poll:KXLALIGAGAME': 6, 'sp.k.series_poll:KXLALIGAGOAL': 6, 'sp.k.series_poll:KXAUTBUNDESGAME': 2, 'sp.k.series_poll:KXCZEFLTOTAL': 7, 'sp.k.series_poll:KXELITESERIENTOTAL': 2, 'sp.k.series_poll:KXEREDIVISIETOTAL': 2, 'sp.k.always:KXNCAAFGAME': 7, 'sp.k.series_poll:KXLIGUE11HBTTS': 3, 'sp.k.series_poll:KXLIGUE11HSCORE': 4, 'sp.k.series_poll:KXLIGUE11H': 4, 'sp.k.series_poll:KXLIGUE11HSPREAD': 1}

## Catalogue (latest inventory, 11:30Z)

Polymarket US sports events 4422 of 5916 active events; Kalshi near-term sports markets 740 in 333 events; calls so far {'pm': 45, 'k': 420}; MB {'pm': 157891796, 'k': 69568125}

| venue | sport / league / type | markets | two-sided | med spread | vol 24h |
|---|---|---|---|---|---|
| pm | football / nfl / futures | 3782 | 68% | 0.010 | 0 |
| pm | football / cfb / futures | 1598 | 80% | 0.010 | 0 |
| pm | basketball / nba / futures | 1380 | 61% | 0.020 | 0 |
| pm | ice-hockey / nhl / futures | 779 | 98% | 0.010 | 0 |
| pm | basketball / wcbb / basketball_team_full_game_winner | 675 | 34% | 0.195 | 0 |
| pm | basketball / cbb / basketball_team_full_game_winner | 655 | 27% | 0.030 | 0 |
| k | KXNCAAFGAME / College Football Game | 506 | 100% | 0.100 | 735070 |
| pm | golf / worlwide / futures | 470 | 0% | 0.480 | 0 |
| pm | golf / lpga / futures | 440 | 0% | - | 0 |
| pm | soccer / epl / futures | 435 | 86% | 0.010 | 0 |
| pm | golf / abudhabc / futures | 352 | 0% | - | 0 |
| pm | basketball / cbb / futures | 317 | 85% | 0.010 | 0 |
| pm | tennis / utr / tennis_match_winner | 277 | 23% | 0.420 | 0 |
| pm | soccer / ucl / futures | 276 | 78% | 0.010 | 0 |
| pm | baseball / mlb / futures | 264 | 26% | 0.001 | 0 |
| pm | football / cfb / football_team_full_game_winner | 211 | 84% | 0.083 | 0 |
| pm | table-tennis / setkameua / table_tennis_match_winner | 192 | 90% | 0.170 | 0 |
| pm | tennis / itfme / tennis_match_winner | 186 | 83% | 0.010 | 0 |
| pm | macro /  / futures | 150 | 75% | 0.010 | 0 |
| pm | soccer / lal / futures | 146 | 66% | 0.010 | 0 |
| pm | boxing / boxing / futures | 145 | 0% | - | 0 |
| pm | mma / ufc / futures | 142 | 82% | 0.010 | 0 |
| pm | tennis / atp / tennis_match_winner | 118 | 85% | 0.010 | 0 |
| pm | basketball / nba / basketball_team_full_game_winner | 113 | 70% | 0.270 | 0 |
| pm | tennis / itfwo / tennis_match_winner | 111 | 86% | 0.010 | 0 |
| pm | tennis / atp / futures | 107 | 40% | 0.010 | 0 |
| pm | soccer / sea / futures | 86 | 81% | 0.010 | 0 |
| pm | tennis / wta / futures | 79 | 42% | 0.010 | 0 |
| pm | soccer / bun / futures | 79 | 82% | 0.010 | 0 |
| pm | soccer / lg1 / futures | 77 | 84% | 0.010 | 0 |
| pm | soccer / j2 / soccer_team_full_time_winner | 60 | 67% | 0.025 | 0 |
| pm | tennis / atpdb / tennis_match_winner | 59 | 49% | 0.320 | 0 |
| pm | tennis / wta / tennis_match_winner | 58 | 86% | 0.010 | 0 |
| pm | motorsports / nascar / futures | 57 | 19% | 0.030 | 0 |
| pm | soccer / uecl / soccer_team_full_time_winner | 55 | 98% | 0.030 | 0 |
| pm | table-tennis / czechligapro / table_tennis_match_winner | 55 | 0% | - | 0 |
| pm | soccer / ucl / soccer_team_full_time_winner | 54 | 100% | 0.010 | 0 |
| pm | soccer / uel / soccer_team_full_time_winner | 54 | 100% | 0.020 | 0 |
| pm | soccer / mls / futures | 53 | 91% | 0.010 | 0 |
| pm | golf / masttour / futures | 52 | 100% | 0.499 | 0 |
| pm | soccer / acle / soccer_team_full_time_winner | 48 | 88% | 0.020 | 0 |
| pm | technology /  / futures | 42 | 74% | 0.010 | 0 |
| pm | macro / usgas / futures | 40 | 2% | 0.500 | 0 |
| pm | motorsports / f1 / futures | 38 | 34% | 0.011 | 0 |
| pm | soccer / lmx / futures | 36 | 28% | 0.045 | 0 |
| pm | soccer / uel / futures | 36 | 3% | 0.150 | 0 |
| pm | soccer / uecl / futures | 36 | 0% | - | 0 |
| pm | soccer / sea / soccer_team_full_time_winner | 36 | 100% | 0.010 | 0 |
| pm | soccer / ekst / soccer_team_full_time_winner | 36 | 61% | 0.060 | 0 |
| pm | soccer / serca / soccer_team_full_time_winner | 36 | 44% | 0.475 | 0 |
| pm | soccer / eflch / soccer_team_full_time_winner | 36 | 100% | 0.020 | 0 |
| pm | table-tennis / setkamemd / table_tennis_match_winner | 36 | 44% | 0.090 | 0 |
| pm | soccer / lal / soccer_team_full_time_winner | 33 | 100% | 0.010 | 0 |
| pm | soccer / epl / soccer_team_full_time_winner | 33 | 100% | 0.010 | 0 |
| pm | soccer / ligpor / soccer_team_full_time_winner | 33 | 94% | 0.060 | 0 |
| pm | soccer / tff1 / soccer_team_full_time_winner | 33 | 39% | 0.480 | 0 |
| pm | soccer / alsv / soccer_team_full_time_winner | 33 | 70% | 0.060 | 0 |
| pm | ice-hockey / nhl / hockey_team_full_game_winner | 33 | 100% | 0.010 | 0 |
| k | KXNFLGAME / NFL Game | 32 | 100% | 0.010 | 1991568 |
| pm | table-tennis / setkamecz / table_tennis_match_winner | 31 | 100% | 0.150 | 0 |

## Opportunities

| kind | distinct | hits | max margin $/contract | max persistence | fresh-BBO still open |
|---|---|---|---|---|---|
| decided_k | 769 | 61559 | 0.9893 | 169 min | 0/0 |
| decided_pm | 23 | 488 | 0.9947 | 28 min | 182/488 |
| decided_pm_closed | 14 | 144 | 0.9893 | 30 min | 0/144 |
| dutch_k | 16 | 71 | 0.0817 | 4 min | 0/0 |
| dutch_k_sell | 3 | 6 | 0.0107 | 0 min | 0/0 |
| dutch_pm | 64 | 3143 | 0.5316 | 50 min | 0/0 |
| implication_k | 6796 | 400267 | 0.9786 | 110 min | 0/0 |
| lag_k_settled | 188 | 34532 | 0.9973 | 273 min | 28936/33511 |
| lag_k_settled_closed | 165 | 2545 | 0.9973 | 272 min | 0/2545 |

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
- **lag_k_settled** darts — Scott Robertson vs. Andy Baetens — bid 0.04 ask 0.20 sell_yes @ 0.04 | margin 0.5127 | 95 min, 377 hits | fresh bbo 0.04/0.20 depth 3/2 | score 2-3 LIVE
- **lag_k_settled** esports — World Squad vs. CIS Squad — bid - ask 0.01 buy_yes @ 0.01 | margin 0.9893 | 77 min, 390 hits | fresh bbo -/0.01 depth 0/13 | score 0-0 Game 1
- **lag_k_settled** soccer — AC Milan vs. FC Internazionale Milano — bid 0.44 ask 0.45 sell_yes @ 0.44 | margin 0.7163 | 108 min, 353 hits | fresh bbo 0.44/0.45 depth 25/33 | score 2-1 1H
- **lag_k_settled** soccer — AC Milan vs. FC Internazionale Milano — bid 0.26 ask 0.27 sell_yes @ 0.26 | margin 0.2563 | 108 min, 353 hits | fresh bbo 0.26/0.27 depth 23/55 | score 2-1 1H
- **lag_k_settled** soccer — AC Milan vs. FC Internazionale Milano — bid 0.29 ask 0.31 buy_yes @ 0.31 | margin 0.8832 | 108 min, 353 hits | fresh bbo 0.29/0.31 depth 19/37 | score 2-1 1H
- **lag_k_settled** basketball — Villanova (W) vs. Notre Dame (W) — bid 0.01 ask 0.02 sell_yes @ 0.01 | margin 0.2563 | 92 min, 364 hits | fresh bbo -/0.02 depth 0/36 | score 45-65 H2

## Live paper trades (no orders; Kalshi prices, taker fees)

Ledger L2-2026-11-01 (earlier ledgers excluded: L1)

**Total closed P&L: $-335.75 on $1288.75 staked (-26.1%)**

| rule | entries | closed | winners | staked | P&L | ROI |
|---|---|---|---|---|---|---|
| R1 anchor [ncaaf] | 26 | 26 | 11 | $262.99 | $-34.99 | -13% |
| R1 anchor [nfl] | 5 | 5 | 1 | $50.90 | $-31.90 | -63% |
| R2 q1cheap [ncaaf] | 37 | 37 | 2 | $194.50 | $-142.50 | -73% |
| R2 q1cheap [nfl] | 6 | 6 | 1 | $31.46 | $-2.46 | -8% |
| R3 blowout [ncaaf] | 16 | 16 | 1 | $339.32 | $-197.32 | -58% |
| R4 halftime [ncaaf] | 19 | 19 | 6 | $95.24 | $+9.76 | +10% |
| R6 decided [other] | 16 | 16 | 16 | $314.34 | $+63.66 | +20% |

| time (UTC) | rule | game | team | entry | contracts | why | result |
|---|---|---|---|---|---|---|---|
| 02:11 | R1 anchor | PHI Eagles vs. WAS Commander | Philadelphia | 0.62 | 16 | pregame dog (mid 0.30) leads 10-3 in Q2, ask 0.62 | final score (pending Kalshi settlement): 0.00, $-10.18 |
| 23:01 | R6 decided | Houston Dash vs. Portland Th | Over 0.5 1H goals scored | 0.76 | 26 | 1H (0, 1) > 0.5 | kalshi settled: 1.00, $+5.91 |
| 22:54 | R6 decided | Houston Dash vs. Portland Th | Over 0.5 goals scored | 0.96 | 20 | score 0-1 total 1 > 0.5 | kalshi settled: 1.00, $+0.75 |
| 22:24 | R1 anchor | NE Patriots vs. MIA Dolphins | Miami | 0.39 | 25 | pregame dog (mid 0.24) leads 3-6 in Q2, ask 0.39 | final score (pending Kalshi settlement): 0.00, $-10.17 |
| 22:23 | R6 decided | NE Patriots vs. MIA Dolphins | Both Teams To Score | 0.72 | 27 | both scored 3-6 | kalshi settled: 1.00, $+7.18 |
| 21:40 | R6 decided | NE Patriots vs. MIA Dolphins | Over 2.5 goals scored | 0.71 | 28 | score 3-0 total 3 > 2.5 | kalshi settled: 1.00, $+7.72 |
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
| soccer | KXMLSTOTAL | 1824 | 799 | 24 | 99 | 4 | 0.82 | 188 / $5.63 | 4423 / $44.23 |
| soccer | KXELITESERIENTOTAL | 1513 | 782 | 26 | 94 | 0 | - | 0 / $0.00 | 33 / $0.33 |
| soccer | KXIDNSLTOTAL | 1469 | 1144 | 9 | 32 | 0 | 0.96 | 0 / $0.00 | 82 / $0.82 |
| football | KXNFLTOTALPRECISE | 1307 | 386 | 35 | 109 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXALLSVENSKANTOTAL | 1261 | 891 | 9 | 34 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXEREDIVISIETOTAL | 1183 | 413 | 36 | 120 | 0 | - | 0 / $0.00 | 337 / $3.38 |
| soccer | KXLIGAFTOTAL | 1112 | 1971 | 1 | 12 | 0 | 0.98 | 0 / $0.00 | 0 / $0.00 |
| soccer | KXSERIECTOTAL | 1051 | 1323 | 12 | 41 | 0 | 0.97 | 0 / $0.00 | 165 / $1.65 |
| soccer | KXBELGIANPLTOTAL | 1041 | 458 | 19 | 68 | 0 | 0.89 | 763 / $22.89 | 763 / $7.63 |
| tennis | KXATPSETWINNER | 980 | 60 | 190 | 492 | 0 | - | 0 / $0.00 | 316 / $3.16 |
| tennis | KXWTASETWINNER | 852 | 46 | 160 | 464 | 0 | - | 0 / $0.00 | 156 / $1.57 |
| soccer | KXAUTBUNDESTOTAL | 846 | 405 | 18 | 70 | 0 | 0.01 | 490 / $14.70 | 523 / $5.23 |
| soccer | KXDENSUPERLIGATOTAL | 773 | 662 | 11 | 44 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXBRASILEIROBTOTAL | 616 | 1171 | 3 | 20 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| tennis | KXATPCHALLENGERMATCH | 610 | 180 | 31 | 108 | 0 | - | 0 / $0.00 | 201 / $2.01 |
| soccer | KXTHAIL1TOTAL | 550 | 727 | 4 | 17 | 0 | 0.96 | 0 / $0.00 | 0 / $0.00 |
| soccer | KXHUNNB1TOTAL | 543 | 1882 | 4 | 14 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXBUNDESLIGA2TOTAL | 514 | 258 | 8 | 35 | 0 | - | 0 / $0.00 | 586 / $5.86 |
| soccer | KXECULPTOTAL | 436 | 1359 | 1 | 5 | 0 | 0.93 | 0 / $0.00 | 0 / $0.00 |
| soccer | KXDIMAYORTOTAL | 318 | 1348 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| football | KXNFLGAME | 288 | 842 | 0 | 2 | 0 | 0.02 | 0 / $0.00 | 141142 / $1411.43 |
| soccer | KXCZEFNLTOTAL | 277 | 428 | 2 | 12 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXTFF1LIGTOTAL | 252 | 1052 | 3 | 11 | 1 | 0.88 | 1148 / $34.44 | 1148 / $11.48 |
| soccer | KXHNLTOTAL | 251 | 1129 | 2 | 8 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXMYSLTOTAL | 223 | 528 | 2 | 8 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXMLS1HTOTAL | 208 | 637 | 8 | 28 | 3 | 0.61 | 0 / $0.00 | 36 / $0.36 |
| soccer | KXKLEAGUETOTAL | 192 | 556 | 3 | 12 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXAPFDDHTOTAL | 189 | 1707 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
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
| soccer | KXSERIECSPREAD | 76 | 5590 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXBUNDESLIGA2SPREAD | 72 | 228 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXMLSSPREAD | 65 | 590 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXBRASILEIROBBTTS | 57 | 442 | 1 | 4 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| football | KXMLSTOTAL | 56 | 266 | 1 | 4 | 22 | 0.63 | 23789 / $713.66 | 23789 / $237.90 |
| soccer | KXMLS1H | 50 | 633 | 0 | 0 | 2 | 0.63 | 0 / $0.00 | 0 / $0.00 |
| soccer | KXMLSGAME | 39 | 590 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXDENSUPERLIGASPREAD | 38 | 1891 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXSUPERLIGTOTAL | 38 | 378 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXMLS1HBTTS | 38 | 1329 | 1 | 2 | 1 | 0.78 | 0 / $0.00 | 0 / $0.00 |
| soccer | KXARGNACBTOTAL | 38 | 5169 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXSCOCUPTOTAL | 35 | 2799 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXIDNSLBTTS | 22 | 595 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXEREDIVISIEBTTS | 21 | 167 | 1 | 4 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXBUNDESLIGA2BTTS | 19 | 236 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXSLGREECETOTAL | 19 | 2918 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXARGNACBBTTS | 19 | 7012 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| football | KXMLSBTTS | 6 | - | 0 | 0 | 6 | 0.72 | 1850 / $55.50 | 1850 / $18.49 |
| soccer | KXEREDIVISIESPREAD | 4 | 763 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXELITESERIENBTTS | 4 | 5122 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| soccer | KXDENSUPERLIGABTTS | 3 | 1100 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / $0.00 |
| football | KXNFLEQBTTS | 1 | - | 0 | 0 | 1 | 0.54 | 10 / $0.30 | 10 / $0.10 |

Latency counts from when OUR score feed changed (Polymarket's feed lags reality, so true bot speed is faster). Resting-bid columns: contracts that sellers dumped below that price after the decision, and the profit a resting bid there would have made (maker fee ignored).

## Decided-state engine (contracts the live score already settled, still trading)

2742 contracts decided while active; 769 had a price leaving > 0.4c after fees; 630 of those were mispriced AFTER the score was stable (lock tier)

| sport | game | contract | decided | reason | max margin | mispriced for | lock margin | lock depth |
|---|---|---|---|---|---|---|---|---|
| basketball | NY Knicks vs. PHI 76ers | KXNBA1QTOTAL-26OCT30NYKPHI-60 | YES | score 31-42 total 73 > 59.5 | 0.989 | 420s | 0.989 | 3350 |
| basketball | NY Knicks vs. PHI 76ers | KXNBA1QTOTAL-26OCT30NYKPHI-58 | YES | score 31-42 total 73 > 57.5 | 0.989 | 480s | 0.989 | 10805 |
| basketball | NY Knicks vs. PHI 76ers | KXNBA1QTOTAL-26OCT30NYKPHI-56 | YES | score 31-42 total 73 > 55.5 | 0.989 | 569s | 0.989 | 11573 |
| basketball | NY Knicks vs. PHI 76ers | KXNBA1QTOTAL-26OCT30NYKPHI-54 | YES | score 31-42 total 73 > 53.5 | 0.989 | 616s | 0.989 | 8797 |
| basketball | NY Knicks vs. PHI 76ers | KXNBA1QTOTAL-26OCT30NYKPHI-52 | YES | score 31-42 total 73 > 51.5 | 0.989 | 705s | 0.989 | 6187 |
| basketball | CHI Bulls vs. BOS Celtics | KXNBA1QTOTAL-26OCT30CHIBOS-73 | YES | score 37-65 total 102 > 72.5 | 0.989 | 810s | 0.989 | 1255 |
| basketball | CHI Bulls vs. BOS Celtics | KXNBA1QTOTAL-26OCT30CHIBOS-71 | YES | score 37-65 total 102 > 70.5 | 0.989 | 840s | 0.989 | 718 |
| basketball | ORL Magic vs. TOR Raptors | KXNBA1QTOTAL-26OCT30ORLTOR-64 | YES | score 37-33 total 70 > 63.5 | 0.989 | 689s | 0.989 | 6492 |
| basketball | ORL Magic vs. TOR Raptors | KXNBA1QTOTAL-26OCT30ORLTOR-62 | YES | score 37-33 total 70 > 61.5 | 0.989 | 689s | 0.989 | 7444 |
| basketball | ORL Magic vs. TOR Raptors | KXNBA1QTOTAL-26OCT30ORLTOR-60 | YES | score 37-33 total 70 > 59.5 | 0.989 | 720s | 0.989 | 4307 |
| basketball | DET Pistons vs. BKN Nets | KXNBA1QTOTAL-26OCT30DETBKN-70 | YES | score 35-37 total 72 > 69.5 | 0.989 | 254s | 0.989 | 1773 |
| basketball | DET Pistons vs. BKN Nets | KXNBA1QTOTAL-26OCT30DETBKN-68 | YES | score 35-37 total 72 > 67.5 | 0.989 | 420s | 0.989 | 1094 |
| basketball | DET Pistons vs. BKN Nets | KXNBA1QTOTAL-26OCT30DETBKN-66 | YES | score 35-37 total 72 > 65.5 | 0.989 | 510s | 0.989 | 1103 |
| basketball | DET Pistons vs. BKN Nets | KXNBA1QTOTAL-26OCT30DETBKN-64 | YES | score 35-37 total 72 > 63.5 | 0.989 | 569s | 0.989 | 4269 |
| basketball | DET Pistons vs. BKN Nets | KXNBA1QTOTAL-26OCT30DETBKN-62 | YES | score 35-37 total 72 > 61.5 | 0.989 | 569s | 0.989 | 4369 |
| basketball | DET Pistons vs. BKN Nets | KXNBA1QTOTAL-26OCT30DETBKN-60 | YES | score 35-37 total 72 > 59.5 | 0.989 | 569s | 0.989 | 3713 |
| basketball | DET Pistons vs. BKN Nets | KXNBA1QTOTAL-26OCT30DETBKN-58 | YES | score 35-37 total 72 > 57.5 | 0.989 | 646s | 0.989 | 4360 |
| basketball | DET Pistons vs. BKN Nets | KXNBA1QTOTAL-26OCT30DETBKN-56 | YES | score 35-37 total 72 > 55.5 | 0.989 | 705s | 0.989 | 661 |
| basketball | DET Pistons vs. BKN Nets | KXNBA1QTOTAL-26OCT30DETBKN-54 | YES | score 35-37 total 72 > 53.5 | 0.989 | 781s | 0.989 | 171 |
| basketball | DET Pistons vs. BKN Nets | KXNBA1QTOTAL-26OCT30DETBKN-52 | YES | score 35-37 total 72 > 51.5 | 0.989 | 781s | 0.989 | 1398 |
| basketball | DET Pistons vs. BKN Nets | KXNBA1QTOTAL-26OCT30DETBKN-50 | YES | score 35-37 total 72 > 49.5 | 0.989 | 810s | 0.989 | 202 |
| basketball | ORL Magic vs. TOR Raptors | KXNBA1QTOTAL-26OCT30ORLTOR-66 | YES | score 37-33 total 70 > 65.5 | 0.989 | 420s | 0.989 | 5826 |
| basketball | ORL Magic vs. TOR Raptors | KXNBA1QTOTAL-26OCT30ORLTOR-68 | YES | score 37-33 total 70 > 67.5 | 0.989 | 360s | 0.989 | 5738 |
| basketball | NY Knicks vs. PHI 76ers | KXNBA2QTOTAL-26OCT30NYKPHI-70 | YES | score 56-65 total 121 > 69.5 | 0.989 | 2087s | 0.989 | 2310 |
| basketball | NY Knicks vs. PHI 76ers | KXNBA2QTOTAL-26OCT30NYKPHI-68 | YES | score 56-65 total 121 > 67.5 | 0.989 | 2087s | 0.989 | 2084 |

## Close / settlement latency (how clunky each venue is after the final whistle)

Kalshi: settlement_ts − close_time per series (negative = settled before the scheduled close)

| series | n | median | p90 |
|---|---|---|---|
| KXNFLPASSYDSPRECISE Pass Yards Precise | 12485 | 4.0 min | 4.1 min |
| KXESOCCERGAME eSoccer Game | 3982 | 4.0 min | 4.1 min |
| KXNCAAFSPREAD College Football Spread | 2311 | 4.0 min | 4.1 min |
| KXNCAAFTOTAL College Football Total Points | 1680 | 4.0 min | 4.1 min |
| KXNFLTOTALPRECISE Total Precise | 1248 | 4.0 min | 4.1 min |
| KXNCAAFTEAMTOTAL College Football Team Total Po | 1193 | 4.0 min | 4.1 min |
| KXNFLRECYDS Pro Football Receiving Yards | 1188 | 2.0 min | 2.1 min |
| KXNFLRECYDSPROT Receiving Yards Protected | 1132 | 6.0 min | 6.1 min |
| KXNHLGOAL NHL Goalscorer | 1116 | 3.0 min | 3.1 min |
| KXNBA3PT NBA Player Threes | 1078 | 2.0 min | 2.1 min |
| KXNCAAF1HSPREAD College Football 1st Half Spre | 1048 | 4.0 min | 4.1 min |
| KXNBA3PTPROT NBA Player Threes Protected | 996 | 2.5 min | 2.6 min |
| KXNBAREB NBA Player Rebounds | 976 | 2.0 min | 2.1 min |
| KXNBAREBPROT NBA Player Rebounds Protected | 942 | 2.5 min | 2.6 min |
| KXLIGAPROMATCH Russia Liga Pro Match | 924 | 4.0 min | 4.1 min |
| KXNBAPTS NBA Player Points | 886 | 2.0 min | 2.1 min |
| KXNFLRECPROT Receptions Protected | 850 | 6.0 min | 6.1 min |
| KXNBATEAMTOTAL NBA Team Total | 848 | 2.5 min | 2.6 min |
| KXNBAPTSPROT NBA Player Points Protected | 820 | 2.5 min | 2.6 min |
| KXNBAAST NBA Player Assists | 794 | 2.0 min | 2.1 min |
| KXNHLPTS Pro Hockey Points | 794 | 3.0 min | 3.1 min |
| KXNFLREC Pro Football Player Receptions | 791 | 2.0 min | 2.1 min |
| KXNBAASTPROT NBA Player Assists Protected | 788 | 2.5 min | 2.6 min |
| KXNCAAF2HSPREAD College Football 2nd Half Spre | 720 | 4.0 min | 4.1 min |
| KXNCAAF1HTOTAL College Football 1st Half Tota | 697 | 4.0 min | 4.1 min |
| KXNBASPREAD NBA Spread | 611 | 1.8 min | 1.8 min |
| KXNBATOTAL NBA Total | 610 | 1.8 min | 1.8 min |
| KXMLSGOAL Goalscorer | 597 | 6.0 min | 6.1 min |
| KXNHLFIRSTGOAL NHL First Goal | 596 | 6.0 min | 6.0 min |
| KXNHLAST Pro Hockey Assists | 569 | 6.0 min | 6.1 min |
| KXNFLRSHYDSPROT Rushing Yards Protected | 549 | 6.0 min | 6.1 min |
| KXEBASKETBALLGAME eBasketball Game | 508 | 4.0 min | 4.1 min |
| KXNFLTDPROT Pro Football Touchdowns Protec | 479 | 6.0 min | 6.1 min |
| KXNCAAF2HTOTAL College Football 2nd Half Tota | 477 | 4.0 min | 4.1 min |
| KXNBA1HTEAMTOTAL NBA 1st Half Team Total | 462 | 2.5 min | 2.6 min |
| KXNFLRSHYDS Pro Football Rushing Yards | 458 | 2.0 min | 2.1 min |
| KXMLSSCORE Correct Score | 444 | 6.0 min | 6.1 min |
| KXNFLTD Pro Football Touchdowns | 426 | 2.0 min | 2.1 min |
| KXNBA1HTOTAL NBA 1st Half Total | 399 | 2.5 min | 2.6 min |
| KXNBA1HSPREAD NBA 1st Half Spread | 399 | 2.5 min | 2.6 min |

## Participant fingerprint (per sport; 60 s snapshots)

change% = share of scan cycles (60 s) where the best quote moved; react = median minutes from a score change to the next quote move (humans: slow, bursty, round sizes; bots: constant cadence, odd/constant sizes, instant reaction)

| venue | sport | markets | snapshots | two-sided | med spread | change% | react (min) | round sizes | med size |
|---|---|---|---|---|---|---|---|---|---|
| pm | soccer | 1905 | 276636 | 87% | 0.020 | 19% | 0.5 (n=4360) | - | - |
| pm | tennis | 1525 | 111649 | 91% | 0.010 | 23% | 0.5 (n=54536) | - | - |
| pm | esports | 3320 | 86789 | 76% | 0.030 | 19% | 0.5 (n=18267) | - | - |
| pm | table-tennis | 1531 | 59166 | 95% | 0.030 | 31% | 0.5 (n=29430) | - | - |
| pm | basketball | 763 | 57566 | 83% | 0.050 | 25% | 0.5 (n=10107) | - | - |
| pm | football | 120 | 22436 | 91% | 0.005 | 17% | 1.1 (n=1098) | - | - |
| pm | climate | 179 | 10883 | 76% | 0.050 | 22% | - (n=0) | - | - |
| pm | ice-hockey | 91 | 9569 | 84% | 0.070 | 15% | 0.7 (n=523) | - | - |
| pm | motorsports | 159 | 8546 | 40% | 0.040 | 14% | - (n=0) | - | - |
| pm | misc | 47 | 3778 | 93% | 0.010 | 12% | - (n=0) | - | - |
| pm | beach-volleyball | 69 | 3064 | 85% | 0.010 | 24% | 0.5 (n=1630) | - | - |
| pm | cricket | 8 | 2711 | 93% | 0.030 | 10% | 1.0 (n=412) | - | - |
| pm | golf | 155 | 871 | 3% | 0.169 | 4% | - (n=0) | - | - |
| pm | darts | 32 | 806 | 90% | 0.080 | 27% | 0.5 (n=125) | - | - |
| pm | mma | 14 | 759 | 95% | 0.020 | 4% | - (n=0) | - | - |
| pm | rugby | 20 | 337 | 72% | 0.450 | 22% | - (n=0) | - | - |
| pm | macro | 98 | 314 | 0% | - | 0% | - (n=0) | - | - |
| pm | baseball | 2 | 199 | 89% | 0.070 | 14% | 0.9 (n=8) | - | - |
| pm | boxing | 4 | 165 | 95% | 0.030 | 56% | - (n=0) | - | - |
| pm | pickleball | 13 | 101 | 75% | 0.270 | 14% | - (n=0) | - | - |
| k | KXNCAAFGAME College Football Game | 720 | 646698 | 98% | 0.040 | 2% | - | 8% | 71 |
| k | KXNFLPASSYDSPRECISE Pass Yards Precise | 15652 | 185544 | 0% | 0.390 | 0% | - | 0% | 1 |
| k | KXNBA3PT NBA Player Threes | 1533 | 145496 | 82% | 0.080 | 13% | - | 24% | 31 |
| k | KXNFLGAME NFL Game | 56 | 135548 | 99% | 0.010 | 2% | - | 3% | 115421 |
| k | KXCS2MAP Counter-Strike 2 Map Win | 496 | 106161 | 93% | 0.470 | 5% | - | 19% | 100 |
| k | KXNBAAST NBA Player Assists | 1138 | 79111 | 84% | 0.070 | 12% | - | 25% | 27 |
| k | KXNBAPTS NBA Player Points | 1296 | 69307 | 81% | 0.050 | 14% | - | 23% | 42 |
| k | KXESOCCERGAME eSoccer Game | 4347 | 68668 | 23% | 0.460 | 6% | - | 27% | 35 |
| k | KXNBAREB NBA Player Rebounds | 1432 | 64431 | 78% | 0.080 | 16% | - | 22% | 36 |
| k | KXNBA3PTPROT NBA Player Threes Protec | 1484 | 58105 | 35% | 0.150 | 2% | - | 19% | 105 |
| k | KXNCAAFSPREAD College Football Spread | 2631 | 57724 | 50% | 0.090 | 4% | - | 12% | 75 |
| k | KXNCAAFTEAMTOTAL College Football Team To | 1259 | 55350 | 72% | 0.020 | 2% | - | 25% | 383 |
| k | KXNCAAFTOTAL College Football Total P | 1889 | 39524 | 48% | 0.140 | 4% | - | 16% | 135 |
| k | KXNBA1HTEAMTOTAL NBA 1st Half Team Total | 704 | 36598 | 62% | 0.260 | 15% | - | 23% | 123 |
| k | KXNBAASTPROT NBA Player Assists Prote | 1111 | 33342 | 28% | 0.150 | 2% | - | 17% | 162 |
| k | KXATPSETWINNER ATP Set Winner | 240 | 32208 | 92% | 0.030 | 4% | - | 11% | 164 |
| k | KXMLSSCORE Correct Score | 450 | 31078 | 52% | 0.020 | 3% | - | 14% | 1192 |
| k | KXNCAAF1H College Football 1st Hal | 1047 | 30303 | 86% | 0.820 | 1% | - | 27% | 133 |
| k | KXNBA1HTOTAL NBA 1st Half Total | 608 | 29387 | 65% | 0.040 | 10% | - | 27% | 144 |
| k | KXNBA1HSPREAD NBA 1st Half Spread | 608 | 29290 | 67% | 0.030 | 10% | - | 15% | 144 |
| k | KXNBAPTSPROT NBA Player Points Protec | 1204 | 26085 | 26% | 0.750 | 2% | - | 12% | 162 |
| k | KXLIGAMXSCORE Correct Score | 270 | 25148 | 54% | 0.020 | 3% | - | 13% | 800 |
| k | KXNBA2HSPREAD NBA 2nd Half Spread | 646 | 25109 | 71% | 0.130 | 20% | - | 28% | 123 |
| k | KXWTASETWINNER WTA Set Winner | 276 | 25094 | 77% | 0.050 | 4% | - | 27% | 71 |
| k | KXATPCHALLENGERMATCH Challenger ATP  | 308 | 24645 | 89% | 0.010 | 8% | - | 5% | 540 |
| k | KXNBAREBPROT NBA Player Rebounds Prot | 1380 | 24326 | 25% | 0.530 | 4% | - | 17% | 33 |
| k | KXNBA2HTOTAL NBA 2nd Half Total | 646 | 23655 | 73% | 0.160 | 20% | - | 25% | 101 |
| k | KXNCAAF1HSPREAD College Football 1st Hal | 1062 | 23323 | 42% | 0.020 | 8% | - | 30% | 344 |
| k | KXNFLTOTALPRECISE Total Precise | 1976 | 22799 | 4% | 0.060 | 2% | - | 21% | 2 |
| k | KXNCAAMBTOTAL Men's College Basketball | 2377 | 21562 | 95% | 0.110 | 2% | - | 30% | 49 |
| k | KXNFLRECYDSPROT Receiving Yards Protecte | 1626 | 19862 | 11% | 0.740 | 5% | - | 15% | 19 |
| k | KXNHLGOAL NHL Goalscorer | 1176 | 19439 | 26% | 0.020 | 11% | - | 20% | 64 |
| k | KXNEXTTEAMNHL Next Team NHL | 230 | 18860 | 0% | 0.130 | 0% | - | 23% | 341 |
| k | KXNFLRECYDS Pro Football Receiving Y | 1605 | 18316 | 0% | - | 0% | - | 0% | - |
| k | KXMLSTOTAL MLS Total | 209 | 17862 | 86% | 0.050 | 2% | - | 12% | 190 |
| k | KXNBA2QSPREAD NBA 2nd Quarter Spread | 416 | 17614 | 65% | 0.040 | 11% | - | 18% | 168 |
| k | KXNCAAMBSPREAD Men's College Basketball | 1945 | 16179 | 97% | 0.100 | 1% | - | 35% | 50 |
| k | KXNBA2QTOTAL NBA 2nd Quarter Total | 403 | 15760 | 60% | 0.050 | 11% | - | 34% | 159 |
| k | KXNBA1QSPREAD NBA 1st Quarter Spread | 338 | 14231 | 59% | 0.040 | 12% | - | 32% | 200 |
| k | KXNCAAF2HSPREAD College Football 2nd Hal | 720 | 14148 | 40% | 0.050 | 7% | - | 12% | 8 |

## Schema notes (raw keys seen)

- polymarket: active, archived, category, chatChannel, closed, combos, createdAt, description, elapsed, endDate, ended, eventState, fixtureId, gameId, hidden, id, insiderTradingRules, live, marketCounts, marketGroups, markets, metadata, participants, payoutEstimateMessage, payoutEstimateTime, period, primaryTag, score, seriesSlug, slug, sortType, sportradarGameId, startDate, startTime, streamProvider, streamRequiresAuth, tags, teams, ticker, title, updatedAt
- kalshi: can_close_early, close_time, created_time, early_close_condition, event_ticker, exchange_index, expected_expiration_time, expiration_time, expiration_value, floor_strike, last_price_dollars, latest_expiration_time, market_type, no_ask_dollars, no_bid_dollars, no_sub_title, notional_value_dollars, occurrence_datetime, open_interest_fp, open_time, previous_price_dollars, previous_yes_ask_dollars, previous_yes_bid_dollars, price_level_structure, price_ranges, result, rules_primary, rules_secondary, settlement_bounds_type, settlement_timer_seconds, status, strike_type, ticker, title, updated_time, volume_24h_fp, volume_fp, yes_ask_dollars, yes_ask_size_fp, yes_bid_dollars, yes_bid_size_fp, yes_sub_title

