"""Baseline T1 — Index-lag TAKER on Kalshi/Polymarket 15-min crypto windows.

Deliberately a taker strategy. The research says this loses after fees;
it is included so the backtest report proves or disproves that under
realistic (depth-walked, fee-charged, latency-applied) fills.

Mechanism: same P(up) model as mm_crypto_twap (index vs window open, normal
CDF over remaining time). When fair - best_ask > taker_fee(ask) + `edge`
we lift the ask with an IOC for min(`size`, `depth_frac` * depth within
`max_walk` cents); symmetric when best_bid - fair > fee + edge we hit the
bid (sell YES = buy NO). Positions are held to settlement (the trade thesis
is a mispriced settlement probability, not a scalp) unless `flatten_on_flip`
and the model flips against us by more than `flip_margin`.

Gates: signal staleness, last `no_trade_before_close` seconds (the book
is empty/sniped), per-window position cap, cooldown between takes.

Why it should lose: Kalshi taker fee 0.07*p(1-p) is 1.75c at p=0.5; the
book is quoted by makers who see the same index within ~1s; the gaps that
survive are adverse (our index is stale relative to BRTI/Chainlink).
Failure modes: all of the above plus paying the spread on every entry.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from pb.core.types import Action, Book, Market, Order, TIF
from pb.sim.engine import Fill, Settlement, Signal, SimAPI, Strategy
from pb.strategies.base import clamp_size, register, taker_fee_per_contract
from pb.strategies.mm_crypto_twap import CryptoMMParams, CryptoTwapMM


@dataclass
class TakerLagParams:
    edge: float = 0.02
    size: float = 10.0
    depth_frac: float = 0.5
    max_walk: float = 0.02
    max_position: float = 50.0
    cooldown: float = 5.0
    no_trade_before_close: float = 60.0
    signal_max_age: float = 5.0
    flatten_on_flip: bool = False
    flip_margin: float = 0.10
    vol_window: float = 900.0
    vol_floor: float = 0.00015
    index_signal: str | None = None


@register
class TakerLag(Strategy):
    name = "taker_lag"

    def __init__(self, params: TakerLagParams | None = None, markets: list[str] | None = None):
        self.p = params or TakerLagParams()
        self.markets = set(markets or [])
        self.model = CryptoTwapMM(CryptoMMParams(signal_max_age=self.p.signal_max_age, vol_window=self.p.vol_window,
                                                 vol_floor=self.p.vol_floor, index_signal=self.p.index_signal),
                                  markets)
        self.last: dict[str, float] = {}
        self.takes: list[dict] = []

    def on_start(self, api: SimAPI) -> None:
        self.model.on_start(api)
        self.model.qm = _NullQM()

    def on_signal(self, api: SimAPI, sig: Signal) -> None:
        self.model.on_signal(api, sig)
        for mid in list(self.model.windows):
            b = api.book(mid)
            if b is not None:
                self._maybe_take(api, b)

    def on_settlement(self, api: SimAPI, s: Settlement) -> None:
        self.model.on_settlement(api, s)

    def on_market_added(self, api: SimAPI, market: Market) -> None:
        if self.markets:
            self.markets.add(market.market_id)
        self.model.on_market_added(api, market)

    def on_market_removed(self, api: SimAPI, market_id: str) -> None:
        self.markets.discard(market_id)
        self.last.pop(market_id, None)
        self.model.on_market_removed(api, market_id)

    def on_book(self, api: SimAPI, b: Book) -> None:
        if self.markets and b.market_id not in self.markets:
            return
        self._maybe_take(api, b)

    def _maybe_take(self, api: SimAPI, b: Book) -> None:
        p = self.p
        mid = b.market_id
        w = self.model._window(api, mid)
        if w is None or b.best_ask is None or b.best_bid is None:
            return
        if w.close_ts - api.now < p.no_trade_before_close:
            return
        if api.now - self.last.get(mid, -math.inf) < p.cooldown:
            return
        fair, _ = self.model.fair(api, mid)
        if fair is None:
            return
        pos = api.position(mid).contracts
        if p.flatten_on_flip and pos != 0:
            if (pos > 0 and fair < 0.5 - p.flip_margin) or (pos < 0 and fair > 0.5 + p.flip_margin):
                act = Action.SELL if pos > 0 else Action.BUY
                px = b.best_bid if act is Action.SELL else b.best_ask
                api.place(Order(mid, act, px, abs(pos), tif=TIF.IOC, strategy=self.name))
                self.last[mid] = api.now
                return
        fee_a = taker_fee_per_contract(api, mid, b.best_ask)
        fee_b = taker_fee_per_contract(api, mid, b.best_bid)
        if fair - b.best_ask > fee_a + p.edge and pos < p.max_position:
            depth = b.depth_within(Action.BUY, p.max_walk)
            sz = clamp_size(p.size, p.depth_frac * depth, p.max_position - pos)
            if sz > 0:
                api.place(Order(mid, Action.BUY, b.best_ask + p.max_walk, sz, tif=TIF.IOC, strategy=self.name))
                self.last[mid] = api.now
                self.takes.append({"ts": api.now, "market": mid, "action": "buy", "fair": fair, "ask": b.best_ask})
        elif b.best_bid - fair > fee_b + p.edge and -pos < p.max_position:
            depth = b.depth_within(Action.SELL, p.max_walk)
            sz = clamp_size(p.size, p.depth_frac * depth, p.max_position + pos)
            if sz > 0:
                api.place(Order(mid, Action.SELL, b.best_bid - p.max_walk, sz, tif=TIF.IOC, strategy=self.name))
                self.last[mid] = api.now
                self.takes.append({"ts": api.now, "market": mid, "action": "sell", "fair": fair, "bid": b.best_bid})


class _NullQM:
    """Quote manager stub so the embedded model never rests orders."""

    def set(self, *a, **k) -> None: ...
    def pull(self, *a, **k) -> None: ...
    def pull_all(self) -> None: ...
