"""Link venue sports markets to Odds-API events: team-name normalisation.

The Odds API names teams in full ("Dallas Cowboys"); Kalshi encodes them as
3-letter codes in the ticker (`KXNFLGAME-26OCT19DALWAS-DAL` = Dallas @
Washington on 2026-10-19, YES = Dallas wins); Polymarket uses nicknames in
the question ("Cowboys vs. Commanders", outcomes ["Cowboys", "Commanders"]).

* `normalize_team(text, sport=None) -> canonical full name | None`
* `parse_kalshi_sports_ticker(ticker) -> KalshiGame | None`
* `parse_polymarket_question(title, outcomes) -> (team_a, team_b, yes_team) | None`
* `build_links(markets, odds_events=None) -> list[OddsLink]`: the matcher the
  paper runner feeds into `pb.data.feeds.odds_api_sharp_prob` / `espn_game_state`.
  With `odds_events` (the `/sports/{sport}/odds` payload, or `/events`) a link
  is only emitted when the teams AND the date (±1 day) agree with an event;
  without, the link carries the canonical names and the odds feed's own
  `_team_eq` match applies.
* `ODDS_API_SPORT_KEYS`: "nfl" -> "americanfootball_nfl" etc.

No I/O here.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable, Optional

from pb.core.types import Market, Venue
from pb.data.feeds import OddsLink, _iso_ts

ODDS_API_SPORT_KEYS = {"nfl": "americanfootball_nfl", "nba": "basketball_nba", "mlb": "baseball_mlb",
                       "nhl": "icehockey_nhl", "ncaaf": "americanfootball_ncaaf", "ncaab": "basketball_ncaab"}
ESPN_SPORT_PATHS = {"nfl": "football/nfl", "nba": "basketball/nba", "mlb": "baseball/mlb", "nhl": "hockey/nhl"}
KALSHI_SERIES_SPORT = {"KXNFLGAME": "nfl", "KXNBAGAME": "nba", "KXMLBGAME": "mlb", "KXNHLGAME": "nhl",
                       "KXNFL": "nfl", "KXNBA": "nba", "KXMLB": "mlb", "KXNHL": "nhl"}

# (code, full name, extra aliases). Full name == The Odds API / ESPN display name.
_TEAMS: dict[str, list[tuple[str, str, tuple[str, ...]]]] = {
    "nfl": [
        ("ARI", "Arizona Cardinals", ()), ("ATL", "Atlanta Falcons", ()), ("BAL", "Baltimore Ravens", ()),
        ("BUF", "Buffalo Bills", ()), ("CAR", "Carolina Panthers", ()), ("CHI", "Chicago Bears", ()),
        ("CIN", "Cincinnati Bengals", ()), ("CLE", "Cleveland Browns", ()), ("DAL", "Dallas Cowboys", ()),
        ("DEN", "Denver Broncos", ()), ("DET", "Detroit Lions", ()), ("GB", "Green Bay Packers", ("GNB",)),
        ("HOU", "Houston Texans", ()), ("IND", "Indianapolis Colts", ()), ("JAX", "Jacksonville Jaguars", ("JAC",)),
        ("KC", "Kansas City Chiefs", ("KAN",)), ("LV", "Las Vegas Raiders", ("LVR", "OAK", "Oakland Raiders")),
        ("LAC", "Los Angeles Chargers", ("SD", "San Diego Chargers", "LA Chargers")),
        ("LAR", "Los Angeles Rams", ("LA", "St. Louis Rams", "LA Rams")), ("MIA", "Miami Dolphins", ()),
        ("MIN", "Minnesota Vikings", ()), ("NE", "New England Patriots", ("NWE",)),
        ("NO", "New Orleans Saints", ("NOR",)), ("NYG", "New York Giants", ("NY Giants",)),
        ("NYJ", "New York Jets", ("NY Jets",)), ("PHI", "Philadelphia Eagles", ()),
        ("PIT", "Pittsburgh Steelers", ()), ("SF", "San Francisco 49ers", ("SFO", "Niners")),
        ("SEA", "Seattle Seahawks", ()), ("TB", "Tampa Bay Buccaneers", ("TAM", "Bucs")),
        ("TEN", "Tennessee Titans", ()), ("WAS", "Washington Commanders", ("WSH", "Washington Football Team",
                                                                           "Washington Redskins")),
    ],
    "nba": [
        ("ATL", "Atlanta Hawks", ()), ("BOS", "Boston Celtics", ()), ("BKN", "Brooklyn Nets", ("BRK", "NJN")),
        ("CHA", "Charlotte Hornets", ("CHO",)), ("CHI", "Chicago Bulls", ()), ("CLE", "Cleveland Cavaliers", ("Cavs",)),
        ("DAL", "Dallas Mavericks", ("Mavs",)), ("DEN", "Denver Nuggets", ()), ("DET", "Detroit Pistons", ()),
        ("GSW", "Golden State Warriors", ("GS",)), ("HOU", "Houston Rockets", ()), ("IND", "Indiana Pacers", ()),
        ("LAC", "Los Angeles Clippers", ("LA Clippers",)), ("LAL", "Los Angeles Lakers", ("LA Lakers",)),
        ("MEM", "Memphis Grizzlies", ()), ("MIA", "Miami Heat", ()), ("MIL", "Milwaukee Bucks", ()),
        ("MIN", "Minnesota Timberwolves", ("Wolves",)), ("NOP", "New Orleans Pelicans", ("NO", "NOLA")),
        ("NYK", "New York Knicks", ("NY Knicks",)), ("OKC", "Oklahoma City Thunder", ()),
        ("ORL", "Orlando Magic", ()), ("PHI", "Philadelphia 76ers", ("Sixers",)), ("PHX", "Phoenix Suns", ("PHO",)),
        ("POR", "Portland Trail Blazers", ("Blazers",)), ("SAC", "Sacramento Kings", ()),
        ("SAS", "San Antonio Spurs", ("SA",)), ("TOR", "Toronto Raptors", ()), ("UTA", "Utah Jazz", ("UTAH",)),
        ("WAS", "Washington Wizards", ("WSH",)),
    ],
    "mlb": [
        ("ARI", "Arizona Diamondbacks", ("AZ", "D-backs", "Dbacks")), ("ATL", "Atlanta Braves", ()),
        ("BAL", "Baltimore Orioles", ()), ("BOS", "Boston Red Sox", ()), ("CHC", "Chicago Cubs", ()),
        ("CWS", "Chicago White Sox", ("CHW",)), ("CIN", "Cincinnati Reds", ()), ("CLE", "Cleveland Guardians", ("Indians",)),
        ("COL", "Colorado Rockies", ()), ("DET", "Detroit Tigers", ()), ("HOU", "Houston Astros", ()),
        ("KC", "Kansas City Royals", ("KCR",)), ("LAA", "Los Angeles Angels", ("ANA", "LA Angels")),
        ("LAD", "Los Angeles Dodgers", ("LA Dodgers",)), ("MIA", "Miami Marlins", ()), ("MIL", "Milwaukee Brewers", ()),
        ("MIN", "Minnesota Twins", ()), ("NYM", "New York Mets", ("NY Mets",)), ("NYY", "New York Yankees", ("NY Yankees",)),
        ("OAK", "Oakland Athletics", ("ATH", "Athletics", "A's", "Sacramento Athletics")), ("PHI", "Philadelphia Phillies", ()),
        ("PIT", "Pittsburgh Pirates", ()), ("SD", "San Diego Padres", ("SDP",)), ("SF", "San Francisco Giants", ("SFG",)),
        ("SEA", "Seattle Mariners", ()), ("STL", "St. Louis Cardinals", ("St Louis Cardinals",)),
        ("TB", "Tampa Bay Rays", ("TBR",)), ("TEX", "Texas Rangers", ()), ("TOR", "Toronto Blue Jays", ()),
        ("WSH", "Washington Nationals", ("WAS", "Nats")),
    ],
    "nhl": [
        ("ANA", "Anaheim Ducks", ()), ("BOS", "Boston Bruins", ()), ("BUF", "Buffalo Sabres", ()),
        ("CGY", "Calgary Flames", ("CAL",)), ("CAR", "Carolina Hurricanes", ("Canes",)), ("CHI", "Chicago Blackhawks", ()),
        ("COL", "Colorado Avalanche", ("Avs",)), ("CBJ", "Columbus Blue Jackets", ()), ("DAL", "Dallas Stars", ()),
        ("DET", "Detroit Red Wings", ()), ("EDM", "Edmonton Oilers", ()), ("FLA", "Florida Panthers", ()),
        ("LAK", "Los Angeles Kings", ("LA", "LA Kings")), ("MIN", "Minnesota Wild", ()), ("MTL", "Montreal Canadiens", ("MON", "Montréal Canadiens", "Habs")),
        ("NSH", "Nashville Predators", ("Preds",)), ("NJD", "New Jersey Devils", ("NJ",)), ("NYI", "New York Islanders", ("NY Islanders",)),
        ("NYR", "New York Rangers", ("NY Rangers",)), ("OTT", "Ottawa Senators", ("Sens",)), ("PHI", "Philadelphia Flyers", ()),
        ("PIT", "Pittsburgh Penguins", ("Pens",)), ("SJS", "San Jose Sharks", ("SJ",)), ("SEA", "Seattle Kraken", ()),
        ("STL", "St. Louis Blues", ("St Louis Blues",)), ("TBL", "Tampa Bay Lightning", ("TB", "Bolts")),
        ("TOR", "Toronto Maple Leafs", ("Leafs",)), ("UTA", "Utah Mammoth", ("UTAH", "Utah Hockey Club", "Utah HC")),
        ("VAN", "Vancouver Canucks", ()), ("VGK", "Vegas Golden Knights", ("VEG", "LV", "Las Vegas Golden Knights")),
        ("WSH", "Washington Capitals", ("WAS", "Caps")), ("WPG", "Winnipeg Jets", ("WIN",)),
    ],
}


def _key(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def _build_index() -> dict[str, dict[str, str]]:
    """sport -> {normalised alias: full name}. Aliases: code, full name, city,
    nickname (last word(s)), and the extras."""
    out: dict[str, dict[str, str]] = {}
    for sport, teams in _TEAMS.items():
        idx: dict[str, str] = {}
        nick_count: dict[str, int] = {}
        for code, full, extras in teams:
            nick = full.split()[-1]
            nick_count[_key(nick)] = nick_count.get(_key(nick), 0) + 1
        for code, full, extras in teams:
            words = full.split()
            nick = words[-1]
            city = " ".join(words[:-1])
            # multi-word nicknames
            cands = {code, full, nick, city, *extras}
            if nick.lower() in ("sox", "jays", "blazers", "wings", "jackets", "leafs", "knights"):
                cands.add(" ".join(words[-2:]))
            for c in cands:
                k = _key(c)
                if not k:
                    continue
                # a plain city shared by two teams of the same league (LA, NY, Chicago) is ambiguous
                if c == city and sum(1 for _, f, _ in teams if f.startswith(city + " ")) > 1:
                    continue
                if c == nick and nick_count[_key(nick)] > 1:
                    continue
                idx.setdefault(k, full)
        out[sport] = idx
    return out


_INDEX = _build_index()


def sports() -> list[str]:
    return list(_TEAMS)


def normalize_team(text: str, sport: Optional[str] = None) -> Optional[str]:
    """Canonical full name for a code / nickname / city / full name, or None.
    Without `sport` every league is searched; an alias that resolves to
    different teams in different leagues (e.g. "DAL") returns None."""
    k = _key(text)
    if not k:
        return None
    leagues = [sport.lower()] if sport else list(_INDEX)
    exact = {_INDEX[lg][k] for lg in leagues if k in _INDEX.get(lg, {})}
    if exact:
        return exact.pop() if len(exact) == 1 else None
    # "Dallas Cowboys (-3.5)" / "Cowboys ML" -> longest alias contained in the text,
    # across leagues; the longest one wins ("dallascowboys" beats "dallas").
    hits: list[tuple[int, str]] = []
    for lg in leagues:
        for a, full in _INDEX.get(lg, {}).items():
            if len(a) >= 4 and a in k:
                hits.append((len(a), full))
    if not hits:
        return None
    top = max(n for n, _ in hits)
    best = {f for n, f in hits if n == top}
    return best.pop() if len(best) == 1 else None


def team_eq(a: str, b: str, sport: Optional[str] = None) -> bool:
    na, nb = normalize_team(a, sport), normalize_team(b, sport)
    if na and nb:
        return na == nb
    return _key(a) == _key(b) and bool(_key(a))


# ----------------------------------------------------------------------------
# Kalshi tickers
# ----------------------------------------------------------------------------
_KALSHI_GAME_RE = re.compile(
    r"^(?P<series>KX[A-Z]+?)-(?P<yy>\d{2})(?P<mon>[A-Z]{3})(?P<dd>\d{2})(?P<teams>[A-Z]{4,8})(?:-(?P<outcome>[A-Z]{2,4}))?$",
    re.I)
_MONTHS = {m: i for i, m in enumerate(
    ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"], 1)}


@dataclass(frozen=True)
class KalshiGame:
    sport: str
    date: str            # YYYY-MM-DD (US game date)
    away: str            # canonical full name
    home: str
    outcome: str         # canonical full name whose win == YES ("" for a non-winner market, e.g. tie)
    away_code: str = ""
    home_code: str = ""


def _split_codes(codes: str, sport: str) -> Optional[tuple[str, str]]:
    """'DALWAS' -> ('DAL','WAS'); codes are 2-3 letters each, so try every split."""
    idx = _INDEX.get(sport, {})
    for i in range(2, len(codes) - 1):
        a, b = codes[:i], codes[i:]
        if 2 <= len(a) <= 3 and 2 <= len(b) <= 3 and _key(a) in idx and _key(b) in idx:
            return a, b
    return None


def parse_kalshi_sports_ticker(ticker: str, sport: Optional[str] = None) -> Optional[KalshiGame]:
    m = _KALSHI_GAME_RE.match((ticker or "").strip().upper())
    if not m:
        return None
    series = m.group("series")
    sport = (sport or KALSHI_SERIES_SPORT.get(series) or
             next((s for k, s in KALSHI_SERIES_SPORT.items() if series.startswith(k)), None))
    if not sport:
        return None
    split = _split_codes(m.group("teams"), sport)
    if split is None:
        return None
    away_c, home_c = split
    away, home = _INDEX[sport][_key(away_c)], _INDEX[sport][_key(home_c)]
    try:
        date = f"20{m.group('yy')}-{_MONTHS[m.group('mon')]:02d}-{int(m.group('dd')):02d}"
    except KeyError:
        return None
    oc = m.group("outcome") or ""
    outcome = _INDEX[sport].get(_key(oc), "") if oc else ""
    if oc and not outcome:
        outcome = ""  # e.g. "-TIE"
    return KalshiGame(sport=sport, date=date, away=away, home=home, outcome=outcome,
                      away_code=away_c, home_code=home_c)


# ----------------------------------------------------------------------------
# Polymarket questions
# ----------------------------------------------------------------------------
_VS_RE = re.compile(r"^\s*(?P<a>.+?)\s+(?:vs\.?|v\.?|@|at)\s+(?P<b>.+?)\s*(?:\(|:|-\s|$)", re.I)
_WIN_RE = re.compile(r"will\s+(?:the\s+)?(?P<t>.+?)\s+(?:win|beat|defeat)\b(?:\s+(?:the\s+)?(?P<o>[A-Za-z0-9 .'-]+?))?(?:\s+on\b|\s+in\b|\?|$)", re.I)


def parse_polymarket_question(title: str, outcomes: Iterable[str] = (), sport: Optional[str] = None
                              ) -> Optional[tuple[str, str, str]]:
    """-> (team_a, team_b, yes_team) canonical names. `outcomes[0]` is the YES
    token's outcome on Polymarket; for "Will X beat Y?" YES == X."""
    outs = [str(o) for o in outcomes]
    teams: list[str] = []
    yes = None
    m = _VS_RE.match(title or "")
    if m:
        teams = [normalize_team(m.group("a"), sport) or "", normalize_team(m.group("b"), sport) or ""]
    else:
        w = _WIN_RE.search(title or "")
        if w:
            t = normalize_team(w.group("t"), sport)
            o = normalize_team(w.group("o") or "", sport) if w.group("o") else None
            if t:
                yes = t
                teams = [t, o or ""]
    if outs and len(outs) >= 2:
        o0, o1 = normalize_team(outs[0], sport), normalize_team(outs[1], sport)
        if o0 and o1:
            teams = [o0, o1] if not all(teams) else teams
            yes = yes or o0
        elif o0 and yes is None and outs[0].lower() not in ("yes", "no"):
            yes = o0
    if yes is None and teams and all(teams):
        yes = teams[0]
    if not teams or not all(teams) or not yes:
        return None
    return teams[0], teams[1], yes


# ----------------------------------------------------------------------------
# Odds-API event matching
# ----------------------------------------------------------------------------
def _event_date(ev: dict) -> Optional[str]:
    ts = _iso_ts(ev.get("commence_time"))
    if ts is None:
        return None
    # US game date: commence_time is UTC; shift by -5h so late-evening ET games keep their date
    return datetime.fromtimestamp(ts - 5 * 3600, tz=timezone.utc).strftime("%Y-%m-%d")


def _date_close(a: Optional[str], b: Optional[str], tol_days: int = 1) -> bool:
    if not a or not b:
        return True
    try:
        da, db = datetime.fromisoformat(a), datetime.fromisoformat(b)
    except ValueError:
        return True
    return abs((da - db).days) <= tol_days


def match_event(home: str, away: str, events: Iterable[dict], sport: Optional[str] = None,
                date: Optional[str] = None) -> Optional[dict]:
    """Find the Odds-API event with these teams (either orientation, date ±1 day)."""
    cands = []
    for ev in events:
        eh, ea = normalize_team(str(ev.get("home_team", "")), sport), normalize_team(str(ev.get("away_team", "")), sport)
        if {eh, ea} != {home, away} or not (eh and ea):
            continue
        if not _date_close(date, _event_date(ev)):
            continue
        cands.append(ev)
    if not cands:
        return None
    # prefer an exact orientation match
    for ev in cands:
        if normalize_team(str(ev.get("home_team", "")), sport) == home:
            return ev
    return cands[0]


def link_market(market: Market, odds_events: Optional[Iterable[dict]] = None,
                sport: Optional[str] = None) -> Optional[OddsLink]:
    """One market -> OddsLink (or None if the market is not a recognised game)."""
    meta = market.meta or {}
    if market.venue is Venue.KALSHI:
        g = parse_kalshi_sports_ticker(market.market_id, sport)
        if g is None or not g.outcome:
            return None
        sport, home, away, outcome, date = g.sport, g.home, g.away, g.outcome, g.date
    else:
        sp = sport or meta.get("sport")
        parsed = parse_polymarket_question(market.title or meta.get("question", ""), meta.get("outcomes", []), sp)
        if parsed is None:
            return None
        a, b, outcome = parsed
        # "A vs B" on Polymarket is usually away vs home (US convention) but not reliably; let the
        # events decide orientation when we have them.
        home, away = b, a
        sport = sp or next((lg for lg in _INDEX if a in _INDEX[lg].values() and b in _INDEX[lg].values()), "")
        date = datetime.fromtimestamp(market.close_ts, tz=timezone.utc).strftime("%Y-%m-%d") if market.close_ts else None
    if odds_events is not None:
        ev = match_event(home, away, odds_events, sport, date)
        if ev is None:
            return None
        home = normalize_team(str(ev.get("home_team")), sport) or home
        away = normalize_team(str(ev.get("away_team")), sport) or away
    return OddsLink(market_id=market.market_id, home_team=home, away_team=away, outcome=outcome, sport=sport or "")


def build_links(markets: Iterable[Market], odds_events: Optional[Iterable[dict]] = None,
                sport: Optional[str] = None) -> list[OddsLink]:
    evs = list(odds_events) if odds_events is not None else None
    out = []
    for m in markets:
        ln = link_market(m, evs, sport)
        if ln is not None:
            out.append(ln)
    return out


def sport_for_markets(markets: Iterable[Market]) -> Optional[str]:
    """Infer the league from Kalshi series tickers (first match)."""
    for m in markets:
        if m.venue is Venue.KALSHI:
            g = parse_kalshi_sports_ticker(m.market_id)
            if g:
                return g.sport
        sp = (m.meta or {}).get("sport")
        if sp:
            return str(sp).lower()
    return None


__all__ = ["ODDS_API_SPORT_KEYS", "ESPN_SPORT_PATHS", "KALSHI_SERIES_SPORT", "KalshiGame", "normalize_team",
           "team_eq", "parse_kalshi_sports_ticker", "parse_polymarket_question", "match_event", "link_market",
           "build_links", "sport_for_markets", "sports"]
