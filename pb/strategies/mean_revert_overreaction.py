"""Model 9 — News-overreaction fade (post-only).

Mechanism
---------
On Kalshi/Polymarket single-name markets about 29% of moves >= 2c round-trip
within 4 h: the first wave of takers overshoots, then the price partially
reverts. We fade the move *as a maker*:

* Detect a jump: |mid_now - mid_{t-window}| >= `jump` (default 0.05 within
  `window` = 600 s) AND a print-rate spike (prints/sec over 60 s >=
  `print_rate_mult` * the trailing 10-min baseline, or at least
  `min_prints` prints in the window) so we only fade flow-driven moves, not
  quiet repricing (which is more likely to be real information).
* Rest a post-only order on the far side of the move: after an UP move we
  SELL at new_mid + `fade_frac` * move (at or above the ask), after a DOWN
  move we BID at new_mid + `fade_frac` * move (at or below the bid), i.e. we
  wait for the overshoot to come to us. Never cross the touch.
* Take profit when the mid retraces `tp_frac` of the move (post-only exit
  at the touch, then IOC fallback if `tp_taker` and still open after
  `tp_patience`); time-stop at `max_hold` (default 4 h): exit at the touch.
* Stop: if the move extends a further `stop_mult` * jump against us, exit.
* Disabled on crypto series (`disable_series_prefixes` default KXBTC/KXETH
  + "crypto") - 15-min crypto moves are information, not overreaction.
* One fade per market per `cooldown`.

Evidence: 29% of >= 2c moves round-trip within 4 h; makers earn the spread
on top; VPIN spikes predict maker losses so we cap size when VPIN is high
(`vpin_max`) rather than fade the most toxic flow.
Failure modes: the 71% that do not revert (we rely on the stop + the spread
earned), slow bleed on trending markets, resolution-driven jumps (we pull
within `pull_before_close`).

Targets: Kalshi politics/culture/econ single-name markets, Polymarket
politics; not crypto, not live sports.
"""
from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass, field

from pb.core.types import Action, Book, Fill, Order, TIF, Trade
from pb.sim.engine import Settlement, SimAPI, Strategy
from pb.strategies.base import Toxicity, clamp_size, register, round_tick, secs_to_close


@dataclass
class OverreactionParams:
    jump: float = 0.05
    window: float = 600.0
    print_rate_mult: float = 3.0
    min_prints: int = 5
    fade_frac: float = 0.3            # rest this fraction of the move beyond the new mid
    tp_frac: float = 0.5              # take profit after this fraction of the move reverts
    stop_mult: float = 1.0            # exit if the move extends by this * jump against us
    max_hold: float = 4 * 3600.0
    tp_patience: float = 120.0
    tp_taker: bool = True
    size: float = 10.0
    depth_frac_cap: float = 0.5
    vpin_max: float = 0.8
    cooldown: float = 1800.0
    pull_before_close: float = 3600.0
    price_band: tuple[float, float] = (0.05, 0.95)
    disable_series_prefixes: tuple[str, ...] = ("KXBTC", "KXETH", "KXSOL", "KXXRP", "KXDOGE", "crypto")
    tick: float = 0.01


@dataclass
class _Trade:
    entry_order: Order
    direction: int          # +1 = we are long after fade (faded a down-move), -1 short
    ref_mid: float          # pre-jump mid
    jump_mid: float         # post-jump mid
    opened: float
    exit_order: Order | None = None
    exit_since: float | None = None
    filled: float = 0.0


@register
class OverreactionFade(Strategy):
    name = "mean_revert_overreaction"

    def __init__(self, params: OverreactionParams | None = None, markets: list[str] | None = None):
        self.p = params or OverreactionParams()
        self.markets = set(markets or [])
        self.mids: dict[str, deque[tuple[float, float]]] = {}
        self.tox: dict[str, Toxicity] = {}
        self.trades: dict[str, _Trade] = {}
        self.last_fade: dict[str, float] = {}
        self.events: list[dict] = []

    def on_trade(self, api: SimAPI, t: Trade) -> None:
        self.tox.setdefault(t.market_id, Toxicity()).on_trade(t)

    def on_settlement(self, api: SimAPI, s: Settlement) -> None:
        tr = self.trades.pop(s.market_id, None)
        if tr is not None:
            api.cancel(tr.entry_order.order_id)
            if tr.exit_order is not None:
                api.cancel(tr.exit_order.order_id)

    def enabled(self, api: SimAPI, mid: str) -> bool:
        m = api.market(mid)
        if m is None:
            return True
        s = (m.series or m.market_id or "").upper()
        cat = str((m.meta or {}).get("category") or "").upper()
        pre = tuple(x.upper() for x in self.p.disable_series_prefixes)
        return not (s.startswith(pre) or cat.startswith(pre))

    def on_fill(self, api: SimAPI, f: Fill) -> None:
        tr = self.trades.get(f.market_id)
        if tr is None:
            return
        if f.order_id == tr.entry_order.order_id:
            tr.filled += f.size
        elif tr.exit_order is not None and f.order_id == tr.exit_order.order_id:
            if abs(api.position(f.market_id).contracts) < 1e-9:
                self.trades.pop(f.market_id, None)

    def on_book(self, api: SimAPI, b: Book) -> None:
        if self.markets and b.market_id not in self.markets:
            return
        mid = b.market_id
        if b.mid is None:
            return
        h = self.mids.setdefault(mid, deque(maxlen=5000))
        h.append((b.ts, b.mid))
        while h and b.ts - h[0][0] > self.p.window * 2:
            h.popleft()
        tr = self.trades.get(mid)
        if tr is not None:
            self._manage(api, b, tr)
            return
        if not self.enabled(api, mid):
            return
        if secs_to_close(api, mid) < self.p.pull_before_close:
            return
        if api.now - self.last_fade.get(mid, -math.inf) < self.p.cooldown:
            return
        self._detect(api, b, h)

    # -- entry ---------------------------------------------------------------------
    def _detect(self, api: SimAPI, b: Book, h: deque[tuple[float, float]]) -> None:
        p = self.p
        ref = next((m for t, m in h if b.ts - t <= p.window), None)
        if ref is None:
            return
        move = b.mid - ref
        if abs(move) < p.jump:
            return
        tox = self.tox.get(b.market_id)
        if tox is None:
            return
        recent = sum(1 for t in tox.prints if b.ts - t <= p.window)
        rate_now = tox.print_rate(b.ts, 60.0)
        base = max(1e-6, sum(1 for t in tox.prints if 60.0 < b.ts - t <= 660.0) / 600.0)
        if recent < p.min_prints or rate_now < p.print_rate_mult * base:
            return
        if tox.vpin > p.vpin_max:
            return
        if not (p.price_band[0] <= b.mid <= p.price_band[1]):
            return
        if move > 0:
            px = round_tick(max(b.mid + p.fade_frac * move, b.best_bid + p.tick), p.tick)
            px = max(px, b.best_ask)  # post-only: at or above the ask, never below
            act, direction, touch = Action.SELL, -1, b.asks[0].size
        else:
            px = round_tick(min(b.mid + p.fade_frac * move, b.best_ask - p.tick), p.tick)
            px = min(px, b.best_bid)
            act, direction, touch = Action.BUY, +1, b.bids[0].size
        sz = clamp_size(p.size, p.depth_frac_cap * touch)
        if sz <= 0:
            return
        o = Order(b.market_id, act, px, sz, tif=TIF.GTC, post_only=True, strategy=self.name)
        api.place(o)
        self.trades[b.market_id] = _Trade(o, direction, ref, b.mid, api.now)
        self.last_fade[b.market_id] = api.now
        self.events.append({"ts": api.now, "market": b.market_id, "move": move, "price": px, "size": sz})

    # -- management --------------------------------------------------------------------
    def _manage(self, api: SimAPI, b: Book, tr: _Trade) -> None:
        p = self.p
        mid = b.market_id
        pos = api.position(mid).contracts
        move = tr.jump_mid - tr.ref_mid
        reverted = (tr.jump_mid - b.mid) / move + 1e-9 if move else 0.0  # fraction of the move undone
        extended = (b.mid - tr.jump_mid) / move + 1e-9 if move else 0.0  # further in the move's direction
        held = api.now - tr.opened
        live = {o.order_id for o in api.open_orders(mid)}
        entry_live = tr.entry_order.order_id in live
        if abs(pos) < 1e-9:
            # not filled yet: cancel the entry if the move already reverted, the stop hit, or timed out
            if not entry_live:
                if tr.filled <= 0:
                    self.trades.pop(mid, None)
                return
            if reverted >= p.tp_frac or extended >= p.stop_mult or held > p.max_hold or \
                    secs_to_close(api, mid) < p.pull_before_close:
                api.cancel(tr.entry_order.order_id)
                self.trades.pop(mid, None)
            return
        # filled (at least partly): decide exit
        want_exit = reverted >= p.tp_frac or extended >= p.stop_mult or held > p.max_hold or \
            secs_to_close(api, mid) < p.pull_before_close
        if not want_exit:
            return
        if entry_live:
            api.cancel(tr.entry_order.order_id)
        act = Action.SELL if pos > 0 else Action.BUY
        urgent = extended >= p.stop_mult or secs_to_close(api, mid) < p.pull_before_close
        if tr.exit_order is None or tr.exit_order.order_id not in live:
            if tr.exit_order is not None and tr.exit_since is not None and \
                    (urgent or (p.tp_taker and api.now - tr.exit_since > p.tp_patience)):
                px = b.best_bid if act is Action.SELL else b.best_ask
                if px is not None:
                    api.place(Order(mid, act, px, abs(pos), tif=TIF.IOC, strategy=self.name))
                    tr.exit_since = api.now
                return
            px = b.best_ask if act is Action.SELL else b.best_bid   # join the touch, post-only
            o = Order(mid, act, px, abs(pos), tif=TIF.GTC, post_only=True, strategy=self.name)
            api.place(o)
            tr.exit_order = o
            tr.exit_since = tr.exit_since or api.now
        elif urgent or (p.tp_taker and tr.exit_since is not None and api.now - tr.exit_since > p.tp_patience):
            api.cancel(tr.exit_order.order_id)
            px = b.best_bid if act is Action.SELL else b.best_ask
            api.place(Order(mid, act, px, abs(pos), tif=TIF.IOC, strategy=self.name))
            tr.exit_order = None
            tr.exit_since = api.now
