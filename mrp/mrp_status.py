#!/usr/bin/env python3
"""
Mr. P — Status page v0 (stdlib only).  Read-only, plain text, phone-friendly.

  GET /?k=TOKEN                 recorder health + latest BRTI + the analyzer's gate report (cached 10 min)
  GET /windows.csv?k=TOKEN      per-window detail from the last analyzer run
  GET /raw/YYYY-MM-DD/HH.jsonl?k=TOKEN   a raw data file

Env: MRP_DATA_DIR (default ./data), MRP_STATUS_PORT (8787), MRP_STATUS_TOKEN (if set, required as ?k=)
"""
from __future__ import annotations

import glob
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mrp_recorder as R  # noqa: E402  (loads .env, gives DATA_DIR)

DATA_DIR = os.path.abspath(os.environ.get("MRP_DATA_DIR", "./data"))
PORT = int(os.environ.get("MRP_STATUS_PORT", "8787"))
TOKEN = os.environ.get("MRP_STATUS_TOKEN", "")
PY = sys.executable
_cache = {"t": 0.0, "txt": ""}


def sh(cmd: list[str], timeout: float = 20) -> str:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout).stdout.strip()
    except Exception as e:  # noqa
        return f"({' '.join(cmd[:2])} unavailable: {e})"


def tail_jsonl(path: str, n: int = 400) -> list[dict]:
    try:
        with open(path, "rb") as fh:
            fh.seek(0, 2)
            size = fh.tell()
            fh.seek(max(0, size - 200_000))
            lines = fh.read().decode("utf-8", "ignore").splitlines()[-n:]
        out = []
        for ln in lines:
            try:
                out.append(json.loads(ln))
            except json.JSONDecodeError:
                pass
        return out
    except OSError:
        return []


def health() -> str:
    files = sorted(glob.glob(os.path.join(DATA_DIR, "*", "*.jsonl")))
    total = sum(os.path.getsize(f) for f in files)
    du = shutil.disk_usage(DATA_DIR if os.path.isdir(DATA_DIR) else "/")
    lines = [f"Mr. P status  {datetime.now(timezone.utc):%Y-%m-%d %H:%M:%S}Z",
             f"recorder service: {sh(['systemctl', 'is-active', 'mrp']) or '?'}   "
             f"data files: {len(files)}  ({total/1e6:.1f} MB, disk free {du.free/1e9:.1f} GB)"]
    if files:
        recs = tail_jsonl(files[-1])
        last_idx = next((r for r in reversed(recs) if r.get("k") == "pmus.idx"), None)
        last_mkt = next((r for r in reversed(recs) if r.get("k") == "pmus.market"), None)
        last_state = next((r for r in reversed(recs) if r.get("k") == "pmus.state"), None)
        last_err = next((r for r in reversed(recs) if r.get("k") == "err"), None)
        if last_idx:
            age = time.time() - last_idx["d"]["ts"]
            lines.append(f"last BRTI print: {last_idx['d']['c']} @ {datetime.fromtimestamp(last_idx['d']['ts'], tz=timezone.utc):%H:%M:%S}Z "
                         f"({age:.0f}s ago){'  <-- STALE' if age > 30 else ''}")
        if last_mkt:
            apt = last_mkt["d"].get("assetPriceTerms") or {}
            lines.append(f"last market seen: {last_mkt['d'].get('slug')}  priceToBeat={R.parse_amount(apt.get('priceToBeat'))}")
        if last_state:
            lines.append(f"last state change: {last_state['d'].get('slug')} {last_state['d'].get('from')} -> {last_state['d'].get('to')}")
        if last_err:
            lines.append(f"last error: {last_err['d']}")
        kinds: dict[str, int] = {}
        for r in recs:
            kinds[r.get("k")] = kinds.get(r.get("k"), 0) + 1
        lines.append("recent record mix: " + ", ".join(f"{k}={v}" for k, v in sorted(kinds.items())))
    lines.append("")
    lines.append("--- recorder log (last 12 lines) ---")
    lines.append(sh(["journalctl", "-u", "mrp", "-n", "12", "--no-pager", "-o", "cat"]))
    return "\n".join(lines)


def report() -> str:
    if time.time() - _cache["t"] < 600 and _cache["txt"]:
        return _cache["txt"]
    try:
        p = subprocess.run([PY, os.path.join(HERE, "mrp_analyze.py"), DATA_DIR, "--csv",
                            os.path.join(DATA_DIR, "windows.csv")],
                           capture_output=True, text=True, timeout=240)
        txt = (p.stdout or "") + (("\n[stderr]\n" + p.stderr[-2000:]) if p.returncode else "")
    except Exception as e:  # noqa
        txt = f"analyzer failed: {e}"
    _cache.update(t=time.time(), txt=txt)
    return txt


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):  # quiet
        pass

    def _send(self, code: int, body: str, ctype="text/plain; charset=utf-8"):
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        if TOKEN and q.get("k", [""])[0] != TOKEN:
            return self._send(403, "forbidden\n")
        if u.path == "/":
            return self._send(200, health() + "\n\n--- gate report (cached 10 min) ---\n" + report() + "\n")
        if u.path == "/windows.csv":
            p = os.path.join(DATA_DIR, "windows.csv")
            if not os.path.exists(p):
                report()
            try:
                with open(p, encoding="utf-8") as fh:
                    return self._send(200, fh.read(), "text/csv; charset=utf-8")
            except OSError:
                return self._send(404, "no windows.csv yet\n")
        if u.path.startswith("/raw/"):
            rel = os.path.normpath(u.path[len("/raw/"):])
            p = os.path.join(DATA_DIR, rel)
            if rel.startswith("..") or not p.startswith(DATA_DIR) or not os.path.isfile(p):
                return self._send(404, "not found\n")
            with open(p, encoding="utf-8", errors="ignore") as fh:
                return self._send(200, fh.read())
        return self._send(404, "not found\n")


if __name__ == "__main__":
    print(f"status page on :{PORT}  data={DATA_DIR}  token={'set' if TOKEN else 'NONE (open)'}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), H).serve_forever()
