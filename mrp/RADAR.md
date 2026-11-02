# Mr. P — sports radar

Updated 2026-11-02T20:18:26Z by `run-20261102T1848-41504075084` (last 7 days). Read-only scanner of every sports market on Polymarket US and Kalshi — it never places orders.
Kit: `mrp/mrp_sports_radar.py` on the `mrp` branch. Raw tape: `mrp/radar/<run>/`.

# Sports radar report

records 4,578,309 | 2026-10-30 20:17Z → 20:17Z | runs 25 | pairs matched 1385 | errors {'radar': 17, 'sp.k.series_poll:KXATPEXACTMATCH': 10, 'sp.k.series_poll:KXATPMATCH': 10, 'sp.k.series_poll:KXATPSETWINNER': 10, 'sp.k.series_poll:KXAUTBUNDESTOTAL': 4, 'sp.k.series_poll:KXEFLL11H': 6, 'sp.k.series_poll:KXEFLL11HSPREAD': 10, 'sp.k.series_poll:KXHNLTOTAL': 6, 'sp.k.series_poll:KXLALIGABTTS': 9, 'sp.k.series_poll:KXLALIGASCORE': 6, 'sp.k.series_poll:KXLALIGASPREAD': 8, 'sp.k.always:KXNFLGAME': 7, 'sp.k.series_poll:KXATPCHALLENGERMATCH': 7, 'sp.k.series_poll:KXEFLL11HBTTS': 10, 'sp.k.series_poll:KXLALIGA2H': 6, 'sp.k.series_poll:KXCS2MAP': 6, 'sp.k.series_poll:KXEFLL11HTOTAL': 8, 'sp.k.series_poll:KXLALIGA2HBTTS': 8, 'sp.k.series_poll:KXLALIGA2HSPREAD': 6, 'sp.k.series_poll:KXLALIGA2HTOTAL': 4, 'sp.k.series_poll:KXLALIGACORNERS': 8, 'sp.k.series_poll:KXLALIGAGAME': 6, 'sp.k.series_poll:KXLALIGAGOAL': 6, 'sp.k.series_poll:KXAUTBUNDESGAME': 2, 'sp.k.series_poll:KXCZEFLTOTAL': 7, 'sp.k.series_poll:KXELITESERIENTOTAL': 2, 'sp.k.series_poll:KXEREDIVISIETOTAL': 2, 'sp.k.always:KXNCAAFGAME': 7, 'sp.k.series_poll:KXLIGUE11HBTTS': 3, 'sp.k.series_poll:KXLIGUE11HSCORE': 4, 'sp.k.series_poll:KXLIGUE11H': 4, 'sp.k.series_poll:KXLIGUE11HSPREAD': 1}

## Catalogue (latest inventory, 18:54Z)

Polymarket US sports events 4276 of 5769 active events; Kalshi near-term sports markets 1052 in 395 events; calls so far {'pm': 43, 'k': 564}; MB {'pm': 159838363, 'k': 73937844}

| venue | sport / league / type | markets | two-sided | med spread | vol 24h |
|---|---|---|---|---|---|
| pm | football / nfl / futures | 3781 | 68% | 0.010 | 0 |
| pm | football / cfb / futures | 1597 | 79% | 0.010 | 0 |
| pm | basketball / nba / futures | 1451 | 58% | 0.020 | 0 |
| pm | ice-hockey / nhl / futures | 779 | 97% | 0.010 | 0 |
| pm | basketball / wcbb / basketball_team_full_game_winner | 670 | 34% | 0.230 | 0 |
| pm | basketball / cbb / basketball_team_full_game_winner | 653 | 30% | 0.020 | 0 |
| k | KXNCAAFGAME / College Football Game | 506 | 100% | 0.090 | 1081341 |
| pm | golf / worlwide / futures | 473 | 0% | 0.427 | 0 |
| pm | golf / lpga / futures | 440 | 0% | - | 0 |
| pm | soccer / epl / futures | 435 | 86% | 0.010 | 0 |
| pm | golf / abudhabc / futures | 352 | 0% | - | 0 |
| pm | basketball / cbb / futures | 317 | 85% | 0.010 | 0 |
| pm | soccer / ucl / futures | 276 | 78% | 0.010 | 0 |
| pm | tennis / utr / tennis_match_winner | 265 | 27% | 0.330 | 0 |
| pm | baseball / mlb / futures | 264 | 26% | 0.001 | 0 |
| pm | football / cfb / football_team_full_game_winner | 224 | 83% | 0.075 | 0 |
| pm | tennis / itfme / tennis_match_winner | 156 | 52% | 0.020 | 0 |
| pm | macro /  / futures | 150 | 75% | 0.010 | 0 |
| pm | tennis / itfwo / tennis_match_winner | 149 | 53% | 0.060 | 0 |
| pm | soccer / lal / futures | 146 | 66% | 0.010 | 0 |
| pm | boxing / boxing / futures | 145 | 0% | - | 0 |
| pm | mma / ufc / futures | 142 | 81% | 0.010 | 0 |
| pm | motorsports / f1 / futures | 123 | 3% | 0.210 | 0 |
| pm | basketball / nba / basketball_team_full_game_winner | 113 | 70% | 0.270 | 0 |
| pm | tennis / atp / tennis_match_winner | 108 | 87% | 0.010 | 0 |
| pm | tennis / atp / futures | 103 | 41% | 0.010 | 0 |
| pm | soccer / sea / futures | 86 | 80% | 0.010 | 0 |
| pm | table-tennis / setkameua / table_tennis_match_winner | 83 | 100% | 0.170 | 0 |
| pm | soccer / bun / futures | 79 | 82% | 0.010 | 0 |
| pm | soccer / lg1 / futures | 77 | 84% | 0.010 | 0 |
| pm | tennis / wta / futures | 75 | 44% | 0.010 | 0 |
| pm | soccer / j2 / soccer_team_full_time_winner | 60 | 67% | 0.020 | 0 |
| pm | tennis / atpdb / tennis_match_winner | 58 | 48% | 0.285 | 0 |
| pm | motorsports / nascar / futures | 57 | 18% | 0.040 | 0 |
| pm | soccer / uecl / soccer_team_full_time_winner | 55 | 98% | 0.030 | 0 |
| pm | tennis / wta / tennis_match_winner | 55 | 91% | 0.010 | 0 |
| pm | table-tennis / czechligapro / table_tennis_match_winner | 55 | 24% | 0.470 | 0 |
| pm | soccer / ucl / soccer_team_full_time_winner | 54 | 100% | 0.010 | 0 |
| pm | soccer / uel / soccer_team_full_time_winner | 54 | 100% | 0.020 | 0 |
| pm | soccer / mls / futures | 53 | 91% | 0.010 | 0 |
| pm | golf / masttour / futures | 52 | 100% | 0.499 | 0 |
| pm | technology /  / futures | 42 | 74% | 0.010 | 0 |
| pm | macro / usgas / futures | 40 | 0% | - | 0 |
| pm | soccer / lmx / futures | 36 | 28% | 0.045 | 0 |
| pm | soccer / uel / futures | 36 | 3% | 0.150 | 0 |
| pm | soccer / uecl / futures | 36 | 0% | - | 0 |
| pm | soccer / sea / soccer_team_full_time_winner | 36 | 100% | 0.010 | 0 |
| pm | soccer / ekst / soccer_team_full_time_winner | 36 | 53% | 0.060 | 0 |
| pm | soccer / acle / soccer_team_full_time_winner | 36 | 89% | 0.020 | 0 |
| pm | soccer / serca / soccer_team_full_time_winner | 36 | 44% | 0.475 | 0 |
| pm | soccer / eflch / soccer_team_full_time_winner | 36 | 100% | 0.020 | 0 |
| pm | soccer / lal / soccer_team_full_time_winner | 33 | 100% | 0.010 | 0 |
| pm | soccer / epl / soccer_team_full_time_winner | 33 | 100% | 0.010 | 0 |
| pm | soccer / ligpor / soccer_team_full_time_winner | 33 | 100% | 0.040 | 0 |
| pm | soccer / tff1 / soccer_team_full_time_winner | 33 | 30% | 0.480 | 0 |
| pm | soccer / alsv / soccer_team_full_time_winner | 33 | 76% | 0.050 | 0 |
| pm | ice-hockey / nhl / hockey_team_full_game_winner | 33 | 100% | 0.010 | 0 |
| k | KXNFLGAME / NFL Game | 32 | 100% | 0.010 | 3288135 |
| pm | football / nfl / football_team_full_game_winner | 30 | 63% | 0.005 | 0 |
| pm | soccer / lg1 / soccer_team_full_time_winner | 30 | 100% | 0.020 | 0 |

## Opportunities

| kind | distinct | hits | max margin $/contract | max persistence | fresh-BBO still open |
|---|---|---|---|---|---|
| decided_k | 786 | 61792 | 0.9893 | 169 min | 0/0 |
| decided_pm | 22 | 373 | 0.9947 | 28 min | 155/373 |
| decided_pm_closed | 12 | 90 | 0.9893 | 30 min | 0/90 |
| dutch_k | 15 | 70 | 0.0817 | 4 min | 0/0 |
| dutch_k_sell | 3 | 6 | 0.0107 | 0 min | 0/0 |
| dutch_pm | 64 | 3143 | 0.5316 | 50 min | 0/0 |
| implication_k | 6799 | 400246 | 0.9786 | 110 min | 0/0 |
| lag_k_settled | 193 | 33311 | 0.9973 | 273 min | 27666/32290 |
| lag_k_settled_closed | 162 | 2456 | 0.9973 | 272 min | 0/2456 |

Top by persistence × hits:

- **lag_k_settled** esports — BILIBILI GAMING vs. Hanwha Life Esports — bid 0.42 ask 0.43 buy_yes @ 0.43 | margin 0.5732 | 117 min, 1186 hits | fresh bbo 0.42/0.43 depth 12/14 | score - NS
- **lag_k_settled** basketball — Ulm Basketball vs. Baskets Oldenburg — bid 0.99 ask - sell_yes @ 0.99 | margin 0.9893 | 273 min, 941 hits | score 81-65 FT
- **lag_k_settled** basketball — Basketball Lowen Braunschweig vs. Wurzburg Baskets — bid 0.01 ask 0.02 sell_yes @ 0.01 | margin 0.4130 | 227 min, 817 hits | fresh bbo 0.01/0.02 depth 1/18 | score 60-88 Q4
- **lag_k_settled** football — North Alabama vs. Central Arkansas — bid 0.99 ask - sell_yes @ 0.995 | margin 0.9947 | 212 min, 757 hits | fresh bbo 0.99/- depth 13/0 | score 14-9 FT
- **lag_k_settled** basketball — Grambling State vs. Northern Illinois — bid 0.25 ask 0.28 sell_yes @ 0.25 | margin 0.2466 | 223 min, 521 hits | fresh bbo 0.24/0.25 depth 7/15 | score - NS
- **lag_k_settled** esports — SEIJI ESPORTS vs. ZANSIDE GAMING — bid 0.20 ask 0.30 sell_yes @ 0.2 | margin 0.1985 | 120 min, 485 hits | fresh bbo 0.20/0.30 depth 7/8 | score - NS
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
- **lag_k_settled** football — Delaware State vs. Norfolk State — bid 0.99 ask - sell_yes @ 0.995 | margin 0.9947 | 88 min, 346 hits | fresh bbo 0.99/- depth 13/0 | score 36-33 FT
- **lag_k_settled** football — Montana vs. Eastern Washington — bid 0.99 ask - sell_yes @ 0.995 | margin 0.9947 | 85 min, 335 hits | fresh bbo 0.99/- depth 14/0 | score 42-33 FT
- **lag_k_settled** basketball — Western Michigan vs. Old Dominion — bid 0.51 ask 0.53 sell_yes @ 0.51 | margin 0.5027 | 85 min, 322 hits | fresh bbo 0.51/0.53 depth 46/45 | score - NS
- **lag_k_settled** soccer — New England Revolution vs. Inter Miami CF — bid 0.17 ask 0.18 buy_yes @ 0.18 | margin 0.8097 | 70 min, 310 hits | fresh bbo 0.17/0.18 depth 12/37 | score 1-1 2H

## Live paper trades (no orders; Kalshi prices, taker fees)

Ledger L2-2026-11-01 (earlier ledgers excluded: L1)

**Total closed P&L: $-334.95 on $1292.95 staked (-25.9%)**

| rule | entries | closed | winners | staked | P&L | ROI |
|---|---|---|---|---|---|---|
| R1 anchor [ncaaf] | 26 | 26 | 11 | $262.99 | $-34.99 | -13% |
| R1 anchor [nfl] | 5 | 5 | 1 | $50.90 | $-31.90 | -63% |
| R2 q1cheap [ncaaf] | 37 | 37 | 2 | $194.50 | $-142.50 | -73% |
| R2 q1cheap [nfl] | 6 | 6 | 1 | $31.46 | $-2.46 | -8% |
| R3 blowout [ncaaf] | 16 | 16 | 1 | $339.32 | $-197.32 | -58% |
| R4 halftime [ncaaf] | 19 | 19 | 6 | $95.24 | $+9.76 | +10% |
| R6 decided [other] | 23 | 17 | 17 | $318.54 | $+64.46 | +20% |

| time (UTC) | rule | game | team | entry | contracts | why | result |
|---|---|---|---|---|---|---|---|
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

## Bot latency map: how long a decided Kalshi market stays mispriced

| sport | series | markets | already priced | mispriced then fixed | median s mispriced | closed/timeout | contradictions | cheapest ask (size) | resting @0.97 contracts / $ | settled right / wrong |
|---|---|---|---|---|---|---|---|---|---|---|
| tennis | KXATPCHALLENGERMATCH | 46 | 7 | 39 | 0 | 0 | 0 | 0.97 (53) | 0 / $0.00 | 40 / 0 |
| tennis | KXATPSETWINNER | 40 | 2 | 38 | 0 | 0 | 0 | - | 0 / $0.00 | 36 / 0 |
| soccer | KXMLSTOTAL | 38 | 0 | 36 | 0 | 2 | 0 | 0.82 (29) | 188 / $5.63 | 36 / 0 |
| soccer | KXALLSVENSKANTOTAL | 37 | 11 | 26 | 1 | 0 | 0 | - | 0 / $0.00 | 37 / 0 |
| basketball | KXNCAAWBTOTAL | 34 | 34 | 0 | - | 0 | 0 | - | 0 / $0.00 | 22 / 0 |
| soccer | KXEREDIVISIETOTAL | 30 | 0 | 30 | 0 | 0 | 0 | - | 0 / $0.00 | 26 / 0 |
| tennis | KXWTASETWINNER | 28 | 0 | 28 | 1 | 0 | 0 | - | 0 / $0.00 | 28 / 0 |
| soccer | KXELITESERIENTOTAL | 26 | 0 | 26 | 0 | 0 | 0 | - | 0 / $0.00 | 22 / 0 |
| basketball | KXNCAAWBSPREAD | 26 | 26 | 0 | - | 0 | 0 | - | 0 / $0.00 | 17 / 0 |
| soccer | KXDENSUPERLIGATOTAL | 22 | 0 | 22 | 0 | 0 | 0 | - | 0 / $0.00 | 22 / 0 |
| soccer | KXBELGIANPLTOTAL | 22 | 0 | 22 | 1 | 0 | 0 | 0.89 (454) | 763 / $22.89 | 22 / 0 |
| football | KXNFLGAME | 22 | 0 | 22 | 1 | 0 | 0 | 0.02 (0) | 0 / $0.00 | 19 / 0 |
| soccer | KXIDNSLTOTAL | 21 | 0 | 21 | 1 | 0 | 0 | 0.96 (62) | 0 / $0.00 | 21 / 0 |
| soccer | KXLIGAFTOTAL | 20 | 0 | 20 | 1 | 0 | 0 | 0.98 (87) | 0 / $0.00 | 20 / 0 |
| soccer | KXSERIECTOTAL | 20 | 0 | 20 | 1 | 0 | 0 | 0.97 (3) | 0 / $0.00 | 20 / 0 |
| soccer | KXBUNDESLIGA2TOTAL | 19 | 0 | 19 | 2 | 0 | 0 | - | 0 / $0.00 | 19 / 0 |
| soccer | KXAUTBUNDESTOTAL | 19 | 0 | 19 | 1 | 0 | 0 | - | 0 / $0.00 | 13 / 1 |
| soccer | KXAFCCLTOTAL | 16 | 14 | 2 | 2 | 0 | 0 | 0.98 (22) | 0 / $0.00 | 7 / 0 |
| football | KXNFLTOTALPRECISE | 14 | 0 | 14 | 1 | 0 | 0 | - | 0 / $0.00 | 0 / 0 |
| soccer | KXHUNNB1TOTAL | 12 | 0 | 12 | 1 | 0 | 0 | - | 0 / $0.00 | 12 / 0 |
| soccer | KXMLS1HTOTAL | 12 | 0 | 9 | 0 | 3 | 0 | 0.61 (1157) | 0 / $0.00 | 12 / 0 |
| soccer | KXARGNACBTOTAL | 12 | 11 | 1 | 1 | 0 | 0 | - | 0 / $0.00 | 7 / 0 |
| soccer | KXEKSTRAKLASATOTAL | 12 | 12 | 0 | - | 0 | 0 | - | 0 / $0.00 | 12 / 0 |
| soccer | KXECULPTOTAL | 11 | 0 | 11 | 0 | 0 | 0 | 0.93 (23) | 0 / $0.00 | 11 / 0 |
| soccer | KXALLSVENSKANSPREAD | 10 | 5 | 5 | 0 | 0 | 0 | - | 0 / $0.00 | 10 / 0 |
| tennis | KXATPEXACTMATCH | 9 | 0 | 9 | 1 | 0 | 0 | - | 0 / $0.00 | 9 / 0 |
| soccer | KXBRASILEIROBTOTAL | 9 | 0 | 9 | 0 | 0 | 0 | - | 0 / $0.00 | 8 / 0 |
| basketball | KXNCAAMBSPREAD | 9 | 2 | 0 | - | 7 | 0 | 0.62 (20) | 0 / $0.00 | 0 / 0 |
| soccer | KXTHAIL1TOTAL | 8 | 0 | 8 | 1 | 0 | 0 | 0.96 (13) | 0 / $0.00 | 8 / 0 |
| soccer | KXBUNDESLIGA2SPREAD | 8 | 0 | 8 | 2 | 0 | 0 | - | 0 / $0.00 | 8 / 0 |
| soccer | KXMLS1H | 8 | 0 | 6 | 0 | 2 | 0 | 0.63 (492) | 0 / $0.00 | 8 / 0 |
| soccer | KXPERLIGA1TOTAL | 8 | 8 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXKLEAGUETOTAL | 7 | 0 | 7 | 1 | 0 | 0 | - | 0 / $0.00 | 7 / 0 |
| soccer | KXHNLTOTAL | 7 | 0 | 7 | 0 | 0 | 0 | - | 0 / $0.00 | 7 / 0 |
| soccer | KXDIMAYORTOTAL | 7 | 0 | 7 | 0 | 0 | 0 | - | 0 / $0.00 | 7 / 0 |
| basketball | KXNCAAMBTOTAL | 7 | 2 | 0 | - | 5 | 0 | 0.75 (120) | 0 / $0.00 | 0 / 0 |
| tennis | KXATPMATCH | 6 | 0 | 6 | 1 | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| soccer | KXCZEFNLTOTAL | 6 | 0 | 6 | 0 | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| soccer | KXSLGREECETOTAL | 6 | 5 | 1 | 0 | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| basketball | KXNCAAWBGAME | 6 | 6 | 0 | - | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
| soccer | KXMYSLTOTAL | 5 | 0 | 5 | 0 | 0 | 0 | - | 0 / $0.00 | 5 / 0 |
| soccer | KXLALIGA2TOTAL | 5 | 3 | 2 | 0 | 0 | 0 | - | 0 / $0.00 | 5 / 0 |
| soccer | KXAPFDDHTOTAL | 5 | 0 | 5 | 0 | 0 | 0 | - | 0 / $0.00 | 5 / 0 |
| soccer | KXLIGAPORTUGALTOTAL | 5 | 0 | 5 | 0 | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXMLSSPREAD | 5 | 0 | 5 | 1 | 0 | 0 | - | 0 / $0.00 | 5 / 0 |
| soccer | KXEKSTRAKLASASPREAD | 5 | 5 | 0 | - | 0 | 0 | - | 0 / $0.00 | 5 / 0 |
| soccer | KXARGNACBSPREAD | 5 | 5 | 0 | - | 0 | 0 | - | 0 / $0.00 | 0 / 0 |
| soccer | KXSERIECSPREAD | 4 | 0 | 4 | 0 | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
| soccer | KXCZEFLTOTAL | 4 | 0 | 4 | 1 | 0 | 0 | 0.47 (1945) | 76 / $2.29 | 2 / 0 |
| soccer | KXMLS1HBTTS | 4 | 0 | 3 | 0 | 1 | 0 | 0.78 (68) | 0 / $0.00 | 4 / 0 |
| soccer | KXTFF1LIGTOTAL | 3 | 0 | 3 | 1 | 0 | 0 | 0.97 (5) | 0 / $0.00 | 2 / 1 |
| football | KXMLSTOTAL | 3 | 0 | 0 | - | 3 | 0 | 0.71 (2845) | 0 / $0.00 | 3 / 0 |
| soccer | KXMLSGAME | 3 | 0 | 3 | 1 | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXEKSTRAKLASAGAME | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXLIGUE2TOTAL | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 0 / 0 |
| soccer | KXAFCCLGAME | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 0 / 0 |
| soccer | KXARGNACBGAME | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 0 / 0 |
| soccer | KXALLSVENSKANBTTS | 2 | 0 | 2 | 0 | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXEREDIVISIEBTTS | 2 | 0 | 2 | 0 | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXEREDIVISIESPREAD | 2 | 0 | 2 | 0 | 0 | 0 | - | 0 / $0.00 | 0 / 0 |
| soccer | KXDENSUPERLIGASPREAD | 2 | 0 | 2 | 0 | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXLIGAEXPTOTAL | 2 | 0 | 2 | 1 | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXCHLLDPTOTAL | 2 | 0 | 2 | 1 | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXMLSBTTS | 2 | 0 | 2 | 1 | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXARGPREMDIVTOTAL | 2 | 0 | 2 | 1 | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXARGNACBBTTS | 2 | 1 | 1 | 1 | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| tennis | KXATPDOUBLES | 2 | 0 | 2 | 0 | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| basketball | KXNCAAMBGAME | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 0 / 0 |
| soccer | KXIDNSLBTTS | 1 | 0 | 1 | 0 | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXBUNDESLIGA2BTTS | 1 | 0 | 1 | 0 | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXDENSUPERLIGABTTS | 1 | 0 | 1 | 0 | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXSCOCUPTOTAL | 1 | 0 | 1 | 0 | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXSUPERLIGTOTAL | 1 | 0 | 1 | 0 | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXELITESERIENBTTS | 1 | 0 | 1 | 0 | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| football | KXNFLEQBTTS | 1 | 0 | 0 | - | 1 | 0 | 0.54 (28) | 10 / $0.30 | 1 / 0 |
| football | KXMLSBTTS | 1 | 0 | 0 | - | 1 | 0 | 0.72 (25231) | 0 / $0.00 | 1 / 0 |
| soccer | KXBRASILEIROBBTTS | 1 | 0 | 1 | 1 | 0 | 0 | - | 0 / $0.00 | 0 / 0 |
| soccer | KXAFCCLBTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 0 / 0 |

'Already priced' = the book was at 99c+ when we first looked (bots were faster than our score feed). 'Median s mispriced' runs from our decision to the fix. 'Settled right / wrong' checks our certainty against Kalshi's result — any 'wrong' means the score feed or the model failed.

## Decided-state engine (contracts the live score already settled, still trading)

2803 contracts decided while active; 786 had a price leaving > 0.4c after fees; 645 of those were mispriced AFTER the score was stable (lock tier)

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
| KXESOCCERGAME eSoccer Game | 3727 | 4.0 min | 4.1 min |
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
| KXNBAREBPROT NBA Player Rebounds Protected | 941 | 2.5 min | 2.6 min |
| KXNBAPTS NBA Player Points | 886 | 2.0 min | 2.1 min |
| KXLIGAPROMATCH Russia Liga Pro Match | 872 | 4.0 min | 4.1 min |
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
| KXEBASKETBALLGAME eBasketball Game | 482 | 4.0 min | 4.1 min |
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
| pm | soccer | 1869 | 263055 | 86% | 0.020 | 19% | 0.6 (n=4028) | - | - |
| pm | tennis | 1561 | 101430 | 91% | 0.010 | 23% | 0.5 (n=46933) | - | - |
| pm | esports | 3214 | 79393 | 76% | 0.030 | 19% | 0.5 (n=16881) | - | - |
| pm | basketball | 983 | 56585 | 83% | 0.040 | 25% | 0.5 (n=9091) | - | - |
| pm | table-tennis | 1451 | 54082 | 95% | 0.030 | 31% | 0.5 (n=26263) | - | - |
| pm | football | 121 | 22415 | 91% | 0.005 | 17% | 1.1 (n=1098) | - | - |
| pm | climate | 215 | 10895 | 77% | 0.050 | 23% | - (n=0) | - | - |
| pm | motorsports | 159 | 8546 | 40% | 0.040 | 14% | - (n=0) | - | - |
| pm | ice-hockey | 84 | 7345 | 82% | 0.060 | 14% | 0.7 (n=420) | - | - |
| pm | misc | 47 | 3778 | 93% | 0.010 | 12% | - (n=0) | - | - |
| pm | beach-volleyball | 59 | 2708 | 84% | 0.010 | 23% | 0.5 (n=1399) | - | - |
| pm | cricket | 7 | 2112 | 92% | 0.020 | 11% | 1.0 (n=330) | - | - |
| pm | mma | 14 | 759 | 95% | 0.020 | 4% | - (n=0) | - | - |
| pm | darts | 17 | 348 | 82% | 0.070 | 23% | 0.5 (n=62) | - | - |
| pm | macro | 98 | 316 | 0% | - | 0% | - (n=0) | - | - |
| pm | rugby | 20 | 282 | 69% | 0.450 | 20% | - (n=0) | - | - |
| pm | boxing | 4 | 165 | 95% | 0.030 | 56% | - (n=0) | - | - |
| pm | baseball | 1 | 98 | 92% | 0.150 | 10% | 2.3 (n=5) | - | - |
| pm | technology | 10 | 80 | 51% | 0.240 | 18% | - (n=0) | - | - |
| pm | pickleball | 10 | 78 | 74% | 0.175 | 15% | - (n=0) | - | - |
| k | KXNCAAFGAME College Football Game | 720 | 602645 | 98% | 0.050 | 2% | - | 7% | 57 |
| k | KXNFLPASSYDSPRECISE Pass Yards Precise | 15652 | 185544 | 0% | 0.390 | 0% | - | 0% | 1 |
| k | KXNBA3PT NBA Player Threes | 1533 | 145496 | 82% | 0.080 | 13% | - | 24% | 31 |
| k | KXNFLGAME NFL Game | 56 | 125275 | 99% | 0.010 | 2% | - | 3% | 115665 |
| k | KXCS2MAP Counter-Strike 2 Map Win | 456 | 87426 | 93% | 0.470 | 5% | - | 19% | 100 |
| k | KXNBAAST NBA Player Assists | 1138 | 79111 | 84% | 0.070 | 12% | - | 25% | 27 |
| k | KXNBAPTS NBA Player Points | 1296 | 69307 | 81% | 0.050 | 14% | - | 23% | 42 |
| k | KXESOCCERGAME eSoccer Game | 3969 | 64598 | 24% | 0.450 | 6% | - | 27% | 35 |
| k | KXNBAREB NBA Player Rebounds | 1432 | 64431 | 78% | 0.080 | 16% | - | 22% | 36 |
| k | KXNBA3PTPROT NBA Player Threes Protec | 1484 | 58105 | 35% | 0.150 | 2% | - | 19% | 105 |
| k | KXNCAAFSPREAD College Football Spread | 2631 | 57724 | 50% | 0.090 | 4% | - | 12% | 75 |
| k | KXNCAAFTEAMTOTAL College Football Team To | 1259 | 55350 | 72% | 0.020 | 2% | - | 25% | 383 |
| k | KXNCAAFTOTAL College Football Total P | 1889 | 39524 | 48% | 0.140 | 4% | - | 16% | 135 |
| k | KXNBA1HTEAMTOTAL NBA 1st Half Team Total | 704 | 36598 | 62% | 0.260 | 15% | - | 23% | 123 |
| k | KXNCAAMBTOTAL Men's College Basketball | 2444 | 33422 | 95% | 0.110 | 4% | - | 27% | 58 |
| k | KXNBAASTPROT NBA Player Assists Prote | 1111 | 33342 | 28% | 0.150 | 2% | - | 17% | 162 |
| k | KXATPSETWINNER ATP Set Winner | 230 | 32520 | 93% | 0.030 | 3% | - | 11% | 138 |
| k | KXMLSSCORE Correct Score | 450 | 31078 | 52% | 0.020 | 3% | - | 14% | 1192 |
| k | KXNCAAF1H College Football 1st Hal | 1047 | 30303 | 86% | 0.820 | 1% | - | 27% | 133 |
| k | KXNBA1HTOTAL NBA 1st Half Total | 608 | 29387 | 65% | 0.040 | 10% | - | 27% | 144 |
| k | KXNBA1HSPREAD NBA 1st Half Spread | 608 | 29290 | 67% | 0.030 | 10% | - | 15% | 144 |
| k | KXATPCHALLENGERMATCH Challenger ATP  | 316 | 27176 | 89% | 0.010 | 8% | - | 5% | 591 |
| k | KXNBAPTSPROT NBA Player Points Protec | 1204 | 26085 | 26% | 0.750 | 2% | - | 12% | 162 |
| k | KXNCAAMBSPREAD Men's College Basketball | 1994 | 26003 | 96% | 0.080 | 3% | - | 33% | 50 |
| k | KXLIGAMXSCORE Correct Score | 270 | 25148 | 54% | 0.020 | 3% | - | 13% | 800 |
| k | KXNBA2HSPREAD NBA 2nd Half Spread | 646 | 25109 | 71% | 0.130 | 20% | - | 28% | 123 |
| k | KXNBAREBPROT NBA Player Rebounds Prot | 1379 | 24314 | 25% | 0.530 | 4% | - | 17% | 33 |
| k | KXWTASETWINNER WTA Set Winner | 264 | 24222 | 78% | 0.050 | 4% | - | 26% | 62 |
| k | KXNBA2HTOTAL NBA 2nd Half Total | 646 | 23655 | 73% | 0.160 | 20% | - | 25% | 101 |
| k | KXNCAAF1HSPREAD College Football 1st Hal | 1062 | 23323 | 42% | 0.020 | 8% | - | 30% | 344 |
| k | KXNFLTOTALPRECISE Total Precise | 1976 | 22799 | 4% | 0.060 | 2% | - | 21% | 2 |
| k | KXNFLRECYDSPROT Receiving Yards Protecte | 1626 | 19862 | 11% | 0.740 | 5% | - | 15% | 19 |
| k | KXNHLGOAL NHL Goalscorer | 1176 | 19439 | 26% | 0.020 | 11% | - | 20% | 64 |
| k | KXNEXTTEAMNHL Next Team NHL | 230 | 18860 | 0% | 0.130 | 0% | - | 23% | 341 |
| k | KXNFLRECYDS Pro Football Receiving Y | 1605 | 18316 | 0% | - | 0% | - | 0% | - |
| k | KXMLSTOTAL MLS Total | 209 | 17862 | 86% | 0.050 | 2% | - | 12% | 190 |
| k | KXNBA2QSPREAD NBA 2nd Quarter Spread | 416 | 17614 | 65% | 0.040 | 11% | - | 18% | 168 |
| k | KXNBA2QTOTAL NBA 2nd Quarter Total | 403 | 15760 | 60% | 0.050 | 11% | - | 34% | 159 |
| k | KXNBA1QSPREAD NBA 1st Quarter Spread | 338 | 14231 | 59% | 0.040 | 12% | - | 32% | 200 |
| k | KXNCAAF2HSPREAD College Football 2nd Hal | 720 | 14148 | 40% | 0.050 | 7% | - | 12% | 8 |

## Schema notes (raw keys seen)

- polymarket: active, archived, category, chatChannel, closed, combos, createdAt, description, elapsed, endDate, ended, eventState, fixtureId, hidden, id, insiderTradingRules, live, marketCounts, marketGroups, markets, metadata, participants, payoutEstimateMessage, payoutEstimateTime, period, primaryTag, score, seriesSlug, slug, sortType, sportradarGameId, startDate, startTime, streamProvider, streamRequiresAuth, tags, teams, ticker, title, updatedAt
- kalshi: can_close_early, close_time, created_time, early_close_condition, event_ticker, exchange_index, expected_expiration_time, expiration_time, expiration_value, floor_strike, last_price_dollars, latest_expiration_time, market_type, no_ask_dollars, no_bid_dollars, no_sub_title, notional_value_dollars, occurrence_datetime, open_interest_fp, open_time, previous_price_dollars, previous_yes_ask_dollars, previous_yes_bid_dollars, price_level_structure, price_ranges, result, rules_primary, rules_secondary, settlement_bounds_type, settlement_timer_seconds, status, strike_type, ticker, title, updated_time, volume_24h_fp, volume_fp, yes_ask_dollars, yes_ask_size_fp, yes_bid_dollars, yes_bid_size_fp, yes_sub_title

