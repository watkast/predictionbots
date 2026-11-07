# Mr. P — sports radar

Updated 2026-11-07T04:57:03Z by `run-20261107T0022-42312295640` (last 7 days). Read-only scanner of every sports market on Polymarket US and Kalshi — it never places orders.
Kit: `mrp/mrp_sports_radar.py` on the `mrp` branch. Raw tape: `mrp/radar/<run>/`.

# Sports radar report

records 4,550,686 | 2026-11-04 04:55Z → 04:55Z | runs 11 | pairs matched 1402 | errors {'sp.stream': 17, 'radar': 1}

## Catalogue (latest inventory, 03:28Z)

Polymarket US sports events 4589 of 5514 active events; Kalshi near-term sports markets 5445 in 792 events; calls so far {'pm': 2870, 'k': 21595}; MB {'pm': 3412531921, 'k': 10164609044}

| venue | sport / league / type | markets | two-sided | med spread | vol 24h |
|---|---|---|---|---|---|
| pm | football / nfl / futures | 4104 | 60% | 0.010 | 0 |
| pm | football / cfb / futures | 1643 | 40% | 0.010 | 0 |
| pm | basketball / nba / futures | 1450 | 48% | 0.030 | 0 |
| pm | ice-hockey / nhl / futures | 779 | 91% | 0.010 | 0 |
| pm | basketball / cbb / basketball_team_full_game_winner | 760 | 17% | 0.090 | 0 |
| pm | basketball / wcbb / basketball_team_full_game_winner | 735 | 18% | 0.120 | 0 |
| k | KXNCAAFGAME / College Football Game | 518 | 100% | 0.040 | 20027552 |
| pm | soccer / epl / futures | 437 | 87% | 0.010 | 0 |
| pm | basketball / cbb / futures | 396 | 88% | 0.010 | 0 |
| pm | golf / worlwide / futures | 359 | 14% | 0.003 | 0 |
| pm | tennis / utr / tennis_match_winner | 351 | 8% | 0.020 | 0 |
| k | KXNBA3PT / NBA Player Threes | 334 | 100% | 0.070 | 537144 |
| pm | soccer / ucl / futures | 285 | 78% | 0.010 | 0 |
| pm | table-tennis / setkameua / table_tennis_match_winner | 246 | 91% | 0.170 | 0 |
| k | KXLIGAMXSCORE / Correct Score | 240 | 100% | 0.020 | 98249 |
| pm | football / cfb / football_team_full_game_winner | 236 | 80% | 0.010 | 0 |
| pm | golf / lpga / futures | 154 | 2% | 0.150 | 0 |
| pm | soccer / lal / futures | 147 | 49% | 0.010 | 0 |
| pm | mma / ufc / futures | 145 | 83% | 0.010 | 0 |
| pm | boxing / boxing / futures | 145 | 0% | - | 0 |
| pm | golf / abudhabc / futures | 140 | 21% | 0.009 | 0 |
| pm | motorsports / f1 / futures | 123 | 18% | 0.025 | 0 |
| pm | macro /  / futures | 123 | 70% | 0.010 | 0 |
| k | KXNBA2HSPREAD / NBA 2nd Half Spread | 114 | 100% | 0.070 | 44140 |
| k | KXNBA2HTOTAL / NBA 2nd Half Total | 114 | 100% | 0.070 | 16180 |
| pm | basketball / nba / basketball_team_full_game_winner | 107 | 99% | 0.260 | 0 |
| pm | soccer / sea / futures | 88 | 85% | 0.010 | 0 |
| pm | tennis / atp / futures | 85 | 36% | 0.010 | 0 |
| pm | macro / usgas / futures | 82 | 66% | 0.010 | 0 |
| pm | soccer / bun / futures | 80 | 84% | 0.010 | 0 |
| pm | soccer / lg1 / futures | 79 | 86% | 0.010 | 0 |
| pm | tennis / wta / futures | 75 | 44% | 0.030 | 0 |
| pm | baseball / mlb / futures | 72 | 65% | 0.001 | 0 |
| k | KXNBA2D / NBA Player Double Double | 70 | 100% | 0.290 | 59565 |
| pm | macro / usdsl / futures | 63 | 30% | 0.150 | 0 |
| pm | soccer / afcq / soccer_team_full_time_winner | 63 | 57% | 0.465 | 0 |
| pm | esports / dota2 / esports_match_winner | 60 | 47% | 0.070 | 0 |
| k | KXNBA2H / NBA 2nd Half Winner | 57 | 100% | 0.580 | 30075 |
| k | KXNFLGAME / NFL Game | 56 | 100% | 0.010 | 1827739 |
| pm | soccer / unl / soccer_team_full_time_winner | 54 | 98% | 0.050 | 0 |
| pm | technology /  / futures | 53 | 79% | 0.010 | 0 |
| pm | table-tennis / czechligapro / table_tennis_match_winner | 53 | 9% | 0.200 | 0 |
| pm | motorsports / nascar / futures | 52 | 38% | 0.020 | 0 |
| pm | golf / masttour / futures | 52 | 100% | 0.499 | 0 |
| k | KXLIGAMXTEAMTOTAL / Team Total | 51 | 100% | 0.040 | 47694 |
| k | KXLIGAMXTOTAL / Liga MX Total | 49 | 100% | 0.020 | 743347 |
| pm | table-tennis / setkamecz / table_tennis_match_winner | 48 | 85% | 0.170 | 0 |
| k | KXNBA1H / NBA 1st Half Winner | 48 | 100% | 0.060 | 79659 |
| k | KXNBA2Q / NBA 2nd Quarter Winner | 48 | 100% | 0.990 | 770 |
| pm | esports / cs2 / esports_match_winner | 46 | 83% | 0.065 | 0 |
| pm | soccer / mls / soccer_team_full_time_winner | 45 | 100% | 0.010 | 0 |
| k | KXNBA1HTEAMTOTAL / NBA 1st Half Team Total | 44 | 100% | 0.260 | 3035 |
| pm | soccer / mls / futures | 42 | 86% | 0.010 | 0 |
| pm | tennis / itfwo / tennis_match_winner | 42 | 83% | 0.030 | 0 |
| k | KXLIGAMXGOAL / Goalscorer | 40 | 100% | 0.055 | 11026 |
| pm | boxing / boxing / boxing_match_winner | 39 | 72% | 0.080 | 0 |
| k | KXLIGAMXGAME / Liga MX Game | 39 | 100% | 0.020 | 1934048 |
| k | KXNBA1HSPREAD / NBA 1st Half Spread | 38 | 100% | 0.040 | 122247 |
| k | KXNBA1HTOTAL / NBA 1st Half Total | 38 | 100% | 0.040 | 100659 |
| pm | tennis / itfme / tennis_match_winner | 37 | 86% | 0.010 | 0 |

## Opportunities

| kind | distinct | hits | max margin $/contract | max persistence | fresh-BBO still open |
|---|---|---|---|---|---|
| decided_k | 192 | 4027 | 0.9893 | 35 min | 0/0 |
| decided_pm | 45 | 2383 | 0.9893 | 62 min | 164/247 |
| decided_pm_closed | 29 | 2431 | 0.9893 | 63 min | 2340/2431 |
| dutch_k | 26 | 201 | 0.1123 | 18 min | 0/0 |
| dutch_k_sell | 2 | 3 | 0.0663 | 0 min | 0/0 |
| dutch_pm | 59 | 2251 | 0.5248 | 47 min | 0/0 |
| implication_k | 246 | 3079 | 0.7472 | 12 min | 0/0 |
| lag_k_settled | 164 | 28070 | 0.9947 | 299 min | 24795/26457 |
| lag_k_settled_closed | 165 | 2910 | 0.9947 | 111 min | 128/2910 |

Top by persistence × hits:

- **lag_k_settled** football — South Florida vs. East Carolina — bid 0.29 ask 0.30 sell_yes @ 0.295 | margin 0.7008 | 115 min, 796 hits | fresh bbo 0.29/0.30 depth 45/67 | score 10-17 Q4
- **lag_k_settled** esports — Spirit Academy vs. Xipto Esports — bid 0.37 ask 0.38 buy_yes @ 0.38 | margin 0.7163 | 299 min, 539 hits | fresh bbo 0.37/0.38 depth 23/31 | score 1-1 Live
- **lag_k_settled** soccer — Club Universitario de Deportes vs. Sport Boys Association — bid 0.66 ask 0.67 sell_yes @ 0.66 | margin 0.6444 | 121 min, 479 hits | fresh bbo 0.66/0.67 depth 11/7 | score - NS
- **lag_k_settled** soccer — Club Universitario de Deportes vs. Sport Boys Association — bid 0.21 ask 0.23 sell_yes @ 0.21 | margin 0.1985 | 121 min, 479 hits | fresh bbo 0.21/0.23 depth 8/11 | score - NS
- **lag_k_settled** soccer — Club Universitario de Deportes vs. Sport Boys Association — bid 0.12 ask 0.13 sell_yes @ 0.12 | margin 0.1221 | 121 min, 479 hits | fresh bbo 0.12/0.13 depth 8/14 | score - NS
- **lag_k_settled** esports — Spirit Academy Green vs. Fire Flux Esports — bid 0.42 ask 0.43 buy_yes @ 0.43 | margin 0.5530 | 120 min, 479 hits | fresh bbo 0.42/0.43 depth 14/12 | score - NS
- **lag_k_settled** esports — LPH Gaming vs.  Phantom Academy — bid 0.57 ask 0.58 sell_yes @ 0.57 | margin 0.5467 | 120 min, 478 hits | fresh bbo 0.57/0.58 depth 7/8 | score - NS
- **lag_k_settled** basketball — Northern Iowa (W) vs. South Dakota State (W) — bid 0.15 ask 0.16 sell_yes @ 0.15 | margin 0.1379 | 115 min, 458 hits | fresh bbo 0.15/0.16 depth 11/9 | score - NS
- **lag_k_settled** basketball — Washington State (W) vs. Oregon (W) — bid 0.01 ask 0.02 sell_yes @ 0.01 | margin 0.0091 | 115 min, 457 hits | fresh bbo 0.01/0.02 depth 1/16 | score 0-0 NS
- **lag_k_settled** basketball — Baskets Bonn vs. Bnei Herzliya Basket — bid 0.99 ask - sell_yes @ 0.99 | margin 0.9893 | 111 min, 430 hits | fresh bbo 0.99/- depth 15/0 | score 101-89 FT
- **lag_k_settled** tennis — Basile - MEERSCHEN vs. Golescu - Haita — bid 0.59 ask 0.94 buy_yes @ 0.94 | margin 0.1221 | 94 min, 406 hits | fresh bbo 0.59/0.99 depth 4/1 | score 0-0 
- **lag_k_settled** esports — Weibo Gaming vs. Dplus — bid 0.85 ask 0.98 buy_yes @ 0.98 | margin 0.3440 | 108 min, 389 hits | fresh bbo 0.85/0.98 depth 25/2 | score 0-0 Map 1
- **lag_k_settled** tennis — Arcangioli - Cirotte vs. Gaillard - Sequeira — bid 0.92 ask 0.98 buy_yes @ 0.98 | margin 0.0373 | 54 min, 404 hits | fresh bbo 0.07/0.97 depth 6/3 | score 0-0 
- **lag_k_settled** tennis — Burrage / Montgomery vs. Kostovic / Vandromme — bid 0.42 ask 0.83 buy_yes @ 0.83 | margin 0.1602 | 85 min, 340 hits | fresh bbo 0.42/0.83 depth 5/5 | score 0-0 CAN
- **lag_k_settled** esports — eBattles: Argentina (Totti) vs. England (Tesla) — bid 0.18 ask 0.21 sell_yes @ 0.18 | margin 0.1697 | 76 min, 304 hits | score 3-5 FT
- **lag_k_settled** esports — eBattles: Argentina (Totti) vs. England (Tesla) — bid 0.56 ask 0.59 sell_yes @ 0.56 | margin 0.5429 | 40 min, 304 hits | score 3-5 FT
- **lag_k_settled** esports — eBattles: Argentina (Totti) vs. England (Tesla) — bid 0.21 ask 0.25 buy_yes @ 0.25 | margin 0.7370 | 40 min, 300 hits | score 3-5 FT
- **lag_k_settled** esports — eBattles: Liverpool (Maki) vs. Arsenal (Krkula) — bid 0.02 ask 0.04 sell_yes @ 0.02 | margin 0.3772 | 66 min, 267 hits | fresh bbo -/0.95 depth 0/3 | score 3-5 2H
- **lag_k_settled** esports — eBattles: Liverpool (Maki) vs. Arsenal (Krkula) — bid 0.18 ask 0.20 sell_yes @ 0.18 | margin 0.2227 | 66 min, 267 hits | fresh bbo 0.01/0.95 depth 1/3 | score 3-5 2H
- **lag_k_settled** esports — eBattles: Liverpool (Maki) vs. Arsenal (Krkula) — bid 0.76 ask 0.99 buy_yes @ 0.99 | margin 0.5670 | 66 min, 267 hits | fresh bbo 0.92/- depth 4/0 | score 3-5 2H
- **lag_k_settled** esports — eBattles: Liverpool (llulle) vs. Arsenal (Animal) — bid 0.26 ask 0.27 sell_yes @ 0.26 | margin 0.6138 | 66 min, 266 hits | fresh bbo 0.26/0.27 depth 9/10 | score 1-1 1H
- **lag_k_settled** esports — eBattles: Liverpool (llulle) vs. Arsenal (Animal) — bid 0.28 ask 0.31 sell_yes @ 0.28 | margin 0.4328 | 66 min, 263 hits | fresh bbo 0.28/0.31 depth 9/9 | score 1-1 1H
- **lag_k_settled** esports — eBattles: Liverpool (llulle) vs. Arsenal (Animal) — bid 0.43 ask 0.45 buy_yes @ 0.45 | margin 0.7785 | 66 min, 263 hits | fresh bbo 0.08/0.91 depth 4/5 | score 1-1 1H
- **lag_k_settled** esports — eBattles: Real Madrid (Grellz) vs. Paris (Nightxx) — bid 0.40 ask 0.41 sell_yes @ 0.4 | margin 0.8915 | 67 min, 261 hits | fresh bbo 0.40/0.41 depth 2/5 | score 0-0 
- **lag_k_settled** esports — eBattles: Real Madrid (Grellz) vs. Paris (Nightxx) — bid 0.28 ask 0.29 sell_yes @ 0.28 | margin 0.2608 | 67 min, 261 hits | fresh bbo 0.28/0.29 depth 5/2 | score 0-0 

## Live paper trades (no orders; Kalshi prices, taker fees)

Ledger L2-2026-11-01 (earlier ledgers excluded: none)

**Total closed P&L: $-102.55 on $559.55 staked (-18.3%)**

| rule | entries | closed | winners | staked | P&L | ROI |
|---|---|---|---|---|---|---|
| R1 anchor [ncaaf] | 5 | 3 | 2 | $30.31 | $+0.69 | +2% |
| R2 q1cheap [ncaaf] | 8 | 5 | 1 | $26.07 | $+6.93 | +27% |
| R2 q1cheap [nfl] | 1 | 1 | 0 | $5.22 | $-5.22 | -100% |
| R3 blowout [ncaaf] | 1 | 1 | 0 | $21.08 | $-21.08 | -100% |
| R6 decided [other] | 41 | 28 | 23 | $476.88 | $-83.88 | -18% |

| time (UTC) | rule | game | team | entry | contracts | why | result |
|---|---|---|---|---|---|---|---|
| 04:47 | R1 anchor | TCU vs. Arizona | TCU | 0.46 | 21 | pregame dog (mid 0.30) leads 13-10 in Q2, ask 0.46 | open |
| 04:44 | R6 decided | North Dakota State vs. San F | Over 48.5 points | 0.61 | 32 | score 61-70 total 131 > 48.5 | open |
| 04:44 | R6 decided | North Dakota State vs. San F | Over 45.5 points | 0.68 | 29 | score 61-70 total 131 > 45.5 | open |
| 04:44 | R6 decided | North Dakota State vs. San F | Over 42.5 points | 0.74 | 27 | score 61-70 total 131 > 42.5 | open |
| 04:44 | R6 decided | North Dakota State vs. San F | Over 39.5 points | 0.82 | 14 | score 61-70 total 131 > 39.5 | open |
| 04:44 | R6 decided | North Dakota State vs. San F | Over 36.5 points | 0.88 | 22 | score 61-70 total 131 > 36.5 | open |
| 04:44 | R6 decided | North Dakota State vs. San F | Over 33.5 points | 0.93 | 21 | score 61-70 total 131 > 33.5 | open |
| 04:44 | R6 decided | North Dakota State vs. San F | Over 30.5 points | 0.95 | 21 | score 61-70 total 131 > 30.5 | open |
| 03:44 | R2 q1cheap | TCU vs. Arizona | TCU | 0.19 | 26 | Q1 ask 0.19, score 0-7 | open |
| 03:18 | R1 anchor | Nebraska vs. Illinois | Illinois | 0.64 | 15 | pregame dog (mid 0.35) leads 7-14 in Q3, ask 0.64 | final score (pending Kalshi settlement): 1.00, $+5.16 |
| 02:05 | R2 q1cheap | New Mexico vs. Nevada | Nevada | 0.20 | 25 | Q1 ask 0.20, score 0-0 | open |
| 01:52 | R6 decided | Northern Iowa (W) vs. South  | South Dakota St. | 0.84 | 23 | ended 54-76 | final score (pending Kalshi settlement): 1.00, $+3.46 |
| 00:29 | R2 q1cheap | Virginia Tech vs. SMU | Virginia Tech | 0.17 | 29 | Q1 ask 0.17, score 0-7 | final score (pending Kalshi settlement): 0.00, $-5.22 |
| 00:29 | R1 anchor | Southern Illinois (W) vs. In | Indiana St. | 0.40 | 25 | pregame dog (mid 0.40) leads 14-38 in Q2, ask 0.40 | open |
| 00:05 | R2 q1cheap | Northern Iowa (W) vs. South  | Northern Iowa | 0.17 | 29 | Q1 ask 0.17, score 0-0 | final score (pending Kalshi settlement): 0.00, $-5.22 |
| 18:38 | R6 decided | Anastasia Zakharova vs. Lucr | Anastasia Zakharova | 0.90 | 22 | set 2 final 5-2 | open |
| 14:40 | R6 decided | Mai Hontama vs. Magda Linett | Mai Hontama | 0.92 | 1 | set 1 final 6-4 | kalshi settled: 1.00, $+0.07 |
| 04:43 | R6 decided | Cal Poly vs. Arizona | Over 58.5 points | 0.63 | 31 | score 41-59 total 100 > 58.5 | open |
| 04:43 | R6 decided | Cal Poly vs. Arizona | Over 54.5 points | 0.75 | 26 | score 41-59 total 100 > 54.5 | open |
| 04:43 | R6 decided | Cal Poly vs. Arizona | Over 50.5 points | 0.92 | 21 | score 41-59 total 100 > 50.5 | open |
| 04:43 | R6 decided | Cal Poly vs. Arizona | Over 46.5 points | 0.99 | 20 | score 41-59 total 100 > 46.5 | open |
| 04:43 | R6 decided | Cal Poly vs. Arizona | Over 42.5 points | 0.99 | 20 | score 41-59 total 100 > 42.5 | open |
| 03:43 | R2 q1cheap | Cal Poly vs. Arizona | Cal Poly | 0.18 | 27 | Q1 ask 0.18, score 0-0 | open |
| 03:02 | R6 decided | Texas Southern (W) vs. LSU ( | LSU wins by over 40.5 points | 0.98 | 20 | ended 22-131 margin 109 vs 40.5 | kalshi settled: 1.00, $+0.37 |
| 03:02 | R6 decided | Texas Southern (W) vs. LSU ( | LSU wins by over 35.5 points | 0.98 | 20 | ended 22-131 margin 109 vs 35.5 | kalshi settled: 1.00, $+0.37 |
| 03:02 | R6 decided | Texas Southern (W) vs. LSU ( | LSU wins by over 30.5 points | 0.98 | 20 | ended 22-131 margin 109 vs 30.5 | kalshi settled: 1.00, $+0.37 |
| 03:02 | R6 decided | Texas Southern (W) vs. LSU ( | LSU wins by over 26.5 points | 0.98 | 20 | ended 22-131 margin 109 vs 26.5 | kalshi settled: 1.00, $+0.37 |
| 03:02 | R6 decided | Texas Southern (W) vs. LSU ( | LSU wins by over 23.5 points | 0.98 | 20 | ended 22-131 margin 109 vs 23.5 | kalshi settled: 1.00, $+0.37 |
| 03:02 | R6 decided | Texas Southern (W) vs. LSU ( | LSU wins by over 20.5 points | 0.98 | 20 | ended 22-131 margin 109 vs 20.5 | kalshi settled: 1.00, $+0.37 |
| 03:02 | R6 decided | Texas Southern (W) vs. LSU ( | LSU wins by over 1.5 points | 0.99 | 20 | ended 22-131 margin 109 vs 1.5 | kalshi settled: 1.00, $+0.19 |
| 03:02 | R6 decided | Texas Southern (W) vs. LSU ( | LSU wins by over 16.5 points | 0.98 | 20 | ended 22-131 margin 109 vs 16.5 | kalshi settled: 1.00, $+0.37 |
| 03:02 | R6 decided | Texas Southern (W) vs. LSU ( | LSU wins by over 11.5 points | 0.99 | 20 | ended 22-131 margin 109 vs 11.5 | kalshi settled: 1.00, $+0.19 |
| 03:02 | R6 decided | Texas Southern (W) vs. LSU ( | LSU | 0.99 | 20 | ended 22-131 | kalshi settled: 1.00, $+0.19 |
| 03:02 | R6 decided | Texas Southern (W) vs. LSU ( | LSU wins by over 6.5 points | 0.99 | 20 | ended 22-131 margin 109 vs 6.5 | kalshi settled: 1.00, $+0.19 |
| 03:02 | R6 decided | Texas Southern (W) vs. LSU ( | LSU wins by over 45.5 points | 0.98 | 20 | ended 22-131 margin 109 vs 45.5 | kalshi settled: 0.00, $-19.63 |
| 03:01 | R6 decided | Texas Southern (W) vs. LSU ( | Over 133.5 points | 0.99 | 20 | score 22-131 total 153 > 133.5 | kalshi settled: 1.00, $+0.19 |
| 03:01 | R6 decided | Texas Southern (W) vs. LSU ( | Over 137.5 points | 0.99 | 20 | score 22-131 total 153 > 137.5 | kalshi settled: 1.00, $+0.19 |
| 03:01 | R6 decided | Texas Southern (W) vs. LSU ( | Over 141.5 points | 0.98 | 20 | score 22-131 total 153 > 141.5 | kalshi settled: 1.00, $+0.37 |
| 03:01 | R6 decided | Texas Southern (W) vs. LSU ( | Over 144.5 points | 0.98 | 20 | score 22-131 total 153 > 144.5 | kalshi settled: 0.00, $-19.63 |
| 03:01 | R6 decided | Texas Southern (W) vs. LSU ( | Over 147.5 points | 0.98 | 20 | score 22-131 total 153 > 147.5 | kalshi settled: 0.00, $-19.63 |

### Score reaction speed (live, 15 s): share of the 3-minute move done by +15 s / +30 s / +60 s

- 26NOV05UTSAFAU 7-20: 0% / 0% / 0%
- 26NOV05UTSAFAU 7-21: -0% / -0% / -0%
- 26NOV05UTSAFAU 7-21: 0% / 0% / 0%
- 26NOV05UTSAFAU 29-50: -0% / 33% / 100%
- 26NOV05SCSTHOW 21-14: -0% / -0% / 29%
- 26NOV05SCSTHOW 21-14: 0% / 0% / 29%
- 26NOV06USFECU 7-3: -0% / -0% / 17%
- 26NOV06USFECU 7-3: 0% / 0% / 0%
- 26NOV06VTSMU 7-20: 0% / 0% / 50%
- 26NOV06VTSMU 7-20: -0% / -0% / 50%
- 26NOV06USFECU 10-17: 0% / 67% / 67%
- 26NOV06NEBILL 6-0: 100% / 100% / 100%
- 26NOV06NEBILL 6-0: 100% / 100% / 100%
- 26NOV06USFECU 10-3: -0% / 2% / 7%
- 26NOV06USFECU 10-3: 0% / 5% / 10%
- 26NOV06USFECU 10-10: -0% / -0% / -0%
- 26NOV06NEBILL 13-21: -0% / 86% / 100%
- 26NOV06NEBILL 13-21: 0% / 100% / 100%
- 26NOV06TCUARIZ 13-10: -0% / -0% / -0%
- 26NOV06TCUARIZ 14-10: -0% / -0% / -0%

## Bot latency map: how long a decided Kalshi market stays mispriced

| sport | series | markets | already priced | mispriced then fixed | median s mispriced | closed/timeout | contradictions | cheapest ask (size) | resting @0.97 contracts / $ | settled right / wrong |
|---|---|---|---|---|---|---|---|---|---|---|
| basketball | KXNCAAMBTOTAL | 562 | 525 | 21 | 2 | 13 | 3 | 0.64 (1210) | 0 / $0.00 | 537 / 13 |
| basketball | KXNCAAWBTOTAL | 434 | 430 | 4 | 89 | 0 | 0 | 0.95 (2) | 0 / $0.00 | 434 / 0 |
| basketball | KXNCAAMBSPREAD | 264 | 256 | 0 | - | 8 | 0 | 0.98 (122) | 0 / $0.00 | 263 / 1 |
| basketball | KXNCAAWBSPREAD | 98 | 98 | 0 | - | 0 | 0 | - | 0 / $0.00 | 98 / 0 |
| soccer | KXUECLTOTAL | 75 | 68 | 7 | 4 | 0 | 0 | 0.80 (2054) | 59 / $1.76 | 68 / 0 |
| soccer | KXUELTOTAL | 72 | 66 | 6 | 6 | 0 | 0 | 0.86 (188) | 875 / $26.24 | 66 / 1 |
| soccer | KXUCLTOTAL | 68 | 64 | 4 | 9 | 0 | 0 | 0.85 (3) | 1491 / $44.71 | 68 / 0 |
| tennis | KXWTASETWINNER | 56 | 53 | 2 | 739 | 1 | 0 | 0.67 (103) | 359 / $10.78 | 55 / 0 |
| tennis | KXATPSETWINNER | 50 | 50 | 0 | - | 0 | 0 | - | 0 / $0.00 | 48 / 0 |
| basketball | KXNCAAWBGAME | 46 | 46 | 0 | - | 0 | 0 | - | 0 / $0.00 | 46 / 0 |
| basketball | KXNCAAMBGAME | 44 | 44 | 0 | - | 0 | 0 | - | 0 / $0.00 | 44 / 0 |
| basketball | KXEUROLEAGUETOTAL | 37 | 35 | 1 | 3 | 0 | 1 | 0.95 (200) | 0 / $0.00 | 33 / 0 |
| soccer | KXUECL1HTOTAL | 33 | 33 | 0 | - | 0 | 0 | - | 0 / $0.00 | 33 / 0 |
| soccer | KXUECLSPREAD | 33 | 33 | 0 | - | 0 | 0 | - | 0 / $0.00 | 33 / 0 |
| soccer | KXARGPREMDIVTOTAL | 25 | 24 | 0 | - | 1 | 0 | 0.01 (69347) | 36724 / $1101.72 | 24 / 1 |
| soccer | KXUCLSPREAD | 24 | 24 | 0 | - | 0 | 0 | - | 0 / $0.00 | 24 / 0 |
| soccer | KXCZEFNLTOTAL | 24 | 24 | 0 | - | 0 | 0 | - | 0 / $0.00 | 24 / 0 |
| football | KXNCAAFTOTAL | 21 | 21 | 0 | - | 0 | 0 | - | 0 / $0.00 | 18 / 0 |
| tennis | KXATPCHALLENGERDOUBLES | 20 | 20 | 0 | - | 0 | 0 | - | 0 / $0.00 | 20 / 0 |
| soccer | KXAPFDDHTOTAL | 20 | 19 | 1 | 3 | 0 | 0 | 0.98 (114) | 0 / $0.00 | 20 / 0 |
| soccer | KXBRASILEIROTOTAL | 17 | 17 | 0 | - | 0 | 0 | - | 0 / $0.00 | 17 / 0 |
| soccer | KXLIGUE2TOTAL | 16 | 15 | 0 | - | 1 | 0 | 0.56 (600) | 48 / $1.44 | 16 / 0 |
| soccer | KXUEL1HTOTAL | 15 | 15 | 0 | - | 0 | 0 | - | 0 / $0.00 | 15 / 0 |
| tennis | KXATPCHALLENGERMATCH | 14 | 14 | 0 | - | 0 | 0 | - | 0 / $0.00 | 14 / 0 |
| soccer | KXUECLGAME | 14 | 14 | 0 | - | 0 | 0 | - | 0 / $0.00 | 14 / 0 |
| soccer | KXBUNDESLIGAWTOTAL | 14 | 14 | 0 | - | 0 | 0 | - | 27 / $0.82 | 14 / 0 |
| soccer | KXBUNDESLIGA2TOTAL | 13 | 13 | 0 | - | 0 | 0 | - | 0 / $0.00 | 13 / 0 |
| basketball | KXEUROLEAGUESPREAD | 12 | 12 | 0 | - | 0 | 0 | - | 0 / $0.00 | 12 / 0 |
| soccer | KXUECL1HBTTS | 11 | 11 | 0 | - | 0 | 0 | - | 0 / $0.00 | 11 / 0 |
| soccer | KXTFF1LIGTOTAL | 11 | 11 | 0 | - | 0 | 0 | - | 0 / $0.00 | 11 / 0 |
| soccer | KXBELGIANPLTOTAL | 10 | 9 | 1 | 2 | 0 | 0 | 0.98 (91) | 0 / $0.00 | 10 / 0 |
| soccer | KXUELBTTS | 10 | 8 | 2 | 62 | 0 | 0 | 0.74 (2475) | 3227 / $96.80 | 9 / 1 |
| soccer | KXUECLBTTS | 9 | 9 | 0 | - | 0 | 0 | - | 0 / $0.00 | 8 / 0 |
| esports | KXCS2TOTALMAPS | 8 | 8 | 0 | - | 0 | 0 | - | 0 / $0.00 | 7 / 0 |
| soccer | KXEFLCHAMPIONSHIPTOTAL | 8 | 8 | 0 | - | 0 | 0 | - | 0 / $0.00 | 8 / 0 |
| football | KXNCAAFGAME | 8 | 7 | 0 | - | 0 | 1 | - | 0 / $0.00 | 8 / 0 |
| soccer | KXAUTBUNDESTOTAL | 8 | 6 | 2 | 4 | 0 | 0 | 0.98 (22) | 0 / $0.00 | 8 / 0 |
| ice-hockey | KXAHLGAME | 8 | 8 | 0 | - | 0 | 0 | - | 0 / $0.00 | 8 / 0 |
| soccer | KXBRASILEIROBTOTAL | 7 | 7 | 0 | - | 0 | 0 | - | 0 / $0.00 | 7 / 0 |
| soccer | KXEKSTRAKLASATOTAL | 7 | 5 | 2 | 30 | 0 | 0 | 0.95 (24) | 0 / $0.00 | 7 / 0 |
| soccer | KXALLSVENSKANTOTAL | 7 | 7 | 0 | - | 0 | 0 | - | 0 / $0.00 | 7 / 0 |
| soccer | KXDIMAYORTOTAL | 7 | 7 | 0 | - | 0 | 0 | - | 0 / $0.00 | 7 / 0 |
| soccer | KXAFCCLTOTAL | 6 | 6 | 0 | - | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| soccer | KXEFLCHAMPIONSHIP1H | 6 | 6 | 0 | - | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| soccer | KXUCLBTTS | 6 | 5 | 1 | 23 | 0 | 0 | 0.92 (0) | 454 / $13.63 | 6 / 0 |
| soccer | KXLIGAEXPTOTAL | 6 | 6 | 0 | - | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| soccer | KXBRASILEIRO1H | 6 | 6 | 0 | - | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| soccer | KXUECL1H | 6 | 6 | 0 | - | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
| soccer | KXIDNSLTOTAL | 6 | 5 | 0 | - | 0 | 1 | - | 0 / $0.00 | 6 / 0 |
| soccer | KXUCLGAME | 5 | 5 | 0 | - | 0 | 0 | - | 0 / $0.00 | 5 / 0 |
| soccer | KXUEL1HBTTS | 5 | 5 | 0 | - | 0 | 0 | - | 0 / $0.00 | 5 / 0 |
| basketball | KXNCAAFTOTAL | 5 | 2 | 0 | - | 3 | 0 | 0.63 (300) | 0 / $0.00 | 0 / 0 |
| soccer | KXROML1TOTAL | 5 | 5 | 0 | - | 0 | 0 | - | 0 / $0.00 | 5 / 0 |
| tennis | KXATPMATCH | 4 | 4 | 0 | - | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
| soccer | KXAPFDDHSPREAD | 4 | 4 | 0 | - | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
| basketball | KXEUROLEAGUEGAME | 4 | 4 | 0 | - | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
| soccer | KXPERLIGA1TOTAL | 4 | 4 | 0 | - | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
| soccer | KXUCL1H | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXUCL1HTOTAL | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXEFLCHAMPIONSHIP1HTOTAL | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| soccer | KXAPFDDHGAME | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| tennis | KXATPEXACTMATCH | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| basketball | KXNCAAFGAME | 3 | 0 | 0 | - | 3 | 0 | 0.79 (144573) | 295 / $8.84 | 0 / 0 |
| soccer | KXBRASILEIROB1HTOTAL | 3 | 3 | 0 | - | 0 | 0 | - | 0 / $0.00 | 3 / 0 |
| esports | KXCS2SPREAD | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| esports | KXCS2GAME | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| basketball | KXCZENBLGAME | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| basketball | KXNBAGAME | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| tennis | KXWTAMATCH | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| basketball | KXJBLEAGUEGAME | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXCZEFLTOTAL | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXUCL1HBTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| basketball | KXEUROCUPTOTAL | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXEFLCHAMPIONSHIP1HBTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXAPFDDHBTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXTFF1LIGBTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXBUNDESLIGAWBTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXEREDIVISIETOTAL | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXEREDIVISIE1HBTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXLIGUE2BTTS | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXSERIECTOTAL | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 1 / 0 |
| soccer | KXLIGAMXTOTAL | 1 | 1 | 0 | - | 0 | 0 | - | 0 / $0.00 | 0 / 0 |

'Already priced' = the book was at 99c+ when we first looked (bots were faster than our score feed). 'Median s mispriced' runs from our decision to the fix. 'Settled right / wrong' checks our certainty against Kalshi's result — any 'wrong' means the score feed or the model failed.

## Decided-state engine (contracts the live score already settled, still trading)

2400 contracts decided while active; 192 had a price leaving > 0.4c after fees; 72 of those were mispriced AFTER the score was stable (lock tier)

| sport | game | contract | decided | reason | max margin | mispriced for | lock margin | lock depth |
|---|---|---|---|---|---|---|---|---|
| basketball | North Dakota State vs. San Franc | KXNCAAFTOTAL-26NOV07NIUSJSU-49 | YES | score 61-70 total 131 > 48.5 | 0.373 | 274s | 0.373 | 609 |
| basketball | Cal Poly vs. Arizona | KXNCAAFTOTAL-26NOV07NAUCP-59 | YES | score 48-67 total 115 > 58.5 | 0.354 | 1791s | 0.354 | 300 |
| basketball | Northern Arizona (W) vs. Arizona | KXNCAAMBTOTAL-26NOV06CSNKSU-163 | NO | ended total 131 <= 162.5 | 0.344 | 589s | 0.344 | 1210 |
| basketball | Northern Arizona (W) vs. Arizona | KXNCAAMBTOTAL-26NOV06CSNKSU-156 | NO | ended total 131 <= 155.5 | 0.315 | 589s | 0.315 | 5 |
| tennis | Anastasia Zakharova vs. Lucrezia | KXWTASETWINNER-26NOV06ZAKSTE-2-STE | NO | set 2 final 5-2 | 0.315 | 210s | 0.315 | 289 |
| tennis | Anastasia Zakharova vs. Lucrezia | KXWTASETWINNER-26NOV06ZAKSTE-2-ZAK | YES | set 2 final 5-2 | 0.305 | 210s | 0.305 | 178 |
| basketball | North Dakota State vs. San Franc | KXNCAAFTOTAL-26NOV07NIUSJSU-46 | YES | score 61-70 total 131 > 45.5 | 0.305 | 274s | 0.305 | 1655 |
| basketball | Cal Poly vs. Arizona | KXNCAAFTOTAL-26NOV07NAUCP-55 | YES | score 48-67 total 115 > 54.5 | 0.246 | 1791s | 0.246 | 200 |
| basketball | North Dakota State vs. San Franc | KXNCAAFTOTAL-26NOV07NIUSJSU-43 | YES | score 61-70 total 131 > 42.5 | 0.246 | 274s | 0.246 | 404 |
| basketball | North Texas (W) vs. San Diego St | KXNCAAFGAME-26NOV07NIUSJSU-SJSU | YES | ended 57-73 | 0.198 | 139s | 0.198 | 144574 |
| basketball | North Dakota State vs. San Franc | KXNCAAFTOTAL-26NOV07NIUSJSU-40 | YES | score 61-70 total 131 > 39.5 | 0.170 | 274s | 0.170 | 14 |
| basketball | Northern Iowa (W) vs. South Dako | KXNCAAFGAME-26NOV07SDSTUNI-UNI | NO | ended 54-76 | 0.151 | 89s | 0.151 | 513 |
| basketball | Northern Iowa (W) vs. South Dako | KXNCAAFGAME-26NOV07SDSTUNI-SDST | YES | ended 54-76 | 0.151 | 89s | 0.151 | 358 |
| basketball | North Dakota State vs. San Franc | KXNCAAFTOTAL-26NOV07NIUSJSU-37 | YES | score 61-70 total 131 > 36.5 | 0.113 | 274s | 0.113 | 450 |
| tennis | Elena Pridankina vs. Alexandra S | KXWTASETWINNER-26NOV05PRISHU-1-SHU | NO | set 1 final 7-6 | 0.989 | 180s | - | 0 |
| tennis | Elena Pridankina vs. Alexandra S | KXWTASETWINNER-26NOV05PRISHU-1-PRI | YES | set 1 final 7-6 | 0.989 | 180s | - | 0 |
| tennis | Nuno Borges vs. Ignacio Buse | KXATPEXACTMATCH-26NOV05BORBUS-BOR21 | YES | ended 6-0, 6-2 | 0.989 | 323s | - | 0 |
| basketball | North Dakota State vs. San Franc | KXNCAAFTOTAL-26NOV07NIUSJSU-73 | YES | score 61-70 total 131 > 72.5 | 0.873 | 274s | - | 0 |
| basketball | Northern Arizona (W) vs. Arizona | KXNCAAMBSPREAD-26NOV06CSNKSU-CSN12 | YES | ended 52-79 margin 27 vs 11.5 | 0.852 | 589s | - | 0 |
| basketball | Arkansas-Monticello (W) vs. Sout | KXNCAAFGAME-26NOV07ULMARST-ULM | YES | ended 64-71 | 0.841 | 743s | - | 0 |
| basketball | Arkansas-Monticello (W) vs. Sout | KXNCAAFGAME-26NOV07ULMARST-ARST | NO | ended 64-71 | 0.841 | 743s | - | 0 |
| basketball | North Dakota State vs. San Franc | KXNCAAFTOTAL-26NOV07NIUSJSU-70 | YES | score 61-70 total 131 > 69.5 | 0.841 | 274s | - | 0 |
| basketball | Northern Arizona (W) vs. Arizona | KXNCAAMBSPREAD-26NOV06CSNKSU-CSN7 | YES | ended 52-79 margin 27 vs 6.5 | 0.831 | 589s | - | 0 |
| basketball | Cal Poly vs. Arizona | KXNCAAFTOTAL-26NOV07NAUCP-51 | YES | score 48-67 total 115 > 50.5 | 0.075 | 1791s | 0.075 | 2500 |
| tennis | Mai Hontama vs. Magda Linette | KXWTASETWINNER-26NOV06HONLIN-1-HON | YES | set 1 final 6-4 | 0.075 | 0s | 0.075 | 1 |

## Close / settlement latency (how clunky each venue is after the final whistle)

Kalshi: settlement_ts − close_time per series (negative = settled before the scheduled close)

| series | n | median | p90 |
|---|---|---|---|
| KXESOCCERGAME eSoccer Game | 4083 | 4.0 min | 4.1 min |
| KXNCAAMBTOTAL Men's College Basketball Total | 1870 | 4.0 min | 4.1 min |
| KXNCAAWBTOTAL Women's College Basketball Tot | 1456 | 2.5 min | 2.6 min |
| KXNCAAMBSPREAD Men's College Basketball Sprea | 1453 | 1.8 min | 1.8 min |
| KXNBAREB NBA Player Rebounds | 1399 | 2.0 min | 2.1 min |
| KXNBA3PT NBA Player Threes | 1345 | 2.0 min | 2.1 min |
| KXNBA3PTPROT NBA Player Threes Protected | 1331 | 2.6 min | 2.6 min |
| KXNBAREBPROT NBA Player Rebounds Protected | 1321 | 2.6 min | 2.6 min |
| KXNBAPTS NBA Player Points | 1137 | 2.0 min | 2.1 min |
| KXNBAPTSPROT NBA Player Points Protected | 1064 | 2.6 min | 2.6 min |
| KXNHLGOAL NHL Goalscorer | 1007 | 3.0 min | 3.1 min |
| KXNBAASTPROT NBA Player Assists Protected | 980 | 2.6 min | 2.6 min |
| KXNBAAST NBA Player Assists | 876 | 2.0 min | 2.1 min |
| KXNHLPTS Pro Hockey Points | 871 | 3.0 min | 3.1 min |
| KXNBAPRA NBA Player Points + Rebounds + | 838 | 2.5 min | 2.6 min |
| KXNBATEAMTOTAL NBA Team Total | 803 | 2.5 min | 2.6 min |
| KXNCAAWBSPREAD Women's College Basketball Spr | 766 | 1.8 min | 1.8 min |
| KXNBASPREAD NBA Spread | 711 | 1.8 min | 1.8 min |
| KXNHLFIRSTGOAL NHL First Goal | 698 | 6.0 min | 6.0 min |
| KXLIGAPROMATCH Russia Liga Pro Match | 694 | 4.0 min | 4.1 min |
| KXNHLAST Pro Hockey Assists | 660 | 6.0 min | 6.1 min |
| KXNBATOTAL NBA Total | 637 | 1.8 min | 1.8 min |
| KXNFLPASSYDSPRECISE Pass Yards Precise | 602 | 4.1 min | 4.1 min |
| KXITFWMATCH ITF Women's Match | 598 | 2.0 min | 2.1 min |
| KXITFMATCH ITF Men's Match | 584 | 2.0 min | 2.1 min |
| KXEBASKETBALLGAME eBasketball Game | 534 | 4.0 min | 4.1 min |
| KXNBA1HTEAMTOTAL NBA 1st Half Team Total | 506 | 2.5 min | 2.6 min |
| KXUELSCORE Correct Score | 484 | 6.1 min | 6.1 min |
| KXUECLSCORE Correct Score | 466 | 6.0 min | 6.1 min |
| KXNBASTL NBA Player Steals | 463 | 2.0 min | 2.1 min |
| KXNBA1HTOTAL NBA 1st Half Total | 437 | 2.5 min | 2.6 min |
| KXNBA1HSPREAD NBA 1st Half Spread | 437 | 2.5 min | 2.6 min |
| KXNBA2HTOTAL NBA 2nd Half Total | 380 | 2.5 min | 2.6 min |
| KXNBA2HSPREAD NBA 2nd Half Spread | 380 | 2.5 min | 2.6 min |
| KXCS2MAP Counter-Strike 2 Map Winner  | 374 | 3.0 min | 3.1 min |
| KXUCLGOAL UCL Goalscorer | 359 | 6.0 min | 6.1 min |
| KXNBA1QTOTAL NBA 1st Quarter Total | 325 | 2.5 min | 2.6 min |
| KXNBA1QSPREAD NBA 1st Quarter Spread | 312 | 2.5 min | 2.6 min |
| KXNFLPOTM NFL Player of the Month | 300 | 5.0 min | 5.1 min |
| KXNBA2QTOTAL NBA 2nd Quarter Total | 299 | 2.5 min | 2.6 min |

## Participant fingerprint (per sport; 60 s snapshots)

change% = share of scan cycles (60 s) where the best quote moved; react = median minutes from a score change to the next quote move (humans: slow, bursty, round sizes; bots: constant cadence, odd/constant sizes, instant reaction)

| venue | sport | markets | snapshots | two-sided | med spread | change% | react (min) | round sizes | med size |
|---|---|---|---|---|---|---|---|---|---|
| pm | tennis | 1504 | 171054 | 93% | 0.010 | 25% | 0.5 (n=93840) | - | - |
| pm | soccer | 900 | 83208 | 86% | 0.010 | 12% | 0.6 (n=996) | - | - |
| pm | esports | 3483 | 82584 | 78% | 0.020 | 17% | 0.5 (n=16913) | - | - |
| pm | golf | 1289 | 61306 | 46% | 0.007 | 10% | - (n=0) | - | - |
| pm | basketball | 706 | 52050 | 68% | 0.030 | 15% | 0.6 (n=10660) | - | - |
| pm | table-tennis | 1693 | 47163 | 90% | 0.010 | 24% | 0.5 (n=23768) | - | - |
| pm | climate | 216 | 11154 | 67% | 0.070 | 27% | - (n=0) | - | - |
| pm | ice-hockey | 59 | 5802 | 88% | 0.060 | 15% | 0.7 (n=267) | - | - |
| pm | cricket | 10 | 2642 | 92% | 0.050 | 9% | 1.0 (n=266) | - | - |
| pm | football | 13 | 2176 | 91% | 0.005 | 17% | 2.3 (n=100) | - | - |
| pm | beach-volleyball | 61 | 2060 | 89% | 0.010 | 20% | 0.5 (n=1046) | - | - |
| pm | macro | 157 | 2042 | 40% | 0.040 | 15% | - (n=0) | - | - |
| pm | pickleball | 140 | 1043 | 75% | 0.210 | 8% | - (n=0) | - | - |
| pm | mma | 2 | 946 | 71% | 0.080 | 3% | - (n=0) | - | - |
| pm | baseball | 3 | 503 | 98% | 0.060 | 34% | 0.5 (n=9) | - | - |
| pm | boxing | 12 | 26 | 100% | 0.045 | 47% | - (n=0) | - | - |
| pm | technology | 9 | 18 | 0% | - | 0% | - (n=0) | - | - |
| k | KXNCAAFGAME College Football Game | 532 | 738723 | 100% | 0.140 | 4% | - | 8% | 15 |
| k | KXNBA3PT NBA Player Threes | 1526 | 247009 | 74% | 0.080 | 18% | - | 32% | 37 |
| k | KXNBAAST NBA Player Assists | 1108 | 160164 | 79% | 0.100 | 18% | - | 29% | 26 |
| k | KXNBAPTS NBA Player Points | 1328 | 137531 | 81% | 0.060 | 23% | - | 28% | 40 |
| k | KXNBAREB NBA Player Rebounds | 1578 | 137450 | 81% | 0.080 | 21% | - | 27% | 36 |
| k | KXNCAAFTEAMTOTAL College Football Team To | 1450 | 111298 | 97% | 0.030 | 2% | - | 28% | 183 |
| k | KXCS2MAP Counter-Strike 2 Map Win | 488 | 108680 | 96% | 0.900 | 5% | - | 25% | 75 |
| k | KXNCAAMBTOTAL Men's College Basketball | 2406 | 108679 | 72% | 0.070 | 11% | - | 21% | 100 |
| k | KXNFLGAME NFL Game | 58 | 99979 | 100% | 0.010 | 1% | - | 4% | 63664 |
| k | KXNCAAMBSPREAD Men's College Basketball | 1807 | 86093 | 70% | 0.070 | 11% | - | 25% | 112 |
| k | KXNBA3PTPROT NBA Player Threes Protec | 1493 | 84104 | 46% | 0.160 | 2% | - | 18% | 25 |
| k | KXNCAAWBTOTAL Women's College Basketba | 1841 | 69181 | 46% | 0.390 | 3% | - | 27% | 35 |
| k | KXNBAPRA NBA Player Points + Rebo | 942 | 66449 | 80% | 0.300 | 17% | - | 12% | 5 |
| k | KXESOCCERGAME eSoccer Game | 4254 | 64812 | 24% | 0.590 | 5% | - | 28% | 37 |
| k | KXNBAASTPROT NBA Player Assists Prote | 1062 | 58581 | 53% | 0.220 | 3% | - | 12% | 5 |
| k | KXNCAAFSPREAD College Football Spread | 2790 | 54729 | 86% | 0.030 | 1% | - | 23% | 533 |
| k | KXUECLSCORE Correct Score | 540 | 46773 | 43% | 0.020 | 9% | - | 22% | 1009 |
| k | KXNBAREBPROT NBA Player Rebounds Prot | 1508 | 46601 | 52% | 0.160 | 3% | - | 17% | 45 |
| k | KXNCAAWBGAME Women's College Basketba | 552 | 44597 | 85% | 0.270 | 6% | - | 16% | 10 |
| k | KXNBAPTSPROT NBA Player Points Protec | 1227 | 44450 | 58% | 0.070 | 4% | - | 12% | 27 |
| k | KXNBA1HTEAMTOTAL NBA 1st Half Team Total | 572 | 42890 | 66% | 0.320 | 17% | - | 36% | 200 |
| k | KXUELSCORE Correct Score | 510 | 40966 | 49% | 0.020 | 9% | - | 13% | 2425 |
| k | KXNBA2HSPREAD NBA 2nd Half Spread | 475 | 40067 | 73% | 0.210 | 30% | - | 40% | 62 |
| k | KXNCAAWBSPREAD Women's College Basketba | 911 | 39808 | 49% | 0.320 | 9% | - | 53% | 30 |
| k | KXNBA2HTOTAL NBA 2nd Half Total | 475 | 37754 | 76% | 0.270 | 27% | - | 44% | 106 |
| k | KXNBA1HTOTAL NBA 1st Half Total | 475 | 37198 | 67% | 0.050 | 15% | - | 26% | 100 |
| k | KXNBA1HSPREAD NBA 1st Half Spread | 494 | 37099 | 67% | 0.050 | 15% | - | 24% | 150 |
| k | KXUCLSCORE Correct Score | 290 | 32618 | 46% | 0.010 | 9% | - | 14% | 2848 |
| k | KXNCAAF1HSPREAD College Football 1st Hal | 1291 | 29645 | 91% | 0.050 | 2% | - | 19% | 237 |
| k | KXNCAAFTOTAL College Football Total P | 1959 | 27943 | 88% | 0.030 | 2% | - | 32% | 356 |
| k | KXNBA3QSPREAD NBA 3rd Quarter Spread | 325 | 27475 | 74% | 0.030 | 22% | - | 62% | 70 |
| k | KXNBA3QTOTAL NBA 3rd Quarter Total | 325 | 27174 | 74% | 0.050 | 23% | - | 52% | 100 |
| k | KXITFWMATCH ITF Women's Match | 692 | 27017 | 77% | 0.020 | 13% | - | 8% | 126 |
| k | KXNBA2QSPREAD NBA 2nd Quarter Spread | 325 | 26554 | 70% | 0.040 | 17% | - | 26% | 100 |
| k | KXITFMATCH ITF Men's Match | 652 | 25901 | 74% | 0.020 | 14% | - | 7% | 148 |
| k | KXNCAAMB1H Men's College Basketball | 252 | 25811 | 50% | 0.060 | 3% | - | 44% | 300 |
| k | KXNCAAMBGAME Men's College Basketball | 456 | 25324 | 75% | 0.020 | 4% | - | 12% | 357 |
| k | KXNBA2QTOTAL NBA 2nd Quarter Total | 325 | 25151 | 70% | 0.050 | 16% | - | 39% | 75 |
| k | KXNBA4QTOTAL NBA 4th Quarter Total | 325 | 23833 | 79% | 0.080 | 30% | - | 59% | 84 |
| k | KXDOTA2MAP Dota 2 Map Winner | 260 | 23205 | 94% | 0.940 | 3% | - | 15% | 100 |

## Schema notes (raw keys seen)

- polymarket: active, archived, category, chatChannel, closed, combos, createdAt, description, elapsed, endDate, ended, eventState, fixtureId, gameId, hidden, id, insiderTradingRules, live, marketCounts, marketGroups, markets, metadata, participants, payoutEstimateMessage, payoutEstimateTime, period, primaryTag, score, seriesSlug, slug, sortType, sportradarGameId, startDate, startTime, streamProvider, streamRequiresAuth, tags, teams, ticker, title, updatedAt
- kalshi: can_close_early, close_time, created_time, custom_strike, early_close_condition, event_ticker, exchange_index, expected_expiration_time, expiration_time, expiration_value, last_price_dollars, latest_expiration_time, market_type, no_ask_dollars, no_bid_dollars, no_sub_title, notional_value_dollars, occurrence_datetime, open_interest_fp, open_time, previous_price_dollars, previous_yes_ask_dollars, previous_yes_bid_dollars, price_level_structure, price_ranges, result, rules_primary, rules_secondary, settlement_bounds_type, settlement_timer_seconds, settlement_ts, settlement_value_dollars, status, strike_type, ticker, title, updated_time, volume_24h_fp, volume_fp, yes_ask_dollars, yes_ask_size_fp, yes_bid_dollars, yes_bid_size_fp, yes_sub_title

