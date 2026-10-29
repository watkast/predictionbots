#!/usr/bin/env python3
"""
Implication locks ("dominance"): when event A implies event B, P(A) <= P(B) must hold, so a book that
bids A above B's ask gives a risk-free pair: sell A at its bid, buy B at its ask. Whatever happens:
  B happens, A happens      ->  +1 (B)  -1 (A)  = 0      + (bid_A - ask_B)
  B happens, A does not     ->  +1 (B)   0      = +1     + (bid_A - ask_B)   (the "middle" — bonus)
  neither                   ->   0       0      = 0      + (bid_A - ask_B)
A cannot happen without B. Profit after taker fees = bid_A - ask_B - fee(bid_A) - fee(ask_B).

Every leg is canonicalised to the event {axis > x} with its own (bid, ask, bid_size, ask_size):
  spread "Team A -3.5"  (A wins by more than 3.5)      -> margin_A > 3.5
  spread "Team B +3.5"  (B loses by less than 3.5 or wins) = NOT(margin_A > 3.5) -> complement
  moneyline A (no-draw sport)                          -> margin_A > 0
  total over 220.5                                     -> total > 220.5 ; under 220.5 = NOT(total > 220.5)
A complement leg {axis <= x} is turned into {axis > x} by swapping: bid' = 1 - ask, ask' = 1 - bid.
Then for legs i, j on one axis with x_i >= x_j (i implies j): lock margin = bid_i - ask_j - fees.
Same-venue pairs are clean locks. Cross-venue pairs are locks only if both rulebooks settle the same
game identically (overtime, postponement, retirement) — flagged, never assumed.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Leg:
    venue: str
    id: str
    game: str              # game key shared by legs of the same game (venue-agnostic when matched)
    axis: str              # "margin_<teamA>" or "total" (or any monotone quantity)
    x: float               # threshold; the canonical event is {axis > x}
    bid: Optional[float]
    ask: Optional[float]
    bid_q: Optional[float] = None
    ask_q: Optional[float] = None
    theta: float = 0.07    # taker fee coefficient: fee = theta * p * (1 - p)
    label: str = ""


def complement(bid: Optional[float], ask: Optional[float], bid_q=None, ask_q=None):
    """(bid, ask) of {axis <= x} -> (bid, ask) of {axis > x}."""
    b = None if ask is None else round(1 - ask, 6)
    a = None if bid is None else round(1 - bid, 6)
    return b, a, ask_q, bid_q


def fee(theta: float, p: float) -> float:
    return theta * p * (1 - p)


def implication_locks(legs: list[Leg], min_margin: float = 0.004, cross_venue: bool = True) -> list[dict]:
    by_axis: dict[tuple, list[Leg]] = {}
    for lg in legs:
        if lg.bid is None and lg.ask is None:
            continue
        by_axis.setdefault((lg.game, lg.axis), []).append(lg)
    out = []
    for (game, axis), ls in by_axis.items():
        for i in ls:                       # i: the harder event (sold at its bid)
            if i.bid is None:
                continue
            for j in ls:                   # j: the easier event (bought at its ask)
                if j is i or j.ask is None or i.x < j.x:
                    continue
                if i.venue != j.venue and not cross_venue:
                    continue
                if i.x == j.x and i.venue == j.venue and i.id == j.id:
                    continue
                m = i.bid - j.ask - fee(i.theta, i.bid) - fee(j.theta, j.ask)
                if m > min_margin:
                    out.append({"kind": "implication" + ("_x" if i.venue != j.venue else ""), "game": game, "axis": axis,
                                "sell": i.id, "sell_label": i.label, "sell_x": i.x, "sell_bid": i.bid, "sell_q": i.bid_q,
                                "buy": j.id, "buy_label": j.label, "buy_x": j.x, "buy_ask": j.ask, "buy_q": j.ask_q,
                                "venues": sorted({i.venue, j.venue}), "margin": round(m, 4),
                                "depth": min(q for q in (i.bid_q, j.ask_q) if q is not None) if (i.bid_q or j.ask_q) else None,
                                "middle_bonus": i.x > j.x})
    return out


if __name__ == "__main__":
    # self-test: Lakers -3.5 bid 0.58 vs Lakers moneyline ask 0.52 -> 0.06 gap clears ~3.5c of taker fees at mid prices
    legs = [Leg("pm", "lal-ml", "LAL-DEN", "margin_LAL", 0.0, 0.50, 0.52, 300, 200, 0.0695, "Lakers ML"),
            Leg("pm", "lal-sp", "LAL-DEN", "margin_LAL", 3.5, 0.58, 0.60, 100, 100, 0.0695, "Lakers -3.5")]
    # Nuggets +3.5 quoted bid 0.42 / ask 0.44  ==  NOT(margin_LAL > 3.5): complement -> bid 0.56 ask 0.58
    b, a, bq, aq = complement(0.42, 0.44, 50, 60)
    legs.append(Leg("k", "den-sp", "LAL-DEN", "margin_LAL", 3.5, b, a, bq, aq, 0.07, "Nuggets +3.5 (complement)"))
    for o in implication_locks(legs):
        print(o)
    assert any(o["sell"] == "lal-sp" and o["buy"] == "lal-ml" for o in implication_locks(legs))
    assert all(o["margin"] > 0 for o in implication_locks(legs))
    print("ok")
