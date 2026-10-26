"""scripts/report.py and scripts/paper_matrix.py (pure, no network)."""
import asyncio
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_report_aggregates_ledgers_and_backtests(tmp_path):
    report = _load("report")
    led = tmp_path / "ledger"
    led.mkdir()
    day1, day2 = 1792152000.0, 1792152000.0 + 86400
    fills = [
        {"type": "fill", "ts": day1 + 10, "market_id": "KXBTC15M-A", "order_id": "1", "action": "buy", "price": 0.40,
         "size": 10, "fee": 0.0, "is_maker": True},
        {"type": "fill", "ts": day2 + 10, "market_id": "KXBTC15M-A", "order_id": "2", "action": "sell", "price": 0.50,
         "size": 10, "fee": 0.07, "is_maker": False},
    ]
    for rid, fs in (("mm_crypto_twap_kxbtc15m-20261016T1200", fills[:1]), ("mm_crypto_twap_kxbtc15m-20261017T1200", fills[1:])):
        (led / f"{rid}.jsonl").write_text("\n".join(json.dumps(f) for f in fs) + "\n")
    s1 = {"run_id": "mm_crypto_twap_kxbtc15m-20261016T1200", "net_pnl": 0.0, "fees": 0.0, "fills": 1, "maker_fills": 1,
          "max_capital_at_risk": 4.0, "started_at": day1, "updated_at": day1 + 3600, "uptime_secs": 3600,
          "strategies": ["mm_crypto_twap"], "venue": "kalshi", "markets": ["KXBTC15M-A"],
          "reality": {"cross_assumed_fill_frac": 0.0}, "risk": {"halted": False}}
    s2 = dict(s1, run_id="mm_crypto_twap_kxbtc15m-20261017T1200", net_pnl=0.93, fees=0.07, maker_fills=0,
              started_at=day2, updated_at=day2 + 3600,
              reality={"cross_assumed_fill_frac": 0.8, "max_fill_to_touch_depth": 2.0}, risk={"halted": True, "halt_reason": "kill_file x"})
    s3 = {"run_id": "taker_lag_kxbtc15m-20261016T1200", "net_pnl": -1.5, "fees": 0.5, "fills": 4, "maker_fills": 0,
          "max_capital_at_risk": 10.0, "started_at": day1, "updated_at": day1 + 100, "uptime_secs": 100,
          "strategies": ["taker_lag"], "markets": ["KXBTC15M-A"]}
    for s in (s1, s2, s3):
        (led / f"{s['run_id']}.summary.json").write_text(json.dumps(s))
    rep = tmp_path / "reports"
    rep.mkdir()
    (rep / "mm_inventory.json").write_text(json.dumps([
        {"strategy": "mm_inventory", "label": "oos1", "fidelity": "L2", "n_events": 100,
         "summary": {"net_pnl": 2.5, "net_pnl_on_max_capital": 0.05, "maker_pct": 100.0, "fills": 12,
                     "max_drawdown": 0.4, "market_win_rate": 0.6},
         "reality": {"cross_assumed_fill_frac": 0.1, "top3_market_pnl_frac": 0.5}},
        {"strategy": "mm_inventory", "label": "bad", "error": "boom"}]))

    summaries, fl = report.load_paper(led)
    rows = report.paper_leaderboard(summaries, fl)
    assert [r["run"] for r in rows] == ["mm_crypto_twap_kxbtc15m", "taker_lag_kxbtc15m"]
    r = rows[0]
    assert r["net_pnl"] == pytest.approx(0.93) and r["runs"] == 2 and r["days"] == 2 and r["hours"] == 2.0
    assert r["maker_pct"] == 50.0 and r["venue"] == "kalshi" and r["ret_on_max_cap"] == pytest.approx(0.93 / 4.0)
    assert "cross-assumed 80%" in r["flags"] and "fill>touch" in r["flags"] and "HALTED" in r["flags"]
    assert rows[1]["venue"] == "kalshi" and rows[1]["flags"] == "-"
    csv_path = tmp_path / "eq.csv"
    n = report.write_equity_csv(fl, csv_path)
    lines = csv_path.read_text().splitlines()
    assert n == 2 and lines[0].startswith("run,day,")
    last = lines[-1].split(",")
    assert last[0] == "mm_crypto_twap_kxbtc15m" and float(last[4]) == pytest.approx(0.93) and float(last[5]) == pytest.approx(0.93)
    bts = report.load_backtests(rep)
    assert len(bts) == 1 and bts[0]["label"] == "oos1" and bts[0]["fidelity"] == "L2"
    md = report.render(rows, bts, n, "x.csv")
    assert "| mm_crypto_twap_kxbtc15m | mm_crypto_twap | kalshi | 0.93 |" in md
    assert "| mm_inventory | mm_inventory | oos1 | L2 | 2.50 | 5.0% |" in md
    assert report.run_group("favorite_maker_kalshi_scan-20261016T1200") == "favorite_maker_kalshi_scan"
    assert report.run_group("paper-1792152000") == "paper"
    assert report.run_group("gha-1792152000") == "gha"


def test_paper_matrix_commands_and_env_gating(monkeypatch):
    pm = _load("paper_matrix")
    m = pm.load_matrix(ROOT / "configs" / "paper_matrix.yaml")
    # 2026-10-26: the matrix is retired; the entries live under `retired:` (with a dated reason) and
    # `runs:` is empty, so the paper workflow has nothing to launch. build_command must still work on
    # them so an entry can be moved back and run unchanged.
    assert m["runs"] == []
    entries = m["retired"]
    names = [r["name"] for r in entries]
    assert "mm_crypto_twap_kxbtc15m" in names and "sharp_line_maker_kxnflgame" in names
    assert len(names) == len(set(names)) == 13
    for r in entries:
        assert r.get("retired_on") and r.get("reason"), r["name"]
    from pb.live.paper import _import_all_strategies
    from pb.strategies.base import REGISTRY

    _import_all_strategies()
    for r in entries:
        assert r["strategy"] in REGISTRY, r["name"]
        assert (ROOT / r["params"]).exists(), r["params"]
    by = {r["name"]: r for r in entries}
    cmd = pm.build_command(by["mm_crypto_twap_kxbtc15m"], m["defaults"], duration=42, run_id="rid")
    assert cmd[1].endswith("scripts/paper.py")
    s = " ".join(cmd)
    assert "--venue kalshi --strategy mm_crypto_twap --run-id rid" in s
    assert "--kalshi-series KXBTC15M --top 2 --signals coinbase,twap --duration 42" in s
    assert "--daily-loss-limit 50" in s and "--max-capital 2000" in s and "--no-record" not in s
    assert "--roll-secs 60" in s
    cmd = pm.build_command(dict(by["mm_crypto_twap_kxbtc15m"], roll_secs=0), m["defaults"])
    assert "--roll-secs 0" in " ".join(cmd)
    cmd = pm.build_command(by["taker_lag_kxbtc15m"], m["defaults"])
    assert "--set size=1" in " ".join(cmd) and "--duration 3300" in " ".join(cmd)
    cmd = pm.build_command(by["mm_inventory_kxhigh"], m["defaults"])
    assert "--kalshi-series KXHIGHNY KXHIGHMIA KXHIGHCHI" in " ".join(cmd) and "--signals" not in cmd
    cmd = pm.build_command(by["favorite_maker_kalshi_scan"], m["defaults"])
    assert "--kalshi-scan nonsports --top 20" in " ".join(cmd)
    cmd = pm.build_command(by["mm_inventory_poly_crypto15m"], m["defaults"])
    assert "--venue polymarket" in " ".join(cmd) and "--poly-crypto-15m" in cmd
    cmd = pm.build_command(by["complete_set_arb_polymarket"], m["defaults"])
    assert "--poly-events" in cmd
    assert pm.missing_env(by["sharp_line_maker_kxnflgame"], {}) == ["ODDS_API_KEY"]
    assert pm.missing_env(by["sharp_line_maker_kxnflgame"], {"ODDS_API_KEY": "k"}) == []
    assert pm.missing_env(by["mm_crypto_twap_kxbtc15m"], {}) == []
    # every generated command parses with scripts/paper.py's argparser
    paper = _load("paper")
    for r in entries:
        argv = pm.build_command(r, m["defaults"])[2:]
        monkeypatch.setattr(sys, "argv", ["paper.py", *argv])
        a = paper.parse()
        assert a.strategy == r["strategy"] and a.venue == r["venue"]


def test_paper_matrix_retired_entries_are_listed_not_run(monkeypatch, capsys):
    pm = _load("paper_matrix")
    monkeypatch.setattr(sys, "argv", ["paper_matrix.py", "--list"])
    assert pm.main() == 0
    out = capsys.readouterr().out
    assert "no active entries" in out and "oracle_lag_kxbtc15m" in out and "RETIRED 2026-10-26" in out
    monkeypatch.setattr(sys, "argv", ["paper_matrix.py", "--all"])
    assert pm.main() == 0 and "no active entries" in capsys.readouterr().out
    monkeypatch.setattr(sys, "argv", ["paper_matrix.py", "--entry", "oracle_lag_kxbtc15m"])
    assert pm.main() == 2
    assert "retired entries" in capsys.readouterr().err


def test_paper_matrix_no_markets_is_skipped_not_failed(monkeypatch, capsys, tmp_path):
    pm = _load("paper_matrix")
    # a one-entry matrix of our own: the shipped matrix has no active runs any more
    mx = tmp_path / "matrix.yaml"
    mx.write_text("defaults: {duration: 10}\nruns:\n  - {name: e1, strategy: mm_inventory, venue: polymarket, "
                  "select: {poly_crypto_15m: true, top: 2}, params: configs/mm_inventory.yaml}\n")

    class R:
        def __init__(self, rc):
            self.returncode = rc

    calls = []
    monkeypatch.setattr(pm.subprocess, "run", lambda cmd, cwd: (calls.append(cmd), R(pm.NO_MARKETS_EXIT))[1])
    monkeypatch.setattr(sys, "argv", ["paper_matrix.py", "--matrix", str(mx), "--entry", "e1"])
    assert pm.main() == 0 and calls
    assert "skipped: selector found no markets" in capsys.readouterr().out
    monkeypatch.setattr(pm.subprocess, "run", lambda cmd, cwd: R(1))
    assert pm.main() == 1


def test_report_and_dashboard_void_runs(tmp_path):
    report = _load("report")
    led = tmp_path / "ledger"
    led.mkdir()
    day = 1792152000.0
    base = {"fees": 0.0, "fills": 3, "maker_fills": 3, "max_capital_at_risk": 10.0, "started_at": day,
            "updated_at": day + 100, "uptime_secs": 100, "strategies": ["mm_crypto_twap"], "venue": "kalshi",
            "markets": ["KXBTC15M-A"], "reality": {}, "risk": {}}
    good = dict(base, run_id="mm_crypto_twap_kxbtc15m-20261017T1200", net_pnl=1.0)
    bad = dict(base, run_id="mm_crypto_twap_kxbtc15m-20261016T2316", net_pnl=222.9, fills=72)
    glob_bad = dict(base, run_id="taker_lag_kxbtc15m-20261016T1205", net_pnl=-0.5, strategies=["taker_lag"])
    for s in (good, bad, glob_bad):
        (led / f"{s['run_id']}.summary.json").write_text(json.dumps(s))
        (led / f"{s['run_id']}.jsonl").write_text(json.dumps(
            {"type": "fill", "ts": day + 1, "market_id": "KXBTC15M-A", "order_id": "1", "action": "sell",
             "price": 0.5, "size": 10, "fee": 0.0, "is_maker": True}) + "\n")
    vy = tmp_path / "voided.yaml"
    vy.write_text("voided:\n  - run_id: mm_crypto_twap_kxbtc15m-20261016T2316\n    reason: >-\n      audit: orphan\n"
                  "      orders\n  - run_id: 'taker_lag_kxbtc15m-20261016T*'\n    reason: measurement bug\n")
    voided = report.load_voided(vy)
    assert voided["mm_crypto_twap_kxbtc15m-20261016T2316"] == "audit: orphan orders"
    assert report.void_reason("taker_lag_kxbtc15m-20261016T1205", voided) == "measurement bug"
    assert report.void_reason("taker_lag_kxbtc15m-20261017T1205", voided) is None
    assert report.load_voided(tmp_path / "missing.yaml") == {}
    summaries, fl = report.load_paper(led, voided)
    rows = report.paper_leaderboard(summaries, fl)
    assert [r["run"] for r in rows] == ["mm_crypto_twap_kxbtc15m"]
    assert rows[0]["net_pnl"] == 1.0 and rows[0]["runs"] == 1          # the $222.90 is out of the total
    assert set(fl) == {"mm_crypto_twap_kxbtc15m"} and len(fl["mm_crypto_twap_kxbtc15m"]) == 1
    vrows = report.load_paper_voided(led, voided)
    assert [v["run_id"] for v in vrows] == ["mm_crypto_twap_kxbtc15m-20261016T2316", "taker_lag_kxbtc15m-20261016T1205"]
    md = report.render(rows, [], 1, "x.csv", vrows)
    assert "### Voided runs" in md and "| mm_crypto_twap_kxbtc15m-20261016T2316 | mm_crypto_twap | 222.90 | 72 |" in md
    assert "measurement bug" in md
    # without a voided file nothing changes
    summaries, fl = report.load_paper(led)
    assert len(summaries) == 3 and "Voided" not in report.render(report.paper_leaderboard(summaries, fl), [], 1, "x")
    # the repo's voided.yaml lists the audited 2026-10-16 runs
    repo = report.load_voided(ROOT / "reports" / "voided.yaml")
    assert "mm_crypto_twap_kxbtc15m-20261016T2316" in repo and "taker_lag_kxbtc15m-20261016T2316" in repo
    assert all("AUDIT_mm_crypto_twap" in r for r in repo.values())
    # dashboard: voided section rendered, totals exclude it
    dash = _load("dashboard")
    vent = tmp_path / "ventures.yaml"
    vent.write_text("ventures: []\n")
    html = dash.build(led, vent, tmp_path / "eq.csv", vy)
    assert "Voided runs" in html and "mm_crypto_twap_kxbtc15m-20261016T2316" in html
    assert "$1.00" in html and "$223.90" not in html
    html2 = dash.build(led, vent, tmp_path / "eq.csv", tmp_path / "missing.yaml")
    assert "Voided runs" not in html2


async def test_replay_check_replays_ledger_with_and_without_risk(tmp_path, capsys):
    """Record a tiny Kalshi-like window, write a ledger summary for it, replay."""
    from pb.core.types import Action, Book, Level, Market, Trade, Venue
    from pb.data.recorder import Recorder

    now = 1792152000.0
    mid = "KXBTC15M-26OCT161200-00"
    m = Market(venue=Venue.KALSHI, market_id=mid, series="KXBTC15M", open_ts=now - 900, close_ts=now + 600,
               meta={"window_open_ts": now - 900, "window_close_ts": now + 600, "window_secs": 900, "asset": "BTC"})

    def bk(ts, bid, ask, sz=50):
        return Book(ts=ts, market_id=mid, bids=[Level(bid, sz)], asks=[Level(ask, sz)])

    class Feed:
        def __init__(self, evs):
            self.evs = list(evs)

        def __aiter__(self):
            return self

        async def __anext__(self):
            if self.evs:
                await asyncio.sleep(0)
                return self.evs.pop(0)
            await asyncio.sleep(3600)

    evs = [bk(now + i, 0.45 + 0.01 * (i % 3), 0.47 + 0.01 * (i % 3)) for i in range(40)]
    evs += [Trade(now + 20.5, mid, 0.45, 5, Action.SELL)]
    rec = Recorder("kalshi", [m], tmp_path / "recorded", feed=Feed(evs), flush_secs=100, max_seconds=0.2,
                   clock=lambda: now)
    await rec.run()
    led = tmp_path / "ledger"
    led.mkdir()
    rid = "mm_inventory_kxhigh-20261016T1200"
    (led / f"{rid}.summary.json").write_text(json.dumps({
        "run_id": rid, "net_pnl": 0.5, "fills": 7, "contracts_traded": 70, "max_capital_at_risk": 9.0,
        "started_at": now, "updated_at": now + 100, "strategies": ["mm_inventory"], "markets": [mid],
        "reality": {"cross_assumed_fill_frac": 1.0, "max_fill_to_touch_depth": 1.0},
        "risk": {"accepted": 10, "rejected": 2}}))
    rc = _load("replay_check")
    assert rc.main(["--run-id", rid, "--ledger", str(led), "--data", str(tmp_path / "recorded"),
                    "--latency", "0.0", "--max-orders-per-min", "1"]) == 0
    out = capsys.readouterr().out
    assert "live ledger" in out and "replay no-risk" in out and "replay risk" in out and "delta net pnl" in out
    rc.main(["--run-id", rid, "--ledger", str(led), "--data", str(tmp_path / "recorded"), "--latency", "0.0",
             "--max-orders-per-min", "1", "--json"])
    res = json.loads(capsys.readouterr().out)
    rows = {r["source"]: r for r in res["rows"]}
    assert res["strategy"] == "mm_inventory" and res["markets"] == [mid] and res["events"] > 40
    assert rows["live ledger"]["net_pnl"] == 0.5 and rows["live ledger"]["fills"] == 7
    assert rows["replay risk"]["risk_rejected"] > 0 >= 0           # the 1/min gate rejected re-quotes
    assert rows["replay no-risk"]["fills"] >= rows["replay risk"]["fills"]
    assert res["delta_risk_minus_no_risk"] == pytest.approx(rows["replay risk"]["net_pnl"] - rows["replay no-risk"]["net_pnl"])
    assert res["delta_no_risk_minus_live"] == pytest.approx(rows["replay no-risk"]["net_pnl"] - 0.5)
