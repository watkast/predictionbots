# Mr. P — sports radar

Updated 2026-11-07T02:13:38Z by `run-20261107T0022-42312295640` (last 7 days). Read-only scanner of every sports market on Polymarket US and Kalshi — it never places orders.
Kit: `mrp/mrp_sports_radar.py` on the `mrp` branch. Raw tape: `mrp/radar/<run>/`.

# Sports radar report

records 4,557,274 | 2026-11-04 02:12Z → 02:12Z | runs 11 | pairs matched 1386 | errors {'sp.stream': 16, 'radar': 1}

## Catalogue (latest inventory, 00:30Z)

Polymarket US sports events 4653 of 5579 active events; Kalshi near-term sports markets 874 in 376 events; calls so far {'pm': 44, 'k': 487}; MB {'pm': 164711133, 'k': 63249935}

| venue | sport / league / type | markets | two-sided | med spread | vol 24h |
|---|---|---|---|---|---|
| pm | football / nfl / futures | 4104 | 58% | 0.010 | 0 |
| pm | football / cfb / futures | 1643 | 41% | 0.010 | 0 |
| pm | basketball / nba / futures | 1450 | 53% | 0.030 | 0 |
| pm | basketball / cbb / basketball_team_full_game_winner | 806 | 17% | 0.040 | 0 |
| pm | ice-hockey / nhl / futures | 779 | 92% | 0.010 | 0 |
| pm | basketball / wcbb / basketball_team_full_game_winner | 760 | 19% | 0.190 | 0 |
| k | KXNCAAFGAME / College Football Game | 508 | 100% | 0.030 | 6930735 |
| pm | soccer / epl / futures | 437 | 87% | 0.010 | 0 |
| pm | basketball / cbb / futures | 396 | 88% | 0.010 | 0 |
| pm | golf / worlwide / futures | 359 | 14% | 0.003 | 0 |
| pm | tennis / utr / tennis_match_winner | 328 | 6% | 0.010 | 0 |
| pm | soccer / ucl / futures | 285 | 79% | 0.010 | 0 |
| pm | table-tennis / setkameua / table_tennis_match_winner | 246 | 88% | 0.170 | 0 |
| pm | football / cfb / football_team_full_game_winner | 236 | 90% | 0.015 | 0 |
| pm | golf / lpga / futures | 154 | 3% | 0.098 | 0 |
| pm | soccer / lal / futures | 147 | 49% | 0.010 | 0 |
| pm | mma / ufc / futures | 145 | 83% | 0.010 | 0 |
| pm | boxing / boxing / futures | 145 | 0% | - | 0 |
| pm | golf / abudhabc / futures | 140 | 21% | 0.008 | 0 |
| pm | motorsports / f1 / futures | 123 | 18% | 0.025 | 0 |
| pm | macro /  / futures | 123 | 70% | 0.010 | 0 |
| pm | basketball / nba / basketball_team_full_game_winner | 112 | 98% | 0.270 | 0 |
| pm | soccer / sea / futures | 88 | 85% | 0.010 | 0 |
| pm | tennis / atp / futures | 85 | 36% | 0.010 | 0 |
| pm | macro / usgas / futures | 82 | 70% | 0.010 | 0 |
| pm | soccer / bun / futures | 80 | 84% | 0.010 | 0 |
| pm | soccer / lg1 / futures | 79 | 85% | 0.010 | 0 |
| pm | tennis / wta / futures | 75 | 44% | 0.030 | 0 |
| pm | baseball / mlb / futures | 72 | 65% | 0.001 | 0 |
| pm | macro / usdsl / futures | 63 | 21% | 0.200 | 0 |
| pm | soccer / afcq / soccer_team_full_time_winner | 63 | 60% | 0.450 | 0 |
| pm | esports / dota2 / esports_match_winner | 60 | 47% | 0.090 | 0 |
| k | KXNFLGAME / NFL Game | 56 | 100% | 0.010 | 1947601 |
| pm | soccer / unl / soccer_team_full_time_winner | 54 | 100% | 0.035 | 0 |
| pm | table-tennis / czechligapro / table_tennis_match_winner | 54 | 13% | 0.430 | 0 |
| pm | technology /  / futures | 53 | 79% | 0.010 | 0 |
| pm | motorsports / nascar / futures | 52 | 46% | 0.010 | 0 |
| pm | golf / masttour / futures | 52 | 100% | 0.499 | 0 |
| pm | table-tennis / setkamecz / table_tennis_match_winner | 48 | 67% | 0.170 | 0 |
| pm | esports / cs2 / esports_match_winner | 46 | 76% | 0.190 | 0 |
| pm | soccer / mls / soccer_team_full_time_winner | 45 | 100% | 0.010 | 0 |
| pm | tennis / itfwo / tennis_match_winner | 44 | 91% | 0.040 | 0 |
| pm | soccer / mls / futures | 42 | 86% | 0.010 | 0 |
| pm | boxing / boxing / boxing_match_winner | 41 | 76% | 0.080 | 0 |
| pm | soccer / lmx / futures | 36 | 61% | 0.120 | 0 |
| pm | soccer / uel / futures | 36 | 0% | - | 0 |
| pm | soccer / uecl / futures | 36 | 0% | - | 0 |
| pm | table-tennis / setkamemd / table_tennis_match_winner | 36 | 0% | - | 0 |
| pm | tennis / itfme / tennis_match_winner | 35 | 91% | 0.040 | 0 |
| pm | soccer / sercb / soccer_team_full_time_winner | 33 | 91% | 0.040 | 0 |
| pm | soccer / lal2 / soccer_team_full_time_winner | 33 | 91% | 0.040 | 0 |
| pm | soccer / eflch / soccer_team_full_time_winner | 33 | 100% | 0.010 | 0 |
| pm | ice-hockey / ahl / hockey_team_full_game_winner | 32 | 31% | 0.115 | 0 |
| pm | ice-hockey / nhl / hockey_team_full_game_winner | 31 | 100% | 0.010 | 0 |
| pm | soccer / j1 / soccer_team_full_time_winner | 30 | 100% | 0.020 | 0 |
| pm | soccer / j2 / soccer_team_full_time_winner | 30 | 100% | 0.020 | 0 |
| pm | soccer / sercc / soccer_team_full_time_winner | 30 | 100% | 0.035 | 0 |
| pm | soccer / lco / soccer_team_full_time_winner | 30 | 100% | 0.030 | 0 |
| pm | football / nfl / football_team_full_game_winner | 29 | 100% | 0.005 | 0 |
| pm | mma / ufc / ufc_fight_winner | 28 | 96% | 0.010 | 0 |

## Opportunities

| kind | distinct | hits | max margin $/contract | max persistence | fresh-BBO still open |
|---|---|---|---|---|---|
| decided_k | 176 | 3687 | 0.9893 | 35 min | 0/0 |
| decided_pm | 45 | 2383 | 0.9893 | 62 min | 164/247 |
| decided_pm_closed | 29 | 2431 | 0.9893 | 63 min | 2340/2431 |
| dutch_k | 25 | 146 | 0.1123 | 18 min | 0/0 |
| dutch_k_sell | 2 | 3 | 0.0663 | 0 min | 0/0 |
| dutch_pm | 59 | 2755 | 0.5248 | 47 min | 0/0 |
| implication_k | 248 | 3084 | 0.7472 | 12 min | 0/0 |
| lag_k_settled | 155 | 26455 | 0.9947 | 299 min | 23406/24842 |
| lag_k_settled_closed | 158 | 2802 | 0.9947 | 111 min | 128/2802 |

Top by persistence × hits:

- **lag_k_settled** esports — Spirit Academy vs. Xipto Esports — bid 0.37 ask 0.38 buy_yes @ 0.38 | margin 0.7163 | 299 min, 539 hits | fresh bbo 0.37/0.38 depth 23/31 | score 1-1 Live
- **lag_k_settled** football — South Florida vs. East Carolina — bid 0.51 ask 0.52 sell_yes @ 0.51 | margin 0.7008 | 115 min, 491 hits | fresh bbo 0.51/0.52 depth 55/49 | score 10-10 HT
- **lag_k_settled** soccer — Club Universitario de Deportes vs. Sport Boys Association — bid 0.66 ask 0.67 sell_yes @ 0.66 | margin 0.6444 | 121 min, 479 hits | fresh bbo 0.66/0.67 depth 11/7 | score - NS
- **lag_k_settled** soccer — Club Universitario de Deportes vs. Sport Boys Association — bid 0.21 ask 0.23 sell_yes @ 0.21 | margin 0.1985 | 121 min, 479 hits | fresh bbo 0.21/0.23 depth 8/11 | score - NS
- **lag_k_settled** soccer — Club Universitario de Deportes vs. Sport Boys Association — bid 0.12 ask 0.13 sell_yes @ 0.12 | margin 0.1221 | 121 min, 479 hits | fresh bbo 0.12/0.13 depth 8/14 | score - NS
- **lag_k_settled** esports — Spirit Academy Green vs. Fire Flux Esports — bid 0.42 ask 0.43 buy_yes @ 0.43 | margin 0.5530 | 120 min, 479 hits | fresh bbo 0.42/0.43 depth 14/12 | score - NS
- **lag_k_settled** esports — LPH Gaming vs.  Phantom Academy — bid 0.57 ask 0.58 sell_yes @ 0.57 | margin 0.5467 | 120 min, 478 hits | fresh bbo 0.57/0.58 depth 7/8 | score - NS
- **lag_k_settled** basketball — Northern Iowa (W) vs. South Dakota State (W) — bid 0.15 ask 0.16 sell_yes @ 0.15 | margin 0.1379 | 115 min, 458 hits | fresh bbo 0.15/0.16 depth 11/9 | score - NS
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
- **lag_k_settled** esports — eBattles: England (Upcake22) vs. France (mko1919) — bid 0.06 ask 0.09 sell_yes @ 0.06 | margin 0.3146 | 64 min, 259 hits | fresh bbo 0.06/0.09 depth 2/2 | score 4-2 2H
- **lag_k_settled** esports — eBattles: England (Maxa) vs. France (Ganger_29) — bid 0.09 ask 0.10 sell_yes @ 0.09 | margin 0.4427 | 64 min, 256 hits | fresh bbo 0.09/0.10 depth 3/3 | score 0-1 2H
- **lag_k_settled** esports — eBattles: England (Maxa) vs. France (Ganger_29) — bid 0.27 ask 0.28 sell_yes @ 0.27 | margin 0.3342 | 64 min, 256 hits | fresh bbo 0.27/0.28 depth 2/3 | score 0-1 2H

## Live paper trades (no orders; Kalshi prices, taker fees)

Ledger L2-2026-11-01 (earlier ledgers excluded: none)

**Total closed P&L: $+1.58 on $139.42 staked (+1.1%)**

| rule | entries | closed | winners | staked | P&L | ROI |
|---|---|---|---|---|---|---|
| R1 anchor [ncaaf] | 3 | 1 | 1 | $10.18 | $+5.82 | +57% |
| R2 q1cheap [ncaaf] | 7 | 4 | 1 | $20.85 | $+12.15 | +58% |
| R2 q1cheap [nfl] | 1 | 1 | 0 | $5.22 | $-5.22 | -100% |
| R3 blowout [ncaaf] | 1 | 1 | 0 | $21.08 | $-21.08 | -100% |
| R6 decided [other] | 34 | 7 | 7 | $82.09 | $+9.91 | +12% |

| time (UTC) | rule | game | team | entry | contracts | why | result |
|---|---|---|---|---|---|---|---|
| 02:05 | R2 q1cheap | New Mexico vs. Nevada | Nevada | 0.20 | 25 | Q1 ask 0.20, score 0-0 | open |
| 01:52 | R6 decided | Northern Iowa (W) vs. South  | South Dakota St. | 0.84 | 23 | ended 54-76 | final score (pending Kalshi settlement): 1.00, $+3.46 |
| 00:29 | R2 q1cheap | Virginia Tech vs. SMU | Virginia Tech | 0.17 | 29 | Q1 ask 0.17, score 0-7 | open |
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
| 03:02 | R6 decided | Texas Southern (W) vs. LSU ( | LSU wins by over 40.5 points | 0.98 | 20 | ended 22-131 margin 109 vs 40.5 | open |
| 03:02 | R6 decided | Texas Southern (W) vs. LSU ( | LSU wins by over 35.5 points | 0.98 | 20 | ended 22-131 margin 109 vs 35.5 | open |
| 03:02 | R6 decided | Texas Southern (W) vs. LSU ( | LSU wins by over 30.5 points | 0.98 | 20 | ended 22-131 margin 109 vs 30.5 | open |
| 03:02 | R6 decided | Texas Southern (W) vs. LSU ( | LSU wins by over 26.5 points | 0.98 | 20 | ended 22-131 margin 109 vs 26.5 | open |
| 03:02 | R6 decided | Texas Southern (W) vs. LSU ( | LSU wins by over 23.5 points | 0.98 | 20 | ended 22-131 margin 109 vs 23.5 | open |
| 03:02 | R6 decided | Texas Southern (W) vs. LSU ( | LSU wins by over 20.5 points | 0.98 | 20 | ended 22-131 margin 109 vs 20.5 | open |
| 03:02 | R6 decided | Texas Southern (W) vs. LSU ( | LSU wins by over 1.5 points | 0.99 | 20 | ended 22-131 margin 109 vs 1.5 | open |
| 03:02 | R6 decided | Texas Southern (W) vs. LSU ( | LSU wins by over 16.5 points | 0.98 | 20 | ended 22-131 margin 109 vs 16.5 | open |
| 03:02 | R6 decided | Texas Southern (W) vs. LSU ( | LSU wins by over 11.5 points | 0.99 | 20 | ended 22-131 margin 109 vs 11.5 | open |
| 03:02 | R6 decided | Texas Southern (W) vs. LSU ( | LSU | 0.99 | 20 | ended 22-131 | open |
| 03:02 | R6 decided | Texas Southern (W) vs. LSU ( | LSU wins by over 6.5 points | 0.99 | 20 | ended 22-131 margin 109 vs 6.5 | open |
| 03:02 | R6 decided | Texas Southern (W) vs. LSU ( | LSU wins by over 45.5 points | 0.98 | 20 | ended 22-131 margin 109 vs 45.5 | open |
| 03:01 | R6 decided | Texas Southern (W) vs. LSU ( | Over 133.5 points | 0.99 | 20 | score 22-131 total 153 > 133.5 | open |
| 03:01 | R6 decided | Texas Southern (W) vs. LSU ( | Over 137.5 points | 0.99 | 20 | score 22-131 total 153 > 137.5 | open |
| 03:01 | R6 decided | Texas Southern (W) vs. LSU ( | Over 141.5 points | 0.98 | 20 | score 22-131 total 153 > 141.5 | open |
| 03:01 | R6 decided | Texas Southern (W) vs. LSU ( | Over 144.5 points | 0.98 | 20 | score 22-131 total 153 > 144.5 | open |
| 03:01 | R6 decided | Texas Southern (W) vs. LSU ( | Over 147.5 points | 0.98 | 20 | score 22-131 total 153 > 147.5 | open |
| 03:01 | R6 decided | Texas Southern (W) vs. LSU ( | Over 149.5 points | 0.98 | 20 | score 22-131 total 153 > 149.5 | open |
| 03:01 | R6 decided | Texas Southern (W) vs. LSU ( | Over 151.5 points | 0.98 | 20 | score 22-131 total 153 > 151.5 | open |
| 03:00 | R3 blowout | UTSA vs. Florida Atlantic | UTSA | 0.14 | 142 | down 19 in Q3, ask 0.14 | final score (pending Kalshi settlement): 0.00, $-21.08 |
| 02:50 | R6 decided | Texas Southern (W) vs. LSU ( | Over 128.5 points | 0.99 | 20 | score 16-113 total 129 > 128.5 | open |
| 02:48 | R6 decided | Eastern Illinois (W) vs. Iow | Over 115.5 points | 0.93 | 1 | score 39-80 total 119 > 115.5 | open |
| 02:02 | R6 decided | Akron (W) vs. George Mason ( | Over 125.5 points | 0.98 | 1 | score 60-66 total 126 > 125.5 | kalshi settled: 1.00, $+0.02 |
| 02:02 | R6 decided | Eastern Michigan (W) vs. Pur | Over 149.5 points | 0.97 | 1 | score 69-81 total 150 > 149.5 | kalshi settled: 1.00, $+0.03 |
| 01:30 | R1 anchor | UTSA vs. Florida Atlantic | Florida Atlantic | 0.62 | 16 | pregame dog (mid 0.28) leads 7-21 in Q2, ask 0.62 | final score (pending Kalshi settlement): 1.00, $+5.82 |
| 01:19 | R2 q1cheap | JAC Jaguars vs. BAL Ravens | Baltimore | 0.19 | 26 | Q1 ask 0.19, score 0-0 | kalshi settled: 0.00, $-5.22 |
| 01:09 | R2 q1cheap | James Madison vs. Southern M | Southern Miss | 0.18 | 27 | Q1 ask 0.18, score 0-0 | kalshi settled: 0.00, $-5.14 |

### Score reaction speed (live, 15 s): share of the 3-minute move done by +15 s / +30 s / +60 s

- 26NOV05UTSAFAU 7-13: -0% / -0% / -0%
- 26NOV05UTSAFAU 7-13: 0% / 11% / 11%
- 26NOV05UTSAFAU 7-14: -0% / -0% / 40%
- 26NOV05UTSAFAU 7-14: 0% / 0% / 40%
- 26NOV05UTSAFAU 7-20: -0% / -0% / 14%
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
- 26NOV06NEBILL 6-0: 100% / 100% / 100%
- 26NOV06NEBILL 6-0: 100% / 100% / 100%
- 26NOV06USFECU 10-3: -0% / 2% / 7%
- 26NOV06USFECU 10-3: 0% / 5% / 10%
- 26NOV06USFECU 10-10: -0% / -0% / -0%

## Bot latency map: how long a decided Kalshi market stays mispriced

| sport | series | markets | already priced | mispriced then fixed | median s mispriced | closed/timeout | contradictions | cheapest ask (size) | resting @0.97 contracts / $ | settled right / wrong |
|---|---|---|---|---|---|---|---|---|---|---|
| basketball | KXNCAAMBTOTAL | 667 | 630 | 21 | 2 | 13 | 3 | 0.64 (1210) | 0 / $0.00 | 631 / 0 |
| basketball | KXNCAAWBTOTAL | 532 | 527 | 5 | 80 | 0 | 0 | 0.85 (2) | 0 / $0.00 | 532 / 0 |
| basketball | KXNCAAMBSPREAD | 353 | 345 | 0 | - | 8 | 0 | 0.98 (122) | 0 / $0.00 | 342 / 0 |
| basketball | KXNCAAWBSPREAD | 143 | 143 | 0 | - | 0 | 0 | - | 0 / $0.00 | 143 / 0 |
| soccer | KXUECLTOTAL | 75 | 68 | 7 | 4 | 0 | 0 | 0.80 (2054) | 59 / $1.76 | 68 / 0 |
| soccer | KXUELTOTAL | 72 | 66 | 6 | 6 | 0 | 0 | 0.86 (188) | 875 / $26.24 | 66 / 1 |
| soccer | KXUCLTOTAL | 68 | 64 | 4 | 9 | 0 | 0 | 0.85 (3) | 1491 / $44.71 | 68 / 0 |
| basketball | KXNCAAWBGAME | 62 | 62 | 0 | - | 0 | 0 | - | 0 / $0.00 | 62 / 0 |
| tennis | KXWTASETWINNER | 56 | 53 | 2 | 739 | 1 | 0 | 0.67 (103) | 359 / $10.78 | 55 / 0 |
| basketball | KXNCAAMBGAME | 55 | 55 | 0 | - | 0 | 0 | - | 0 / $0.00 | 53 / 0 |
| tennis | KXATPSETWINNER | 50 | 50 | 0 | - | 0 | 0 | - | 0 / $0.00 | 48 / 0 |
| ice-hockey | KXNHLTOTAL | 39 | 39 | 0 | - | 0 | 0 | - | 0 / $0.00 | 39 / 0 |
| basketball | KXEUROLEAGUETOTAL | 37 | 35 | 1 | 3 | 0 | 1 | 0.95 (200) | 0 / $0.00 | 33 / 0 |
| football | KXNCAAFTOTAL | 35 | 35 | 0 | - | 0 | 0 | - | 0 / $0.00 | 35 / 0 |
| soccer | KXUECL1HTOTAL | 33 | 33 | 0 | - | 0 | 0 | - | 0 / $0.00 | 33 / 0 |
| soccer | KXUECLSPREAD | 33 | 33 | 0 | - | 0 | 0 | - | 0 / $0.00 | 33 / 0 |
| soccer | KXUCLSPREAD | 24 | 24 | 0 | - | 0 | 0 | - | 0 / $0.00 | 24 / 0 |
| soccer | KXCZEFNLTOTAL | 24 | 24 | 0 | - | 0 | 0 | - | 0 / $0.00 | 24 / 0 |
| tennis | KXATPCHALLENGERDOUBLES | 20 | 20 | 0 | - | 0 | 0 | - | 0 / $0.00 | 20 / 0 |
| soccer | KXAPFDDHTOTAL | 20 | 19 | 1 | 3 | 0 | 0 | 0.98 (114) | 0 / $0.00 | 20 / 0 |
| soccer | KXARGPREMDIVTOTAL | 18 | 18 | 0 | - | 0 | 0 | - | 0 / $0.00 | 17 / 0 |
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
| soccer | KXAUTBUNDESTOTAL | 8 | 6 | 2 | 4 | 0 | 0 | 0.98 (22) | 0 / $0.00 | 8 / 0 |
| soccer | KXBRASILEIROBTOTAL | 7 | 7 | 0 | - | 0 | 0 | - | 0 / $0.00 | 7 / 0 |
| soccer | KXEKSTRAKLASATOTAL | 7 | 5 | 2 | 30 | 0 | 0 | 0.95 (24) | 0 / $0.00 | 7 / 0 |
| soccer | KXALLSVENSKANTOTAL | 7 | 7 | 0 | - | 0 | 0 | - | 0 / $0.00 | 7 / 0 |
| football | KXNCAAFGAME | 6 | 6 | 0 | - | 0 | 0 | - | 0 / $0.00 | 6 / 0 |
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
| esports | KXCS2GAME | 4 | 4 | 0 | - | 0 | 0 | - | 0 / $0.00 | 4 / 0 |
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
| basketball | KXCZENBLGAME | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| basketball | KXNBAGAME | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| tennis | KXWTAMATCH | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| basketball | KXJBLEAGUEGAME | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
| soccer | KXDIMAYORTOTAL | 2 | 2 | 0 | - | 0 | 0 | - | 0 / $0.00 | 2 / 0 |
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

'Already priced' = the book was at 99c+ when we first looked (bots were faster than our score feed). 'Median s mispriced' runs from our decision to the fix. 'Settled right / wrong' checks our certainty against Kalshi's result — any 'wrong' means the score feed or the model failed.

## Decided-state engine (contracts the live score already settled, still trading)

2831 contracts decided while active; 176 had a price leaving > 0.4c after fees; 65 of those were mispriced AFTER the score was stable (lock tier)

| sport | game | contract | decided | reason | max margin | mispriced for | lock margin | lock depth |
|---|---|---|---|---|---|---|---|---|
| basketball | Cal Poly vs. Arizona | KXNCAAFTOTAL-26NOV07NAUCP-59 | YES | score 48-67 total 115 > 58.5 | 0.354 | 1791s | 0.354 | 300 |
| basketball | Northern Arizona (W) vs. Arizona | KXNCAAMBTOTAL-26NOV06CSNKSU-163 | NO | ended total 131 <= 162.5 | 0.344 | 589s | 0.344 | 1210 |
| basketball | Northern Arizona (W) vs. Arizona | KXNCAAMBTOTAL-26NOV06CSNKSU-156 | NO | ended total 131 <= 155.5 | 0.315 | 589s | 0.315 | 5 |
| tennis | Anastasia Zakharova vs. Lucrezia | KXWTASETWINNER-26NOV06ZAKSTE-2-STE | NO | set 2 final 5-2 | 0.315 | 210s | 0.315 | 289 |
| tennis | Anastasia Zakharova vs. Lucrezia | KXWTASETWINNER-26NOV06ZAKSTE-2-ZAK | YES | set 2 final 5-2 | 0.305 | 210s | 0.305 | 178 |
| basketball | Cal Poly vs. Arizona | KXNCAAFTOTAL-26NOV07NAUCP-55 | YES | score 48-67 total 115 > 54.5 | 0.246 | 1791s | 0.246 | 200 |
| basketball | North Texas (W) vs. San Diego St | KXNCAAFGAME-26NOV07NIUSJSU-SJSU | YES | ended 57-73 | 0.198 | 139s | 0.198 | 144574 |
| basketball | Northern Iowa (W) vs. South Dako | KXNCAAFGAME-26NOV07SDSTUNI-UNI | NO | ended 54-76 | 0.151 | 89s | 0.151 | 513 |
| basketball | Northern Iowa (W) vs. South Dako | KXNCAAFGAME-26NOV07SDSTUNI-SDST | YES | ended 54-76 | 0.151 | 89s | 0.151 | 358 |
| tennis | Elena Pridankina vs. Alexandra S | KXWTASETWINNER-26NOV05PRISHU-1-SHU | NO | set 1 final 7-6 | 0.989 | 180s | - | 0 |
| tennis | Elena Pridankina vs. Alexandra S | KXWTASETWINNER-26NOV05PRISHU-1-PRI | YES | set 1 final 7-6 | 0.989 | 180s | - | 0 |
| tennis | Nuno Borges vs. Ignacio Buse | KXATPEXACTMATCH-26NOV05BORBUS-BOR21 | YES | ended 6-0, 6-2 | 0.989 | 323s | - | 0 |
| basketball | Northern Arizona (W) vs. Arizona | KXNCAAMBSPREAD-26NOV06CSNKSU-CSN12 | YES | ended 52-79 margin 27 vs 11.5 | 0.852 | 589s | - | 0 |
| basketball | Arkansas-Monticello (W) vs. Sout | KXNCAAFGAME-26NOV07ULMARST-ULM | YES | ended 64-71 | 0.841 | 743s | - | 0 |
| basketball | Arkansas-Monticello (W) vs. Sout | KXNCAAFGAME-26NOV07ULMARST-ARST | NO | ended 64-71 | 0.841 | 743s | - | 0 |
| basketball | Northern Arizona (W) vs. Arizona | KXNCAAMBSPREAD-26NOV06CSNKSU-CSN7 | YES | ended 52-79 margin 27 vs 6.5 | 0.831 | 589s | - | 0 |
| basketball | Cal Poly vs. Arizona | KXNCAAFTOTAL-26NOV07NAUCP-51 | YES | score 48-67 total 115 > 50.5 | 0.075 | 1791s | 0.075 | 2500 |
| tennis | Mai Hontama vs. Magda Linette | KXWTASETWINNER-26NOV06HONLIN-1-HON | YES | set 1 final 6-4 | 0.075 | 0s | 0.075 | 1 |
| basketball | Northern Arizona (W) vs. Arizona | KXNCAAMBGAME-26NOV06CSNKSU-CSN | YES | ended 52-79 | 0.799 | 589s | - | 0 |
| basketball | Northern Arizona (W) vs. Arizona | KXNCAAMBSPREAD-26NOV06CSNKSU-CSN2 | YES | ended 52-79 margin 27 vs 1.5 | 0.758 | 589s | - | 0 |
| basketball | Eastern Illinois (W) vs. Iowa (W | KXNCAAMBTOTAL-26NOV06EIUIOWA-116 | YES | score 39-80 total 119 > 115.5 | 0.065 | 255s | 0.065 | 1 |
| basketball | Cal Poly vs. Arizona | KXNCAAFTOTAL-26NOV07NAUCP-83 | YES | score 48-67 total 115 > 82.5 | 0.706 | 1791s | - | 0 |
| basketball | Cal Poly vs. Arizona | KXNCAAFTOTAL-26NOV07NAUCP-79 | YES | score 48-67 total 115 > 78.5 | 0.644 | 1791s | - | 0 |
| soccer | Madura United vs. Arema FC | KXIDNSLTOTAL-26NOV06MAUARE-3 | YES | score 3-0 total 3 > 2.5 | 0.644 | 90s | - | 0 |
| basketball | Cal Poly vs. Arizona | KXNCAAFTOTAL-26NOV07NAUCP-71 | YES | score 48-67 total 115 > 70.5 | 0.624 | 1791s | - | 0 |

## Close / settlement latency (how clunky each venue is after the final whistle)

Kalshi: settlement_ts − close_time per series (negative = settled before the scheduled close)

| series | n | median | p90 |
|---|---|---|---|
| KXESOCCERGAME eSoccer Game | 4074 | 4.0 min | 4.1 min |
| KXNCAAWBTOTAL Women's College Basketball Tot | 1499 | 2.5 min | 2.6 min |
| KXNHLGOAL NHL Goalscorer | 1465 | 3.0 min | 3.1 min |
| KXNCAAMBTOTAL Men's College Basketball Total | 1355 | 4.0 min | 4.1 min |
| KXNHLPTS Pro Hockey Points | 1208 | 3.0 min | 3.1 min |
| KXNCAAMBSPREAD Men's College Basketball Sprea | 1080 | 1.8 min | 1.8 min |
| KXNBA3PTPROT NBA Player Threes Protected | 973 | 2.5 min | 2.6 min |
| KXNBAREB NBA Player Rebounds | 972 | 2.0 min | 2.1 min |
| KXNHLAST Pro Hockey Assists | 961 | 6.0 min | 6.1 min |
| KXNBA3PT NBA Player Threes | 943 | 2.0 min | 2.1 min |
| KXNHLFIRSTGOAL NHL First Goal | 914 | 6.0 min | 6.0 min |
| KXNBAREBPROT NBA Player Rebounds Protected | 911 | 2.5 min | 2.6 min |
| KXNBAPTS NBA Player Points | 836 | 2.0 min | 2.1 min |
| KXNCAAWBSPREAD Women's College Basketball Spr | 808 | 1.8 min | 1.8 min |
| KXNBAPTSPROT NBA Player Points Protected | 763 | 2.6 min | 2.6 min |
| KXNBAASTPROT NBA Player Assists Protected | 689 | 2.6 min | 2.6 min |
| KXLIGAPROMATCH Russia Liga Pro Match | 688 | 4.0 min | 4.1 min |
| KXITFWMATCH ITF Women's Match | 616 | 2.0 min | 2.1 min |
| KXNFLPASSYDSPRECISE Pass Yards Precise | 602 | 4.1 min | 4.1 min |
| KXITFMATCH ITF Men's Match | 594 | 2.0 min | 2.1 min |
| KXNBAPRA NBA Player Points + Rebounds + | 588 | 2.5 min | 2.6 min |
| KXNBAAST NBA Player Assists | 572 | 2.0 min | 2.1 min |
| KXEBASKETBALLGAME eBasketball Game | 534 | 4.0 min | 4.1 min |
| KXNBATEAMTOTAL NBA Team Total | 514 | 2.5 min | 2.6 min |
| KXUELSCORE Correct Score | 484 | 6.1 min | 6.1 min |
| KXNBASPREAD NBA Spread | 468 | 1.8 min | 1.8 min |
| KXUECLSCORE Correct Score | 466 | 6.0 min | 6.1 min |
| KXNBATOTAL NBA Total | 425 | 1.8 min | 1.8 min |
| KXNBA1HTEAMTOTAL NBA 1st Half Team Total | 396 | 2.5 min | 2.6 min |
| KXCS2MAP Counter-Strike 2 Map Winner  | 382 | 3.0 min | 3.1 min |
| KXUCLGOAL UCL Goalscorer | 359 | 6.0 min | 6.1 min |
| KXNBA1HTOTAL NBA 1st Half Total | 342 | 2.5 min | 2.6 min |
| KXNBA1HSPREAD NBA 1st Half Spread | 342 | 2.5 min | 2.6 min |
| KXNBASTL NBA Player Steals | 321 | 2.0 min | 2.1 min |
| KXNFLPOTM NFL Player of the Month | 300 | 5.0 min | 5.1 min |
| KXNBA1QTOTAL NBA 1st Quarter Total | 299 | 2.5 min | 2.6 min |
| KXUCLSCORE Correct Score | 290 | 6.0 min | 6.1 min |
| KXNBA1QSPREAD NBA 1st Quarter Spread | 286 | 2.5 min | 2.6 min |
| KXCS2GAME Counter-Strike 2 Game | 276 | 3.0 min | 3.0 min |
| KXNHLTOTAL NHL Total Goals | 266 | 1.8 min | 1.8 min |

## Participant fingerprint (per sport; 60 s snapshots)

change% = share of scan cycles (60 s) where the best quote moved; react = median minutes from a score change to the next quote move (humans: slow, bursty, round sizes; bots: constant cadence, odd/constant sizes, instant reaction)

| venue | sport | markets | snapshots | two-sided | med spread | change% | react (min) | round sizes | med size |
|---|---|---|---|---|---|---|---|---|---|
| pm | tennis | 1510 | 174391 | 93% | 0.010 | 25% | 0.5 (n=95096) | - | - |
| pm | esports | 3441 | 82497 | 78% | 0.020 | 17% | 0.5 (n=16843) | - | - |
| pm | soccer | 768 | 79671 | 86% | 0.010 | 12% | 0.6 (n=976) | - | - |
| pm | golf | 1289 | 61306 | 46% | 0.007 | 10% | - (n=0) | - | - |
| pm | basketball | 715 | 49274 | 69% | 0.030 | 15% | 0.6 (n=10119) | - | - |
| pm | table-tennis | 1664 | 47579 | 90% | 0.010 | 24% | 0.5 (n=23951) | - | - |
| pm | climate | 216 | 11088 | 67% | 0.070 | 26% | - (n=0) | - | - |
| pm | ice-hockey | 69 | 5579 | 88% | 0.060 | 14% | 0.7 (n=257) | - | - |
| pm | cricket | 9 | 2575 | 92% | 0.040 | 10% | 1.0 (n=276) | - | - |
| pm | beach-volleyball | 58 | 2053 | 89% | 0.010 | 20% | 0.5 (n=1046) | - | - |
| pm | macro | 157 | 2042 | 40% | 0.040 | 15% | - (n=0) | - | - |
| pm | football | 14 | 1973 | 92% | 0.005 | 19% | 2.1 (n=94) | - | - |
| pm | pickleball | 144 | 1047 | 75% | 0.210 | 8% | - (n=0) | - | - |
| pm | mma | 2 | 914 | 73% | 0.080 | 3% | - (n=0) | - | - |
| pm | baseball | 3 | 505 | 98% | 0.060 | 35% | 0.5 (n=9) | - | - |
| pm | technology | 9 | 18 | 0% | - | 0% | - (n=0) | - | - |
| k | KXNCAAFGAME College Football Game | 534 | 728548 | 100% | 0.140 | 4% | - | 8% | 15 |
| k | KXNBA3PT NBA Player Threes | 1511 | 204589 | 75% | 0.090 | 18% | - | 32% | 39 |
| k | KXNCAAFTEAMTOTAL College Football Team To | 1478 | 168889 | 97% | 0.040 | 2% | - | 29% | 121 |
| k | KXNBAAST NBA Player Assists | 1090 | 138790 | 80% | 0.100 | 18% | - | 29% | 26 |
| k | KXNBAPTS NBA Player Points | 1306 | 123498 | 83% | 0.060 | 23% | - | 28% | 40 |
| k | KXNBAREB NBA Player Rebounds | 1537 | 118563 | 83% | 0.080 | 20% | - | 27% | 37 |
| k | KXCS2MAP Counter-Strike 2 Map Win | 496 | 117196 | 96% | 0.910 | 5% | - | 24% | 75 |
| k | KXNCAAMBTOTAL Men's College Basketball | 2595 | 116855 | 77% | 0.060 | 11% | - | 20% | 100 |
| k | KXNFLGAME NFL Game | 58 | 99182 | 100% | 0.010 | 1% | - | 4% | 62047 |
| k | KXNCAAMBSPREAD Men's College Basketball | 2004 | 93238 | 75% | 0.060 | 11% | - | 24% | 116 |
| k | KXNCAAFSPREAD College Football Spread | 2815 | 81271 | 87% | 0.030 | 1% | - | 25% | 500 |
| k | KXNCAAWBTOTAL Women's College Basketba | 2102 | 75083 | 45% | 0.390 | 3% | - | 26% | 36 |
| k | KXNBA3PTPROT NBA Player Threes Protec | 1481 | 70015 | 47% | 0.150 | 2% | - | 19% | 28 |
| k | KXESOCCERGAME eSoccer Game | 4188 | 64485 | 23% | 0.590 | 5% | - | 28% | 37 |
| k | KXNCAAWBGAME Women's College Basketba | 602 | 54398 | 86% | 0.290 | 6% | - | 19% | 10 |
| k | KXNBAPRA NBA Player Points + Rebo | 936 | 53719 | 82% | 0.300 | 17% | - | 12% | 5 |
| k | KXNBAASTPROT NBA Player Assists Prote | 1054 | 50369 | 54% | 0.190 | 3% | - | 13% | 6 |
| k | KXNCAAFTOTAL College Football Total P | 1977 | 47432 | 87% | 0.030 | 1% | - | 30% | 302 |
| k | KXNCAAF1HSPREAD College Football 1st Hal | 1311 | 46781 | 95% | 0.070 | 2% | - | 26% | 15 |
| k | KXUECLSCORE Correct Score | 540 | 46773 | 43% | 0.020 | 9% | - | 22% | 1009 |
| k | KXNCAAWBSPREAD Women's College Basketba | 1073 | 42906 | 47% | 0.320 | 8% | - | 51% | 30 |
| k | KXUELSCORE Correct Score | 510 | 40966 | 49% | 0.020 | 9% | - | 13% | 2425 |
| k | KXNBAREBPROT NBA Player Rebounds Prot | 1482 | 40058 | 56% | 0.160 | 3% | - | 17% | 79 |
| k | KXNBAPTSPROT NBA Player Points Protec | 1220 | 38357 | 61% | 0.070 | 3% | - | 12% | 44 |
| k | KXNBA1HTEAMTOTAL NBA 1st Half Team Total | 550 | 37012 | 67% | 0.350 | 18% | - | 36% | 200 |
| k | KXNHLGOAL NHL Goalscorer | 1677 | 34199 | 27% | 0.090 | 8% | - | 15% | 9 |
| k | KXNBA1HTOTAL NBA 1st Half Total | 475 | 32705 | 69% | 0.050 | 16% | - | 25% | 100 |
| k | KXUCLSCORE Correct Score | 290 | 32618 | 46% | 0.010 | 9% | - | 14% | 2848 |
| k | KXNBA1HSPREAD NBA 1st Half Spread | 475 | 32560 | 69% | 0.050 | 16% | - | 24% | 135 |
| k | KXITFWMATCH ITF Women's Match | 710 | 32310 | 80% | 0.020 | 11% | - | 8% | 120 |
| k | KXNCAAF1HTOTAL College Football 1st Hal | 867 | 32093 | 95% | 0.070 | 2% | - | 22% | 55 |
| k | KXNBA2HSPREAD NBA 2nd Half Spread | 475 | 31587 | 74% | 0.250 | 29% | - | 39% | 73 |
| k | KXNCAAMBGAME Men's College Basketball | 486 | 31232 | 79% | 0.020 | 3% | - | 11% | 324 |
| k | KXNBA2HTOTAL NBA 2nd Half Total | 456 | 29891 | 77% | 0.340 | 27% | - | 41% | 166 |
| k | KXNCAAF1H College Football 1st Hal | 786 | 28275 | 99% | 0.890 | 1% | - | 58% | 300 |
| k | KXNCAAMB1H Men's College Basketball | 276 | 27095 | 49% | 0.060 | 3% | - | 43% | 300 |
| k | KXITFMATCH ITF Men's Match | 658 | 26731 | 74% | 0.020 | 14% | - | 7% | 145 |
| k | KXDOTA2MAP Dota 2 Map Winner | 260 | 23205 | 94% | 0.940 | 3% | - | 15% | 100 |
| k | KXNBA3QSPREAD NBA 3rd Quarter Spread | 325 | 22819 | 77% | 0.040 | 23% | - | 62% | 60 |
| k | KXNBA2QSPREAD NBA 2nd Quarter Spread | 325 | 22807 | 72% | 0.040 | 18% | - | 25% | 85 |

## Schema notes (raw keys seen)

- polymarket: active, archived, category, chatChannel, closed, combos, createdAt, description, elapsed, endDate, ended, eventState, fixtureId, gameId, hidden, id, insiderTradingRules, live, marketCounts, marketGroups, markets, metadata, participants, payoutEstimateMessage, payoutEstimateTime, period, primaryTag, score, seriesSlug, slug, sortType, sportradarGameId, startDate, startTime, streamProvider, streamRequiresAuth, tags, teams, ticker, title, updatedAt
- kalshi: can_close_early, close_time, created_time, custom_strike, early_close_condition, event_ticker, exchange_index, expected_expiration_time, expiration_time, expiration_value, last_price_dollars, latest_expiration_time, market_type, no_ask_dollars, no_bid_dollars, no_sub_title, notional_value_dollars, occurrence_datetime, open_interest_fp, open_time, previous_price_dollars, previous_yes_ask_dollars, previous_yes_bid_dollars, price_level_structure, price_ranges, result, rules_primary, rules_secondary, settlement_bounds_type, settlement_timer_seconds, settlement_ts, settlement_value_dollars, status, strike_type, ticker, title, updated_time, volume_24h_fp, volume_fp, yes_ask_dollars, yes_ask_size_fp, yes_bid_dollars, yes_bid_size_fp, yes_sub_title

