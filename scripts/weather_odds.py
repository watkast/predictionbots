"""Real-world odds for Kalshi daily high-temperature markets, from the National Weather Service forecast.

For each KXHIGH* series we know the station city, fetch the NWS point forecast (api.weather.gov, free, no key),
take the forecast daytime high for each date, and turn it into a probability for each contract's temperature bracket
with a normal error model: the forecast is the centre, the spread is the typical error of an NWS high-temperature
forecast at that lead time (±2.5°F same day, ±3°F next day, ±4°F two days out, ±5°F beyond). That is a model, stated
on the page; the forecast itself is the National Weather Service's.

Used by scripts/market_pages.py: `probability(series_ticker, market) -> (p, detail) | None`.
"""
from __future__ import annotations

import math
import re
import sys
from datetime import date, datetime, timezone

LOG = lambda *a: print(*a, file=sys.stderr)

# series -> (city label, lat, lon) at or near the settlement station
STATIONS = {
    "KXHIGHAUS": ("Austin (AUS)", 30.18, -97.68), "KXHIGHCHI": ("Chicago (Midway)", 41.79, -87.75),
    "KXHIGHDEN": ("Denver (DEN)", 39.85, -104.66), "KXHIGHLAX": ("Los Angeles (LAX)", 33.94, -118.41),
    "KXHIGHMIA": ("Miami (MIA)", 25.79, -80.29), "KXHIGHNY": ("New York (Central Park)", 40.78, -73.97),
    "KXHIGHPHIL": ("Philadelphia (PHL)", 39.87, -75.23), "KXHIGHTATL": ("Atlanta (ATL)", 33.64, -84.43),
    "KXHIGHTBOS": ("Boston (BOS)", 42.36, -71.01), "KXHIGHTDAL": ("Dallas (DFW)", 32.90, -97.04),
    "KXHIGHTDC": ("Washington (DCA)", 38.85, -77.04), "KXHIGHTEWR": ("Newark (EWR)", 40.69, -74.17),
    "KXHIGHTHOU": ("Houston (Hobby)", 29.64, -95.28), "KXHIGHTLV": ("Las Vegas (LAS)", 36.08, -115.15),
    "KXHIGHTMIN": ("Minneapolis (MSP)", 44.88, -93.22), "KXHIGHTNOLA": ("New Orleans (MSY)", 29.99, -90.25),
    "KXHIGHTOKC": ("Oklahoma City (OKC)", 35.39, -97.60), "KXHIGHTPHX": ("Phoenix (PHX)", 33.43, -112.01),
    "KXHIGHTSAN": ("San Diego (SAN)", 32.73, -117.19), "KXHIGHTSATX": ("San Antonio (SAT)", 29.53, -98.47),
    "KXHIGHTSEA": ("Seattle (SEA)", 47.45, -122.31), "KXHIGHTSFO": ("San Francisco (SFO)", 37.62, -122.37),
    "KXHIGHTTTN": ("Trenton (TTN)", 40.28, -74.81),
}
SIGMA = {0: 2.5, 1: 3.0, 2: 4.0}
FORECASTS: dict[str, dict[str, int]] = {}      # series -> {YYYY-MM-DD: high °F}
MONTHS = {m: i for i, m in enumerate(["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"], 1)}


def phi(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def load(http, series: list[str]) -> None:
    """Fetch the NWS forecast once per station. `http` is market_pages.Http (paced, retries)."""
    for s in series:
        if s not in STATIONS or s in FORECASTS:
            continue
        _, lat, lon = STATIONS[s]
        pt = http.get(f"https://api.weather.gov/points/{lat},{lon}")
        url = (((pt or {}).get("properties") or {}).get("forecast"))
        if not url:
            LOG("nws: no forecast url for", s); continue
        fc = http.get(url)
        out = {}
        for per in (((fc or {}).get("properties") or {}).get("periods") or []):
            if per.get("isDaytime") and per.get("temperature") is not None and per.get("startTime"):
                t = per["temperature"]
                if per.get("temperatureUnit") == "C":
                    t = round(t * 9 / 5 + 32)
                out[per["startTime"][:10]] = int(t)
        FORECASTS[s] = out
    LOG(f"nws: forecasts for {sum(1 for s in series if FORECASTS.get(s))} of {sum(1 for s in series if s in STATIONS)} stations")


def market_date(m: dict) -> str | None:
    """Kalshi event tickers end in -26NOV08 (YYMONDD); fall back to the close time's date."""
    ev = m.get("event_ticker") or m.get("ticker") or ""
    mt = re.search(r"-(\d{2})([A-Z]{3})(\d{2})(?:-|$)", ev)
    if mt and mt.group(2) in MONTHS:
        return f"20{mt.group(1)}-{MONTHS[mt.group(2)]:02d}-{int(mt.group(3)):02d}"
    c = m.get("close_time") or ""
    return c[:10] or None


def probability(series: str, m: dict) -> tuple[float, str] | None:
    fc = FORECASTS.get(series)
    if not fc:
        return None
    d = market_date(m)
    if not d or d not in fc:
        return None
    hi = fc[d]
    lead = max(0, (date.fromisoformat(d) - datetime.now(timezone.utc).date()).days)
    sd = SIGMA.get(lead, 5.0)
    lo_s, hi_s, kind = m.get("floor_strike"), m.get("cap_strike"), (m.get("strike_type") or "").lower()
    try:
        lo = float(lo_s) if lo_s is not None else None
        up = float(hi_s) if hi_s is not None else None
    except (TypeError, ValueError):
        return None
    # Kalshi brackets are whole degrees: "between 60 and 61" means 60 <= high <= 61 -> continuity-corrected
    if kind in ("between",) and lo is not None and up is not None:
        p = phi((up + 0.5 - hi) / sd) - phi((lo - 0.5 - hi) / sd)
    elif kind in ("greater", "greater_or_equal") and lo is not None:
        p = 1 - phi((lo + (0.5 if kind == "greater" else -0.5) - hi) / sd)
    elif kind in ("less", "less_or_equal") and up is not None:
        p = phi((up - (0.5 if kind == "less" else -0.5) - hi) / sd)
    else:
        return None
    return max(0.0, min(1.0, p)), f"NWS forecast high {hi}°F for {d} at {STATIONS[series][0]}, typical error ±{sd:g}°F"


def selftest() -> None:
    FORECASTS["KXHIGHDEN"] = {"2026-11-09": 60}
    m = {"event_ticker": "KXHIGHDEN-26NOV09", "floor_strike": 60, "cap_strike": 61, "strike_type": "between"}
    p, why = probability("KXHIGHDEN", m)
    assert 0.2 < p < 0.35 and "60°F" in why, (p, why)
    g, _ = probability("KXHIGHDEN", {"event_ticker": "KXHIGHDEN-26NOV09", "floor_strike": 65, "strike_type": "greater"})
    assert g < 0.1
    assert market_date({"event_ticker": "KXHIGHNY-26DEC01"}) == "2026-12-01"
    print("selftest ok")


if __name__ == "__main__":
    selftest()
