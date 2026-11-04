# Mr. P — sports radar

Updated 2026-11-04T02:55:24Z by `run-20261103T2348-41740895463` (last 7 days). Read-only scanner of every sports market on Polymarket US and Kalshi — it never places orders.
Kit: `mrp/mrp_sports_radar.py` on the `mrp` branch. Raw tape: `mrp/radar/<run>/`.

# Sports radar report

records 3,956,849 | 2026-11-01 02:57Z → 02:53Z | runs 29 | pairs matched 1536 | errors {'sp.k.series_poll:KXATPEXACTMATCH': 10, 'sp.k.series_poll:KXATPMATCH': 10, 'sp.k.series_poll:KXATPSETWINNER': 10, 'sp.k.series_poll:KXAUTBUNDESTOTAL': 4, 'sp.k.series_poll:KXEFLL11H': 6, 'sp.k.series_poll:KXEFLL11HSPREAD': 10, 'sp.k.series_poll:KXHNLTOTAL': 6, 'sp.k.series_poll:KXLALIGABTTS': 9, 'sp.k.series_poll:KXLALIGASCORE': 6, 'sp.k.series_poll:KXLALIGASPREAD': 8, 'sp.k.always:KXNFLGAME': 7, 'sp.k.series_poll:KXATPCHALLENGERMATCH': 7, 'sp.k.series_poll:KXEFLL11HBTTS': 10, 'sp.k.series_poll:KXLALIGA2H': 6, 'sp.k.series_poll:KXCS2MAP': 6, 'sp.k.series_poll:KXEFLL11HTOTAL': 8, 'sp.k.series_poll:KXLALIGA2HBTTS': 8, 'sp.k.series_poll:KXLALIGA2HSPREAD': 6, 'sp.k.series_poll:KXLALIGA2HTOTAL': 4, 'sp.k.series_poll:KXLALIGACORNERS': 8, 'sp.k.series_poll:KXLALIGAGAME': 6, 'sp.k.series_poll:KXLALIGAGOAL': 6, 'radar': 6, 'sp.k.series_poll:KXAUTBUNDESGAME': 2, 'sp.k.series_poll:KXCZEFLTOTAL': 7, 'sp.k.series_poll:KXELITESERIENTOTAL': 2, 'sp.k.series_poll:KXEREDIVISIETOTAL': 2, 'sp.k.always:KXNCAAFGAME': 7, 'sp.k.series_poll:KXLIGUE11HBTTS': 3, 'sp.k.series_poll:KXLIGUE11HSCORE': 4, 'sp.k.series_poll:KXLIGUE11H': 4, 'sp.k.series_poll:KXLIGUE11HSPREAD': 1, 'sp.stream': 48}

## Catalogue (latest inventory, 02:52Z)

Polymarket US sports events 4591 of 5945 active events; Kalshi near-term sports markets 9650 in 1729 events; calls so far {'pm': 1669, 'k': 19319}; MB {'pm': 3935547055, 'k': 8086724438}

| venue | sport / league / type | markets | two-sided | med spread | vol 24h |
|---|---|---|---|---|---|
| pm | football / nfl / futures | 3753 | 67% | 0.010 | 0 |
| pm | football / cfb / futures | 1645 | 54% | 0.010 | 0 |
| k | KXNCAAFTEAMTOTAL / College Football Team Total Points | 1436 | 100% | 0.040 | 317510 |
| pm | basketball / nba / futures | 1380 | 64% | 0.010 | 0 |
| k | KXNCAAF1HSPREAD / College Football 1st Half Spread | 1269 | 100% | 0.170 | 1441 |
| k | KXNCAAF1HTOTAL / College Football 1st Half Total | 840 | 100% | 0.240 | 3631 |
| pm | ice-hockey / nhl / futures | 779 | 93% | 0.010 | 0 |
| k | KXNCAAF1H / College Football 1st Half Winner | 762 | 100% | 0.890 | 3919 |
| pm | basketball / wcbb / basketball_team_full_game_winner | 599 | 28% | 0.405 | 0 |
| pm | basketball / cbb / basketball_team_full_game_winner | 583 | 28% | 0.120 | 0 |
| k | KXNHLGOAL / NHL Goalscorer | 563 | 100% | 0.010 | 688620 |
| k | KXNCAAFGAME / College Football Game | 512 | 100% | 0.080 | 11561908 |
| pm | golf / worlwide / futures | 493 | 36% | 0.006 | 0 |
| pm | golf / lpga / futures | 440 | 0% | - | 0 |
| pm | soccer / epl / futures | 437 | 84% | 0.010 | 0 |
| pm | golf / abudhabc / futures | 352 | 34% | 0.011 | 0 |
| k | KXNHLAST / Pro Hockey Assists | 343 | 100% | 0.110 | 129746 |
| k | KXNCAAMBGAME / Men's College Basketball Game | 332 | 100% | 0.030 | 2392208 |
| k | KXNCAAWBGAME / Women's College Basketball Game | 332 | 100% | 0.205 | 451477 |
| pm | basketball / cbb / futures | 317 | 85% | 0.010 | 0 |
| k | KXITFWMATCH / ITF Women's Match | 314 | 100% | 0.030 | 1152471 |
| pm | soccer / ucl / futures | 285 | 75% | 0.010 | 0 |
| k | KXNCAAMBTOTAL / Men's College Basketball Total Points | 261 | 100% | 0.040 | 1136554 |
| k | KXNCAAWBTOTAL / Women's College Basketball Total Points | 238 | 100% | 0.970 | 13413 |
| pm | football / cfb / football_team_full_game_winner | 236 | 89% | 0.050 | 0 |
| pm | table-tennis / setkameua / table_tennis_match_winner | 235 | 75% | 0.170 | 0 |
| k | KXNCAAMBSPREAD / Men's College Basketball Spread | 225 | 100% | 0.040 | 1610382 |
| pm | tennis / itfme / tennis_match_winner | 216 | 75% | 0.030 | 0 |
| pm | tennis / itfwo / tennis_match_winner | 198 | 80% | 0.030 | 0 |
| pm | tennis / utr / tennis_match_winner | 168 | 26% | 0.370 | 0 |
| pm | macro /  / futures | 150 | 79% | 0.010 | 0 |
| k | KXNCAAWBSPREAD / Women's College Basketball Spread | 150 | 100% | 0.990 | 4497 |
| pm | soccer / lal / futures | 147 | 65% | 0.010 | 0 |
| pm | mma / ufc / futures | 145 | 83% | 0.010 | 0 |
| pm | boxing / boxing / futures | 145 | 0% | - | 0 |
| pm | table-tennis / wtt / table_tennis_match_winner | 144 | 55% | 0.390 | 0 |
| pm | motorsports / f1 / futures | 123 | 15% | 0.001 | 0 |
| pm | basketball / nba / basketball_team_full_game_winner | 103 | 73% | 0.200 | 0 |
| k | KXNHLGAME / NHL Game | 100 | 100% | 0.040 | 3272636 |
| pm | tennis / atp / futures | 95 | 37% | 0.010 | 0 |
| pm | soccer / sea / futures | 88 | 77% | 0.010 | 0 |
| pm | macro / usgas / futures | 87 | 22% | 0.450 | 0 |
| k | KXNHL3PTOTAL / 3rd Period Total | 86 | 100% | 0.130 | 21587 |
| pm | soccer / bun / futures | 80 | 82% | 0.010 | 0 |
| pm | soccer / lg1 / futures | 79 | 81% | 0.010 | 0 |
| k | KXNCAAMB1H / Men's College Basketball 1st Half Winner | 78 | 100% | 0.990 | 1015 |
| pm | tennis / wta / futures | 75 | 44% | 0.010 | 0 |
| pm | esports / cs2 / esports_match_winner | 73 | 58% | 0.100 | 0 |
| pm | baseball / mlb / futures | 72 | 72% | 0.001 | 0 |
| k | KXNHL3P / NHL 3rd Period Winner | 72 | 100% | 0.285 | 30982 |
| pm | tennis / atp / tennis_match_winner | 64 | 91% | 0.010 | 0 |
| pm | macro / usdsl / futures | 63 | 0% | - | 0 |
| pm | motorsports / nascar / futures | 62 | 27% | 0.020 | 0 |
| k | KXNFLGAME / NFL Game | 58 | 100% | 0.010 | 1834386 |
| pm | table-tennis / czechligapro / table_tennis_match_winner | 57 | 14% | 0.465 | 0 |
| k | KXNHL3PSPREAD / NHL 3rd Period Spread | 57 | 100% | 0.210 | 6448 |
| pm | soccer / uecl / soccer_team_full_time_winner | 55 | 98% | 0.020 | 0 |
| pm | soccer / uel / soccer_team_full_time_winner | 54 | 100% | 0.010 | 0 |
| pm | golf / masttour / futures | 52 | 100% | 0.499 | 0 |
| pm | soccer / mls / futures | 51 | 92% | 0.010 | 0 |

## Opportunities

| kind | distinct | hits | max margin $/contract | max persistence | fresh-BBO still open |
|---|---|---|---|---|---|
| decided_k | 157 | 4746 | 0.9893 | 169 min | 0/0 |
| decided_pm | 18 | 259 | 0.9893 | 7 min | 144/259 |
| decided_pm_closed | 12 | 196 | 0.9893 | 14 min | 0/196 |
| dutch_k | 13 | 84 | 0.0429 | 24 min | 0/0 |
| dutch_pm | 48 | 2851 | 0.4629 | 50 min | 0/0 |
| implication_k | 40 | 2074 | 0.7040 | 101 min | 0/0 |
| lag_k_settled | 164 | 25465 | 0.9973 | 294 min | 23784/25416 |
| lag_k_settled_closed | 141 | 1952 | 0.9973 | 95 min | 0/1952 |

Top by persistence × hits:

- **lag_k_settled** basketball — Charleston Southern vs. South Florida — bid 0.01 ask 0.02 sell_yes @ 0.01 | margin 0.0373 | 294 min, 593 hits | fresh bbo 0.01/0.02 depth 1/37 | score 52-68 H2
- **lag_k_settled** basketball — Grambling State vs. Northern Illinois — bid 0.25 ask 0.28 sell_yes @ 0.25 | margin 0.2466 | 223 min, 521 hits | fresh bbo 0.24/0.25 depth 7/15 | score - NS
- **decided_k** 🔒 football — NE Patriots vs. MIA Dolphins — buy_yes @ 0.77 | margin 0.2756 | 169 min, 418 hits | score 24-19 Q4
- **decided_k** 🔒 football — NE Patriots vs. MIA Dolphins — buy_yes @ 0.92 | margin 0.1031 | 169 min, 418 hits | score 24-19 Q4
- **decided_k** 🔒 football — NE Patriots vs. MIA Dolphins — buy_yes @ 0.99 | margin 0.0280 | 169 min, 418 hits | score 24-19 Q4
- **decided_k** 🔒 football — NE Patriots vs. MIA Dolphins — buy_yes @ 0.77 | margin 0.2659 | 111 min, 441 hits | score 24-13 Q4
- **lag_k_settled** basketball — Western Michigan vs. Old Dominion — bid 0.51 ask 0.53 sell_yes @ 0.51 | margin 0.5027 | 111 min, 423 hits | fresh bbo 0.51/0.53 depth 46/44 | score - NS
- **decided_k** soccer — New England Revolution vs. Inter Miami CF — buy_yes @ 0.23 | margin 0.7576 | 126 min, 397 hits | score 2-2 90'
- **decided_k** football — NE Patriots vs. MIA Dolphins — buy_yes @ 0.2 | margin 0.8201 | 126 min, 390 hits | score 24-19 Q4
- **decided_k** football — NE Patriots vs. MIA Dolphins — buy_yes @ 0.36 | margin 0.6750 | 126 min, 390 hits | score 24-19 Q4
- **implication_k** 🔒  — 26NOV01NEMIA — | margin 0.6541 | 101 min, 395 hits | score - 
- **lag_k_settled** tennis — Nagy - Zelnickova vs. Daems - Tian — bid 0.57 ask 0.78 sell_yes @ 0.57 | margin 0.5530 | 120 min, 360 hits | fresh bbo 0.57/0.78 depth 4/5 | score 0-0 
- **lag_k_settled** esports — Glitchtech Esports vs. BOJONG — bid - ask 0.01 buy_yes @ 0.01 | margin 0.9893 | 94 min, 373 hits | fresh bbo -/0.01 depth 0/27 | score 0-0 Map 1
- **lag_k_settled** basketball — Villanova (W) vs. Notre Dame (W) — bid 0.01 ask 0.02 sell_yes @ 0.01 | margin 0.2563 | 92 min, 364 hits | fresh bbo -/0.02 depth 0/36 | score 45-65 H2
- **lag_k_settled** tennis — Luis Felipe Miguel vs. Igor Marcondes — bid 0.01 ask 0.02 sell_yes @ 0.01 | margin 0.4130 | 67 min, 389 hits | fresh bbo 0.01/0.02 depth 1/42 | score 5-7, 3-5:0-0 S2
- **lag_k_settled** tennis — Aytekin - Tan vs. Januchowski - Sotikovs — bid 0.30 ask 0.50 buy_yes @ 0.5 | margin 0.4826 | 90 min, 359 hits | fresh bbo 0.06/0.95 depth 4/3 | score 0-0 
- **lag_k_settled** tennis — Burdet - Senn vs. Herck - Wygona — bid 0.46 ask 0.55 sell_yes @ 0.46 | margin 0.5027 | 120 min, 320 hits | fresh bbo 0.42/0.50 depth 6/13 | score 3-3:30-40 S1
- **lag_k_settled** soccer — New England Revolution vs. Inter Miami CF — bid 0.17 ask 0.18 buy_yes @ 0.18 | margin 0.8097 | 70 min, 310 hits | fresh bbo 0.17/0.18 depth 12/37 | score 1-1 2H
- **lag_k_settled** soccer — New England Revolution vs. Inter Miami CF — bid 0.54 ask 0.55 sell_yes @ 0.54 | margin 0.5227 | 70 min, 310 hits | fresh bbo 0.53/0.54 depth 25/42 | score 1-1 2H
- **lag_k_settled** soccer — New England Revolution vs. Inter Miami CF — bid 0.28 ask 0.29 sell_yes @ 0.28 | margin 0.4328 | 70 min, 310 hits | fresh bbo 0.28/0.29 depth 17/44 | score 1-1 2H
- **lag_k_settled** soccer — Portland Timbers vs. Houston Dynamo — bid 0.55 ask 0.56 buy_yes @ 0.56 | margin 0.4229 | 75 min, 300 hits | fresh bbo 0.55/0.56 depth 19/26 | score 0-0 
- **lag_k_settled** soccer — Portland Timbers vs. Houston Dynamo — bid 0.23 ask 0.24 sell_yes @ 0.23 | margin 0.2177 | 75 min, 300 hits | fresh bbo 0.23/0.24 depth 12/26 | score 0-0 
- **lag_k_settled** soccer — Portland Timbers vs. Houston Dynamo — bid 0.21 ask 0.22 sell_yes @ 0.21 | margin 0.1985 | 75 min, 300 hits | fresh bbo 0.21/0.22 depth 13/20 | score 0-0 
- **lag_k_settled** basketball — Eastern Michigan vs. Coastal Carolina — bid 0.99 ask - sell_yes @ 0.99 | margin 0.9893 | 75 min, 297 hits | fresh bbo 0.99/- depth 14/0 | score 71-70 FT
- **implication_k** 🔒  — 26NOV01NEMIA — | margin 0.4518 | 45 min, 301 hits | score - 

## Live paper trades (no orders; Kalshi prices, taker fees)

Ledger L2-2026-11-01 (earlier ledgers excluded: none)

**Total closed P&L: $-110.23 on $625.23 staked (-17.6%)**

| rule | entries | closed | winners | staked | P&L | ROI |
|---|---|---|---|---|---|---|
| R1 anchor [ncaaf] | 3 | 2 | 1 | $20.55 | $+7.45 | +36% |
| R1 anchor [nfl] | 6 | 6 | 1 | $61.25 | $-42.25 | -69% |
| R2 q1cheap [ncaaf] | 2 | 0 | 0 | $0.00 | $+0.00 | +0% |
| R2 q1cheap [nfl] | 6 | 6 | 1 | $31.46 | $-2.46 | -8% |
| R3 blowout [ncaaf] | 2 | 2 | 0 | $42.54 | $-42.54 | -100% |
| R6 decided [other] | 28 | 28 | 22 | $469.42 | $-30.42 | -6% |

| time (UTC) | rule | game | team | entry | contracts | why | result |
|---|---|---|---|---|---|---|---|
| 02:05 | R1 anchor | Ohio vs. Akron | Akron | 0.40 | 25 | pregame dog (mid 0.20) leads 7-9 in Q3, ask 0.40 | open |
| 01:36 | R2 q1cheap | Buffalo vs. Miami (OH) | Buffalo | 0.20 | 25 | Q1 ask 0.20, score 3-7 | open |
| 00:12 | R2 q1cheap | Ohio vs. Akron | Akron | 0.19 | 26 | Q1 ask 0.19, score 0-0 | open |
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

### Score reaction speed (live, 15 s): share of the 3-minute move done by +15 s / +30 s / +60 s

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
- 26NOV03OHIOAKR 14-15: -0% / -0% / -0%
- 26NOV03OHIOAKR 14-15: 14% / 14% / 14%

## Bot latency map: how long a decided Kalshi market stays mispriced

| sport | series | markets | already priced | mispriced then fixed | median s mispriced | closed/timeout | contradictions | cheapest ask (size) | resting @0.97 contracts / $ | settled right / wrong |
|---|---|---|---|---|---|---|---|---|---|---|
| basketball | KXNCAAWBTOTAL | 318 | 310 | 8 | 360 | 0 | 0 | 0.01 (1600) | 298 / $8.94 | 290 / 6 |
| basketball | KXNCAAMBTOTAL | 304 | 298 | 1 | 1 | 5 | 0 | 0.75 (120) | 0 / $0.00 | 275 / 0 |
| basketball | KXNCAAMBSPREAD | 200 | 193 | 0 | - | 7 | 0 | 0.62 (20) | 0 / $0.00 | 200 / 0 |
| basketball | KXNCAAWBSPREAD | 167 | 167 | 0 | - | 0 | 0 | - | 0 / $0.00 | 167 / 0 |
| tennis | KXATPCHALLENGERMATCH | 60 | 21 | 39 | 0 | 0 | 0 | 0.97 (53) | 0 / $0.00 | 54 / 0 |
| soccer | KXUCLTOTAL | 59 | 56 | 3 | 6 | 0 | 0 | 0.79 (112) | 1079 / $32.37 | 59 / 0 |
| tennis | KXWTASETWINNER | 58 | 30 | 28 | 1 | 0 | 0 | - | 0 / $0.00 | 56 / 0 |
| soccer | KXAFCCLTOTAL | 58 | 55 | 3 | 2 | 0 | 0 | 0.31 (28) | 24398 / $731.93 | 58 / 0 |
| soccer | KXJ2LEAGUETOTAL | 55 | 55 | 0 | - | 0 | 0 | - | 0 / $0.00 | 51 / 0 |
| tennis | KXATPSETWINNER | 48 | 10 | 38 | 0 | 0 | 0 | - | 0 / $0.00 | 44 / 0 |
| basketball | KXNCAAWBGAME | 42 | 42 | 0 | - | 0 | 0 | - | 0 / $0.00 | 42 / 0 |
| soccer | KXALLSVENSKANTOTAL | 38 | 12 | 26 | 1 | 0 | 0 | - | 0 / $0.00 | 38 / 0 |
| soccer | KXMLSTOTAL | 38 | 0 | 36 | 0 | 2 | 0 | 0.82 (29) | 188 / $5.63 | 36 / 0 |
| soccer | KXJ2LEAGUESPREAD | 35 | 35 | 0 | - | 0 | 0 | - | 0 / $0.00 | 35 / 0 |
| basketball | KXNBASPREAD | 33 | 33 | 0 | - | 0 | 0 | - | 0 / $0.00 | 33 / 0 |
| basketball | KXNCAAMBGAME | 32 | 32 | 0 | - | 0 | 0 | - | 0 / $0.00 | 32 / 0 |
| soccer | KXUCLSPREAD | 31 | 21 | 7 | 1 | 0 | 3 | 0.60 (1000) | 0 / $0.00 | 31 / 0 |
| soccer | KXEREDIVISIETOTAL | 30 | 0 | 30 | 0 | 0 | 0 | - | 0 / $0.00 | 26 / 0 |
| ice-hockey | KXNHLTOTAL | 28 | 28 | 0 | - | 0 | 0 | - | 0 / $0.00 | 18 / 0 |
| soccer | KXELITESERIENTOTAL | 26 | 0 | 26 | 0 | 0 | 0 | - | 0 / $0.00 | 22 / 0 |
| soccer | KXLIGAFTOTAL | 25 | 5 | 20 | 1 | 0 | 0 | 0.98 (87) | 0 / $0.00 | 25 / 0 |
| soccer | KXSERIECTOTAL | 24 | 4 | 20 | 1 | 0 | 0 | 0.97 (3) | 0 / $0.00 | 24 / 0 |
| soccer | KXECULPTOTAL | 24 | 13 | 11 | 0 | 0 | 0 | 0.93 (23) | 0 / $0.00 | 24 / 0 |
| football | KXNFLGAME | 24 | 2 | 22 | 1 | 0 | 0 | 0.02 (0) | 0 / $0.00 | 21 / 0 |
| soccer | KXJ2LEAGUEGAME | 24 | 24 | 0 | - | 0 | 0 | - | 0 / $0.00 | 24 / 0 |
| basketball | KXFIBACHAMPTOTAL | 23 | 22 | 1 | 2 | 0 | 0 | 0.78 (4) | 0 / $0.00 | 23 / 0 |
| soccer | KXDENSUPERLIGATOTAL | 22 | 0 | 22 | 0 | 0 | 0 | - | 0 / $0.00 | 22 / 0 |
| soccer | KXBELGIANPLTOTAL | 22 | 0 | 22 | 1 | 0 | 0 | 0.89 (454) | 763 / $22.89 | 22 / 0 |
| soccer | KXIDNSLTOTAL | 21 | 0 | 21 | 1 | 0 | 0 | 0.96 (62) | 0 / $0.00 | 21 / 0 |
| soccer | KXUCL1HTOTAL | 21 | 21 | 0 | - | 0 | 0 | - | 0 / $0.00 | 21 / 0 |
| soccer | KXBUNDESLIGA2TOTAL | 19 | 0 | 19 | 2 | 0 | 0 | - | 0 / $0.00 | 19 / 0 |
| soccer | KXAUTBUNDESTOTAL | 19 | 0 | 19 | 1 | 0 | 0 | - | 0 / $0.00 | 13 / 1 |
| soccer | KXEKSTRAKLASATOTAL | 18 | 18 | 0 | - | 0 | 0 | - | 0 / $0.00 | 18 / 0 |
| soccer | KXEFLCHAMPIONSHIP1HTOTAL | 18 | 18 | 0 | - | 0 | 0 | - | 0 / $0.00 | 18 / 0 |
| soccer | KXUCLGAME | 16 | 8 | 5 | 1 | 0 | 3 | 0.69 (44525) | 0 / $0.00 | 16 / 0 |
| soccer | KXBRASILEIROBTOTAL | 15 | 6 | 9 | 0 | 0 | 0 | - | 0 / $0.00 | 14 / 0 |
| soccer | KXLIGUE2TOTAL | 15 | 15 | 0 | - | 0 | 0 | - | 0 / $0.00 | 15 / 0 |
| soccer | KXAFCCLSPREAD | 15 | 15 | 0 | - | 0 | 0 | - | 0 / $0.00 | 15 / 0 |
| football | KXNFLTOTALPRECISE | 14 | 0 | 14 | 1 | 0 | 0 | - | 0 / $0.00 | 0 / 0 |
| soccer | KXHUNNB1TOTAL | 12 | 0 | 12 | 1 | 0 | 0 | - | 0 / $0.00 | 12 / 0 |
| soccer | KXMLS1HTOTAL | 12 | 0 | 9 | 0 | 3 | 0 | 0.61 (1157) | 0 / $0.00 | 12 / 0 |
| soccer | KXARGPREMDIVTOTAL | 12 | 10 | 2 | 1 | 0 | 0 | - | 0 / $0.00 | 12 / 0 |
| soccer | KXARGNACBTOTAL | 12 | 11 | 1 | 1 | 0 | 0 | - | 0 / $0.00 | 12 / 0 |
| soccer | KXAPFDDHTOTAL | 11 | 6 | 5 | 0 | 0 | 0 | - | 0 / $0.00 | 11 / 0 |
| soccer | KXDIMAYORTOTAL | 11 | 4 | 7 | 0 | 0 | 0 | - | 0 / $0.00 | 11 / 0 |
| soccer | KXALLSVENSKANSPREAD | 10 | 5 | 5 | 0 | 0 | 0 | - | 0 / $0.00 | 10 / 0 |
| soccer | KXPERLIGA1TOTAL | 10 | 10 | 0 | - | 0 | 0 | - | 0 / $0.00 | 10 / 0 |
| tennis | KXATPEXACTMATCH | 9 | 0 | 9 | 1 | 0 | 0 | - | 0 / $0.00 | 9 / 0 |
| soccer | KXEFLCHAMPIONSHIPTOTAL | 9 | 9 | 0 | - | 0 | 0 | - | 0 / $0.00 | 9 / 0 |
| soccer | KXTHAIL1TOTAL | 8 | 0 | 8 | 1 | 0 | 0 | 0.96 (13) | 0 / $0.00 | 8 / 0 |
| soccer | KXBUNDESLIGA2SPREAD | 8 | 0 | 8 | 2 | 0 | 0 | - | 0 / $0.00 | 8 / 0 |
| soccer | KXMLS1H | 8 | 0 | 6 | 0 | 2 | 0 | 0.63 (492) | 0 / $0.00 | 8 / 0 |
| soccer | KXJ2LEAGUEBTTS | 8 | 8 | 0 | - | 0 | 0 | - | 0 / $0.00 | 8 / 0 |
| soccer | KXKLEAGUETOTAL | 7 | 0 | 7 | 1 | 0 | 0 | - | 0 / $0.00 | 7 / 0 |
| soccer | KXHNLTOTAL | 7 | 0 | 7 | 0 | 0 | 0 | - | 0 / $0.00 | 7 / 0 |
| soccer | KXUCL1HBTTS | 7 | 7 | 0 | - | 0 | 0 | - | 0 / $0.00 | 7 / 0 |
| tennis | KXATPMATCH | 6 | 0 | 6 | 1 | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| soccer | KXCZEFNLTOTAL | 6 | 0 | 6 | 0 | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| soccer | KXSLGREECETOTAL | 6 | 5 | 1 | 0 | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| soccer | KXEFLCHAMPIONSHIP1H | 6 | 6 | 0 | - | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| soccer | KXUCLBTTS | 6 | 6 | 0 | - | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| soccer | KXMYSLTOTAL | 5 | 0 | 5 | 0 | 0 | 0 | - | 0 / $0.00 | 5 / 0 |
| soccer | KXLALIGA2TOTAL | 5 | 3 | 2 | 0 | 0 | 0 | - | 0 / $0.00 | 5 / 0 |
| soccer | KXLIGAPORTUGALTOTAL | 5 | 0 | 5 | 0 | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXMLSSPREAD | 5 | 0 | 5 | 1 | 0 | 0 | - | 0 / $0.00 | 5 / 0 |
| soccer | KXEKSTRAKLASASPREAD | 5 | 5 | 0 | - | 0 | 0 | - | 0 / $0.00 | 5 / 0 |
| soccer | KXARGNACBSPREAD | 5 | 5 | 0 | - | 0 | 0 | - | 0 / $0.00 | 5 / 0 |
| soccer | KXSERIECSPREAD | 4 | 0 | 4 | 0 | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
| soccer | KXCZEFLTOTAL | 4 | 0 | 4 | 1 | 0 | 0 | 0.47 (1945) | 76 / $2.29 | 2 / 0 |
| soccer | KXMLS1HBTTS | 4 | 0 | 3 | 0 | 1 | 0 | 0.78 (68) | 0 / $0.00 | 4 / 0 |
| soccer | KXLIGUE1SPREAD | 4 | 4 | 0 | - | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
| soccer | KXECULPSPREAD | 4 | 4 | 0 | - | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
| soccer | KXBRASILEIROTOTAL | 4 | 4 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXTFF1LIGTOTAL | 3 | 0 | 3 | 1 | 0 | 0 | 0.97 (5) | 0 / $0.00 | 2 / 1 |
| football | KXMLSTOTAL | 3 | 0 | 0 | - | 3 | 0 | 0.71 (2845) | 0 / $0.00 | 3 / 0 |
| soccer | KXMLSGAME | 3 | 0 | 3 | 1 | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXEKSTRAKLASAGAME | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXAFCCLGAME | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXAFCCLBTTS | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXARGNACBGAME | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| basketball | KXLNBPTOTAL | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 0 / 0 |
| soccer | KXUCL1H | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| esports | KXCS2TOTALMAPS | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
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
| basketball | KXNBAGAME | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| tennis | KXWTACHALLENGERMATCH | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| basketball | KXKORISLIIGAGAME | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| basketball | KXEUROCUPGAME | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXEFLCHAMPIONSHIP1HBTTS | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| esports | KXCS2GAME | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| basketball | KXFIBACHAMPGAME | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
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
| soccer | KXEFLCHAMPIONSHIPBTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |

'Already priced' = the book was at 99c+ when we first looked (bots were faster than our score feed). 'Median s mispriced' runs from our decision to the fix. 'Settled right / wrong' checks our certainty against Kalshi's result — any 'wrong' means the score feed or the model failed.

## Decided-state engine (contracts the live score already settled, still trading)

2593 contracts decided while active; 157 had a price leaving > 0.4c after fees; 47 of those were mispriced AFTER the score was stable (lock tier)

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
| basketball | Alcorn State (W) vs. Ole Miss (W | KXNCAAMBTOTAL-26NOV02ALCNMISS-154 | NO | ended total 118 <= 153.5 | 0.237 | 269s | 0.237 | 120 |
| soccer | Portland Timbers vs. Houston Dyn | KXMLS1HTOTAL-26NOV01PORHOU-1 | YES | 1H (1, 0) > 0.5 | 0.227 | 1010s | 0.227 | 2345 |
| soccer | Houston Dash vs. Portland Thorns | KXMLS1HBTTS-26NOV01PORHOU-BTTS | NO | 1H final (0, 1) | 0.208 | 1010s | 0.208 | 4846 |
| soccer | Houston Dash vs. Portland Thorns | KXMLS1H-26NOV01PORHOU-HOU | NO | 1H final (0, 1) | 0.179 | 1010s | 0.179 | 4248 |
| basketball | Alcorn State (W) vs. Ole Miss (W | KXNCAAMBTOTAL-26NOV02ALCNMISS-158 | NO | ended total 118 <= 157.5 | 0.179 | 269s | 0.179 | 158 |
| basketball | Alcorn State (W) vs. Ole Miss (W | KXNCAAMBSPREAD-26NOV02ALCNMISS-MISS23 | YES | ended 38-80 margin 42 vs 22.5 | 0.170 | 269s | 0.170 | 581 |
| basketball | Texas Southern (W) vs. Tulane (W | KXNCAAWBTOTAL-26NOV02TXSOTULN-133 | YES | score 57-137 total 194 > 132.5 | 0.170 | 575s | 0.170 | 11 |
| tennis | Lorenzo Musetti vs. Hubert Hurka | KXATPSETWINNER-26NOV01MUSHUR-2-MUS | YES | set 2 final 7-6 | 0.160 | 44s | 0.160 | 5 |
| soccer | Houston Dash vs. Portland Thorns | KXMLS1HTOTAL-26NOV01PORHOU-3 | NO | 1H final (0, 1) <= 2.5 | 0.141 | 1010s | 0.141 | 144 |
| basketball | Texas Southern (W) vs. Tulane (W | KXNCAAWBTOTAL-26NOV02TXSOTULN-130 | YES | score 57-137 total 194 > 129.5 | 0.141 | 575s | 0.141 | 62 |
| basketball | Alcorn State (W) vs. Ole Miss (W | KXNCAAMBTOTAL-26NOV02ALCNMISS-162 | NO | ended total 118 <= 161.5 | 0.122 | 269s | 0.122 | 500 |
| soccer | New England Revolution vs. Inter | KXMLSTOTAL-26NOV01NEMIA-2 | YES | score 1-2 total 3 > 1.5 | 0.103 | 10189s | 0.103 | 22035 |
| basketball | Texas Southern (W) vs. Tulane (W | KXNCAAWBTOTAL-26NOV02TXSOTULN-140 | YES | score 57-137 total 194 > 139.5 | 0.103 | 575s | 0.103 | 100 |
| basketball | Texas Southern (W) vs. Tulane (W | KXNCAAWBTOTAL-26NOV02TXSOTULN-136 | YES | score 57-137 total 194 > 135.5 | 0.094 | 575s | 0.094 | 25 |
| tennis | Rinky Hijikata vs. Vit Kopriva | KXATPEXACTMATCH-26NOV01HIJKOP-HIJ21 | YES | ended 7-6(7-5), 6-2 | 0.989 | 466s | - | 0 |

## Close / settlement latency (how clunky each venue is after the final whistle)

Kalshi: settlement_ts − close_time per series (negative = settled before the scheduled close)

| series | n | median | p90 |
|---|---|---|---|
| KXNFLPASSYDSPRECISE Pass Yards Precise | 13465 | 4.0 min | 4.1 min |
| KXESOCCERGAME eSoccer Game | 3535 | 4.0 min | 4.1 min |
| KXNCAAMBTOTAL Men's College Basketball Total | 2209 | 4.0 min | 4.1 min |
| KXNCAAMBSPREAD Men's College Basketball Sprea | 1734 | 1.8 min | 1.8 min |
| KXNFLTOTALPRECISE Total Precise | 1400 | 4.0 min | 4.1 min |
| KXNFLRECYDS Pro Football Receiving Yards | 1309 | 2.0 min | 2.1 min |
| KXNFLRECYDSPROT Receiving Yards Protected | 1258 | 6.0 min | 6.1 min |
| KXNBA3PTPROT NBA Player Threes Protected | 1136 | 2.5 min | 2.6 min |
| KXNCAAWBTOTAL Women's College Basketball Tot | 1116 | 2.5 min | 2.6 min |
| KXNBAREB NBA Player Rebounds | 1040 | 2.0 min | 2.1 min |
| KXNBAREBPROT NBA Player Rebounds Protected | 988 | 2.5 min | 2.6 min |
| KXNBA3PT NBA Player Threes | 922 | 2.0 min | 2.1 min |
| KXNFLRECPROT Receptions Protected | 893 | 6.0 min | 6.1 min |
| KXNBAPTS NBA Player Points | 886 | 2.0 min | 2.1 min |
| KXNFLREC Pro Football Player Receptions | 864 | 2.0 min | 2.1 min |
| KXNBAPTSPROT NBA Player Points Protected | 847 | 2.5 min | 2.6 min |
| KXNCAAWBSPREAD Women's College Basketball Spr | 838 | 1.8 min | 1.8 min |
| KXNBAASTPROT NBA Player Assists Protected | 821 | 2.5 min | 2.6 min |
| KXNBATEAMTOTAL NBA Team Total | 788 | 2.5 min | 2.6 min |
| KXNBAAST NBA Player Assists | 705 | 2.0 min | 2.1 min |
| KXNHLGOAL NHL Goalscorer | 700 | 3.0 min | 3.1 min |
| KXLIGAPROMATCH Russia Liga Pro Match | 634 | 4.0 min | 4.1 min |
| KXNBAPRA NBA Player Points + Rebounds + | 625 | 2.5 min | 2.6 min |
| KXNHLPTS Pro Hockey Points | 598 | 3.0 min | 3.1 min |
| KXNBASPREAD NBA Spread | 552 | 1.8 min | 1.8 min |
| KXNFLRSHYDSPROT Rushing Yards Protected | 549 | 6.0 min | 6.1 min |
| KXNFLTDPROT Pro Football Touchdowns Protec | 526 | 6.0 min | 6.1 min |
| KXNFLRSHYDS Pro Football Rushing Yards | 513 | 2.0 min | 2.1 min |
| KXNBATOTAL NBA Total | 492 | 1.8 min | 1.8 min |
| KXNFLTD Pro Football Touchdowns | 462 | 2.0 min | 2.1 min |
| KXEBASKETBALLGAME eBasketball Game | 458 | 4.0 min | 4.1 min |
| KXITFWMATCH ITF Women's Match | 423 | 2.0 min | 2.1 min |
| KXITFMATCH ITF Men's Match | 414 | 2.0 min | 2.1 min |
| KXNCAAFSPREAD College Football Spread | 396 | 4.0 min | 4.1 min |
| KXNHLFIRSTGOAL NHL First Goal | 377 | 6.0 min | 6.0 min |
| KXNBA1HTEAMTOTAL NBA 1st Half Team Total | 375 | 2.5 min | 2.6 min |
| KXUCLGOAL UCL Goalscorer | 371 | 6.0 min | 13.5 min |
| KXAFCCLSCORE Correct Score | 364 | 6.0 min | 6.1 min |
| KXNBASTL NBA Player Steals | 344 | 2.0 min | 2.1 min |
| KXNBA1HTOTAL NBA 1st Half Total | 338 | 2.5 min | 2.6 min |

## Participant fingerprint (per sport; 60 s snapshots)

change% = share of scan cycles (60 s) where the best quote moved; react = median minutes from a score change to the next quote move (humans: slow, bursty, round sizes; bots: constant cadence, odd/constant sizes, instant reaction)

| venue | sport | markets | snapshots | two-sided | med spread | change% | react (min) | round sizes | med size |
|---|---|---|---|---|---|---|---|---|---|
| pm | soccer | 1062 | 160554 | 86% | 0.020 | 18% | 0.6 (n=2298) | - | - |
| pm | tennis | 2156 | 143012 | 92% | 0.010 | 25% | 0.5 (n=68303) | - | - |
| pm | esports | 3097 | 73792 | 76% | 0.030 | 18% | 0.5 (n=14856) | - | - |
| pm | basketball | 832 | 63139 | 80% | 0.030 | 20% | 0.5 (n=9508) | - | - |
| pm | table-tennis | 1550 | 49248 | 95% | 0.030 | 32% | 0.5 (n=23003) | - | - |
| pm | climate | 215 | 11156 | 78% | 0.050 | 27% | - (n=0) | - | - |
| pm | motorsports | 137 | 7908 | 39% | 0.040 | 16% | - (n=0) | - | - |
| pm | ice-hockey | 50 | 3861 | 86% | 0.030 | 13% | 0.7 (n=205) | - | - |
| pm | football | 32 | 3767 | 91% | 0.003 | 20% | 1.2 (n=200) | - | - |
| pm | beach-volleyball | 62 | 2543 | 82% | 0.010 | 24% | 0.5 (n=1287) | - | - |
| pm | misc | 47 | 1518 | 91% | 0.010 | 13% | - (n=0) | - | - |
| pm | cricket | 6 | 955 | 91% | 0.010 | 18% | 1.0 (n=102) | - | - |
| pm | pickleball | 145 | 902 | 13% | 0.180 | 4% | - (n=0) | - | - |
| pm | macro | 78 | 794 | 31% | 0.310 | 17% | - (n=0) | - | - |
| pm | technology | 24 | 482 | 57% | 0.120 | 30% | - (n=0) | - | - |
| pm | baseball | 3 | 300 | 93% | 0.050 | 15% | 1.0 (n=12) | - | - |
| pm | rugby | 2 | 18 | 33% | 0.450 | 3% | - (n=0) | - | - |
| pm | boxing | 1 | 1 | 0% | - | 0% | - (n=0) | - | - |
| k | KXNCAAFGAME College Football Game | 544 | 501239 | 99% | 0.110 | 2% | - | 8% | 14 |
| k | KXNFLPASSYDSPRECISE Pass Yards Precise | 15652 | 200288 | 0% | 0.390 | 0% | - | 0% | 1 |
| k | KXNFLGAME NFL Game | 84 | 111061 | 99% | 0.010 | 2% | - | 4% | 59135 |
| k | KXNBA3PT NBA Player Threes | 1305 | 108844 | 73% | 0.140 | 13% | - | 31% | 40 |
| k | KXCS2MAP Counter-Strike 2 Map Win | 584 | 84413 | 92% | 0.610 | 4% | - | 19% | 103 |
| k | KXNCAAMBTOTAL Men's College Basketball | 2964 | 82860 | 66% | 0.080 | 7% | - | 27% | 100 |
| k | KXNBAAST NBA Player Assists | 990 | 71941 | 77% | 0.150 | 13% | - | 29% | 35 |
| k | KXNCAAMBSPREAD Men's College Basketball | 2401 | 66187 | 64% | 0.060 | 6% | - | 30% | 75 |
| k | KXNBAPTS NBA Player Points | 1143 | 63107 | 76% | 0.120 | 17% | - | 24% | 30 |
| k | KXESOCCERGAME eSoccer Game | 3837 | 56596 | 16% | 0.670 | 5% | - | 31% | 25 |
| k | KXNBAREB NBA Player Rebounds | 1279 | 53573 | 70% | 0.160 | 19% | - | 28% | 29 |
| k | KXNCAAWBTOTAL Women's College Basketba | 1624 | 51275 | 28% | 0.490 | 2% | - | 13% | 41 |
| k | KXUCLSCORE Correct Score | 594 | 49949 | 63% | 0.010 | 3% | - | 17% | 3020 |
| k | KXNHLGOAL NHL Goalscorer | 1488 | 48884 | 56% | 0.080 | 11% | - | 35% | 49 |
| k | KXATPCHALLENGERMATCH Challenger ATP  | 414 | 46683 | 91% | 0.010 | 8% | - | 5% | 1005 |
| k | KXNBA3PTPROT NBA Player Threes Protec | 1320 | 46661 | 19% | 0.160 | 2% | - | 26% | 162 |
| k | KXNCAAWBSPREAD Women's College Basketba | 1250 | 42143 | 24% | 0.500 | 3% | - | 19% | 41 |
| k | KXNCAAWBGAME Women's College Basketba | 592 | 38086 | 84% | 0.220 | 6% | - | 20% | 19 |
| k | KXNCAAFTEAMTOTAL College Football Team To | 1715 | 34608 | 88% | 0.040 | 3% | - | 26% | 100 |
| k | KXNBAASTPROT NBA Player Assists Prote | 977 | 31465 | 19% | 0.150 | 2% | - | 21% | 162 |
| k | KXNCAAF1H College Football 1st Hal | 789 | 29134 | 98% | 0.860 | 1% | - | 32% | 133 |
| k | KXNBA2HSPREAD NBA 2nd Half Spread | 437 | 27510 | 68% | 0.330 | 27% | - | 45% | 100 |
| k | KXNBAPRA NBA Player Points + Rebo | 731 | 26385 | 62% | 0.420 | 18% | - | 13% | 5 |
| k | KXAFCCLSCORE Correct Score | 424 | 25828 | 39% | 0.020 | 2% | - | 15% | 453 |
| k | KXNBAPTSPROT NBA Player Points Protec | 1082 | 25794 | 20% | 0.090 | 3% | - | 16% | 162 |
| k | KXNBA2HTOTAL NBA 2nd Half Total | 437 | 25784 | 68% | 0.450 | 22% | - | 36% | 60 |
| k | KXWTASETWINNER WTA Set Winner | 216 | 24816 | 80% | 0.040 | 4% | - | 23% | 45 |
| k | KXNFLTOTALPRECISE Total Precise | 1976 | 24775 | 4% | 0.060 | 2% | - | 21% | 2 |
| k | KXMLSSCORE Correct Score | 210 | 23628 | 57% | 0.020 | 4% | - | 13% | 1288 |
| k | KXNBAREBPROT NBA Player Rebounds Prot | 1263 | 23565 | 15% | 0.160 | 4% | - | 25% | 200 |
| k | KXNCAAFSPREAD College Football Spread | 758 | 23157 | 69% | 0.140 | 7% | - | 11% | 35 |
| k | KXNCAAF1HSPREAD College Football 1st Hal | 1375 | 22566 | 91% | 0.120 | 2% | - | 32% | 15 |
| k | KXNBA1HSPREAD NBA 1st Half Spread | 380 | 22040 | 68% | 0.070 | 15% | - | 22% | 200 |
| k | KXNBA1HTOTAL NBA 1st Half Total | 380 | 21433 | 66% | 0.080 | 14% | - | 32% | 100 |
| k | KXNFLRECYDSPROT Receiving Yards Protecte | 1638 | 21248 | 11% | 0.740 | 5% | - | 15% | 19 |
| k | KXATPSETWINNER ATP Set Winner | 208 | 20134 | 92% | 0.040 | 4% | - | 11% | 47 |
| k | KXNFLRECYDS Pro Football Receiving Y | 1739 | 19832 | 0% | - | 0% | - | 0% | - |
| k | KXITFMATCH ITF Men's Match | 728 | 19822 | 78% | 0.040 | 16% | - | 9% | 59 |
| k | KXNBA3QSPREAD NBA 3rd Quarter Spread | 299 | 19819 | 74% | 0.070 | 24% | - | 54% | 100 |
| k | KXNBA3QTOTAL NBA 3rd Quarter Total | 299 | 19226 | 73% | 0.070 | 23% | - | 44% | 100 |

## Schema notes (raw keys seen)

- polymarket: active, archived, category, chatChannel, closed, combos, createdAt, description, elapsed, endDate, ended, eventState, fixtureId, hidden, id, insiderTradingRules, live, marketCounts, marketGroups, markets, metadata, participants, payoutEstimateMessage, payoutEstimateTime, period, primaryTag, score, seriesSlug, slug, sortType, sportradarGameId, startDate, startTime, streamProvider, streamRequiresAuth, tags, teams, ticker, title, updatedAt
- kalshi: can_close_early, close_time, created_time, custom_strike, early_close_condition, event_ticker, exchange_index, expected_expiration_time, expiration_time, expiration_value, last_price_dollars, latest_expiration_time, market_type, no_ask_dollars, no_bid_dollars, no_sub_title, notional_value_dollars, occurrence_datetime, open_interest_fp, open_time, previous_price_dollars, previous_yes_ask_dollars, previous_yes_bid_dollars, price_level_structure, price_ranges, result, rules_primary, rules_secondary, settlement_bounds_type, settlement_timer_seconds, settlement_value_dollars, status, strike_type, ticker, title, updated_time, volume_24h_fp, volume_fp, yes_ask_dollars, yes_ask_size_fp, yes_bid_dollars, yes_bid_size_fp, yes_sub_title

