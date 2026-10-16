"""Reference signal producers -> `Signal` events (live async generators) plus
pure helpers that the backtester and the unit tests reuse.

Live producers (all async generators yielding `pb.sim.engine.Signal`):

* `coinbase_index(products)`   Coinbase Advanced Trade WS `market_trades`
                                channel -> `btc_index` / `eth_index`
* `kraken_index(pairs)`        Kraken WS v2 `trade` channel (fallback)
* `polymarket_twap()`          Polymarket free relay `crypto_prices_twap_sixty`
                                -> `twap60` (text "PING" every 5 s keeps it alive)
* `open_meteo_fcst_prob(...)`  ensemble daily-high members -> `fcst_prob` per
                                ladder rung (P(high in [lo, hi]) with a station
                                bias correction), polled
* `nws_latest_observation(...)` api.weather.gov latest obs (User-Agent required)
* `odds_api_sharp_prob(...)`   The Odds API h2h -> de-vigged `sharp_prob` and
                                `book_prob_<bookmaker>` per linked market, polled
* `espn_game_state(...)`       ESPN scoreboard -> `game_state` ("pre"/"in"/"post")

Pure helpers (no I/O): `KalshiCryptoWindow`, `devig_multiplicative`,
`devig_power`, `american_to_prob`, `decimal_to_prob`, `ensemble_rung_probs`,
`parse_coinbase_trade`, `parse_kraken_trade`, `parse_poly_twap`,
`sharp_signals_from_odds`.

Nothing here touches the network at import time. Network calls are made
through injected `httpx.AsyncClient` / websocket factories so tests can mock
them (see tests/test_feeds.py).
"""
from __future__ import annotations

import asyncio
import json
import logging
import math
import re
import statistics
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, AsyncIterator, Awaitable, Callable, Iterable, Optional
from zoneinfo import ZoneInfo

from pb.core.types import Market
from pb.sim.engine import Signal

log = logging.getLogger(__name__)

COINBASE_WS = "wss://advanced-trade-ws.coinbase.com"
KRAKEN_WS = "wss://ws.kraken.com/v2"
POLY_TWAP_WS = "wss://ws-live-data.polymarket.com"
OPEN_METEO_ENSEMBLE = "https://ensemble-api.open-meteo.com/v1/ensemble"
NWS_API = "https://api.weather.gov"
ODDS_API = "https://api.the-odds-api.com/v4"
ESPN_SCOREBOARD = "https://site.api.espn.com/apis/site/v2/sports"
NWS_USER_AGENT = "predictionbots/0.1 (machwonder@pm.me)"


# ----------------------------------------------------------------------------
# Kalshi 15-minute crypto window parsing
# ----------------------------------------------------------------------------
_TICKER_RE = re.compile(
    r"^(?P<series>KX(?P<asset>BTC|ETH|SOL|XRP|DOGE)(?P<dur>15M|1H|H|D|60M)?)"
    r"-(?P<yy>\d{2})(?P<mon>[A-Z]{3})(?P<dd>\d{2})(?P<hh>\d{2})(?P<mm>\d{2})"
    r"(?:-(?P<rest>.*))?$", re.I)
_MONTHS = {m: i for i, m in enumerate(
    ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"], 1)}
_DUR_SECS = {"15M": 900, "1H": 3600, "H": 3600, "60M": 3600, "D": 86400, None: 900}


@dataclass(frozen=True)
class KalshiCryptoWindow:
    """Open/close timestamps of a Kalshi short-horizon crypto market.

    Resolution order (`from_market`): explicit `meta["window_open_ts"]` /
    `meta["window_close_ts"]` > ticker parse (`KXBTC15M-26OCT161315-...`, the
    date-time is the window CLOSE in US/Eastern) > `Market.close_ts` minus the
    series duration. Never raises; `ok` is False when nothing could be inferred.
    """
    asset: str = ""
    open_ts: float = 0.0
    close_ts: float = 0.0
    duration: float = 900.0
    ok: bool = False
    source: str = ""

    @property
    def strike_signal(self) -> str:
        return f"{self.asset.lower()}_index" if self.asset else ""

    @classmethod
    def parse_ticker(cls, ticker: str, tz: str = "America/New_York") -> "KalshiCryptoWindow":
        m = _TICKER_RE.match((ticker or "").strip())
        if not m:
            return cls()
        try:
            dur = _DUR_SECS.get((m.group("dur") or "").upper() or None, 900)
            year = 2000 + int(m.group("yy"))
            mon = _MONTHS[m.group("mon").upper()]
            dt = datetime(year, mon, int(m.group("dd")), int(m.group("hh")), int(m.group("mm")),
                          tzinfo=ZoneInfo(tz))
            close = dt.timestamp()
            return cls(asset=m.group("asset").upper(), open_ts=close - dur, close_ts=close,
                       duration=float(dur), ok=True, source="ticker")
        except Exception:  # pragma: no cover - defensive
            return cls(asset=(m.group("asset") or "").upper())

    @classmethod
    def from_market(cls, market: Market, tz: str = "America/New_York") -> "KalshiCryptoWindow":
        meta = market.meta or {}
        asset = str(meta.get("asset") or "").upper()
        if not asset:
            for cand in (market.market_id, market.series):
                mm = re.match(r"^KX(BTC|ETH|SOL|XRP|DOGE)", (cand or "").upper())
                if mm:
                    asset = mm.group(1)
                    break
        wo, wc = meta.get("window_open_ts"), meta.get("window_close_ts")
        if wo is not None and wc is not None:
            try:
                wo, wc = float(wo), float(wc)
                if wc > wo:
                    return cls(asset=asset, open_ts=wo, close_ts=wc, duration=wc - wo, ok=True, source="meta")
            except (TypeError, ValueError):
                pass
        parsed = cls.parse_ticker(market.market_id, tz)
        if parsed.ok:
            if market.close_ts and abs(market.close_ts - parsed.close_ts) > 2 * parsed.duration:
                # ticker disagrees badly with venue close_ts: trust venue, keep duration
                return cls(asset=asset or parsed.asset, open_ts=market.close_ts - parsed.duration,
                           close_ts=market.close_ts, duration=parsed.duration, ok=True, source="close_ts")
            return cls(asset=asset or parsed.asset, open_ts=parsed.open_ts, close_ts=parsed.close_ts,
                       duration=parsed.duration, ok=True, source="ticker")
        if market.close_ts:
            dur = float(meta.get("window_secs") or 900.0)
            return cls(asset=asset, open_ts=market.close_ts - dur, close_ts=market.close_ts,
                       duration=dur, ok=True, source="close_ts")
        return cls(asset=asset)


# ----------------------------------------------------------------------------
# Crypto spot indices
# ----------------------------------------------------------------------------
_PRODUCT_SIGNAL = {"BTC-USD": "btc_index", "ETH-USD": "eth_index", "BTC/USD": "btc_index",
                   "ETH/USD": "eth_index", "SOL-USD": "sol_index", "SOL/USD": "sol_index"}


def parse_coinbase_trade(msg: dict) -> list[Signal]:
    """Coinbase Advanced Trade `market_trades` message -> Signals (last price)."""
    out: list[Signal] = []
    if msg.get("channel") != "market_trades":
        return out
    for ev in msg.get("events", []):
        for t in ev.get("trades", []):
            pid = t.get("product_id", "")
            name = _PRODUCT_SIGNAL.get(pid)
            if not name:
                continue
            try:
                px = float(t["price"])
                ts = _iso_ts(t.get("time")) or time.time()
            except (KeyError, TypeError, ValueError):
                continue
            out.append(Signal(ts=ts, name=name, market_id=None,
                              value={"price": px, "size": float(t.get("size", 0) or 0), "src": "coinbase"}))
    return out


def parse_kraken_trade(msg: dict) -> list[Signal]:
    """Kraken WS v2 `trade` message -> Signals."""
    out: list[Signal] = []
    if msg.get("channel") != "trade":
        return out
    for t in msg.get("data", []):
        name = _PRODUCT_SIGNAL.get(t.get("symbol", ""))
        if not name:
            continue
        try:
            px = float(t["price"])
            ts = _iso_ts(t.get("timestamp")) or time.time()
        except (KeyError, TypeError, ValueError):
            continue
        out.append(Signal(ts=ts, name=name, market_id=None,
                          value={"price": px, "size": float(t.get("qty", 0) or 0), "src": "kraken"}))
    return out


def parse_poly_twap(msg: Any) -> list[Signal]:
    """Polymarket live-data relay message (topic crypto_prices_twap_sixty) -> `twap60`.
    The payload shape has changed before; we look for a symbol and a value
    anywhere reasonable and otherwise drop the message."""
    if isinstance(msg, str):
        if msg.strip().upper() in ("PONG", "PING", ""):
            return []
        try:
            msg = json.loads(msg)
        except ValueError:
            return []
    if not isinstance(msg, dict):
        return []
    topic = str(msg.get("topic") or msg.get("type") or "")
    if "twap" not in topic.lower():
        return []
    payload = msg.get("payload") or msg.get("data") or msg
    items = payload if isinstance(payload, list) else [payload]
    out = []
    for it in items:
        if not isinstance(it, dict):
            continue
        sym = str(it.get("symbol") or it.get("asset") or it.get("pair") or "").upper()
        asset = sym.replace("USDT", "").replace("USD", "").replace("/", "").replace("-", "")
        val = it.get("twap") or it.get("value") or it.get("price")
        try:
            val = float(val)
        except (TypeError, ValueError):
            continue
        ts = it.get("timestamp") or it.get("ts") or msg.get("timestamp")
        ts = _any_ts(ts) or time.time()
        out.append(Signal(ts=ts, name="twap60", market_id=None,
                          value={"asset": asset, "twap": val, "src": "polymarket"}))
    return out


async def _ws_messages(url: str, subscribe: Any, ws_factory: Callable[..., Any] | None = None,
                       ping_text: str | None = None, ping_every: float = 5.0,
                       reconnect_delay: float = 2.0) -> AsyncIterator[Any]:
    """Generic reconnecting websocket reader. `ws_factory(url)` must return an
    async context manager yielding an object with `send` and async iteration."""
    if ws_factory is None:
        import websockets  # lazy

        ws_factory = websockets.connect
    while True:
        try:
            async with ws_factory(url) as ws:
                if subscribe is not None:
                    await ws.send(json.dumps(subscribe) if not isinstance(subscribe, str) else subscribe)
                pinger = None
                if ping_text:
                    async def _ping():
                        while True:
                            await asyncio.sleep(ping_every)
                            await ws.send(ping_text)
                    pinger = asyncio.create_task(_ping())
                try:
                    async for raw in ws:
                        yield raw
                finally:
                    if pinger:
                        pinger.cancel()
        except asyncio.CancelledError:
            raise
        except Exception as e:  # pragma: no cover - network
            log.warning("ws %s error: %s; reconnecting", url, e)
            await asyncio.sleep(reconnect_delay)


async def coinbase_index(products: Iterable[str] = ("BTC-USD", "ETH-USD"),
                         ws_factory: Callable[..., Any] | None = None) -> AsyncIterator[Signal]:
    sub = {"type": "subscribe", "product_ids": list(products), "channel": "market_trades"}
    async for raw in _ws_messages(COINBASE_WS, sub, ws_factory):
        try:
            msg = json.loads(raw) if isinstance(raw, (str, bytes)) else raw
        except ValueError:
            continue
        for s in parse_coinbase_trade(msg):
            yield s


async def kraken_index(pairs: Iterable[str] = ("BTC/USD", "ETH/USD"),
                       ws_factory: Callable[..., Any] | None = None) -> AsyncIterator[Signal]:
    sub = {"method": "subscribe", "params": {"channel": "trade", "symbol": list(pairs)}}
    async for raw in _ws_messages(KRAKEN_WS, sub, ws_factory):
        try:
            msg = json.loads(raw) if isinstance(raw, (str, bytes)) else raw
        except ValueError:
            continue
        for s in parse_kraken_trade(msg):
            yield s


async def polymarket_twap(ws_factory: Callable[..., Any] | None = None) -> AsyncIterator[Signal]:
    sub = {"action": "subscribe", "subscriptions": [{"topic": "crypto_prices_twap_sixty", "type": "*"}]}
    async for raw in _ws_messages(POLY_TWAP_WS, sub, ws_factory, ping_text="PING", ping_every=5.0):
        for s in parse_poly_twap(raw if isinstance(raw, str) else raw.decode() if isinstance(raw, bytes) else raw):
            yield s


async def index_with_fallback(primary: AsyncIterator[Signal], fallback_factory: Callable[[], AsyncIterator[Signal]],
                              stale_after: float = 15.0) -> AsyncIterator[Signal]:
    """Yield from `primary`; if it goes quiet for `stale_after` seconds switch to
    the fallback generator (and keep the primary in case it recovers)."""
    q: asyncio.Queue = asyncio.Queue()

    async def pump(gen, tag):
        async for s in gen:
            await q.put((tag, s))

    tp = asyncio.create_task(pump(primary, "p"))
    tf: Optional[asyncio.Task] = None
    last_primary = time.time()
    try:
        while True:
            try:
                tag, s = await asyncio.wait_for(q.get(), timeout=stale_after)
            except asyncio.TimeoutError:
                if tf is None:
                    tf = asyncio.create_task(pump(fallback_factory(), "f"))
                continue
            if tag == "p":
                last_primary = time.time()
                yield s
            elif time.time() - last_primary > stale_after:
                yield s
    finally:
        tp.cancel()
        if tf:
            tf.cancel()


# ----------------------------------------------------------------------------
# Weather: Open-Meteo ensemble -> P(high in rung)
# ----------------------------------------------------------------------------
def ensemble_rung_probs(members: Iterable[float], rungs: list[tuple[float | None, float | None]],
                        bias: float = 0.0, spread_scale: float = 1.0,
                        min_prob: float = 0.005) -> list[float]:
    """P(daily high falls in each [lo, hi] rung) from ensemble members.

    `bias` is added to every member (station - model climatology, degrees F).
    `spread_scale` inflates member dispersion around their mean (ensembles are
    under-dispersive; 1.2-1.5 is typical). A rung with lo=None is "below hi",
    hi=None is "above lo" (Kalshi ladders: lo <= T <= hi inclusive on integers,
    so we treat the bins as [lo-0.5, hi+0.5) on the continuous scale).
    A tiny Gaussian kernel per member smooths the empirical distribution."""
    xs = [float(m) + bias for m in members if m is not None and not math.isnan(float(m))]
    if not xs:
        return [float("nan")] * len(rungs)
    mu = statistics.fmean(xs)
    xs = [mu + spread_scale * (x - mu) for x in xs]
    sd = statistics.pstdev(xs) if len(xs) > 1 else 1.0
    h = max(0.3, 0.6 * sd * len(xs) ** (-0.2))  # Silverman-ish kernel width

    def cdf(x: float) -> float:
        return sum(0.5 * (1 + math.erf((x - m) / (h * math.sqrt(2)))) for m in xs) / len(xs)

    out = []
    for lo, hi in rungs:
        a = -math.inf if lo is None else lo - 0.5
        b = math.inf if hi is None else hi + 0.5
        pa = 0.0 if a == -math.inf else cdf(a)
        pb_ = 1.0 if b == math.inf else cdf(b)
        out.append(min(1 - min_prob, max(min_prob, pb_ - pa)))
    return out


def parse_rung(market: Market) -> Optional[tuple[float | None, float | None]]:
    """Rung bounds from `Market.meta` (`rung_lo`/`rung_hi`, or `floor_strike`/
    `cap_strike` as Kalshi calls them) or the title/subtitle ("72° to 73°",
    "74° or above", "69° or below")."""
    meta = market.meta or {}
    lo = meta.get("rung_lo", meta.get("floor_strike"))
    hi = meta.get("rung_hi", meta.get("cap_strike"))
    if lo is not None or hi is not None:
        return (None if lo is None else float(lo), None if hi is None else float(hi))
    text = f"{market.title} {meta.get('subtitle', '')}"
    m = re.search(r"(-?\d+(?:\.\d+)?)°?\s*(?:to|-)\s*(-?\d+(?:\.\d+)?)°?", text)
    if m:
        return float(m.group(1)), float(m.group(2))
    m = re.search(r"(-?\d+(?:\.\d+)?)°?\s*or\s*(above|higher|more)", text, re.I)
    if m:
        return float(m.group(1)), None
    m = re.search(r"(-?\d+(?:\.\d+)?)°?\s*or\s*(below|lower|less)", text, re.I)
    if m:
        return None, float(m.group(1))
    return None


def open_meteo_members(payload: dict, day_index: int = 0, var: str = "temperature_2m_max") -> list[float]:
    """Pull `<var>_member01..` (and the control run `<var>`) for one day."""
    daily = payload.get("daily", {})
    out = []
    for k, v in daily.items():
        if k == var or k.startswith(var + "_member"):
            if isinstance(v, list) and len(v) > day_index and v[day_index] is not None:
                out.append(float(v[day_index]))
    return out


async def open_meteo_fcst_prob(client: Any, markets: list[Market], latitude: float, longitude: float,
                               tz: str = "America/New_York", bias: float = 0.0, spread_scale: float = 1.2,
                               poll_secs: float = 900.0, models: str = "gfs025,ecmwf_ifs025",
                               target_date: Optional[str] = None, once: bool = False,
                               sleep: Callable[[float], Awaitable[None]] = asyncio.sleep) -> AsyncIterator[Signal]:
    """Poll the Open-Meteo ensemble API and emit `fcst_prob` per rung market.
    `markets` must carry rung bounds (see `parse_rung`). `client` is an
    httpx.AsyncClient-like object with `get(url, params=...)`."""
    rungs = [(m, parse_rung(m)) for m in markets]
    rungs = [(m, r) for m, r in rungs if r is not None]
    params = {"latitude": latitude, "longitude": longitude, "daily": "temperature_2m_max",
              "models": models, "forecast_days": 7, "temperature_unit": "fahrenheit", "timezone": tz}
    while True:
        try:
            r = await client.get(OPEN_METEO_ENSEMBLE, params=params)
            data = r.json()
            dates = data.get("daily", {}).get("time", [])
            idx = 0
            if target_date and target_date in dates:
                idx = dates.index(target_date)
            members = open_meteo_members(data, idx)
            probs = ensemble_rung_probs(members, [r for _, r in rungs], bias=bias, spread_scale=spread_scale)
            now = time.time()
            for (m, _), p in zip(rungs, probs):
                yield Signal(ts=now, name="fcst_prob", market_id=m.market_id, value=p)
            if members:
                yield Signal(ts=now, name="fcst_members", market_id=None,
                             value={"n": len(members), "mean": statistics.fmean(members),
                                    "sd": statistics.pstdev(members) if len(members) > 1 else 0.0})
        except Exception as e:  # pragma: no cover - network
            log.warning("open-meteo poll failed: %s", e)
        if once:
            return
        await sleep(poll_secs)


async def nws_latest_observation(client: Any, station: str) -> Optional[dict]:
    """GET /stations/{station}/observations/latest -> {"ts", "temp_f", "raw"}."""
    r = await client.get(f"{NWS_API}/stations/{station}/observations/latest",
                         headers={"User-Agent": NWS_USER_AGENT, "Accept": "application/geo+json"})
    data = r.json()
    props = data.get("properties", {})
    t = props.get("temperature", {}) or {}
    val = t.get("value")
    if val is None:
        return None
    unit = str(t.get("unitCode", "wmoUnit:degC"))
    temp_f = val * 9 / 5 + 32 if "degC" in unit else float(val)
    return {"ts": _iso_ts(props.get("timestamp")) or time.time(), "temp_f": temp_f, "raw": props}


async def nws_observation_signal(client: Any, station: str, market_ids: Iterable[str] | None = None,
                                 poll_secs: float = 300.0, once: bool = False,
                                 sleep: Callable[[float], Awaitable[None]] = asyncio.sleep) -> AsyncIterator[Signal]:
    """Poll NWS and emit `obs_temp_f` (global) and the running `obs_high_f`."""
    hi = -math.inf
    while True:
        try:
            ob = await nws_latest_observation(client, station)
            if ob is not None:
                hi = max(hi, ob["temp_f"])
                yield Signal(ts=ob["ts"], name="obs_temp_f", market_id=None, value=ob["temp_f"])
                yield Signal(ts=ob["ts"], name="obs_high_f", market_id=None, value=hi)
        except Exception as e:  # pragma: no cover - network
            log.warning("nws poll failed: %s", e)
        if once:
            return
        await sleep(poll_secs)


# ----------------------------------------------------------------------------
# Sports: The Odds API -> de-vigged sharp probability
# ----------------------------------------------------------------------------
def american_to_prob(odds: float) -> float:
    odds = float(odds)
    return 100 / (odds + 100) if odds > 0 else -odds / (-odds + 100)


def decimal_to_prob(odds: float) -> float:
    return 1.0 / float(odds)


def devig_multiplicative(implied: list[float]) -> list[float]:
    s = sum(implied)
    return [p / s for p in implied] if s > 0 else implied


def devig_power(implied: list[float], tol: float = 1e-10, max_iter: int = 100) -> list[float]:
    """Power method: find k such that sum(p_i ** k) == 1 (bisection on k)."""
    if any(p <= 0 or p >= 1 for p in implied) or len(implied) < 2:
        return devig_multiplicative(implied)
    lo, hi = 0.5, 5.0
    for _ in range(max_iter):
        k = (lo + hi) / 2
        s = sum(p ** k for p in implied)
        if abs(s - 1) < tol:
            break
        if s > 1:
            lo = k
        else:
            hi = k
    k = (lo + hi) / 2
    out = [p ** k for p in implied]
    s = sum(out)
    return [p / s for p in out]


def devig(implied: list[float], method: str = "power") -> list[float]:
    return devig_power(implied) if method == "power" else devig_multiplicative(implied)


@dataclass
class OddsLink:
    """Maps an odds-API event/outcome to a prediction market."""
    market_id: str
    home_team: str
    away_team: str
    outcome: str            # team name whose win == YES (or "Draw")
    sport: str = ""


def sharp_signals_from_odds(events: list[dict], links: list[OddsLink], now: float,
                            sharp_books: tuple[str, ...] = ("pinnacle",), method: str = "power",
                            consensus: tuple[str, ...] = ("pinnacle", "draftkings", "fanduel")) -> list[Signal]:
    """The Odds API `/sports/{sport}/odds` payload + links -> Signals.
    Emits `book_prob_<bk>` for every bookmaker and `sharp_prob` = Pinnacle if
    present else the mean of the consensus books."""
    out: list[Signal] = []
    for ev in events:
        home, away = str(ev.get("home_team", "")), str(ev.get("away_team", ""))
        for ln in links:
            if not (_team_eq(ln.home_team, home) and _team_eq(ln.away_team, away)):
                continue
            book_probs: dict[str, float] = {}
            for bk in ev.get("bookmakers", []):
                key = str(bk.get("key", "")).lower()
                for mk in bk.get("markets", []):
                    if mk.get("key") != "h2h":
                        continue
                    outs = mk.get("outcomes", [])
                    names = [str(o.get("name", "")) for o in outs]
                    try:
                        prices = [float(o["price"]) for o in outs]
                    except (KeyError, TypeError, ValueError):
                        continue
                    # The Odds API returns decimal by default; american if requested.
                    if any(abs(x) >= 100 for x in prices):
                        implied = [american_to_prob(x) for x in prices]
                    else:
                        implied = [decimal_to_prob(x) for x in prices if x > 0]
                    if len(implied) != len(names):
                        continue
                    fair = devig(implied, method)
                    for nm, p in zip(names, fair):
                        if _team_eq(nm, ln.outcome):
                            book_probs[key] = p
                            out.append(Signal(ts=now, name=f"book_prob_{key}", market_id=ln.market_id, value=p))
            sharp = next((book_probs[b] for b in sharp_books if b in book_probs), None)
            if sharp is None:
                cons = [book_probs[b] for b in consensus if b in book_probs]
                sharp = statistics.fmean(cons) if cons else None
            if sharp is not None:
                out.append(Signal(ts=now, name="sharp_prob", market_id=ln.market_id,
                                  value={"p": sharp, "books": dict(book_probs),
                                         "commence_ts": _iso_ts(ev.get("commence_time"))}))
    return out


async def odds_api_sharp_prob(client: Any, api_key: str, sport: str, links: list[OddsLink],
                              poll_secs: float = 60.0, once: bool = False, regions: str = "us,eu",
                              bookmakers: str = "pinnacle,draftkings,fanduel",
                              sleep: Callable[[float], Awaitable[None]] = asyncio.sleep) -> AsyncIterator[Signal]:
    params = {"apiKey": api_key, "regions": regions, "markets": "h2h", "bookmakers": bookmakers,
              "oddsFormat": "decimal"}
    while True:
        try:
            r = await client.get(f"{ODDS_API}/sports/{sport}/odds", params=params)
            for s in sharp_signals_from_odds(r.json(), links, time.time()):
                yield s
        except Exception as e:  # pragma: no cover - network
            log.warning("odds api poll failed: %s", e)
        if once:
            return
        await sleep(poll_secs)


def parse_espn_scoreboard(payload: dict) -> dict[str, dict]:
    """ESPN scoreboard JSON -> {event_id: {"state", "home", "away", "period", "clock", "ts"}}."""
    out = {}
    for ev in payload.get("events", []):
        comp = (ev.get("competitions") or [{}])[0]
        st = (comp.get("status") or ev.get("status") or {}).get("type", {})
        teams = {c.get("homeAway"): (c.get("team") or {}).get("displayName", "") for c in comp.get("competitors", [])}
        out[str(ev.get("id"))] = {
            "state": str(st.get("state", "pre")),  # pre / in / post
            "completed": bool(st.get("completed", False)),
            "home": teams.get("home", ""), "away": teams.get("away", ""),
            "period": (comp.get("status") or {}).get("period"),
            "clock": (comp.get("status") or {}).get("displayClock"),
            "ts": _iso_ts(ev.get("date")),
        }
    return out


async def espn_game_state(client: Any, sport_path: str, links: list[OddsLink], poll_secs: float = 60.0,
                          once: bool = False,
                          sleep: Callable[[float], Awaitable[None]] = asyncio.sleep) -> AsyncIterator[Signal]:
    """`sport_path` like "football/nfl". Emits `game_state` per linked market."""
    while True:
        try:
            r = await client.get(f"{ESPN_SCOREBOARD}/{sport_path}/scoreboard")
            games = parse_espn_scoreboard(r.json())
            now = time.time()
            for g in games.values():
                for ln in links:
                    if _team_eq(ln.home_team, g["home"]) and _team_eq(ln.away_team, g["away"]):
                        yield Signal(ts=now, name="game_state", market_id=ln.market_id, value=g["state"])
        except Exception as e:  # pragma: no cover - network
            log.warning("espn poll failed: %s", e)
        if once:
            return
        await sleep(poll_secs)


# ----------------------------------------------------------------------------
# Backtest helpers: turn recorded reference series into Signal events
# ----------------------------------------------------------------------------
def signals_from_rows(rows: Iterable[dict], name: str, ts_key: str = "ts", value_key: str = "value",
                      market_key: str | None = "market_id") -> list[Signal]:
    out = []
    for r in rows:
        mid = r.get(market_key) if market_key else None
        out.append(Signal(ts=float(r[ts_key]), name=name, market_id=mid, value=r[value_key]))
    out.sort(key=lambda s: s.ts)
    return out


def index_signals_from_prices(prices: Iterable[tuple[float, float]], name: str = "btc_index") -> list[Signal]:
    return [Signal(ts=float(t), name=name, market_id=None, value=float(p)) for t, p in prices]


# ----------------------------------------------------------------------------
# small utils
# ----------------------------------------------------------------------------
def _iso_ts(s: Any) -> Optional[float]:
    if not s:
        return None
    try:
        s = str(s).replace("Z", "+00:00")
        return datetime.fromisoformat(s).timestamp()
    except ValueError:
        return None


def _any_ts(v: Any) -> Optional[float]:
    if v is None:
        return None
    try:
        f = float(v)
        return f / 1000 if f > 1e11 else f
    except (TypeError, ValueError):
        return _iso_ts(v)


def _team_eq(a: str, b: str) -> bool:
    na = re.sub(r"[^a-z0-9]", "", (a or "").lower())
    nb = re.sub(r"[^a-z0-9]", "", (b or "").lower())
    return bool(na) and (na == nb or na in nb or nb in na)


def signal_price(sig: Signal) -> Optional[float]:
    """Numeric price out of an index/twap signal value (float or dict)."""
    v = sig.value
    if isinstance(v, dict):
        for k in ("price", "twap", "p", "value"):
            if k in v:
                try:
                    return float(v[k])
                except (TypeError, ValueError):
                    return None
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None
