# Mr. P — sports radar

Updated 2026-11-03T02:47:00Z by `run-20261103T0146-41561898803` (last 7 days). Read-only scanner of every sports market on Polymarket US and Kalshi — it never places orders.
Kit: `mrp/mrp_sports_radar.py` on the `mrp` branch. Raw tape: `mrp/radar/<run>/`.

# Sports radar report

records 4,040,762 | 2026-10-31 02:45Z → 02:45Z | runs 25 | pairs matched 1577 | errors {'radar': 17, 'sp.k.series_poll:KXATPEXACTMATCH': 10, 'sp.k.series_poll:KXATPMATCH': 10, 'sp.k.series_poll:KXATPSETWINNER': 10, 'sp.k.series_poll:KXAUTBUNDESTOTAL': 4, 'sp.k.series_poll:KXEFLL11H': 6, 'sp.k.series_poll:KXEFLL11HSPREAD': 10, 'sp.k.series_poll:KXHNLTOTAL': 6, 'sp.k.series_poll:KXLALIGABTTS': 9, 'sp.k.series_poll:KXLALIGASCORE': 6, 'sp.k.series_poll:KXLALIGASPREAD': 8, 'sp.k.always:KXNFLGAME': 7, 'sp.k.series_poll:KXATPCHALLENGERMATCH': 7, 'sp.k.series_poll:KXEFLL11HBTTS': 10, 'sp.k.series_poll:KXLALIGA2H': 6, 'sp.k.series_poll:KXCS2MAP': 6, 'sp.k.series_poll:KXEFLL11HTOTAL': 8, 'sp.k.series_poll:KXLALIGA2HBTTS': 8, 'sp.k.series_poll:KXLALIGA2HSPREAD': 6, 'sp.k.series_poll:KXLALIGA2HTOTAL': 4, 'sp.k.series_poll:KXLALIGACORNERS': 8, 'sp.k.series_poll:KXLALIGAGAME': 6, 'sp.k.series_poll:KXLALIGAGOAL': 6, 'sp.k.series_poll:KXAUTBUNDESGAME': 2, 'sp.k.series_poll:KXCZEFLTOTAL': 7, 'sp.k.series_poll:KXELITESERIENTOTAL': 2, 'sp.k.series_poll:KXEREDIVISIETOTAL': 2, 'sp.k.always:KXNCAAFGAME': 7, 'sp.k.series_poll:KXLIGUE11HBTTS': 3, 'sp.k.series_poll:KXLIGUE11HSCORE': 4, 'sp.k.series_poll:KXLIGUE11H': 4, 'sp.k.series_poll:KXLIGUE11HSPREAD': 1, 'sp.stream': 41}

## Catalogue (latest inventory, 01:52Z)

Polymarket US sports events 4601 of 6114 active events; Kalshi near-term sports markets 2655 in 583 events; calls so far {'pm': 51, 'k': 755}; MB {'pm': 176070320, 'k': 92699402}

| venue | sport / league / type | markets | two-sided | med spread | vol 24h |
|---|---|---|---|---|---|
| pm | football / nfl / futures | 3781 | 66% | 0.010 | 0 |
| pm | football / cfb / futures | 1597 | 78% | 0.010 | 0 |
| pm | basketball / nba / futures | 1452 | 55% | 0.020 | 0 |
| pm | ice-hockey / nhl / futures | 779 | 96% | 0.010 | 0 |
| pm | basketball / cbb / basketball_team_full_game_winner | 644 | 26% | 0.040 | 0 |
| pm | basketball / wcbb / basketball_team_full_game_winner | 627 | 30% | 0.410 | 0 |
| k | KXNCAAFGAME / College Football Game | 506 | 100% | 0.090 | 1131936 |
| pm | golf / worlwide / futures | 485 | 17% | 0.006 | 0 |
| pm | golf / lpga / futures | 440 | 0% | - | 0 |
| pm | soccer / epl / futures | 435 | 86% | 0.010 | 0 |
| pm | golf / abudhabc / futures | 352 | 0% | - | 0 |
| pm | basketball / cbb / futures | 317 | 85% | 0.010 | 0 |
| pm | table-tennis / setkameua / table_tennis_match_winner | 277 | 94% | 0.170 | 0 |
| pm | soccer / ucl / futures | 276 | 77% | 0.010 | 0 |
| pm | baseball / mlb / futures | 264 | 24% | 0.001 | 0 |
| pm | tennis / utr / tennis_match_winner | 232 | 24% | 0.410 | 0 |
| pm | football / cfb / football_team_full_game_winner | 230 | 87% | 0.075 | 0 |
| k | KXNFLFFWEEKLEAD / Weekly Fantasy Football Leader | 230 | 100% | 0.140 | 999 |
| pm | tennis / itfme / tennis_match_winner | 216 | 55% | 0.060 | 0 |
| pm | tennis / itfwo / tennis_match_winner | 192 | 66% | 0.020 | 0 |
| pm | macro /  / futures | 150 | 75% | 0.010 | 0 |
| k | KXNFLFFWEEKTOP / Weekly Fantasy Football Top Players | 148 | 100% | 0.150 | 337 |
| pm | soccer / lal / futures | 146 | 66% | 0.010 | 0 |
| pm | mma / ufc / futures | 145 | 82% | 0.010 | 0 |
| pm | boxing / boxing / futures | 145 | 0% | - | 0 |
| pm | motorsports / f1 / futures | 123 | 15% | 0.055 | 0 |
| pm | basketball / nba / basketball_team_full_game_winner | 113 | 75% | 0.200 | 0 |
| pm | tennis / atp / futures | 103 | 41% | 0.010 | 0 |
| pm | tennis / atp / tennis_match_winner | 99 | 90% | 0.010 | 0 |
| pm | macro / usgas / futures | 89 | 8% | 0.060 | 0 |
| pm | soccer / sea / futures | 86 | 80% | 0.010 | 0 |
| pm | esports / cs2 / esports_match_winner | 81 | 58% | 0.190 | 0 |
| pm | soccer / bun / futures | 80 | 82% | 0.010 | 0 |
| pm | soccer / lg1 / futures | 77 | 84% | 0.010 | 0 |
| pm | tennis / wta / futures | 75 | 44% | 0.010 | 0 |
| pm | macro / usdsl / futures | 63 | 0% | - | 0 |
| pm | table-tennis / czechligapro / table_tennis_match_winner | 62 | 16% | 0.450 | 0 |
| pm | soccer / j2 / soccer_team_full_time_winner | 60 | 67% | 0.020 | 0 |
| pm | motorsports / nascar / futures | 57 | 14% | 0.090 | 0 |
| pm | soccer / uecl / soccer_team_full_time_winner | 55 | 98% | 0.020 | 0 |
| pm | soccer / ucl / soccer_team_full_time_winner | 54 | 100% | 0.010 | 0 |
| pm | soccer / uel / soccer_team_full_time_winner | 54 | 100% | 0.020 | 0 |
| pm | tennis / atpdb / tennis_match_winner | 54 | 50% | 0.300 | 0 |
| pm | golf / masttour / futures | 52 | 100% | 0.499 | 0 |
| pm | tennis / wta / tennis_match_winner | 52 | 98% | 0.010 | 0 |
| pm | soccer / mls / futures | 51 | 92% | 0.010 | 0 |
| pm | table-tennis / setkamecz / table_tennis_match_winner | 48 | 92% | 0.170 | 0 |
| pm | technology /  / futures | 42 | 74% | 0.010 | 0 |
| pm | soccer / eflch / soccer_team_full_time_winner | 39 | 100% | 0.010 | 0 |
| pm | soccer / lmx / futures | 36 | 28% | 0.035 | 0 |
| pm | soccer / uel / futures | 36 | 3% | 0.160 | 0 |
| pm | soccer / uecl / futures | 36 | 0% | - | 0 |
| pm | table-tennis / setkamemd / table_tennis_match_winner | 36 | 3% | 0.380 | 0 |
| pm | ice-hockey / nhl / hockey_team_full_game_winner | 33 | 100% | 0.010 | 0 |
| pm | soccer / par1 / soccer_team_full_time_winner | 33 | 70% | 0.040 | 0 |
| k | KXNFLGAME / NFL Game | 32 | 100% | 0.010 | 17522213 |
| pm | football / nfl / football_team_full_game_winner | 30 | 67% | 0.005 | 0 |
| pm | soccer / acle / soccer_team_full_time_winner | 30 | 90% | 0.020 | 0 |
| pm | soccer / bel1 / soccer_team_full_time_winner | 30 | 93% | 0.040 | 0 |
| pm | soccer / lal / soccer_team_full_time_winner | 30 | 100% | 0.010 | 0 |

## Opportunities

| kind | distinct | hits | max margin $/contract | max persistence | fresh-BBO still open |
|---|---|---|---|---|---|
| decided_k | 328 | 16054 | 0.9893 | 169 min | 0/0 |
| decided_pm | 23 | 339 | 0.9947 | 21 min | 180/339 |
| decided_pm_closed | 12 | 147 | 0.9893 | 22 min | 0/147 |
| dutch_k | 15 | 69 | 0.0817 | 4 min | 0/0 |
| dutch_k_sell | 2 | 4 | 0.0066 | 0 min | 0/0 |
| dutch_pm | 54 | 2613 | 0.5316 | 50 min | 0/0 |
| implication_k | 2741 | 135765 | 0.9786 | 110 min | 0/0 |
| lag_k_settled | 200 | 33027 | 0.9973 | 294 min | 26826/31986 |
| lag_k_settled_closed | 175 | 2412 | 0.9973 | 272 min | 0/2412 |

Top by persistence × hits:

- **lag_k_settled** esports — BILIBILI GAMING vs. Hanwha Life Esports — bid 0.42 ask 0.43 buy_yes @ 0.43 | margin 0.5732 | 117 min, 1186 hits | fresh bbo 0.42/0.43 depth 12/14 | score - NS
- **lag_k_settled** basketball — Ulm Basketball vs. Baskets Oldenburg — bid 0.99 ask - sell_yes @ 0.99 | margin 0.9893 | 273 min, 941 hits | score 81-65 FT
- **lag_k_settled** basketball — Basketball Lowen Braunschweig vs. Wurzburg Baskets — bid 0.01 ask 0.02 sell_yes @ 0.01 | margin 0.4130 | 227 min, 817 hits | fresh bbo 0.01/0.02 depth 1/18 | score 60-88 Q4
- **lag_k_settled** football — North Alabama vs. Central Arkansas — bid 0.99 ask - sell_yes @ 0.995 | margin 0.9947 | 212 min, 757 hits | fresh bbo 0.99/- depth 13/0 | score 14-9 FT
- **lag_k_settled** basketball — Charleston Southern vs. South Florida — bid 0.01 ask 0.02 sell_yes @ 0.01 | margin 0.0373 | 294 min, 593 hits | fresh bbo 0.01/0.02 depth 1/37 | score 52-68 H2
- **lag_k_settled** basketball — Grambling State vs. Northern Illinois — bid 0.25 ask 0.28 sell_yes @ 0.25 | margin 0.2466 | 223 min, 521 hits | fresh bbo 0.24/0.25 depth 7/15 | score - NS
- **lag_k_settled** esports — SEIJI ESPORTS vs. ZANSIDE GAMING — bid 0.20 ask 0.30 sell_yes @ 0.2 | margin 0.1985 | 120 min, 485 hits | fresh bbo 0.20/0.30 depth 7/8 | score - NS
- **decided_k** 🔒 football — NE Patriots vs. MIA Dolphins — buy_yes @ 0.77 | margin 0.2756 | 169 min, 418 hits | score 24-19 Q4
- **decided_k** 🔒 football — NE Patriots vs. MIA Dolphins — buy_yes @ 0.92 | margin 0.1031 | 169 min, 418 hits | score 24-19 Q4
- **decided_k** 🔒 football — NE Patriots vs. MIA Dolphins — buy_yes @ 0.99 | margin 0.0280 | 169 min, 418 hits | score 24-19 Q4
- **decided_k** 🔒 football — NE Patriots vs. MIA Dolphins — buy_yes @ 0.77 | margin 0.2659 | 111 min, 441 hits | score 24-13 Q4
- **lag_k_settled** basketball — Western Michigan vs. Old Dominion — bid 0.51 ask 0.53 sell_yes @ 0.51 | margin 0.5027 | 111 min, 423 hits | fresh bbo 0.51/0.53 depth 46/44 | score - NS
- **implication_k** 🔒  — 26NOV01NEMIA — | margin 0.6541 | 101 min, 424 hits | score - 
- **decided_k** soccer — New England Revolution vs. Inter Miami CF — buy_yes @ 0.23 | margin 0.7576 | 126 min, 397 hits | score 2-2 90'
- **lag_k_settled** esports — Nova Esports vs. Any Questions Gaming — bid 0.96 ask - sell_yes @ 0.96 | margin 0.9573 | 61 min, 460 hits | fresh bbo 0.96/- depth 19/0 | score 1-0 Map 2
- **decided_k** football — NE Patriots vs. MIA Dolphins — buy_yes @ 0.2 | margin 0.8201 | 126 min, 390 hits | score 24-19 Q4
- **decided_k** football — NE Patriots vs. MIA Dolphins — buy_yes @ 0.36 | margin 0.6750 | 126 min, 390 hits | score 24-19 Q4
- **lag_k_settled** esports — World Squad vs. CIS Squad — bid - ask 0.01 buy_yes @ 0.01 | margin 0.9893 | 77 min, 390 hits | fresh bbo -/0.01 depth 0/13 | score 0-0 Game 1
- **lag_k_settled** soccer — AC Milan vs. FC Internazionale Milano — bid 0.44 ask 0.45 sell_yes @ 0.44 | margin 0.7163 | 108 min, 353 hits | fresh bbo 0.44/0.45 depth 25/33 | score 2-1 1H
- **lag_k_settled** soccer — AC Milan vs. FC Internazionale Milano — bid 0.26 ask 0.27 sell_yes @ 0.26 | margin 0.2563 | 108 min, 353 hits | fresh bbo 0.26/0.27 depth 23/55 | score 2-1 1H
- **lag_k_settled** soccer — AC Milan vs. FC Internazionale Milano — bid 0.29 ask 0.31 buy_yes @ 0.31 | margin 0.8832 | 108 min, 353 hits | fresh bbo 0.29/0.31 depth 19/37 | score 2-1 1H
- **lag_k_settled** basketball — Villanova (W) vs. Notre Dame (W) — bid 0.01 ask 0.02 sell_yes @ 0.01 | margin 0.2563 | 92 min, 364 hits | fresh bbo -/0.02 depth 0/36 | score 45-65 H2
- **lag_k_settled** football — Delaware State vs. Norfolk State — bid 0.99 ask - sell_yes @ 0.995 | margin 0.9947 | 88 min, 346 hits | fresh bbo 0.99/- depth 13/0 | score 36-33 FT
- **lag_k_settled** football — Montana vs. Eastern Washington — bid 0.99 ask - sell_yes @ 0.995 | margin 0.9947 | 85 min, 335 hits | fresh bbo 0.99/- depth 14/0 | score 42-33 FT
- **lag_k_settled** soccer — New England Revolution vs. Inter Miami CF — bid 0.17 ask 0.18 buy_yes @ 0.18 | margin 0.8097 | 70 min, 310 hits | fresh bbo 0.17/0.18 depth 12/37 | score 1-1 2H

## Live paper trades (no orders; Kalshi prices, taker fees)

Ledger L2-2026-11-01 (earlier ledgers excluded: L1)

**Total closed P&L: $-431.15 on $1444.15 staked (-29.9%)**

| rule | entries | closed | winners | staked | P&L | ROI |
|---|---|---|---|---|---|---|
| R1 anchor [ncaaf] | 26 | 26 | 11 | $262.99 | $-34.99 | -13% |
| R1 anchor [nfl] | 6 | 5 | 1 | $50.90 | $-31.90 | -63% |
| R2 q1cheap [ncaaf] | 37 | 37 | 2 | $194.50 | $-142.50 | -73% |
| R2 q1cheap [nfl] | 6 | 6 | 1 | $31.46 | $-2.46 | -8% |
| R3 blowout [ncaaf] | 16 | 16 | 1 | $339.32 | $-197.32 | -58% |
| R4 halftime [ncaaf] | 19 | 19 | 6 | $95.24 | $+9.76 | +10% |
| R6 decided [other] | 34 | 28 | 22 | $469.73 | $-31.73 | -7% |

| time (UTC) | rule | game | team | entry | contracts | why | result |
|---|---|---|---|---|---|---|---|
| 01:54 | R1 anchor | CHI Bears vs. SEA Seahawks | Chicago | 0.50 | 20 | pregame dog (mid 0.49) leads 7-0 in Q2, ask 0.50 | open |
| 00:02 | R6 decided | Texas Southern (W) vs. Tulan | Over 154.5 points | 0.99 | 20 | score 57-137 total 194 > 154.5 | kalshi settled: 0.00, $-19.81 |
| 00:02 | R6 decided | Texas Southern (W) vs. Tulan | Over 149.5 points | 0.99 | 20 | score 57-137 total 194 > 149.5 | kalshi settled: 0.00, $-19.81 |
| 00:02 | R6 decided | Texas Southern (W) vs. Tulan | Over 144.5 points | 0.99 | 20 | score 57-137 total 194 > 144.5 | kalshi settled: 0.00, $-19.81 |
| 23:55 | R6 decided | Texas Southern (W) vs. Tulan | Over 139.5 points | 0.90 | 22 | score 57-137 total 194 > 139.5 | kalshi settled: 0.00, $-19.94 |
| 23:55 | R6 decided | Texas Southern (W) vs. Tulan | Over 135.5 points | 0.90 | 11 | score 57-137 total 194 > 135.5 | kalshi settled: 0.00, $-9.97 |
| 23:55 | R6 decided | Texas Southern (W) vs. Tulan | Over 132.5 points | 0.82 | 11 | score 57-137 total 194 > 132.5 | kalshi settled: 0.00, $-9.13 |
| 23:55 | R6 decided | Texas Southern (W) vs. Tulan | Over 129.5 points | 0.85 | 13 | score 57-137 total 194 > 129.5 | kalshi settled: 1.00, $+1.83 |
| 23:55 | R6 decided | Texas Southern (W) vs. Tulan | Over 125.5 points | 0.98 | 1 | score 57-137 total 194 > 125.5 | kalshi settled: 1.00, $+0.02 |
| 23:55 | R6 decided | Texas Southern (W) vs. Tulan | Over 120.5 points | 0.93 | 1 | score 57-137 total 194 > 120.5 | kalshi settled: 1.00, $+0.07 |
| 23:55 | R6 decided | Texas Southern (W) vs. Tulan | Over 115.5 points | 0.99 | 20 | score 57-137 total 194 > 115.5 | kalshi settled: 1.00, $+0.19 |
| 23:55 | R6 decided | Texas Southern (W) vs. Tulan | Over 110.5 points | 0.99 | 20 | score 57-137 total 194 > 110.5 | kalshi settled: 1.00, $+0.19 |
| 19:09 | R6 decided | Alcorn State (W) vs. Ole Mis | Ole Miss wins by over 7.5 points | 0.99 | 20 | ended 38-80 margin 42 vs 7.5 | open |
| 19:09 | R6 decided | Alcorn State (W) vs. Ole Mis | Ole Miss wins by over 29.5 points | 0.63 | 31 | ended 38-80 margin 42 vs 29.5 | open |
| 19:09 | R6 decided | Alcorn State (W) vs. Ole Mis | Ole Miss wins by over 26.5 points | 0.69 | 28 | ended 38-80 margin 42 vs 26.5 | open |
| 19:09 | R6 decided | Alcorn State (W) vs. Ole Mis | Ole Miss wins by over 22.5 points | 0.82 | 24 | ended 38-80 margin 42 vs 22.5 | open |
| 19:09 | R6 decided | Alcorn State (W) vs. Ole Mis | Ole Miss wins by over 17.5 points | 0.93 | 21 | ended 38-80 margin 42 vs 17.5 | open |
| 19:09 | R6 decided | Alcorn State (W) vs. Ole Mis | Ole Miss wins by over 12.5 points | 0.97 | 20 | ended 38-80 margin 42 vs 12.5 | open |
| 11:57 | R6 decided | Lorenzo Musetti vs. Hubert H | Lorenzo Musetti | 0.83 | 5 | set 2 final 7-6 | kalshi settled: 1.00, $+0.80 |
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

### Score reaction speed (live, 15 s): share of the 3-minute move done by +15 s / +30 s / +60 s

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
- 26NOV02CHISEA 13-9: 0% / 67% / 67%

## Bot latency map: how long a decided Kalshi market stays mispriced

| sport | series | markets | already priced | mispriced then fixed | median s mispriced | closed/timeout | contradictions | cheapest ask (size) | resting @0.97 contracts / $ | settled right / wrong |
|---|---|---|---|---|---|---|---|---|---|---|
| basketball | KXNCAAWBTOTAL | 125 | 119 | 6 | 370 | 0 | 0 | 0.01 (1600) | 298 / $8.94 | 116 / 6 |
| basketball | KXNCAAWBSPREAD | 68 | 68 | 0 | - | 0 | 0 | - | 0 / $0.00 | 68 / 0 |
| tennis | KXATPCHALLENGERMATCH | 46 | 7 | 39 | 0 | 0 | 0 | 0.97 (53) | 0 / $0.00 | 40 / 0 |
| tennis | KXATPSETWINNER | 40 | 2 | 38 | 0 | 0 | 0 | - | 0 / $0.00 | 36 / 0 |
| soccer | KXMLSTOTAL | 38 | 0 | 36 | 0 | 2 | 0 | 0.82 (29) | 188 / $5.63 | 36 / 0 |
| soccer | KXALLSVENSKANTOTAL | 37 | 11 | 26 | 1 | 0 | 0 | - | 0 / $0.00 | 37 / 0 |
| soccer | KXEREDIVISIETOTAL | 30 | 0 | 30 | 0 | 0 | 0 | - | 0 / $0.00 | 26 / 0 |
| tennis | KXWTASETWINNER | 28 | 0 | 28 | 1 | 0 | 0 | - | 0 / $0.00 | 28 / 0 |
| soccer | KXELITESERIENTOTAL | 26 | 0 | 26 | 0 | 0 | 0 | - | 0 / $0.00 | 22 / 0 |
| soccer | KXLIGAFTOTAL | 25 | 5 | 20 | 1 | 0 | 0 | 0.98 (87) | 0 / $0.00 | 25 / 0 |
| soccer | KXSERIECTOTAL | 24 | 4 | 20 | 1 | 0 | 0 | 0.97 (3) | 0 / $0.00 | 24 / 0 |
| soccer | KXDENSUPERLIGATOTAL | 22 | 0 | 22 | 0 | 0 | 0 | - | 0 / $0.00 | 22 / 0 |
| soccer | KXBELGIANPLTOTAL | 22 | 0 | 22 | 1 | 0 | 0 | 0.89 (454) | 763 / $22.89 | 22 / 0 |
| football | KXNFLGAME | 22 | 0 | 22 | 1 | 0 | 0 | 0.02 (0) | 0 / $0.00 | 19 / 0 |
| soccer | KXIDNSLTOTAL | 21 | 0 | 21 | 1 | 0 | 0 | 0.96 (62) | 0 / $0.00 | 21 / 0 |
| soccer | KXBUNDESLIGA2TOTAL | 19 | 0 | 19 | 2 | 0 | 0 | - | 0 / $0.00 | 19 / 0 |
| soccer | KXAUTBUNDESTOTAL | 19 | 0 | 19 | 1 | 0 | 0 | - | 0 / $0.00 | 13 / 1 |
| soccer | KXEKSTRAKLASATOTAL | 18 | 18 | 0 | - | 0 | 0 | - | 0 / $0.00 | 18 / 0 |
| soccer | KXECULPTOTAL | 17 | 6 | 11 | 0 | 0 | 0 | 0.93 (23) | 0 / $0.00 | 17 / 0 |
| soccer | KXAFCCLTOTAL | 16 | 14 | 2 | 2 | 0 | 0 | 0.98 (22) | 0 / $0.00 | 16 / 0 |
| soccer | KXBRASILEIROBTOTAL | 15 | 6 | 9 | 0 | 0 | 0 | - | 0 / $0.00 | 14 / 0 |
| soccer | KXLIGUE2TOTAL | 15 | 15 | 0 | - | 0 | 0 | - | 0 / $0.00 | 15 / 0 |
| football | KXNFLTOTALPRECISE | 14 | 0 | 14 | 1 | 0 | 0 | - | 0 / $0.00 | 0 / 0 |
| basketball | KXNCAAWBGAME | 14 | 14 | 0 | - | 0 | 0 | - | 0 / $0.00 | 14 / 0 |
| soccer | KXHUNNB1TOTAL | 12 | 0 | 12 | 1 | 0 | 0 | - | 0 / $0.00 | 12 / 0 |
| soccer | KXMLS1HTOTAL | 12 | 0 | 9 | 0 | 3 | 0 | 0.61 (1157) | 0 / $0.00 | 12 / 0 |
| soccer | KXARGPREMDIVTOTAL | 12 | 10 | 2 | 1 | 0 | 0 | - | 0 / $0.00 | 12 / 0 |
| soccer | KXARGNACBTOTAL | 12 | 11 | 1 | 1 | 0 | 0 | - | 0 / $0.00 | 12 / 0 |
| soccer | KXALLSVENSKANSPREAD | 10 | 5 | 5 | 0 | 0 | 0 | - | 0 / $0.00 | 10 / 0 |
| tennis | KXATPEXACTMATCH | 9 | 0 | 9 | 1 | 0 | 0 | - | 0 / $0.00 | 9 / 0 |
| basketball | KXNCAAMBSPREAD | 9 | 2 | 0 | - | 7 | 0 | 0.62 (20) | 0 / $0.00 | 0 / 0 |
| soccer | KXTHAIL1TOTAL | 8 | 0 | 8 | 1 | 0 | 0 | 0.96 (13) | 0 / $0.00 | 8 / 0 |
| soccer | KXBUNDESLIGA2SPREAD | 8 | 0 | 8 | 2 | 0 | 0 | - | 0 / $0.00 | 8 / 0 |
| soccer | KXMLS1H | 8 | 0 | 6 | 0 | 2 | 0 | 0.63 (492) | 0 / $0.00 | 8 / 0 |
| soccer | KXPERLIGA1TOTAL | 8 | 8 | 0 | - | 0 | 0 | - | 0 / $0.00 | 8 / 0 |
| soccer | KXKLEAGUETOTAL | 7 | 0 | 7 | 1 | 0 | 0 | - | 0 / $0.00 | 7 / 0 |
| soccer | KXHNLTOTAL | 7 | 0 | 7 | 0 | 0 | 0 | - | 0 / $0.00 | 7 / 0 |
| soccer | KXDIMAYORTOTAL | 7 | 0 | 7 | 0 | 0 | 0 | - | 0 / $0.00 | 7 / 0 |
| basketball | KXNCAAMBTOTAL | 7 | 2 | 0 | - | 5 | 0 | 0.75 (120) | 0 / $0.00 | 0 / 0 |
| tennis | KXATPMATCH | 6 | 0 | 6 | 1 | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| soccer | KXCZEFNLTOTAL | 6 | 0 | 6 | 0 | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| soccer | KXSLGREECETOTAL | 6 | 5 | 1 | 0 | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| soccer | KXMYSLTOTAL | 5 | 0 | 5 | 0 | 0 | 0 | - | 0 / $0.00 | 5 / 0 |
| soccer | KXLALIGA2TOTAL | 5 | 3 | 2 | 0 | 0 | 0 | - | 0 / $0.00 | 5 / 0 |
| soccer | KXAPFDDHTOTAL | 5 | 0 | 5 | 0 | 0 | 0 | - | 0 / $0.00 | 5 / 0 |
| soccer | KXLIGAPORTUGALTOTAL | 5 | 0 | 5 | 0 | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXMLSSPREAD | 5 | 0 | 5 | 1 | 0 | 0 | - | 0 / $0.00 | 5 / 0 |
| soccer | KXEKSTRAKLASASPREAD | 5 | 5 | 0 | - | 0 | 0 | - | 0 / $0.00 | 5 / 0 |
| soccer | KXARGNACBSPREAD | 5 | 5 | 0 | - | 0 | 0 | - | 0 / $0.00 | 5 / 0 |
| soccer | KXSERIECSPREAD | 4 | 0 | 4 | 0 | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
| soccer | KXCZEFLTOTAL | 4 | 0 | 4 | 1 | 0 | 0 | 0.47 (1945) | 76 / $2.29 | 2 / 0 |
| soccer | KXMLS1HBTTS | 4 | 0 | 3 | 0 | 1 | 0 | 0.78 (68) | 0 / $0.00 | 4 / 0 |
| soccer | KXLIGUE1SPREAD | 4 | 4 | 0 | - | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
| soccer | KXECULPSPREAD | 4 | 4 | 0 | - | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
| soccer | KXTFF1LIGTOTAL | 3 | 0 | 3 | 1 | 0 | 0 | 0.97 (5) | 0 / $0.00 | 2 / 1 |
| football | KXMLSTOTAL | 3 | 0 | 0 | - | 3 | 0 | 0.71 (2845) | 0 / $0.00 | 3 / 0 |
| soccer | KXMLSGAME | 3 | 0 | 3 | 1 | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXEKSTRAKLASAGAME | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXAFCCLGAME | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXARGNACBGAME | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXALLSVENSKANBTTS | 2 | 0 | 2 | 0 | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXEREDIVISIEBTTS | 2 | 0 | 2 | 0 | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXEREDIVISIESPREAD | 2 | 0 | 2 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / 0 |
| soccer | KXDENSUPERLIGASPREAD | 2 | 0 | 2 | 0 | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXLIGAEXPTOTAL | 2 | 0 | 2 | 1 | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXCHLLDPTOTAL | 2 | 0 | 2 | 1 | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXMLSBTTS | 2 | 0 | 2 | 1 | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXARGNACBBTTS | 2 | 1 | 1 | 1 | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| tennis | KXATPDOUBLES | 2 | 0 | 2 | 0 | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| basketball | KXNCAAMBGAME | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 0 / 0 |
| soccer | KXLIGUE1TOTAL | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXBRASILEIROTOTAL | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXIDNSLBTTS | 1 | 0 | 1 | 0 | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXBUNDESLIGA2BTTS | 1 | 0 | 1 | 0 | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXDENSUPERLIGABTTS | 1 | 0 | 1 | 0 | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXSCOCUPTOTAL | 1 | 0 | 1 | 0 | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXSUPERLIGTOTAL | 1 | 0 | 1 | 0 | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXELITESERIENBTTS | 1 | 0 | 1 | 0 | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| football | KXNFLEQBTTS | 1 | 0 | 0 | - | 1 | 0 | 0.54 (28) | 10 / $0.30 | 1 / 0 |
| football | KXMLSBTTS | 1 | 0 | 0 | - | 1 | 0 | 0.72 (25231) | 0 / $0.00 | 1 / 0 |
| soccer | KXBRASILEIROBBTTS | 1 | 0 | 1 | 1 | 0 | 0 | - | 0 / $0.00 | 0 / 0 |
| soccer | KXAFCCLBTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXSERIECBTTS | 1 | 0 | 1 | 17 | 0 | 0 | 0.97 (11) | 0 / $0.00 | 1 / 0 |
| soccer | KXLIGUE1BTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXARGPREMDIVBTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |

'Already priced' = the book was at 99c+ when we first looked (bots were faster than our score feed). 'Median s mispriced' runs from our decision to the fix. 'Settled right / wrong' checks our certainty against Kalshi's result — any 'wrong' means the score feed or the model failed.

## Decided-state engine (contracts the live score already settled, still trading)

2275 contracts decided while active; 328 had a price leaving > 0.4c after fees; 185 of those were mispriced AFTER the score was stable (lock tier)

| sport | game | contract | decided | reason | max margin | mispriced for | lock margin | lock depth |
|---|---|---|---|---|---|---|---|---|
| basketball | HOU Rockets vs. DAL Mavericks | KXNBA2HSPREAD-26OCT30HOUDAL-DAL8 | NO | ended 111-116 margin 5 vs 7.5 | 0.989 | 270s | 0.989 | 1882 |
| basketball | HOU Rockets vs. DAL Mavericks | KXNBA2HSPREAD-26OCT30HOUDAL-DAL6 | NO | ended 111-116 margin 5 vs 5.5 | 0.989 | 270s | 0.989 | 1684 |
| basketball | HOU Rockets vs. DAL Mavericks | KXNBA2HSPREAD-26OCT30HOUDAL-DAL12 | NO | ended 111-116 margin 5 vs 11.5 | 0.989 | 270s | 0.989 | 11904 |
| basketball | HOU Rockets vs. DAL Mavericks | KXNBA2HSPREAD-26OCT30HOUDAL-DAL10 | NO | ended 111-116 margin 5 vs 9.5 | 0.989 | 270s | 0.989 | 1450 |
| basketball | HOU Rockets vs. DAL Mavericks | KXNBA2HTOTAL-26OCT30HOUDAL-134 | YES | score 111-116 total 227 > 133.5 | 0.989 | 270s | 0.989 | 10371 |
| basketball | LA Lakers vs. GS Warriors | KXNBA1QTOTAL-26OCT30LALGSW-55 | YES | score 44-33 total 77 > 54.5 | 0.989 | 982s | 0.989 | 16849 |
| basketball | LA Lakers vs. GS Warriors | KXNBA2QTOTAL-26OCT30LALGSW-54 | YES | score 69-60 total 129 > 53.5 | 0.989 | 3885s | 0.989 | 27914 |
| basketball | LA Lakers vs. GS Warriors | KXNBA1QTOTAL-26OCT30LALGSW-59 | YES | score 44-33 total 77 > 58.5 | 0.989 | 953s | 0.989 | 5448 |
| basketball | LA Lakers vs. GS Warriors | KXNBA1QTOTAL-26OCT30LALGSW-57 | YES | score 44-33 total 77 > 56.5 | 0.989 | 953s | 0.989 | 5485 |
| basketball | LA Lakers vs. GS Warriors | KXNBA2QTOTAL-26OCT30LALGSW-60 | YES | score 69-60 total 129 > 59.5 | 0.989 | 3856s | 0.989 | 25211 |
| basketball | LA Lakers vs. GS Warriors | KXNBA2QTOTAL-26OCT30LALGSW-58 | YES | score 69-60 total 129 > 57.5 | 0.989 | 3856s | 0.989 | 30956 |
| basketball | LA Lakers vs. GS Warriors | KXNBA2QTOTAL-26OCT30LALGSW-56 | YES | score 69-60 total 129 > 55.5 | 0.989 | 3856s | 0.989 | 28883 |
| basketball | LA Lakers vs. GS Warriors | KXNBA1QTOTAL-26OCT30LALGSW-61 | YES | score 44-33 total 77 > 60.5 | 0.989 | 877s | 0.989 | 18192 |
| basketball | LA Lakers vs. GS Warriors | KXNBA4QTOTAL-26OCT30LALGSW-62 | YES | score 95-112 total 207 > 61.5 | 0.989 | 7406s | 0.989 | 9352 |
| basketball | LA Lakers vs. GS Warriors | KXNBA4QTOTAL-26OCT30LALGSW-60 | YES | score 95-112 total 207 > 59.5 | 0.989 | 7406s | 0.989 | 9022 |
| basketball | LA Lakers vs. GS Warriors | KXNBA4QTOTAL-26OCT30LALGSW-58 | YES | score 95-112 total 207 > 57.5 | 0.989 | 7406s | 0.989 | 9045 |
| basketball | LA Lakers vs. GS Warriors | KXNBA4QTOTAL-26OCT30LALGSW-56 | YES | score 95-112 total 207 > 55.5 | 0.989 | 7406s | 0.989 | 8474 |
| basketball | LA Lakers vs. GS Warriors | KXNBA4QTOTAL-26OCT30LALGSW-54 | YES | score 95-112 total 207 > 53.5 | 0.989 | 7406s | 0.989 | 9336 |
| basketball | LA Lakers vs. GS Warriors | KXNBA4QTOTAL-26OCT30LALGSW-52 | YES | score 95-112 total 207 > 51.5 | 0.989 | 7406s | 0.989 | 9174 |
| basketball | LA Lakers vs. GS Warriors | KXNBA4QTOTAL-26OCT30LALGSW-50 | YES | score 95-112 total 207 > 49.5 | 0.989 | 7406s | 0.989 | 8281 |
| basketball | LA Lakers vs. GS Warriors | KXNBA4QTOTAL-26OCT30LALGSW-48 | YES | score 95-112 total 207 > 47.5 | 0.989 | 7406s | 0.989 | 10336 |
| basketball | LA Lakers vs. GS Warriors | KXNBA4QTOTAL-26OCT30LALGSW-46 | YES | score 95-112 total 207 > 45.5 | 0.989 | 7406s | 0.989 | 8201 |
| basketball | LA Lakers vs. GS Warriors | KXNBA4QTOTAL-26OCT30LALGSW-44 | YES | score 95-112 total 207 > 43.5 | 0.989 | 7406s | 0.989 | 7191 |
| basketball | LA Lakers vs. GS Warriors | KXNBA1QTOTAL-26OCT30LALGSW-65 | YES | score 44-33 total 77 > 64.5 | 0.989 | 800s | 0.989 | 12096 |
| basketball | LA Lakers vs. GS Warriors | KXNBA1QTOTAL-26OCT30LALGSW-63 | YES | score 44-33 total 77 > 62.5 | 0.989 | 800s | 0.989 | 19594 |

## Close / settlement latency (how clunky each venue is after the final whistle)

Kalshi: settlement_ts − close_time per series (negative = settled before the scheduled close)

| series | n | median | p90 |
|---|---|---|---|
| KXNFLPASSYDSPRECISE Pass Yards Precise | 12485 | 4.0 min | 4.1 min |
| KXESOCCERGAME eSoccer Game | 3655 | 4.0 min | 4.1 min |
| KXNCAAFSPREAD College Football Spread | 2296 | 4.0 min | 4.1 min |
| KXNCAAFTOTAL College Football Total Points | 1667 | 4.0 min | 4.1 min |
| KXNFLTOTALPRECISE Total Precise | 1248 | 4.0 min | 4.1 min |
| KXNFLRECYDS Pro Football Receiving Yards | 1188 | 2.0 min | 2.1 min |
| KXNCAAFTEAMTOTAL College Football Team Total Po | 1168 | 4.0 min | 4.1 min |
| KXNFLRECYDSPROT Receiving Yards Protected | 1132 | 6.0 min | 6.1 min |
| KXNCAAMBTOTAL Men's College Basketball Total | 1094 | 4.0 min | 4.1 min |
| KXNCAAF1HSPREAD College Football 1st Half Spre | 1006 | 4.0 min | 4.1 min |
| KXNHLGOAL NHL Goalscorer | 990 | 3.0 min | 3.1 min |
| KXLIGAPROMATCH Russia Liga Pro Match | 958 | 4.0 min | 4.1 min |
| KXNCAAMBSPREAD Men's College Basketball Sprea | 928 | 1.8 min | 1.8 min |
| KXNBA3PTPROT NBA Player Threes Protected | 872 | 2.5 min | 2.6 min |
| KXNFLRECPROT Receptions Protected | 854 | 6.0 min | 6.1 min |
| KXNFLREC Pro Football Player Receptions | 794 | 2.0 min | 2.1 min |
| KXNBA3PT NBA Player Threes | 778 | 2.0 min | 2.1 min |
| KXNBAREBPROT NBA Player Rebounds Protected | 728 | 2.5 min | 2.6 min |
| KXNBAREB NBA Player Rebounds | 725 | 2.0 min | 2.1 min |
| KXNCAAF2HSPREAD College Football 2nd Half Spre | 720 | 4.0 min | 4.1 min |
| KXNCAAWBTOTAL Women's College Basketball Tot | 712 | 2.5 min | 2.6 min |
| KXNHLPTS Pro Hockey Points | 704 | 3.0 min | 3.1 min |
| KXNBAPTS NBA Player Points | 677 | 2.0 min | 2.1 min |
| KXNCAAF1HTOTAL College Football 1st Half Tota | 671 | 4.0 min | 4.1 min |
| KXNBAASTPROT NBA Player Assists Protected | 643 | 2.5 min | 2.6 min |
| KXNBAPTSPROT NBA Player Points Protected | 632 | 2.5 min | 2.6 min |
| KXNBATEAMTOTAL NBA Team Total | 629 | 2.5 min | 2.6 min |
| KXMLSGOAL Goalscorer | 597 | 6.0 min | 6.1 min |
| KXNBAAST NBA Player Assists | 567 | 2.0 min | 2.1 min |
| KXNCAAWBSPREAD Women's College Basketball Spr | 553 | 1.8 min | 1.8 min |
| KXNFLRSHYDSPROT Rushing Yards Protected | 549 | 6.0 min | 6.1 min |
| KXNHLFIRSTGOAL NHL First Goal | 522 | 6.0 min | 6.0 min |
| KXNHLAST Pro Hockey Assists | 503 | 6.0 min | 6.1 min |
| KXNFLTDPROT Pro Football Touchdowns Protec | 480 | 6.0 min | 6.1 min |
| KXNCAAF2HTOTAL College Football 2nd Half Tota | 477 | 4.0 min | 4.1 min |
| KXEBASKETBALLGAME eBasketball Game | 468 | 4.0 min | 4.1 min |
| KXNBASPREAD NBA Spread | 466 | 1.8 min | 1.8 min |
| KXNBA1HTEAMTOTAL NBA 1st Half Team Total | 462 | 2.5 min | 2.6 min |
| KXNFLRSHYDS Pro Football Rushing Yards | 458 | 2.0 min | 2.1 min |
| KXMLSSCORE Correct Score | 444 | 6.0 min | 6.1 min |

## Participant fingerprint (per sport; 60 s snapshots)

change% = share of scan cycles (60 s) where the best quote moved; react = median minutes from a score change to the next quote move (humans: slow, bursty, round sizes; bots: constant cadence, odd/constant sizes, instant reaction)

| venue | sport | markets | snapshots | two-sided | med spread | change% | react (min) | round sizes | med size |
|---|---|---|---|---|---|---|---|---|---|
| pm | soccer | 1737 | 255189 | 86% | 0.020 | 19% | 0.6 (n=3871) | - | - |
| pm | tennis | 1735 | 104281 | 92% | 0.010 | 23% | 0.5 (n=46891) | - | - |
| pm | esports | 3146 | 76636 | 76% | 0.030 | 19% | 0.5 (n=16332) | - | - |
| pm | basketball | 967 | 63722 | 81% | 0.040 | 23% | 0.5 (n=10152) | - | - |
| pm | table-tennis | 1525 | 53112 | 95% | 0.030 | 31% | 0.5 (n=25826) | - | - |
| pm | football | 121 | 21829 | 91% | 0.005 | 17% | 1.1 (n=1074) | - | - |
| pm | climate | 215 | 11069 | 77% | 0.050 | 25% | - (n=0) | - | - |
| pm | motorsports | 159 | 8546 | 40% | 0.040 | 14% | - (n=0) | - | - |
| pm | ice-hockey | 62 | 5437 | 81% | 0.050 | 13% | 0.7 (n=303) | - | - |
| pm | misc | 47 | 3778 | 93% | 0.010 | 12% | - (n=0) | - | - |
| pm | beach-volleyball | 68 | 2713 | 83% | 0.010 | 23% | 0.5 (n=1399) | - | - |
| pm | cricket | 7 | 1898 | 91% | 0.020 | 14% | 1.0 (n=318) | - | - |
| pm | mma | 14 | 713 | 94% | 0.020 | 4% | - (n=0) | - | - |
| pm | rugby | 17 | 260 | 69% | 0.450 | 18% | - (n=0) | - | - |
| pm | technology | 24 | 217 | 35% | 0.120 | 16% | - (n=0) | - | - |
| pm | macro | 40 | 200 | 0% | - | 0% | - (n=0) | - | - |
| pm | boxing | 4 | 165 | 95% | 0.030 | 56% | - (n=0) | - | - |
| pm | darts | 7 | 141 | 69% | 0.070 | 17% | 0.5 (n=18) | - | - |
| pm | baseball | 2 | 102 | 92% | 0.150 | 10% | 2.3 (n=5) | - | - |
| pm | pickleball | 7 | 61 | 74% | 0.170 | 13% | - (n=0) | - | - |
| k | KXNCAAFGAME College Football Game | 720 | 587561 | 98% | 0.060 | 2% | - | 7% | 36 |
| k | KXNFLPASSYDSPRECISE Pass Yards Precise | 15652 | 185544 | 0% | 0.390 | 0% | - | 0% | 1 |
| k | KXNFLGAME NFL Game | 56 | 119974 | 99% | 0.010 | 2% | - | 3% | 114843 |
| k | KXNBA3PT NBA Player Threes | 1907 | 99630 | 78% | 0.110 | 13% | - | 23% | 37 |
| k | KXCS2MAP Counter-Strike 2 Map Win | 480 | 85410 | 93% | 0.450 | 4% | - | 19% | 100 |
| k | KXNBAPTS NBA Player Points | 1617 | 62048 | 82% | 0.110 | 18% | - | 24% | 30 |
| k | KXESOCCERGAME eSoccer Game | 3948 | 60633 | 20% | 0.520 | 6% | - | 29% | 32 |
| k | KXNBAAST NBA Player Assists | 1396 | 58447 | 81% | 0.120 | 12% | - | 24% | 30 |
| k | KXNCAAFSPREAD College Football Spread | 2631 | 57664 | 50% | 0.090 | 4% | - | 12% | 75 |
| k | KXNBAREB NBA Player Rebounds | 1847 | 52671 | 78% | 0.140 | 21% | - | 26% | 30 |
| k | KXNCAAFTEAMTOTAL College Football Team To | 1241 | 46539 | 67% | 0.020 | 2% | - | 24% | 375 |
| k | KXNCAAMBTOTAL Men's College Basketball | 2502 | 42751 | 85% | 0.100 | 5% | - | 27% | 65 |
| k | KXNBA3PTPROT NBA Player Threes Protec | 1889 | 42509 | 28% | 0.170 | 2% | - | 24% | 162 |
| k | KXNCAAFTOTAL College Football Total P | 1889 | 39472 | 48% | 0.140 | 4% | - | 16% | 135 |
| k | KXNCAAWBTOTAL Women's College Basketba | 1290 | 35706 | 29% | 0.530 | 2% | - | 12% | 41 |
| k | KXNCAAMBSPREAD Men's College Basketball | 2029 | 33381 | 87% | 0.080 | 4% | - | 32% | 50 |
| k | KXATPSETWINNER ATP Set Winner | 224 | 32528 | 93% | 0.030 | 3% | - | 11% | 138 |
| k | KXNCAAWBSPREAD Women's College Basketba | 1026 | 31942 | 26% | 0.570 | 3% | - | 18% | 41 |
| k | KXMLSSCORE Correct Score | 450 | 31078 | 52% | 0.020 | 3% | - | 14% | 1192 |
| k | KXATPCHALLENGERMATCH Challenger ATP  | 326 | 29024 | 89% | 0.010 | 8% | - | 5% | 628 |
| k | KXNBA1HTEAMTOTAL NBA 1st Half Team Total | 638 | 28941 | 62% | 0.320 | 14% | - | 24% | 123 |
| k | KXNCAAF1H College Football 1st Hal | 1038 | 28593 | 86% | 0.840 | 1% | - | 25% | 133 |
| k | KXNBAASTPROT NBA Player Assists Prote | 1385 | 27183 | 22% | 0.140 | 2% | - | 18% | 162 |
| k | KXNBA1HTOTAL NBA 1st Half Total | 551 | 25875 | 70% | 0.050 | 13% | - | 32% | 101 |
| k | KXNBA1HSPREAD NBA 1st Half Spread | 544 | 25594 | 72% | 0.040 | 12% | - | 19% | 113 |
| k | KXLIGAMXSCORE Correct Score | 264 | 25076 | 54% | 0.020 | 3% | - | 13% | 800 |
| k | KXWTASETWINNER WTA Set Winner | 264 | 24222 | 78% | 0.050 | 4% | - | 26% | 62 |
| k | KXNBAPTSPROT NBA Player Points Protec | 1533 | 23047 | 25% | 0.280 | 3% | - | 14% | 162 |
| k | KXNCAAWBGAME Women's College Basketba | 500 | 23008 | 85% | 0.120 | 5% | - | 12% | 12 |
| k | KXNFLTOTALPRECISE Total Precise | 1976 | 22799 | 4% | 0.060 | 2% | - | 21% | 2 |
| k | KXNCAAF1HSPREAD College Football 1st Hal | 1020 | 20406 | 37% | 0.020 | 12% | - | 29% | 310 |
| k | KXNBAREBPROT NBA Player Rebounds Prot | 1779 | 20218 | 20% | 0.170 | 4% | - | 23% | 188 |
| k | KXNBAPRA NBA Player Points + Rebo | 904 | 19966 | 76% | 0.390 | 20% | - | 13% | 5 |
| k | KXNFLRECYDSPROT Receiving Yards Protecte | 1626 | 19862 | 11% | 0.740 | 5% | - | 15% | 19 |
| k | KXNEXTTEAMNHL Next Team NHL | 230 | 18860 | 0% | 0.130 | 0% | - | 23% | 341 |
| k | KXNFLRECYDS Pro Football Receiving Y | 1605 | 18316 | 0% | - | 0% | - | 0% | - |
| k | KXMLSTOTAL MLS Total | 209 | 17862 | 86% | 0.050 | 2% | - | 12% | 190 |
| k | KXNBA2HSPREAD NBA 2nd Half Spread | 665 | 15852 | 65% | 0.150 | 16% | - | 28% | 126 |
| k | KXNBA2QSPREAD NBA 2nd Quarter Spread | 377 | 15301 | 68% | 0.050 | 15% | - | 23% | 160 |
| k | KXNBA2HTOTAL NBA 2nd Half Total | 665 | 15106 | 67% | 0.200 | 18% | - | 26% | 158 |

## Schema notes (raw keys seen)

- polymarket: active, archived, category, chatChannel, closed, combos, createdAt, description, elapsed, endDate, ended, eventState, fixtureId, gameId, hidden, id, insiderTradingRules, live, marketCounts, marketGroups, markets, metadata, participants, payoutEstimateMessage, payoutEstimateTime, period, primaryTag, score, seriesSlug, slug, sortType, sportradarGameId, startDate, startTime, streamProvider, streamRequiresAuth, tags, teams, ticker, title, updatedAt
- kalshi: can_close_early, close_time, created_time, custom_strike, early_close_condition, event_ticker, exchange_index, expected_expiration_time, expiration_time, expiration_value, last_price_dollars, latest_expiration_time, market_type, no_ask_dollars, no_bid_dollars, no_sub_title, notional_value_dollars, occurrence_datetime, open_interest_fp, open_time, previous_price_dollars, previous_yes_ask_dollars, previous_yes_bid_dollars, price_level_structure, price_ranges, primary_participant_key, result, rules_primary, rules_secondary, settlement_bounds_type, settlement_timer_seconds, status, strike_type, ticker, title, updated_time, volume_24h_fp, volume_fp, yes_ask_dollars, yes_ask_size_fp, yes_bid_dollars, yes_bid_size_fp, yes_sub_title

