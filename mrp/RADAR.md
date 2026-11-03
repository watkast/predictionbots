# Mr. P — sports radar

Updated 2026-11-03T20:46:07Z by `run-20261103T1802-41689834111` (last 7 days). Read-only scanner of every sports market on Polymarket US and Kalshi — it never places orders.
Kit: `mrp/mrp_sports_radar.py` on the `mrp` branch. Raw tape: `mrp/radar/<run>/`.

# Sports radar report

records 3,983,946 | 2026-10-31 20:44Z → 20:44Z | runs 28 | pairs matched 1567 | errors {'sp.k.series_poll:KXATPEXACTMATCH': 10, 'sp.k.series_poll:KXATPMATCH': 10, 'sp.k.series_poll:KXATPSETWINNER': 10, 'sp.k.series_poll:KXAUTBUNDESTOTAL': 4, 'sp.k.series_poll:KXEFLL11H': 6, 'sp.k.series_poll:KXEFLL11HSPREAD': 10, 'sp.k.series_poll:KXHNLTOTAL': 6, 'sp.k.series_poll:KXLALIGABTTS': 9, 'sp.k.series_poll:KXLALIGASCORE': 6, 'sp.k.series_poll:KXLALIGASPREAD': 8, 'sp.k.always:KXNFLGAME': 7, 'sp.k.series_poll:KXATPCHALLENGERMATCH': 7, 'sp.k.series_poll:KXEFLL11HBTTS': 10, 'sp.k.series_poll:KXLALIGA2H': 6, 'sp.k.series_poll:KXCS2MAP': 6, 'sp.k.series_poll:KXEFLL11HTOTAL': 8, 'sp.k.series_poll:KXLALIGA2HBTTS': 8, 'sp.k.series_poll:KXLALIGA2HSPREAD': 6, 'sp.k.series_poll:KXLALIGA2HTOTAL': 4, 'sp.k.series_poll:KXLALIGACORNERS': 8, 'sp.k.series_poll:KXLALIGAGAME': 6, 'sp.k.series_poll:KXLALIGAGOAL': 6, 'radar': 6, 'sp.k.series_poll:KXAUTBUNDESGAME': 2, 'sp.k.series_poll:KXCZEFLTOTAL': 7, 'sp.k.series_poll:KXELITESERIENTOTAL': 2, 'sp.k.series_poll:KXEREDIVISIETOTAL': 2, 'sp.k.always:KXNCAAFGAME': 7, 'sp.k.series_poll:KXLIGUE11HBTTS': 3, 'sp.k.series_poll:KXLIGUE11HSCORE': 4, 'sp.k.series_poll:KXLIGUE11H': 4, 'sp.k.series_poll:KXLIGUE11HSPREAD': 1, 'sp.stream': 48}

## Catalogue (latest inventory, 18:11Z)

Polymarket US sports events 4338 of 5850 active events; Kalshi near-term sports markets 819 in 370 events; calls so far {'pm': 50, 'k': 512}; MB {'pm': 183869160, 'k': 73163353}

| venue | sport / league / type | markets | two-sided | med spread | vol 24h |
|---|---|---|---|---|---|
| pm | football / nfl / futures | 3740 | 66% | 0.010 | 0 |
| pm | football / cfb / futures | 1597 | 76% | 0.010 | 0 |
| pm | basketball / nba / futures | 1380 | 58% | 0.010 | 0 |
| pm | ice-hockey / nhl / futures | 779 | 93% | 0.010 | 0 |
| pm | basketball / wcbb / basketball_team_full_game_winner | 619 | 27% | 0.400 | 0 |
| pm | basketball / cbb / basketball_team_full_game_winner | 591 | 22% | 0.070 | 0 |
| k | KXNCAAFGAME / College Football Game | 506 | 100% | 0.100 | 1170873 |
| pm | golf / worlwide / futures | 490 | 37% | 0.007 | 0 |
| pm | golf / lpga / futures | 440 | 0% | - | 0 |
| pm | soccer / epl / futures | 435 | 84% | 0.010 | 0 |
| pm | golf / abudhabc / futures | 352 | 37% | 0.008 | 0 |
| pm | basketball / cbb / futures | 317 | 85% | 0.010 | 0 |
| pm | soccer / ucl / futures | 276 | 78% | 0.010 | 0 |
| pm | football / cfb / football_team_full_game_winner | 236 | 91% | 0.080 | 0 |
| pm | tennis / utr / tennis_match_winner | 197 | 42% | 0.010 | 0 |
| pm | tennis / itfme / tennis_match_winner | 186 | 63% | 0.045 | 0 |
| pm | tennis / itfwo / tennis_match_winner | 183 | 63% | 0.070 | 0 |
| pm | macro /  / futures | 150 | 81% | 0.010 | 0 |
| pm | soccer / lal / futures | 146 | 66% | 0.010 | 0 |
| pm | mma / ufc / futures | 145 | 83% | 0.010 | 0 |
| pm | boxing / boxing / futures | 145 | 0% | - | 0 |
| pm | motorsports / f1 / futures | 123 | 16% | 0.009 | 0 |
| pm | pickleball / ppa / pickleball_match_winner | 118 | 0% | - | 0 |
| pm | basketball / nba / basketball_team_full_game_winner | 103 | 72% | 0.225 | 0 |
| pm | tennis / atp / futures | 96 | 38% | 0.010 | 0 |
| pm | table-tennis / setkameua / table_tennis_match_winner | 93 | 99% | 0.100 | 0 |
| pm | macro / usgas / futures | 87 | 7% | 0.010 | 0 |
| pm | soccer / sea / futures | 86 | 83% | 0.010 | 0 |
| pm | soccer / bun / futures | 80 | 81% | 0.010 | 0 |
| pm | tennis / atp / tennis_match_winner | 79 | 82% | 0.010 | 0 |
| pm | esports / cs2 / esports_match_winner | 79 | 70% | 0.010 | 0 |
| pm | soccer / lg1 / futures | 77 | 83% | 0.010 | 0 |
| pm | tennis / wta / futures | 75 | 44% | 0.010 | 0 |
| pm | baseball / mlb / futures | 72 | 72% | 0.001 | 0 |
| pm | soccer / eflch / soccer_team_full_time_winner | 72 | 94% | 0.020 | 0 |
| pm | macro / usdsl / futures | 63 | 0% | - | 0 |
| pm | motorsports / nascar / futures | 62 | 32% | 0.020 | 0 |
| k | KXNFLGAME / NFL Game | 58 | 100% | 0.020 | 1240814 |
| pm | soccer / uecl / soccer_team_full_time_winner | 55 | 98% | 0.020 | 0 |
| pm | table-tennis / czechligapro / table_tennis_match_winner | 55 | 15% | 0.475 | 0 |
| pm | soccer / ucl / soccer_team_full_time_winner | 54 | 100% | 0.010 | 0 |
| pm | soccer / uel / soccer_team_full_time_winner | 54 | 100% | 0.010 | 0 |
| pm | golf / masttour / futures | 52 | 100% | 0.499 | 0 |
| pm | soccer / mls / futures | 51 | 92% | 0.010 | 0 |
| pm | tennis / atpdb / tennis_match_winner | 50 | 40% | 0.070 | 0 |
| pm | technology /  / futures | 42 | 74% | 0.010 | 0 |
| pm | ice-hockey / nhl / hockey_team_full_game_winner | 41 | 100% | 0.010 | 0 |
| pm | soccer / lmx / futures | 36 | 31% | 0.040 | 0 |
| pm | soccer / uel / futures | 36 | 0% | - | 0 |
| pm | soccer / uecl / futures | 36 | 0% | - | 0 |
| pm | soccer / par1 / soccer_team_full_time_winner | 36 | 67% | 0.030 | 0 |
| pm | tennis / wta / tennis_match_winner | 35 | 86% | 0.010 | 0 |
| pm | soccer / bel1 / soccer_team_full_time_winner | 30 | 90% | 0.040 | 0 |
| pm | soccer / lal / soccer_team_full_time_winner | 30 | 100% | 0.010 | 0 |
| pm | soccer / epl / soccer_team_full_time_winner | 30 | 100% | 0.010 | 0 |
| pm | soccer / sea / soccer_team_full_time_winner | 30 | 100% | 0.010 | 0 |
| pm | soccer / tff1 / soccer_team_full_time_winner | 30 | 33% | 0.425 | 0 |
| pm | soccer / serca / soccer_team_full_time_winner | 30 | 33% | 0.465 | 0 |
| pm | soccer / j1 / soccer_team_full_time_winner | 30 | 100% | 0.045 | 0 |
| pm | soccer / j2 / soccer_team_full_time_winner | 30 | 100% | 0.070 | 0 |

## Opportunities

| kind | distinct | hits | max margin $/contract | max persistence | fresh-BBO still open |
|---|---|---|---|---|---|
| decided_k | 158 | 5407 | 0.9893 | 169 min | 0/0 |
| decided_pm | 17 | 255 | 0.9893 | 7 min | 140/255 |
| decided_pm_closed | 12 | 196 | 0.9893 | 14 min | 0/196 |
| dutch_k | 13 | 57 | 0.0429 | 24 min | 0/0 |
| dutch_pm | 36 | 2258 | 0.4629 | 50 min | 0/0 |
| implication_k | 41 | 2118 | 0.7040 | 101 min | 0/0 |
| lag_k_settled | 197 | 28465 | 0.9973 | 294 min | 23610/27912 |
| lag_k_settled_closed | 162 | 2282 | 0.9973 | 108 min | 0/2282 |

Top by persistence × hits:

- **lag_k_settled** basketball — Charleston Southern vs. South Florida — bid 0.01 ask 0.02 sell_yes @ 0.01 | margin 0.0373 | 294 min, 593 hits | fresh bbo 0.01/0.02 depth 1/37 | score 52-68 H2
- **lag_k_settled** football — North Alabama vs. Central Arkansas — bid 0.99 ask - sell_yes @ 0.995 | margin 0.9947 | 212 min, 606 hits | fresh bbo 0.99/- depth 13/0 | score 14-9 FT
- **lag_k_settled** basketball — Grambling State vs. Northern Illinois — bid 0.25 ask 0.28 sell_yes @ 0.25 | margin 0.2466 | 223 min, 521 hits | fresh bbo 0.24/0.25 depth 7/15 | score - NS
- **lag_k_settled** esports — SEIJI ESPORTS vs. ZANSIDE GAMING — bid 0.20 ask 0.30 sell_yes @ 0.2 | margin 0.1985 | 120 min, 479 hits | fresh bbo 0.20/0.30 depth 7/8 | score - NS
- **decided_k** 🔒 football — NE Patriots vs. MIA Dolphins — buy_yes @ 0.77 | margin 0.2756 | 169 min, 418 hits | score 24-19 Q4
- **decided_k** 🔒 football — NE Patriots vs. MIA Dolphins — buy_yes @ 0.92 | margin 0.1031 | 169 min, 418 hits | score 24-19 Q4
- **decided_k** 🔒 football — NE Patriots vs. MIA Dolphins — buy_yes @ 0.99 | margin 0.0280 | 169 min, 418 hits | score 24-19 Q4
- **decided_k** 🔒 football — NE Patriots vs. MIA Dolphins — buy_yes @ 0.77 | margin 0.2659 | 111 min, 441 hits | score 24-13 Q4
- **lag_k_settled** basketball — Western Michigan vs. Old Dominion — bid 0.51 ask 0.53 sell_yes @ 0.51 | margin 0.5027 | 111 min, 423 hits | fresh bbo 0.51/0.53 depth 46/44 | score - NS
- **implication_k** 🔒  — 26NOV01NEMIA — | margin 0.6541 | 101 min, 424 hits | score - 
- **decided_k** soccer — New England Revolution vs. Inter Miami CF — buy_yes @ 0.23 | margin 0.7576 | 126 min, 397 hits | score 2-2 90'
- **decided_k** football — NE Patriots vs. MIA Dolphins — buy_yes @ 0.2 | margin 0.8201 | 126 min, 390 hits | score 24-19 Q4
- **decided_k** football — NE Patriots vs. MIA Dolphins — buy_yes @ 0.36 | margin 0.6750 | 126 min, 390 hits | score 24-19 Q4
- **lag_k_settled** tennis — Nagy - Zelnickova vs. Daems - Tian — bid 0.57 ask 0.78 sell_yes @ 0.57 | margin 0.5530 | 120 min, 360 hits | fresh bbo 0.57/0.78 depth 4/5 | score 0-0 
- **lag_k_settled** esports — Glitchtech Esports vs. BOJONG — bid - ask 0.01 buy_yes @ 0.01 | margin 0.9893 | 94 min, 373 hits | fresh bbo -/0.01 depth 0/27 | score 0-0 Map 1
- **lag_k_settled** basketball — Villanova (W) vs. Notre Dame (W) — bid 0.01 ask 0.02 sell_yes @ 0.01 | margin 0.2563 | 92 min, 364 hits | fresh bbo -/0.02 depth 0/36 | score 45-65 H2
- **lag_k_settled** tennis — Aytekin - Tan vs. Januchowski - Sotikovs — bid 0.30 ask 0.50 buy_yes @ 0.5 | margin 0.4826 | 90 min, 359 hits | fresh bbo 0.06/0.95 depth 4/3 | score 0-0 
- **lag_k_settled** tennis — Burdet - Senn vs. Herck - Wygona — bid 0.46 ask 0.55 sell_yes @ 0.46 | margin 0.5027 | 120 min, 320 hits | fresh bbo 0.42/0.50 depth 6/13 | score 3-3:30-40 S1
- **lag_k_settled** football — Delaware State vs. Norfolk State — bid 0.99 ask - sell_yes @ 0.995 | margin 0.9947 | 88 min, 346 hits | fresh bbo 0.99/- depth 13/0 | score 36-33 FT
- **lag_k_settled** football — Montana vs. Eastern Washington — bid 0.99 ask - sell_yes @ 0.995 | margin 0.9947 | 85 min, 335 hits | fresh bbo 0.99/- depth 14/0 | score 42-33 FT
- **lag_k_settled** soccer — New England Revolution vs. Inter Miami CF — bid 0.17 ask 0.18 buy_yes @ 0.18 | margin 0.8097 | 70 min, 310 hits | fresh bbo 0.17/0.18 depth 12/37 | score 1-1 2H
- **lag_k_settled** soccer — New England Revolution vs. Inter Miami CF — bid 0.54 ask 0.55 sell_yes @ 0.54 | margin 0.5227 | 70 min, 310 hits | fresh bbo 0.53/0.54 depth 25/42 | score 1-1 2H
- **lag_k_settled** soccer — New England Revolution vs. Inter Miami CF — bid 0.28 ask 0.29 sell_yes @ 0.28 | margin 0.4328 | 70 min, 310 hits | fresh bbo 0.28/0.29 depth 17/44 | score 1-1 2H
- **lag_k_settled** soccer — Portland Timbers vs. Houston Dynamo — bid 0.55 ask 0.56 buy_yes @ 0.56 | margin 0.4229 | 75 min, 300 hits | fresh bbo 0.55/0.56 depth 19/26 | score 0-0 
- **lag_k_settled** soccer — Portland Timbers vs. Houston Dynamo — bid 0.23 ask 0.24 sell_yes @ 0.23 | margin 0.2177 | 75 min, 300 hits | fresh bbo 0.23/0.24 depth 12/26 | score 0-0 

## Live paper trades (no orders; Kalshi prices, taker fees)

Ledger L2-2026-11-01 (earlier ledgers excluded: none)

**Total closed P&L: $-222.52 on $921.52 staked (-24.1%)**

| rule | entries | closed | winners | staked | P&L | ROI |
|---|---|---|---|---|---|---|
| R1 anchor [ncaaf] | 7 | 7 | 4 | $71.28 | $+22.72 | +32% |
| R1 anchor [nfl] | 6 | 6 | 1 | $61.25 | $-42.25 | -69% |
| R2 q1cheap [ncaaf] | 4 | 4 | 0 | $20.96 | $-20.96 | -100% |
| R2 q1cheap [nfl] | 6 | 6 | 1 | $31.46 | $-2.46 | -8% |
| R3 blowout [ncaaf] | 7 | 7 | 0 | $148.55 | $-148.55 | -100% |
| R4 halftime [ncaaf] | 8 | 8 | 3 | $39.74 | $-11.74 | -30% |
| R6 decided [other] | 32 | 32 | 26 | $548.28 | $-19.28 | -4% |

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
| basketball | KXNCAAMBTOTAL | 178 | 173 | 0 | - | 5 | 0 | 0.75 (120) | 0 / $0.00 | 171 / 0 |
| basketball | KXNCAAWBTOTAL | 125 | 119 | 6 | 370 | 0 | 0 | 0.01 (1600) | 298 / $8.94 | 116 / 6 |
| basketball | KXNCAAMBSPREAD | 119 | 112 | 0 | - | 7 | 0 | 0.62 (20) | 0 / $0.00 | 119 / 0 |
| basketball | KXNCAAWBSPREAD | 68 | 68 | 0 | - | 0 | 0 | - | 0 / $0.00 | 68 / 0 |
| tennis | KXWTASETWINNER | 58 | 30 | 28 | 1 | 0 | 0 | - | 0 / $0.00 | 56 / 0 |
| soccer | KXAFCCLTOTAL | 58 | 55 | 3 | 2 | 0 | 0 | 0.31 (28) | 24398 / $731.93 | 58 / 0 |
| tennis | KXATPCHALLENGERMATCH | 56 | 17 | 39 | 0 | 0 | 0 | 0.97 (53) | 0 / $0.00 | 50 / 0 |
| soccer | KXJ2LEAGUETOTAL | 55 | 55 | 0 | - | 0 | 0 | - | 0 / $0.00 | 51 / 0 |
| tennis | KXATPSETWINNER | 48 | 10 | 38 | 0 | 0 | 0 | - | 0 / $0.00 | 44 / 0 |
| soccer | KXALLSVENSKANTOTAL | 38 | 12 | 26 | 1 | 0 | 0 | - | 0 / $0.00 | 38 / 0 |
| soccer | KXMLSTOTAL | 38 | 0 | 36 | 0 | 2 | 0 | 0.82 (29) | 188 / $5.63 | 36 / 0 |
| soccer | KXJ2LEAGUESPREAD | 35 | 35 | 0 | - | 0 | 0 | - | 0 / $0.00 | 35 / 0 |
| basketball | KXNBASPREAD | 33 | 33 | 0 | - | 0 | 0 | - | 0 / $0.00 | 33 / 0 |
| soccer | KXEREDIVISIETOTAL | 30 | 0 | 30 | 0 | 0 | 0 | - | 0 / $0.00 | 26 / 0 |
| soccer | KXELITESERIENTOTAL | 26 | 0 | 26 | 0 | 0 | 0 | - | 0 / $0.00 | 22 / 0 |
| soccer | KXLIGAFTOTAL | 25 | 5 | 20 | 1 | 0 | 0 | 0.98 (87) | 0 / $0.00 | 25 / 0 |
| soccer | KXSERIECTOTAL | 24 | 4 | 20 | 1 | 0 | 0 | 0.97 (3) | 0 / $0.00 | 24 / 0 |
| football | KXNFLGAME | 24 | 2 | 22 | 1 | 0 | 0 | 0.02 (0) | 0 / $0.00 | 21 / 0 |
| soccer | KXJ2LEAGUEGAME | 24 | 24 | 0 | - | 0 | 0 | - | 0 / $0.00 | 24 / 0 |
| soccer | KXDENSUPERLIGATOTAL | 22 | 0 | 22 | 0 | 0 | 0 | - | 0 / $0.00 | 22 / 0 |
| soccer | KXBELGIANPLTOTAL | 22 | 0 | 22 | 1 | 0 | 0 | 0.89 (454) | 763 / $22.89 | 22 / 0 |
| soccer | KXIDNSLTOTAL | 21 | 0 | 21 | 1 | 0 | 0 | 0.96 (62) | 0 / $0.00 | 21 / 0 |
| basketball | KXNCAAMBGAME | 20 | 20 | 0 | - | 0 | 0 | - | 0 / $0.00 | 20 / 0 |
| soccer | KXBUNDESLIGA2TOTAL | 19 | 0 | 19 | 2 | 0 | 0 | - | 0 / $0.00 | 19 / 0 |
| soccer | KXAUTBUNDESTOTAL | 19 | 0 | 19 | 1 | 0 | 0 | - | 0 / $0.00 | 13 / 1 |
| soccer | KXEKSTRAKLASATOTAL | 18 | 18 | 0 | - | 0 | 0 | - | 0 / $0.00 | 18 / 0 |
| soccer | KXECULPTOTAL | 17 | 6 | 11 | 0 | 0 | 0 | 0.93 (23) | 0 / $0.00 | 17 / 0 |
| soccer | KXBRASILEIROBTOTAL | 15 | 6 | 9 | 0 | 0 | 0 | - | 0 / $0.00 | 14 / 0 |
| soccer | KXLIGUE2TOTAL | 15 | 15 | 0 | - | 0 | 0 | - | 0 / $0.00 | 15 / 0 |
| soccer | KXAFCCLSPREAD | 15 | 15 | 0 | - | 0 | 0 | - | 0 / $0.00 | 15 / 0 |
| football | KXNFLTOTALPRECISE | 14 | 0 | 14 | 1 | 0 | 0 | - | 0 / $0.00 | 0 / 0 |
| basketball | KXNCAAWBGAME | 14 | 14 | 0 | - | 0 | 0 | - | 0 / $0.00 | 14 / 0 |
| soccer | KXHUNNB1TOTAL | 12 | 0 | 12 | 1 | 0 | 0 | - | 0 / $0.00 | 12 / 0 |
| soccer | KXMLS1HTOTAL | 12 | 0 | 9 | 0 | 3 | 0 | 0.61 (1157) | 0 / $0.00 | 12 / 0 |
| soccer | KXARGPREMDIVTOTAL | 12 | 10 | 2 | 1 | 0 | 0 | - | 0 / $0.00 | 12 / 0 |
| soccer | KXARGNACBTOTAL | 12 | 11 | 1 | 1 | 0 | 0 | - | 0 / $0.00 | 12 / 0 |
| soccer | KXUCLTOTAL | 12 | 12 | 0 | - | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| soccer | KXEFLCHAMPIONSHIP1HTOTAL | 12 | 12 | 0 | - | 0 | 0 | - | 0 / $0.00 | 0 / 0 |
| soccer | KXALLSVENSKANSPREAD | 10 | 5 | 5 | 0 | 0 | 0 | - | 0 / $0.00 | 10 / 0 |
| tennis | KXATPEXACTMATCH | 9 | 0 | 9 | 1 | 0 | 0 | - | 0 / $0.00 | 9 / 0 |
| basketball | KXFIBACHAMPTOTAL | 9 | 9 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXTHAIL1TOTAL | 8 | 0 | 8 | 1 | 0 | 0 | 0.96 (13) | 0 / $0.00 | 8 / 0 |
| soccer | KXBUNDESLIGA2SPREAD | 8 | 0 | 8 | 2 | 0 | 0 | - | 0 / $0.00 | 8 / 0 |
| soccer | KXMLS1H | 8 | 0 | 6 | 0 | 2 | 0 | 0.63 (492) | 0 / $0.00 | 8 / 0 |
| soccer | KXDIMAYORTOTAL | 8 | 1 | 7 | 0 | 0 | 0 | - | 0 / $0.00 | 8 / 0 |
| soccer | KXPERLIGA1TOTAL | 8 | 8 | 0 | - | 0 | 0 | - | 0 / $0.00 | 8 / 0 |
| soccer | KXJ2LEAGUEBTTS | 8 | 8 | 0 | - | 0 | 0 | - | 0 / $0.00 | 8 / 0 |
| soccer | KXKLEAGUETOTAL | 7 | 0 | 7 | 1 | 0 | 0 | - | 0 / $0.00 | 7 / 0 |
| soccer | KXHNLTOTAL | 7 | 0 | 7 | 0 | 0 | 0 | - | 0 / $0.00 | 7 / 0 |
| tennis | KXATPMATCH | 6 | 0 | 6 | 1 | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| soccer | KXCZEFNLTOTAL | 6 | 0 | 6 | 0 | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| soccer | KXSLGREECETOTAL | 6 | 5 | 1 | 0 | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| soccer | KXUCLSPREAD | 6 | 6 | 0 | - | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
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
| soccer | KXAFCCLBTTS | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXARGNACBGAME | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| basketball | KXLNBPTOTAL | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 0 / 0 |
| soccer | KXUCL1HTOTAL | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXUCL1H | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXUCLGAME | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| basketball | KXEUROCUPTOTAL | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXALLSVENSKANBTTS | 2 | 0 | 2 | 0 | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXEREDIVISIEBTTS | 2 | 0 | 2 | 0 | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXEREDIVISIESPREAD | 2 | 0 | 2 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / 0 |
| soccer | KXDENSUPERLIGASPREAD | 2 | 0 | 2 | 0 | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXLIGAEXPTOTAL | 2 | 0 | 2 | 1 | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXCHLLDPTOTAL | 2 | 0 | 2 | 1 | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXMLSBTTS | 2 | 0 | 2 | 1 | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXARGNACBBTTS | 2 | 1 | 1 | 1 | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| tennis | KXATPDOUBLES | 2 | 0 | 2 | 0 | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXLIGUE1TOTAL | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXBRASILEIROTOTAL | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| basketball | KXNBAGAME | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| tennis | KXWTACHALLENGERMATCH | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| basketball | KXKORISLIIGAGAME | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| basketball | KXEUROCUPGAME | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 0 / 0 |
| esports | KXCS2TOTALMAPS | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 0 / 0 |
| soccer | KXIDNSLBTTS | 1 | 0 | 1 | 0 | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXBUNDESLIGA2BTTS | 1 | 0 | 1 | 0 | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXDENSUPERLIGABTTS | 1 | 0 | 1 | 0 | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXSCOCUPTOTAL | 1 | 0 | 1 | 0 | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXSUPERLIGTOTAL | 1 | 0 | 1 | 0 | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXELITESERIENBTTS | 1 | 0 | 1 | 0 | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| football | KXNFLEQBTTS | 1 | 0 | 0 | - | 1 | 0 | 0.54 (28) | 10 / $0.30 | 1 / 0 |
| football | KXMLSBTTS | 1 | 0 | 0 | - | 1 | 0 | 0.72 (25231) | 0 / $0.00 | 1 / 0 |
| soccer | KXBRASILEIROBBTTS | 1 | 0 | 1 | 1 | 0 | 0 | - | 0 / $0.00 | 0 / 0 |
| soccer | KXSERIECBTTS | 1 | 0 | 1 | 17 | 0 | 0 | 0.97 (11) | 0 / $0.00 | 1 / 0 |
| soccer | KXLIGUE1BTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXARGPREMDIVBTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXUCL1HBTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |

'Already priced' = the book was at 99c+ when we first looked (bots were faster than our score feed). 'Median s mispriced' runs from our decision to the fix. 'Settled right / wrong' checks our certainty against Kalshi's result — any 'wrong' means the score feed or the model failed.

## Decided-state engine (contracts the live score already settled, still trading)

2027 contracts decided while active; 158 had a price leaving > 0.4c after fees; 49 of those were mispriced AFTER the score was stable (lock tier)

| sport | game | contract | decided | reason | max margin | mispriced for | lock margin | lock depth |
|---|---|---|---|---|---|---|---|---|
| soccer | Houston Dash vs. Portland Thorns | KXMLS1HTOTAL-26NOV01PORHOU-2 | NO | 1H final (0, 1) <= 1.5 | 0.373 | 1010s | 0.373 | 1158 |
| soccer | Houston Dash vs. Portland Thorns | KXMLS1H-26NOV01PORHOU-TIE | NO | 1H final (0, 1) | 0.354 | 1010s | 0.354 | 492 |
| basketball | Alcorn State (W) vs. Ole Miss (W | KXNCAAMBSPREAD-26NOV02ALCNMISS-MISS30 | YES | ended 38-80 margin 42 vs 29.5 | 0.354 | 269s | 0.354 | 40 |
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
| soccer | Colorado Rapids SC vs. Chicago F | KXMLSTOTAL-26OCT31COLCHI-3 | YES | score 2-2 total 4 > 2.5 | 0.160 | 706s | 0.160 | 25957 |
| tennis | Lorenzo Musetti vs. Hubert Hurka | KXATPSETWINNER-26NOV01MUSHUR-2-MUS | YES | set 2 final 7-6 | 0.160 | 44s | 0.160 | 5 |
| soccer | Houston Dash vs. Portland Thorns | KXMLS1HTOTAL-26NOV01PORHOU-3 | NO | 1H final (0, 1) <= 2.5 | 0.141 | 1010s | 0.141 | 144 |
| basketball | Texas Southern (W) vs. Tulane (W | KXNCAAWBTOTAL-26NOV02TXSOTULN-130 | YES | score 57-137 total 194 > 129.5 | 0.141 | 575s | 0.141 | 62 |
| basketball | Alcorn State (W) vs. Ole Miss (W | KXNCAAMBTOTAL-26NOV02ALCNMISS-162 | NO | ended total 118 <= 161.5 | 0.122 | 269s | 0.122 | 500 |
| soccer | New England Revolution vs. Inter | KXMLSTOTAL-26NOV01NEMIA-2 | YES | score 1-2 total 3 > 1.5 | 0.103 | 10189s | 0.103 | 22035 |
| basketball | Texas Southern (W) vs. Tulane (W | KXNCAAWBTOTAL-26NOV02TXSOTULN-140 | YES | score 57-137 total 194 > 139.5 | 0.103 | 575s | 0.103 | 100 |

## Close / settlement latency (how clunky each venue is after the final whistle)

Kalshi: settlement_ts − close_time per series (negative = settled before the scheduled close)

| series | n | median | p90 |
|---|---|---|---|
| KXNFLPASSYDSPRECISE Pass Yards Precise | 13465 | 4.0 min | 4.1 min |
| KXESOCCERGAME eSoccer Game | 3523 | 4.0 min | 4.1 min |
| KXNCAAMBTOTAL Men's College Basketball Total | 2061 | 4.0 min | 4.1 min |
| KXNCAAMBSPREAD Men's College Basketball Sprea | 1597 | 1.8 min | 1.8 min |
| KXNCAAFSPREAD College Football Spread | 1534 | 4.0 min | 4.1 min |
| KXNFLTOTALPRECISE Total Precise | 1400 | 4.0 min | 4.1 min |
| KXNBA3PTPROT NBA Player Threes Protected | 1335 | 2.5 min | 2.6 min |
| KXNFLRECYDS Pro Football Receiving Yards | 1309 | 2.0 min | 2.1 min |
| KXNBAREB NBA Player Rebounds | 1304 | 2.0 min | 2.1 min |
| KXNFLRECYDSPROT Receiving Yards Protected | 1258 | 6.0 min | 6.1 min |
| KXNBAREBPROT NBA Player Rebounds Protected | 1201 | 2.5 min | 2.6 min |
| KXNBA3PT NBA Player Threes | 1173 | 2.0 min | 2.1 min |
| KXNBAPTS NBA Player Points | 1146 | 2.0 min | 2.1 min |
| KXNCAAFTOTAL College Football Total Points | 1129 | 4.0 min | 4.1 min |
| KXNBAPTSPROT NBA Player Points Protected | 1037 | 2.5 min | 2.6 min |
| KXNBATEAMTOTAL NBA Team Total | 1028 | 2.5 min | 2.6 min |
| KXNBAASTPROT NBA Player Assists Protected | 984 | 2.5 min | 2.6 min |
| KXNHLGOAL NHL Goalscorer | 939 | 3.0 min | 3.1 min |
| KXNBAAST NBA Player Assists | 915 | 2.0 min | 2.1 min |
| KXNFLRECPROT Receptions Protected | 893 | 6.0 min | 6.1 min |
| KXNCAAWBTOTAL Women's College Basketball Tot | 873 | 2.5 min | 2.6 min |
| KXNFLREC Pro Football Player Receptions | 864 | 2.0 min | 2.1 min |
| KXNCAAFTEAMTOTAL College Football Team Total Po | 789 | 4.0 min | 4.1 min |
| KXNHLPTS Pro Hockey Points | 784 | 3.0 min | 3.1 min |
| KXNBASPREAD NBA Spread | 754 | 1.8 min | 1.8 min |
| KXNBAPRA NBA Player Points + Rebounds + | 727 | 2.5 min | 2.6 min |
| KXLIGAPROMATCH Russia Liga Pro Match | 700 | 4.0 min | 4.1 min |
| KXNBATOTAL NBA Total | 674 | 1.8 min | 1.8 min |
| KXNCAAF1HSPREAD College Football 1st Half Spre | 669 | 4.0 min | 4.1 min |
| KXNCAAWBSPREAD Women's College Basketball Spr | 664 | 1.8 min | 1.8 min |
| KXNHLFIRSTGOAL NHL First Goal | 549 | 6.0 min | 6.0 min |
| KXNFLRSHYDSPROT Rushing Yards Protected | 549 | 6.0 min | 6.1 min |
| KXNHLAST Pro Hockey Assists | 544 | 6.0 min | 6.1 min |
| KXNCAAF2HSPREAD College Football 2nd Half Spre | 531 | 4.0 min | 4.1 min |
| KXNBA1HTEAMTOTAL NBA 1st Half Team Total | 529 | 2.5 min | 2.6 min |
| KXNFLTDPROT Pro Football Touchdowns Protec | 526 | 6.0 min | 6.1 min |
| KXNFLRSHYDS Pro Football Rushing Yards | 513 | 2.0 min | 2.1 min |
| KXNBA1HTOTAL NBA 1st Half Total | 471 | 2.5 min | 2.6 min |
| KXEBASKETBALLGAME eBasketball Game | 462 | 4.0 min | 4.1 min |
| KXNFLTD Pro Football Touchdowns | 462 | 2.0 min | 2.1 min |

## Participant fingerprint (per sport; 60 s snapshots)

change% = share of scan cycles (60 s) where the best quote moved; react = median minutes from a score change to the next quote move (humans: slow, bursty, round sizes; bots: constant cadence, odd/constant sizes, instant reaction)

| venue | sport | markets | snapshots | two-sided | med spread | change% | react (min) | round sizes | med size |
|---|---|---|---|---|---|---|---|---|---|
| pm | soccer | 1182 | 165900 | 86% | 0.020 | 18% | 0.6 (n=2456) | - | - |
| pm | tennis | 1956 | 131324 | 91% | 0.010 | 24% | 0.5 (n=62403) | - | - |
| pm | esports | 3128 | 74550 | 76% | 0.030 | 19% | 0.5 (n=15210) | - | - |
| pm | basketball | 917 | 61199 | 80% | 0.030 | 21% | 0.5 (n=9130) | - | - |
| pm | table-tennis | 1468 | 49014 | 95% | 0.030 | 31% | 0.5 (n=22929) | - | - |
| pm | climate | 215 | 11194 | 79% | 0.050 | 27% | - (n=0) | - | - |
| pm | football | 93 | 10923 | 87% | 0.005 | 16% | 1.1 (n=532) | - | - |
| pm | motorsports | 159 | 8084 | 39% | 0.040 | 16% | - (n=0) | - | - |
| pm | ice-hockey | 60 | 3775 | 83% | 0.050 | 13% | 0.7 (n=197) | - | - |
| pm | misc | 47 | 2952 | 92% | 0.010 | 14% | - (n=0) | - | - |
| pm | beach-volleyball | 57 | 2522 | 82% | 0.010 | 23% | 0.5 (n=1263) | - | - |
| pm | cricket | 6 | 899 | 91% | 0.010 | 17% | 1.0 (n=91) | - | - |
| pm | macro | 78 | 794 | 31% | 0.310 | 17% | - (n=0) | - | - |
| pm | pickleball | 147 | 667 | 3% | 0.180 | 1% | - (n=0) | - | - |
| pm | technology | 24 | 482 | 57% | 0.120 | 30% | - (n=0) | - | - |
| pm | mma | 12 | 345 | 96% | 0.010 | 28% | - (n=0) | - | - |
| pm | baseball | 2 | 305 | 93% | 0.050 | 15% | 1.0 (n=12) | - | - |
| pm | darts | 6 | 64 | 62% | 0.090 | 16% | 0.5 (n=11) | - | - |
| pm | rugby | 4 | 22 | 32% | 0.450 | 4% | - (n=0) | - | - |
| pm | boxing | 3 | 20 | 75% | 0.020 | 57% | - (n=0) | - | - |
| k | KXNCAAFGAME College Football Game | 674 | 502934 | 98% | 0.100 | 2% | - | 8% | 14 |
| k | KXNFLPASSYDSPRECISE Pass Yards Precise | 15652 | 200288 | 0% | 0.390 | 0% | - | 0% | 1 |
| k | KXNBA3PT NBA Player Threes | 1484 | 133744 | 75% | 0.130 | 14% | - | 31% | 40 |
| k | KXNFLGAME NFL Game | 84 | 114567 | 99% | 0.010 | 3% | - | 3% | 74528 |
| k | KXCS2MAP Counter-Strike 2 Map Win | 530 | 79427 | 91% | 0.540 | 4% | - | 19% | 100 |
| k | KXNBAAST NBA Player Assists | 1121 | 77109 | 76% | 0.140 | 13% | - | 29% | 32 |
| k | KXNBAPTS NBA Player Points | 1310 | 68525 | 74% | 0.120 | 18% | - | 24% | 30 |
| k | KXNCAAMBTOTAL Men's College Basketball | 2789 | 65730 | 61% | 0.100 | 5% | - | 28% | 74 |
| k | KXNBAREB NBA Player Rebounds | 1452 | 58726 | 68% | 0.150 | 19% | - | 28% | 30 |
| k | KXESOCCERGAME eSoccer Game | 3939 | 57747 | 18% | 0.610 | 5% | - | 30% | 27 |
| k | KXNBA3PTPROT NBA Player Threes Protec | 1445 | 54348 | 21% | 0.220 | 2% | - | 27% | 162 |
| k | KXNCAAMBSPREAD Men's College Basketball | 2250 | 51905 | 61% | 0.080 | 5% | - | 31% | 50 |
| k | KXATPCHALLENGERMATCH Challenger ATP  | 408 | 42656 | 91% | 0.010 | 8% | - | 5% | 916 |
| k | KXNCAAWBTOTAL Women's College Basketba | 1448 | 40583 | 26% | 0.540 | 2% | - | 12% | 41 |
| k | KXNCAAFSPREAD College Football Spread | 2121 | 37217 | 43% | 0.140 | 7% | - | 11% | 35 |
| k | KXNCAAWBSPREAD Women's College Basketba | 1124 | 35396 | 24% | 0.580 | 3% | - | 18% | 41 |
| k | KXUCLSCORE Correct Score | 594 | 33497 | 71% | 0.010 | 3% | - | 17% | 3053 |
| k | KXNBAASTPROT NBA Player Assists Prote | 1080 | 33489 | 18% | 0.150 | 2% | - | 21% | 162 |
| k | KXNBA1HSPREAD NBA 1st Half Spread | 494 | 33430 | 69% | 0.050 | 16% | - | 19% | 150 |
| k | KXNBA2HSPREAD NBA 2nd Half Spread | 494 | 33205 | 71% | 0.280 | 28% | - | 41% | 119 |
| k | KXNBA1HTOTAL NBA 1st Half Total | 494 | 33081 | 67% | 0.060 | 16% | - | 29% | 100 |
| k | KXNBA1HTEAMTOTAL NBA 1st Half Team Total | 572 | 32527 | 55% | 0.330 | 14% | - | 32% | 253 |
| k | KXNBA2HTOTAL NBA 2nd Half Total | 494 | 31521 | 71% | 0.380 | 24% | - | 33% | 83 |
| k | KXMLSSCORE Correct Score | 408 | 29432 | 54% | 0.020 | 3% | - | 14% | 1186 |
| k | KXNBAPTSPROT NBA Player Points Protec | 1210 | 28270 | 19% | 0.230 | 3% | - | 16% | 162 |
| k | KXNBAPRA NBA Player Points + Rebo | 778 | 27287 | 60% | 0.420 | 18% | - | 13% | 5 |
| k | KXNBAREBPROT NBA Player Rebounds Prot | 1399 | 26196 | 14% | 0.170 | 4% | - | 25% | 200 |
| k | KXNCAAWBGAME Women's College Basketba | 534 | 25708 | 83% | 0.150 | 5% | - | 14% | 13 |
| k | KXAFCCLSCORE Correct Score | 424 | 25660 | 39% | 0.020 | 2% | - | 15% | 453 |
| k | KXNCAAF1H College Football 1st Hal | 987 | 25048 | 88% | 0.840 | 1% | - | 25% | 133 |
| k | KXWTASETWINNER WTA Set Winner | 218 | 24792 | 80% | 0.040 | 4% | - | 23% | 45 |
| k | KXNFLTOTALPRECISE Total Precise | 1976 | 24775 | 4% | 0.060 | 2% | - | 21% | 2 |
| k | KXNCAAFTOTAL College Football Total P | 1540 | 23593 | 35% | 0.170 | 6% | - | 10% | 89 |
| k | KXNBA3QSPREAD NBA 3rd Quarter Spread | 338 | 22805 | 74% | 0.060 | 24% | - | 54% | 100 |
| k | KXNFLRECYDSPROT Receiving Yards Protecte | 1638 | 21248 | 11% | 0.740 | 5% | - | 15% | 19 |
| k | KXNBA3QTOTAL NBA 3rd Quarter Total | 338 | 21063 | 71% | 0.070 | 23% | - | 43% | 100 |
| k | KXNBA2QSPREAD NBA 2nd Quarter Spread | 338 | 20831 | 67% | 0.060 | 19% | - | 21% | 168 |
| k | KXNFLRECYDS Pro Football Receiving Y | 1739 | 19832 | 0% | - | 0% | - | 0% | - |
| k | KXATPSETWINNER ATP Set Winner | 204 | 19236 | 92% | 0.040 | 4% | - | 11% | 54 |
| k | KXNEXTTEAMNHL Next Team NHL | 230 | 18860 | 0% | 0.130 | 0% | - | 23% | 341 |

## Schema notes (raw keys seen)

- polymarket: active, archived, category, chatChannel, closed, combos, createdAt, description, elapsed, endDate, ended, eventState, fixtureId, hidden, id, insiderTradingRules, live, marketCounts, marketGroups, markets, metadata, participants, payoutEstimateMessage, payoutEstimateTime, period, primaryTag, score, seriesSlug, slug, sortType, sportradarGameId, startDate, startTime, streamProvider, streamRequiresAuth, tags, teams, ticker, title, updatedAt
- kalshi: can_close_early, close_time, created_time, early_close_condition, event_ticker, exchange_index, expected_expiration_time, expiration_time, expiration_value, floor_strike, last_price_dollars, latest_expiration_time, market_type, no_ask_dollars, no_bid_dollars, no_sub_title, notional_value_dollars, occurrence_datetime, open_interest_fp, open_time, previous_price_dollars, previous_yes_ask_dollars, previous_yes_bid_dollars, price_level_structure, price_ranges, result, rules_primary, rules_secondary, settlement_bounds_type, settlement_timer_seconds, settlement_value_dollars, status, strike_type, ticker, title, updated_time, volume_24h_fp, volume_fp, yes_ask_dollars, yes_ask_size_fp, yes_bid_dollars, yes_bid_size_fp, yes_sub_title

