import json
from datetime import date
from pathlib import Path

import yaml

import metrics

HERE = Path(__file__).resolve().parents[1]


def test_bundled_metrics_json_loads_and_matches_portfolio():
    data = metrics.load(HERE / "metrics.json")
    assert data["as_of"]
    ids = {p["id"] for p in data["products"]}
    port = yaml.safe_load((HERE / "portfolio.yaml").read_text())
    port_ids = {p["id"] for p in port["products"]}
    assert ids <= port_ids, "every metrics product must be in portfolio.yaml"
    assert "oddsmath" in ids
    s = metrics.summarize(data)
    assert s["totals"]["mrr_usd"] == 0 and s["totals"]["sunset_candidates"] == []
    assert s["rows"][0]["verdict"] == "n/a"


def test_missing_file_is_empty_portfolio(tmp_path):
    s = metrics.dashboard_rows(tmp_path / "nope.json")
    assert s["rows"] == [] and s["totals"]["products"] == 0 and s["totals"]["min_uptime_pct_30d"] is None


def _prod(**kw):
    base = {"id": "x", "status": "live", "launched": "2026-08-01", "mrr_usd": 50, "revenue_30d_usd": 60,
            "cost_usd_30d": 5, "uptime_pct_30d": 99.9, "support_minutes_30d": 10}
    base.update(kw)
    return base


def test_kill_rules():
    today = date(2026, 10, 17)   # 77 days after 2026-08-01
    assert metrics.verdict(_prod(), today)[0] == "OK"
    v, why = metrics.verdict(_prod(mrr_usd=5), today)
    assert v == "SUNSET" and "MRR" in why[0]
    v, why = metrics.verdict(_prod(support_minutes_30d=90), today)
    assert v == "SUNSET" and "support" in why[0]
    v, why = metrics.verdict(_prod(uptime_pct_30d=97.0), today)
    assert v == "WATCH" and "uptime" in why[0]
    v, why = metrics.verdict(_prod(revenue_30d_usd=1, cost_usd_30d=5), today)
    assert v == "WATCH" and "net margin" in why[0]
    # young product with low MRR: not killed yet, but watched inside the last 2 weeks
    assert metrics.verdict(_prod(mrr_usd=0, launched="2026-10-01"), today)[0] == "OK"
    assert metrics.verdict(_prod(mrr_usd=0, launched="2026-08-25"), today)[0] == "WATCH"
    assert metrics.verdict(_prod(status="building"), today)[0] == "n/a"


def test_summary_totals_and_cli(tmp_path, capsys):
    p = tmp_path / "m.json"
    p.write_text(json.dumps({"as_of": "2026-10-17", "products": [
        _prod(id="a"), _prod(id="b", mrr_usd=0, revenue_30d_usd=0, cost_usd_30d=3, launched="2026-07-01")]}))
    s = metrics.dashboard_rows(p, date(2026, 10, 17))
    assert s["totals"]["mrr_usd"] == 50 and s["totals"]["net_30d_usd"] == 52
    assert s["totals"]["sunset_candidates"] == ["b"]
    assert s["totals"]["min_uptime_pct_30d"] == 99.9
    assert metrics.main(["--path", str(p)]) == 0
    out = capsys.readouterr().out
    assert "SUNSET" in out and "TOTAL mrr=$50" in out
    assert metrics.main(["--path", str(p), "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["totals"]["live"] == 2
