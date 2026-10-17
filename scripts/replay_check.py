#!/usr/bin/env python
"""Replay a paper run's recorded data through the engine, with and without the
RiskManager, and print the delta against the live ledger. One command per audit.

    python scripts/replay_check.py --run-id mm_crypto_twap_kxbtc15m-20261016T2316
    python scripts/replay_check.py --run-id <id> --ledger data/ledger --data data/recorded --latency 0.3
    python scripts/replay_check.py --run-id <id> --strategy mm_crypto_twap --params configs/mm_crypto_twap.yaml \
        --markets KXBTC15M-26OCT161930-30 --json

What it does
------------
1. Reads `<ledger>/<run_id>.summary.json` for the strategy, the markets it
   traded (`markets`), the time span (`started_at`..`updated_at`) and the live
   numbers (net pnl, fills, risk counters).
2. Finds the matrix entry (`configs/paper_matrix.yaml`, by run group) for the
   params file, `--set` overrides and risk limits, unless given on the CLI.
3. Loads the recorded parquet (`pb.data.loaders.load_recorded`) for those
   markets, sliced to the run's span (+ settlements after it).
4. Runs the strategy twice through `pb.sim.engine.Engine` with the same
   `SimConfig` the paper runner used: once bare, once behind a `RiskManager`
   whose clock is the engine clock (so the daily-loss, rate and capital gates
   behave as they did live).
5. Prints a three-column table (live ledger / replay no-risk / replay risk)
   and the deltas. Exit code 0; `--json` prints the dict instead.

If the live number sits far from BOTH replays, the live run saw something the
recording does not contain (feed gaps, timing) or ran different code; if the
no-risk replay is wild and the risk replay is tame, the risk gate was doing the
strategy's job (that was the 2026-10-16 mm_crypto_twap case).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _load_summary(ledger: Path, run_id: str) -> dict:
    p = ledger / f"{run_id}.summary.json"
    if not p.exists():
        raise SystemExit(f"no summary at {p}")
    return json.loads(p.read_text())


def matrix_entry_for(run_id: str, matrix_path: Path) -> dict | None:
    """The paper_matrix entry whose name is the run group of `run_id`."""
    from scripts.paper_matrix import load_matrix
    from scripts.report import run_group

    if not matrix_path.exists():
        return None
    grp = run_group(run_id)
    for r in load_matrix(matrix_path)["runs"]:
        if r.get("name") == grp:
            return r
    return None


def replay(strategy: str, params: dict, markets: list[str], data: str, t0: float | None, t1: float | None,
           sim_kwargs: dict, risk_limits=None, signals: bool = True) -> dict:
    """Run once. `risk_limits=None` -> bare engine; else a RiskManager on the
    engine clock gates every order. Returns summary + reality + risk status."""
    from pb.live.paper import build_strategy
    from pb.live.risk import RiskManager
    from pb.sim.backtest import _slice, default_fee_for, reality_flags
    from pb.sim.engine import Engine, Result, SimConfig
    from pb.data.loaders import load_recorded

    mkts, events = load_recorded(data, markets or None, signals=signals)
    events = list(events)
    if t0 is not None or t1 is not None:
        lo = t0 if t0 is not None else min((e.ts for e in events), default=0.0)
        hi = t1 if t1 is not None else max((e.ts for e in events), default=0.0) + 1.0
        events = _slice(events, (lo, hi))
    eng = Engine(mkts, default_fee_for(mkts), SimConfig(**sim_kwargs))
    rm = None
    if risk_limits is not None:
        rm = RiskManager(eng, risk_limits, clock=lambda: eng.now, name="replay").install()
    strat = build_strategy(strategy, dict(params), [m.market_id for m in mkts] or None)
    eng.add_strategy(strat)
    res = eng.run(iter(events))
    s = Result(eng).summary()
    s["reality"] = reality_flags(eng)
    s["events"] = len(events)
    s["per_market"] = {m: round(p.realized - p.fees, 4) for m, p in eng.positions.items()}
    s["risk"] = rm.status() if rm is not None else None
    return s


def _row(label: str, s: dict) -> dict:
    r = s.get("reality") or {}
    k = s.get("risk") or {}
    return {
        "source": label,
        "net_pnl": round(float(s.get("net_pnl", 0.0)), 2),
        "fills": int(s.get("fills", 0)),
        "contracts": round(float(s.get("contracts_traded", 0.0)), 1),
        "max_cap": round(float(s.get("max_capital_at_risk", 0.0)), 2),
        "cross_assumed": r.get("cross_assumed_fill_frac", 0.0),
        "max_fill_touch": r.get("max_fill_to_touch_depth", 0.0),
        "risk_accepted": k.get("accepted", "-") if k else "-",
        "risk_rejected": k.get("rejected", "-") if k else "-",
        "halted": (k.get("halt_reason") or "") if k else "-",
    }


def render(rows: list[dict]) -> str:
    cols = ["source", "net_pnl", "fills", "contracts", "max_cap", "cross_assumed", "max_fill_touch",
            "risk_accepted", "risk_rejected", "halted"]
    widths = {c: max(len(c), *(len(str(r[c])) for r in rows)) for c in cols}
    out = [" | ".join(c.ljust(widths[c]) for c in cols), "-+-".join("-" * widths[c] for c in cols)]
    for r in rows:
        out.append(" | ".join(str(r[c]).ljust(widths[c]) for c in cols))
    live, bare, risk = rows[0], rows[1], rows[2]
    out += ["",
            f"delta net pnl: replay(no risk) - live = {bare['net_pnl'] - live['net_pnl']:+.2f}; "
            f"replay(risk) - live = {risk['net_pnl'] - live['net_pnl']:+.2f}; "
            f"risk - no risk = {risk['net_pnl'] - bare['net_pnl']:+.2f}",
            f"delta fills:   replay(no risk) - live = {bare['fills'] - live['fills']:+d}; "
            f"replay(risk) - live = {risk['fills'] - live['fills']:+d}"]
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--ledger", default=str(ROOT / "data/ledger"))
    ap.add_argument("--data", default=str(ROOT / "data/recorded"), help="recorded parquet dir or glob")
    ap.add_argument("--matrix", default=str(ROOT / "configs/paper_matrix.yaml"))
    ap.add_argument("--strategy", help="default: from the summary")
    ap.add_argument("--params", help="YAML params file (default: the matrix entry's)")
    ap.add_argument("--markets", nargs="*", help="default: the summary's markets")
    ap.add_argument("--start", type=float, help="epoch; default: summary started_at")
    ap.add_argument("--end", type=float, help="epoch; default: summary updated_at")
    ap.add_argument("--whole-recording", action="store_true", help="do not slice to the run's span")
    ap.add_argument("--latency", type=float, default=0.3)
    ap.add_argument("--max-position", type=float, default=None)
    ap.add_argument("--daily-loss-limit", type=float, default=None)
    ap.add_argument("--max-capital", type=float, default=None)
    ap.add_argument("--max-capital-per-market", type=float, default=None)
    ap.add_argument("--max-orders-per-min", type=int, default=120)
    ap.add_argument("--no-recorded-signals", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    from pb.live.paper import load_params_yaml
    from pb.live.risk import RiskLimits

    summary = _load_summary(Path(a.ledger), a.run_id)
    entry = matrix_entry_for(a.run_id, Path(a.matrix)) or {}
    from scripts.paper_matrix import load_matrix
    defaults = load_matrix(Path(a.matrix))["defaults"] if Path(a.matrix).exists() else {}
    strategy = a.strategy or ",".join(summary.get("strategies") or []) or entry.get("strategy")
    if not strategy:
        raise SystemExit("cannot infer the strategy; pass --strategy")
    params_file = a.params or entry.get("params")
    params = load_params_yaml(str(ROOT / params_file) if params_file and not Path(params_file).exists()
                              else params_file, strategy)
    for k, v in (entry.get("params_override") or {}).items():
        params[k] = v
    markets = a.markets if a.markets else list(summary.get("markets") or [])
    t0 = None if a.whole_recording else (a.start if a.start is not None else summary.get("started_at"))
    t1 = None if a.whole_recording else (a.end if a.end is not None else summary.get("updated_at"))

    def lim(name: str, cli, key: str, fallback):
        return cli if cli is not None else float(entry.get(key, defaults.get(key, fallback)))

    sim = {"order_latency": a.latency, "cancel_latency": a.latency,
           "max_position_per_market": lim("max_position", a.max_position, "max_position", 200.0)}
    limits = RiskLimits(daily_loss_limit=lim("dll", a.daily_loss_limit, "daily_loss_limit", 50.0),
                        max_capital_total=lim("mc", a.max_capital, "max_capital", 2000.0),
                        max_capital_per_market=lim("mcm", a.max_capital_per_market, "max_capital_per_market", 500.0),
                        max_orders_per_min=a.max_orders_per_min, stale_secs=1e12,
                        kill_file=str(ROOT / "data" / "KILL.replay-never"))
    bare = replay(strategy, params, markets, a.data, t0, t1, sim, None, signals=not a.no_recorded_signals)
    risk = replay(strategy, params, markets, a.data, t0, t1, sim, limits, signals=not a.no_recorded_signals)
    rows = [_row("live ledger", summary), _row("replay no-risk", bare), _row("replay risk", risk)]
    result = {"run_id": a.run_id, "strategy": strategy, "markets": markets, "params": params,
              "span": [t0, t1], "events": bare["events"], "rows": rows,
              "delta_no_risk_minus_live": round(rows[1]["net_pnl"] - rows[0]["net_pnl"], 2),
              "delta_risk_minus_live": round(rows[2]["net_pnl"] - rows[0]["net_pnl"], 2),
              "delta_risk_minus_no_risk": round(rows[2]["net_pnl"] - rows[1]["net_pnl"], 2),
              "per_market_no_risk": bare["per_market"], "per_market_risk": risk["per_market"]}
    if a.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print(f"replay_check {a.run_id}: {strategy} on {markets or 'all recorded markets'}, "
              f"{bare['events']} events, latency {a.latency}s")
        print(render(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
