"""Model 5 — Endgame "bond": rest bids at 95-99c on near-certain outcomes in
the final hours (`taker=False`, never lifts).

Mechanism
---------
A contract at 0.97 with 12 h to settlement is a 3.1% yield for half a day
(~2,200%/yr nominal) IF it settles YES. The realised return is T-bill-like
because of (a) oracle/dispute tail risk and (b) adverse selection: the only
reason someone hits a 97c bid is that they know something. We therefore:

* only quote within the last `max_hours` before close (default 12 h) and
  only if the market's series/category is in `allow_categories` /
  `allow_series_prefixes` (low oracle-dispute risk: scheduled data releases,
  sports finals, weather, crypto windows - NOT political/legal "will X happen
  by" markets that resolve on interpretation);
* require the favourite side's mid in [`min_price`, `max_price`]
  (0.95-0.99), touch depth >= `min_depth`, and the annualised yield
  (true_prob - price - fee) / price * 365 / days >= `hurdle_annual` where
  true_prob = price + `prior_edge` (calibration says 95-99c is slightly
  under-priced) minus `dispute_haircut`;
* cap exposure per market (`max_per_market` dollars locked) and total
  (`max_total`), sizing to a fraction of touch depth;
* rest one tick below the ask (join bid or improve by `improve_ticks`) so we
  collect the spread rather than pay it; symmetric NO handling.

Evidence: endgame returns ~ T-bill-like with fat left tail; makers at
>70c small positive; Kalshi maker fee 0 on most non-sports series (on sports
the 0.0175 maker fee at 0.97 is ~0.05c, negligible).
Failure modes: resolution reversal (the fat tail), stale/empty books in the
last hour (depth gate), capital lock across many simultaneous markets
(total cap), slow settlement extending the lock (yield assumes close_ts).

Targets: Kalshi econ/weather/crypto-window series in the final hours;
Polymarket sports finals once the game state is "post".
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from pb.core.types import Action, Book, Fill, Market
from pb.sim.engine import Settlement, SimAPI, Strategy
from pb.strategies.base import Quote, QuoteManager, clamp_size, maker_fee_per_contract, register, round_tick, secs_to_close


@dataclass
class EndgameParams:
    min_price: float = 0.95
    max_price: float = 0.99
    max_hours: float = 12.0
    min_minutes: float = 10.0           # pull inside this (settlement sniping / no liquidity)
    prior_edge: float = 0.01
    dispute_haircut: float = 0.003
    hurdle_annual: float = 0.20
    min_depth: float = 20.0
    size: float = 50.0
    depth_frac_cap: float = 0.5
    max_per_market: float = 500.0       # dollars locked
    max_total: float = 3000.0
    improve_ticks: int = 0
    allow_categories: tuple[str, ...] = ("weather", "crypto", "economics", "sports", "finance")
    allow_series_prefixes: tuple[str, ...] = ("KXHIGH", "KXLOW", "KXBTC", "KXETH", "KXCPI", "KXFED",
                                              "KXJOBS", "KXGDP", "KXUNEMP", "KXINX", "KXNASDAQ",
                                              "KXNFL", "KXNBA", "KXMLB", "KXNHL")
    tick: float = 0.01
    taker: bool = False                 # informational: this strategy never takes


@register
class EndgameBond(Strategy):
    name = "endgame_bond"

    def __init__(self, params: EndgameParams | None = None, markets: list[str] | None = None):
        self.p = params or EndgameParams()
        self.markets = set(markets or [])
        self.qm: QuoteManager | None = None
        self.seen: set[str] = set()

    def on_start(self, api: SimAPI) -> None:
        self.qm = QuoteManager(api, self.name, tick=self.p.tick)

    def on_settlement(self, api: SimAPI, s: Settlement) -> None:
        self.qm.pull(s.market_id)

    def on_market_added(self, api: SimAPI, market: Market) -> None:
        if self.markets:
            self.markets.add(market.market_id)

    def on_market_removed(self, api: SimAPI, market_id: str) -> None:
        if self.qm is not None:
            self.qm.pull(market_id)
        self.markets.discard(market_id)
        self.seen.discard(market_id)

    def on_fill(self, api: SimAPI, f: Fill) -> None:
        b = api.book(f.market_id)
        if b is not None:
            self._quote(api, b)

    def on_book(self, api: SimAPI, b: Book) -> None:
        if self.markets and b.market_id not in self.markets:
            return
        self._quote(api, b)

    def allowed(self, m: Market | None) -> bool:
        if m is None:
            return False
        s = (m.series or m.market_id or "").upper()
        cat = str((m.meta or {}).get("category") or m.series or "").lower()
        return s.startswith(tuple(x.upper() for x in self.p.allow_series_prefixes)) or \
            cat in tuple(c.lower() for c in self.p.allow_categories)

    def annual_yield(self, price: float, days: float, fee: float) -> float:
        true = min(1.0, price + self.p.prior_edge) - self.p.dispute_haircut
        if days <= 0 or price <= 0:
            return 0.0
        return (true - price - fee) / price * 365.0 / days

    def _locked(self, api: SimAPI) -> float:
        return sum(api.position(mid).capital_at_risk() for mid in self.seen)

    def _quote(self, api: SimAPI, b: Book) -> None:
        p = self.p
        mid = b.market_id
        m = api.market(mid)
        self.seen.add(mid)
        secs = secs_to_close(api, mid)
        if not self.allowed(m) or b.mid is None or not math.isfinite(secs):
            self.qm.pull(mid)
            return
        if secs > p.max_hours * 3600 or secs < p.min_minutes * 60:
            self.qm.pull(mid)
            return
        side = None
        if p.min_price <= b.mid <= p.max_price:
            side = Action.BUY
        elif p.min_price <= 1 - b.mid <= p.max_price:
            side = Action.SELL
        if side is None:
            self.qm.pull(mid)
            return
        if side is Action.BUY:
            rest = min(b.best_bid + p.improve_ticks * p.tick, b.best_ask - p.tick)
            fav_px = rest
            touch = b.bids[0].size
        else:
            rest = max(b.best_ask - p.improve_ticks * p.tick, b.best_bid + p.tick)
            fav_px = 1 - rest
            touch = b.asks[0].size
        fav_px = round_tick(fav_px, p.tick)
        if not (p.min_price <= fav_px <= p.max_price) or touch < p.min_depth:
            self.qm.pull(mid)
            return
        days = secs / 86400.0
        fee = maker_fee_per_contract(api, mid, fav_px)
        if self.annual_yield(fav_px, days, fee) < p.hurdle_annual:
            self.qm.pull(mid)
            return
        pos = api.position(mid)
        locked_here = pos.capital_at_risk()
        room_mkt = max(0.0, p.max_per_market - locked_here) / fav_px
        room_tot = max(0.0, p.max_total - self._locked(api)) / fav_px
        sz = clamp_size(p.size, p.depth_frac_cap * touch, room_mkt, room_tot)
        if sz <= 0:
            self.qm.pull(mid)
            return
        px = round_tick(rest, p.tick)
        if side is Action.BUY:
            self.qm.set(mid, Quote(px, None, sz, 0.0))
        else:
            self.qm.set(mid, Quote(None, px, 0.0, sz))
