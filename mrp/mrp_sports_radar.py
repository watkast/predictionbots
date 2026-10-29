#!/usr/bin/env python3
"""
Mr. P — sports radar v0.2 (read-only; public endpoints only; no keys; never places orders).

Scans the sports catalogue of Polymarket US and Kalshi for "clunkiness gaps" — places where a
contract's outcome is already known, or two prices contradict each other — and records enough
tape to fingerprint who is quoting each market (humans vs bots) offline.

Every cycle (default 60 s):
  Polymarket US  GET /v1/events?live=true                 in-play games: score, period, every market's BBO
                 GET /v1/events?ended=true&closed=false   games that finished but whose markets are still open
                 GET /v1/events?active=true&closed=false&startTimeMin/Max   (every 10 min) near-term universe
                 GET /v1/events?closed=true&finishedTimestampMin            (hourly) how fast markets close
                 GET /v1/events?active=true&closed=false (all pages)        (hourly) inventory
  Kalshi         GET /markets?min_close_ts=now-1h&max_close_ts=now+6h      near-term markets, any status
                 GET /markets?status=settled&min_settled_ts=now-2h         settlements (for lag detection)
                 GET /events/{ticker}                                      event metadata, cached (MECNET flag)
                 GET /series?category=Sports                               the sports series set (hourly)

Detectors (every cycle; each hit is re-checked against a fresh BBO call where the venue offers one):
  dead_pm        Polymarket event ended / score decides a total, market still quoting away from 0/1
  lag_k_settled  Kalshi finalized a game; the matched Polymarket market still trades
  dutch_k        Kalshi MECNET event: sum of YES asks < 1 - fees  (or sum of YES bids > 1 + fees)
  dutch_pm       Polymarket event: a group of >= 2 one-sided outcome markets whose asks sum < 1 - fees
  xvenue         matched moneyline, buy on one venue / sell on the other, positive after both fees

Records (JSONL, same Writer/format as the recorder):
  sp.start sp.stop  err
  sp.pm.event    compact Polymarket event + markets (live / ended-open / near-term)
  sp.pm.closed   recently closed Polymarket events: finishedTimestamp vs closedTime per sport
  sp.k.market    compact Kalshi near-term market (status, result, prices, sizes)
  sp.k.event     Kalshi event metadata (once per event)
  sp.k.settled   Kalshi markets settled in the last 2 h
  sp.k.series    the sports series set
  sp.match       a Polymarket event paired with a Kalshi event (once per pair)
  sp.opp         an opportunity with margin after fees, depth, first_seen, persist_s, fresh-BBO confirmation
  sp.inventory   hourly catalogue summary per venue/sport/market type
  sp.sample      one raw object per venue (schema reference)
"""
from __future__ import annotations

import json
import os
import re
import signal
import statistics
import sys
import threading
import time
from datetime import datetime, timezone
from typing import Any, Optional

import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mrp_recorder as R  # Writer, parse_ts, log, hosts, .env  # noqa: E402

W = R.W
log = R.log
PMUS_BASE = R.PMUS_BASE
KALSHI_REST = R.KALSHI_REST + "/trade-api/v2"
CYCLE = float(os.environ.get("MRP_RADAR_CYCLE", "60"))
NEAR_EVERY = float(os.environ.get("MRP_RADAR_NEAR_SECONDS", "600"))
INV_EVERY = float(os.environ.get("MRP_RADAR_INVENTORY_SECONDS", "3600"))
MAX_PAGES = int(os.environ.get("MRP_RADAR_MAX_PAGES", "60"))
REQ_GAP = float(os.environ.get("MRP_RADAR_REQ_GAP", "0.2"))           # >= 200 ms between requests per venue
MIN_MARGIN = float(os.environ.get("MRP_RADAR_MIN_MARGIN", "0.004"))    # $ per contract after fees
PM_FEE_DEFAULT, K_FEE_DEFAULT = 0.07, 0.07
STOP = threading.Event()
SESS = requests.Session()
SESS.headers["User-Agent"] = "mrp-sports-radar/0.2 (read-only)"
BYTES = {"pm": 0, "k": 0}
CALLS = {"pm": 0, "k": 0}
_last_call = {"pm": 0.0, "k": 0.0}


# ----------------------------------------------------------------------------- http
def get(venue: str, url: str, params: Any = None, timeout: float = 20.0) -> Any:
    gap = REQ_GAP - (time.time() - _last_call[venue])
    if gap > 0:
        time.sleep(gap)
    _last_call[venue] = time.time()
    r = None
    for attempt in range(3):
        r = SESS.get(url, params=params, timeout=timeout)
        CALLS[venue] += 1
        BYTES[venue] += len(r.content or b"")
        if r.status_code == 429 or r.status_code >= 500:
            time.sleep(1.5 * (attempt + 1))
            continue
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json()
    raise RuntimeError(f"{venue} {url} -> {r.status_code} {r.text[:120]}")


def f(v: Any) -> Optional[float]:
    if isinstance(v, dict):
        v = v.get("value")
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def iso(t: float) -> str:
    return datetime.fromtimestamp(t, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fee(theta: float, p: float) -> float:
    return theta * p * (1 - p)


STOP_WORDS = {"the", "vs", "at", "and", "of", "fc", "win", "wins", "will", "match", "game", "winner", "beat", "to", "in",
              "men", "women", "mens", "womens", "team", "club", "united", "city", "real", "de", "la", "le", "los", "las",
              "yes", "no", "or", "draw", "tie", "total", "over", "under", "spread", "moneyline", "points", "sets"}


def tokens(s: Any) -> set:
    return {w for w in re.sub(r"[^a-z0-9 ]", " ", str(s or "").lower()).split() if len(w) >= 3 and w not in STOP_WORDS}


def team_sides(title: str) -> list[str]:
    parts = re.split(r"\s+(?:vs\.?|v\.?|@|at|-)\s+", title or "", flags=re.I)
    return [p.strip() for p in parts][:2] if len(parts) >= 2 else []


# ----------------------------------------------------------------------------- Polymarket US
def pm_page(params: dict, max_pages: int = MAX_PAGES) -> list[dict]:
    out = []
    for page in range(max_pages):
        q = dict(params, limit=200, offset=page * 200)
        data = get("pm", PMUS_BASE + "/v1/events", params=q)
        evs = (data or {}).get("events") or []
        out.extend(evs)
        if len(evs) < 200:
            break
    return out


def pm_sport(ev: dict) -> tuple[str, str]:
    sport, league = "", ""
    for t in ev.get("tags") or []:
        sp, lg = t.get("sport"), t.get("league")
        if isinstance(sp, dict) and not sport:
            sport = str(sp.get("slug") or sp.get("name") or sp.get("label") or "")
        if isinstance(lg, dict) and not league:
            league = str(lg.get("slug") or lg.get("name") or lg.get("label") or "")
    if not sport:
        sport = str(ev.get("category") or "")
    if not league:
        league = str(ev.get("subcategory") or ev.get("seriesSlug") or "")
    return sport.lower(), league.lower()


NON_SPORT = ("crypto", "politics", "finance", "economics", "culture", "pop-culture", "science", "weather", "business", "tech")


def pm_is_sport(ev: dict) -> bool:
    if ev.get("gameId") or ev.get("sportradarGameId") or ev.get("eventState"):
        return True
    sport, _ = pm_sport(ev)
    if sport and sport not in NON_SPORT:
        return True
    return any(isinstance(t.get("sport"), dict) or isinstance(t.get("league"), dict) for t in ev.get("tags") or [])


def pm_compact(ev: dict) -> dict:
    es = ev.get("eventState") or {}
    mk = []
    for m in ev.get("markets") or []:
        sides = []
        for s in m.get("marketSides") or []:
            sides.append({"long": s.get("long"), "px": f(s.get("price")) if s.get("price") is not None else f(s.get("quote")),
                          "desc": (s.get("description") or "")[:40], "team": s.get("teamId"), "tr": s.get("tradable")})
        mk.append({"id": m.get("id"), "slug": m.get("slug"), "q": (m.get("question") or m.get("title") or "")[:90],
                   "type": m.get("sportsMarketType") or m.get("marketType"), "line": f(m.get("line")),
                   "status": str(m.get("status") or "").replace("MARKET_STATUS_", ""), "active": m.get("active"),
                   "closed": m.get("closed"), "bid": f(m.get("bestBidQuote")), "ask": f(m.get("bestAskQuote")),
                   "fee": f(m.get("feeCoefficient")), "tick": f(m.get("orderPriceMinTickSize")),
                   "vol24": f(m.get("volume24hr")), "vol": f(m.get("volume")), "sides": sides})
    sport, league = pm_sport(ev)
    return {"id": ev.get("id"), "slug": ev.get("slug"), "title": (ev.get("title") or "")[:100], "sport": sport, "league": league,
            "gameId": ev.get("gameId"), "live": ev.get("live") if ev.get("live") is not None else es.get("live"),
            "ended": ev.get("ended") if ev.get("ended") is not None else es.get("ended"),
            "score": ev.get("score") or es.get("score"), "period": ev.get("period") or es.get("period"),
            "elapsed": ev.get("elapsed") or es.get("elapsed"), "start": ev.get("startTime") or ev.get("startDate"),
            "finished": ev.get("finishedTimestamp") or es.get("finishedTimestamp"), "closedTime": ev.get("closedTime"),
            "closed": ev.get("closed"), "active": ev.get("active"), "vol24": f(ev.get("volume24hr")), "liq": f(ev.get("liquidity")),
            "oi": f(ev.get("openInterest")),
            "teams": [{"id": t.get("id"), "name": (t.get("name") or "")[:40], "abbr": t.get("abbreviation")} for t in (ev.get("teams") or [])][:4],
            "periodScores": es.get("periodScores"), "markets": mk}


def pm_bbo(slug: str) -> Optional[dict]:
    data = get("pm", f"{PMUS_BASE}/v1/markets/{slug}/bbo")
    if not data:
        return None
    b = data.get("bbo") or data.get("marketBBO") or data
    return {"slug": slug, "bid": f(b.get("bestBid")), "ask": f(b.get("bestAsk")), "bidDepth": b.get("bidDepth"),
            "askDepth": b.get("askDepth"), "last": f(b.get("lastTradePx")), "oi": b.get("openInterest")}


# ----------------------------------------------------------------------------- Kalshi
class Kalshi:
    def __init__(self):
        self.series: dict[str, dict] = {}
        self.series_at = 0.0
        self.events: dict[str, dict] = {}
        self.event_misses: dict[str, float] = {}

    def refresh_series(self):
        if time.time() - self.series_at < INV_EVERY and self.series:
            return
        out, cats = {}, {}
        for params in ({"category": "Sports"}, {"category": "sports"}, {}):
            try:
                data = get("k", KALSHI_REST + "/series", params=params) or {}
            except Exception as e:  # noqa
                W.err("sp.k.series", e)
                continue
            for s in data.get("series") or []:
                cat = str(s.get("category") or "")
                cats[cat] = cats.get(cat, 0) + 1
                if cat.lower() == "sports" or (not cat and params):
                    out[s["ticker"]] = {"title": (s.get("title") or "")[:60], "cat": cat, "fee": s.get("fee_type"),
                                        "mult": s.get("fee_multiplier"), "tags": (s.get("tags") or [])[:4],
                                        "src": [x.get("name") for x in (s.get("settlement_sources") or [])][:2]}
            if out:
                break
        if out:
            self.series, self.series_at = out, time.time()
            W.write("sp.k.series", {"n": len(out), "cats": cats, "series": out})
            log(f"kalshi sports series: {len(out)}")

    def is_sport(self, event_ticker: str) -> bool:
        return event_ticker.split("-")[0] in self.series if self.series else event_ticker.startswith("KX")

    def event_meta(self, ticker: str) -> Optional[dict]:
        if ticker in self.events:
            return self.events[ticker]
        if time.time() - self.event_misses.get(ticker, 0) < 1800:
            return None
        try:
            data = get("k", f"{KALSHI_REST}/events/{ticker}") or {}
        except Exception as e:  # noqa
            W.err("sp.k.event", e)
            self.event_misses[ticker] = time.time()
            return None
        ev = data.get("event") or {}
        if not ev:
            self.event_misses[ticker] = time.time()
            return None
        meta = {"t": ticker, "series": ev.get("series_ticker") or ticker.split("-")[0], "title": (ev.get("title") or "")[:100],
                "sub": (ev.get("sub_title") or "")[:60], "mx": ev.get("mutually_exclusive"), "crt": ev.get("collateral_return_type"),
                "strike": ev.get("strike_date"), "feeo": ev.get("fee_type_override"), "multo": ev.get("fee_multiplier_override"),
                "src": [x.get("name") for x in (ev.get("settlement_sources") or [])][:2]}
        self.events[ticker] = meta
        W.write("sp.k.event", meta)
        return meta

    def near_term(self, now: float) -> list[dict]:
        out, cursor = [], ""
        for _ in range(MAX_PAGES):
            data = get("k", KALSHI_REST + "/markets", params={"min_close_ts": int(now - 3600), "max_close_ts": int(now + 6 * 3600),
                                                               "limit": 1000, "cursor": cursor}) or {}
            ms = data.get("markets") or []
            out.extend(m for m in ms if self.is_sport(str(m.get("event_ticker") or "")))
            cursor = data.get("cursor") or ""
            if not cursor or not ms:
                break
        return out

    def settled(self, since: int) -> list[dict]:
        out, cursor = [], ""
        for _ in range(10):
            data = get("k", KALSHI_REST + "/markets", params={"status": "settled", "min_settled_ts": since, "limit": 1000,
                                                               "cursor": cursor}) or {}
            ms = data.get("markets") or []
            out.extend(m for m in ms if self.is_sport(str(m.get("event_ticker") or "")))
            cursor = data.get("cursor") or ""
            if not cursor or not ms:
                break
        return out


def k_compact(m: dict) -> dict:
    et = str(m.get("event_ticker") or "")
    return {"t": m.get("ticker"), "ev": et, "series": et.split("-")[0], "yes": (m.get("yes_sub_title") or "")[:40],
            "no": (m.get("no_sub_title") or "")[:40], "title": (m.get("title") or "")[:80],
            "yb": f(m.get("yes_bid_dollars")), "ya": f(m.get("yes_ask_dollars")), "nb": f(m.get("no_bid_dollars")),
            "na": f(m.get("no_ask_dollars")), "ybq": f(m.get("yes_bid_size_fp")), "yaq": f(m.get("yes_ask_size_fp")),
            "last": f(m.get("last_price_dollars")), "vol24": f(m.get("volume_24h_fp")), "oi": f(m.get("open_interest_fp")),
            "status": m.get("status"), "result": m.get("result"), "close": m.get("close_time"), "exp": m.get("expected_expiration_time"),
            "open": m.get("open_time"), "settled": m.get("settlement_ts"), "mtype": m.get("market_type"),
            "strike": m.get("floor_strike"), "early": m.get("can_close_early")}


class Delta:
    """Writes a record only when its signature changed, or every `every` cycles. Each record carries
    chg ("new" first sighting / True changed / False periodic) and unch = unchanged cycles since the
    previous write, so the analyzer can recover cycle counts: cycles = unch + (1 if chg is True)."""

    def __init__(self, kind: str, every: int = 5):
        self.kind, self.every = kind, every
        self.last: dict[str, Any] = {}
        self.unch: dict[str, int] = {}
        self.seen: dict[str, float] = {}

    def push(self, key: str, payload: dict, sig: Any):
        self.seen[key] = time.time()
        if key not in self.last:
            W.write(self.kind, dict(payload, chg="new", unch=0))
            self.last[key], self.unch[key] = sig, 0
        elif sig != self.last[key]:
            W.write(self.kind, dict(payload, chg=True, unch=self.unch[key]))
            self.last[key], self.unch[key] = sig, 0
        else:
            self.unch[key] += 1
            if self.unch[key] >= self.every:
                W.write(self.kind, dict(payload, chg=False, unch=self.unch[key]))
                self.unch[key] = 0

    def sweep(self, max_age: float = 7200):
        cut = time.time() - max_age
        for k in [k for k, t in self.seen.items() if t < cut]:
            self.seen.pop(k, None); self.last.pop(k, None); self.unch.pop(k, None)


def pm_sig(pe: dict):
    return (pe.get("score"), pe.get("period"), pe.get("live"), pe.get("ended"), pe.get("closed"),
            tuple((m.get("slug"), m.get("bid"), m.get("ask"), m.get("status"), m.get("closed")) for m in pe["markets"]))


def k_sig(m: dict):
    return (m.get("yb"), m.get("ya"), m.get("ybq"), m.get("yaq"), m.get("status"), m.get("result"), m.get("last"))


# ----------------------------------------------------------------------------- detectors
def pm_theta(m: dict) -> float:
    return m.get("fee") or PM_FEE_DEFAULT


def detect_dead_pm(events: list[dict]) -> list[dict]:
    opps = []
    for ev in events:
        if ev.get("closed"):
            continue
        sc = ev.get("score")
        nums = [int(x) for x in re.findall(r"\d+", sc)] if isinstance(sc, str) else []
        for m in ev["markets"]:
            if m.get("closed") or m.get("status") in ("CLOSED", "RESOLVED"):
                continue
            bid, ask = m.get("bid"), m.get("ask")
            if bid is None and ask is None:
                continue
            quoting_mid = (ask is not None and 0.03 < ask < 0.97) or (bid is not None and 0.03 < bid < 0.97)
            if ev.get("ended") and quoting_mid:
                opps.append({"kind": "dead_pm", "venue": "polymarket", "event": ev["slug"], "title": ev["title"], "sport": ev["sport"],
                             "market": m["slug"], "q": m["q"], "type": m["type"], "line": m.get("line"), "bid": bid, "ask": ask,
                             "score": sc, "period": ev.get("period"), "status": m.get("status"),
                             "note": "event ended, market still quoting away from 0/1"})
            t = str(m.get("type") or "").lower()
            if len(nums) >= 2 and "total" in t and m.get("line") is not None and nums[0] + nums[1] > float(m["line"]):
                # Over is decided for any sport whose score only increases. Which side is "long" is in m["sides"].
                if quoting_mid:
                    opps.append({"kind": "dead_pm_total", "venue": "polymarket", "event": ev["slug"], "title": ev["title"],
                                 "sport": ev["sport"], "market": m["slug"], "q": m["q"], "type": m["type"], "line": m["line"],
                                 "score": sc, "period": ev.get("period"), "bid": bid, "ask": ask, "sides": m.get("sides"),
                                 "note": "score already exceeds the total; Over is decided"})
    return opps


def detect_dutch_pm(events: list[dict]) -> list[dict]:
    """Groups of >= 2 outcome markets in one event (e.g. 3-way soccer, tournament winner) whose asks sum < 1."""
    opps = []
    for ev in events:
        if ev.get("closed"):
            continue
        groups: dict[str, list[dict]] = {}
        for m in ev["markets"]:
            if m.get("closed") or m.get("ask") is None:
                continue
            t = str(m.get("type") or "").lower()
            if any(x in t for x in ("spread", "total", "prop")) or m.get("line") is not None:
                continue
            groups.setdefault(t, []).append(m)
        for t, ms in groups.items():
            if len(ms) < 2:
                continue
            s_ask = sum(m["ask"] for m in ms)
            fees = sum(fee(pm_theta(m), m["ask"]) for m in ms)
            if s_ask + fees < 1 - MIN_MARGIN:
                opps.append({"kind": "dutch_pm", "venue": "polymarket", "event": ev["slug"], "title": ev["title"], "sport": ev["sport"],
                             "type": t, "n": len(ms), "sum_ask": round(s_ask, 4), "margin": round(1 - s_ask - fees, 4),
                             "legs": [(m["slug"], m["ask"]) for m in ms],
                             "note": "pays only if the legs are exhaustive and mutually exclusive — check the rules"})
    return opps


def detect_dutch_k(markets: list[dict], K: Kalshi) -> list[dict]:
    by_ev: dict[str, list[dict]] = {}
    for m in markets:
        if m.get("status") == "active" and (m.get("mtype") or "binary") == "binary":
            by_ev.setdefault(m["ev"], []).append(m)
    opps = []
    for et, ms in by_ev.items():
        if len(ms) < 2:
            continue
        meta = K.event_meta(et)
        if not meta or not meta.get("mx"):
            continue
        theta = K_FEE_DEFAULT * (meta.get("multo") or 1.0)
        if all(m.get("ya") is not None for m in ms):
            s_ask = sum(m["ya"] for m in ms)
            fees = sum(fee(theta, m["ya"]) for m in ms)
            if s_ask + fees < 1 - MIN_MARGIN:
                opps.append({"kind": "dutch_k", "venue": "kalshi", "event": et, "title": meta["title"], "series": meta["series"],
                             "n": len(ms), "sum_ask": round(s_ask, 4), "margin": round(1 - s_ask - fees, 4),
                             "depth": min(m.get("yaq") or 0 for m in ms), "legs": [(m["t"], m["ya"], m.get("yaq")) for m in ms]})
        if all(m.get("yb") is not None for m in ms):
            s_bid = sum(m["yb"] for m in ms)
            fees_b = sum(fee(theta, m["yb"]) for m in ms)
            if s_bid - fees_b > 1 + MIN_MARGIN:
                opps.append({"kind": "dutch_k_sell", "venue": "kalshi", "event": et, "title": meta["title"], "series": meta["series"],
                             "n": len(ms), "sum_bid": round(s_bid, 4), "margin": round(s_bid - fees_b - 1, 4),
                             "depth": min(m.get("ybq") or 0 for m in ms), "legs": [(m["t"], m["yb"], m.get("ybq")) for m in ms]})
    return opps


def match_games(pm: list[dict], kms: list[dict], K: Kalshi) -> list[tuple[dict, dict, list[dict]]]:
    """Pair a Polymarket event with a Kalshi event (team tokens on both sides + start within hours)."""
    by_ev: dict[str, list[dict]] = {}
    for m in kms:
        by_ev.setdefault(m["ev"], []).append(m)
    k_index = []
    for et, ms in by_ev.items():
        meta = K.events.get(et) or {"title": "", "strike": None}
        kt = tokens(meta.get("title")) | set().union(*[tokens(m["yes"]) | tokens(m["title"]) for m in ms])
        k_index.append((et, meta, ms, kt))
    pairs = []
    for pe in pm:
        sides = [tokens(s) for s in team_sides(pe["title"])]
        if len(sides) != 2 or not all(sides):
            names = [tokens(t["name"]) for t in pe.get("teams") or []]
            sides = [s for s in names if s][:2]
        if len(sides) != 2:
            continue
        p_start = R.parse_ts(pe.get("start"))
        best, best_score = None, 0
        for et, meta, ms, kt in k_index:
            if not all(s & kt for s in sides):
                continue
            k_close = min((R.parse_ts(m.get("exp") or m.get("close")) or 0) for m in ms)
            if p_start and k_close and not (-6 * 3600 < k_close - p_start < 12 * 3600):
                continue
            score = sum(len(s & kt) for s in sides)
            if score > best_score:
                best, best_score = (et, meta, ms), score
        if best:
            pairs.append((pe, dict(best[1], t=best[0]), best[2]))
    return pairs


def detect_xvenue(pairs, K: Kalshi) -> list[dict]:
    opps = []
    for pe, kmeta, kms in pairs:
        theta_k = K_FEE_DEFAULT * (kmeta.get("multo") or 1.0)
        for pmm in pe["markets"]:
            t = str(pmm.get("type") or "").lower()
            if pmm.get("closed") or pmm.get("line") is not None or not ("moneyline" in t or "winner" in t or t in ("", "none")):
                continue
            longs = [s for s in pmm.get("sides") or [] if s.get("long")]
            long_t = tokens(longs[0]["desc"]) if longs else tokens(pmm["q"])
            for km in kms:
                if km.get("status") != "active" or not (tokens(km["yes"]) & long_t):
                    continue
                pb, pa, kb, ka = pmm.get("bid"), pmm.get("ask"), km.get("yb"), km.get("ya")
                cands = []
                if pb is not None and ka is not None:
                    cands.append(("sellPM_buyK", pb - ka - fee(pm_theta(pmm), pb) - fee(theta_k, ka), km.get("yaq")))
                if pa is not None and kb is not None:
                    cands.append(("buyPM_sellK", kb - pa - fee(pm_theta(pmm), pa) - fee(theta_k, kb), km.get("ybq")))
                if not cands:
                    continue
                d, margin, depth = max(cands, key=lambda c: c[1])
                if margin > MIN_MARGIN:
                    opps.append({"kind": "xvenue", "pm_event": pe["slug"], "pm_market": pmm["slug"], "k_market": km["t"], "sport": pe["sport"],
                                 "team": km["yes"], "dir": d, "margin": round(margin, 4), "k_depth": depth, "pm_bid": pb, "pm_ask": pa,
                                 "k_bid": kb, "k_ask": ka, "live": pe.get("live"), "score": pe.get("score"),
                                 "note": "a lock only if both rulebooks settle this game identically (OT, postponement, retirement)"})
    return opps


def detect_lag(settled: list[dict], pm: list[dict], K: Kalshi) -> list[dict]:
    opps = []
    for sm in settled:
        if sm.get("result") not in ("yes", "no"):
            continue
        meta = K.event_meta(sm["ev"]) or {}
        st = tokens(sm.get("title")) | tokens(sm.get("yes")) | tokens(meta.get("title"))
        for pe in pm:
            if pe.get("closed"):
                continue
            sides = [tokens(s) for s in team_sides(pe["title"])]
            if len(sides) != 2 or not all(s & st for s in sides):
                continue
            for m in pe["markets"]:
                t = str(m.get("type") or "").lower()
                if m.get("closed") or (m.get("bid") is None and m.get("ask") is None) or m.get("line") is not None:
                    continue
                if not ("moneyline" in t or "winner" in t or t in ("", "none")):
                    continue
                opps.append({"kind": "lag_k_settled", "k_market": sm["t"], "k_result": sm["result"], "k_yes": sm.get("yes"),
                             "k_settled": sm.get("settled"), "pm_event": pe["slug"], "pm_market": m["slug"], "q": m["q"], "sport": pe["sport"],
                             "pm_bid": m.get("bid"), "pm_ask": m.get("ask"), "pm_ended": pe.get("ended"), "score": pe.get("score"),
                             "note": "Kalshi finalized this game; the Polymarket market is still open"})
    return opps


# ----------------------------------------------------------------------------- inventory
def inventory(pm: list[dict], kms: list[dict], K: Kalshi) -> dict:
    inv: dict[str, dict] = {}

    def add(key, bid, ask, vol):
        d = inv.setdefault(key, {"n": 0, "two_sided": 0, "spreads": [], "vol24": 0.0})
        d["n"] += 1
        if bid is not None and ask is not None:
            d["two_sided"] += 1
            d["spreads"].append(round(ask - bid, 3))
        d["vol24"] += vol or 0

    for pe in pm:
        for m in pe["markets"]:
            if not m.get("closed"):
                add(f"pm|{pe['sport']}|{pe['league']}|{m.get('type')}", m.get("bid"), m.get("ask"), m.get("vol24"))
    for m in kms:
        if m.get("status") == "active":
            add(f"k|{m['series']}|{(K.series.get(m['series']) or {}).get('title', '')}", m.get("yb"), m.get("ya"), m.get("vol24"))
    for d in inv.values():
        d["med_spread"] = round(statistics.median(d["spreads"]), 3) if d["spreads"] else None
        d["spreads"] = None
        d["vol24"] = round(d["vol24"], 1)
    return inv


# ----------------------------------------------------------------------------- main loop
def opp_key(o: dict) -> str:
    return json.dumps({x: o.get(x) for x in ("kind", "event", "market", "pm_market", "k_market", "team", "dir", "type")}, sort_keys=True)


def main():
    W.write("sp.start", {"cycle": CYCLE, "near": NEAR_EVERY, "inv": INV_EVERY, "pid": os.getpid(), "pm": PMUS_BASE, "k": KALSHI_REST})
    log(f"sports radar v0.2 starting (cycle {CYCLE:.0f}s)")
    K = Kalshi()
    seen_opps: dict[str, float] = {}
    seen_pairs: set = set()
    seen_settled: set = set()
    sampled: set = set()
    last_near = last_inv = 0.0
    near_pm: list[dict] = []
    n_cycle = 0
    pm_delta, k_delta = Delta("sp.pm.event"), Delta("sp.k.market")

    def _stop(*_):
        STOP.set()
    if threading.current_thread() is threading.main_thread():
        signal.signal(signal.SIGINT, _stop)
        signal.signal(signal.SIGTERM, _stop)

    while not STOP.is_set():
        t0 = time.time()
        n_cycle += 1
        try:
            K.refresh_series()
            now = time.time()
            # --- Polymarket: live + ended-but-open every cycle; near-term every NEAR_EVERY; inventory hourly
            live_raw = [e for e in pm_page({"live": "true", "active": "true", "closed": "false"}, 5) if pm_is_sport(e)]
            ended_raw = [e for e in pm_page({"ended": "true", "closed": "false"}, 5) if pm_is_sport(e)]
            if live_raw and "pm" not in sampled:
                sampled.add("pm"); W.write("sp.sample", {"venue": "polymarket", "event": live_raw[0]})
            pm_now = {e["slug"]: pm_compact(e) for e in live_raw + ended_raw if e.get("slug")}
            if now - last_near > NEAR_EVERY:
                last_near = now
                near_raw = pm_page({"active": "true", "closed": "false", "startTimeMin": iso(now - 6 * 3600),
                                    "startTimeMax": iso(now + 12 * 3600)})
                near_pm = [pm_compact(e) for e in near_raw if pm_is_sport(e) and e.get("slug")]
                for pe in near_pm:
                    if pe["slug"] not in pm_now:
                        pm_delta.push(pe["slug"], dict(pe, src="near"), pm_sig(pe))
            for pe in pm_now.values():
                pm_delta.push(pe["slug"], dict(pe, src="live" if pe.get("live") else "ended"), pm_sig(pe))
            pm_all = list(pm_now.values()) + [pe for pe in near_pm if pe["slug"] not in pm_now]
            # --- Kalshi: near-term markets (any status) + settlements
            k_raw = K.near_term(now)
            if k_raw and "k" not in sampled:
                sampled.add("k"); W.write("sp.sample", {"venue": "kalshi", "market": k_raw[0]})
            kms = [k_compact(m) for m in k_raw]
            for m in kms:
                if m.get("t"):
                    k_delta.push(m["t"], m, k_sig(m))
            for et in sorted({m["ev"] for m in kms}):
                if et not in K.events and len(K.events) < 5000:
                    K.event_meta(et)
            settled = [k_compact(m) for m in K.settled(int(now) - 7200)]
            new_settled = [m for m in settled if m.get("t") and m["t"] not in seen_settled]
            if new_settled:
                seen_settled.update(m["t"] for m in new_settled)
                W.write("sp.k.settled", new_settled[:500])
            if n_cycle % 60 == 0:
                pm_delta.sweep(); k_delta.sweep()
                seen_settled.intersection_update({m["t"] for m in settled if m.get("t")})
            # --- matching + detectors
            pairs = match_games(pm_all, kms, K)
            for pe, kmeta, _ in pairs:
                key = f"{pe['slug']}|{kmeta['t']}"
                if key not in seen_pairs:
                    seen_pairs.add(key)
                    W.write("sp.match", {"pm": pe["slug"], "pm_title": pe["title"], "k": kmeta["t"], "k_title": kmeta.get("title"), "sport": pe["sport"]})
            opps = (detect_dead_pm(pm_all) + detect_dutch_pm(pm_all) + detect_dutch_k(kms, K) + detect_xvenue(pairs, K)
                    + detect_lag(settled, pm_all, K))
            confirmed = 0
            for o in opps:
                key = opp_key(o)
                first = seen_opps.setdefault(key, now)
                o["first_seen"] = int(first)
                o["persist_s"] = int(now - first)
                # fresh confirmation on the Polymarket leg (list quotes can be cached)
                slug = o.get("market") or o.get("pm_market")
                if slug and confirmed < 20:
                    try:
                        o["bbo"] = pm_bbo(slug)
                        confirmed += 1
                    except Exception as e:  # noqa
                        o["bbo_err"] = str(e)[:100]
                W.write("sp.opp", o)
            for key in [k_ for k_, t in seen_opps.items() if now - t > 86400]:
                seen_opps.pop(key, None)
            # --- hourly: inventory + recently closed Polymarket events (close latency)
            if now - last_inv > INV_EVERY:
                last_inv = now
                try:
                    all_raw = pm_page({"active": "true", "closed": "false"})
                    all_pm = [pm_compact(e) for e in all_raw if pm_is_sport(e) and e.get("slug")]
                    closed_raw = pm_page({"closed": "true", "finishedTimestampMin": iso(now - 6 * 3600)}, 10)
                    for e in closed_raw:
                        if pm_is_sport(e):
                            pe = pm_compact(e)
                            rec = {k: pe.get(k) for k in ("slug", "title", "sport", "league", "finished", "closedTime", "ended", "score")}
                            rec.update(m_closed=sum(1 for m in pe["markets"] if m.get("closed")), m_n=len(pe["markets"]))
                            W.write("sp.pm.closed", rec)
                    inv = inventory(all_pm, kms, K)
                    W.write("sp.inventory", {"pm_events": len(all_pm), "pm_events_total": len(all_raw), "k_markets": len(kms),
                                             "k_events": len({m['ev'] for m in kms}), "pairs": len(pairs), "by": inv,
                                             "calls": dict(CALLS), "bytes": dict(BYTES)})
                    log(f"inventory: pm sports events {len(all_pm)}/{len(all_raw)}, kalshi near-term sports markets {len(kms)}, "
                        f"pairs {len(pairs)}, calls {CALLS}, MB {BYTES['pm']/1e6:.1f}/{BYTES['k']/1e6:.1f}")
                except Exception as e:  # noqa
                    W.err("sp.inventory", e)
            kinds: dict[str, int] = {}
            for o in opps:
                kinds[o["kind"]] = kinds.get(o["kind"], 0) + 1
            log(f"cycle {n_cycle}: pm live {len(live_raw)} ended-open {len(ended_raw)} near {len(near_pm)} | kalshi near {len(kms)} "
                f"settled2h {len(settled)} events {len(K.events)} | pairs {len(pairs)} opps {kinds or '-'} | {time.time() - t0:.1f}s")
        except Exception as e:  # noqa
            W.err("radar", e)
            log(f"radar error: {type(e).__name__}: {e}")
        STOP.wait(max(1.0, CYCLE - (time.time() - t0)))
    W.write("sp.stop", {"lines": W.count, "calls": CALLS, "bytes": BYTES})


if __name__ == "__main__":
    main()
