"""Backtest harness: run / sweep / walk-forward / report, low-fidelity flag,
signal merging, build_strategy for every registered strategy, YAML configs."""
import json
from pathlib import Path

import pytest
import yaml

from pb.core.types import Book, Market, Venue
from pb.data.loaders import HistoryEvents
from pb.live.paper import _import_all_strategies, build_strategy
from pb.sim import backtest as BT
from pb.sim.engine import Settlement, Signal
from pb.sim.synthetic import synthetic_events
from pb.strategies import base
from tests.helpers import book, mk, sig

ROOT = Path(__file__).resolve().parents[1]


def test_every_registered_strategy_builds_from_its_yaml():
    _import_all_strategies()
    names = set(base.REGISTRY)
    assert {"mm_crypto_twap", "mm_weather_ladder", "favorite_maker", "endgame_bond", "sharp_line_maker",
            "complete_set_arb", "cross_venue_arb", "mean_revert_overreaction", "taker_momentum", "taker_lag"} <= names
    for name in names:
        cfg = ROOT / "configs" / f"{name}.yaml"
        assert cfg.exists(), f"missing configs/{name}.yaml"
        data = yaml.safe_load(cfg.read_text())
        strat = build_strategy(name, data[name], ["M"])
        assert strat.name == name
        # grid keys must be real params
        import dataclasses
        fields = {f.name for f in dataclasses.fields(strat.p)}
        for k in (data.get("grid") or {}):
            assert k in fields, f"{name}: grid key {k} is not a param"


def test_run_backtest_synthetic_has_summary_and_reality_flags():
    spec = BT.BacktestSpec("mm_inventory", {"size": 5}, BT.DataSpec("synthetic", synthetic_kwargs={"seconds": 600}))
    r = BT.run_backtest(spec)
    assert r.error is None
    assert {"net_pnl", "fees", "fills", "maker_pct", "max_drawdown", "max_capital_at_risk",
            "net_pnl_on_max_capital", "markets_traded", "market_win_rate"} <= set(r.summary)
    assert {"cross_assumed_fill_frac", "max_fill_to_touch_depth", "top3_market_pnl_frac"} <= set(r.reality)
    assert r.fidelity == "L2"


def test_low_fidelity_history_forces_maker_requires_through():
    ms, ev = synthetic_events(seconds=300)
    h = HistoryEvents(markets=ms, events=iter(ev), low_fidelity=True)
    r = BT.run_backtest(BT.BacktestSpec("mm_inventory", {}, BT.DataSpec("history", history=h)))
    assert r.error is None and r.fidelity.startswith("low")
    # explicit override wins
    h2 = HistoryEvents(markets=ms, events=iter(ev), low_fidelity=True)
    r2 = BT.run_backtest(BT.BacktestSpec("mm_inventory", {}, BT.DataSpec("history", history=h2),
                                         sim={"maker_requires_through": False}))
    assert r2.fidelity == "L2"


def test_signals_are_merged_in_ts_order_and_reach_strategy():
    m = mk("KXPRES-X", series="KXPRES", close_ts=1e7)
    events = [book(0, [(0.80, 20)], [(0.82, 20)], m.market_id), book(10, [(0.80, 20)], [(0.82, 20)], m.market_id)]
    sigs = [sig(5, "fcst_prob", 0.5, m.market_id)]
    markets, ev, low = BT.load_data(BT.DataSpec("events", events=([m], events), signals=sigs))
    assert [type(e).__name__ for e in ev] == ["Book", "Signal", "Book"]


def test_grid_sweep_parallel_and_walk_forward_and_report(tmp_path):
    spec = BT.BacktestSpec("mm_inventory", {}, BT.DataSpec("synthetic", synthetic_kwargs={"seconds": 900}))
    data = BT.load_data(spec.data)
    rs = BT.grid_sweep(spec, {"size": [5, 10], "gamma": [0.01, 0.02]}, workers=2, data=data)
    assert len(rs) == 4 and all(r.error is None for r in rs)
    assert {(r.params["size"], r.params["gamma"]) for r in rs} == {(5, 0.01), (5, 0.02), (10, 0.01), (10, 0.02)}
    wf = BT.walk_forward(spec, 3, data=data)
    assert [r.label for r in wf] == ["fold0", "fold1", "fold2"]
    assert all(r.error is None for r in wf) and wf[0].n_events > 0
    wf2 = BT.walk_forward(spec, 3, grid={"size": [5, 10]}, data=data)
    assert [r.label for r in wf2] == ["oos1", "oos2"]
    assert "selected_in_sample" in wf2[0].reality
    md, js = BT.write_report(rs + wf2, tmp_path, "t")
    text = md.read_text()
    assert "| strategy |" in text and "Reality flags" in text and "mm_inventory" in text
    j = json.loads(js.read_text())
    assert len(j) == 6 and j[0]["summary"]["fills"] >= 0


def test_backtest_error_is_captured_not_raised():
    r = BT.run_backtest(BT.BacktestSpec("does_not_exist", {}, BT.DataSpec("synthetic", synthetic_kwargs={"seconds": 10})))
    assert r.error and "does_not_exist" in r.error


def test_books_are_not_mutated_across_runs():
    spec = BT.BacktestSpec("taker_momentum", {"move": 0.0, "size": 10, "cooldown": 0.0},
                           BT.DataSpec("synthetic", synthetic_kwargs={"seconds": 200, "depth": 5.0}))
    data = BT.load_data(spec.data)
    sizes_before = [l.size for e in data[1] if isinstance(e, Book) for l in e.asks]
    BT.run_backtest(spec, data)
    sizes_after = [l.size for e in data[1] if isinstance(e, Book) for l in e.asks]
    assert sizes_before == sizes_after


def test_default_fee_for_distinguishes_venues():
    k = Market(venue=Venue.KALSHI, market_id="KXNFLGAME-1", series="KXNFLGAME")
    p = Market(venue=Venue.POLYMARKET, market_id="tok", meta={"category": "politics"})
    f = BT.default_fee_for([k, p])
    assert f("KXNFLGAME-1").maker_rate > 0 and f("tok").taker_rate == 0.04 and f("tok").maker_rate == 0


def test_cli_parse_grid():
    import importlib.util
    spec = importlib.util.spec_from_file_location("bt_cli", ROOT / "scripts" / "backtest.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.parse_grid("size=5,10;mode=taker,maker_kalshi") == {"size": [5, 10], "mode": ["taker", "maker_kalshi"]}
    assert mod.parse_grid(None) == {}
