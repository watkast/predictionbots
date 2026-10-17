"""scripts/report.py and scripts/paper_matrix.py (pure, no network)."""
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
    names = [r["name"] for r in m["runs"]]
    assert "mm_crypto_twap_kxbtc15m" in names and "sharp_line_maker_kxnflgame" in names
    assert len(names) == len(set(names)) == 10
    from pb.live.paper import _import_all_strategies
    from pb.strategies.base import REGISTRY

    _import_all_strategies()
    for r in m["runs"]:
        assert r["strategy"] in REGISTRY, r["name"]
        assert (ROOT / r["params"]).exists(), r["params"]
    by = {r["name"]: r for r in m["runs"]}
    cmd = pm.build_command(by["mm_crypto_twap_kxbtc15m"], m["defaults"], duration=42, run_id="rid")
    assert cmd[1].endswith("scripts/paper.py")
    s = " ".join(cmd)
    assert "--venue kalshi --strategy mm_crypto_twap --run-id rid" in s
    assert "--kalshi-series KXBTC15M --top 2 --signals coinbase,twap --duration 42" in s
    assert "--daily-loss-limit 50" in s and "--max-capital 2000" in s and "--no-record" not in s
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
    for r in m["runs"]:
        argv = pm.build_command(r, m["defaults"])[2:]
        monkeypatch.setattr(sys, "argv", ["paper.py", *argv])
        a = paper.parse()
        assert a.strategy == r["strategy"] and a.venue == r["venue"]


def test_paper_matrix_no_markets_is_skipped_not_failed(monkeypatch, capsys):
    pm = _load("paper_matrix")

    class R:
        def __init__(self, rc):
            self.returncode = rc

    calls = []
    monkeypatch.setattr(pm.subprocess, "run", lambda cmd, cwd: (calls.append(cmd), R(pm.NO_MARKETS_EXIT))[1])
    monkeypatch.setattr(sys, "argv", ["paper_matrix.py", "--entry", "mm_inventory_poly_crypto15m"])
    assert pm.main() == 0 and calls
    assert "skipped: selector found no markets" in capsys.readouterr().out
    monkeypatch.setattr(pm.subprocess, "run", lambda cmd, cwd: R(1))
    assert pm.main() == 1
