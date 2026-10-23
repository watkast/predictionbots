# mm_inventory backtest

Generated 2026-10-23 11:18:21 UTC

| strategy | label | net pnl | fees | fills | maker % | max DD | max capital | ret/maxcap | markets | win rate | params |
|---|---|---|---|---|---|---|---|---|---|---|---|
| mm_inventory | base | 5.418 | 0 | 94 | 100 | 0.579 | 7.13 | 0.7599 | 1 | 1 | `{}` |

## Reality flags

| strategy | label | fidelity | events | cross-assumed fills | max fill/touch depth | top-3 market pnl share | pnl/contract |
|---|---|---|---|---|---|---|---|
| mm_inventory | base | L2 | 4348 | 12.8% (12) | 1.0 | 100% | 0.00696 |

Interpretation: a high cross-assumed-fill fraction means most maker fills were inferred from the book moving through our price without a print (adverse assumption, but also the least certain). A max fill/touch-depth ratio > 1 means a single fill exceeded the resting size at the touch at fill time. A top-3 share near 100% means the result is concentrated and probably not robust.
