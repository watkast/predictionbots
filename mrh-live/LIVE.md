# Mr. H — Coinbase hopper, LIVE (real money, maker on every order)

Updated 2026-11-08T06:45:16Z · cycles 361 · universe 113 coins · profile aggressive (+5% impulse, 3× volume, 8% trail) · post-only limit orders at the touch (maker 0.5%) · entry TTL 15 min, chase cap +2% · disaster stop 6% under the trail · panic sell 3% under it · caps $200.00/entry, 4 hops/day, floor $1.20, swap after 2 h

**HALTED: floor: $0.00 < $1.20** — remove mrh/LIVE_ON, fix, delete `halted` in live_state.json on the data branch, restore.

## Book

| now | start | deposits | P&L | peak | USD free | hops | win % | fees paid | position / order |
|---|---|---|---|---|---|---|---|---|---|
| $6.92 | $3.44 | $-7.23 | $+10.71 (+311.0%) | $17.73 | $0.00 | 6 | 50% | $0.609 | CAP 69 @ 0.10315 · hw 0.10405 · stop 0.095726 · disaster 0.089483 parked |

## Hops

| time (UTC) | coin | in | out | held | net | fee | reason |
|---|---|---|---|---|---|---|---|
| 11-07T06:40 | ZEC | 1326.04 | 1303.65 | 358 m | -2.57% ($-0.089) | $0.030  | stop |
| 11-07T09:50 | CT | 0.134642 | 0.139278 | 80 m | +1.60% ($+0.053) | $0.031  | stop |
| 11-07T11:45 | ICNT | 0.3088 | 0.3311 | 25 m | +5.31% ($+0.409) | $0.074  | stop |
| 11-07T15:15 | ALIGN | 0.0043 | 0.00412 | 115 m | -5.90% ($-0.479) | $0.069  | stop |
| 11-07T16:15 | RITUAL | 0.02645 | 0.02537 | 40 m | -5.79% ($-0.442) | $0.065  | stop |
| 11-07T19:50 | RITUAL | 0.02404 | 0.02444 | 125 m | +0.25% ($+0.018) | $0.036  | stop |

## Last 25 events

- `11-07T13:20:31` **order_sent** label="park_stop", pid="ALIGN-USD", side="SELL", cfg={"stop_limit_stop_limit_gtc": {"base_size": "1874", "limit_p, order_id="e85804f1-c1d7-4f26-be17-0e4a92904787"
- `11-07T15:15:15` **sold** pid="ALIGN-USD", px=0.00412, net=-0.4793, net_pct=-0.059, reason="stop"
- `11-07T15:35:15` **signal** pid="RITUAL-USD", candle_start=1794065400, impulse=0.0305, vol_mult=4.16, above_2h_high=false, close=0.02635, bid=0.02643, ask=0.02645, spread=0.0008
- `11-07T15:35:34` **order_sent** label="buy", pid="RITUAL-USD", side="BUY", cfg={"market_market_ioc": {"quote_size": "7.65567"}}, order_id="fd9abb19-3649-4d87-b049-9b410d9f6c41"
- `11-07T15:35:35` **bought** pid="RITUAL-USD", px=0.02645, qty=286.0, cost=7.6328
- `11-07T15:35:36` **order_sent** label="park_stop", pid="RITUAL-USD", side="SELL", cfg={"stop_limit_stop_limit_gtc": {"base_size": "286", "limit_pr, order_id="d4919e89-db58-4f48-8793-878f56985812"
- `11-07T15:40:16` **order_sent** label="park_stop", pid="RITUAL-USD", side="SELL", cfg={"stop_limit_stop_limit_gtc": {"base_size": "286", "limit_pr, order_id="927eec6d-8a26-4df8-baeb-381b49d61634"
- `11-07T16:15:15` **sold** pid="RITUAL-USD", px=0.02537, net=-0.4423, net_pct=-0.0579, reason="stop"
- `11-07T17:28:28` **start** mode="live", key="1957dba3ea6c", alg="EdDSA", max_usd=200.0, floor=1.2, max_hops_day=6
- `11-07T17:45:15` **signal** pid="RITUAL-USD", candle_start=1794073200, impulse=0.032, vol_mult=3.59, above_2h_high=false, close=0.0242, bid=0.02402, ask=0.02404, spread=0.0008
- `11-07T17:45:30` **order_sent** label="buy", pid="RITUAL-USD", side="BUY", cfg={"market_market_ioc": {"quote_size": "7.2134"}}, order_id="26858cde-aa0d-4b1e-beb6-bdc2a1c47ebe"
- `11-07T17:45:31` **bought** pid="RITUAL-USD", px=0.02404, qty=297.0, cost=7.2041
- `11-07T17:45:31` **order_sent** label="park_stop", pid="RITUAL-USD", side="SELL", cfg={"stop_limit_stop_limit_gtc": {"base_size": "297", "limit_pr, order_id="8caa2381-6c0f-400b-bf8e-cb148d4b8633"
- `11-07T18:05:16` **order_sent** label="park_stop", pid="RITUAL-USD", side="SELL", cfg={"stop_limit_stop_limit_gtc": {"base_size": "297", "limit_pr, order_id="9e4366fa-c52a-4517-acbe-aea9fbd0f6de"
- `11-07T18:25:16` **order_sent** label="park_stop", pid="RITUAL-USD", side="SELL", cfg={"stop_limit_stop_limit_gtc": {"base_size": "297", "limit_pr, order_id="b3dc3fda-4f71-411a-90ec-8aa0479dca5f"
- `11-07T19:05:16` **order_sent** label="park_stop", pid="RITUAL-USD", side="SELL", cfg={"stop_limit_stop_limit_gtc": {"base_size": "297", "limit_pr, order_id="971566fe-dba1-4ae8-a299-21c34b8dec74"
- `11-07T19:25:16` **order_sent** label="park_stop", pid="RITUAL-USD", side="SELL", cfg={"stop_limit_stop_limit_gtc": {"base_size": "297", "limit_pr, order_id="c132ee80-e225-4354-b7fd-7802ae58301a"
- `11-07T19:50:15` **sold** pid="RITUAL-USD", px=0.02444, net=0.0182, net_pct=0.0025, reason="stop"
- `11-07T23:30:02` **start** mode="live", key="1957dba3ea6c", alg="EdDSA", max_usd=200.0, floor=1.2, max_hops_day=4, maker=true, fast_s=20.0, entry_ttl_min=15.0, entry_chase=0.02, disaster_gap=0.06, panic_gap=0.03, impulse=0.05, vol_mult=3.0, trail=0.08
- `11-08T01:25:15` **cash_flow** amount=-7.23, usd=0.0017, total_flows=-7.23
- `11-08T01:25:15` **halted** reason="floor: $0.00 < $1.20"
- `11-08T01:30:16` **adopted** pid="CAP-USD", qty=69.0, entry_px=0.10315, value=7.12, stop=false, exit=false
- `11-08T01:30:16` **order_sent** label="park_stop", pid="CAP-USD", side="SELL", cfg={"stop_limit_stop_limit_gtc": {"base_size": "69", "limit_pri, order_id="30ca1f54-d55b-4df8-b541-5ddcf2eb7907"
- `11-08T01:35:16` **order_sent** label="park_stop", pid="CAP-USD", side="SELL", cfg={"stop_limit_stop_limit_gtc": {"base_size": "69", "limit_pri, order_id="476fdc8d-d16b-436b-817d-b6e9dd533608"
- `11-08T05:02:48` **start** mode="live", key="1957dba3ea6c", alg="EdDSA", max_usd=200.0, floor=1.2, max_hops_day=4, maker=true, fast_s=20.0, entry_ttl_min=15.0, entry_chase=0.02, disaster_gap=0.06, panic_gap=0.03, impulse=0.05, vol_mult=3.0, trail=0.08

Paper twin: mrh/MRH.md · the 30-day replay (the real verdict): mrh-backtest/BACKTEST.md on this branch.

