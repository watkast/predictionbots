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

import difflib
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
import mrp_decided as D  # noqa: E402
from mrp_implications import Leg, implication_locks  # noqa: E402

W = R.W
log = R.log
PMUS_BASE = R.PMUS_BASE
KALSHI_REST = R.KALSHI_REST + "/trade-api/v2"
CYCLE = float(os.environ.get("MRP_RADAR_CYCLE", "15"))          # live games: scoring pace needs <= 15 s
NEAR_EVERY = float(os.environ.get("MRP_RADAR_NEAR_SECONDS", "600"))
INV_EVERY = float(os.environ.get("MRP_RADAR_INVENTORY_SECONDS", "10800"))
K_SWEEP_EVERY = float(os.environ.get("MRP_RADAR_K_SWEEP_SECONDS", "300"))   # full Kalshi near-term discovery
ENDED_EVERY = 4                                                              # ended-but-open poll every N cycles
MAX_PAGES = int(os.environ.get("MRP_RADAR_MAX_PAGES", "60"))
REQ_GAP = float(os.environ.get("MRP_RADAR_REQ_GAP", "0.2"))           # >= 200 ms between requests per venue
MIN_MARGIN = float(os.environ.get("MRP_RADAR_MIN_MARGIN", "0.004"))    # $ per contract after fees
PM_FEE_DEFAULT, K_FEE_DEFAULT = 0.07, 0.07
STOP = threading.Event()
SESS = requests.Session()
SESS.headers["User-Agent"] = "mrp-sports-radar/0.3 (read-only)"
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
    b = data.get("marketData") or data.get("bbo") or data
    return {"slug": slug, "bid": f(b.get("bestBid")), "ask": f(b.get("bestAsk")), "bidDepth": b.get("bidDepth"),
            "askDepth": b.get("askDepth"), "bidQ": f(b.get("bidShares")), "askQ": f(b.get("askShares")),
            "last": f(b.get("lastTradePx")), "state": str(b.get("state") or "").replace("MARKET_STATE_", ""),
            "settle": f(b.get("settlementPx"))}


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
                "src": [x.get("name") for x in (ev.get("settlement_sources") or [])][:2],
                "n": len(data.get("markets") or ev.get("markets") or []) or None}
        self.events[ticker] = meta
        W.write("sp.k.event", meta)
        return meta

    def near_term(self, now: float) -> list[dict]:
        out, cursor = [], ""
        for _ in range(MAX_PAGES):
            data = get("k", KALSHI_REST + "/markets", params={"min_close_ts": int(now - 3600), "max_close_ts": int(now + 6 * 3600),
                                                               "limit": 1000, "cursor": cursor, "mve_filter": "exclude"}) or {}
            ms = data.get("markets") or []
            out.extend(m for m in ms if self.is_sport(str(m.get("event_ticker") or "")))
            cursor = data.get("cursor") or ""
            if not cursor or not ms:
                break
        return out

    def by_series(self, series: str) -> list[dict]:
        out, cursor = [], ""
        for _ in range(5):
            data = get("k", KALSHI_REST + "/markets", params={"series_ticker": series, "status": "open", "limit": 1000,
                                                               "cursor": cursor}) or {}
            ms = data.get("markets") or []
            out.extend(ms)
            cursor = data.get("cursor") or ""
            if not cursor or not ms:
                break
        return out

    def settled(self, since: int) -> list[dict]:
        out, cursor = [], ""
        for _ in range(10):
            data = get("k", KALSHI_REST + "/markets", params={"status": "settled", "min_settled_ts": since, "limit": 1000,
                                                               "cursor": cursor, "mve_filter": "exclude"}) or {}
            ms = data.get("markets") or []
            out.extend(m for m in ms if self.is_sport(str(m.get("event_ticker") or "")))
            cursor = data.get("cursor") or ""
            if not cursor or not ms:
                break
        return out


def k_compact(m: dict) -> dict:
    et = str(m.get("event_ticker") or "")
    parts = et.split("-")
    return {"t": m.get("ticker"), "ev": et, "series": parts[0], "game": parts[1] if len(parts) > 1 else et,
            "yes": (m.get("yes_sub_title") or "")[:40],
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


MONTHS = {m: i for i, m in enumerate(("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"), 1)}


def k_game_date(game: str) -> Optional[float]:
    m = re.match(r"(\d\d)([A-Z]{3})(\d\d)", game or "")
    if not m or m.group(2) not in MONTHS:
        return None
    try:
        return datetime(2000 + int(m.group(1)), MONTHS[m.group(2)], int(m.group(3)), tzinfo=timezone.utc).timestamp()
    except ValueError:
        return None


def pm_sides(pe: dict) -> list[set]:
    """Distinctive name tokens per side: tokens shared by both sides (common first names) are dropped."""
    names = [t["name"] for t in pe.get("teams") or []][:2]
    if len(names) != 2:
        names = team_sides(pe["title"])
    if len(names) != 2:
        return []
    a, b = tokens(names[0]), tokens(names[1])
    a, b = a - b, b - a
    return [a, b] if a and b else []


def _fz(a: str, b: str) -> bool:
    """Same name modulo transliteration: 'hazem' ~ 'hazm', 'khaleej' ~ 'khalij'."""
    if a == b:
        return True
    if min(len(a), len(b)) < 4:
        return False
    if a[:5] == b[:5] and min(len(a), len(b)) >= 5:
        return True
    return difflib.SequenceMatcher(None, a, b).ratio() >= 0.8


def fuzzy_hit(side: set, kt: set) -> int:
    return sum(1 for a in side if any(_fz(a, b) for b in kt))


def pm_codes(pe: dict) -> list[str]:
    """Team codes from Polymarket slugs: 'atc-spl-kha-haz-2026-10-29-kha' -> ['kha', 'haz']."""
    for m in pe.get("markets") or []:
        parts = str(m.get("slug") or "").split("-")
        if len(parts) >= 5 and re.fullmatch(r"\d{4}", parts[4] if len(parts) > 4 else ""):
            return [x for x in parts[2:4] if x.isalpha()]
    return []


K_SPORT_PREFIX = (("tennis", ("ATP", "WTA", "ITF", "CHALLENGER", "DAVIS", "BJK", "UTR"), ("TENNIS",)),
                  ("table-tennis", ("LIGAPRO", "WTT", "SETKA", "TTCUP", "TTELITE"), ("TABLETENNIS",)),
                  ("darts", ("PDC",), ("DARTS",)),
                  ("esports", ("ESOCCER", "EBASKETBALL", "EFOOTBALL", "EHOCKEY", "ETENNIS", "CS2", "LOL", "VALORANT", "DOTA",
                               "COD", "R6", "OVERWATCH", "ROCKETLEAGUE"), ()),
                  ("cricket", ("T20", "ODI", "IPL", "BBL", "CPL"), ("CRICKET",)),
                  ("ice-hockey", ("NHL", "KHL", "SHL", "AHL", "LIIGA", "DEL"), ("HOCKEY",)))


def k_sport(series: str) -> Optional[str]:
    core = series.upper()[2:] if series.upper().startswith("KX") else series.upper()
    for sport, prefixes, subs in K_SPORT_PREFIX:
        if core.startswith(prefixes) or any(x in core for x in subs):
            return sport
    return None


def sport_ok(pm_sport: str, series: str) -> bool:
    ks = k_sport(series)
    if ks is None:   # football/soccer/basketball/... : only reject the obviously-other sports
        return pm_sport not in ("tennis", "table-tennis", "darts", "esports", "cricket")
    return ks == pm_sport


CODE_SPORTS = ("tennis", "table-tennis")


def name_codes(name: str) -> set:
    """3-letter codes Kalshi may use for a player: first 3 letters of each word, and of 2-word surnames ('De Alba' -> DEA)."""
    words = [w for w in re.sub(r"[^a-z ]", " ", (name or "").lower()).split() if w]
    codes = {w[:3].upper() for w in words if len(w) >= 2}
    codes |= {(a + b)[:3].upper() for a, b in zip(words, words[1:])}
    return codes


def code_cover(pe: dict, gk: str) -> bool:
    """Individual sports: every 3-letter chunk of the Kalshi game key (after the date/time) must belong to exactly
    one side's player names, and each side must own at least one chunk. 'ALTLEH' <- Altmaier / Lehecka."""
    letters = re.sub(r"^\d{2}[A-Z]{3}\d{2}\d*", "", gk)
    if not letters or len(letters) % 3:
        return False
    chunks = [letters[i:i + 3] for i in range(0, len(letters), 3)]
    names = [t["name"] for t in pe.get("teams") or []][:2] or team_sides(pe["title"])
    if len(names) != 2:
        return False
    side_codes = [set().union(*[name_codes(p) for p in re.split(r"\s*[/,&]\s*|\s+-\s+", n)]) for n in names]
    owned = [0, 0]
    for ch in chunks:
        hit = [ch in side_codes[0], ch in side_codes[1]]
        if hit[0] == hit[1]:
            return False
        owned[0 if hit[0] else 1] += 1
    return owned[0] > 0 and owned[1] > 0


def match_games(pm: list[dict], kms: list[dict]) -> list[tuple[dict, str, list[dict]]]:
    """Pair a Polymarket event with a Kalshi *game* (every Kalshi event sharing the game key, e.g. 26OCT29KHAHAZ:
    winner, totals, BTTS, 1H, set winners...). Both sides must hit distinctive tokens; the date must agree within 1 day."""
    by_game: dict[str, list[dict]] = {}
    for m in kms:
        by_game.setdefault(m["game"], []).append(m)
    idx = []
    for gk, ms in by_game.items():
        kt = set().union(*[tokens(m["yes"]) | tokens(m["title"]) | tokens(m.get("evtitle")) for m in ms])
        idx.append((gk, ms, kt, k_game_date(gk)))
    pairs = []
    for pe in pm:
        sides = pm_sides(pe)
        if not sides:
            continue
        p_start = R.parse_ts(pe.get("start"))
        best, best_score = None, 0
        codes = pm_codes(pe)
        for gk, ms, kt, kd in idx:
            if kd is None or (p_start and abs(p_start - kd) > 1.5 * 86400):
                continue
            if pe.get("sport") in CODE_SPORTS and not code_cover(pe, gk):
                continue
            if not sport_ok(pe.get("sport") or "", ms[0]["series"]):
                continue
            code_hit = len(codes) == 2 and len(codes[0]) >= 3 and gk[7:].lower() in (codes[0] + codes[1], codes[1] + codes[0])
            hits = [fuzzy_hit(sd, kt) for sd in sides]
            if not (code_hit or all(hits)):
                continue
            score = sum(hits) + (5 if code_hit else 0)
            if score > best_score:
                best, best_score = (gk, ms), score
        if best:
            pairs.append((pe, best[0], best[1]))
    return pairs


def detect_decided(pairs, pm_all: list[dict], score_age: dict[str, float]) -> list[dict]:
    """The decided-state engine: contracts the live score has already settled, still trading."""
    opps = []
    games: dict[str, D.Game] = {}
    for pe in pm_all:
        g = D.build_game(pe, score_age.get(pe["slug"], 0.0))
        if g is None:
            continue
        games[pe["slug"]] = g
        for m in pe["markets"]:
            if m.get("closed"):
                continue
            dec = D.decide_pm(g, m)
            e = dec and D.edge(dec, m.get("bid"), m.get("ask"), pm_theta(m))
            if e and e[2] > MIN_MARGIN:
                opps.append({"kind": "decided_pm", "venue": "polymarket", "event": pe["slug"], "title": pe["title"], "sport": pe["sport"],
                             "market": m["slug"], "q": m["q"], "action": e[0], "price": e[1], "margin": e[2], "bid": m.get("bid"),
                             "ask": m.get("ask"), "reason": dec.reason, "score": pe.get("score"), "period": pe.get("period"),
                             "score_age_s": int(g.score_age_s), "lock": (not dec.score_dependent) or g.score_age_s >= D.SETTLE_AGE.get(g.sport, 120)})
    for pe, gk, kms in pairs:
        g = games.get(pe["slug"])
        if g is None:
            continue
        for km in kms:
            if km.get("status") != "active":
                continue
            dec = D.decide_k(g, km)
            if dec is None:
                continue
            e = D.edge(dec, km.get("yb"), km.get("ya"), K_FEE_DEFAULT)
            rec = {"kind": "decided_k", "venue": "kalshi", "event": km["ev"], "market": km["t"], "game": gk, "pm_event": pe["slug"],
                   "title": pe["title"], "sport": pe["sport"], "k_yes": km["yes"], "decided_yes": dec.yes, "reason": dec.reason,
                   "yb": km.get("yb"), "ya": km.get("ya"), "ybq": km.get("ybq"), "yaq": km.get("yaq"),
                   "score": pe.get("score"), "period": pe.get("period"), "score_age_s": int(g.score_age_s),
                   "lock": (not dec.score_dependent) or g.score_age_s >= D.SETTLE_AGE.get(g.sport, 120)}
            if e:
                rec.update(action=e[0], price=e[1], margin=e[2], depth=km.get("yaq") if e[0] == "buy_yes" else km.get("ybq"))
            W.write("sp.decided", rec)                     # every decided-but-active market: repricing latency study
            if e and e[2] > MIN_MARGIN:
                opps.append(rec)
    return opps


def detect_dutch_pm(events: list[dict]) -> list[dict]:
    """Soccer-style 3-way (home / draw / away as three Yes/No markets): asks summing below $1 after fees."""
    opps = []
    for ev in events:
        if ev.get("closed"):
            continue
        groups: dict[str, list[dict]] = {}
        for m in ev["markets"]:
            t = str(m.get("type") or "").lower()
            if t.endswith("full_time_winner") and not m.get("closed"):
                groups.setdefault(t, []).append(m)
        for t, ms in groups.items():
            if len(ms) != 3 or any(m.get("ask") is None for m in ms):
                continue
            s_ask = sum(m["ask"] for m in ms)
            fees = sum(fee(pm_theta(m), m["ask"]) for m in ms)
            if s_ask + fees < 1 - MIN_MARGIN:
                opps.append({"kind": "dutch_pm", "venue": "polymarket", "event": ev["slug"], "title": ev["title"], "sport": ev["sport"],
                             "type": t, "n": 3, "sum_ask": round(s_ask, 4), "margin": round(1 - s_ask - fees, 4),
                             "legs": [(m["slug"], m["ask"]) for m in ms], "lock": True})
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
        if not meta or not meta.get("mx") or meta.get("n") != len(ms):
            continue                                   # every outcome must be present and active, else the sum lies
        theta = K_FEE_DEFAULT * (meta.get("multo") or 1.0)
        if all(m.get("ya") is not None and 0 < m["ya"] < 1 for m in ms):
            s_ask = sum(m["ya"] for m in ms)
            fees = sum(fee(theta, m["ya"]) for m in ms)
            if s_ask + fees < 1 - MIN_MARGIN:
                opps.append({"kind": "dutch_k", "venue": "kalshi", "event": et, "title": meta["title"], "series": meta["series"],
                             "n": len(ms), "sum_ask": round(s_ask, 4), "margin": round(1 - s_ask - fees, 4), "lock": True,
                             "depth": min(m.get("yaq") or 0 for m in ms), "legs": [(m["t"], m["ya"], m.get("yaq")) for m in ms]})
        if all(m.get("yb") is not None and 0 < m["yb"] < 1 for m in ms):
            s_bid = sum(m["yb"] for m in ms)
            fees_b = sum(fee(theta, m["yb"]) for m in ms)
            if s_bid - fees_b > 1 + MIN_MARGIN:
                opps.append({"kind": "dutch_k_sell", "venue": "kalshi", "event": et, "title": meta["title"], "series": meta["series"],
                             "n": len(ms), "sum_bid": round(s_bid, 4), "margin": round(s_bid - fees_b - 1, 4), "lock": True,
                             "depth": min(m.get("ybq") or 0 for m in ms), "legs": [(m["t"], m["yb"], m.get("ybq")) for m in ms]})
    return opps


def detect_impl_k(kms: list[dict]) -> list[dict]:
    """Same-game ladders on Kalshi: 'wins by > 3.5' can never be worth more than 'wins'; 'over 3.5' never more than 'over 2.5'."""
    legs = []
    for m in kms:
        if m.get("status") != "active":
            continue
        kind = D.classify_k(m["series"], m["t"])
        scope = "1h" if kind.startswith("h1") else "ft"
        suffix = m["t"].rsplit("-", 1)[-1]
        try:
            x = float(m["strike"]) if m.get("strike") is not None else None
        except (TypeError, ValueError):
            x = None
        if kind in ("total", "h1_total", "total_maps") and x is not None:
            axis = f"{scope}_total" + ("_maps" if kind == "total_maps" else "")
        elif kind in ("spread", "h1_spread") and x is not None:
            axis = f"{scope}_margin_{re.sub(r'[0-9]+$', '', suffix)}"
        elif kind in ("winner", "h1_winner") and suffix != "TIE":
            axis, x = f"{scope}_margin_{suffix}", 0.0
        else:
            continue
        legs.append(Leg("kalshi", m["t"], m["game"], axis, x, m.get("yb"), m.get("ya"), m.get("ybq"), m.get("yaq"), K_FEE_DEFAULT, m["yes"]))
    out = []
    for o in implication_locks(legs, MIN_MARGIN, cross_venue=False):
        o.update(kind="implication_k", venue="kalshi", event=o["game"], market=f"{o['sell']}>{o['buy']}", lock=True)
        out.append(o)
    return out


def detect_lag(settled: list[dict], pm_all: list[dict]) -> list[dict]:
    """Kalshi finalized a match-winner market; the Polymarket winner market of the same game still trades off 0/1."""
    opps = []
    games = [sm for sm in settled if sm.get("result") in ("yes", "no") and D.classify_k(sm["series"], sm["t"]) == "winner"]
    by_game: dict[str, list[dict]] = {}
    for sm in games:
        if sm["result"] == "yes" and not sm["t"].endswith("-TIE"):
            by_game.setdefault(sm["game"], []).append(sm)
    if not by_game:
        return opps
    for pe, gk, _ in match_games([p for p in pm_all if not p.get("closed")], games):
        if gk not in by_game:
            continue
        win_t = set().union(*[tokens(sm["yes"]) for sm in by_game[gk]])
        for m in pe["markets"]:
            t = str(m.get("type") or "").lower()
            if m.get("closed") or "winner" not in t:
                continue
            longs = [s_ for s_ in m.get("sides") or [] if s_.get("long")]
            if not longs:
                continue
            lt = tokens(longs[0]["desc"])
            if str(longs[0]["desc"]).lower() == "yes":
                lt = set().union(*[tokens(t_["name"]) for t_ in pe.get("teams") or [] if t_.get("id") == longs[0].get("team")] or [set()])
                if not lt:                                   # draw market: a Kalshi team won, so the draw lost
                    dec = D.Decision(False, "kalshi winner settled", False)
                else:
                    dec = D.Decision(bool(lt & win_t), "kalshi winner settled", False)
            else:
                if not lt:
                    continue
                dec = D.Decision(bool(lt & win_t), "kalshi winner settled", False)
            e = D.edge(dec, m.get("bid"), m.get("ask"), pm_theta(m))
            if e and e[2] > MIN_MARGIN:
                opps.append({"kind": "lag_k_settled", "venue": "polymarket", "event": pe["slug"], "title": pe["title"], "sport": pe["sport"],
                             "market": m["slug"], "q": m["q"], "k_winner": [sm["yes"] for sm in by_game[gk]], "k_game": gk,
                             "action": e[0], "price": e[1], "margin": e[2], "bid": m.get("bid"), "ask": m.get("ask"),
                             "score": pe.get("score"), "period": pe.get("period"), "lock": False,
                             "note": "Kalshi says the game is over; verify both venues settle the same official result"})
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
    return json.dumps({x: o.get(x) for x in ("kind", "event", "market", "action", "type")}, sort_keys=True)


def main():
    W.write("sp.start", {"v": "0.3", "cycle": CYCLE, "near": NEAR_EVERY, "inv": INV_EVERY, "k_sweep": K_SWEEP_EVERY, "pid": os.getpid()})
    log(f"sports radar v0.3 starting (cycle {CYCLE:.0f}s)")
    K = Kalshi()
    seen_opps: dict[str, float] = {}
    seen_pairs: set = set()
    seen_settled: set = set()
    sampled: set = set()
    last_near = last_inv = last_sweep = 0.0
    near_pm: list[dict] = []
    ended_pm: dict[str, dict] = {}
    kmap: dict[str, dict] = {}                  # Kalshi ticker -> compact market (sweep + hot-series refresh)
    hot_series: set = set()                     # Kalshi series with a matched game that is live / just ended
    score_seen: dict[str, tuple] = {}           # pm slug -> (score, first time seen)
    settled: list[dict] = []
    n_cycle = 0
    pm_delta, k_delta = Delta("sp.pm.event", every=20), Delta("sp.k.market", every=20)

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
            # --- Polymarket: live every cycle (15 s), ended-but-open every ENDED_EVERY cycles, near-term every NEAR_EVERY
            live_raw = [e for e in pm_page({"live": "true", "active": "true", "closed": "false"}, 5) if pm_is_sport(e)]
            if n_cycle % ENDED_EVERY == 1:
                ended_pm = {e["slug"]: pm_compact(e) for e in pm_page({"ended": "true", "closed": "false"}, 5)
                            if pm_is_sport(e) and e.get("slug")}
            if live_raw and "pm" not in sampled:
                sampled.add("pm"); W.write("sp.sample", {"venue": "polymarket", "event": live_raw[0]})
            pm_now = dict(ended_pm)
            pm_now.update({e["slug"]: pm_compact(e) for e in live_raw if e.get("slug")})
            for slug, pe in pm_now.items():
                sc = (pe.get("score"), pe.get("period") if pe.get("sport") == "tennis" else None)
                if score_seen.get(slug, (None,))[0] != sc:
                    score_seen[slug] = (sc, now)
            score_age = {slug: now - v[1] for slug, v in score_seen.items()}
            if now - last_near > NEAR_EVERY:
                last_near = now
                near_raw = pm_page({"active": "true", "closed": "false", "startTimeMin": iso(now - 6 * 3600),
                                    "startTimeMax": iso(now + 12 * 3600)})
                near_pm = [pm_compact(e) for e in near_raw if pm_is_sport(e) and e.get("slug")]
                for pe in near_pm:
                    if pe["slug"] not in pm_now:
                        pm_delta.push(pe["slug"], dict(pe, src="near"), pm_sig(pe))
            for pe in pm_now.values():
                pm_delta.push(pe["slug"], dict(pe, src="live" if pe.get("live") else "ended", score_age_s=int(score_age.get(pe["slug"], 0))),
                              pm_sig(pe))
            pm_all = list(pm_now.values()) + [pe for pe in near_pm if pe["slug"] not in pm_now]
            # --- Kalshi: full near-term sweep every K_SWEEP_EVERY; hot series (live matched games) every cycle
            if now - last_sweep > K_SWEEP_EVERY:
                last_sweep = now
                k_raw = K.near_term(now)
                if k_raw and "k" not in sampled:
                    sampled.add("k"); W.write("sp.sample", {"venue": "kalshi", "market": k_raw[0]})
                kmap = {m["t"]: m for m in (k_compact(x) for x in k_raw) if m.get("t")}
                for et in sorted({m["ev"] for m in kmap.values()}):
                    if et not in K.events and len(K.events) < 5000:
                        K.event_meta(et)
                settled = [k_compact(m) for m in K.settled(int(now) - 7200)]
                new_settled = [m for m in settled if m.get("t") and m["t"] not in seen_settled]
                if new_settled:
                    seen_settled.update(m["t"] for m in new_settled)
                    W.write("sp.k.settled", new_settled[:500])
            else:
                for sr in sorted(hot_series)[:25]:
                    try:
                        for x in K.by_series(sr):
                            m = k_compact(x)
                            if m.get("t"):
                                kmap[m["t"]] = m
                    except Exception as e:  # noqa
                        W.err(f"sp.k.series_poll:{sr}", e)
            kms = list(kmap.values())
            for m in kms:
                m["evtitle"] = (K.events.get(m["ev"]) or {}).get("title")
            for m in settled:
                if not m.get("evtitle") and len(K.events) < 5000:
                    m["evtitle"] = (K.event_meta(m["ev"]) or {}).get("title")
            for m in kms:
                k_delta.push(m["t"], m, k_sig(m))
            if n_cycle % 240 == 0:
                pm_delta.sweep(); k_delta.sweep()
                seen_settled.intersection_update({m["t"] for m in settled if m.get("t")})
                for slug in [s_ for s_, v in score_seen.items() if now - v[1] > 6 * 3600]:
                    score_seen.pop(slug, None)
            # --- matching + detectors
            live_or_ended = [pe for pe in pm_all if pe.get("live") or pe.get("ended")]
            pairs = match_games(live_or_ended, kms)
            hot_series = {m["series"] for _, _, ms in pairs for m in ms}
            for pe, gk, ms in pairs:
                key = f"{pe['slug']}|{gk}"
                if key not in seen_pairs:
                    seen_pairs.add(key)
                    W.write("sp.match", {"pm": pe["slug"], "pm_title": pe["title"], "k_game": gk, "sport": pe["sport"],
                                         "k_series": sorted({m["series"] for m in ms}), "k_sample": ms[0]["title"]})
            opps = (detect_decided(pairs, pm_all, score_age) + detect_dutch_pm(pm_all) + detect_dutch_k(kms, K)
                    + detect_impl_k(kms) + detect_lag(settled, pm_all))
            confirmed = 0
            for o in opps:
                key = opp_key(o)
                first = seen_opps.setdefault(key, now)
                o["first_seen"] = int(first)
                o["persist_s"] = int(now - first)
                slug = o.get("market") if o.get("venue") == "polymarket" else None
                if slug and confirmed < 10:
                    try:
                        o["bbo"] = pm_bbo(slug)
                        confirmed += 1
                    except Exception as e:  # noqa
                        o["bbo_err"] = str(e)[:100]
                st = (o.get("bbo") or {}).get("state")
                if st and st != "OPEN":
                    # Polymarket already halted this market: the event-list quote is stale, nothing is tradable
                    o["kind"] = o["kind"] + "_closed"
                    o["lock"] = False
                W.write("sp.opp", o)
            for key in [k_ for k_, t in seen_opps.items() if now - t > 86400]:
                seen_opps.pop(key, None)
            # --- every INV_EVERY: inventory + recently closed Polymarket events (close latency)
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
                except Exception as e:  # noqa
                    W.err("sp.inventory", e)
            kinds: dict[str, int] = {}
            for o in opps:
                kinds[o["kind"]] = kinds.get(o["kind"], 0) + 1
            if n_cycle % 4 == 1 or opps:
                log(f"cycle {n_cycle}: pm live {len(live_raw)} ended-open {len(ended_pm)} near {len(near_pm)} | kalshi {len(kms)} "
                    f"hot {len(hot_series)} | pairs {len(pairs)} opps {kinds or '-'} | MB {BYTES['pm']/1e6:.0f}/{BYTES['k']/1e6:.0f} "
                    f"| {time.time() - t0:.1f}s")
        except Exception as e:  # noqa
            W.err("radar", e)
            log(f"radar error: {type(e).__name__}: {e}")
        STOP.wait(max(1.0, CYCLE - (time.time() - t0)))
    W.write("sp.stop", {"lines": W.count, "calls": CALLS, "bytes": BYTES})


if __name__ == "__main__":
    main()
