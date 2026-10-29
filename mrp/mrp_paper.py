#!/usr/bin/env python3
"""
Mr. P live paper trader (no orders, ever). Runs inside the sports radar every cycle (15 s) on live
Polymarket US scores + Kalshi prices and paper-trades every NFL angle we have, so tonight's games test
them in real time:

  R1 anchor     Q2/Q3: pregame underdog LEADING, its Kalshi ask 0.35-0.65 -> buy $10, hold   (validated, both seasons)
  R2 q1cheap    Q1: any team's ask <= 0.20                                -> buy $5, hold   (validated, both seasons)
  R3 blowout    Q2/Q3: team trailing by >= 17, ask 0.08-0.16              -> buy $20, hold  (the curling shot; thin sample)
  R4 halftime   price drifted > 3c during halftime -> at Q3 start buy the OTHER side, $5 (H2 hypothesis, untested)
  R5 react      a score just changed -> buy the scoring team at the first ask seen, sell at the bid 120 s later, $5
                (H4: is a 15 s score feed faster than the Kalshi book?)
  R6 decided    radar decided-state opportunity with lock=True -> buy $20 (capped by displayed depth), hold
  observe       last 2:00 of Q4 snapshots (H1), every score's Kalshi reaction path at +0/15/30/60/120 s (H4)

Positions settle from Kalshi results (status determined/finalized + result) or the Polymarket final score.
Kalshi taker fee 0.07*p*(1-p) per contract on every fill. State persists to <data dir>/paper_state.json so a
self-update restart keeps open positions; every entry/exit/settlement is also a JSONL record (sp.paper.*).
"""
from __future__ import annotations

import json
import math
import os
import re
import time
from typing import Any, Optional

THETA = 0.07
NFL_SERIES = ("KXNFLGAME", "KXNCAAFGAME")
STAKE = {"R1 anchor": 10.0, "R2 q1cheap": 5.0, "R3 blowout": 20.0, "R4 halftime": 5.0, "R5 react": 5.0, "R6 decided": 20.0}


def fee(p: float) -> float:
    return THETA * p * (1 - p)


def parse_period(period: Any, ended: bool) -> tuple[Optional[int], bool]:
    """('Q3' -> 3, False); 'HT'/'Half' -> (2, True) halftime flag; 'OT' -> 5; final -> (None, False)."""
    p = str(period or "").upper().strip()
    if ended or p in ("FT", "F", "FINAL", "END", "POST"):
        return None, False
    if p in ("HT", "HALF", "HALFTIME", "H"):
        return 2, True
    if "OT" in p:
        return 5, False
    m = re.search(r"(\d)", p)
    if m:
        return int(m.group(1)), False
    return None, False


def parse_clock(elapsed: Any) -> Optional[int]:
    m = re.search(r"(\d{1,2}):(\d\d)", str(elapsed or ""))
    return int(m.group(1)) * 60 + int(m.group(2)) if m else None


class Paper:
    def __init__(self, W, data_dir: str, decided_mod):
        self.W = W
        self.D = decided_mod
        self.path = os.path.join(data_dir, "paper_state.json")
        self.st: dict = {"open": {}, "fired": [], "pre": {}, "half": {}, "last_score": {}, "react": {}, "closed": 0, "pnl": 0.0}
        try:
            with open(self.path) as fh:
                self.st.update(json.load(fh))
        except (OSError, ValueError):
            pass

    def save(self):
        try:
            with open(self.path + ".tmp", "w") as fh:
                json.dump(self.st, fh)
            os.replace(self.path + ".tmp", self.path)
        except OSError:
            pass

    # ------------------------------------------------------------------ helpers
    def fired(self, key: str) -> bool:
        return key in self.st["fired"]

    def buy(self, rule: str, game: str, km: dict, title: str, why: str, now: float, extra: Optional[dict] = None,
            stake: Optional[float] = None) -> Optional[dict]:
        ask = km.get("ya")
        if ask is None or not (0.01 <= ask <= 0.99):
            return None
        stake = stake if stake is not None else STAKE[rule]
        n = math.floor(stake / ask)
        depth = km.get("yaq")
        if extra and extra.get("cap_depth") and depth:
            n = min(n, int(depth))
        if n < 1:
            return None
        pid = f"{rule}|{km['t']}|{int(now)}"
        pos = {"id": pid, "rule": rule, "game": game, "ticker": km["t"], "team": km.get("yes"), "title": title, "entry": ask,
               "n": n, "cost": round(n * ask + n * fee(ask), 4), "t": int(now), "why": why, "depth": depth}
        if extra:
            pos.update({k: v for k, v in extra.items() if k != "cap_depth"})
        self.st["open"][pid] = pos
        self.W.write("sp.paper.entry", pos)
        return pos

    def close(self, pid: str, payout_px: float, how: str, now: float, taker_exit: bool = False):
        pos = self.st["open"].pop(pid, None)
        if not pos:
            return
        proceeds = pos["n"] * payout_px - (pos["n"] * fee(payout_px) if taker_exit else 0.0)
        pnl = round(proceeds - pos["cost"], 4)
        rec = dict(pos, exit=payout_px, how=how, pnl=pnl, roi=round(pnl / pos["cost"], 4) if pos["cost"] else None,
                   held_s=int(now - pos["t"]))
        self.st["closed"] += 1
        self.st["pnl"] = round(self.st["pnl"] + pnl, 4)
        self.W.write("sp.paper.exit", rec)

    # ------------------------------------------------------------------ main hook
    def step(self, now: float, pm_all: list[dict], kmap: dict[str, dict], pairs: list, opps: list[dict], settled: list[dict]):
        D = self.D
        # 1) record pregame Kalshi mids for NFL/NCAAF games (kickoff role)
        for m in kmap.values():
            if not m["series"].startswith(NFL_SERIES) or m.get("status") != "active":
                continue
            if m.get("yb") is not None and m.get("ya") is not None and 0 < m["yb"] <= m["ya"] < 1:
                self.st["pre"].setdefault(m["game"], {})
                pre = self.st["pre"][m["game"]]
                if not pre.get("_locked"):
                    pre[m["t"]] = round((m["yb"] + m["ya"]) / 2, 4)
        # 2) live NFL games paired with Kalshi
        for pe, gk, kms in pairs:
            series = {m["series"] for m in kms}
            if not any(s.startswith(NFL_SERIES) for s in series):
                continue
            league = "nfl" if any(s.startswith("KXNFLGAME") for s in series) else "ncaaf"
            g = D.build_game(pe, 0.0)
            if g is None or g.totals is None:
                continue
            per, half = parse_period(pe.get("period"), bool(pe.get("ended")))
            clock = parse_clock(pe.get("elapsed"))
            pre = self.st["pre"].setdefault(gk, {})
            if pe.get("live") and not pre.get("_locked"):
                pre["_locked"] = True                       # freeze pregame mids at first live sighting
            teams = []                                       # (index in g, kalshi market)
            for km in kms:
                if not km["series"].startswith(NFL_SERIES) or km.get("status") != "active" or km["t"].endswith("-TIE"):
                    continue
                i = D.team_index(g, km.get("yes") or "")
                if i is not None:
                    teams.append((i, km))
            if len(teams) != 2 or teams[0][0] == teams[1][0]:
                continue
            title = pe["title"]
            tag = f"{league}:{gk}"
            sc = g.totals
            # observe: score changes -> reaction paths (H4) + R5 react trade
            key_sc = f"{sc[0]}-{sc[1]}"
            last = self.st["last_score"].get(gk)
            if last is not None and last != key_sc:
                a0, b0 = (int(x) for x in last.split("-"))
                scorer = 0 if sc[0] - a0 > sc[1] - b0 else 1
                rid = f"{gk}|{key_sc}|{int(now)}"
                self.st["react"][rid] = {"game": gk, "scorer": scorer, "t0": now, "score": key_sc, "period": per,
                                         "path": {str(km["t"]): [[0, km.get("yb"), km.get("ya")]] for _, km in teams}}
                km_s = next(km for i, km in teams if i == scorer)
                if not self.fired(f"R5|{rid}"):
                    self.st["fired"].append(f"R5|{rid}")
                    self.buy("R5 react", tag, km_s, title, f"{key_sc} score, buy scorer at first ask", now, {"exit_at": now + 120})
            self.st["last_score"][gk] = key_sc
            for rid, r in list(self.st["react"].items()):
                if r["game"] != gk:
                    continue
                dt = now - r["t0"]
                for i, km in teams:
                    path = r["path"].setdefault(str(km["t"]), [])
                    if dt <= 180:
                        path.append([int(dt), km.get("yb"), km.get("ya")])
                if dt > 180:
                    self.W.write("sp.react", r)
                    self.st["react"].pop(rid, None)
            # observe: last two minutes of Q4 (H1)
            if per == 4 and clock is not None and clock <= 120:
                self.W.write("sp.final2", {"game": tag, "clock": clock, "score": key_sc,
                                           "k": {km["t"]: [km.get("yb"), km.get("ya")] for _, km in teams}})
            # R4 halftime: remember mids at halftime, act at Q3 start
            hs = self.st["half"].setdefault(gk, {})
            if half:
                for i, km in teams:
                    if km.get("yb") is not None and km.get("ya") is not None:
                        hs.setdefault("start", {}).setdefault(km["t"], round((km["yb"] + km["ya"]) / 2, 4))
                        hs.setdefault("end", {})[km["t"]] = round((km["yb"] + km["ya"]) / 2, 4)
            elif per == 3 and hs.get("start") and not self.fired(f"R4|{gk}"):
                self.st["fired"].append(f"R4|{gk}")
                for i, km in teams:
                    s0 = hs["start"].get(km["t"]); s1 = hs.get("end", {}).get(km["t"])
                    if s0 is not None and s1 is not None and s1 - s0 > 0.03:
                        other = next(k for j, k in teams if j != i)
                        self.buy("R4 halftime", tag, other, title, f"{km.get('yes')} rose {s1 - s0:+.3f} at halftime; fade it", now)
                        break
            for i, km in teams:
                ask = km.get("ya")
                if ask is None:
                    continue
                diff = sc[i] - sc[1 - i]
                # R2 q1cheap
                if per == 1 and 0.02 < ask <= 0.20 and not self.fired(f"R2|{gk}|{i}"):
                    self.st["fired"].append(f"R2|{gk}|{i}")
                    self.buy("R2 q1cheap", tag, km, title, f"Q1 ask {ask:.2f}, score {key_sc}", now)
                # R1 anchor
                pm_ = pre.get(km["t"])
                if per in (2, 3) and pm_ is not None and pm_ < 0.5 and diff > 0 and 0.35 <= ask <= 0.65 and not self.fired(f"R1|{gk}"):
                    self.st["fired"].append(f"R1|{gk}")
                    self.buy("R1 anchor", tag, km, title, f"pregame dog (mid {pm_:.2f}) leads {key_sc} in Q{per}, ask {ask:.2f}", now)
                # R3 blowout
                if per in (2, 3) and diff <= -17 and 0.08 <= ask <= 0.16 and not self.fired(f"R3|{gk}|{i}"):
                    self.st["fired"].append(f"R3|{gk}|{i}")
                    self.buy("R3 blowout", tag, km, title, f"down {-diff} in Q{per}, ask {ask:.2f}", now)
        # 3) R6 decided-state locks from the radar
        for o in opps:
            if o.get("kind") != "decided_k" or not o.get("lock") or o.get("action") != "buy_yes":
                continue
            km = kmap.get(o.get("market"))
            if km and not self.fired(f"R6|{km['t']}"):
                self.st["fired"].append(f"R6|{km['t']}")
                self.buy("R6 decided", o.get("game") or km["game"], km, o.get("title") or "", o.get("reason") or "", now,
                         {"cap_depth": True, "certain": True})
        # 4) exits: timed (R5) and settlements
        res = {}
        for m in list(kmap.values()) + list(settled):
            if m.get("result") in ("yes", "no") and m.get("status") in ("determined", "finalized", "settled", "closed"):
                res[m["t"]] = 1.0 if m["result"] == "yes" else 0.0
        finals = {}
        for pe, gk, kms in pairs:
            if pe.get("ended"):
                g = D.build_game(pe, 0.0)
                if g and g.totals and g.totals[0] != g.totals[1]:
                    for km in kms:
                        i = D.team_index(g, km.get("yes") or "")
                        if i is not None and km["series"].startswith(NFL_SERIES):
                            finals[km["t"]] = 1.0 if g.totals[i] > g.totals[1 - i] else 0.0
        for pid, pos in list(self.st["open"].items()):
            if pos.get("exit_at") and now >= pos["exit_at"]:
                km = kmap.get(pos["ticker"])
                if km and km.get("yb") is not None:
                    self.close(pid, km["yb"], "timed exit at bid", now, taker_exit=True)
                    continue
            if pos["ticker"] in res:
                self.close(pid, res[pos["ticker"]], "kalshi settled", now)
            elif pos["ticker"] in finals and now - pos["t"] > 60:
                self.close(pid, finals[pos["ticker"]], "final score (pending Kalshi settlement)", now)
        # prune
        if len(self.st["fired"]) > 5000:
            self.st["fired"] = self.st["fired"][-3000:]
        self.save()
