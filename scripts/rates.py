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


UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) predictionbots-rates/1.0 (+https://predictionbots.io)", "Accept": "application/xml,text/xml,*/*"}


def fetch_tbill(client) -> tuple[float, str] | None:
    import datetime as _dt
    now = datetime.now(timezone.utc)
    months = [now.strftime("%Y%m"), (now.replace(day=1) - _dt.timedelta(days=1)).strftime("%Y%m")]
    for ym in months:
        url = TBILL_XML.format(ym=ym)
        r = client.get(url, timeout=30, headers=UA)
        print(f"tbill {ym}: HTTP {r.status_code}, {len(r.text)} bytes", file=sys.stderr)
        if r.status_code != 200:
            continue
        entries = re.findall(r"<entry>(.*?)</entry>", r.text, re.S | re.I)
        if not entries:
            print("tbill: no <entry> elements; head:", r.text[:300].replace("\n", " "), file=sys.stderr)
            continue
        names = sorted(set(re.findall(r"<d:([A-Za-z0-9_]+)", entries[-1])))
        print("tbill: fields:", ", ".join(names), file=sys.stderr)
        best = None
        for e in entries:
            d = re.search(r"<d:INDEX_DATE[^>]*>([^<]+)<", e)
            y = (re.search(r"<d:ROUND_B1_YIELD_4WK_COUPON_EQU[^>]*>([^<]+)<", e)
                 or re.search(r"<d:[A-Z0-9_]*4WK[A-Z0-9_]*(?:COUPON|CE|YIELD)[A-Z0-9_]*[^>]*>([^<]+)<", e)
                 or re.search(r"<d:[A-Z0-9_]*4WK[A-Z0-9_]*[^>]*>([^<]+)<", e))
            if d and y:
                try:
                    best = (float(y.group(1)) / 100, d.group(1)[:10])
                except ValueError:
                    pass
        if best:
            return best
    return None


def fetch_ibond(client) -> tuple[float, str] | None:
    r = client.get(IBOND_PAGE, timeout=30, headers=UA)
    print(f"ibond: HTTP {r.status_code}, {len(r.text)} bytes", file=sys.stderr)
    if r.status_code != 200:
        return None
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", r.text, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"\s+", " ", t)
    # TreasuryDirect phrasing varies: "Current Rate: 3.98%", "3.98% for I bonds issued November 1, 2025 to April 30, 2026"
    DATE = r"([A-Z][a-z]+ \d{1,2},? \d{4})"
    per = re.search(r"issued\s+" + DATE + r"\s*(?:through|to|-|\u2013)\s*" + DATE, t)
    period = f"{per.group(1)} to {per.group(2)}" if per else "current"
    m2 = re.search(r"(?:current (?:interest )?rate|composite rate)[^0-9%]{0,60}?([0-9]+\.[0-9]+)%", t, re.I)
    if m2:
        return float(m2.group(1)) / 100, period
    m = re.search(r"(?<!fixed rate of )([0-9]+\.[0-9]+)%\s*(?:composite)?[^%]{0,160}?issued\s+" + DATE, t)
    if m:
        return float(m.group(1)) / 100, period
    for mm in list(re.finditer(r"[0-9]+\.[0-9]+%", t))[:6]:
        print("ibond: no match; context:", t[max(0, mm.start() - 160): mm.end() + 80], file=sys.stderr)
    return None


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
