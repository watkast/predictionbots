"""Real-world odds for sports game-winner markets: sportsbook consensus from The Odds API (the-odds-api.com).

Needs ODDS_API_KEY. For each upcoming game we take every bookmaker's moneyline, convert to implied probabilities, remove
the bookmaker margin (normalise each book's two or three outcomes to sum to 1), and average across books. That is the
consensus, stated as such on the page.

The quota (free tier: 500 credits a month; one credit per league per fetch) is protected four ways, in this order:
  1. a snapshot younger than MAX_AGE_S (12 h) is reused: at most two paid fetches a day, whatever the deploy cadence;
  2. only leagues the API lists as in season are fetched (its /sports call is free and never counts);
  3. the same free call returns the account's own counters, and a fetch that would dip into the last RESERVE credits
     is skipped;
  4. with no snapshot at all (first run, or every copy of the cache lost) a fetch also has to be under an even
     monthly pace, so a broken cache cannot spend the month in a few days.
8 leagues x 2 fetches x 31 days = 496, under the 500 even with every league in season at once (they never are).
The snapshot carries the time of the last attempt even when it found no games, so an empty answer is not re-bought on
every build. Query parameters (the key) are never logged: the build log is published.

Matching: a market row matches a game when its text names one of the game's teams (full name, or nickname such as
"Texans"), and its YES side (Kalshi yes_sub_title / the market title) names that team. Unmatched rows show a dash.
"""
from __future__ import annotations

import calendar
import json
import os
import re
import sys
import time
from pathlib import Path

LOG = lambda *a: print(*a, file=sys.stderr)
API = "https://api.the-odds-api.com/v4/sports"
LEAGUES = {"americanfootball_nfl": "NFL", "basketball_nba": "NBA", "icehockey_nhl": "NHL", "americanfootball_ncaaf": "NCAAF",
           "basketball_ncaab": "NCAAB", "soccer_epl": "EPL", "soccer_usa_mls": "MLS", "baseball_mlb": "MLB"}
MAX_AGE_S = 12 * 3600      # reuse a snapshot this long: two paid fetches a day at most
MONTH_BUDGET = 500         # the free tier's monthly credits
RESERVE = 25               # never spend the last credits (leaves room for a manual check)
GAMES: list[dict] = []     # {league, home, away, probs: {team: p}, books, start}
LAST_FETCH = {"t": 0.0}
STATE: dict = {}           # what snapshot() writes: {t, games, used, remaining, leagues}


def _tokens(team: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", team.lower())
    out = {team.lower()}
    if words:
        out.add(words[-1])                       # nickname: "texans"
        out.add(" ".join(words[:-1]))            # city: "houston"
    return {t for t in out if len(t) >= 3}


def _int(x):
    try:
        return int(float(x))
    except (TypeError, ValueError):
        return None


def _read(path) -> dict | None:
    """A snapshot file, or None if it is missing, not JSON (a CDN's HTML fallback, say) or has no timestamp."""
    try:
        c = json.loads(Path(path).read_text())
        return c if isinstance(c, dict) and float(c.get("t", 0)) > 0 and isinstance(c.get("games", []), list) else None
    except Exception:
        return None


def _full(http, url: str, params: dict):
    """(json or None, lower-cased headers, status). Uses the client's get_full when it has one (so the quota headers
    are visible); a plain get() works too, without the counters."""
    if hasattr(http, "get_full"):
        return http.get_full(url, params)
    j = http.get(url, params)
    return j, {}, 200 if j is not None else 0


def pace_allowance(now: float, per_fetch: int) -> float:
    """Credits an even monthly pace allows by `now` (UTC calendar month), plus two fetches of slack."""
    tm = time.gmtime(now)
    days = calendar.monthrange(tm.tm_year, tm.tm_mon)[1]
    return MONTH_BUDGET * (tm.tm_mday / days) + 2 * per_fetch


def snapshot() -> dict:
    return {"t": STATE.get("t", 0.0), "games": STATE.get("games", []), "used": STATE.get("used"),
            "remaining": STATE.get("remaining"), "leagues": STATE.get("leagues", [])}


def _consensus(events, label: str) -> list[dict]:
    out = []
    for ev in events or []:
        per_team: dict[str, list[float]] = {}
        books = 0
        for bk in ev.get("bookmakers") or []:
            mk = next((m for m in bk.get("markets") or [] if m.get("key") == "h2h"), None)
            if not mk:
                continue
            imp = {o["name"]: 1 / o["price"] for o in mk.get("outcomes") or [] if o.get("price")}
            tot = sum(imp.values())
            if tot <= 0:
                continue
            books += 1
            for name, v in imp.items():
                per_team.setdefault(name, []).append(v / tot)
        if per_team and books:
            out.append({"league": label, "home": ev.get("home_team"), "away": ev.get("away_team"), "start": ev.get("commence_time"),
                        "probs": {k: sum(v) / len(v) for k, v in per_team.items()}, "books": books})
    return out


def load(http, cache_path=None, max_age_s: int = MAX_AGE_S, extra_caches=None, now: float | None = None) -> int:
    """Fill GAMES from the newest snapshot if it is younger than max_age_s; otherwise fetch (inside the quota guards in
    the module docstring) and save. `extra_caches` are other copies of the snapshot (the build keeps one in the Actions
    cache and one on the data branch); the newest readable one wins. Returns the number of games loaded."""
    now = time.time() if now is None else now
    GAMES.clear()
    STATE.clear()
    LAST_FETCH["t"] = 0.0
    found = [c for c in (_read(p) for p in [cache_path, *(extra_caches or [])] if p) if c]
    prev = max(found, key=lambda c: float(c["t"])) if found else None
    if prev:
        STATE.update({"t": float(prev["t"]), "games": [], "used": prev.get("used"), "remaining": prev.get("remaining"), "leagues": prev.get("leagues", [])})
        age = now - float(prev["t"])
        if 0 <= age < max_age_s:
            GAMES[:] = prev.get("games") or []
            STATE["games"] = GAMES
            LAST_FETCH["t"] = float(prev["t"])
            LOG(f"odds: {len(GAMES)} games from the snapshot ({age / 3600:.1f} h old); no API call")
            _save(cache_path)
            return len(GAMES)
    key = os.environ.get("ODDS_API_KEY")
    if not key:
        LOG("odds: no ODDS_API_KEY; sports real-world odds off")
        STATE.clear()
        return 0
    listed, hdr, status = _full(http, API, {"apiKey": key})           # free: does not count against the quota
    if listed is None:
        LOG(f"odds: the league list did not load (status {status}); no fetch this run")
        return 0
    in_season = {s.get("key") for s in listed if isinstance(s, dict) and s.get("active", True)}
    leagues = [k for k in LEAGUES if k in in_season]
    used, remaining = _int(hdr.get("x-requests-used")), _int(hdr.get("x-requests-remaining"))
    STATE.update({"used": used, "remaining": remaining})
    if not leagues:
        LOG("odds: none of our leagues is in season; nothing to fetch")
        return _attempted(cache_path, now, [])
    if remaining is not None and remaining < len(leagues) + RESERVE:
        LOG(f"odds: {remaining} credits left this period; holding the last {RESERVE}. No fetch this run")
        return 0
    if prev is None and used is not None and used > pace_allowance(now, len(leagues)):
        LOG(f"odds: no snapshot found and {used} credits already used this month (pace allows {pace_allowance(now, len(leagues)):.0f}); no fetch this run")
        return 0
    fetched = []
    for sport in leagues:
        j, h, st = _full(http, f"{API}/{sport}/odds", {"apiKey": key, "regions": "us", "markets": "h2h", "oddsFormat": "decimal"})
        if "x-requests-remaining" in h:
            STATE["remaining"], STATE["used"] = _int(h.get("x-requests-remaining")), _int(h.get("x-requests-used"))
        if st in (401, 403, 429):
            LOG(f"odds: the API answered {st} (key or quota); stopping this fetch")
            break
        fetched.append(sport)
        GAMES.extend(_consensus(j, LEAGUES[sport]))
        if STATE.get("remaining") is not None and STATE["remaining"] < RESERVE:
            LOG(f"odds: {STATE['remaining']} credits left; stopping this fetch")
            break
    LOG(f"odds: {len(GAMES)} games with consensus across {len(fetched)} of {len(leagues)} in-season leagues (fresh fetch; "
        f"credits used {STATE.get('used')}, left {STATE.get('remaining')})")
    return _attempted(cache_path, now, fetched)


def _attempted(cache_path, now: float, leagues: list[str]) -> int:
    """Record the attempt (with or without games) so the 12-hour clock starts now."""
    STATE.update({"t": now, "games": GAMES, "leagues": leagues})
    LAST_FETCH["t"] = now
    _save(cache_path)
    return len(GAMES)


def _save(cache_path) -> None:
    if not cache_path:
        return
    try:
        Path(cache_path).parent.mkdir(parents=True, exist_ok=True)
        Path(cache_path).write_text(json.dumps(snapshot()))
    except Exception as e:
        LOG("odds snapshot not written:", repr(e))


def probability(text: str, yes_side: str) -> tuple[float, str] | None:
    """text: everything we know about the market (title + rules); yes_side: the team the YES contract pays on."""
    t, y = (text or "").lower(), (yes_side or "").lower()
    if not t or not y:
        return None
    for g in GAMES:
        teams = [g["home"], g["away"]]
        if not all(any(tok in t for tok in _tokens(tm)) for tm in teams):
            continue
        for tm in teams:
            if any(tok in y for tok in _tokens(tm)):
                p = g["probs"].get(tm)
                if p is not None:
                    return p, f"Sportsbook consensus for {tm} ({g['league']}, {g['books']} books, margin removed), The Odds API"
    return None


def selftest() -> None:
    GAMES.clear()
    GAMES.append({"league": "NFL", "home": "Tennessee Titans", "away": "Houston Texans", "start": "", "probs": {"Tennessee Titans": 0.41, "Houston Texans": 0.59}, "books": 8})
    p, why = probability("Houston at Tennessee: If Houston wins, the market resolves to Houston", "Houston")
    assert abs(p - 0.59) < 1e-9 and "8 books" in why
    assert probability("Dallas at Philadelphia", "Dallas") is None
    print("selftest ok")


if __name__ == "__main__":
    selftest()
