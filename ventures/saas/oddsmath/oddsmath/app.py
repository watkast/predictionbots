"""Framework-free JSON router for oddsmath.

`handle(method, path, body, headers, env)` returns `(status, payload)` and has
no I/O, so it runs identically under the local stdlib server, under Cloudflare
Python Workers (`worker.py`) and in tests. `wsgi_app` wraps it for any WSGI host.

Auth: when `env["PROXY_SECRET"]` is set, every /v1/* request must carry
`X-RapidAPI-Proxy-Secret: <secret>` (how RapidAPI proves a call came through
its billing proxy). When `env["API_KEYS"]` (comma-separated) is set, a request
may instead carry `X-API-Key` in that list (keys handed out after a Stripe
payment link checkout). With neither set the API is open (free tier / dev).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable
from urllib.parse import parse_qs

from . import __version__
from . import core
from .core import OddsError

_HERE = Path(__file__).resolve().parent
OPENAPI_PATH = _HERE.parent / "openapi.yaml"

RATE_NOTE = "free: 100 req/day per IP; paid tiers via RapidAPI or Stripe (see README)"


# --------------------------------------------------------------------------
# endpoint implementations: dict -> dict
# --------------------------------------------------------------------------
def _num(body: dict, key: str, default=None, required: bool = False) -> Any:
    if key not in body or body[key] is None:
        if required:
            raise OddsError(f"missing field {key!r}")
        return default
    return body[key]


def ep_convert(body: dict) -> dict:
    fmt = body.get("fmt", "american")
    vals = body.get("odds")
    single = vals is None or not isinstance(vals, list)
    if vals is None:
        vals = [_num(body, "value", required=True)]
    elif single:
        vals = [vals]
    out = [core.all_formats(core.to_prob(v, fmt)) for v in vals]
    return {"input_fmt": fmt, "results": out if not single else out[0]}


def ep_devig(body: dict) -> dict:
    odds = _num(body, "odds", required=True)
    if not isinstance(odds, list):
        raise OddsError("odds must be a list")
    return core.devig_report(odds, body.get("fmt", "american"), body.get("method", "power"),
                             body.get("labels"))


def ep_ev(body: dict) -> dict:
    return core.ev_report(
        fair_prob=_num(body, "fair_prob", required=True),
        offered=_num(body, "offered", required=True),
        fmt=body.get("fmt", "decimal"),
        stake=body.get("stake", 1.0),
        kelly_mult=body.get("kelly_mult", 0.25),
        bankroll=body.get("bankroll"),
        venue=body.get("venue"),
        side=body.get("side", "taker"),
        category=body.get("category"),
        maker_fees=body.get("maker_fees"),
        live=bool(body.get("live", False)),
    )


def ep_fees(body: dict) -> dict:
    return core.venue_fee(
        venue=_num(body, "venue", required=True),
        price=_num(body, "price", required=True),
        contracts=body.get("contracts", 1),
        side=body.get("side", "taker"),
        category=body.get("category"),
        maker_fees=body.get("maker_fees"),
        live=bool(body.get("live", False)),
    )


def ep_arb(body: dict) -> dict:
    outcomes = _num(body, "outcomes", required=True)
    if not isinstance(outcomes, list):
        raise OddsError("outcomes must be a list")
    return core.arb_report(outcomes, body.get("bankroll", 100.0), body.get("fmt", "decimal"))


def ep_complete_set(body: dict) -> dict:
    return core.complete_set_report(
        yes_price=_num(body, "yes_price", required=True),
        no_price=_num(body, "no_price", required=True),
        venue=body.get("venue", "kalshi"),
        contracts=body.get("contracts", 100),
        category=body.get("category"),
        live=bool(body.get("live", False)),
    )


def ep_parlay(body: dict) -> dict:
    probs = _num(body, "probs", required=True)
    if not isinstance(probs, list):
        raise OddsError("probs must be a list")
    return core.parlay(probs, body.get("offered_decimal"))


ROUTES: dict[tuple[str, str], Callable[[dict], dict]] = {
    ("POST", "/v1/convert"): ep_convert,
    ("POST", "/v1/devig"): ep_devig,
    ("POST", "/v1/ev"): ep_ev,
    ("POST", "/v1/fees"): ep_fees,
    ("POST", "/v1/arb"): ep_arb,
    ("POST", "/v1/complete-set"): ep_complete_set,
    ("POST", "/v1/parlay"): ep_parlay,
}

# GET aliases accept the same fields as query-string parameters (handy for curl)
GET_ALIASES = {"/v1/convert": ep_convert, "/v1/fees": ep_fees, "/v1/ev": ep_ev}


def _coerce_query(qs: dict[str, list[str]]) -> dict:
    out: dict[str, Any] = {}
    for k, vs in qs.items():
        v = vs[-1]
        if k in ("odds", "probs", "labels"):
            parts = [x for x in v.split(",") if x != ""]
            out[k] = [_auto(x) for x in parts]
        else:
            out[k] = _auto(v)
    return out


def _auto(x: str):
    if x.lower() in ("true", "false"):
        return x.lower() == "true"
    try:
        return int(x)
    except ValueError:
        try:
            return float(x)
        except ValueError:
            return x


# --------------------------------------------------------------------------
# dispatcher
# --------------------------------------------------------------------------
def _authorized(path: str, headers: dict, env: dict) -> bool:
    if not path.startswith("/v1/"):
        return True
    h = {k.lower(): v for k, v in (headers or {}).items()}
    secret = (env or {}).get("PROXY_SECRET")
    keys = [k.strip() for k in ((env or {}).get("API_KEYS") or "").split(",") if k.strip()]
    if not secret and not keys:
        return True
    if secret and h.get("x-rapidapi-proxy-secret") == secret:
        return True
    if keys and h.get("x-api-key") in keys:
        return True
    return False


def handle(method: str, path: str, body: dict | bytes | str | None = None,
           headers: dict | None = None, env: dict | None = None,
           query: str = "") -> tuple[int, dict]:
    method = (method or "GET").upper()
    path = path.split("?", 1)[0].rstrip("/") or "/"
    if path in ("/", "/health", "/v1/health"):
        return 200, {"ok": True, "service": "oddsmath", "version": __version__,
                     "endpoints": sorted(p for _, p in ROUTES), "rate_limit": RATE_NOTE}
    if path in ("/openapi.yaml", "/openapi.json", "/v1/openapi.yaml"):
        try:
            return 200, {"_raw": OPENAPI_PATH.read_text(), "_content_type": "application/yaml"}
        except OSError:
            return 404, {"error": "openapi spec not bundled"}
    if not _authorized(path, headers or {}, env or {}):
        return 401, {"error": "unauthorized: subscribe on RapidAPI or send X-API-Key"}
    if method == "GET" and path in GET_ALIASES:
        fn = GET_ALIASES[path]
        payload = _coerce_query(parse_qs(query or ""))
    else:
        fn = ROUTES.get((method, path))
        if fn is None:
            if any(p == path for _, p in ROUTES):
                return 405, {"error": f"{method} not allowed on {path}; use POST"}
            return 404, {"error": f"no route {method} {path}"}
        if isinstance(body, (bytes, str)):
            try:
                payload = json.loads(body or "{}")
            except json.JSONDecodeError as e:
                return 400, {"error": f"invalid JSON body: {e.msg}"}
        else:
            payload = body or {}
        if not isinstance(payload, dict):
            return 400, {"error": "JSON body must be an object"}
    try:
        return 200, fn(payload)
    except OddsError as e:
        return 400, {"error": str(e)}
    except (TypeError, ValueError, KeyError) as e:
        return 400, {"error": f"bad input: {e}"}


def render(status: int, payload: dict) -> tuple[int, str, bytes]:
    """(status, content_type, body_bytes) for any transport."""
    if "_raw" in payload:
        return status, payload.get("_content_type", "text/plain"), payload["_raw"].encode()
    return status, "application/json", json.dumps(payload, separators=(",", ":")).encode()


_REASONS = {200: "OK", 400: "Bad Request", 401: "Unauthorized", 404: "Not Found", 405: "Method Not Allowed"}


def wsgi_app(environ, start_response, env: dict | None = None):
    length = int(environ.get("CONTENT_LENGTH") or 0)
    body = environ["wsgi.input"].read(length) if length else b""
    headers = {k[5:].replace("_", "-"): v for k, v in environ.items() if k.startswith("HTTP_")}
    status, payload = handle(environ.get("REQUEST_METHOD", "GET"), environ.get("PATH_INFO", "/"),
                             body, headers, env, environ.get("QUERY_STRING", ""))
    status, ctype, raw = render(status, payload)
    start_response(f"{status} {_REASONS.get(status, 'Error')}",
                   [("Content-Type", ctype), ("Content-Length", str(len(raw))),
                    ("Access-Control-Allow-Origin", "*")])
    return [raw]
