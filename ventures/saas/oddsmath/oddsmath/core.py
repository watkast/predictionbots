"""Betting / prediction-market math. Pure functions, no I/O, no third-party deps.

Conventions
-----------
* A *probability* is a float in (0, 1). A *price* on Kalshi/Polymarket/Novig is
  the YES probability (Kalshi cents / 100).
* *Decimal* odds d >= 1.0 pay d per unit staked (including the stake).
* *American* odds: +150 pays 1.5 per unit, -200 pays 0.5 per unit.
* *Fractional* odds "5/2" pay 5 per 2 staked.

Fee formulas (as of 2026-10-17, see README for sources)
-------------------------------------------------------
* Kalshi   taker: ceil_cents(0.07 * C * p * (1-p)) per order; maker 0.0175 * ...
           only on series flagged `quadratic_with_maker_fees` (most sports/econ).
* Polymarket taker: C * rate * p * (1-p), rate by category (crypto 0.07,
           sports 0.05, politics 0.04, ...); maker 0 (rebate pools ignored).
* Novig    taker: 0.06 * C * p * (1-p) while the event is live, 0 pregame;
           maker 0 (plus a 50 % credit of the live taker fee, ignored here).
"""
from __future__ import annotations

import math
from fractions import Fraction
from typing import Iterable, Sequence


class OddsError(ValueError):
    """Bad input; the API turns this into HTTP 400."""


# --------------------------------------------------------------------------
# conversions
# --------------------------------------------------------------------------
def _check_prob(p: float) -> float:
    if not (0.0 < p < 1.0):
        raise OddsError(f"probability must be in (0,1), got {p}")
    return float(p)


def american_to_prob(a: float) -> float:
    a = float(a)
    if -100 < a < 100:
        raise OddsError(f"american odds must be <= -100 or >= 100, got {a}")
    return 100.0 / (a + 100.0) if a > 0 else -a / (-a + 100.0)


def prob_to_american(p: float) -> float:
    p = _check_prob(p)
    return round(-100.0 * p / (1.0 - p), 2) if p >= 0.5 else round(100.0 * (1.0 - p) / p, 2)


def decimal_to_prob(d: float) -> float:
    d = float(d)
    if d <= 1.0:
        raise OddsError(f"decimal odds must be > 1, got {d}")
    return 1.0 / d


def prob_to_decimal(p: float) -> float:
    return 1.0 / _check_prob(p)


def fractional_to_prob(s: str | float) -> float:
    if isinstance(s, (int, float)):
        frac = Fraction(str(s))
    else:
        txt = str(s).strip().replace("-", "/").replace(":", "/")
        if "/" not in txt:
            raise OddsError(f"fractional odds must look like '5/2', got {s!r}")
        num, den = txt.split("/", 1)
        try:
            frac = Fraction(int(num), int(den))
        except (ValueError, ZeroDivisionError) as e:
            raise OddsError(f"bad fractional odds {s!r}: {e}") from None
    if frac <= 0:
        raise OddsError(f"fractional odds must be positive, got {s!r}")
    return 1.0 / (1.0 + float(frac))


def prob_to_fractional(p: float, max_den: int = 100) -> str:
    p = _check_prob(p)
    f = Fraction(1.0 / p - 1.0).limit_denominator(max_den)
    return f"{f.numerator}/{f.denominator}"


def cents_to_prob(c: float) -> float:
    c = float(c)
    if not (0.0 < c < 100.0):
        raise OddsError(f"cents must be in (0,100), got {c}")
    return c / 100.0


def to_prob(value, fmt: str) -> float:
    """Convert `value` expressed in `fmt` to a probability."""
    fmt = (fmt or "").lower()
    if fmt in ("prob", "probability", "p"):
        return _check_prob(float(value))
    if fmt in ("american", "us", "moneyline"):
        return american_to_prob(value)
    if fmt in ("decimal", "eu"):
        return decimal_to_prob(value)
    if fmt in ("fractional", "uk"):
        return fractional_to_prob(value)
    if fmt in ("cents", "kalshi"):
        return cents_to_prob(value)
    raise OddsError(f"unknown odds format {fmt!r}; use prob|american|decimal|fractional|cents")


def all_formats(p: float) -> dict:
    p = _check_prob(p)
    return {
        "probability": round(p, 6),
        "american": prob_to_american(p),
        "decimal": round(prob_to_decimal(p), 4),
        "fractional": prob_to_fractional(p),
        "cents": round(p * 100.0, 2),
    }


# --------------------------------------------------------------------------
# devig (remove the bookmaker margin from a full set of outcome prices)
# --------------------------------------------------------------------------
DEVIG_METHODS = ("multiplicative", "additive", "power", "shin")


def _bisect(f, lo: float, hi: float, iters: int = 200) -> float:
    flo = f(lo)
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        fm = f(mid)
        if abs(fm) < 1e-12:
            return mid
        if (fm < 0) == (flo < 0):
            lo, flo = mid, fm
        else:
            hi = mid
    return 0.5 * (lo + hi)


def devig(implied: Sequence[float], method: str = "power") -> list[float]:
    """Fair probabilities from implied probabilities (which sum to 1 + overround)."""
    q = [_check_prob(x) for x in implied]
    if len(q) < 2:
        raise OddsError("devig needs at least two outcomes")
    s = sum(q)
    if s <= 1.0:
        # no vig (or negative vig = arbitrage); still normalise so result is a distribution
        return [x / s for x in q]
    method = (method or "power").lower()
    if method == "multiplicative":
        return [x / s for x in q]
    if method == "additive":
        over = (s - 1.0) / len(q)
        out = [max(x - over, 1e-9) for x in q]
        t = sum(out)
        return [x / t for x in out]
    if method == "power":
        k = _bisect(lambda k: sum(x ** k for x in q) - 1.0, 1.0, 50.0)
        out = [x ** k for x in q]
        t = sum(out)
        return [x / t for x in out]
    if method == "shin":
        def p_of(z: float) -> list[float]:
            return [(math.sqrt(z * z + 4.0 * (1.0 - z) * x * x / s) - z) / (2.0 * (1.0 - z)) for x in q]
        z = _bisect(lambda z: sum(p_of(z)) - 1.0, 0.0, 0.999999)
        out = p_of(z)
        t = sum(out)
        return [x / t for x in out]
    raise OddsError(f"unknown devig method {method!r}; use {'|'.join(DEVIG_METHODS)}")


def devig_report(odds: Sequence, fmt: str = "american", method: str = "power",
                 labels: Sequence[str] | None = None) -> dict:
    implied = [to_prob(v, fmt) for v in odds]
    hold = sum(implied) - 1.0
    labels = list(labels) if labels else [f"outcome_{i + 1}" for i in range(len(implied))]
    if len(labels) != len(implied):
        raise OddsError("labels must match odds length")
    methods = DEVIG_METHODS if method == "all" else (method,)
    fair = {m: devig(implied, m) for m in methods}
    rows = []
    for i, lab in enumerate(labels):
        row = {"label": lab, "offered": odds[i], "implied": round(implied[i], 6)}
        for m in methods:
            row[f"fair_{m}"] = round(fair[m][i], 6)
        rows.append(row)
    return {"method": method, "hold": round(hold, 6), "overround_pct": round(hold * 100.0, 4),
            "outcomes": rows}


# --------------------------------------------------------------------------
# fees
# --------------------------------------------------------------------------
KALSHI_TAKER = 0.07
KALSHI_MAKER = 0.0175
POLY_TAKER_BY_CATEGORY = {
    "crypto": 0.07, "sports": 0.05, "economics": 0.05, "culture": 0.05, "weather": 0.05,
    "other": 0.05, "politics": 0.04, "finance": 0.04, "tech": 0.04, "mentions": 0.04,
    "geopolitics": 0.0,
}
NOVIG_TAKER_LIVE = 0.06


def _ceil_cents(x: float) -> float:
    return math.ceil(x * 100.0 - 1e-9) / 100.0


def venue_fee(venue: str, price: float, contracts: float, side: str = "taker",
              category: str | None = None, maker_fees: bool | None = None,
              live: bool = False) -> dict:
    """Dollar fee for `contracts` $1-payout contracts at YES-probability `price`."""
    p = _check_prob(price)
    c = float(contracts)
    if c <= 0:
        raise OddsError("contracts must be > 0")
    side = (side or "taker").lower()
    if side not in ("taker", "maker"):
        raise OddsError("side must be taker|maker")
    base = c * p * (1.0 - p)
    v = (venue or "").lower()
    if v == "kalshi":
        if side == "taker":
            fee = _ceil_cents(KALSHI_TAKER * base)
        else:
            fee = _ceil_cents(KALSHI_MAKER * base) if maker_fees else 0.0
        note = "taker 0.07*C*p*(1-p) rounded up to the cent; maker 0.0175 only on quadratic_with_maker_fees series"
    elif v == "polymarket":
        rate = POLY_TAKER_BY_CATEGORY.get((category or "other").lower(), 0.05)
        fee = rate * base if side == "taker" else 0.0
        note = f"taker rate {rate} for category {category or 'other'}; maker 0 (rebate pools ignored)"
    elif v == "novig":
        fee = NOVIG_TAKER_LIVE * base if (side == "taker" and live) else 0.0
        note = "taker 0.06*C*p*(1-p) only while live; pregame free; maker 0 (50% live-fee credit ignored)"
    elif v in ("none", "", "custom"):
        fee, note = 0.0, "no fee"
    else:
        raise OddsError(f"unknown venue {venue!r}; use kalshi|polymarket|novig|none")
    return {"venue": v or "none", "side": side, "price": p, "contracts": c, "fee_usd": round(fee, 4),
            "fee_per_contract_cents": round(100.0 * fee / c, 4), "note": note}


# --------------------------------------------------------------------------
# expected value / kelly
# --------------------------------------------------------------------------
def kelly_fraction(p: float, decimal_odds: float) -> float:
    """Full-Kelly stake fraction for win prob p at decimal odds d (0 if no edge)."""
    p = _check_prob(p)
    b = decimal_odds - 1.0
    if b <= 0:
        raise OddsError("decimal odds must be > 1")
    return max(0.0, (p * b - (1.0 - p)) / b)


def ev_report(fair_prob: float, offered, fmt: str = "decimal", stake: float = 1.0,
              kelly_mult: float = 0.25, bankroll: float | None = None,
              venue: str | None = None, side: str = "taker", category: str | None = None,
              maker_fees: bool | None = None, live: bool = False) -> dict:
    """EV of a bet/contract at `offered` given a fair probability. For prediction
    markets pass fmt='prob' or 'cents' (the offered price) and a venue for fees."""
    p = _check_prob(fair_prob)
    q = to_prob(offered, fmt)      # implied probability of the offered price
    d = 1.0 / q                     # decimal odds
    stake = float(stake)
    if stake <= 0:
        raise OddsError("stake must be > 0")
    fee = 0.0
    if venue and venue.lower() not in ("none", ""):
        # a stake of S dollars at price q buys S/q contracts
        contracts = stake / q
        fee = venue_fee(venue, q, contracts, side, category, maker_fees, live)["fee_usd"]
    ev = stake * (p * (d - 1.0) - (1.0 - p)) - fee
    kelly = kelly_fraction(p, d)
    out = {
        "fair_prob": round(p, 6), "offered": offered, "implied_prob": round(q, 6),
        "decimal_odds": round(d, 4), "edge": round(p - q, 6), "edge_pct": round((p - q) * 100.0, 4),
        "stake": stake, "fee_usd": round(fee, 4), "ev_usd": round(ev, 4),
        "roi_pct": round(100.0 * ev / stake, 4),
        "kelly_full": round(kelly, 6), "kelly_fraction_used": kelly_mult,
        "kelly_stake_frac": round(kelly * kelly_mult, 6),
    }
    if bankroll is not None:
        out["kelly_stake_usd"] = round(float(bankroll) * kelly * kelly_mult, 2)
    return out


# --------------------------------------------------------------------------
# arbitrage across books / venues
# --------------------------------------------------------------------------
def arb_report(outcomes: Sequence[dict], bankroll: float = 100.0, fmt: str = "decimal") -> dict:
    """outcomes: [{"label": "A", "quotes": [{"book": "x", "odds": 2.1}, ...]}, ...]
    Picks the best quote per outcome; arb if sum of implied probs < 1."""
    if len(outcomes) < 2:
        raise OddsError("arb needs at least two outcomes")
    best = []
    for o in outcomes:
        quotes = o.get("quotes") or []
        if not quotes:
            raise OddsError(f"outcome {o.get('label')!r} has no quotes")
        scored = []
        for qq in quotes:
            prob = to_prob(qq["odds"], qq.get("fmt", fmt))
            scored.append((prob, qq))
        prob, qq = min(scored, key=lambda t: t[0])
        best.append({"label": o.get("label", f"outcome_{len(best) + 1}"), "book": qq.get("book"),
                     "odds": qq["odds"], "implied": round(prob, 6), "decimal": round(1.0 / prob, 4)})
    total = sum(b["implied"] for b in best)
    margin = 1.0 - total
    bankroll = float(bankroll)
    for b in best:
        b["stake"] = round(bankroll * b["implied"] / total, 2)
        b["payout_if_wins"] = round(b["stake"] * b["decimal"], 2)
    return {"is_arb": margin > 1e-9, "sum_implied": round(total, 6), "margin_pct": round(margin * 100.0, 4),
            "guaranteed_profit_usd": round(bankroll * margin / total, 2) if margin > 0 else 0.0,
            "bankroll": bankroll, "legs": best}


def complete_set_report(yes_price: float, no_price: float, venue: str = "kalshi",
                        contracts: float = 100.0, category: str | None = None,
                        live: bool = False) -> dict:
    """Prediction-market complete-set check: buy YES at yes_price and NO at no_price
    (both as probabilities) as a taker; profit if yes+no+fees < 1."""
    y, n = _check_prob(yes_price), _check_prob(no_price)
    fy = venue_fee(venue, y, contracts, "taker", category, None, live)["fee_usd"]
    fn = venue_fee(venue, n, contracts, "taker", category, None, live)["fee_usd"]
    cost = contracts * (y + n) + fy + fn
    profit = contracts - cost
    return {"venue": venue, "yes_price": y, "no_price": n, "contracts": contracts,
            "gross_edge_cents": round((1.0 - y - n) * 100.0, 4), "fees_usd": round(fy + fn, 4),
            "net_profit_usd": round(profit, 4), "is_arb": profit > 1e-9}


def parlay(probs: Iterable[float], offered_decimal: float | None = None) -> dict:
    ps = [_check_prob(p) for p in probs]
    if not ps:
        raise OddsError("parlay needs at least one leg")
    fair_p = math.prod(ps)
    out = {"legs": len(ps), "fair_prob": round(fair_p, 6), "fair_decimal": round(1.0 / fair_p, 4)}
    if offered_decimal is not None:
        d = float(offered_decimal)
        if d <= 1.0:
            raise OddsError("offered decimal odds must be > 1")
        out["offered_decimal"] = d
        out["ev_per_unit"] = round(fair_p * (d - 1.0) - (1.0 - fair_p), 6)
    return out
