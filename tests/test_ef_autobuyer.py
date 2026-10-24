"""Early Favorite auto-buyer: book parsing, favorite side, limit fills, P&L."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("efa", Path(__file__).parents[1] / "scripts" / "ef_autobuyer.py")
efa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(efa)


def book(bids, offers):
    amt = lambda p: {"value": str(p), "currency": "USD"}
    return {"marketData": {"marketSlug": "x", "state": "MARKET_STATE_OPEN",
                           "bids": [{"px": amt(p), "qty": str(q)} for p, q in bids],
                           "offers": [{"px": amt(p), "qty": str(q)} for p, q in offers],
                           "stats": {"lastPriceSample": {"longPx": amt(0.85), "shortPx": amt(0.16)}}}}


def test_parse_sorts_and_reads_sample():
    b = efa.parse_book(book([(0.80, 10), (0.84, 5)], [(0.90, 3), (0.86, 7)]))
    assert b["bids"][0] == (0.84, 5.0) and b["offers"][0] == (0.86, 7.0)
    assert b["long_px"] == 0.85


def test_up_favorite_entry_and_limit_fill():
    b = efa.parse_book(book([(0.84, 50)], [(0.85, 40), (0.86, 100), (0.90, 500)]))
    e = efa.decide(b)
    assert e["side"] == "Up" and e["ask"] == 0.85 and e["limit"] == 0.86
    f = e["fills"]["100"]
    # 40 @ .85 = 34, then 66/.86 = 76.74 @ .86 -> full $100, never touches .90
    assert f["fill_frac"] == 1.0 and 0.85 < f["vwap"] < 0.86
    big = e["fills"]["250"]
    assert big["fill_frac"] < 1.0       # .90 level is above the limit


def test_down_favorite_uses_bids():
    b = efa.parse_book(book([(0.12, 1000), (0.10, 1000)], [(0.14, 1000)]))
    e = efa.decide(b)
    assert e["side"] == "Down" and abs(e["ask"] - 0.88) < 1e-9


def test_out_of_band_no_entry():
    assert efa.decide(efa.parse_book(book([(0.70, 100)], [(0.72, 100)]))) is None
    assert efa.decide(efa.parse_book(book([(0.96, 100)], [(0.97, 100)]))) is None


def test_pnl_includes_fee():
    win = efa.pnl(100, 0.85, True, 0.0695)
    loss = efa.pnl(100, 0.85, False, 0.0695)
    fee = 0.0695 * 0.85 * 0.15 * 100
    assert abs(win - (15 - fee)) < 1e-3 and abs(loss - (-85 - fee)) < 1e-3


def test_read_book_retries_until_window_closes():
    # fake clock: each call advances 1 s; a fake gateway that 404s (None) for the first 3 reads
    t = {"now": 1000.0}
    clock = lambda: t["now"]

    def tick(s):
        t["now"] += s

    calls = []

    def get(path):
        calls.append(path)
        tick(0.1)
        return {"marketData": {}} if len(calls) > 3 else None

    j, tries, t_read, lat = efa.read_book(get, "slug-a", until=1000.0 + 45, every=5, clock=clock, sleep=tick)
    assert j is not None and tries == 4 and 1015.0 <= t_read <= 1016.0 and 0 < lat < 0.2
    assert calls[0] == efa.BOOK_PATH.format(slug="slug-a")


def test_read_book_gives_up_at_window_end():
    t = {"now": 2000.0}
    clock = lambda: t["now"]
    tick = lambda s: t.__setitem__("now", t["now"] + s)
    n = {"c": 0}

    def get(path):
        n["c"] += 1
        return None

    j, tries, t_read, _ = efa.read_book(get, "slug-b", until=2000.0 + 45, every=5, clock=clock, sleep=tick)
    assert j is None and tries == n["c"] == 9 and t_read == 2040.0
