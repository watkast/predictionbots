"""Model 8 — Cross-venue arbitrage: Kalshi vs Polymarket on linked markets.

Linking: two `Market`s share `meta["pair_id"]` (set by the integration
layer; e.g. "BTC-15M-2026-10-16T13:15" or an election contract). Both are
expressed on the YES leg with identical semantics (the integrator is
responsible for checking the resolution criteria match - that is the
failure mode that has burned every cross-venue arber).

Modes
-----
* `mode="taker"` (default): when venue A's ask + venue B's NO-ask (= 1 -
  B's bid) < 1 - feeA - feeB - `min_edge` - slippage, buy YES on A (IOC)
  and sell YES on B (IOC) for size = min(walked depth on both legs) *
  `depth_frac`. The walk uses the recorded levels so the average price (not
  the touch) is what must clear the fee hurdle. Symmetric in the other
  direction. Position nets to zero across venues (held to settlement;
  settlement timing/reference differences are the residual risk).
* `mode="maker_kalshi"`: rest a post-only order on Kalshi at the price that
  would make the pair profitable after hedging with a taker order on
  Polymarket at ITS current touch (minus the Polymarket taker fee and
  `hedge_pad`); on a Kalshi fill, immediately IOC the hedge on Polymarket.
  Kalshi maker fees are zero on crypto/weather so the combined fee is only
  the Polymarket taker leg. Unhedged exposure after a failed hedge is
  flattened at the touch if `flatten_unhedged`.

Fees come from the engine per market (so the Kalshi leg uses Kalshi's
schedule and the Polymarket leg the category rate).

Evidence: cross-venue gaps on identical contracts are typically < the sum
of taker fees (7c*p(1-p) + 4-7c*p(1-p)); when they appear they are in thin
books and close within seconds. The maker-leg variant is the only form
likely to clear fees. Both forms are limited by the pair-semantics risk.
Failure modes: resolution-rule mismatch (TWAP vs BRTI, different cut-off
times), legging risk, withdrawal/capital split across venues (no
rebalancing modelled), stale book on one venue.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from pb.core.types import Action, Book, Fill, Market, Order, TIF, Venue
from pb.sim.engine import Settlement, SimAPI, Strategy
from pb.strategies.base import register, round_tick, taker_fee_per_contract, walk_cost


@dataclass
class CrossVenueParams:
    mode: str = "taker"                  # "taker" | "maker_kalshi"
    min_edge: float = 0.005
    max_size: float = 100.0
    min_size: float = 5.0
    depth_frac: float = 0.8
    slippage_pad: float = 0.005          # extra per-leg allowance beyond walked avg
    cooldown: float = 2.0
    hedge_pad: float = 0.01              # maker mode: cushion vs. hedge touch moving
    maker_size: float = 10.0
    flatten_unhedged: bool = True
    max_pair_position: float = 200.0
    tick: float = 0.01
    max_book_age: float = 30.0


@register
class CrossVenueArb(Strategy):
    name = "cross_venue_arb"

    def __init__(self, params: CrossVenueParams | None = None, markets: list[str] | None = None):
        self.p = params or CrossVenueParams()
        self.markets = set(markets or [])
        self.pairs: dict[str, set[str]] = {}
        self.pair_of: dict[str, str] = {}
        self.last_try: dict[str, float] = {}
        self.resting: dict[str, Order] = {}      # kalshi market -> maker order
        self.opportunities: list[dict] = []

    def on_settlement(self, api: SimAPI, s: Settlement) -> None:
        o = self.resting.pop(s.market_id, None)
        if o is not None:
            api.cancel(o.order_id)

    def on_market_added(self, api: SimAPI, market: Market) -> None:
        if self.markets:
            self.markets.add(market.market_id)
        self._register(api, market)

    def on_market_removed(self, api: SimAPI, market_id: str) -> None:
        self.on_settlement(api, Settlement(ts=api.now, market_id=market_id, result=0.0))
        self.markets.discard(market_id)
        pid = self.pair_of.pop(market_id, None)
        if pid is not None:
            self.pairs.get(pid, set()).discard(market_id)
            if not self.pairs.get(pid):
                self.pairs.pop(pid, None)

    def _register(self, api: SimAPI, m: Market) -> str | None:
        pid = (m.meta or {}).get("pair_id")
        if not pid:
            return None
        pid = str(pid)
        self.pair_of[m.market_id] = pid
        self.pairs.setdefault(pid, set()).add(m.market_id)
        return pid

    def on_book(self, api: SimAPI, b: Book) -> None:
        if self.markets and b.market_id not in self.markets:
            return
        m = api.market(b.market_id)
        if m is None:
            return
        pid = self._register(api, m)
        if pid is None:
            return
        mids = self.pairs[pid]
        if len(mids) != 2:
            return
        a, c = sorted(mids)
        ma, mc = api.market(a), api.market(c)
        ba, bc = api.book(a), api.book(c)
        if ba is None or bc is None or not (ba.bids and ba.asks and bc.bids and bc.asks):
            return
        if max(api.now - ba.ts, api.now - bc.ts) > self.p.max_book_age:
            return
        if self.p.mode == "maker_kalshi":
            self._maker(api, pid, ma, mc, ba, bc)
        else:
            self._taker(api, pid, a, c, ba, bc)

    # -- taker mode ----------------------------------------------------------------
    def _leg_edge(self, api: SimAPI, buy_mid: str, buy_book: Book, sell_mid: str, sell_book: Book, size: float):
        avg_buy, fb = walk_cost(buy_book.asks, size)
        avg_sell, fs = walk_cost(sell_book.bids, size)
        size = min(size, fb, fs)
        if size < self.p.min_size:
            return None
        fee = taker_fee_per_contract(api, buy_mid, avg_buy) + taker_fee_per_contract(api, sell_mid, avg_sell)
        edge = avg_sell - avg_buy - fee - 2 * self.p.slippage_pad
        return edge, size, avg_buy, avg_sell

    def _taker(self, api: SimAPI, pid: str, a: str, c: str, ba: Book, bc: Book) -> None:
        if api.now - self.last_try.get(pid, -math.inf) < self.p.cooldown:
            return
        net = api.position(a).contracts + api.position(c).contracts
        best = None
        for buy_mid, buy_book, sell_mid, sell_book in ((a, ba, c, bc), (c, bc, a, ba)):
            size = min(self.p.max_size, self.p.depth_frac * min(buy_book.asks[0].size, sell_book.bids[0].size))
            if size < self.p.min_size:
                continue
            r = self._leg_edge(api, buy_mid, buy_book, sell_mid, sell_book, size)
            if r is None or r[0] < self.p.min_edge:
                continue
            if best is None or r[0] > best[0][0]:
                best = (r, buy_mid, buy_book, sell_mid, sell_book)
        if best is None:
            return
        (edge, size, avg_buy, avg_sell), buy_mid, buy_book, sell_mid, sell_book = best
        if abs(api.position(buy_mid).contracts) + size > self.p.max_pair_position:
            return
        self.last_try[pid] = api.now
        self.opportunities.append({"ts": api.now, "pair": pid, "edge": edge, "size": size,
                                   "buy": buy_mid, "sell": sell_mid})
        api.place(Order(buy_mid, Action.BUY, avg_buy + self.p.slippage_pad, size, tif=TIF.IOC, strategy=self.name))
        api.place(Order(sell_mid, Action.SELL, avg_sell - self.p.slippage_pad, size, tif=TIF.IOC, strategy=self.name))
        if self.p.flatten_unhedged:
            api.schedule(1.0, lambda: self._flatten(api, a, c))

    def _flatten(self, api: SimAPI, a: str, c: str) -> None:
        net = api.position(a).contracts + api.position(c).contracts
        if abs(net) < 1e-9:
            return
        # reduce on whichever venue has the better touch for the reducing trade
        action = Action.SELL if net > 0 else Action.BUY
        cands = []
        for mid in (a, c):
            b = api.book(mid)
            if b is None:
                continue
            px = b.best_bid if action is Action.SELL else b.best_ask
            if px is None:
                continue
            cands.append((px if action is Action.BUY else -px, mid, px))
        if not cands:
            return
        _, mid, px = min(cands)
        api.place(Order(mid, action, px, abs(net), tif=TIF.IOC, strategy=self.name))

    # -- maker mode ----------------------------------------------------------------
    def _maker(self, api: SimAPI, pid: str, ma: Market, mc: Market, ba: Book, bc: Book) -> None:
        k, pm = (ma, mc) if ma.venue is Venue.KALSHI else (mc, ma)
        if k.venue is not Venue.KALSHI:
            return
        kb, pb_ = (ba if k is ma else bc), (bc if k is ma else ba)
        # Rest a bid on Kalshi at price such that selling on Polymarket at its bid clears fees.
        hedge_sell = pb_.best_bid
        hedge_buy = pb_.best_ask
        fee_sell = taker_fee_per_contract(api, pm.market_id, hedge_sell)
        fee_buy = taker_fee_per_contract(api, pm.market_id, hedge_buy)
        # breakeven prices; any better price is still profitable, so clamp to one tick inside the touch
        bid_px = round_tick(min(hedge_sell - fee_sell - self.p.min_edge - self.p.hedge_pad,
                                kb.best_ask - self.p.tick), self.p.tick)
        ask_px = round_tick(max(hedge_buy + fee_buy + self.p.min_edge + self.p.hedge_pad,
                                kb.best_bid + self.p.tick), self.p.tick)
        net = api.position(k.market_id).contracts + api.position(pm.market_id).contracts
        cur = self.resting.get(k.market_id)
        live_ids = {o.order_id for o in api.open_orders(k.market_id)}
        if cur is not None and cur.order_id not in live_ids:
            cur = None
            self.resting.pop(k.market_id, None)
        want = None
        size = min(self.p.maker_size, self.p.depth_frac * pb_.bids[0].size)
        if bid_px >= kb.best_bid - 1e-9 and bid_px < kb.best_ask - 1e-9 and size >= self.p.min_size:
            want = (Action.BUY, bid_px, size)
        else:
            size = min(self.p.maker_size, self.p.depth_frac * pb_.asks[0].size)
            if ask_px <= kb.best_ask + 1e-9 and ask_px > kb.best_bid + 1e-9 and size >= self.p.min_size:
                want = (Action.SELL, ask_px, size)
        if want is None or abs(net) > 1e-9:
            if cur is not None:
                api.cancel(cur.order_id)
                self.resting.pop(k.market_id, None)
            return
        act, px, sz = want
        if cur is not None and cur.action is act and abs(cur.price - px) < 1e-9:
            return
        if cur is not None:
            api.cancel(cur.order_id)
        o = Order(k.market_id, act, px, sz, tif=TIF.GTC, post_only=True, strategy=self.name)
        api.place(o)
        self.resting[k.market_id] = o

    def on_fill(self, api: SimAPI, f: Fill) -> None:
        if self.p.mode != "maker_kalshi" or not f.is_maker:
            return
        pid = self.pair_of.get(f.market_id)
        if pid is None:
            return
        other = next((m for m in self.pairs[pid] if m != f.market_id), None)
        if other is None:
            return
        b = api.book(other)
        if b is None:
            return
        if f.action is Action.BUY and b.best_bid is not None:
            api.place(Order(other, Action.SELL, b.best_bid - self.p.slippage_pad, f.size, tif=TIF.IOC, strategy=self.name))
        elif f.action is Action.SELL and b.best_ask is not None:
            api.place(Order(other, Action.BUY, b.best_ask + self.p.slippage_pad, f.size, tif=TIF.IOC, strategy=self.name))
        self.opportunities.append({"ts": api.now, "pair": pid, "kind": "maker_fill", "size": f.size, "price": f.price})
        if self.p.flatten_unhedged:
            a, c = sorted(self.pairs[pid])
            api.schedule(1.0, lambda: self._flatten(api, a, c))
