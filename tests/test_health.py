"""Health watchdog content checks and the errlog guard (no network)."""
import importlib.util, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

from pb import errlog

spec = importlib.util.spec_from_file_location("health", Path(__file__).parents[1] / "scripts" / "health_check.py")
hc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hc)


def test_watchdog_watches_what_the_business_runs_on():
    ids = {w[0] for w in hc.WATCH} | {c[0] for c in hc.CONTENT}
    assert {"site-deploy", "site-live", "recorder", "benchmark"} <= ids
    watched = " ".join(f"{w[1]} {w[3]}" for w in hc.WATCH)
    for retired in ("ef-", "polyus/", "carry", "mrh", "bounty", "paper-matrix"):     # trading-era jobs, retired 13 Nov 2026
        assert retired not in watched
    assert all(len(w) == 6 and w[2] in ("main", "data", "mrp-data") and w[4] > 0 for w in hc.WATCH)


def test_site_built_reads_the_live_stamp_and_fails_closed():
    page = '<p class="lede">One page per series. 12,080 series across both venues, rebuilt 13 Nov 2026 08:04 UTC. Crypto minutes read</p>'
    assert hc.site_built(fetch=lambda url: page) == datetime(2026, 11, 13, 8, 4, tzinfo=timezone.utc)
    assert hc.site_built(fetch=lambda url: page.replace("13 Nov", "5 Nov")) == datetime(2026, 11, 5, 8, 4, tzinfo=timezone.utc)
    assert hc.site_built(fetch=lambda url: "<html><title>PredictMeNot</title>the home page, served for an unknown path</html>") is None
    assert hc.site_built(fetch=lambda url: page.replace("13 Nov 2026", "99 Xyz 2026")) is None

    def down(url):
        raise OSError("connection refused")
    assert hc.site_built(fetch=down) is None                  # a domain that does not answer is a failed check, not a crash
    assert hc.site_built(fetch=lambda url: None) is None


def test_the_www_address_is_watched_too():
    seen = []
    hc.site_built(fetch=lambda url: seen.append(url) or "", base="https://www.predictmenot.com")
    assert seen == ["https://www.predictmenot.com/markets/"]
    checks = {c[0]: c for c in hc.CONTENT}
    assert {"site-live", "site-live-www"} <= set(checks)
    calls = []
    real = hc.site_built
    try:
        hc.site_built = lambda d=None, fetch=None, base=None: calls.append(base)
        checks["site-live-www"][2](None)
    finally:
        hc.site_built = real
    assert calls == [hc.WWW]


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
