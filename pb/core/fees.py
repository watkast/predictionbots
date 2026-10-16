"""Fee models. All functions return dollars for a fill of `size` contracts at
probability-price `p`. Positive = fee paid, negative = rebate received.

Sources (Oct 2026):
- Kalshi: taker = ceil(M * 0.07 * C * P * (1-P)) rounded up to the cent per order;
  maker = ceil(M_m * 0.0175 * C * P * (1-P)) ONLY on series with
  fee_type == quadratic_with_maker_fees (mostly sports + econ). Crypto 15-min,
  hourly and daily weather series currently have NO maker fee.
- Polymarket: taker fee = C * rate * p * (1-p), maker pays 0, maker rebate pool
  per category (we conservatively ignore the rebate unless explicitly enabled).
  Rates: crypto 0.07, sports 0.05, econ/culture/weather/other 0.05,
  politics/finance/tech/mentions 0.04, geopolitics 0.
"""
from __future__ import annotations

import math
from dataclasses import dataclass


def _ceil_cents(x: float) -> float:
    return math.ceil(x * 100 - 1e-9) / 100


@dataclass(frozen=True)
class FeeSchedule:
    taker_rate: float          # coefficient on C*p*(1-p)
    maker_rate: float = 0.0    # coefficient on C*p*(1-p); 0 => free
    maker_rebate_frac: float = 0.0  # fraction of taker-equivalent fee rebated to maker (Polymarket pools)
    round_up_cents: bool = True      # Kalshi rounds per-order up to the cent

    def fee(self, p: float, size: float, is_maker: bool) -> float:
        base = size * p * (1 - p)
        if is_maker:
            f = self.maker_rate * base
            rebate = self.maker_rebate_frac * self.taker_rate * base
            out = f - rebate
        else:
            out = self.taker_rate * base
        if self.round_up_cents and out > 0:
            out = _ceil_cents(out)
        return out


# --- Kalshi -----------------------------------------------------------------
KALSHI_TAKER = 0.07
KALSHI_MAKER = 0.0175

KALSHI_DEFAULT = FeeSchedule(taker_rate=KALSHI_TAKER, maker_rate=0.0)
KALSHI_WITH_MAKER_FEES = FeeSchedule(taker_rate=KALSHI_TAKER, maker_rate=KALSHI_MAKER)

# Series prefixes known to carry maker fees (sports game lines, econ). Verified
# at runtime via GET /series/{ticker} fee_type; this is only the offline default.
KALSHI_MAKER_FEE_PREFIXES = (
    "KXNFL", "KXNBA", "KXMLB", "KXNHL", "KXNCAA", "KXEPL", "KXUCL", "KXATP", "KXWTA",
    "KXF1", "KXCPI", "KXFED", "KXJOBS", "KXGDP", "KXUNEMP", "KXGAS", "KXEGG",
    "KXINX", "KXNASDAQ", "KXMVE",
)


def kalshi_schedule(series_ticker: str, fee_type: str | None = None,
                    fee_multiplier: float | None = None) -> FeeSchedule:
    if fee_type is not None:
        has_maker = "maker" in fee_type
    else:
        has_maker = series_ticker.upper().startswith(KALSHI_MAKER_FEE_PREFIXES)
    m = 1.0 if fee_multiplier is None else fee_multiplier
    return FeeSchedule(taker_rate=KALSHI_TAKER * m,
                       maker_rate=(KALSHI_MAKER * m) if has_maker else 0.0)


# --- Polymarket -------------------------------------------------------------
POLY_RATES = {
    "crypto": (0.07, 0.20),
    "sports": (0.05, 0.15),
    "economics": (0.05, 0.25),
    "culture": (0.05, 0.25),
    "weather": (0.05, 0.25),
    "other": (0.05, 0.25),
    "politics": (0.04, 0.25),
    "finance": (0.04, 0.25),
    "tech": (0.04, 0.25),
    "mentions": (0.04, 0.25),
    "geopolitics": (0.0, 0.0),
}


def polymarket_schedule(category: str, include_rebate: bool = False,
                        taker_rate_override: float | None = None) -> FeeSchedule:
    tr, reb = POLY_RATES.get(category.lower(), (0.05, 0.25))
    if taker_rate_override is not None:
        tr = taker_rate_override
    return FeeSchedule(taker_rate=tr, maker_rate=0.0,
                       maker_rebate_frac=(reb if include_rebate else 0.0),
                       round_up_cents=False)
