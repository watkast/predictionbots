#!/usr/bin/env python3
"""
Mr. S — "Dead Man's Ticket", LIVE (REAL MONEY, hard-capped). Buys Kalshi soccer contracts whose outcome the score
has ALREADY decided while someone still sells them below $1, and holds them to settlement. Nothing else.

What it buys (only these Kalshi market kinds, all decided by monotone facts):
  1H total / 1H winner-or-tie / 1H both-teams-score  -> after the first half is over (or the line is already beaten)
  full-game total / both-teams-score                 -> line already beaten in regulation, or full time (regulation only)

Two independent score sources must agree before anything counts:
  A = ESPN scoreboard (status, period, per-half linescores)      B = Polymarket US sportradar feed (score, periodScores)
Both sources must produce the SAME decision, the same score, and the score must have been unchanged in both for
>= MRS_SETTLE_S seconds (VAR / corrections). Extra time / penalties: full-game markets are never traded.

Guards (any one blocks the order): live book cheaper than MRS_MIN_ASK (= market says our "certain" is unlikely ->
our data is wrong) | price above MRS_MAX_ASK or edge after fee < MRS_MIN_EDGE | caps per order / game / day / total
open risk | switch file mrs/LIVE_ON missing on main | HALT: any settled losing trade stops all new orders until a
human resets it. Leagues in MRS_LIVE_LEAGUES trade real money; MRS_SHADOW_LEAGUES run the same logic as paper.

Writes MRS.md, state.json, live.jsonl to $MRS_DIR. The only private Kalshi endpoints it calls: GET /portfolio/balance
(start-up check, value never published) and POST /portfolio/orders (immediate-or-cancel buys). Never sells, never cancels
anything it did not place, never touches positions it did not open.
"""
from __future__ import annotations

import argparse
import base64
import json
import math
import os
import re
import sys
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

MRS_DIR = os.environ.get("MRS_DIR", "./mrsdata")
os.makedirs(MRS_DIR, exist_ok=True)
os.environ.setdefault("MRP_DATA_DIR", os.path.join(MRS_DIR, "raw"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests  # noqa: E402

import mrp_decided as D  # noqa: E402
import mrp_recorder as R  # noqa: E402
import mrp_sports_radar as S  # noqa: E402

E = os.environ.get
MODE = E("MRS_MODE", "live")
LIVE_LEAGUES = [x for x in E("MRS_LIVE_LEAGUES", "usa.1").split(",") if x]
SHADOW_LEAGUES = [x for x in E("MRS_SHADOW_LEAGUES", "bel.1,uefa.champions,uefa.europa,eng.1,esp.1,ita.1,ger.1,fra.1,ned.1,por.1,"
                                 "aut.1,tur.1,ksa.1,mex.1").split(",") if x and x not in LIVE_LEAGUES]
# ESPN league -> Kalshi series prefix (a wrong/missing prefix just finds no markets; the report lists what was found)
K_PREFIX = {"usa.1": "KXMLS", "bel.1": "KXBELGIANPL", "uefa.champions": "KXUCL", "uefa.europa": "KXUEL", "eng.1": "KXEPL",
            "esp.1": "KXLALIGA", "ita.1": "KXSERIEA", "ger.1": "KXBUNDESLIGA", "fra.1": "KXLIGUE1", "ned.1": "KXEREDIVISIE",
            "por.1": "KXLIGAPORTUGAL", "aut.1": "KXAUTBUNDES", "tur.1": "KXSUPERLIG", "ksa.1": "KXSAUDIPL", "mex.1": "KXLIGAMX"}
SUFFIXES = ("1HTOTAL", "1H", "1HBTTS", "TOTAL", "BTTS")
FULL_GAME_KINDS = ("total", "btts")

ORDER_USD = float(E("MRS_ORDER_USD", "10"))
GAME_USD = float(E("MRS_GAME_USD", "20"))
DAY_USD = float(E("MRS_DAY_USD", "40"))
RISK_USD = float(E("MRS_RISK_USD", "50"))          # max cost of open (unsettled) live positions
MIN_ASK = float(E("MRS_MIN_ASK", "0.60"))
MAX_ASK = float(E("MRS_MAX_ASK", "0.97"))
MIN_EDGE = float(E("MRS_MIN_EDGE", "0.01"))        # $ per contract after the taker fee
SETTLE_S = float(E("MRS_SETTLE_S", "240"))
CYCLE = float(E("MRS_CYCLE", "10"))
K_FEE = 0.07
SWITCH_URL = E("MRS_SWITCH_URL", "https://raw.githubusercontent.com/watkast/predictionbots/main/mrs/LIVE_ON")
ESPN = "https://site.api.espn.com/apis/site/v2/sports/soccer/{lg}/scoreboard"
KREST = R.KALSHI_REST + "/trade-api/v2"

STATE_P = os.path.join(MRS_DIR, "state.json")
LOG_P = os.path.join(MRS_DIR, "live.jsonl")
MD_P = os.path.join(MRS_DIR, "MRS.md")
SESS = requests.Session()


def now() -> float:
    return time.time()


def log(_k: str, **d):
    kind = _k
    rec = {"t": round(now(), 3), "k": kind, **d}
    with open(LOG_P, "a") as fh:
        fh.write(json.dumps(rec, default=str) + "\n")
    print(datetime.now(timezone.utc).strftime("%H:%M:%S"), kind, json.dumps(d, default=str)[:300], flush=True)


def jget(url: str, params: Any = None, headers: Any = None, timeout: float = 15) -> Any:
    for attempt in range(3):
        try:
            r = SESS.get(url, params=params, headers=headers, timeout=timeout)
        except requests.RequestException:
            time.sleep(1 + attempt)
            continue
        if r.status_code == 404:
            return None
        if r.status_code == 429 or r.status_code >= 500:
            time.sleep(1.5 * (attempt + 1))
            continue
        r.raise_for_status()
        return r.json()
    return None


def num(v: Any) -> Optional[float]:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


# ----------------------------------------------------------------------------- state
def load_state() -> dict:
    try:
        with open(STATE_P) as fh:
            st = json.load(fh)
    except (OSError, ValueError):
        st = {}
    st.setdefault("trades", [])          # every live or shadow buy
    st.setdefault("halted", None)        # reason string once halted
    st.setdefault("seen", {})            # ticker -> first time a decision was seen (for "stale for N s")
    st.setdefault("blocked", {})         # ticker -> last block reason
    st.setdefault("started", now())
    return st


def save_state(st: dict):
    st["seen"] = {k: v for k, v in st["seen"].items() if now() - v < 3 * 86400}
    st["blocked"] = dict(list(st["blocked"].items())[-300:])
    tmp = STATE_P + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(st, fh, indent=1, default=str)
    os.replace(tmp, STATE_P)


# ----------------------------------------------------------------------------- source A: ESPN
ET_WORDS = ("EXTRA", "OVERTIME", "SHOOTOUT", "AET", "PEN", "END_OF_REGULATION", "END_REGULATION")
VOID_WORDS = ("POSTPONED", "CANCEL", "ABANDON", "SUSPEND", "DELAY", "FORFEIT")


def espn_games(league: str, ht_memory: dict) -> list[dict]:
    d0 = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y%m%d")
    d1 = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y%m%d")
    data = jget(ESPN.format(lg=league), params={"dates": f"{d0}-{d1}", "limit": 200}) or {}
    out = []
    for ev in data.get("events") or []:
        comp = (ev.get("competitions") or [{}])[0]
        st = comp.get("status") or ev.get("status") or {}
        typ = st.get("type") or {}
        name, state = str(typ.get("name") or "").upper(), str(typ.get("state") or "")
        if state == "pre" or not name:
            continue
        period = int(num(st.get("period")) or 0)
        cs = comp.get("competitors") or []
        if len(cs) != 2:
            continue
        et = any(w in name for w in ET_WORDS) or period > 2
        if any(w in name for w in VOID_WORDS):
            per = "POST"
        elif et:
            per = "ET"
        elif "HALFTIME" in name:
            per = "HT"
        elif "FIRST_HALF" in name or (state == "in" and period == 1):
            per = "1H"
        elif "SECOND_HALF" in name or (state == "in" and period == 2):
            per = "2H"
        elif state == "post" or "FULL_TIME" in name or "FINAL" in name:
            per = "FT"
        else:
            continue
        ended = per == "FT" or (et and state == "post")
        teams, scores, lines = [], [], []
        for c in cs:
            t = c.get("team") or {}
            nm = " ".join(dict.fromkeys(x for x in (t.get("displayName"), t.get("shortDisplayName")) if x))
            teams.append({"id": str(c.get("id") or t.get("id")), "name": nm, "abbr": str(t.get("abbreviation") or "").upper()})
            scores.append(int(num(c.get("score")) or 0))
            lines.append([int(num(x.get("value")) or 0) for x in c.get("linescores") or []])
        eid = str(ev.get("id"))
        if per == "HT":
            ht_memory[eid] = tuple(scores)
        h1 = None
        if all(len(x) >= 1 for x in lines) and per != "1H":
            h1 = (lines[0][0], lines[1][0])
        elif eid in ht_memory:
            h1 = ht_memory[eid]
        elif per == "HT":
            h1 = tuple(scores)
        ids = [t["id"] for t in teams]
        ps = []
        if per == "1H":
            ps = [{"label": "1H", "scores": [{"competitorId": ids[i], "score": scores[i]} for i in (0, 1)]}]
        elif h1 is not None and per in ("HT", "2H", "FT", "ET"):
            ps = [{"label": "1H", "scores": [{"competitorId": ids[i], "score": h1[i]} for i in (0, 1)]}]
            if per != "HT":
                ps.append({"label": "2H", "scores": [{"competitorId": ids[i], "score": scores[i] - h1[i]} for i in (0, 1)]})
        out.append({"src": "espn", "league": league, "id": eid, "slug": f"espn-{league}-{eid}", "sport": "soccer",
                    "start": ev.get("date"), "teams": teams, "score": f"{scores[0]}-{scores[1]}", "period": per, "ended": ended,
                    "et": et, "espn_period": period, "status": name, "periodScores": ps, "h1": h1})
    return out


# ----------------------------------------------------------------------------- matching
def ts(s: Any) -> Optional[float]:
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def side_match(names_a: list[str], names_b: list[str]) -> Optional[list[int]]:
    """Map each name in A to a distinct name in B by fuzzy tokens; None if ambiguous."""
    if len(names_a) != 2 or len(names_b) != 2:
        return None
    ta = [S.tokens(n) for n in names_a]
    tb = [S.tokens(n) for n in names_b]
    ta = [ta[0] - ta[1], ta[1] - ta[0]]
    tb = [tb[0] - tb[1], tb[1] - tb[0]]
    if not all(ta) or not all(tb):
        return None
    hit = [[S.fuzzy_hit(ta[i], tb[j]) > 0 for j in (0, 1)] for i in (0, 1)]
    if hit[0][0] and hit[1][1] and not hit[0][1] and not hit[1][0]:
        return [0, 1]
    if hit[0][1] and hit[1][0] and not hit[0][0] and not hit[1][1]:
        return [1, 0]
    return None


def codes_match(game_seg: str, eg: dict) -> bool:
    letters = re.sub(r"^\d\d[A-Z]{3}\d\d", "", game_seg or "")
    a, b = eg["teams"][0]["abbr"], eg["teams"][1]["abbr"]
    return bool(a and b and letters in (a + b, b + a))


# ----------------------------------------------------------------------------- Kalshi
_ev_title: dict[str, str] = {}


def k_markets(prefix: str) -> list[dict]:
    out = []
    for suf in SUFFIXES:
        data = jget(KREST + "/markets", params={"series_ticker": prefix + suf, "status": "open", "limit": 200}) or {}
        for m in data.get("markets") or []:
            km = S.k_compact(m)
            if km["series"] != prefix + suf:
                continue
            if km["ev"] not in _ev_title:
                e = jget(KREST + f"/events/{km['ev']}") or {}
                _ev_title[km["ev"]] = str((e.get("event") or {}).get("title") or "")
            km["evtitle"] = _ev_title[km["ev"]]
            out.append(km)
    return out


def k_book(ticker: str) -> Optional[dict]:
    data = jget(KREST + f"/markets/{ticker}/orderbook", params={"depth": 30}) or {}
    ob = data.get("orderbook") or data.get("orderbook_fp") or {}

    def lv(key_d, key_c):
        rows = ob.get(key_d)
        if rows:
            return [(float(p), float(q)) for p, q in rows]
        rows = ob.get(key_c) or []
        return [(p / 100.0, float(q)) for p, q in rows]
    if not ob:
        return None
    return {"yes": lv("yes_dollars", "yes"), "no": lv("no_dollars", "no")}


def asks_for(book: dict, buy_yes: bool) -> list[tuple[float, float]]:
    """Asks on the side we buy, cheapest first: buying YES lifts NO bids (ask = 1 - no bid) and vice versa."""
    rows = book["no"] if buy_yes else book["yes"]
    return sorted(((round(1 - p, 4), q) for p, q in rows if q > 0), key=lambda x: x[0])


def fee_per(p: float) -> float:
    return K_FEE * p * (1 - p)


_signer = None


def k_private(method: str, path: str, body: Optional[dict] = None) -> tuple[int, Any]:
    global _signer
    if _signer is None:
        _signer = R._kalshi_signer()
    full = "/trade-api/v2" + path
    h = dict(_signer(method, full), **{"Content-Type": "application/json"})
    r = SESS.request(method, R.KALSHI_REST + full, headers=h, data=json.dumps(body) if body is not None else None, timeout=15)
    try:
        js = r.json()
    except ValueError:
        js = {"text": r.text[:300]}
    return r.status_code, js


# ----------------------------------------------------------------------------- main loop pieces
class Ages:
    """Seconds a game's score (per source) has been unchanged; the first sighting counts as a change."""

    def __init__(self):
        self.sig: dict[str, tuple] = {}
        self.t: dict[str, float] = {}

    def age(self, key: str, sig: tuple) -> float:
        if self.sig.get(key) != sig:
            self.sig[key], self.t[key] = sig, now()
        return now() - self.t[key]


def switch_on() -> bool:
    try:
        r = SESS.get(SWITCH_URL, timeout=10, params={"t": int(now())})
        return r.status_code == 200
    except requests.RequestException:
        return False


def open_risk(st: dict) -> float:
    return sum(t["cost"] for t in st["trades"] if t["live"] and t.get("result") is None)


def spent(st: dict, live: bool, day: Optional[str] = None, game: Optional[str] = None) -> float:
    return sum(t["cost"] for t in st["trades"] if t["live"] == live and (day is None or t["day"] == day)
               and (game is None or t["game"] == game))


def settle(st: dict):
    for t in st["trades"]:
        if t.get("result") is not None or t["filled"] <= 0:
            if t["filled"] <= 0 and t.get("result") is None:
                t["result"] = "unfilled"
            continue
        m = (jget(KREST + f"/markets/{t['ticker']}") or {}).get("market") or {}
        res = str(m.get("result") or "").lower()
        if res not in ("yes", "no"):
            continue
        won = res == t["side"]
        t["result"], t["pnl"] = res, round((t["filled"] if won else 0) - t["cost"] - t["fees"], 4)
        log("settled", ticker=t["ticker"], live=t["live"], won=won, pnl=t["pnl"])
        if t["live"] and not won and not st["halted"]:
            st["halted"] = f"{datetime.now(timezone.utc):%Y-%m-%d %H:%M}Z loss on {t['ticker']} ({t['why']})"
            log("HALT", reason=st["halted"])


def buy(st: dict, cand: dict, live: bool, dry: bool) -> Optional[dict]:
    tk, buy_yes = cand["ticker"], cand["yes"]
    book = k_book(tk)
    if not book:
        return None
    asks = asks_for(book, buy_yes)
    if not asks:
        st["blocked"][tk] = "no asks (already repriced)"
        return None
    if asks[0][0] < MIN_ASK:
        msg = f"contradiction: ask {asks[0][0]} < {MIN_ASK}"
        if st["blocked"].get(tk) != msg:
            log("contradiction", ticker=tk, ask=asks[0][0], why=cand["why"])
        st["blocked"][tk] = msg
        return None
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    room = min(ORDER_USD, GAME_USD - spent(st, live, game=cand["game"]), DAY_USD - spent(st, live, day=day),
               (RISK_USD - open_risk(st)) if live else ORDER_USD)
    n, cost, limit = 0, 0.0, None
    for p, q in asks:
        if p > MAX_ASK or (1 - p - fee_per(p)) < MIN_EDGE:
            break
        take = int(min(q, math.floor((room - cost) / (p + fee_per(p)) + 1e-9)))
        if take <= 0:
            break
        n, cost, limit = n + take, cost + take * p, p
        if take < q:
            break                                   # cap reached inside this level: never pay up a level for nothing
    if n <= 0:
        st["blocked"][tk] = f"no edge/room: best ask {asks[0][0]}, room ${room:.2f}"
        return None
    side = "yes" if buy_yes else "no"
    trade = {"t": now(), "day": day, "ticker": tk, "game": cand["game"], "league": cand["league"], "kind": cand["kind"],
             "side": side, "limit": limit, "want": n, "filled": 0, "cost": 0.0, "fees": 0.0, "live": live,
             "why": cand["why"], "stale_s": round(now() - st["seen"].get(tk, now()), 1), "best_ask": asks[0][0],
             "ask_depth": round(sum(q for p, q in asks if p <= MAX_ASK)), "result": None}
    if not live:
        trade.update(filled=n, cost=round(cost, 4), fees=round(n * fee_per(limit), 4), paper=True)
    else:
        cents = int(round(limit * 100))
        body = {"ticker": tk, "side": side, "action": "buy", "type": "limit", "count": n, "time_in_force": "immediate_or_cancel",
                "client_order_id": f"mrs-{uuid.uuid4().hex[:20]}", ("yes_price" if buy_yes else "no_price"): cents}
        code, js = k_private("POST", "/portfolio/orders", body)
        o = (js or {}).get("order") or {}
        filled = num(o.get("fill_count_fp")) if o.get("fill_count_fp") is not None else num(o.get("fill_count"))
        fcost = num(o.get("taker_fill_cost_dollars")) if o.get("taker_fill_cost_dollars") is not None else (num(o.get("taker_fill_cost")) or 0) / 100
        ffee = num(o.get("taker_fees_dollars")) if o.get("taker_fees_dollars") is not None else (num(o.get("taker_fees")) or 0) / 100
        trade.update(code=code, order_id=o.get("order_id"), status=o.get("status"), filled=filled or 0, cost=round(fcost or 0, 4),
                     fees=round(ffee or 0, 4))
        if code >= 300:
            trade["error"] = json.dumps(js)[:300]
    st["trades"].append(trade)
    log("buy", **{k: v for k, v in trade.items() if k != "t"})
    return trade


def report(st: dict, info: dict):
    L = ["# Mr. S — live", "", f"Updated {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC · mode **{MODE}** · "
         f"switch **{'ON' if info.get('switch') else 'OFF'}** · live leagues: {', '.join(LIVE_LEAGUES)}", ""]
    if st["halted"]:
        L += [f"## ⛔ HALTED — {st['halted']}", "No new orders until a human resets `halted` in state.json.", ""]
    if info.get("blocked_start"):
        L += [f"## ⚠️ {info['blocked_start']}", ""]
    for live in (True, False):
        tr = [t for t in st["trades"] if t["live"] == live and t["filled"] > 0]
        done = [t for t in tr if t.get("pnl") is not None]
        pnl = sum(t["pnl"] for t in done)
        w = sum(1 for t in done if t["pnl"] > 0)
        L += [f"## {'Real money' if live else 'Shadow (paper, other leagues)'}",
              f"{len(tr)} buys · {len(done)} settled · {w} right / {len(done) - w} wrong · P&L **${pnl:+.2f}** · "
              f"open ${sum(t['cost'] for t in tr if t.get('result') is None):.2f}", ""]
        if tr:
            L += ["| time UTC | market | side | n | avg px | stale s | why | result | P&L |", "|---|---|---|---|---|---|---|---|---|"]
            for t in tr[-25:][::-1]:
                avg = t["cost"] / t["filled"] if t["filled"] else 0
                L.append(f"| {datetime.fromtimestamp(t['t'], timezone.utc):%m-%d %H:%M} | {t['ticker']} | {t['side']} | {t['filled']:g} | "
                         f"{avg:.3f} | {t['stale_s']:g} | {t['why'][:40]} | {t.get('result') or 'open'} | "
                         f"{'' if t.get('pnl') is None else format(t['pnl'], '+.2f')} |")
            L.append("")
    fails = [t for t in st["trades"] if t["live"] and t.get("error")]
    if fails:
        L += ["## Order errors", *[f"- {t['ticker']}: {t['error'][:200]}" for t in fails[-5:]], ""]
    L += ["## Right now", f"games in play/just ended: {info.get('games', 0)} · matched to Kalshi: {info.get('kmatched', 0)} · "
          f"to Polymarket: {info.get('pmatched', 0)} · decided markets agreed by both: {info.get('agreed', 0)} · "
          f"disagreements: {info.get('disagree', 0)}", ""]
    if info.get("series_found"):
        L += ["Kalshi series with open markets: " + ", ".join(sorted(info["series_found"])), ""]
    if st["blocked"]:
        L += ["### Last blocks", *[f"- {k}: {v}" for k, v in list(st["blocked"].items())[-12:]], ""]
    L += ["---", f"caps: ${ORDER_USD:g}/order · ${GAME_USD:g}/game · ${DAY_USD:g}/day · ${RISK_USD:g} open risk · ask {MIN_ASK}–{MAX_ASK} · "
          f"score stable ≥ {SETTLE_S:g}s in ESPN and Polymarket"]
    with open(MD_P, "w") as fh:
        fh.write("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--minutes", type=float, default=float(E("MRS_MINUTES", "335")))
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    dry = a.dry or MODE != "live"
    st = load_state()
    info: dict = {}
    if not dry:
        if not R.KALSHI_ON:
            info["blocked_start"] = "Kalshi keys missing: live orders impossible (running shadow only)"
            dry = True
        else:
            code, js = k_private("GET", "/portfolio/balance")
            bal = (num((js or {}).get("balance")) or 0) / 100 if code == 200 else None
            if code != 200:
                info["blocked_start"] = f"Kalshi balance check failed (HTTP {code}): key may lack trading access"
                dry = True
            elif bal < RISK_USD:
                info["blocked_start"] = f"Kalshi balance below the ${RISK_USD:g} risk cap — fund the account (orders still try, capped by cash)"
            log("start", mode="dry" if dry else "live", balance_ok=bool(bal and bal >= RISK_USD))
    end = now() + a.minutes * 60
    ages_e, ages_p, ht_mem = Ages(), Ages(), {}
    last = {"switch": 0.0, "settle": 0.0, "report": 0.0, "pm": 0.0, "k": {}}
    pm_events: list[dict] = []
    kcache: dict[str, list[dict]] = {}
    while now() < end:
        t0 = now()
        games: list[dict] = []
        try:
            if now() - last["switch"] > 300:
                info["switch"], last["switch"] = switch_on(), now()
            games = []
            for lg in LIVE_LEAGUES + SHADOW_LEAGUES:
                try:
                    games += espn_games(lg, ht_mem)
                except Exception as e:  # noqa
                    log("err", where=f"espn {lg}", e=str(e)[:200])
            games = [g for g in games if not g["ended"] or (ts(g["start"]) or 0) > now() - 5 * 3600]
            info.update(games=len(games), kmatched=0, pmatched=0, agreed=0, disagree=0)
            info.setdefault("series_found", set())
            if games:
                if now() - last["pm"] > 15:
                    raw = S.pm_page({"live": "true", "active": "true", "closed": "false"}, 5) + \
                        S.pm_page({"ended": "true", "closed": "false"}, 5)
                    pm_events = [S.pm_compact(e) for e in raw if S.pm_is_sport(e)]
                    pm_events = [p for p in pm_events if p["sport"] in ("soccer", "football-soccer") or "soccer" in p["sport"]]
                    last["pm"] = now()
                for lg in {g["league"] for g in games}:
                    if now() - last["k"].get(lg, 0) > 30 and lg in K_PREFIX:
                        kcache[lg] = k_markets(K_PREFIX[lg])
                        last["k"][lg] = now()
                        info["series_found"] |= {m["series"] for m in kcache[lg]}
            for eg in games:
                ea = ages_e.age(eg["slug"], (eg["score"], eg["h1"]))
                ge = D.build_game(eg, ea)
                if ge is None:
                    continue
                # Polymarket twin (source B)
                pe = None
                for p in pm_events:
                    st_ = ts(p.get("start"))
                    if st_ and abs(st_ - (ts(eg["start"]) or 0)) > 6 * 3600:
                        continue
                    names = [t["name"] for t in p.get("teams") or []][:2] or S.team_sides(p["title"])
                    if side_match([t["name"] for t in eg["teams"]], names):
                        pe = p
                        break
                gp = None
                if pe is not None:
                    info["pmatched"] += 1
                    p2 = dict(pe, sport="soccer")
                    gp = D.build_game(p2, ages_p.age(pe["slug"], (pe.get("score"), json.dumps(pe.get("periodScores"), sort_keys=True))))
                # Kalshi markets for this game
                kms = []
                for km in kcache.get(eg["league"], []):
                    kd = S.k_game_date(km["game"])
                    if kd is None or abs(kd - (ts(eg["start"]) or 0)) > 1.5 * 86400:
                        continue
                    if codes_match(km["game"], eg) or side_match([t["name"] for t in eg["teams"]], S.team_sides(km["evtitle"])):
                        kms.append(km)
                if kms:
                    info["kmatched"] += 1
                for km in kms:
                    kind = D.classify_k(km["series"], km["t"])
                    if kind in FULL_GAME_KINDS and eg["et"]:
                        continue                                    # extra time / penalties: Kalshi rule ambiguity, never
                    de = D.decide_k(ge, km)
                    if de is None:
                        continue
                    if kind in FULL_GAME_KINDS and not de.yes and not (eg["period"] == "FT" and eg["espn_period"] <= 2):
                        continue                                    # unders only at regulation full time
                    st["seen"].setdefault(km["t"], now())
                    dp = D.decide_k(gp, km) if gp is not None else None
                    if dp is None or dp.yes != de.yes or not gp.totals or not ge.totals or sorted(gp.totals) != sorted(ge.totals):
                        if dp is not None and dp.yes != de.yes:
                            info["disagree"] += 1
                        if dp is not None and dp.yes != de.yes and not str(st["blocked"].get(km["t"], "")).startswith("Polymarket"):
                            log("disagree", ticker=km["t"], espn=eg["score"], pm=pe and pe.get("score"), espn_dec=de.reason,
                                pm_dec=dp.reason)
                        st["blocked"][km["t"]] = "Polymarket does not confirm" if gp else "no Polymarket twin"
                        continue
                    if min(ge.score_age_s, gp.score_age_s) < SETTLE_S:
                        st["blocked"][km["t"]] = f"settling ({int(min(ge.score_age_s, gp.score_age_s))}s)"
                        continue
                    info["agreed"] += 1
                    if any(t["ticker"] == km["t"] and t["filled"] > 0 for t in st["trades"]):
                        continue
                    if any(t["ticker"] == km["t"] and now() - t["t"] < 60 for t in st["trades"]):
                        continue
                    live = eg["league"] in LIVE_LEAGUES and not dry
                    if live and (st["halted"] or not info.get("switch")):
                        st["blocked"][km["t"]] = "halted" if st["halted"] else "switch off"
                        continue
                    buy(st, {"ticker": km["t"], "yes": de.yes, "game": eg["slug"], "league": eg["league"], "kind": kind,
                             "why": f"{de.reason} | ESPN {eg['score']} {eg['period']} | PM {pe.get('score')} {pe.get('period')}"},
                        live, dry)
            if now() - last["settle"] > 120:
                settle(st)
                last["settle"] = now()
            if now() - last["report"] > 30:
                save_state(st)
                report(st, info)
                last["report"] = now()
        except Exception as e:  # noqa
            log("err", where="loop", e=repr(e)[:300])
        time.sleep(max(1.0, CYCLE - (now() - t0)) if games else 30)
    settle(st)
    save_state(st)
    report(st, info)


if __name__ == "__main__":
    main()
