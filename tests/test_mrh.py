"""Mr. H (Coinbase paper hopper): pure-logic tests plus the script's own deterministic selftest. No network."""
import importlib.util
import sys
from pathlib import Path

spec = importlib.util.spec_from_file_location("mrh_paper", Path(__file__).resolve().parents[1] / "scripts" / "mrh_paper.py")
mrh = importlib.util.module_from_spec(spec)
sys.modules["mrh_paper"] = mrh
spec.loader.exec_module(mrh)


def _cs(n=30, close=1.0, vol=100.0):
    return [{"start": 1_800_000_000 + i * 300, "open": close, "close": close, "high": close * 1.001, "low": close * 0.999, "volume": vol}
            for i in range(n)]


def test_universe_filters():
    uni = mrh.build_universe(mrh.FakeCB().products())
    assert [u["id"] for u in uni] == ["FLAT-USD", "PUMP-USD"]  # sorted by USD volume


def test_evaluate_profiles():
    cs = _cs()
    cs[-1] = {**cs[-1], "open": 1.0, "close": 1.025, "high": 1.03, "volume": 350.0}
    assert mrh.evaluate(cs, mrh.PROFILES["aggressive"])["impulse"] == 0.025
    assert mrh.evaluate(cs, mrh.PROFILES["standard"])["above_2h_high"] is True
    # inside the 2-h range: aggressive still fires, standard does not
    cs[-2] = {**cs[-2], "high": 1.05}
    assert mrh.evaluate(cs, mrh.PROFILES["aggressive"]) is not None
    assert mrh.evaluate(cs, mrh.PROFILES["standard"]) is None
    # volume gate
    cs[-1]["volume"] = 200.0
    assert mrh.evaluate(cs, mrh.PROFILES["aggressive"]) is None
    assert mrh.evaluate(cs[:10], mrh.PROFILES["aggressive"]) is None


def test_fees_and_trail():
    # a flat round trip loses exactly both taker fees
    b = mrh.Book("x")
    b.enter("A-USD", 1.0, mrh.now(), {}, 1.0)
    rec = b.mark(1.0, mrh.now(), trail=0.0)
    assert rec and abs(b.bankroll - 4.0 * (1 - mrh.TAKER_FEE) ** 2) < 1e-12
    # trailing stop: 4% off a 1.30 high-water mark fires at 1.248, not at 1.25
    b = mrh.Book("y")
    b.enter("A-USD", 1.0, mrh.now(), {}, 1.0)
    assert b.mark(1.30, mrh.now(), 0.04) is None and b.mark(1.25, mrh.now(), 0.04) is None
    assert b.mark(1.248, mrh.now(), 0.04)["reason"] == "trail"


def test_selftest():
    mrh.selftest()
