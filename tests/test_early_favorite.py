"""Early Favorite forward tracker: rule triggers, settlement, pending, fee."""
import json

from scripts.early_favorite_tracker import RULE, score, summarize

WS = 1_792_600_000


def _round(tmp, slug, ws, prices, ptb=None, sp=None):
    # prices keyed by ELAPSED minute; history labels run one minute behind (label = elapsed - 1)
    hist = [{"timestamp": ws + 60 * (m - 1), "longPrice": ua, "shortPrice": da} for m, (ua, da) in prices.items()]
    (tmp / "price_history" / f"{slug}.json").write_text(json.dumps(
        {"slug": slug, "windowStart": ws, "windowEnd": ws + 900, "history": hist}))
    terms = {"priceToBeat": {"value": str(ptb)} if ptb else None, "settlementPrice": {"value": str(sp)} if sp else None}
    return {"slug": slug, "assetPriceTerms": terms}


def test_rule(tmp_path):
    (tmp_path / "price_history").mkdir()
    mk = [
        _round(tmp_path, "a", WS, {2: (0.85, 0.16), 3: (0.90, 0.11)}, 100, 101),        # Up 0.85 at m2, Up wins
        _round(tmp_path, "b", WS + 900, {2: (0.60, 0.41), 3: (0.12, 0.89)}, 100, 99),    # m2 no; Down 0.89 at m3, Down wins
        _round(tmp_path, "c", WS + 1800, {2: (0.82, 0.19), 3: (0.83, 0.18)}, 100, 99),   # Up 0.82, Down wins -> loss
        _round(tmp_path, "d", WS + 2700, {2: (0.97, 0.04), 3: (0.98, 0.03)}, 100, 101),  # too expensive -> skipped
        _round(tmp_path, "e", WS + 3600, {2: (0.84, 0.17)}),                             # triggered, not settled -> pending
    ]
    (tmp_path / "markets.json").write_text(json.dumps(mk))
    ledger, pending, skipped = score(tmp_path, WS)
    assert [(r["slug"], r["side"], r["minute"], r["won"]) for r in ledger] == [("a", "Up", 2, 1), ("b", "Down", 3, 1), ("c", "Up", 2, 0)]
    assert skipped == 1 and len(pending) == 1 and pending[0]["reason"] == "not settled yet"
    a = ledger[0]
    n = RULE["stake_usd"] / 0.85
    assert abs(a["pnl"] - (n - 100 - 0.0695 * 0.85 * 0.15 * n)) < 0.01
    assert ledger[2]["pnl"] < -100
    s = summarize(ledger, pending, skipped, WS)
    assert s["rounds_scored"] == 3 and s["wins"] == 2 and s["longest_losing_streak"] == 1


def test_pull_column(tmp_path):
    from scripts.early_favorite_tracker import pull_by_minute
    # 120 minutes of steadily rising candles -> every trend part says up -> +3 once the averages have warmed up
    cs = [{"timestamp": WS - 7200 + 60 * i, "open": 100 + i, "high": 100.5 + i, "low": 99.5 + i, "close": 100.2 + i} for i in range(120)]
    (tmp_path / "brti_1m.json").write_text(json.dumps(cs))
    pulls = pull_by_minute(tmp_path)
    assert pulls[WS - 60] == 3 and pulls[WS - 7200 + 60 * 119] == 3
    assert pull_by_minute(tmp_path / "nowhere") == {}
    # a round at WS whose check at minute 2 reads the candle starting at WS+60: Down favorite against an up pull -> -3
    cs += [{"timestamp": WS + 60 * i, "open": 220 + i, "high": 220.5 + i, "low": 219.5 + i, "close": 220.2 + i} for i in range(5)]
    (tmp_path / "brti_1m.json").write_text(json.dumps(cs))
    (tmp_path / "price_history").mkdir()
    mk = [_round(tmp_path, "a", WS, {2: (0.15, 0.86)}, 100, 99)]
    (tmp_path / "markets.json").write_text(json.dumps(mk))
    ledger, pending, skipped = score(tmp_path, WS)
    assert ledger[0]["side"] == "Down" and ledger[0]["pull"] == -3 and ledger[0]["won"] == 1
    s = summarize(ledger, pending, skipped, WS)
    assert [p["rounds"] for p in s["pull"]] == [0, 0, 1]


def test_cut_column(tmp_path):
    from scripts.early_favorite_tracker import CUT
    (tmp_path / "price_history").mkdir()
    mk = [
        # Up 0.85 at 2:00; at 10:00 elapsed the Down ask is 0.70 -> Up bid 0.30 < 0.45 -> cut; Up then loses at settlement
        _round(tmp_path, "a", WS, {2: (0.85, 0.16), 10: (0.31, 0.70)}, 100, 99),
        # Up 0.85; at 10:00 Up bid is 0.90 -> no cut; wins
        _round(tmp_path, "b", WS + 900, {2: (0.85, 0.16), 10: (0.91, 0.10)}, 100, 101),
        # Down 0.82; at 10:00 the Up ask is 0.60 -> Down bid 0.40 -> cut; Down then WINS (the cut gives the win away)
        _round(tmp_path, "c", WS + 1800, {2: (0.19, 0.82), 10: (0.60, 0.41)}, 100, 99),
        # Up 0.85, no 10:00 price stored -> column empty
        _round(tmp_path, "d", WS + 2700, {2: (0.85, 0.16)}, 100, 101),
    ]
    (tmp_path / "markets.json").write_text(json.dumps(mk))
    ledger, pending, skipped = score(tmp_path, WS)
    a, b, c, d = ledger
    assert a["cut"] == 1 and a["bid_at_cut"] == 0.30 and a["won"] == 0
    n = RULE["stake_usd"] / 0.85
    px = 0.30 - CUT["slippage"]
    exp = n * px - 100 - 0.0695 * 0.85 * 0.15 * n - 0.0695 * px * (1 - px) * n
    assert abs(a["pnl_cut"] - exp) < 0.01 and a["pnl_cut"] > a["pnl"]          # the cut saved most of the stake
    assert b["cut"] == 0 and b["pnl_cut"] == b["pnl"]                            # no cut -> identical to hold
    assert c["cut"] == 1 and c["won"] == 1 and c["pnl_cut"] < c["pnl"]            # cut a winner -> worse than hold
    assert d["bid_at_cut"] is None and d["cut"] == 0 and d["pnl_cut"] == d["pnl"]
    s = summarize(ledger, pending, skipped, WS)
    k = s["cut"]
    assert k["rounds_with_price"] == 3 and k["cuts"] == 2
    assert k["cuts_that_would_have_lost"] == 1 and k["cuts_that_would_have_won"] == 1
    assert abs(k["cut_minus_hold_usd"] - round((a["pnl_cut"] - a["pnl"]) + (c["pnl_cut"] - c["pnl"]), 2)) < 0.02
