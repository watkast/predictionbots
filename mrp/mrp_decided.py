#!/usr/bin/env python3
"""
Decided-state engine: from a live game state (Polymarket US sportradar feed: score, period, periodScores
keyed by competitor id, ended flag) decide which Kalshi / Polymarket contracts are ALREADY settled by
logic while they still trade.

    decide_k(game, kmarket) -> Decision | None      Kalshi sub-markets (totals, 1H totals, BTTS, 1H BTTS,
                                                     1H winner/tie, tennis set winners, CS2 total maps / map
                                                     spread, match/game winners once the game ended)
    decide_pm(game, pm_market) -> Decision | None   Polymarket winner markets once the game ended

Only monotone facts are used (scores never go down; a finished period never changes) EXCEPT that a
just-scored goal can be overturned (VAR / video review). Every decision carries score_age_s; the radar
treats a decision as a lock only after the score has been stable for SETTLE_AGE[sport] seconds.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

VOID_PERIODS = {"POST", "PST", "CANC", "CAN", "ABD", "ABAN", "INT", "DEL", "SUS", "WO", "RET", "CANCELLED", "POSTPONED"}
# seconds the score must be unchanged before a goal-dependent decision counts as a lock (reviews / corrections)
SETTLE_AGE = {"soccer": 240, "ice-hockey": 240, "football": 300, "basketball": 90, "esports": 60, "tennis": 30,
              "table-tennis": 30, "darts": 30, "cricket": 120, "beach-volleyball": 30}
FIRST_HALF = {"1H", "H1", "FIRST_HALF"}
AFTER_FIRST_HALF = {"HT", "2H", "H2", "FT", "ET", "AET", "PEN", "AP", "OT", "SECOND_HALF", "ENDED"}


@dataclass
class Game:
    slug: str
    sport: str
    period: str
    ended: bool
    teams: list[dict]                        # [{id, name}] in title / score order
    per: list[tuple[str, dict]]              # [(label, {competitor_id: score})] in order
    totals: Optional[tuple[int, int]]        # (team0, team1) running totals for plain-score sports
    score_age_s: float = 0.0
    raw_score: str = ""
    tok: list[set] = field(default_factory=list)   # name tokens per team


@dataclass
class Decision:
    yes: bool              # True: YES is certain; False: NO is certain
    reason: str
    score_dependent: bool  # depends on a goal that could still be reviewed


def _tok(s: str) -> set:
    return {w for w in re.sub(r"[^a-z0-9 ]", " ", (s or "").lower()).split() if len(w) >= 3}


def build_game(pe: dict, score_age_s: float) -> Optional[Game]:
    teams = [t for t in pe.get("teams") or [] if t.get("id") is not None][:2]
    period = str(pe.get("period") or "").upper().strip()
    if period in VOID_PERIODS or len(teams) != 2:
        return None
    per = []
    for p in pe.get("periodScores") or []:
        sc = {str(s.get("competitorId")): s.get("score") for s in p.get("scores") or []}
        per.append((str(p.get("label") or "").upper(), sc))
    ids = [str(t["id"]) for t in teams]
    totals = None
    sc = pe.get("score")
    mm = re.fullmatch(r"\s*(\d+)\s*-\s*(\d+)\s*", sc) if isinstance(sc, str) else None
    if mm and pe.get("sport") not in ("tennis", "table-tennis", "beach-volleyball", "cricket"):
        totals = (int(mm.group(1)), int(mm.group(2)))
        # cross-check the score order against periodScores when available (must agree, else distrust)
        if per and all(all(i in d for i in ids) for _, d in per):
            s0 = sum(int(d[ids[0]] or 0) for _, d in per)
            s1 = sum(int(d[ids[1]] or 0) for _, d in per)
            if (s0, s1) != totals:
                totals = None if (s1, s0) != totals else (s0, s1)
    return Game(slug=pe.get("slug"), sport=str(pe.get("sport") or ""), period=period, ended=bool(pe.get("ended")),
                teams=teams, per=per, totals=totals, score_age_s=score_age_s, raw_score=str(sc or ""),
                tok=[_tok(t.get("name")) for t in teams])


def first_half(g: Game) -> tuple[Optional[tuple[int, int]], bool]:
    """(1H score, 1H finished?)"""
    ids = [str(t["id"]) for t in g.teams]
    for lab, d in g.per:
        if lab in FIRST_HALF or lab in ("1", "P1H"):
            if all(i in d for i in ids):
                return (int(d[ids[0]] or 0), int(d[ids[1]] or 0)), (g.period in AFTER_FIRST_HALF or g.ended or len(g.per) > 1)
    if g.totals is not None and g.period in FIRST_HALF:
        return g.totals, False
    if g.totals is not None and g.period == "HT":
        return g.totals, True
    return None, False


def sets_won(g: Game) -> Optional[tuple[int, int]]:
    ids = [str(t["id"]) for t in g.teams]
    done = completed_periods(g)
    w = [0, 0]
    for lab, d in done:
        a, b = int(d.get(ids[0]) or 0), int(d.get(ids[1]) or 0)
        if a == b:
            return None
        w[0 if a > b else 1] += 1
    return tuple(w)


def completed_periods(g: Game) -> list[tuple[str, dict]]:
    """Every period except the one in progress (all of them once the game ended)."""
    return list(g.per) if g.ended else list(g.per[:-1])


def team_index(g: Game, name: str) -> Optional[int]:
    t = _tok(name)
    hits = [i for i in (0, 1) if g.tok[i] & t and not (g.tok[1 - i] & t - g.tok[i])]
    hits = [i for i in (0, 1) if (g.tok[i] - g.tok[1 - i]) & t]
    return hits[0] if len(hits) == 1 else None


def winner(g: Game) -> Optional[int]:
    """Index of the winner once the game ended (None if unknown / tie)."""
    if not g.ended:
        return None
    if g.sport in ("tennis", "table-tennis", "beach-volleyball"):
        w = sets_won(g)
        if w and w[0] != w[1]:
            return 0 if w[0] > w[1] else 1
        return None
    if g.totals is not None and g.totals[0] != g.totals[1]:
        return 0 if g.totals[0] > g.totals[1] else 1
    return None


def classify_k(series: str, ticker: str) -> str:
    s = series.upper()
    if "SETWINNER" in s:
        return "set_winner"
    if s.endswith("TOTALMAPS"):
        return "total_maps"
    if "1HBTTS" in s:
        return "h1_btts"
    if s.endswith("BTTS"):
        return "btts"
    if "TEAMTOTAL" in s:
        return "team_total"                      # one team's own goals: a different quantity from the game total
    if "1HTOTAL" in s:
        return "h1_total"
    if "1HSPREAD" in s:
        return "h1_spread"
    if s.endswith("1H"):
        return "h1_winner"
    if "TOTAL" in s:
        return "total"
    if "SPREAD" in s:
        return "spread"
    if s.endswith("MAP"):
        return "map_winner"
    if s.endswith(("GAME", "MATCH", "DOUBLES")):
        return "winner"
    return "other"


def decide_k(g: Game, km: dict) -> Optional[Decision]:
    kind = classify_k(km.get("series") or "", km.get("t") or "")
    tick = str(km.get("t") or "")
    is_tie = tick.endswith("-TIE")
    strike = km.get("strike")
    try:
        strike = float(strike) if strike is not None else None
    except (TypeError, ValueError):
        strike = None
    yes_name = km.get("yes") or ""

    if kind == "total" and strike is not None and g.totals is not None:
        tot = sum(g.totals)
        if tot > strike:
            return Decision(True, f"score {g.raw_score} total {tot} > {strike}", True)
        if g.ended:
            return Decision(False, f"ended total {tot} <= {strike}", True)
    if kind == "btts" and g.totals is not None:
        if g.totals[0] > 0 and g.totals[1] > 0:
            return Decision(True, f"both scored {g.raw_score}", True)
        if g.ended:
            return Decision(False, f"ended {g.raw_score}", True)
    if kind in ("h1_total", "h1_btts", "h1_winner"):
        h1, done = first_half(g)
        if h1 is not None:
            if kind == "h1_total" and strike is not None:
                if sum(h1) > strike:
                    return Decision(True, f"1H {h1} > {strike}", True)
                if done:
                    return Decision(False, f"1H final {h1} <= {strike}", True)
            if kind == "h1_btts":
                if h1[0] > 0 and h1[1] > 0:
                    return Decision(True, f"1H both scored {h1}", True)
                if done:
                    return Decision(False, f"1H final {h1}", True)
            if kind == "h1_winner" and done:
                if is_tie:
                    return Decision(h1[0] == h1[1], f"1H final {h1}", True)
                i = team_index(g, yes_name)
                if i is not None:
                    return Decision(h1[i] > h1[1 - i], f"1H final {h1}", True)
    if kind == "set_winner":
        m = re.search(r"-(\d+)-[A-Z0-9]+$", tick)
        n = int(m.group(1)) if m else None
        done = completed_periods(g)
        i = team_index(g, yes_name)
        if n and i is not None and len(done) >= n:
            ids = [str(t["id"]) for t in g.teams]
            d = done[n - 1][1]
            a, b = int(d.get(ids[0]) or 0), int(d.get(ids[1]) or 0)
            if a != b:
                return Decision((a > b) == (i == 0), f"set {n} final {a}-{b}", False)
    if kind == "total_maps" and strike is not None:
        m = re.search(r"MAP\s*(\d+)", g.period)
        if m and int(m.group(1)) > strike:
            return Decision(True, f"{g.period} in progress > {strike} maps", False)
    if kind == "spread" and g.sport == "esports" and strike is not None:
        m = re.search(r"MAP\s*(\d+)", g.period)
        if m and int(m.group(1)) >= 3 and strike >= 1.5:
            # a best-of-3 that reached map 3 cannot be won by 2 maps
            return Decision(False, f"{g.period}: no 2-0 possible", False)
    if kind in ("winner", "spread") and g.ended:
        w = winner(g)
        if kind == "winner":
            if is_tie and g.totals is not None:
                return Decision(g.totals[0] == g.totals[1], f"ended {g.raw_score}", True)
            i = team_index(g, yes_name)
            if w is not None and i is not None:
                return Decision(w == i, f"ended {g.raw_score}", True)
        if kind == "spread" and strike is not None and g.totals is not None:
            i = team_index(g, yes_name)
            if i is not None:
                margin = g.totals[i] - g.totals[1 - i]
                return Decision(margin > strike, f"ended {g.raw_score} margin {margin} vs {strike}", True)
    return None


def decide_pm(g: Game, m: dict) -> Optional[Decision]:
    """Polymarket winner market once the game ended: long side = team (tennis-style) or Yes for teamId / draw."""
    if not g.ended:
        return None
    t = str(m.get("type") or "").lower()
    if "winner" not in t and "moneyline" not in t:
        return None
    longs = [s for s in m.get("sides") or [] if s.get("long")]
    if not longs:
        return None
    lg = longs[0]
    ids = [t_["id"] for t_ in g.teams]
    w = winner(g)
    if lg.get("team") in ids and str(lg.get("desc") or "").lower() not in ("yes", "no"):
        if w is None:
            return None
        return Decision(ids.index(lg["team"]) == w, f"ended {g.raw_score}", True)
    if str(lg.get("desc") or "").lower() == "yes":
        if lg.get("team") in ids and w is not None:
            return Decision(ids.index(lg["team"]) == w, f"ended {g.raw_score}", True)
        if lg.get("team") is None and g.totals is not None and "draw" in (m.get("slug") or "") + (m.get("q") or "").lower():
            return Decision(g.totals[0] == g.totals[1], f"ended {g.raw_score}", True)
    return None


def edge(dec: Decision, bid: Optional[float], ask: Optional[float], theta: float) -> Optional[tuple[str, float, float]]:
    """(action, price, margin per contract after taker fee) for the certain side, or None if no price."""
    if dec.yes and ask is not None and 0 < ask < 1:
        return "buy_yes", ask, round(1 - ask - theta * ask * (1 - ask), 4)
    if not dec.yes and bid is not None and 0 < bid < 1:
        return "sell_yes", bid, round(bid - theta * bid * (1 - bid), 4)
    return None


if __name__ == "__main__":
    pe = {"slug": "x", "sport": "soccer", "period": "2H", "ended": False, "score": "1-2",
          "teams": [{"id": 1, "name": "Al Khaleej Saudi Club"}, {"id": 2, "name": "Al Hazem SC"}],
          "periodScores": [{"label": "1H", "scores": [{"competitorId": "1", "score": 1}, {"competitorId": "2", "score": 1}]},
                           {"label": "2H", "scores": [{"competitorId": "1", "score": 0}, {"competitorId": "2", "score": 1}]}]}
    g = build_game(pe, 600)
    cases = [({"series": "KXSAUDIPLTOTAL", "t": "KXSAUDIPLTOTAL-26OCT29KHAHAZ-3", "strike": 2.5, "yes": "Over 2.5"}, True),
             ({"series": "KXSAUDIPLTOTAL", "t": "KXSAUDIPLTOTAL-26OCT29KHAHAZ-4", "strike": 3.5, "yes": "Over 3.5"}, None),
             ({"series": "KXSAUDIPLBTTS", "t": "KXSAUDIPLBTTS-26OCT29KHAHAZ-BTTS", "yes": "Both Teams To Score"}, True),
             ({"series": "KXSAUDIPL1HTOTAL", "t": "KXSAUDIPL1HTOTAL-26OCT29KHAHAZ-2", "strike": 1.5, "yes": "Over 1.5"}, True),
             ({"series": "KXSAUDIPL1HTOTAL", "t": "KXSAUDIPL1HTOTAL-26OCT29KHAHAZ-3", "strike": 2.5, "yes": "Over 2.5"}, False),
             ({"series": "KXSAUDIPL1H", "t": "KXSAUDIPL1H-26OCT29KHAHAZ-TIE", "yes": "Tie 1st Half"}, True),
             ({"series": "KXSAUDIPL1H", "t": "KXSAUDIPL1H-26OCT29KHAHAZ-KHA", "yes": "Al-Khaleej"}, False),
             ({"series": "KXSAUDIPLGAME", "t": "KXSAUDIPLGAME-26OCT29KHAHAZ-HAZ", "yes": "Al-Hazm"}, None)]
    for km, want in cases:
        d = decide_k(g, km)
        got = None if d is None else d.yes
        assert got == want, (km["t"], got, want, d)
    tn = {"slug": "t", "sport": "tennis", "period": "S3", "ended": False, "score": "6-4, 3-6, 2-2",
          "teams": [{"id": 3128, "name": "Alex Michelsen"}, {"id": 3061, "name": "Arthur Fils"}],
          "periodScores": [{"label": "S1", "scores": [{"competitorId": "3128", "score": 6}, {"competitorId": "3061", "score": 4}]},
                           {"label": "S2", "scores": [{"competitorId": "3128", "score": 3}, {"competitorId": "3061", "score": 6}]},
                           {"label": "S3", "scores": [{"competitorId": "3128", "score": 2}, {"competitorId": "3061", "score": 2}]}]}
    g = build_game(tn, 60)
    assert decide_k(g, {"series": "KXATPSETWINNER", "t": "KXATPSETWINNER-26OCT29MICFIL-2-MIC", "yes": "Alex Michelsen"}).yes is False
    assert decide_k(g, {"series": "KXATPSETWINNER", "t": "KXATPSETWINNER-26OCT29MICFIL-1-MIC", "yes": "Alex Michelsen"}).yes is True
    assert decide_k(g, {"series": "KXATPSETWINNER", "t": "KXATPSETWINNER-26OCT29MICFIL-3-FIL", "yes": "Arthur Fils"}) is None
    tn["ended"], tn["period"] = True, "FT"
    tn["periodScores"][2]["scores"] = [{"competitorId": "3128", "score": 6}, {"competitorId": "3061", "score": 3}]
    g = build_game(tn, 60)
    pmm = {"type": "tennis_match_winner", "sides": [{"long": True, "desc": "Alex Michelsen", "team": 3128}]}
    assert decide_pm(g, pmm).yes is True
    assert decide_k(g, {"series": "KXATPMATCH", "t": "KXATPMATCH-26OCT29MICFIL-FIL", "yes": "Arthur Fils"}).yes is False
    assert build_game(dict(tn, period="POST"), 60) is None
    print(edge(Decision(True, "", True), 0.90, 0.93, 0.07), edge(Decision(False, "", True), 0.05, 0.08, 0.07))
    print("ok")
