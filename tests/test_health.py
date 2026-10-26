"""Health watchdog content checks and the errlog guard (no network)."""
import importlib.util, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

from pb import errlog

spec = importlib.util.spec_from_file_location("health", Path(__file__).parents[1] / "scripts" / "health_check.py")
hc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hc)


def test_ef_autobuyer_last_check_uses_actual_read_time(tmp_path):
    d = tmp_path / "polyus" / "ef_autobuyer"; d.mkdir(parents=True)
    led = {"a": {"window_start": 1000, "checks": [{"at": 120, "t": 155.4}]},
           "b": {"window_start": 1900, "checks": []},                       # the Saturday shape: round, no checks
           "c": {"window_start": 100, "checks": [{"at": 180}]}}
    d.joinpath("ledger.json").write_text(json.dumps(led))
    assert hc.ef_autobuyer_last_check(tmp_path) == datetime.fromtimestamp(1155.4, timezone.utc)
    d.joinpath("ledger.json").write_text(json.dumps({"b": led["b"]}))
    assert hc.ef_autobuyer_last_check(tmp_path) is None


def test_polyus_log_and_tracker_generated(tmp_path):
    (tmp_path / "polyus" / "early_favorite").mkdir(parents=True)
    (tmp_path / "polyus" / "fetch-20261026T0604.log").write_text("x")
    (tmp_path / "polyus" / "fetch-20261025T2142.log").write_text("x")
    assert hc.polyus_last_fetch_log(tmp_path) == datetime(2026, 10, 26, 6, 4, tzinfo=timezone.utc)
    (tmp_path / "polyus" / "early_favorite" / "early_favorite.json").write_text(json.dumps({"generated": "2026-10-26T06:08:04Z"}))
    assert hc.ef_tracker_generated(tmp_path) == datetime(2026, 10, 26, 6, 8, 4, tzinfo=timezone.utc)


def test_errlog_guard_records_and_reraises(tmp_path):
    with pytest.raises(NameError):
        with errlog.guard("demo", out=tmp_path, step="check"):
            raise NameError("name 't0' is not defined")
    recs = errlog.read(tmp_path)
    assert len(recs) == 1 and recs[0]["bot"] == "demo" and recs[0]["fatal"] and "t0" in recs[0]["message"]
    assert recs[0]["context"] == {"step": "check"} and "NameError" in recs[0]["traceback"]
    assert errlog.read(tmp_path, since=recs[0]["t"]) == []          # strictly after
    errlog.record("demo", "fallback", "used stale data", out=tmp_path)
    assert len(errlog.read(tmp_path)) == 2 and not errlog.read(tmp_path)[1]["fatal"]
    # new records found under the data worktree pattern
    (tmp_path / "polyus" / "x").mkdir(parents=True)
    (tmp_path / "polyus" / "x" / "errors.jsonl").write_text(json.dumps({"t": "2026-10-26T00:00:00Z", "bot": "x", "kind": "K"}) + "\n")
    found = hc.new_error_records(tmp_path, "2026-10-25T00:00:00Z")
    assert {r["bot"] for r in found} == {"demo", "x"}
    assert hc.new_error_records(tmp_path, "2026-10-27T00:00:00Z") == [r for r in found if r["t"] > "2026-10-27T00:00:00Z"]


def test_guard_fails_the_process():
    code = "import sys; sys.path.insert(0, '.')\nfrom pb.errlog import guard\nwith guard('p'):\n    raise RuntimeError('boom')"
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, cwd=Path(__file__).parents[1])
    assert r.returncode == 1 and "::error title=p RuntimeError::boom" in r.stderr
