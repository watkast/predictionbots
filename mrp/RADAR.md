# Mr. P — sports radar

Updated 2026-11-03T05:01:47Z by `run-20261103T0146-41561898803` (last 7 days). Read-only scanner of every sports market on Polymarket US and Kalshi — it never places orders.
Kit: `mrp/mrp_sports_radar.py` on the `mrp` branch. Raw tape: `mrp/radar/<run>/`.

# Sports radar report

records 4,152,872 | 2026-10-31 05:00Z → 05:00Z | runs 24 | pairs matched 1617 | errors {'radar': 17, 'sp.k.series_poll:KXATPEXACTMATCH': 10, 'sp.k.series_poll:KXATPMATCH': 10, 'sp.k.series_poll:KXATPSETWINNER': 10, 'sp.k.series_poll:KXAUTBUNDESTOTAL': 4, 'sp.k.series_poll:KXEFLL11H': 6, 'sp.k.series_poll:KXEFLL11HSPREAD': 10, 'sp.k.series_poll:KXHNLTOTAL': 6, 'sp.k.series_poll:KXLALIGABTTS': 9, 'sp.k.series_poll:KXLALIGASCORE': 6, 'sp.k.series_poll:KXLALIGASPREAD': 8, 'sp.k.always:KXNFLGAME': 7, 'sp.k.series_poll:KXATPCHALLENGERMATCH': 7, 'sp.k.series_poll:KXEFLL11HBTTS': 10, 'sp.k.series_poll:KXLALIGA2H': 6, 'sp.k.series_poll:KXCS2MAP': 6, 'sp.k.series_poll:KXEFLL11HTOTAL': 8, 'sp.k.series_poll:KXLALIGA2HBTTS': 8, 'sp.k.series_poll:KXLALIGA2HSPREAD': 6, 'sp.k.series_poll:KXLALIGA2HTOTAL': 4, 'sp.k.series_poll:KXLALIGACORNERS': 8, 'sp.k.series_poll:KXLALIGAGAME': 6, 'sp.k.series_poll:KXLALIGAGOAL': 6, 'sp.k.series_poll:KXAUTBUNDESGAME': 2, 'sp.k.series_poll:KXCZEFLTOTAL': 7, 'sp.k.series_poll:KXELITESERIENTOTAL': 2, 'sp.k.series_poll:KXEREDIVISIETOTAL': 2, 'sp.k.always:KXNCAAFGAME': 7, 'sp.k.series_poll:KXLIGUE11HBTTS': 3, 'sp.k.series_poll:KXLIGUE11HSCORE': 4, 'sp.k.series_poll:KXLIGUE11H': 4, 'sp.k.series_poll:KXLIGUE11HSPREAD': 1, 'sp.stream': 48}

## Catalogue (latest inventory, 04:50Z)

Polymarket US sports events 4428 of 5939 active events; Kalshi near-term sports markets 8186 in 825 events; calls so far {'pm': 1757, 'k': 17900}; MB {'pm': 3130088878, 'k': 7619144189}

| venue | sport / league / type | markets | two-sided | med spread | vol 24h |
|---|---|---|---|---|---|
| pm | football / nfl / futures | 3742 | 66% | 0.010 | 0 |
| pm | football / cfb / futures | 1597 | 78% | 0.010 | 0 |
| pm | basketball / nba / futures | 1452 | 56% | 0.020 | 0 |
| pm | ice-hockey / nhl / futures | 779 | 96% | 0.010 | 0 |
| pm | basketball / wcbb / basketball_team_full_game_winner | 584 | 28% | 0.415 | 0 |
| pm | basketball / cbb / basketball_team_full_game_winner | 553 | 29% | 0.055 | 0 |
| k | KXNCAAFGAME / College Football Game | 506 | 100% | 0.100 | 1189217 |
| pm | golf / worlwide / futures | 485 | 18% | 0.006 | 0 |
| pm | golf / lpga / futures | 440 | 0% | - | 0 |
| pm | soccer / epl / futures | 435 | 86% | 0.010 | 0 |
| pm | golf / abudhabc / futures | 352 | 0% | - | 0 |
| pm | basketball / cbb / futures | 317 | 85% | 0.010 | 0 |
| pm | soccer / ucl / futures | 276 | 78% | 0.010 | 0 |
| pm | table-tennis / setkameua / table_tennis_match_winner | 276 | 96% | 0.170 | 0 |
| pm | baseball / mlb / futures | 264 | 25% | 0.001 | 0 |
| pm | football / cfb / football_team_full_game_winner | 230 | 87% | 0.085 | 0 |
| k | KXNFLFFWEEKLEAD / Weekly Fantasy Football Leader | 230 | 100% | 0.120 | 1453 |
| pm | tennis / utr / tennis_match_winner | 227 | 25% | 0.410 | 0 |
| pm | tennis / itfme / tennis_match_winner | 219 | 63% | 0.010 | 0 |
| k | KXNBA3PT / NBA Player Threes | 180 | 100% | 0.100 | 224591 |
| pm | tennis / itfwo / tennis_match_winner | 176 | 68% | 0.010 | 0 |
| k | KXNBA3PTPROT / NBA Player Threes Protected | 175 | 100% | 1.000 | 5521 |
| pm | macro /  / futures | 150 | 75% | 0.010 | 0 |
| k | KXNFLFFWEEKTOP / Weekly Fantasy Football Top Players | 148 | 100% | 0.130 | 1843 |
| pm | soccer / lal / futures | 146 | 66% | 0.010 | 0 |
| pm | mma / ufc / futures | 145 | 83% | 0.010 | 0 |
| pm | boxing / boxing / futures | 145 | 0% | - | 0 |
| pm | motorsports / f1 / futures | 123 | 16% | 0.043 | 0 |
| k | KXNBAAST / NBA Player Assists | 119 | 100% | 0.080 | 115207 |
| k | KXNBAASTPROT / NBA Player Assists Protected | 115 | 100% | 1.000 | 370 |
| pm | tennis / atp / futures | 103 | 41% | 0.010 | 0 |
| pm | basketball / nba / basketball_team_full_game_winner | 101 | 74% | 0.260 | 0 |
| pm | tennis / atp / tennis_match_winner | 98 | 97% | 0.010 | 0 |
| pm | macro / usgas / futures | 89 | 11% | 0.390 | 0 |
| pm | soccer / sea / futures | 86 | 81% | 0.010 | 0 |
| pm | soccer / bun / futures | 80 | 84% | 0.010 | 0 |
| pm | esports / cs2 / esports_match_winner | 80 | 66% | 0.080 | 0 |
| pm | soccer / lg1 / futures | 77 | 84% | 0.010 | 0 |
| pm | tennis / wta / futures | 75 | 44% | 0.010 | 0 |
| pm | macro / usdsl / futures | 63 | 0% | - | 0 |
| pm | soccer / j2 / soccer_team_full_time_winner | 60 | 67% | 0.010 | 0 |
| pm | motorsports / nascar / futures | 57 | 25% | 0.055 | 0 |
| k | KXNBA2HSPREAD / NBA 2nd Half Spread | 57 | 100% | 0.120 | 87557 |
| k | KXNBA2HTOTAL / NBA 2nd Half Total | 57 | 100% | 0.330 | 47288 |
| pm | table-tennis / czechligapro / table_tennis_match_winner | 56 | 20% | 0.470 | 0 |
| pm | soccer / uecl / soccer_team_full_time_winner | 55 | 98% | 0.020 | 0 |
| pm | tennis / atpdb / tennis_match_winner | 55 | 47% | 0.385 | 0 |
| pm | soccer / ucl / soccer_team_full_time_winner | 54 | 100% | 0.010 | 0 |
| pm | soccer / uel / soccer_team_full_time_winner | 54 | 100% | 0.020 | 0 |
| pm | golf / masttour / futures | 52 | 100% | 0.499 | 0 |
| pm | tennis / wta / tennis_match_winner | 52 | 100% | 0.010 | 0 |
| pm | soccer / mls / futures | 51 | 92% | 0.010 | 0 |
| k | KXNBA2H / NBA 2nd Half Winner | 51 | 100% | 0.970 | 29987 |
| k | KXNBA3Q / NBA 3rd Quarter Winner | 51 | 100% | 0.990 | 67231 |
| k | KXNBA4Q / NBA 4th Quarter Winner | 51 | 100% | 0.990 | 2454 |
| pm | table-tennis / setkamecz / table_tennis_match_winner | 48 | 100% | 0.170 | 0 |
| k | KXNBA1H / NBA 1st Half Winner | 45 | 100% | 0.660 | 84815 |
| k | KXNBA2Q / NBA 2nd Quarter Winner | 45 | 100% | 0.990 | 29831 |
| pm | technology /  / futures | 42 | 74% | 0.010 | 0 |
| k | KXNBA1Q / NBA 1st Quarter Winner | 42 | 100% | 0.805 | 0 |

## Opportunities

| kind | distinct | hits | max margin $/contract | max persistence | fresh-BBO still open |
|---|---|---|---|---|---|
| decided_k | 196 | 5607 | 0.9893 | 169 min | 0/0 |
| decided_pm | 23 | 339 | 0.9947 | 21 min | 180/339 |
| decided_pm_closed | 12 | 147 | 0.9893 | 22 min | 0/147 |
| dutch_k | 15 | 69 | 0.0817 | 4 min | 0/0 |
| dutch_k_sell | 2 | 4 | 0.0066 | 0 min | 0/0 |
| dutch_pm | 50 | 2117 | 0.5316 | 50 min | 0/0 |
| implication_k | 1093 | 36651 | 0.9573 | 101 min | 0/0 |
| lag_k_settled | 208 | 33220 | 0.9973 | 294 min | 26826/32179 |
| lag_k_settled_closed | 181 | 2517 | 0.9973 | 272 min | 0/2517 |

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

**Total closed P&L: $-416.08 on $1573.08 staked (-26.5%)**

| rule | entries | closed | winners | staked | P&L | ROI |
|---|---|---|---|---|---|---|
| R1 anchor [ncaaf] | 26 | 26 | 11 | $262.99 | $-34.99 | -13% |
| R1 anchor [nfl] | 6 | 6 | 1 | $61.25 | $-42.25 | -69% |
| R2 q1cheap [ncaaf] | 37 | 37 | 2 | $194.50 | $-142.50 | -73% |
| R2 q1cheap [nfl] | 6 | 6 | 1 | $31.46 | $-2.46 | -8% |
| R3 blowout [ncaaf] | 16 | 16 | 1 | $339.32 | $-197.32 | -58% |
| R4 halftime [ncaaf] | 19 | 19 | 6 | $95.24 | $+9.76 | +10% |
| R6 decided [other] | 34 | 34 | 28 | $588.31 | $-6.31 | -1% |

| time (UTC) | rule | game | team | entry | contracts | why | result |
|---|---|---|---|---|---|---|---|
| 01:54 | R1 anchor | CHI Bears vs. SEA Seahawks | Chicago | 0.50 | 20 | pregame dog (mid 0.49) leads 7-0 in Q2, ask 0.50 | final score (pending Kalshi settlement): 0.00, $-10.35 |
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
| 19:09 | R6 decided | Alcorn State (W) vs. Ole Mis | Ole Miss wins by over 7.5 points | 0.99 | 20 | ended 38-80 margin 42 vs 7.5 | kalshi settled: 1.00, $+0.19 |
| 19:09 | R6 decided | Alcorn State (W) vs. Ole Mis | Ole Miss wins by over 29.5 points | 0.63 | 31 | ended 38-80 margin 42 vs 29.5 | kalshi settled: 1.00, $+10.96 |
| 19:09 | R6 decided | Alcorn State (W) vs. Ole Mis | Ole Miss wins by over 26.5 points | 0.69 | 28 | ended 38-80 margin 42 vs 26.5 | kalshi settled: 1.00, $+8.26 |
| 19:09 | R6 decided | Alcorn State (W) vs. Ole Mis | Ole Miss wins by over 22.5 points | 0.82 | 24 | ended 38-80 margin 42 vs 22.5 | kalshi settled: 1.00, $+4.07 |
| 19:09 | R6 decided | Alcorn State (W) vs. Ole Mis | Ole Miss wins by over 17.5 points | 0.93 | 21 | ended 38-80 margin 42 vs 17.5 | kalshi settled: 1.00, $+1.37 |
| 19:09 | R6 decided | Alcorn State (W) vs. Ole Mis | Ole Miss wins by over 12.5 points | 0.97 | 20 | ended 38-80 margin 42 vs 12.5 | kalshi settled: 1.00, $+0.56 |
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
- 26NOV02CHISEA 20-15: -0% / 117% / 100%

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
| football | KXNFLGAME | 24 | 2 | 22 | 1 | 0 | 0 | 0.02 (0) | 0 / $0.00 | 21 / 0 |
| soccer | KXDENSUPERLIGATOTAL | 22 | 0 | 22 | 0 | 0 | 0 | - | 0 / $0.00 | 22 / 0 |
| soccer | KXBELGIANPLTOTAL | 22 | 0 | 22 | 1 | 0 | 0 | 0.89 (454) | 763 / $22.89 | 22 / 0 |
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
| basketball | KXNCAAMBSPREAD | 9 | 2 | 0 | - | 7 | 0 | 0.62 (20) | 0 / $0.00 | 9 / 0 |
| soccer | KXTHAIL1TOTAL | 8 | 0 | 8 | 1 | 0 | 0 | 0.96 (13) | 0 / $0.00 | 8 / 0 |
| soccer | KXBUNDESLIGA2SPREAD | 8 | 0 | 8 | 2 | 0 | 0 | - | 0 / $0.00 | 8 / 0 |
| soccer | KXMLS1H | 8 | 0 | 6 | 0 | 2 | 0 | 0.63 (492) | 0 / $0.00 | 8 / 0 |
| soccer | KXDIMAYORTOTAL | 8 | 1 | 7 | 0 | 0 | 0 | - | 0 / $0.00 | 8 / 0 |
| soccer | KXPERLIGA1TOTAL | 8 | 8 | 0 | - | 0 | 0 | - | 0 / $0.00 | 8 / 0 |
| soccer | KXKLEAGUETOTAL | 7 | 0 | 7 | 1 | 0 | 0 | - | 0 / $0.00 | 7 / 0 |
| soccer | KXHNLTOTAL | 7 | 0 | 7 | 0 | 0 | 0 | - | 0 / $0.00 | 7 / 0 |
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
| basketball | KXLNBPTOTAL | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 0 / 0 |
| soccer | KXALLSVENSKANBTTS | 2 | 0 | 2 | 0 | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXEREDIVISIEBTTS | 2 | 0 | 2 | 0 | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXEREDIVISIESPREAD | 2 | 0 | 2 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / 0 |
| soccer | KXDENSUPERLIGASPREAD | 2 | 0 | 2 | 0 | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXLIGAEXPTOTAL | 2 | 0 | 2 | 1 | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXCHLLDPTOTAL | 2 | 0 | 2 | 1 | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXMLSBTTS | 2 | 0 | 2 | 1 | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXARGNACBBTTS | 2 | 1 | 1 | 1 | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| tennis | KXATPDOUBLES | 2 | 0 | 2 | 0 | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| basketball | KXNCAAMBGAME | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
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

2060 contracts decided while active; 196 had a price leaving > 0.4c after fees; 66 of those were mispriced AFTER the score was stable (lock tier)

| sport | game | contract | decided | reason | max margin | mispriced for | lock margin | lock depth |
|---|---|---|---|---|---|---|---|---|
| soccer | Houston Dash vs. Portland Thorns | KXMLS1HTOTAL-26NOV01PORHOU-2 | NO | 1H final (0, 1) <= 1.5 | 0.373 | 1010s | 0.373 | 1158 |
| soccer | Houston Dash vs. Portland Thorns | KXMLS1H-26NOV01PORHOU-TIE | NO | 1H final (0, 1) | 0.354 | 1010s | 0.354 | 492 |
| basketball | Alcorn State (W) vs. Ole Miss (W | KXNCAAMBSPREAD-26NOV02ALCNMISS-MISS30 | YES | ended 38-80 margin 42 vs 29.5 | 0.354 | 269s | 0.354 | 40 |
| tennis | Juan Manuel Cerundolo vs. Aleksa | KXATPSETWINNER-26OCT31CERKOV-1-KOV | NO | set 1 final 7-6 | 0.315 | 0s | 0.315 | 69 |
| tennis | Juan Manuel Cerundolo vs. Aleksa | KXATPSETWINNER-26OCT31CERKOV-1-CER | YES | set 1 final 7-6 | 0.315 | 0s | 0.315 | 202 |
| tennis | Adolfo Daniel Vallejo vs. Lorenz | KXATPMATCH-26NOV01VALSON-VAL | NO | ended 3-6, 6-4, 6-7(5-7) | 0.315 | 369s | 0.315 | 20485 |
| tennis | Adolfo Daniel Vallejo vs. Lorenz | KXATPMATCH-26NOV01VALSON-SON | YES | ended 3-6, 6-4, 6-7(5-7) | 0.315 | 369s | 0.315 | 35588 |
| basketball | Alcorn State (W) vs. Ole Miss (W | KXNCAAMBSPREAD-26NOV02ALCNMISS-MISS27 | YES | ended 38-80 margin 42 vs 26.5 | 0.295 | 269s | 0.295 | 40 |
| football | LV Raiders vs. NY Jets | KXNFLEQBTTS-26NOV01LVNYJ-Y | YES | both scored 35-30 | 0.276 | 559s | 0.276 | 160 |
| soccer | New England Revolution vs. Inter | KXMLSTOTAL-26NOV01NEMIA-3 | YES | score 1-2 total 3 > 2.5 | 0.276 | 10189s | 0.276 | 33106 |
| football | NE Patriots vs. MIA Dolphins | KXMLSBTTS-26NOV01NEMIA-BTTS | YES | both scored 24-13 | 0.266 | 6674s | 0.266 | 31858 |
| tennis | Lorenzo Musetti vs. Hubert Hurka | KXATPSETWINNER-26NOV01MUSHUR-2-HUR | NO | set 2 final 7-6 | 0.266 | 44s | 0.266 | 0 |
| soccer | AD Cali vs. Boyaca Chico FC | KXDIMAYORTOTAL-26NOV01CALCHI-2 | YES | score 2-0 total 2 > 1.5 | 0.237 | 1771s | 0.237 | 144 |
| basketball | Alcorn State (W) vs. Ole Miss (W | KXNCAAMBTOTAL-26NOV02ALCNMISS-154 | NO | ended total 118 <= 153.5 | 0.237 | 269s | 0.237 | 120 |
| soccer | Portland Timbers vs. Houston Dyn | KXMLS1HTOTAL-26NOV01PORHOU-1 | YES | 1H (1, 0) > 0.5 | 0.227 | 1010s | 0.227 | 2345 |
| soccer | Houston Dash vs. Portland Thorns | KXMLS1HBTTS-26NOV01PORHOU-BTTS | NO | 1H final (0, 1) | 0.208 | 1010s | 0.208 | 4846 |
| soccer | Houston Dash vs. Portland Thorns | KXMLS1H-26NOV01PORHOU-HOU | NO | 1H final (0, 1) | 0.179 | 1010s | 0.179 | 4248 |
| basketball | Alcorn State (W) vs. Ole Miss (W | KXNCAAMBTOTAL-26NOV02ALCNMISS-158 | NO | ended total 118 <= 157.5 | 0.179 | 269s | 0.179 | 158 |
| basketball | Alcorn State (W) vs. Ole Miss (W | KXNCAAMBSPREAD-26NOV02ALCNMISS-MISS23 | YES | ended 38-80 margin 42 vs 22.5 | 0.170 | 269s | 0.170 | 581 |
| basketball | Texas Southern (W) vs. Tulane (W | KXNCAAWBTOTAL-26NOV02TXSOTULN-133 | YES | score 57-137 total 194 > 132.5 | 0.170 | 575s | 0.170 | 11 |
| tennis | Adolfo Daniel Vallejo vs. Grigor | KXATPSETWINNER-26OCT31VALDIM-2-DIM | YES | set 2 final 4-6 | 0.160 | 0s | 0.160 | 154 |
| soccer | Colorado Rapids SC vs. Chicago F | KXMLSTOTAL-26OCT31COLCHI-3 | YES | score 2-2 total 4 > 2.5 | 0.160 | 706s | 0.160 | 25957 |
| tennis | Lorenzo Musetti vs. Hubert Hurka | KXATPSETWINNER-26NOV01MUSHUR-2-MUS | YES | set 2 final 7-6 | 0.160 | 44s | 0.160 | 5 |
| tennis | Mariia Tkacheva vs. Rada Zolotar | KXWTASETWINNER-26OCT31TKAZOL-2-ZOL | YES | set 2 final 1-2 | 0.151 | 332s | 0.151 | 2 |
| tennis | Mariia Tkacheva vs. Rada Zolotar | KXWTASETWINNER-26OCT31TKAZOL-2-TKA | NO | set 2 final 1-2 | 0.151 | 332s | 0.151 | 1 |

## Close / settlement latency (how clunky each venue is after the final whistle)

Kalshi: settlement_ts − close_time per series (negative = settled before the scheduled close)

| series | n | median | p90 |
|---|---|---|---|
| KXNFLPASSYDSPRECISE Pass Yards Precise | 12485 | 4.0 min | 4.1 min |
| KXESOCCERGAME eSoccer Game | 3634 | 4.0 min | 4.1 min |
| KXNCAAFSPREAD College Football Spread | 2228 | 4.0 min | 4.1 min |
| KXNCAAMBTOTAL Men's College Basketball Total | 1818 | 4.0 min | 4.1 min |
| KXNCAAFTOTAL College Football Total Points | 1626 | 4.0 min | 4.1 min |
| KXNCAAMBSPREAD Men's College Basketball Sprea | 1392 | 1.8 min | 1.8 min |
| KXNFLRECYDS Pro Football Receiving Yards | 1309 | 2.0 min | 2.1 min |
| KXNFLTOTALPRECISE Total Precise | 1248 | 4.0 min | 4.1 min |
| KXNBAREB NBA Player Rebounds | 1213 | 2.0 min | 2.1 min |
| KXNCAAFTEAMTOTAL College Football Team Total Po | 1137 | 4.0 min | 4.1 min |
| KXNFLRECYDSPROT Receiving Yards Protected | 1132 | 6.0 min | 6.1 min |
| KXNBA3PTPROT NBA Player Threes Protected | 1108 | 2.5 min | 2.6 min |
| KXNBAREBPROT NBA Player Rebounds Protected | 1081 | 2.5 min | 2.6 min |
| KXNHLGOAL NHL Goalscorer | 1080 | 3.0 min | 3.1 min |
| KXNBAPTS NBA Player Points | 1013 | 2.0 min | 2.1 min |
| KXNBA3PT NBA Player Threes | 1005 | 2.0 min | 2.1 min |
| KXNCAAF1HSPREAD College Football 1st Half Spre | 985 | 4.0 min | 4.1 min |
| KXLIGAPROMATCH Russia Liga Pro Match | 952 | 4.0 min | 4.1 min |
| KXNBAPTSPROT NBA Player Points Protected | 927 | 2.5 min | 2.6 min |
| KXNBATEAMTOTAL NBA Team Total | 907 | 2.5 min | 2.6 min |
| KXNBAASTPROT NBA Player Assists Protected | 905 | 2.5 min | 2.6 min |
| KXNFLREC Pro Football Player Receptions | 864 | 2.0 min | 2.1 min |
| KXNFLRECPROT Receptions Protected | 863 | 6.0 min | 6.1 min |
| KXNBAAST NBA Player Assists | 858 | 2.0 min | 2.1 min |
| KXNCAAWBTOTAL Women's College Basketball Tot | 835 | 2.5 min | 2.6 min |
| KXNHLPTS Pro Hockey Points | 819 | 3.0 min | 3.1 min |
| KXNCAAF2HSPREAD College Football 2nd Half Spre | 700 | 4.0 min | 4.1 min |
| KXNCAAF1HTOTAL College Football 1st Half Tota | 658 | 4.0 min | 4.1 min |
| KXNBASPREAD NBA Spread | 655 | 1.8 min | 1.8 min |
| KXNCAAWBSPREAD Women's College Basketball Spr | 643 | 1.8 min | 1.8 min |
| KXNBAPRA NBA Player Points + Rebounds + | 621 | 2.5 min | 2.6 min |
| KXMLSGOAL Goalscorer | 597 | 6.0 min | 6.1 min |
| KXNHLFIRSTGOAL NHL First Goal | 595 | 6.0 min | 6.0 min |
| KXNBATOTAL NBA Total | 581 | 1.8 min | 1.8 min |
| KXNHLAST Pro Hockey Assists | 571 | 6.0 min | 6.1 min |
| KXNFLRSHYDSPROT Rushing Yards Protected | 549 | 6.0 min | 6.1 min |
| KXNBA1HTEAMTOTAL NBA 1st Half Team Total | 529 | 2.5 min | 2.6 min |
| KXNFLRSHYDS Pro Football Rushing Yards | 513 | 2.0 min | 2.1 min |
| KXNFLTDPROT Pro Football Touchdowns Protec | 484 | 6.0 min | 6.1 min |
| KXNBA1HTOTAL NBA 1st Half Total | 471 | 2.5 min | 2.6 min |

## Participant fingerprint (per sport; 60 s snapshots)

change% = share of scan cycles (60 s) where the best quote moved; react = median minutes from a score change to the next quote move (humans: slow, bursty, round sizes; bots: constant cadence, odd/constant sizes, instant reaction)

| venue | sport | markets | snapshots | two-sided | med spread | change% | react (min) | round sizes | med size |
|---|---|---|---|---|---|---|---|---|---|
| pm | soccer | 1722 | 252786 | 86% | 0.020 | 19% | 0.6 (n=3847) | - | - |
| pm | tennis | 1770 | 106644 | 92% | 0.010 | 23% | 0.5 (n=48195) | - | - |
| pm | esports | 3186 | 76778 | 76% | 0.030 | 19% | 0.5 (n=16320) | - | - |
| pm | basketball | 900 | 68164 | 80% | 0.040 | 22% | 0.5 (n=11312) | - | - |
| pm | table-tennis | 1550 | 53000 | 95% | 0.030 | 32% | 0.5 (n=25801) | - | - |
| pm | football | 118 | 21730 | 91% | 0.005 | 17% | 1.1 (n=1073) | - | - |
| pm | climate | 215 | 11213 | 77% | 0.050 | 26% | - (n=0) | - | - |
| pm | motorsports | 159 | 8546 | 40% | 0.040 | 14% | - (n=0) | - | - |
| pm | ice-hockey | 60 | 5347 | 81% | 0.050 | 13% | 0.7 (n=292) | - | - |
| pm | misc | 47 | 3778 | 93% | 0.010 | 12% | - (n=0) | - | - |
| pm | beach-volleyball | 70 | 2702 | 84% | 0.010 | 24% | 0.5 (n=1398) | - | - |
| pm | cricket | 7 | 1808 | 91% | 0.020 | 15% | 1.0 (n=312) | - | - |
| pm | mma | 14 | 666 | 94% | 0.020 | 5% | - (n=0) | - | - |
| pm | technology | 24 | 316 | 46% | 0.195 | 29% | - (n=0) | - | - |
| pm | rugby | 17 | 226 | 68% | 0.450 | 19% | - (n=0) | - | - |
| pm | macro | 40 | 200 | 0% | - | 0% | - (n=0) | - | - |
| pm | boxing | 4 | 159 | 94% | 0.030 | 55% | - (n=0) | - | - |
| pm | darts | 7 | 141 | 69% | 0.070 | 17% | 0.5 (n=18) | - | - |
| pm | baseball | 2 | 105 | 92% | 0.140 | 11% | 2.3 (n=5) | - | - |
| pm | pickleball | 7 | 60 | 73% | 0.170 | 13% | - (n=0) | - | - |
| k | KXNCAAFGAME College Football Game | 714 | 584964 | 98% | 0.060 | 2% | - | 7% | 30 |
| k | KXNFLPASSYDSPRECISE Pass Yards Precise | 15652 | 185749 | 0% | 0.390 | 0% | - | 0% | 1 |
| k | KXNBA3PT NBA Player Threes | 1587 | 127391 | 76% | 0.130 | 14% | - | 31% | 40 |
| k | KXNFLGAME NFL Game | 56 | 119830 | 99% | 0.010 | 2% | - | 3% | 112248 |
| k | KXCS2MAP Counter-Strike 2 Map Win | 522 | 86051 | 92% | 0.440 | 4% | - | 19% | 102 |
| k | KXNBAAST NBA Player Assists | 1190 | 73220 | 77% | 0.140 | 13% | - | 29% | 32 |
| k | KXNBAPTS NBA Player Points | 1393 | 61817 | 76% | 0.120 | 18% | - | 25% | 30 |
| k | KXESOCCERGAME eSoccer Game | 3951 | 60522 | 20% | 0.520 | 6% | - | 29% | 32 |
| k | KXNCAAFSPREAD College Football Spread | 2548 | 56763 | 51% | 0.090 | 4% | - | 12% | 75 |
| k | KXNCAAMBTOTAL Men's College Basketball | 2528 | 56064 | 65% | 0.100 | 5% | - | 27% | 65 |
| k | KXNBAREB NBA Player Rebounds | 1526 | 54228 | 70% | 0.150 | 21% | - | 28% | 30 |
| k | KXNBA3PTPROT NBA Player Threes Protec | 1533 | 49275 | 23% | 0.190 | 2% | - | 27% | 162 |
| k | KXNCAAFTEAMTOTAL College Football Team To | 1204 | 46180 | 68% | 0.020 | 2% | - | 24% | 375 |
| k | KXNCAAMBSPREAD Men's College Basketball | 2036 | 44335 | 65% | 0.080 | 4% | - | 32% | 50 |
| k | KXNCAAWBTOTAL Women's College Basketba | 1290 | 38903 | 27% | 0.530 | 2% | - | 12% | 41 |
| k | KXNCAAFTOTAL College Football Total P | 1835 | 38889 | 48% | 0.140 | 4% | - | 16% | 135 |
| k | KXNCAAWBSPREAD Women's College Basketba | 1026 | 34284 | 24% | 0.570 | 3% | - | 18% | 41 |
| k | KXNBA1HSPREAD NBA 1st Half Spread | 494 | 32858 | 70% | 0.050 | 16% | - | 19% | 150 |
| k | KXNBA1HTOTAL NBA 1st Half Total | 494 | 32606 | 68% | 0.060 | 16% | - | 29% | 100 |
| k | KXATPSETWINNER ATP Set Winner | 224 | 32528 | 93% | 0.030 | 3% | - | 11% | 138 |
| k | KXNBA1HTEAMTOTAL NBA 1st Half Team Total | 572 | 31990 | 56% | 0.330 | 14% | - | 32% | 253 |
| k | KXNBA2HSPREAD NBA 2nd Half Spread | 532 | 31873 | 72% | 0.290 | 26% | - | 41% | 125 |
| k | KXMLSSCORE Correct Score | 450 | 31078 | 52% | 0.020 | 3% | - | 14% | 1192 |
| k | KXNBAASTPROT NBA Player Assists Prote | 1145 | 30423 | 20% | 0.140 | 2% | - | 21% | 162 |
| k | KXNBA2HTOTAL NBA 2nd Half Total | 532 | 30383 | 72% | 0.380 | 23% | - | 33% | 92 |
| k | KXATPCHALLENGERMATCH Challenger ATP  | 372 | 30029 | 90% | 0.010 | 8% | - | 5% | 616 |
| k | KXNCAAF1H College Football 1st Hal | 1038 | 28566 | 86% | 0.840 | 1% | - | 25% | 133 |
| k | KXNBAPTSPROT NBA Player Points Protec | 1278 | 24706 | 21% | 0.090 | 3% | - | 15% | 162 |
| k | KXWTASETWINNER WTA Set Winner | 250 | 24024 | 79% | 0.050 | 4% | - | 26% | 62 |
| k | KXNCAAWBGAME Women's College Basketba | 500 | 23636 | 83% | 0.120 | 5% | - | 12% | 12 |
| k | KXNBAPRA NBA Player Points + Rebo | 806 | 23488 | 62% | 0.390 | 20% | - | 13% | 5 |
| k | KXNFLTOTALPRECISE Total Precise | 1976 | 22799 | 4% | 0.060 | 2% | - | 21% | 2 |
| k | KXNBA3QSPREAD NBA 3rd Quarter Spread | 351 | 22620 | 76% | 0.060 | 23% | - | 54% | 100 |
| k | KXNBAREBPROT NBA Player Rebounds Prot | 1469 | 22436 | 16% | 0.170 | 4% | - | 25% | 200 |
| k | KXNBA3QTOTAL NBA 3rd Quarter Total | 351 | 20870 | 73% | 0.070 | 22% | - | 43% | 100 |
| k | KXNBA2QSPREAD NBA 2nd Quarter Spread | 338 | 20506 | 68% | 0.060 | 19% | - | 21% | 168 |
| k | KXNCAAF1HSPREAD College Football 1st Hal | 1020 | 20217 | 38% | 0.020 | 12% | - | 29% | 310 |
| k | KXNFLRECYDSPROT Receiving Yards Protecte | 1626 | 19862 | 11% | 0.740 | 5% | - | 15% | 19 |
| k | KXLIGAMXSCORE Correct Score | 209 | 19381 | 55% | 0.020 | 4% | - | 12% | 855 |
| k | KXNFLRECYDS Pro Football Receiving Y | 1739 | 18880 | 0% | - | 0% | - | 0% | - |

## Schema notes (raw keys seen)

- polymarket: active, archived, category, chatChannel, closed, combos, createdAt, description, elapsed, endDate, ended, eventState, fixtureId, gameId, hidden, id, insiderTradingRules, live, marketCounts, marketGroups, markets, metadata, participants, payoutEstimateMessage, payoutEstimateTime, period, primaryTag, score, seriesSlug, slug, sortType, sportradarGameId, startDate, startTime, streamProvider, streamRequiresAuth, tags, teams, ticker, title, updatedAt
- kalshi: can_close_early, close_time, created_time, custom_strike, early_close_condition, event_ticker, exchange_index, expected_expiration_time, expiration_time, expiration_value, last_price_dollars, latest_expiration_time, market_type, no_ask_dollars, no_bid_dollars, no_sub_title, notional_value_dollars, occurrence_datetime, open_interest_fp, open_time, previous_price_dollars, previous_yes_ask_dollars, previous_yes_bid_dollars, price_level_structure, price_ranges, primary_participant_key, result, rules_primary, rules_secondary, settlement_bounds_type, settlement_timer_seconds, status, strike_type, ticker, title, updated_time, volume_24h_fp, volume_fp, yes_ask_dollars, yes_ask_size_fp, yes_bid_dollars, yes_bid_size_fp, yes_sub_title

