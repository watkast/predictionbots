# Mr. P — gate report

Updated 2026-10-29T08:22:07Z by `run-20261029T0812-40840427395` (last 7 days of data). Read-only recorder — it never places orders.
Kit and docs: `mrp/README.md` on the `mrp` branch. Per-window detail: `mrp/windows.csv`.

```

Mr. P — gate report   windows=1  lot=10  errors_logged=0
data: mrp/data   csv: mrp/windows.csv

settlement reproduction: our 60-sample average matched the exchange's settlementPrice in 0/1 windows  (anything < 100% means a feed gap or a rule mismatch)

T-left    n  flip%  open%  ask<=99 entry_ok  ok&flip  min|d|ok  med|d| ask p50 ask p90  net/lot
-----------------------------------------------------------------------------------------------
   180    1   0.0%   0.0%        0        0        0         -     218       -       -        -
   120    1   0.0% 100.0%        0        0        0         -     205       -       -        -
    90    1   0.0% 100.0%        0        0        0         -     186       -       -        -
    60    1   0.0% 100.0%        0        0        0         -     185       -       -        -
    45    1   0.0% 100.0%        0        0        0         -     178       -       -        -
    30    1   0.0% 100.0%        0        0        0         -     172       -       -        -
    20    1   0.0% 100.0%        0        0        0         -     168       -       -        -
    15    1   0.0% 100.0%        0        0        0         -     166       -       -        -
    10    1   0.0% 100.0%        0        0        0         -     164       -       -        -
     5    1   0.0% 100.0%        0        0        0         -     162       -       -        -
     3    1   0.0% 100.0%        0        0        0         -     161       -       -        -
     2    1   0.0% 100.0%        0        0        0         -     161       -       -        -
     1    1   0.0% 100.0%        0        0        0         -     160       -       -        -

flip% = leading side at T-left lost.  entry_ok = state OPEN, leader ask <= 0.99 with >= 10 contracts, positive net after fee (re-run with --min-d to test a settlement-gate threshold).
ok&flip = entries that would have been taken AND lost — this column must be ZERO, with margin, before anything goes live.

BRTI speed (max absolute move observed over a span, $):
    1s  max=    1.27  p99.9=    1.27  p99=   1.13  median=  0.35  (n=619)
    5s  max=    5.96  p99.9=    5.96  p99=   5.67  median=  1.73  (n=615)
   10s  max=   11.67  p99.9=   11.67  p99=  11.14  median=  3.60  (n=610)
   15s  max=   16.83  p99.9=   16.83  p99=  16.30  median=  5.31  (n=605)
   30s  max=   28.75  p99.9=   28.75  p99=  28.41  median= 10.07  (n=590)
   60s  max=   45.13  p99.9=   45.13  p99=  44.37  median= 18.85  (n=560)
  -> a flip at T-left=k needs the remaining k prints to average 60/k x |d| away. Compare need_rem_move in windows.csv to the max k-second move above.

market state transitions seen (from -> to, relative to window end):
                                  None -> MARKET_STATE_OPEN                    before_end  x2
```
