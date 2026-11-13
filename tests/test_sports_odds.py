"""scripts/sports_odds.py: the quota guards around The Odds API (no network; a fake client counts the paid calls)."""
import calendar
import importlib.util
import json
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
NOW = calendar.timegm((2026, 11, 13, 12, 0, 0))     # 13 Nov 2026 12:00 UTC: day 13 of a 30-day month


def _load():
    spec = importlib.util.spec_from_file_location("sports_odds", ROOT / "scripts" / "sports_odds.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["sports_odds"] = mod
    spec.loader.exec_module(mod)
    return mod


def _event(home="Tennessee Titans", away="Houston Texans"):
    return {"home_team": home, "away_team": away, "commence_time": "2026-11-15T18:00:00Z",
            "bookmakers": [{"key": "a", "markets": [{"key": "h2h", "outcomes": [{"name": home, "price": 2.5}, {"name": away, "price": 1.6}]}]}]}


class FakeApi:
    """The Odds API as the loader sees it: a free league list and paid per-league odds, with the usage headers."""
    def __init__(self, in_season, used=0, limit=500, odds_status=200, events=None, list_ok=True):
        self.in_season, self.used, self.limit, self.odds_status, self.list_ok = in_season, used, limit, odds_status, list_ok
        self.events = [_event()] if events is None else events
        self.paid, self.free, self.logged_params = [], 0, []

    def _hdr(self):
        return {"x-requests-used": str(self.used), "x-requests-remaining": str(self.limit - self.used)}

    def get_full(self, url, params=None, tries=2):
        assert params and params.get("apiKey") == "k"
        if url.endswith("/sports"):
            self.free += 1
            if not self.list_ok:
                return None, {}, 0
            return [{"key": k, "active": True} for k in self.in_season], self._hdr(), 200
        if self.odds_status != 200:
            return None, self._hdr(), self.odds_status
        self.used += 1
        self.paid.append(url.split("/")[-2])
        return self.events, self._hdr(), 200


@pytest.fixture
def sx(monkeypatch):
    monkeypatch.setenv("ODDS_API_KEY", "k")
    return _load()


def test_fresh_snapshot_costs_nothing(sx, tmp_path):
    cache = tmp_path / "odds.json"
    cache.write_text(json.dumps({"t": NOW - 3 * 3600, "games": [{"league": "NFL", "home": "A B", "away": "C D", "probs": {"A B": 0.4, "C D": 0.6}, "books": 3}], "used": 40, "remaining": 460}))
    api = FakeApi(["americanfootball_nfl"])
    assert sx.load(api, cache_path=str(cache), now=NOW) == 1
    assert api.free == 0 and api.paid == []                       # no call of any kind
    assert sx.snapshot()["t"] == NOW - 3 * 3600                   # the clock is the fetch time, not the reuse time


def test_stale_snapshot_fetches_only_in_season_leagues_and_records_the_attempt(sx, tmp_path):
    cache = tmp_path / "odds.json"
    cache.write_text(json.dumps({"t": NOW - 13 * 3600, "games": []}))
    api = FakeApi(["americanfootball_nfl", "basketball_nba", "soccer_epl", "tennis_atp"], used=100)
    n = sx.load(api, cache_path=str(cache), now=NOW)
    assert api.paid == ["americanfootball_nfl", "basketball_nba", "soccer_epl"]     # MLB, NHL, ... are not in season: not bought
    assert n == 3 and len(sx.GAMES) == 3
    saved = json.loads(cache.read_text())
    assert saved["t"] == NOW and saved["used"] == 103 and saved["remaining"] == 397 and len(saved["games"]) == 3
    api2 = FakeApi(["americanfootball_nfl"], used=103)             # the next build, an hour later, reuses it
    assert sx.load(api2, cache_path=str(cache), now=NOW + 3600) == 3 and api2.paid == [] and api2.free == 0


def test_an_empty_answer_is_not_bought_again_on_the_next_build(sx, tmp_path):
    cache = tmp_path / "odds.json"
    api = FakeApi(["americanfootball_nfl"], events=[])
    assert sx.load(api, cache_path=str(cache), now=NOW) == 0 and api.paid == ["americanfootball_nfl"]
    assert json.loads(cache.read_text())["t"] == NOW              # the attempt is on record with zero games
    api2 = FakeApi(["americanfootball_nfl"], events=[])
    assert sx.load(api2, cache_path=str(cache), now=NOW + 1800) == 0 and api2.paid == []


def test_the_newest_copy_of_the_snapshot_wins(sx, tmp_path):
    old, new = tmp_path / "odds.json", tmp_path / "odds.remote.json"
    old.write_text(json.dumps({"t": NOW - 30 * 3600, "games": []}))
    new.write_text(json.dumps({"t": NOW - 2 * 3600, "games": [{"league": "NBA", "home": "A B", "away": "C D", "probs": {}, "books": 1}]}))
    (tmp_path / "junk.json").write_text("<!doctype html><title>not json</title>")         # a CDN's HTML fallback
    api = FakeApi(["basketball_nba"])
    assert sx.load(api, cache_path=str(old), extra_caches=[str(new), str(tmp_path / "junk.json"), str(tmp_path / "missing.json")], now=NOW) == 1
    assert api.paid == [] and json.loads(old.read_text())["t"] == NOW - 2 * 3600          # and the primary copy is brought up to date


def test_the_last_credits_are_never_spent(sx, tmp_path):
    api = FakeApi(["americanfootball_nfl", "basketball_nba"], used=480)                 # 20 left < 2 leagues + reserve of 25
    assert sx.load(api, cache_path=str(tmp_path / "odds.json"), now=NOW) == 0
    assert api.free == 1 and api.paid == []
    assert not (tmp_path / "odds.json").exists()                                         # nothing was attempted, so no clock starts


def test_a_lost_cache_cannot_outrun_the_monthly_pace(sx, tmp_path):
    # day 13 of 30 allows 500*13/30 + 2 fetches = 216.7 + 2*n; 260 used with no snapshot anywhere means something is re-buying
    api = FakeApi(["americanfootball_nfl", "basketball_nba"], used=260)
    assert sx.load(api, cache_path=str(tmp_path / "odds.json"), now=NOW) == 0 and api.paid == []
    api2 = FakeApi(["americanfootball_nfl", "basketball_nba"], used=120)                # a new key, or a first run: under pace, so it fetches
    assert sx.load(api2, cache_path=str(tmp_path / "odds.json"), now=NOW) == 2 and len(api2.paid) == 2
    # with a snapshot on file the 12-hour clock governs and the pace check does not apply
    (tmp_path / "o2.json").write_text(json.dumps({"t": NOW - 13 * 3600, "games": []}))
    api3 = FakeApi(["americanfootball_nfl"], used=260)
    assert sx.load(api3, cache_path=str(tmp_path / "o2.json"), now=NOW) == 1 and api3.paid == ["americanfootball_nfl"]


def test_a_refused_key_stops_the_fetch_and_starts_the_clock(sx, tmp_path):
    cache = tmp_path / "odds.json"
    api = FakeApi(["americanfootball_nfl", "basketball_nba", "icehockey_nhl"], odds_status=401)
    assert sx.load(api, cache_path=str(cache), now=NOW) == 0
    assert api.paid == [] and json.loads(cache.read_text())["t"] == NOW                  # one refusal, then 12 quiet hours


def test_no_key_and_no_league_list_mean_no_calls(sx, tmp_path, monkeypatch):
    api = FakeApi(["americanfootball_nfl"], list_ok=False)
    assert sx.load(api, cache_path=str(tmp_path / "odds.json"), now=NOW) == 0 and api.paid == []
    monkeypatch.delenv("ODDS_API_KEY")
    api2 = FakeApi(["americanfootball_nfl"])
    assert sx.load(api2, cache_path=str(tmp_path / "odds.json"), now=NOW) == 0 and api2.free == 0 and api2.paid == []
    assert not sx.STATE.get("t")                                                         # market_pages writes no odds.json


def test_month_of_builds_stays_inside_the_free_tier(sx, tmp_path, capsys):
    """Thirty-one days of hourly builds. Seven leagues in season (the most that overlap in practice): two fetches a day
    all month, 434 credits. All eight at once (never happens): the reserve stops it short of the limit instead."""
    t0 = calendar.timegm((2026, 12, 1, 0, 0, 0))
    seven, api = list(sx.LEAGUES)[:7], None
    for leagues, expect in ((seven, 7 * 2 * 31), (list(sx.LEAGUES), None)):
        cache = tmp_path / f"odds{len(leagues)}.json"
        api = FakeApi(leagues)
        for h in range(31 * 24):
            sx.load(api, cache_path=str(cache), now=t0 + h * 3600)
        if expect is not None:
            assert len(api.paid) == expect == 434
        else:
            assert 8 * 2 * 29 <= api.used <= sx.MONTH_BUDGET - sx.RESERVE          # 29+ full days, and the reserve is intact
    capsys.readouterr()


def test_http_helper_never_logs_the_key(capsys):
    spec = importlib.util.spec_from_file_location("market_pages", ROOT / "scripts" / "market_pages.py")
    mp = importlib.util.module_from_spec(spec)
    sys.modules["market_pages"] = mp
    spec.loader.exec_module(mp)
    assert mp.Http._safe({"apiKey": "SECRET123", "regions": "us", "access_token": "T", "limit": 5}) == {"apiKey": "***", "regions": "us", "access_token": "***", "limit": 5}

    class Resp:
        status_code, text, headers = 404, "Unknown sport", {"X-Requests-Remaining": "7"}
        def json(self): return {}

    class Client:
        def get(self, url, params=None): return Resp()

    h = mp.Http.__new__(mp.Http)
    h.c, h.pace, h.last = Client(), 0.0, 0.0
    import threading
    h.lock = threading.Lock()
    assert h.get("https://api.example/v4/x", {"apiKey": "SECRET123"}) is None
    j, hdr, st = h.get_full("https://api.example/v4/x", {"apiKey": "SECRET123"})
    assert j is None and st == 404 and hdr["x-requests-remaining"] == "7"
    assert "SECRET123" not in capsys.readouterr().err
