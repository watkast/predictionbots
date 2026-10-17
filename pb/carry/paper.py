"""Paper-signal ledger for the carry venture (no orders, ever).

``scripts/carry_paper.py`` (hourly on GitHub Actions) calls :func:`tick`:

1. poll the current funding rate of every source in ``configs/carry.yaml``
   (Coinbase US perp-style product, Bitnomial/Kraken-US, Binance, Bybit, OKX;
   all public endpoints, see pb/carry/venues.LIVE_FUNDING_SOURCES) and append
   to ``data/carry/funding-live.jsonl`` (one row per *new* funding interval);
2. for each paper entry (venue, asset) recompute the trailing-``lookback``
   annualized mean from the live log and apply the same entry/exit rules as
   :mod:`pb.carry.backtest` (enter > ``entry_ann``, exit < ``exit_ann`` or a
   negative print), accruing ``rate * notional`` per interval while "in";
3. append events to ``data/carry/paper-<venue>-<asset>.jsonl`` and keep the
   position state in ``data/carry/paper-state.json``.

Parsers are pure functions over the venues' JSON so tests need no network.
"""
from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

from pb.carry.venues import LIVE_FUNDING_SOURCES, annualize, venue_fees

log = logging.getLogger("pb.carry.paper")


# --------------------------------------------------------------------------- parsers (pure)


def _iso_ts(s: str | None) -> float | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def parse_coinbase_product(body: dict, interval_hours: float = 1.0) -> dict | None:
    """``GET /api/v3/brokerage/market/products/{id}`` -> {rate, interval_hours, interval_ts, mark}."""
    fpd = body.get("future_product_details") or {}
    pd_ = fpd.get("perpetual_details") or {}
    rate = fpd.get("funding_rate") or pd_.get("funding_rate")
    if rate in (None, ""):
        return None
    fi = fpd.get("funding_interval") or ""
    if isinstance(fi, str) and fi.endswith("s"):
        try:
            interval_hours = float(fi[:-1]) / 3600.0
        except ValueError:
            pass
    ft = _iso_ts(fpd.get("funding_time") or pd_.get("funding_time"))
    price = body.get("price") or body.get("mid_market_price")
    return {"rate": float(rate), "interval_hours": interval_hours, "interval_ts": ft,
            "mark": float(price) if price not in (None, "") else None, "product_id": body.get("product_id")}


def parse_bitnomial(body, interval_hours: float = 8.0) -> dict | None:
    data = body.get("funding_rates", body.get("data", body)) if isinstance(body, dict) else body
    if not data:
        return None
    row = max(data, key=lambda x: str(x.get("interval_end", "")))
    return {"rate": float(row["funding_rate"]), "interval_hours": interval_hours,
            "interval_ts": _iso_ts(row.get("interval_end")), "mark": _f(row.get("mark_price")),
            "product_id": row.get("product_id")}


def parse_binance(body, interval_hours: float = 8.0) -> dict | None:
    if not body:
        return None
    row = max(body, key=lambda x: int(x["fundingTime"]))
    return {"rate": float(row["fundingRate"]), "interval_hours": interval_hours,
            "interval_ts": int(row["fundingTime"]) / 1000, "mark": _f(row.get("markPrice")), "product_id": row.get("symbol")}


def parse_bybit(body, interval_hours: float = 8.0) -> dict | None:
    lst = (body.get("result") or {}).get("list") or []
    if not lst:
        return None
    row = max(lst, key=lambda x: int(x["fundingRateTimestamp"]))
    return {"rate": float(row["fundingRate"]), "interval_hours": interval_hours,
            "interval_ts": int(row["fundingRateTimestamp"]) / 1000, "mark": None, "product_id": row.get("symbol")}


def parse_okx(body, interval_hours: float = 8.0) -> dict | None:
    lst = body.get("data") or []
    if not lst:
        return None
    row = max(lst, key=lambda x: int(x["fundingTime"]))
    rate = row.get("realizedRate") or row.get("fundingRate")
    return {"rate": float(rate), "interval_hours": interval_hours,
            "interval_ts": int(row["fundingTime"]) / 1000, "mark": None, "product_id": row.get("instId")}


def _f(x):
    try:
        return float(x) if x not in (None, "") else None
    except (TypeError, ValueError):
        return None


PARSERS = {
    "coinbase_product": parse_coinbase_product,
    "bitnomial_funding": parse_bitnomial,
    "binance_funding": parse_binance,
    "bybit_funding": parse_bybit,
    "okx_funding": parse_okx,
}


# --------------------------------------------------------------------------- fetch (network)


def fetch_rate(source: str, asset: str, client: httpx.Client, cfg: dict | None = None) -> dict | None:
    sc = {**LIVE_FUNDING_SOURCES[source], **(cfg or {})}
    pid = sc["products"].get(asset.upper())
    kind = sc["kind"]
    if kind == "coinbase_product":
        if pid is None:
            from pb.carry.data import parse_coinbase_perp_products
            r = client.get(sc["list_url"])
            r.raise_for_status()
            pid = parse_coinbase_perp_products(r.json().get("products", [])).get(asset.upper())
            if pid is None:
                return None
        r = client.get(sc["url"].format(product_id=pid))
        r.raise_for_status()
        return parse_coinbase_product(r.json(), sc["interval_hours"])
    if pid is None:
        return None
    if kind == "bitnomial_funding":
        r = client.get(sc["url"], params={"base_symbol": pid, "limit": 3, "order": "desc"})
    elif kind == "binance_funding":
        r = client.get(sc["url"], params={"symbol": pid, "limit": 3})
    elif kind == "bybit_funding":
        r = client.get(sc["url"], params={"category": "linear", "symbol": pid, "limit": 3})
    elif kind == "okx_funding":
        r = client.get(sc["url"], params={"instId": pid, "limit": 3})
    else:
        raise ValueError(kind)
    r.raise_for_status()
    return PARSERS[kind](r.json(), sc["interval_hours"])


# --------------------------------------------------------------------------- ledger / state


def _append(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def load_state(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=1, sort_keys=True))


def record_live(live_log: Path, source: str, asset: str, obs: dict, now: float) -> bool:
    """Append an observation if its funding interval is new for (source, asset). Returns True if new."""
    key_ts = obs.get("interval_ts") or now
    rows = [r for r in _read_jsonl(live_log) if r.get("source") == source and r.get("asset") == asset]
    if rows and any(abs(r.get("interval_ts", 0) - key_ts) < 1 for r in rows[-50:]):
        return False
    _append(live_log, {"ts": now, "source": source, "asset": asset, "rate": obs["rate"],
                       "interval_hours": obs["interval_hours"], "interval_ts": key_ts,
                       "ann": annualize(obs["rate"], obs["interval_hours"]), "mark": obs.get("mark"),
                       "product_id": obs.get("product_id")})
    return True


def trailing_signal(live_log: Path, source: str, asset: str, lookback: int) -> tuple[float | None, list[dict]]:
    rows = [r for r in _read_jsonl(live_log) if r.get("source") == source and r.get("asset") == asset]
    rows.sort(key=lambda r: r.get("interval_ts", 0))
    last = rows[-lookback:]
    if len(last) < lookback:
        return None, last
    return sum(r["ann"] for r in last) / lookback, last


def step_entry(state: dict, entry_cfg: dict, signal: float | None, latest: dict | None, now: float,
               ledger: Path) -> dict:
    """Apply entry/exit rules to one paper entry; mutates and returns its state."""
    name = entry_cfg["name"]
    st = state.setdefault(name, {"in_pos": False, "notional": float(entry_cfg.get("notional", 1000.0)),
                                 "funding": 0.0, "fees": 0.0, "intervals": 0, "trades": 0,
                                 "last_interval_ts": None, "realized": 0.0})
    fees = venue_fees(entry_cfg["fee_venue"], entry_cfg["asset"])
    N = st["notional"]
    mark = (latest or {}).get("mark") or 0.0
    ev = {"ts": now, "type": "tick", "signal": signal, "rate": (latest or {}).get("rate"),
          "interval_ts": (latest or {}).get("interval_ts"), "in_pos": st["in_pos"], "mark": mark}
    _append(ledger, ev)
    if latest is None or signal is None:
        return st
    new_interval = st["last_interval_ts"] != latest.get("interval_ts")
    if st["in_pos"] and new_interval:
        acc = latest["rate"] * N
        st["funding"] += acc
        st["intervals"] += 1
        _append(ledger, {"ts": now, "type": "funding", "amount": acc, "rate": latest["rate"], "notional": N})
    st["last_interval_ts"] = latest.get("interval_ts")
    if st["in_pos"]:
        if signal < entry_cfg["exit_ann"] or (entry_cfg.get("exit_on_negative_print", True) and latest["rate"] < 0):
            cost = fees.spot.cost(N, mark or 1.0, False) + fees.perp.cost(N, mark or 1.0, False) \
                + 2 * N * entry_cfg.get("slippage_bps", 2.0) / 1e4
            st["fees"] += cost
            st["realized"] += st["funding"] - cost
            _append(ledger, {"ts": now, "type": "exit", "signal": signal, "rate": latest["rate"], "cost": cost,
                             "funding_in_trade": st["funding"], "intervals": st["intervals"], "mark": mark,
                             "reason": "signal_below_exit" if signal < entry_cfg["exit_ann"] else "negative_print"})
            st.update(in_pos=False, funding=0.0, intervals=0)
    else:
        if signal > entry_cfg["entry_ann"]:
            cost = fees.spot.cost(N, mark or 1.0, False) + fees.perp.cost(N, mark or 1.0, False) \
                + 2 * N * entry_cfg.get("slippage_bps", 2.0) / 1e4
            st["fees"] += cost
            st["realized"] -= cost
            st["trades"] += 1
            st.update(in_pos=True, funding=0.0, intervals=0, entry_ts=now, entry_mark=mark)
            _append(ledger, {"ts": now, "type": "enter", "signal": signal, "rate": latest["rate"], "cost": cost,
                             "notional": N, "mark": mark})
    return st


def tick(cfg: dict, data_dir: Path, client: httpx.Client | None = None, now: float | None = None,
         fetch=fetch_rate) -> dict:
    """One paper tick. ``fetch(source, asset, client, cfg) -> obs | None`` is injectable for tests."""
    now = now or time.time()
    data_dir = Path(data_dir)
    live_log = data_dir / "funding-live.jsonl"
    state_path = data_dir / "paper-state.json"
    state = load_state(state_path)
    own = client is None
    client = client or httpx.Client(timeout=30, headers={"User-Agent": "predictionbots-carry/0.1"})
    pcfg = cfg.get("paper", {})
    sources: dict = pcfg.get("sources", {s: {} for s in LIVE_FUNDING_SOURCES})
    assets = [a.upper() for a in cfg.get("assets", ["BTC", "ETH"])]
    observed: dict[tuple[str, str], dict] = {}
    errors: dict[str, str] = {}
    try:
        for src, scfg in sources.items():
            for a in assets:
                try:
                    obs = fetch(src, a, client, scfg)
                except Exception as e:  # noqa: BLE001
                    errors[f"{src}/{a}"] = repr(e)
                    log.warning("fetch %s %s: %s", src, a, e)
                    continue
                if obs is None:
                    continue
                observed[(src, a)] = obs
                record_live(live_log, src, a, obs, now)
    finally:
        if own:
            client.close()
    results = {}
    for e in pcfg.get("entries", []):
        src, a = e["source"], e["asset"].upper()
        sig, rows = trailing_signal(live_log, src, a, int(e.get("lookback", 3)))
        latest = observed.get((src, a)) or (rows[-1] if rows else None)
        if latest is not None and "interval_ts" not in latest:
            latest = {**latest, "interval_ts": now}
        st = step_entry(state, e, sig, latest, now, data_dir / f"paper-{e['name']}.jsonl")
        results[e["name"]] = {"signal": sig, "in_pos": st["in_pos"], "realized": st["realized"],
                              "funding_open": st["funding"], "trades": st["trades"]}
    state["_meta"] = {"updated_at": now, "errors": errors}
    save_state(state_path, state)
    return {"observed": {f"{k[0]}/{k[1]}": v for k, v in observed.items()}, "entries": results, "errors": errors}


def summarize(data_dir: Path) -> dict:
    """Roll the paper ledgers up for reports/carry_paper.md."""
    data_dir = Path(data_dir)
    out = {}
    for p in sorted(data_dir.glob("paper-*.jsonl")):
        rows = _read_jsonl(p)
        name = p.stem[len("paper-"):]
        enters = [r for r in rows if r["type"] == "enter"]
        exits = [r for r in rows if r["type"] == "exit"]
        funding = sum(r["amount"] for r in rows if r["type"] == "funding")
        costs = sum(r["cost"] for r in rows if r["type"] in ("enter", "exit"))
        ticks = [r for r in rows if r["type"] == "tick"]
        out[name] = {"ticks": len(ticks), "enters": len(enters), "exits": len(exits), "funding": funding,
                     "costs": costs, "net": funding - costs,
                     "first_ts": ticks[0]["ts"] if ticks else None, "last_ts": ticks[-1]["ts"] if ticks else None,
                     "in_pos_frac": (sum(1 for t in ticks if t.get("in_pos")) / len(ticks)) if ticks else 0.0,
                     "last_signal": ticks[-1].get("signal") if ticks else None}
    return out
