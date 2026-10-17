"""Core data types shared by venues, recorder, simulator and strategies.

Everything is venue-agnostic. Prices are probabilities in [0, 1] (dollars per
contract paying $1). Sizes are contracts (floats; Kalshi allows 0.01 granularity,
Polymarket shares are also fractional).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Venue(str, Enum):
    KALSHI = "kalshi"
    POLYMARKET = "polymarket"
    POLYMARKET_US = "polymarket_us"
    NOVIG = "novig"


class Side(str, Enum):
    """Which outcome we are long after a BUY. We always express orders on the
    YES leg: buying NO at p == selling YES at 1-p. The simulator and venue
    adapters convert as needed."""
    YES = "yes"
    NO = "no"


class Action(str, Enum):
    BUY = "buy"
    SELL = "sell"


class TIF(str, Enum):
    GTC = "gtc"   # rest on book
    IOC = "ioc"   # fill what you can, cancel rest (FAK)
    FOK = "fok"   # all or nothing


@dataclass(slots=True)
class Level:
    price: float   # probability-price of YES
    size: float    # contracts resting


@dataclass(slots=True)
class Book:
    """Order book for a binary market, expressed on the YES leg.

    bids: resting buy-YES orders, sorted best (highest price) first.
    asks: resting sell-YES orders (== NO bids at 1-p), sorted best (lowest) first.
    """
    ts: float            # epoch seconds
    market_id: str
    bids: list[Level] = field(default_factory=list)
    asks: list[Level] = field(default_factory=list)

    @property
    def best_bid(self) -> Optional[float]:
        return self.bids[0].price if self.bids else None

    @property
    def best_ask(self) -> Optional[float]:
        return self.asks[0].price if self.asks else None

    @property
    def mid(self) -> Optional[float]:
        if self.bids and self.asks:
            return (self.bids[0].price + self.asks[0].price) / 2
        return None

    @property
    def spread(self) -> Optional[float]:
        if self.bids and self.asks:
            return self.asks[0].price - self.bids[0].price
        return None

    def depth_within(self, side: Action, cents: float) -> float:
        """Contracts available within `cents` (probability units) of the touch."""
        if side is Action.BUY:
            if not self.asks:
                return 0.0
            lim = self.asks[0].price + cents
            return sum(l.size for l in self.asks if l.price <= lim)
        if not self.bids:
            return 0.0
        lim = self.bids[0].price - cents
        return sum(l.size for l in self.bids if l.price >= lim)

    def microprice(self) -> Optional[float]:
        if not (self.bids and self.asks):
            return self.mid
        b, a = self.bids[0], self.asks[0]
        tot = b.size + a.size
        if tot <= 0:
            return self.mid
        return (b.price * a.size + a.price * b.size) / tot


@dataclass(slots=True)
class Trade:
    """A public print."""
    ts: float
    market_id: str
    price: float          # YES price
    size: float
    taker_action: Action  # BUY => taker lifted the ask (bought YES)


@dataclass(slots=True)
class Order:
    market_id: str
    action: Action
    price: float
    size: float
    tif: TIF = TIF.GTC
    post_only: bool = False
    order_id: Optional[str] = None
    ts: float = 0.0
    strategy: str = ""
    # filled so far
    filled: float = 0.0
    # simulator queue bookkeeping: contracts ahead of us at our price at placement
    queue_ahead: float = 0.0

    @property
    def remaining(self) -> float:
        return max(0.0, self.size - self.filled)


@dataclass(slots=True)
class Fill:
    ts: float
    market_id: str
    order_id: str
    action: Action
    price: float
    size: float
    fee: float            # dollars, positive = paid, negative = rebate
    is_maker: bool
    strategy: str = ""


@dataclass(slots=True)
class Market:
    venue: Venue
    market_id: str        # kalshi ticker / polymarket YES token id
    event_id: str = ""
    series: str = ""      # kalshi series ticker / polymarket category
    title: str = ""
    open_ts: float = 0.0
    close_ts: float = 0.0  # trading close / expiration
    tick: float = 0.01
    min_size: float = 1.0
    result: Optional[float] = None   # 1.0 YES, 0.0 NO, None unresolved
    settle_ts: Optional[float] = None
    meta: dict = field(default_factory=dict)
