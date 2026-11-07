"""Mr. T (terminal sniper): pure-logic tests plus the script's own selftest. No network, no key."""
import importlib.util
import sys
from pathlib import Path

spec = importlib.util.spec_from_file_location("mrt_sniper", Path(__file__).resolve().parents[1] / "scripts" / "mrt_sniper.py")
mrt = importlib.util.module_from_spec(spec)
sys.modules["mrt_sniper"] = mrt
spec.loader.exec_module(mrt)

END, PTB = 1_800_000_600, 100.00
BOOK = {"up_ask": 0.85, "up_ask_q": 40, "up_bid": 0.80, "up_bid_q": 10, "at": END - 3.0}


def test_gate_locks_on_the_running_average_not_spot():
    # 57 prints above the price to beat lock the average even if the last print dips below it
    prints = {s: 100.20 for s in range(END - 60, END - 4)} | {END - 4: 99.90}
    g = mrt.gate(prints, END, PTB, BOOK, END - 3.0)
    assert g["leader"] == "UP" and g["ok"], g
    # the margin is what the remaining prints must average, relative to the last print
    need = (60 * PTB - sum(prints.values())) / 3
    assert abs(g["margin_bps"] - abs(need - 99.90) / 99.90 * 1e4) < 0.01


def test_tie_goes_up_and_down_uses_the_up_bid():
    prints = {s: 100.00 for s in range(END - 60, END)}          # all 60 in, average exactly the price to beat
    g = mrt.gate(prints, END, PTB, BOOK, END - 0.5)
    assert g["leader"] == "UP" and g["margin_bps"] == float("inf") and g["ok"]
    g2 = mrt.gate({s: 99.5 for s in range(END - 60, END - 2)}, END, PTB, BOOK, END - 2.0)
    assert g2["leader"] == "DOWN" and abs(g2["ask"] - 0.20) < 1e-9 and g2["offered"] == 10
    o = mrt.order_for("cpc-btc-updown-5m-x", "DOWN", g2["ask"], 10)
    assert o["intent"] == "ORDER_INTENT_BUY_SHORT" and o["price"]["value"] == "0.80" and o["synchronousExecution"] is True


def test_slug_and_pnl():
    assert mrt.slug_for("btc", "5m", 1_800_000_600) == "cpc-btc-updown-5m-2027-01-15-0810z"
    assert mrt.slug_for("eth", "15m", 1_800_000_000) == "cpceth-eth-updown-15m-2027-01-15-0800z"
    tr = {"leader": "DOWN", "qty": 10, "px": 0.90, "fee": 0.0626}
    assert abs(mrt.pnl(tr, "DOWN") - (10 - 9.0 - 0.0626)) < 1e-9 and abs(mrt.pnl(tr, "UP") - (-9.0 - 0.0626)) < 1e-9


def test_selftest():
    mrt.selftest()
