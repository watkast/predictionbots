# Mr. P — gate report

Updated 2026-10-29T08:32:09Z by `run-20261029T0812-40840427395` (last 7 days of data). Read-only recorder — it never places orders.
Kit and docs: `mrp/README.md` on the `mrp` branch. Per-window detail: `mrp/windows.csv`.

```

Mr. P — gate report   windows=2  lot=10  errors_logged=0
data: mrp/data   csv: mrp/windows.csv

settlement reproduction: our 60-sample average matched the exchange's settlementPrice in 0/2 windows  (anything < 100% means a feed gap or a rule mismatch)

T-left    n  flip%  open%  ask<=99 entry_ok  ok&flip  min|d|ok  med|d| ask p50 ask p90  net/lot
-----------------------------------------------------------------------------------------------
   600    1   0.0%   0.0%        0        0        0         -      58       -       -        -
   300    1   0.0%   0.0%        0        0        0         -      41       -       -        -
   180    2   0.0%   0.0%        0        0        0         -     117       -       -        -
   120    2   0.0% 100.0%        1        1        0        21     113    0.72    0.72     2.66
    90    2   0.0% 100.0%        1        1        0        13     100    0.80    0.80     1.89
    60    2   0.0% 100.0%        1        0        0         -      94    0.40    0.40        -
    45    2   0.0% 100.0%        1        0        0         -      90    0.40    0.40        -
    30    2   0.0% 100.0%        0        0        0         -      91       -       -        -
    20    2   0.0% 100.0%        0        0        0         -      91       -       -        -
    15    2   0.0% 100.0%        0        0        0         -      91       -       -        -
    10    2   0.0% 100.0%        0        0        0         -      92       -       -        -
     5    2   0.0% 100.0%        0        0        0         -      92       -       -        -
     3    2   0.0% 100.0%        0        0        0         -      92       -       -        -
     2    2   0.0% 100.0%        0        0        0         -      92       -       -        -
     1    2   0.0% 100.0%        0        0        0         -      92       -       -        -

flip% = leading side at T-left lost.  entry_ok = state OPEN, leader ask <= 0.99 with >= 10 contracts, positive net after fee (re-run with --min-d to test a settlement-gate threshold).
ok&flip = entries that would have been taken AND lost — this column must be ZERO, with margin, before anything goes live.

BRTI speed (max absolute move observed over a span, $):
    1s  max=    1.31  p99.9=    1.29  p99=   1.16  median=  0.28  (n=1222)
    5s  max=    6.35  p99.9=    6.27  p99=   5.69  median=  1.41  (n=1218)
   10s  max=   12.04  p99.9=   11.91  p99=  11.27  median=  2.82  (n=1213)
   15s  max=   17.42  p99.9=   17.24  p99=  16.54  median=  4.19  (n=1208)
   30s  max=   30.75  p99.9=   30.70  p99=  29.54  median=  7.97  (n=1193)
   60s  max=   55.07  p99.9=   54.71  p99=  52.34  median= 13.77  (n=1163)
  -> a flip at T-left=k needs the remaining k prints to average 60/k x |d| away. Compare need_rem_move in windows.csv to the max k-second move above.

market state transitions seen (from -> to, relative to window end):
                                  None -> MARKET_STATE_OPEN                    before_end  x2
```
