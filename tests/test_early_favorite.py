"""Early Favorite forward tracker: rule triggers, settlement, pending, fee."""
import json

from scripts.early_favorite_tracker import RULE, score, summarize

WS = 1_792_600_000


def _round(tmp, slug, ws, prices, ptb=None, sp=None):
    hist = [{"timestamp": ws + 60 * m, "longPrice": ua, "shortPrice": da} for m, (ua, da) in prices.items()]
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
