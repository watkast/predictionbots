# mm_inventory backtest

Generated 2026-10-17 06:19:50 UTC

| strategy | label | net pnl | fees | fills | maker % | max DD | max capital | ret/maxcap | markets | win rate | params |
|---|---|---|---|---|---|---|---|---|---|---|---|
| mm_inventory | base | 34.5 | 0 | 1267 | 100 | 19.96 | 642 | 0.0537 | 1 | 1 | `{}` |

## Reality flags

| strategy | label | fidelity | events | cross-assumed fills | max fill/touch depth | top-3 market pnl share | pnl/contract |
|---|---|---|---|---|---|---|---|
| mm_inventory | base | L2 | 4348 | 61.0% (773) | 0.831 | 100% | 0.00333 |

Interpretation: a high cross-assumed-fill fraction means most maker fills were inferred from the book moving through our price without a print (adverse assumption, but also the least certain). A max fill/touch-depth ratio > 1 means a single fill exceeded the resting size at the touch at fill time. A top-3 share near 100% means the result is concentrated and probably not robust.
