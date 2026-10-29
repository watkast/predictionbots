# Mr. P — gate report

Updated 2026-10-29T11:03:15Z by `run-20261029T1053-40861040693` (last 7 days of data). Read-only recorder — it never places orders.
Kit and docs: `mrp/README.md` on the `mrp` branch. Per-window detail: `mrp/windows.csv`.

```

Mr. P — gate report   windows=4  lot=10  errors_logged=602
data: mrp/data   csv: mrp/windows.csv

settlement reproduction: our 60-sample average matched the exchange's settlementPrice in 0/4 windows  (anything < 100% means a feed gap or a rule mismatch)

T-left    n  flip%  open%  ask<=99 entry_ok  ok&flip  min|d|ok  med|d| ask p50 ask p90  net/lot
-----------------------------------------------------------------------------------------------
   600    3  66.7%   0.0%        0        0        0         -      22       -       -        -
   300    3  33.3%   0.0%        0        0        0         -      41       -       -        -
   180    4   0.0%  25.0%        1        1        0        76      51    0.99    0.99     0.09
   120    4   0.0% 100.0%        3        2        0        21      46    0.78    0.93     1.66
    90    4   0.0% 100.0%        3        3        0        13      42    0.87    0.95     1.22
    60    4   0.0% 100.0%        2        0        0         -      58    0.96    0.96        -
    45    4   0.0% 100.0%        1        0        0         -      69    0.40    0.40        -
    30    4   0.0% 100.0%        0        0        0         -      76       -       -        -
    20    4   0.0% 100.0%        0        0        0         -      77       -       -        -
    15    4   0.0% 100.0%        0        0        0         -      76       -       -        -
    10    4   0.0% 100.0%        0        0        0         -      74       -       -        -
     5    4   0.0% 100.0%        0        0        0         -      73       -       -        -
     3    4   0.0% 100.0%        0        0        0         -      72       -       -        -
     2    4   0.0% 100.0%        0        0        0         -      71       -       -        -
     1    4   0.0% 100.0%        0        0        0         -      71       -       -        -

flip% = leading side at T-left lost.  entry_ok = state OPEN, leader ask <= 0.99 with >= 10 contracts, positive net after fee (re-run with --min-d to test a settlement-gate threshold).
ok&flip = entries that would have been taken AND lost — this column must be ZERO, with margin, before anything goes live.

BRTI speed (max absolute move observed over a span, $):
    1s  max=    2.33  p99.9=    2.18  p99=   1.69  median=  0.31  (n=3029)
    5s  max=   10.92  p99.9=   10.53  p99=   8.25  median=  1.53  (n=3025)
   10s  max=   21.04  p99.9=   20.73  p99=  16.16  median=  3.00  (n=3020)
   15s  max=   30.76  p99.9=   30.63  p99=  24.60  median=  4.50  (n=3015)
   30s  max=   58.37  p99.9=   58.25  p99=  51.11  median=  8.35  (n=3000)
   60s  max=  102.92  p99.9=  102.90  p99=  96.42  median= 14.98  (n=2970)
  -> a flip at T-left=k needs the remaining k prints to average 60/k x |d| away. Compare need_rem_move in windows.csv to the max k-second move above.

market state transitions seen (from -> to, relative to window end):
                                  None -> MARKET_STATE_OPEN                    before_end  x5
                                  None -> MARKET_STATE_HALTED                  before_end  x3
                     MARKET_STATE_OPEN -> MARKET_STATE_CLOSED                   after_end  x2
```
