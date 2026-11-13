"""The public ledger (scripts/ledger_build.py -> site/data/bot_trades.json): the committed file adds up, the home page
quotes it correctly, and the parsers book a trade the way the bots did. No network."""
import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load():
    spec = importlib.util.spec_from_file_location("ledger_build", ROOT / "scripts" / "ledger_build.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["ledger_build"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def data():
    return json.loads((ROOT / "site" / "data" / "bot_trades.json").read_text())


def test_committed_file_adds_up(data):
    _load().selfcheck(data)                                   # the bots' own reported totals, and the nine unlogged rounds
    t, rows, bots = data["total"], data["rows"], data["bots"]
    assert t["trips"] == len(rows) == sum(b["trips"] for b in bots)
    assert round(sum(r["n"] for r in rows), 2) == t["net"] == round(sum(b["net"] for b in bots), 2)
    assert t["won"] == sum(r["n"] > 0 for r in rows) and t["lost"] == sum(r["n"] < 0 for r in rows) and t["flat"] == sum(r["n"] == 0 for r in rows)
    assert abs(sum(r["cost"] for r in rows) - t["staked"]) < 0.06 * len(bots)   # rows carry cents; bots sum the unrounded costs
    for i, b in enumerate(bots):
        mine = [r for r in rows if r["b"] == i]
        assert len(mine) == b["trips"] and round(sum(r["n"] for r in mine), 2) == b["net"]
    assert rows == sorted(rows, key=lambda r: r["t"], reverse=True)
    for r in rows:
        assert r["cost"] > 0 and r["i"] > 0 and r["w"] and r["u"] in ("c", "$")
        assert r["n"] >= -r["cost"] - 0.011                    # nobody loses more than the stake on a long position
        assert bool(r.get("f")) == bool(r.get("e"))           # a flagged row says where its result came from
        if r["u"] == "c":
            assert 0 < r["i"] < 1 and 0 <= r["o"] <= 1


def test_home_page_quotes_the_file(data):
    html = (ROOT / "site" / "index.html").read_text()
    t = data["total"]
    faq = re.search(r"<h3>Did your own bots make money\?</h3><p>(.*?)</p>", html).group(1)
    assert f"{t['trips']} logged round trips" in faq and f"${abs(t['net']):.2f}" in faq
    assert "two out of three" in faq and 0.62 < t["won"] / t["trips"] < 0.71
    assert "about 8 cents on every dollar" in faq and 0.075 <= abs(t["net"]) / t["staked"] < 0.085
    assert "/data/bot_trades.json" in html and 'id="ledger-bots"' in html and 'id="ledger-unlogged"' in html and 'id="ledger-gaps"' in html
    g = data["gaps"]                                           # what no log shows is stated, with its bounds, not left out
    assert len(g["windows"]) == 3 and 0 < g["low"] < g["high"] and "roughly $3 to $9" in html and round(g["low"]) == 3 and round(g["high"]) == 9
    assert "Every trade is below" not in html                  # the old claim, made over six of 269 rows


def test_mr_e_books_logged_and_unlogged_rounds():
    lb = _load()
    slug = "cpc-btc-updown-15m-2026-11-03-0715z"              # in UNLOGGED: held with 2 seconds left, venue settled Up
    state = {"mode": "live", "rounds": [
        {"T0": 1793687400, "slug": "x-1", "side": "DOWN", "buyPx": 0.25, "qty": 6, "exit": "6 lost at the bell", "pnl": -1.5},
        {"T0": 1793688300, "slug": "x-2", "side": "UP", "buyPx": 0.275, "qty": 6, "exit": "sold at 41¢ avg", "pnl": 0.83},
        {"T0": 1793689200, "slug": "x-3", "side": None, "buyPx": None, "exit": "no fill", "pnl": None},
        {"T0": 1793690100, "slug": slug, "side": "DOWN", "buyPx": 0.275, "qty": 6, "exit": "held to the bell", "pnl": None},
        {"T0": 1793691000, "slug": "x-5", "side": "UP", "buyPx": 0.3, "exit": "lost at the bell", "pnl": -0.3}]}   # early rounds: one share, no qty
    rows = lb.mr_e(json.dumps(state), "", "BTC")
    assert [r["n"] for r in rows] == [-1.5, 0.83, -1.65, -0.3]                       # the unfilled round is not a trade
    assert rows[0]["o"] == 0 and rows[1]["o"] == pytest.approx(0.4133, abs=1e-4) and rows[3]["s"] == "Up"
    unlogged = rows[2]
    assert unlogged["f"] == 1 and unlogged["w"] == "6 lost at the bell" and "settled Up" in unlogged["e"] and unlogged["t"] == "2026-11-03T07:30:00Z"
    # a sale on record before the restart is booked from the log line, not from the venue's result
    sold = {"t": 1, "k": "fill", "d": {"slug": slug, "side": "DOWN", "sold": 0.45, "qty": 6, "soldTotal": 6, "of": 6}}
    r = lb.mr_e(json.dumps({"mode": "live", "rounds": [state["rounds"][3]]}), json.dumps(sold), "BTC")[0]
    assert r["n"] == 1.05 and r["w"] == "sold at 45¢" and r["o"] == pytest.approx(0.45)
    # an early (taker) exit carries the fee the bot booked
    stall = {"t": 1, "k": "fill", "d": {"slug": slug, "side": "DOWN", "sold": 0.40, "qty": 6, "exit": "stall"}}
    r = lb.mr_e(json.dumps({"mode": "live", "rounds": [state["rounds"][3]]}), json.dumps(stall), "BTC")[0]
    assert r["n"] == round(6 * (0.40 - 0.0695 * 0.4 * 0.6) - 1.65, 2)
    with pytest.raises(AssertionError):                       # a new unresolved round cannot slip in as a silent zero
        lb.mr_e(json.dumps({"mode": "live", "rounds": [{"T0": 1, "slug": "not-in-the-table", "side": "UP", "buyPx": 0.3, "qty": 2, "pnl": None}]}), "", "BTC")


def test_mr_p_pairs_fills_from_live_runs_only():
    lb = _load()
    L = lambda t, k, **d: json.dumps({"t": t, "k": k, "d": d})
    log = "\n".join([
        L(1000, "start", mode="dry"), L(2000, "fill", kind="buy", side="UP", px=0.5, qty=10, usd=5.0),          # a dry run's fill: ignored
        L(3000, "start", mode="live"),
        L(1793615735841, "fill", kind="buy", side="UP", px=0.64, qty=30, usd=19.2),
        L(1793615774000, "fill", kind="sell", side="UP", px=0.53, qty=30, proceeds=15.38)])
    rows = lb.mr_p(log)
    assert len(rows) == 1 and rows[0]["n"] == -4.30 and rows[0]["cost"] == pytest.approx(30 * (0.64 + 0.0695 * 0.64 * 0.36), abs=1e-4)
    assert rows[0]["s"] == "Up ×30" and rows[0]["i"] == 0.64 and rows[0]["o"] == 0.53
    with pytest.raises(AssertionError):                       # a live position the log never closes must not vanish
        lb.mr_p("\n".join([L(1, "start", mode="live"), L(2, "fill", kind="buy", side="UP", px=0.5, qty=1, usd=0.5)]))


def test_mr_h_takes_the_bots_own_net():
    lb = _load()
    log = "\n".join([json.dumps({"t": "2026-11-07T08:30:30Z", "ev": "buy", "pid": "CT-USD", "px": 0.1346, "qty": 24.5, "cost": 3.3284}),
                     json.dumps({"t": "2026-11-07T09:50:15Z", "ev": "sell", "pid": "CT-USD", "px": 0.1393, "qty": 24.5, "proceeds": 3.3816, "net": 0.0532, "entry_px": 0.1346, "reason": "stop"})])
    rows = lb.mr_h(log)
    assert len(rows) == 1 and rows[0]["n"] == 0.05 and rows[0]["m"] == "CT · Coinbase" and rows[0]["cost"] == pytest.approx(3.3284)
