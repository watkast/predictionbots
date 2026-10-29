# Mr. P — gate report

Updated 2026-10-29T12:13:03Z by `run-20261029T1142-40867438788` (last 7 days of data). Read-only recorder — it never places orders.
Kit and docs: `mrp/README.md` on the `mrp` branch. Per-window detail: `mrp/windows.csv`.

```

Mr. P — gate report   records=1,313,961  windows=4  lot=10  errors_logged=2474
data: mrp/data   index sources: {'btc': 'kalshi', 'link': 'kalshi', 'sui': 'kalshi', 'hype': 'kalshi', 'hbar': 'kalshi', 'bch': 'kalshi', 'aave': 'kalshi', 'vvv': 'kalshi', 'xlm': 'kalshi', 'near': 'kalshi', 'ltc': 'kalshi', 'pepeusd_rti': 'kalshi', 'ada': 'kalshi', 'dot': 'kalshi', 'wld': 'kalshi', 'uniusd_rti': 'kalshi', 'xrp': 'kalshi', 'bnb': 'kalshi', 'shib': 'kalshi', 'zec': 'kalshi', 'doge': 'kalshi', 'sol': 'kalshi', 'eth': 'kalshi'}

=== BTC 15-minute   windows=4   index=kalshi   settlement reproduced 0/4
T-left    n  flip%  open% med|d|bps PM ask<=.99  <=.95 entry_ok ok&flip min|d|ok$ PM ask p50 K ask p50 K bid p50 lock>0 maxlock
-------------------------------------------------------------------------------------------------------------------------------
   600    3  66.7%     0%       2.8           0      0        0       0         -          -         -         -      0       -
   300    3  33.3%     0%       5.1           0      0        0       0         -          -         -         -      0       -
   180    4   0.0%    25%       6.4           1      0        1       0        76      0.990         -         -      0       -
   120    4   0.0%   100%       5.8           3      3        2       0        21      0.780         -         -      0       -
    90    4   0.0%   100%       5.2           3      3        3       0        13      0.870         -         -      0       -
    60    4   0.0%   100%       7.2           2      1        0       0         -      0.960         -         -      0       -
    45    4   0.0%   100%       8.6           1      1        0       0         -      0.400         -         -      0       -
    30    4   0.0%   100%       9.5           0      0        0       0         -          -         -         -      0       -
    20    4   0.0%   100%       9.7           0      0        0       0         -          -         -         -      0       -
    15    4   0.0%   100%       9.6           0      0        0       0         -          -         -         -      0       -
    10    4   0.0%   100%       9.3           0      0        0       0         -          -         -         -      0       -
     5    4   0.0%   100%       9.1           0      0        0       0         -          -         -         -      0       -
     3    4   0.0%   100%       8.9           0      0        0       0         -          -         -         -      0       -
     2    4   0.0%   100%       8.9           0      0        0       0         -          -         -         -      0       -
     1    4   0.0%   100%       8.9           0      0        0       0         -          -         -         -      0       -
  index speed (kalshi, 4849 prints): 1s max 29.08 p99.9 14.08 | 5s max 44.25 p99.9 30.42 | 10s max 46.92 p99.9 43.21 | 15s max 57.31 p99.9 52.58 | 30s max 58.37 p99.9 58.14 | 60s max 102.92 p99.9 102.87

Columns: PM = Polymarket US (0.01 ticks, leader ask / count with >= lot contracts), K = Kalshi (0.001 ticks). lock>0 = checkpoints where buying the leader on one venue and selling it on the other cleared both fees.
entry_ok = state OPEN, PM leader ask <= 0.99 with >= lot contracts, positive net. ok&flip must be ZERO with margin before anything goes live.

Polymarket state transitions:
                    None -> OPEN                     before_end  x19
                    None -> HALTED                   before_end  x7
                    OPEN -> CLOSED                    after_end  x5
                  HALTED -> OPEN                     before_end  x2
```
