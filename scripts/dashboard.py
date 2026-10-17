#!/usr/bin/env python
"""Build reports/dashboard.html — one self-contained page showing every venture,
every paper run, the equity curve per run, and the reality flags. It reads the
same inputs as scripts/report.py plus configs/ventures.yaml, so it cannot say
anything the ledgers do not.

    python scripts/dashboard.py [--ledger data/ledger] [--out reports/dashboard.html]
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.report import (load_paper, load_paper_voided, load_voided, paper_leaderboard,  # noqa: E402
                            run_group, _realized_by_day)

TRUST_RULES = [
    ("cross-assumed", "fills inferred from book crossing, no prints"),
    ("fill>touch", "fill bigger than resting size"),
    ("top3", "pnl concentrated in <=3 markets"),
    ("HALTED", "risk manager halted"),
    ("risk-rejected", "most orders rejected by risk"),
]


def trust(row: dict) -> tuple[int, list[str]]:
    """0-100 trust score for a paper row: starts at 100, loses points per flag,
    per missing days, per zero fills."""
    score, why = 100, []
    flags = row.get("flags", "") or ""
    for key, desc in TRUST_RULES:
        if key in flags:
            score -= 30 if key in ("cross-assumed", "fill>touch") else 15
            why.append(desc)
    if row.get("days", 0) < 3:
        score -= 20
        why.append(f"only {row.get('days', 0)} run-day(s)")
    if row.get("fills", 0) == 0:
        score -= 25
        why.append("no fills")
    if row.get("maker_pct", 0) < 90 and row.get("strategy", "").startswith(("mm_", "favorite", "endgame", "sharp")):
        score -= 15
        why.append("maker model taking liquidity")
    return max(0, score), why


def verdict_for(row: dict) -> str:
    t, _ = trust(row)
    if row.get("fills", 0) == 0:
        return "no data"
    if t < 50:
        return "artifact?" if row["net_pnl"] > 0 else "untrusted"
    if row["net_pnl"] > 0:
        return "promising" if row.get("days", 0) >= 3 else "early +"
    return "losing"


def load_equity(csv_path: Path) -> dict[str, list[tuple[str, float]]]:
    out: dict[str, list[tuple[str, float]]] = defaultdict(list)
    if not csv_path.exists():
        return out
    with csv_path.open() as f:
        for r in csv.DictReader(f):
            out[r["run"]].append((r["day"], float(r["cum_net_pnl"])))
    return out


def fmt(v, nd=2):
    try:
        return f"{float(v):,.{nd}f}"
    except Exception:
        return str(v)


def svg_curve(points: list[tuple[str, float]], w=220, h=48) -> str:
    if len(points) < 2:
        return ""
    ys = [p[1] for p in points]
    lo, hi = min(ys + [0.0]), max(ys + [0.0])
    rng = (hi - lo) or 1.0
    xs = [i * (w - 4) / (len(points) - 1) + 2 for i in range(len(points))]
    pts = " ".join(f"{x:.1f},{h - 2 - (y - lo) / rng * (h - 4):.1f}" for x, y in zip(xs, ys))
    zero = h - 2 - (0 - lo) / rng * (h - 4)
    color = "var(--good)" if ys[-1] >= 0 else "var(--critical)"
    return (f'<svg class="spark" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="cumulative pnl">'
            f'<line x1="0" x2="{w}" y1="{zero:.1f}" y2="{zero:.1f}" class="zero"/>'
            f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2" stroke-linejoin="round"/></svg>')


def build(ledger: Path, ventures_yaml: Path, equity_csv: Path, voided_yaml: Path | None = None) -> str:
    voided = load_voided(voided_yaml)
    summaries, fills = load_paper(ledger, voided)
    rows = paper_leaderboard(summaries, fills)
    vrows = load_paper_voided(ledger, voided)
    eq = load_equity(equity_csv)
    ventures = yaml.safe_load(ventures_yaml.read_text()).get("ventures", []) if ventures_yaml.exists() else []

    total_net = sum(r["net_pnl"] for r in rows)
    total_cap = sum(r["max_cap"] for r in rows)
    trusted_net = sum(r["net_pnl"] for r in rows if trust(r)[0] >= 50)
    n_runs = len(rows)
    n_pos = sum(1 for r in rows if r["net_pnl"] > 0 and trust(r)[0] >= 50)
    live_capital = sum(float(v.get("capital_usd", 0) or 0) for v in ventures)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    def esc(s):
        return html.escape(str(s))

    run_rows = []
    for r in rows:
        t, why = trust(r)
        v = verdict_for(r)
        cls = {"promising": "good", "early +": "warn", "losing": "critical", "artifact?": "serious",
               "untrusted": "serious", "no data": "muted"}[v]
        run_rows.append(
            f"<tr><td class='name'>{esc(r['run'])}<div class='sub'>{esc(r['strategy'])} · {esc(r['venue'])}</div></td>"
            f"<td class='num {'pos' if r['net_pnl'] > 0 else 'neg' if r['net_pnl'] < 0 else ''}'>{fmt(r['net_pnl'])}</td>"
            f"<td class='num'>{fmt(r['max_cap'])}</td>"
            f"<td class='num'>{fmt(r['ret_pct'], 1) if 'ret_pct' in r else fmt(100 * r['net_pnl'] / r['max_cap'] if r['max_cap'] else 0, 1)}%</td>"
            f"<td class='num'>{r['fills']}</td><td class='num'>{fmt(r['maker_pct'], 0)}%</td>"
            f"<td class='num'>{r['days']}d / {r['hours']}h</td>"
            f"<td>{svg_curve(eq.get(r['run'], []))}</td>"
            f"<td><span class='pill {cls}'>{esc(v)}</span><div class='trust'>trust {t}/100</div>"
            f"<div class='why'>{esc('; '.join(why)) if why else 'no flags'}</div></td></tr>")

    vrows_html = []
    for v in ventures:
        vc = {"edge": "good", "promising": "warn", "unproven": "muted", "artifact": "serious", "losing": "critical"}.get(v.get("verdict", "unproven"), "muted")
        vrows_html.append(
            f"<div class='card'><div class='card-head'><span class='pill {vc}'>{esc(v.get('verdict', ''))}</span>"
            f"<span class='status'>{esc(v.get('status', ''))}</span><span class='cap'>${fmt(v.get('capital_usd', 0), 0)} at risk</span></div>"
            f"<h3>{esc(v.get('name', v.get('id')))}</h3><div class='market'>{esc(v.get('market', ''))}</div>"
            f"<dl><dt>Evidence</dt><dd>{esc(v.get('evidence', ''))}</dd>"
            f"<dt>Risk</dt><dd>{esc(v.get('risk', ''))}</dd><dt>Next</dt><dd>{esc(v.get('next', ''))}</dd></dl></div>")

    void_rows = "".join(
        f"<tr><td class='name'>{esc(v['run_id'])}<div class='sub'>{esc(v['strategy'])}</div></td>"
        f"<td class='num {'pos' if v['net_pnl'] > 0 else 'neg' if v['net_pnl'] < 0 else ''}'>{fmt(v['net_pnl'])}</td>"
        f"<td class='num'>{v['fills']}</td><td>{esc(v['day'])}</td><td class='why'>{esc(v['reason'])}</td></tr>"
        for v in vrows)
    voided_html = ("" if not vrows else
                   f"<h2>Voided runs</h2><div class='sub' style='margin-bottom:8px'>Excluded from every total above "
                   f"(reports/voided.yaml); kept visible so nothing disappears silently.</div>"
                   f"<div class='wrap'><table><thead><tr><th>Run</th><th class='num'>Net $</th><th class='num'>Fills</th>"
                   f"<th>Day</th><th>Reason</th></tr></thead><tbody>{void_rows}</tbody></table></div>")

    tiles = [
        ("Real money deployed", f"${fmt(live_capital, 0)}", "none yet — every number below is paper"),
        ("Paper net P&L (all runs)", f"${fmt(total_net)}", f"on ${fmt(total_cap, 0)} peak collateral"),
        ("Paper net P&L (trusted runs only)", f"${fmt(trusted_net)}", "runs with trust ≥ 50"),
        ("Runs positive & trusted", f"{n_pos} / {n_runs}", "need ≥3 clean days to count"),
    ]
    tiles_html = "".join(f"<div class='tile'><div class='label'>{esc(a)}</div><div class='value'>{esc(b)}</div><div class='sub'>{esc(c)}</div></div>" for a, b, c in tiles)

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Bot Ventures Board</title>
<style>
:root{{--surface:#fcfcfb;--page:#f9f9f7;--ink:#0b0b0b;--ink2:#52514e;--muted:#898781;--grid:#e1e0d9;--border:rgba(11,11,11,.10);
--good:#0ca30c;--warning:#fab219;--serious:#ec835a;--critical:#d03b3b;--s1:#2a78d6;--goodtext:#006300}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--surface:#1a1a19;--page:#0d0d0d;--ink:#f0efec;--ink2:#c3c2b7;--muted:#898781;--grid:#2c2c2a;--border:rgba(255,255,255,.10);--s1:#3987e5;--goodtext:#0ca30c}}}}
:root[data-theme="dark"]{{--surface:#1a1a19;--page:#0d0d0d;--ink:#f0efec;--ink2:#c3c2b7;--muted:#898781;--grid:#2c2c2a;--border:rgba(255,255,255,.10);--s1:#3987e5;--goodtext:#0ca30c}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--page);color:var(--ink);font:15px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif;padding:16px}}
main{{max-width:1180px;margin:0 auto}}h1{{font-size:22px;margin:0 0 4px}}.meta{{color:var(--muted);font-size:13px;margin-bottom:18px}}
.tiles{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin-bottom:24px}}
.tile{{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:14px}}.tile .label{{font-size:12px;color:var(--ink2);text-transform:uppercase;letter-spacing:.04em}}
.tile .value{{font-size:28px;font-weight:600;margin:4px 0}}.tile .sub{{font-size:12px;color:var(--muted)}}
h2{{font-size:17px;margin:26px 0 10px}}
table{{width:100%;border-collapse:collapse;background:var(--surface);border:1px solid var(--border);border-radius:10px;overflow:hidden;font-size:13px}}
th,td{{padding:9px 10px;border-bottom:1px solid var(--grid);vertical-align:top;text-align:left}}th{{color:var(--ink2);font-weight:500;font-size:12px}}
td.num,th.num{{text-align:right;font-variant-numeric:tabular-nums}}.pos{{color:var(--goodtext)}}.neg{{color:var(--critical)}}
.name{{font-weight:600}}.sub{{font-weight:400;color:var(--muted);font-size:12px}}
.pill{{display:inline-block;padding:2px 8px;border-radius:999px;font-size:12px;font-weight:600;border:1px solid var(--border)}}
.pill.good{{color:var(--goodtext)}}.pill.warn{{color:#8a5a00}}.pill.serious{{color:#a3401e}}.pill.critical{{color:var(--critical)}}.pill.muted{{color:var(--muted)}}
:root[data-theme="dark"] .pill.warn,:root:not([data-theme="light"]) .pill.warn{{color:var(--warning)}}
.trust{{font-size:12px;color:var(--ink2);margin-top:4px}}.why{{font-size:11px;color:var(--muted);max-width:220px}}
.spark .zero{{stroke:var(--grid);stroke-width:1}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px}}
.card{{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:14px}}.card h3{{font-size:15px;margin:8px 0 2px}}
.card-head{{display:flex;gap:8px;align-items:center;font-size:12px;color:var(--ink2)}}.card .cap{{margin-left:auto}}.card .market{{font-size:12px;color:var(--muted)}}
dl{{margin:10px 0 0;font-size:13px}}dt{{color:var(--ink2);font-size:11px;text-transform:uppercase;letter-spacing:.04em;margin-top:8px}}dd{{margin:2px 0 0}}
.wrap{{overflow-x:auto}}.note{{background:var(--surface);border-left:3px solid var(--serious);padding:10px 12px;border-radius:6px;font-size:13px;color:var(--ink2);margin:0 0 18px}}
</style></head><body><main>
<h1>Bot Ventures Board</h1><div class="meta">Generated {now} from the paper ledgers in the repo. Nothing here is edited by hand.</div>
<div class="note"><b>How to read this.</b> Every P&amp;L is simulated against live order books with no invented liquidity. A run earns trust only after ≥3 clean days, no reality flags, and P&amp;L spread across markets. A big green number with low trust is a bug until proven otherwise.</div>
<div class="tiles">{tiles_html}</div>
<h2>Paper runs</h2><div class="wrap"><table><thead><tr><th>Run</th><th class="num">Net $</th><th class="num">Peak cap $</th><th class="num">Return</th><th class="num">Fills</th><th class="num">Maker</th><th class="num">Time</th><th>Cum. P&amp;L by day</th><th>Verdict</th></tr></thead>
<tbody>{''.join(run_rows) or '<tr><td colspan=9>No paper runs yet.</td></tr>'}</tbody></table></div>
{voided_html}
<h2>Ventures</h2><div class="cards">{''.join(vrows_html)}</div>
</main></body></html>"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", default=str(ROOT / "data/ledger"))
    ap.add_argument("--ventures", default=str(ROOT / "configs/ventures.yaml"))
    ap.add_argument("--equity", default=str(ROOT / "reports/equity_daily.csv"))
    ap.add_argument("--out", default=str(ROOT / "reports/dashboard.html"))
    ap.add_argument("--voided", default=str(ROOT / "reports/voided.yaml"))
    a = ap.parse_args()
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build(Path(a.ledger), Path(a.ventures), Path(a.equity), Path(a.voided)))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
