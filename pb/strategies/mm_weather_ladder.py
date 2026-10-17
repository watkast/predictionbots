"""Model 3 — Daily-high temperature ladder maker (Kalshi KXHIGH* series,
e.g. KXHIGHNY, KXHIGHCHI, KXHIGHMIA; zero maker fee).

Mechanism
---------
A ladder is a set of mutually exclusive rungs ("70-71", "72-73", "74+")
sharing `Market.meta["ladder_group"]` (fallback: `event_id`). Exactly one
settles YES, so the *true* sum of rung probabilities is 1, but the asks across
a 6-rung ladder sum to ~1.05 median: retail buys every rung it likes and
nobody sells. The edge is therefore on the SELL (ask) side:

* fair_r = P(YES) for rung r from the ensemble-forecast signal `fcst_prob`
  (pb.data.feeds.ensemble_rung_probs with a station bias).
* We rest asks only on rungs where ask_price >= fair_r + edge (overpriced
  rungs), choosing the price max(fair_r + edge, best_bid + tick) and never
  crossing. Asks are limited so that the sum of our resting ask prices
  across the group plus the fair of rungs we do not quote stays >=
  1 + `sum_margin`: if we sold every rung we quote at our prices and the rest
  resolved at fair, we would still be net positive (ladder-level sanity).
* Bids are optional (`quote_bids`): rest bids only on rungs where
  best_ask <= fair_r - edge (underpriced). Default off: the evidence is that
  rungs are over-, not under-priced.
* Inventory: short rungs (we sold YES) skew that rung's ask up by gamma *
  inventory/max_inventory; a running "group delta" (sum of signed
  contracts) is capped at `max_group_short` so a surprise outcome in one
  rung cannot wipe us (we are short the winner at most once).
* Peak-window pull: favorite overpricing collapses (and may invert) in the
  last `peak_window` hours before the expected daily temperature peak
  (`meta["peak_ts"]` if given, else `close_ts` - `peak_offset_h`). In that
  window we pull all asks on rungs whose fair >= `favorite_thresh` and halve
  size elsewhere; with an observation signal `obs_high_f` we also pull any
  rung the observed running high has already made impossible/certain.
* Signal staleness: forecasts are polled every ~15 min; `signal_max_age`
  (default 2 h) kills quoting if the feed dies.

Evidence: 6-rung ladder asks sum ~1.05 median; favorite overpricing ~10x
larger in the last 1-12 h before the daily temp peak; longshot overpricing
far from settlement (so sell far-out rungs early, favorites late only with
observation support). Zero maker fee on Kalshi weather.

Failure modes: forecast bias (station vs model grid - set `bias` in the feed),
ensemble under-dispersion (set spread_scale), a late-day front making the
"certain" rung lose, thin books (depth cap), settlement on the NWS CLI
report which can be revised.

Targets: Kalshi KXHIGH* / KXLOW* daily ladders (and Polymarket weather, where
makers are free but there is no ladder structure beyond the event).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from pb.core.types import Book, Fill, Market
from pb.data.feeds import parse_rung
from pb.sim.engine import Settlement, Signal, SimAPI, Strategy
from pb.strategies.base import Quote, QuoteManager, SignalCache, clamp_size, register, round_tick


@dataclass
class WeatherLadderParams:
    size: float = 10.0
    max_inventory: float = 40.0        # per rung (abs)
    max_group_short: float = 60.0      # sum over rungs of contracts sold YES
    edge: float = 0.03                 # ask >= fair + edge
    sum_margin: float = 0.02           # ladder ask-sum sanity
    gamma: float = 0.05
    quote_bids: bool = False
    peak_window: float = 6.0           # hours before expected peak during which we pull favorites
    peak_offset_h: float = 6.0         # peak ~ close_ts - this when meta["peak_ts"] missing
    favorite_thresh: float = 0.40
    signal_max_age: float = 7200.0
    min_touch_depth: float = 2.0
    depth_frac_cap: float = 0.5
    price_band: tuple[float, float] = (0.03, 0.97)
    max_behind_ask: float = 0.03       # do not rest further than this above the market ask
    tick: float = 0.01
    pull_before_close: float = 600.0


@register
class WeatherLadderMM(Strategy):
    name = "mm_weather_ladder"

    def __init__(self, params: WeatherLadderParams | None = None, markets: list[str] | None = None):
        self.p = params or WeatherLadderParams()
        self.markets = set(markets or [])
        self.fcst = SignalCache()
        self.obs_high: tuple[float, float] | None = None
        self.qm: QuoteManager | None = None
        self.groups: dict[str, set[str]] = {}
        self.group_of: dict[str, str] = {}
        self.our_ask: dict[str, float] = {}

    def on_start(self, api: SimAPI) -> None:
        self.qm = QuoteManager(api, self.name, tick=self.p.tick)
        for mid in self.markets:
            m = api.market(mid)
            if m is not None:
                self._group(api, m)

    def on_settlement(self, api: SimAPI, s: Settlement) -> None:
        self.qm.pull(s.market_id)
        self.our_ask.pop(s.market_id, None)

    def on_market_added(self, api: SimAPI, market: Market) -> None:
        if self.markets:
            self.markets.add(market.market_id)
        self._group(api, market)

    def on_market_removed(self, api: SimAPI, market_id: str) -> None:
        if self.qm is not None:
            self.qm.pull(market_id)
        self.markets.discard(market_id)
        self.our_ask.pop(market_id, None)
        g = self.group_of.pop(market_id, None)
        if g is not None:
            self.groups.get(g, set()).discard(market_id)
            if not self.groups.get(g):
                self.groups.pop(g, None)

    def on_signal(self, api: SimAPI, sig: Signal) -> None:
        if sig.name == "fcst_prob" and sig.market_id:
            try:
                self.fcst.put(sig.market_id, sig.ts, float(sig.value))
            except (TypeError, ValueError):
                return
            b = api.book(sig.market_id)
            if b is not None:
                self._quote(api, b)
        elif sig.name == "obs_high_f":
            try:
                self.obs_high = (sig.ts, float(sig.value))
            except (TypeError, ValueError):
                pass

    def on_fill(self, api: SimAPI, f: Fill) -> None:
        # a fill changes group delta: refresh every sibling
        for mid in self.groups.get(self.group_of.get(f.market_id, ""), {f.market_id}):
            b = api.book(mid)
            if b is not None:
                self._quote(api, b)

    def on_book(self, api: SimAPI, b: Book) -> None:
        if self.markets and b.market_id not in self.markets:
            return
        self._quote(api, b)

    # -- helpers ----------------------------------------------------------------
    def _group(self, api: SimAPI, m: Market) -> str:
        g = str((m.meta or {}).get("ladder_group") or m.event_id or m.market_id)
        self.group_of[m.market_id] = g
        members = self.groups.setdefault(g, set())
        if m.market_id not in members:
            members.add(m.market_id)
            # a new sibling changes the ladder sum: refresh the others
            for sib in list(members):
                if sib != m.market_id:
                    b = api.book(sib)
                    if b is not None:
                        self._quote(api, b)
        return g

    def _group_delta(self, api: SimAPI, g: str) -> float:
        """Contracts sold YES across the group (positive = net short YES)."""
        return -sum(api.position(mid).contracts for mid in self.groups.get(g, ()))

    def _in_peak_window(self, api: SimAPI, m: Market) -> bool:
        peak = (m.meta or {}).get("peak_ts")
        if peak is None:
            if not m.close_ts:
                return False
            peak = m.close_ts - self.p.peak_offset_h * 3600
        try:
            peak = float(peak)
        except (TypeError, ValueError):
            return False
        return 0 <= peak - api.now <= self.p.peak_window * 3600 or api.now > peak

    def _obs_verdict(self, m: Market) -> float | None:
        """1.0 if the running observed high makes the rung certain-ish, 0.0 if
        impossible, else None."""
        if self.obs_high is None:
            return None
        rung = parse_rung(m)
        if rung is None:
            return None
        lo, hi = rung
        h = self.obs_high[1]
        if hi is not None and h > hi + 0.5:
            return 0.0  # already exceeded the cap
        return None

    def _ladder_sum_ok(self, api: SimAPI, g: str, mid: str, ask: float, fair: float) -> bool:
        """If we sold every rung we quote at our prices and the others resolved
        at their forecast fair, would we collect >= 1 + sum_margin? Only
        meaningful when the known forecasts describe the whole ladder (their
        sum is near 1); with a partial ladder we fall back to per-rung edge."""
        total = 0.0
        fair_sum = 0.0
        for sib in self.groups.get(g, ()):
            f = fair if sib == mid else self.fcst.get(sib, api.now, self.p.signal_max_age)
            if f is None:
                continue
            fair_sum += f
            if sib == mid:
                total += ask
            else:
                total += self.our_ask.get(sib, f)
        if len(self.groups.get(g, ())) <= 1 or not (0.9 <= fair_sum <= 1.1):
            return True
        return total >= 1.0 + self.p.sum_margin - 1e-9

    # -- quoting --------------------------------------------------------------------
    def _quote(self, api: SimAPI, b: Book) -> None:
        p = self.p
        mid = b.market_id
        m = api.market(mid)
        if m is None:
            return
        g = self._group(api, m)
        fair = self.fcst.get(mid, api.now, p.signal_max_age)
        pull = fair is None
        if not pull and m.close_ts and m.close_ts - api.now < p.pull_before_close:
            pull = True
        if not pull and (b.best_bid is None or b.best_ask is None):
            pull = True
        if not pull and not (p.price_band[0] <= fair <= p.price_band[1]):
            pull = True
        verdict = self._obs_verdict(m)
        if verdict is not None:
            fair = verdict
        if pull:
            self.qm.pull(mid)
            self.our_ask.pop(mid, None)
            return
        inv = api.position(mid).contracts            # negative = sold YES
        peak = self._in_peak_window(api, m)
        size_mult = 1.0
        ask_allowed = True
        if peak and fair >= p.favorite_thresh and verdict is None:
            ask_allowed = False
        elif peak:
            size_mult = 0.5
        if verdict == 0.0:
            ask_allowed = True  # cannot lose selling a rung the obs already killed

        # ---- ask (sell overpriced rung) -----
        ask = None
        ask_sz = 0.0
        skew = p.gamma * (-inv / p.max_inventory)   # short -> raise ask
        want = fair + p.edge + max(0.0, skew)
        if ask_allowed and b.best_bid is not None:
            cand = max(want, b.best_bid + p.tick)
            cand = round_tick(cand, p.tick)
            if cand >= fair + p.edge - 1e-9 and cand <= b.best_ask + p.max_behind_ask + 1e-9 \
                    and self._ladder_sum_ok(api, g, mid, cand, fair):
                room_rung = max(0.0, p.max_inventory + inv)        # inv<=0 reduces room
                # count sibling asks already resting so the cap binds pre-fill too
                resting_sibs = sum(o.remaining for sib in self.groups.get(g, ()) if sib != mid
                                   for o in [self.qm.live.get(sib, {}).get("ask")] if o is not None)
                room_group = max(0.0, p.max_group_short - self._group_delta(api, g) - resting_sibs)
                touch = b.asks[0].size if b.asks else 0.0
                if touch >= p.min_touch_depth or cand < b.best_ask:
                    ask_sz = clamp_size(p.size * size_mult, p.depth_frac_cap * max(touch, p.size),
                                        room_rung, room_group)
                    ask = cand if ask_sz > 0 else None
        # ---- bid (buy underpriced rung), optional ---
        bid = None
        bid_sz = 0.0
        if p.quote_bids and b.best_ask is not None and b.best_ask <= fair - p.edge:
            cand = round_tick(min(fair - p.edge, b.best_ask - p.tick), p.tick)
            touch = b.bids[0].size if b.bids else 0.0
            bid_sz = clamp_size(p.size * size_mult, p.depth_frac_cap * max(touch, p.size),
                                max(0.0, p.max_inventory - inv))
            bid = cand if bid_sz > 0 else None
        if ask is not None:
            self.our_ask[mid] = ask
        else:
            self.our_ask.pop(mid, None)
        # the group cap must bind immediately: shrink a resting ask that is now too big
        cur = self.qm.live.get(mid, {}).get("ask")
        if cur is not None and (ask is None or cur.remaining > ask_sz + 1e-9):
            api.cancel(cur.order_id)
            self.qm.live[mid].pop("ask", None)
        self.qm.set(mid, Quote(bid, ask, bid_sz, ask_sz))
