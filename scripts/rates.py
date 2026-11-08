"""Risk-free reference rates for the "Same money, elsewhere" card, from official sources only.

  4-week Treasury bill: the Treasury's daily bill-rate XML feed (coupon-equivalent yield, latest business day).
  Series I savings bond: the current composite rate from TreasuryDirect's I-bond page.

Writes site/data/rates.json; keeps the previous value for any rate it cannot fetch, so the card never shows a
number without a date and a source. Run by the site-deploy workflow before the build; safe to run offline.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "site" / "data" / "rates.json"
TBILL_XML = "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml?data=daily_treasury_bill_rates&field_tdr_date_value_month={ym}"
IBOND_PAGE = "https://www.treasurydirect.gov/savings-bonds/i-bonds/"


def load() -> dict:
    try:
        return json.loads(OUT.read_text())
    except Exception:
        return {"asof": None, "tbill_4w": None, "tbill_4w_date": None, "ibond": None, "ibond_period": None,
                "sources": {"tbill_4w": "U.S. Treasury, daily Treasury bill rates (coupon equivalent)",
                            "ibond": "TreasuryDirect, Series I savings bonds, current composite rate"}}


def fetch_tbill(client) -> tuple[float, str] | None:
    now = datetime.now(timezone.utc)
    for ym in (now.strftime("%Y%m"), (now.replace(day=1) - __import__("datetime").timedelta(days=1)).strftime("%Y%m")):
        r = client.get(TBILL_XML.format(ym=ym), timeout=30)
        if r.status_code != 200:
            continue
        entries = re.findall(r"<entry>(.*?)</entry>", r.text, re.S)
        best = None
        for e in entries:
            d = re.search(r"<d:INDEX_DATE[^>]*>([^<]+)<", e)
            y = re.search(r"<d:ROUND_B1_YIELD_4WK_COUPON_EQU[^>]*>([^<]+)<", e)
            if d and y:
                try:
                    best = (float(y.group(1)) / 100, d.group(1)[:10])
                except ValueError:
                    pass
        if best:
            return best
    return None


def fetch_ibond(client) -> tuple[float, str] | None:
    r = client.get(IBOND_PAGE, timeout=30, headers={"User-Agent": "predictionbots-rates/1.0"})
    if r.status_code != 200:
        return None
    t = re.sub(r"<[^>]+>", " ", r.text)
    m = re.search(r"([0-9]+\.[0-9]+)%\s*(?:composite|current rate|for I bonds)[^.]{0,80}?(?:issued|from)\s+([A-Z][a-z]+ \d{4})\s*(?:through|to|-|–)\s*([A-Z][a-z]+ \d{4})", t)
    if not m:
        m2 = re.search(r"(?:composite rate|current rate)[^0-9]{0,40}([0-9]+\.[0-9]+)%", t, re.I)
        return (float(m2.group(1)) / 100, "current") if m2 else None
    return float(m.group(1)) / 100, f"{m.group(2)} to {m.group(3)}"


def main() -> None:
    data = load()
    try:
        import httpx
        with httpx.Client(follow_redirects=True) as c:
            tb = fetch_tbill(c)
            if tb:
                data["tbill_4w"], data["tbill_4w_date"] = tb
                print("tbill 4w", tb, file=sys.stderr)
            else:
                print("tbill: not fetched, keeping previous", file=sys.stderr)
            ib = fetch_ibond(c)
            if ib:
                data["ibond"], data["ibond_period"] = ib
                print("ibond", ib, file=sys.stderr)
            else:
                print("ibond: not fetched, keeping previous", file=sys.stderr)
    except Exception as e:
        print("rates: offline or failed:", repr(e), file=sys.stderr)
    data["asof"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=1))
    print(json.dumps(data))


if __name__ == "__main__":
    main()
