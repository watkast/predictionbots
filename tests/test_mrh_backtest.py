"""Mr. H backtest (historical replay of the hopper's signal rule): pure-logic tests plus the script's own selftest. No network."""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("mrh_backtest", ROOT / "scripts" / "mrh_backtest.py")
bt = importlib.util.module_from_spec(spec)
sys.modules["mrh_backtest"] = bt
spec.loader.exec_module(bt)


def test_replay_scores_one_spike_with_the_paper_rule():
    cs = bt._synthetic(100)
    sigs = [s for s in bt.replay("TEST-USD", cs, {c["start"]: 1.0 for c in cs}) if s["profile"] == "aggressive"]
    assert len(sigs) == 1
    s = sigs[0]
    # the same evaluate() as paper and live: impulse 5% on 10x volume
    assert s["impulse"] == 0.05 and s["vol_mult"] == 10.0 and s["fresh"] and s["scored"]
    # forward score and trail nets are paper's own functions on the 48 candles after the signal
    after = cs[101:149]
    assert s["r4h"] == round(after[-1]["close"] / s["close"] - 1, 4)
    assert s["trail4_net"] == round(bt.trail_pnl(after, s["close"], 0.04), 4)
    assert all(f"trail{t}_net" in s for t in (3, 4, 6, 8, 12)) and "hold4h_net" in s
    # continuation entry: the next candle held (+1%), so it has its own trail nets from that close
    assert s["held"] and abs(s["r_next"] - 0.01) < 1e-9 and s["cont_trail4_net"] < s["trail4_net"]


def test_fresh_flag_and_unscored_tail():
    cs = bt._synthetic(100)
    btc = {c["start"]: 1.0 for c in cs}
    cs[103] = {**cs[103], "open": cs[102]["close"], "close": cs[102]["close"] * 1.03, "volume": 10.0}
    flags = [s["fresh"] for s in bt.replay("TWO-USD", cs, btc) if s["profile"] == "aggressive"]
    assert flags == [True, False]
    late = [s for s in bt.replay("LATE-USD", bt._synthetic(380, 400), btc) if s["profile"] == "aggressive"]
    assert len(late) == 1 and late[0]["scored"] is False and "trail4_net" not in late[0]


def test_report_renders(tmp_path):
    cs = bt._synthetic(100)
    rows = bt.replay("TEST-USD", cs, {c["start"]: 1.0 for c in cs}) * 40
    (tmp_path / "backtest_signals.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    (tmp_path / "coins.json").write_text(json.dumps({"meta": {"generated": "t", "days": 30, "top": 0, "window_start": "a",
                                                                "window_end": "b", "universe": 1, "calls": 1, "seconds": 1}}))
    md = bt.report(tmp_path)
    for needle in ("## Verdict", "| 4% |", "## Continuation entry", "BTC 2-h regime", "| TEST |"):
        assert needle in md


def test_selftest():
    bt.selftest()
