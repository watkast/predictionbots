"""Real-world odds for sports game-winner markets: sportsbook consensus from The Odds API (the-odds-api.com).

Needs ODDS_API_KEY (free tier: 500 requests a month; one request per league per run, so hourly runs need the paid
tier or a slower cadence; the site-deploy workflow calls this at most every 6 hours). For each upcoming game we take
every bookmaker's moneyline, convert to implied probabilities, remove the bookmaker margin (normalise each book's two
or three outcomes to sum to 1), and average across books. That is the consensus, stated as such on the page.

Matching: a market row matches a game when its text names one of the game's teams (full name, or nickname such as
"Texans"), and its YES side (Kalshi yes_sub_title / the market title) names that team. Unmatched rows show a dash.
"""
from __future__ import annotations

import os
import re
import sys
import time

LOG = lambda *a: print(*a, file=sys.stderr)
LEAGUES = {"americanfootball_nfl": "NFL", "basketball_nba": "NBA", "icehockey_nhl": "NHL", "americanfootball_ncaaf": "NCAAF",
           "basketball_ncaab": "NCAAB", "soccer_epl": "EPL", "soccer_usa_mls": "MLS", "baseball_mlb": "MLB"}
GAMES: list[dict] = []        # {league, home, away, probs: {team: p}, books, start}
LAST_FETCH = {"t": 0.0}


def _tokens(team: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", team.lower())
    out = {team.lower()}
    if words:
        out.add(words[-1])                       # nickname: "texans"
        out.add(" ".join(words[:-1]))            # city: "houston"
    return {t for t in out if len(t) >= 3}


def load(http, cache_path=None, max_age_s: int = 6 * 3600) -> int:
    """Use a cached snapshot (from the previous deploy) if it is younger than max_age_s; otherwise fetch and save.
    Keeps the free tier's 500 requests a month: 8 leagues x 4 fetches a day x 30 days = 960 is the paid tier, so the
    default leagues list is trimmed to what is in season at deploy time by the API's own empty responses."""
    import json
    from pathlib import Path
    if cache_path and Path(cache_path).exists():
        try:
            c = json.loads(Path(cache_path).read_text())
            if time.time() - float(c.get("t", 0)) < max_age_s and c.get("games"):
                GAMES[:] = c["games"]; LAST_FETCH["t"] = float(c["t"])
                LOG(f"odds: {len(GAMES)} games from cache ({(time.time() - LAST_FETCH['t']) / 3600:.1f} h old)")
                return len(GAMES)
        except Exception as e:
            LOG("odds cache unreadable:", repr(e))
    key = os.environ.get("ODDS_API_KEY")
    if not key:
        LOG("odds: no ODDS_API_KEY; sports real-world odds off")
        return 0
    for sport, label in LEAGUES.items():
        j = http.get(f"https://api.the-odds-api.com/v4/sports/{sport}/odds", {"apiKey": key, "regions": "us", "markets": "h2h", "oddsFormat": "decimal"})
        for ev in (j or []):
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
                GAMES.append({"league": label, "home": ev.get("home_team"), "away": ev.get("away_team"), "start": ev.get("commence_time"),
                              "probs": {k: sum(v) / len(v) for k, v in per_team.items()}, "books": books})
    LAST_FETCH["t"] = time.time()
    LOG(f"odds: {len(GAMES)} games with consensus across {len(LEAGUES)} leagues (fresh fetch)")
    if cache_path:
        Path(cache_path).parent.mkdir(parents=True, exist_ok=True)
        Path(cache_path).write_text(json.dumps({"t": LAST_FETCH["t"], "games": GAMES}))
    return len(GAMES)


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
