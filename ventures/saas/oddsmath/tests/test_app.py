import io
import json
from pathlib import Path

import yaml

from oddsmath import app
from oddsmath.app import handle, wsgi_app


def test_health_lists_endpoints():
    status, body = handle("GET", "/v1/health")
    assert status == 200 and body["ok"] and "/v1/devig" in body["endpoints"]
    assert handle("GET", "/")[0] == 200


def test_post_routes():
    s, b = handle("POST", "/v1/convert", {"value": -110, "fmt": "american"})
    assert s == 200 and b["results"]["decimal"] == 1.9091
    s, b = handle("POST", "/v1/devig", json.dumps({"odds": [-110, -110]}).encode())
    assert s == 200 and b["outcomes"][0]["fair_power"] == 0.5
    s, b = handle("POST", "/v1/ev", {"fair_prob": 0.6, "offered": 55, "fmt": "cents", "venue": "kalshi", "stake": 55})
    assert s == 200 and b["ev_usd"] > 0
    s, b = handle("POST", "/v1/fees", {"venue": "polymarket", "price": 0.5, "contracts": 100, "category": "crypto"})
    assert s == 200 and b["fee_usd"] == 1.75
    s, b = handle("POST", "/v1/arb", {"outcomes": [{"quotes": [{"odds": 2.1}]}, {"quotes": [{"odds": 2.05}]}]})
    assert s == 200 and b["is_arb"]
    s, b = handle("POST", "/v1/complete-set", {"yes_price": 0.48, "no_price": 0.48})
    assert s == 200 and b["is_arb"]
    s, b = handle("POST", "/v1/parlay", {"probs": [0.5, 0.5]})
    assert s == 200 and b["fair_decimal"] == 4.0


def test_get_aliases_use_query_string():
    s, b = handle("GET", "/v1/convert", query="value=2.5&fmt=decimal")
    assert s == 200 and b["results"]["probability"] == 0.4
    s, b = handle("GET", "/v1/convert", query="odds=-110,150&fmt=american")
    assert s == 200 and len(b["results"]) == 2
    s, b = handle("GET", "/v1/fees", query="venue=novig&price=0.5&contracts=100&live=true")
    assert s == 200 and b["fee_usd"] == 1.5


def test_errors_are_json_400s():
    assert handle("POST", "/v1/devig", {"odds": "nope"})[0] == 400
    assert handle("POST", "/v1/devig", {})[0] == 400
    assert handle("POST", "/v1/devig", b"{not json")[0] == 400
    assert handle("POST", "/v1/devig", b"[1,2]")[0] == 400
    assert handle("POST", "/v1/fees", {"venue": "kalshi", "price": 1.5})[0] == 400
    assert handle("GET", "/v1/devig")[0] == 405
    assert handle("POST", "/v1/nope")[0] == 404


def test_auth_gate():
    env = {"PROXY_SECRET": "s3cret", "API_KEYS": "k1, k2"}
    assert handle("GET", "/v1/health", env=env)[0] == 200  # health stays open
    assert handle("POST", "/v1/parlay", {"probs": [0.5]}, {}, env)[0] == 401
    assert handle("POST", "/v1/parlay", {"probs": [0.5]}, {"X-RapidAPI-Proxy-Secret": "s3cret"}, env)[0] == 200
    assert handle("POST", "/v1/parlay", {"probs": [0.5]}, {"x-api-key": "k2"}, env)[0] == 200
    assert handle("POST", "/v1/parlay", {"probs": [0.5]}, {"x-api-key": "k9"}, env)[0] == 401
    assert handle("POST", "/v1/parlay", {"probs": [0.5]}, {}, {})[0] == 200  # open when unset


def test_wsgi_adapter_no_sockets():
    body = json.dumps({"probs": [0.5, 0.5]}).encode()
    environ = {"REQUEST_METHOD": "POST", "PATH_INFO": "/v1/parlay", "QUERY_STRING": "",
               "CONTENT_LENGTH": str(len(body)), "wsgi.input": io.BytesIO(body),
               "HTTP_X_API_KEY": "abc"}
    captured = {}

    def start_response(status, headers):
        captured["status"] = status
        captured["headers"] = dict(headers)

    out = b"".join(wsgi_app(environ, start_response, {"API_KEYS": "abc"}))
    assert captured["status"].startswith("200")
    assert captured["headers"]["Content-Type"] == "application/json"
    assert json.loads(out)["fair_prob"] == 0.25


def test_openapi_spec_matches_routes():
    spec = yaml.safe_load(Path(app.OPENAPI_PATH).read_text())
    spec_paths = set(spec["paths"])
    routed = {p for _, p in app.ROUTES} | {"/v1/health"}
    assert routed == spec_paths
    for (_, path) in app.ROUTES:
        assert "post" in spec["paths"][path]
    for path in app.GET_ALIASES:
        assert "get" in spec["paths"][path]
    s, b = handle("GET", "/openapi.yaml")
    assert s == 200 and b["_raw"].startswith("openapi:")
