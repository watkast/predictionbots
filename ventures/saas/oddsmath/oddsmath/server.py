"""Local dev server: `python -m oddsmath.server --port 8787` (stdlib only)."""
from __future__ import annotations

import argparse
import os
from wsgiref.simple_server import make_server

from .app import wsgi_app


def main(argv=None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8787)
    a = ap.parse_args(argv)
    env = {k: os.environ[k] for k in ("PROXY_SECRET", "API_KEYS") if os.environ.get(k)}
    with make_server(a.host, a.port, lambda e, s: wsgi_app(e, s, env)) as srv:
        print(f"oddsmath listening on http://{a.host}:{a.port}  (auth: {'on' if env else 'off'})")
        srv.serve_forever()


if __name__ == "__main__":
    main()
