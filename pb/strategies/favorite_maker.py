"""Model 4 — Favorite-longshot bias harvesting as a MAKER.

Mechanism
---------
Prediction-market calibration: contracts priced < 10c lose > 60% of stake,
contracts > 70c earn a small positive post-fee return, and for horizons
longer than a month the calibration slope is ~1.32 (true prob is further
from 0.5 than price). Rather than lifting favorites (taker fee 7% * p(1-p)
eats the edge) we REST bids on the favorite side at prices in
[`min_price`, `max_price`] (default 0.70-0.97) only when our calibration
map says true_prob(price) - price >= `edge`.

* Side: if the YES mid >= min_price we bid YES; if the NO price (1 - mid)
  >= min_price we bid NO (expressed as a SELL YES at 1 - p). The symmetric
  handling means we harvest "longshot overpricing" whichever leg it sits on.
* Calibration map: true_prob = 0.5 + slope * (price - 0.5) clipped to 0.995,
  where slope is interpolated between `slope_short` (1.0: no edge within
  `short_horizon_days`) and `slope_long` (1.32 beyond `long_horizon_days`).
* Capital-lock filter: annualised edge = (true - price) / price * 365 /
  days_to_resolution must be >= `hurdle_annual` (default 15%/yr), so we do
  not lock $0.95 for six months to earn 1c.
* Size scales with time-to-resolution (prefer > `min_days` days; longer
  horizon -> larger slope -> larger size, capped) and by touch depth.
* Exclusions: `exclude_series_prefixes` (sports lines reverse the bias;
  default excludes KX sports prefixes and Polymarket "sports") and
  `allow_series_prefixes` optionally whitelists.
* Pull: in the last `pull_before_close` seconds, when price leaves the band,
  or when our bid would be within `min_dist_to_ask` of the ask (we want to
  be a resting bid, not to lift).

Evidence: favorite-longshot bias robust on Kalshi (Bartlett & O'Hara) and
Polymarket (TUM 2025); maker fee on most Kalshi non-sports series is zero;
>70c contracts small positive post-fee even as takers, much better as makers.
Failure modes: adverse selection on resolution news (we are the bid that gets
hit when the favorite collapses - size cap and exposure cap limit this),
long capital lock, oracle/dispute risk, series where the bias reverses
(sports - excluded).

Targets: Kalshi politics/econ/culture series without maker fees; Polymarket
politics/culture (maker free + rebates). Not sports.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from pb.core.types import Action, Book, Fill, Market
from pb.sim.engine import Settlement, SimAPI, Strategy
from pb.strategies.base import Quote, QuoteManager, clamp_size, maker_fee_per_contract, register, round_tick, secs_to_close


@dataclass
class FavoriteMakerParams:
    min_price: float = 0.70
    max_price: float = 0.97
    edge: float = 0.015                     # required true_prob - price
    slope_short: float = 1.0
    slope_long: float = 1.32
    short_horizon_days: float = 1.0
    long_horizon_days: float = 30.0
    min_days: float = 1.0                  # do not quote inside this horizon
    hurdle_annual: float = 0.15
    size: float = 10.0
    size_per_long_horizon: float = 2.0     # multiplier at long horizon
    max_position: float = 50.0
    max_total_capital: float = 2000.0
    depth_frac_cap: float = 0.5
    min_touch_depth: float = 2.0
    min_dist_to_ask: float = 0.01          # rest at least one tick below ask
    improve: bool = False                  # improve best bid by one tick? default join
    pull_before_close: float = 3600.0
    exclude_series_prefixes: tuple[str, ...] = (
        "KXNFL", "KXNBA", "KXMLB", "KXNHL", "KXNCAA", "KXEPL", "KXUCL", "KXATP", "KXWTA", "KXF1",
        "KXUFC", "KXMMA", "KXPGA", "KXSOCCER", "sports")
    allow_series_prefixes: tuple[str, ...] = ()
    tick: float = 0.01


@register
class FavoriteMaker(Strategy):
    name = "favorite_maker"

    def __init__(self, params: FavoriteMakerParams | None = None, markets: list[str] | None = None):
        self.p = params or FavoriteMakerParams()
        self.markets = set(markets or [])
        self.qm: QuoteManager | None = None
        self._positions_seen: set[str] = set()

    def on_start(self, api: SimAPI) -> None:
        self.qm = QuoteManager(api, self.name, tick=self.p.tick)

    def on_settlement(self, api: SimAPI, s: Settlement) -> None:
        self.qm.pull(s.market_id)

    def on_fill(self, api: SimAPI, f: Fill) -> None:
        b = api.book(f.market_id)
        if b is not None:
            self._quote(api, b)

    def on_book(self, api: SimAPI, b: Book) -> None:
        if self.markets and b.market_id not in self.markets:
            return
        self._quote(api, b)

    # -- model ------------------------------------------------------------------
    def series_allowed(self, m: Market | None) -> bool:
        if m is None:
            return True
        s = (m.series or m.market_id or "").upper()
        if self.p.allow_series_prefixes and not s.startswith(tuple(x.upper() for x in self.p.allow_series_prefixes)):
            return False
        return not s.startswith(tuple(x.upper() for x in self.p.exclude_series_prefixes))

    def slope(self, days: float) -> float:
        p = self.p
        if days <= p.short_horizon_days:
            return p.slope_short
        if days >= p.long_horizon_days:
            return p.slope_long
        w = (days - p.short_horizon_days) / (p.long_horizon_days - p.short_horizon_days)
        return p.slope_short + w * (p.slope_long - p.slope_short)

    def true_prob(self, price: float, days: float) -> float:
        return min(0.995, max(0.005, 0.5 + self.slope(days) * (price - 0.5)))

    def annualised_edge(self, price: float, true: float, days: float, fee: float) -> float:
        if price <= 0 or days <= 0:
            return 0.0
        return (true - price - fee) / price * 365.0 / days

    def _total_capital(self, api: SimAPI) -> float:
        return sum(api.position(mid).capital_at_risk() for mid in self._positions_seen)

    # -- quoting ----------------------------------------------------------------
    def _quote(self, api: SimAPI, b: Book) -> None:
        p = self.p
        mid = b.market_id
        m = api.market(mid)
        self._positions_seen.add(mid)
        if not self.series_allowed(m) or b.mid is None:
            self.qm.pull(mid)
            return
        secs = secs_to_close(api, mid)
        days = secs / 86400.0 if math.isfinite(secs) else p.long_horizon_days
        if secs < p.pull_before_close or days < p.min_days:
            self.qm.pull(mid)
            return
        pos = api.position(mid).contracts
        # choose side: YES favourite or NO favourite
        yes_mid = b.mid
        side: Action | None = None
        if p.min_price <= yes_mid <= p.max_price:
            side = Action.BUY
            price_fav = yes_mid
        elif p.min_price <= 1 - yes_mid <= p.max_price:
            side = Action.SELL
            price_fav = 1 - yes_mid
        if side is None:
            self.qm.pull(mid)
            return
        # price we would rest at (on the favourite leg)
        if side is Action.BUY:
            rest = b.best_bid + (p.tick if p.improve else 0.0)
            rest = min(rest, b.best_ask - p.min_dist_to_ask)
            fav_px = rest
        else:
            rest = b.best_ask - (p.tick if p.improve else 0.0)
            rest = max(rest, b.best_bid + p.min_dist_to_ask)
            fav_px = 1 - rest
        fav_px = round_tick(fav_px, p.tick)
        if not (p.min_price <= fav_px <= p.max_price):
            self.qm.pull(mid)
            return
        true = self.true_prob(fav_px, days)
        fee = maker_fee_per_contract(api, mid, fav_px)
        if true - fav_px - fee < p.edge or self.annualised_edge(fav_px, true, days, fee) < p.hurdle_annual:
            self.qm.pull(mid)
            return
        # size
        horizon_mult = 1.0 + (p.size_per_long_horizon - 1.0) * min(1.0, days / p.long_horizon_days)
        touch = b.bids[0].size if side is Action.BUY else b.asks[0].size
        if touch < p.min_touch_depth:
            self.qm.pull(mid)
            return
        room = p.max_position - (pos if side is Action.BUY else -pos)
        cap_left = (p.max_total_capital - self._total_capital(api)) / max(fav_px, 1e-6)
        sz = clamp_size(p.size * horizon_mult, p.depth_frac_cap * touch, max(0.0, room), max(0.0, cap_left))
        if sz <= 0:
            self.qm.pull(mid)
            return
        px = round_tick(rest, p.tick)
        if side is Action.BUY:
            self.qm.set(mid, Quote(px, None, sz, 0.0))
        else:
            self.qm.set(mid, Quote(None, px, 0.0, sz))
