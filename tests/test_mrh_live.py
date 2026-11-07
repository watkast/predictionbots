"""Mr. H LIVE (Coinbase hopper executor): pure-logic tests plus the script's deterministic selftest. No network, no key."""
import base64
import importlib.util
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def _load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


paper = sys.modules.get("mrh_paper") or _load("mrh_paper")
live = _load("mrh_live")


def test_floor_to_is_exchange_safe():
    assert live.floor_to(3.456789, "0.01") == "3.45"
    assert live.floor_to(0.00259558, "0.00000001") == "0.00259558"
    assert live.floor_to(39.99999, "0.1") == "39.9"
    assert live.floor_to(0.1 + 0.2, "0.01") == "0.3"
    assert live.floor_to(1234.999, "1") == "1234"
    assert live.floor_to(0.0866 * 0.96, "0.00001") == "0.08313"


def test_jwt_claims_and_signature():
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature
    k = ec.generate_private_key(ec.SECP256R1())
    pem = k.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()).decode()
    key, alg = live.load_key(pem.replace("\n", "\\n"))      # GitHub-secret style escaped newlines must work
    assert alg == "ES256"
    tok = live.build_jwt("organizations/o/apiKeys/k", key, alg, "GET", "/api/v3/brokerage/accounts", t=1_800_000_000)
    h, p, s = tok.split(".")
    hdr = json.loads(base64.urlsafe_b64decode(h + "=="))
    pay = json.loads(base64.urlsafe_b64decode(p + "=="))
    assert hdr["alg"] == "ES256" and hdr["kid"] == "organizations/o/apiKeys/k" and hdr["typ"] == "JWT"
    assert pay["uri"] == "GET api.coinbase.com/api/v3/brokerage/accounts" and pay["exp"] - pay["nbf"] == 120 and pay["iss"] == "cdp"
    sig = base64.urlsafe_b64decode(s + "==")
    k.public_key().verify(encode_dss_signature(int.from_bytes(sig[:32], "big"), int.from_bytes(sig[32:], "big")),
                          f"{h}.{p}".encode(), ec.ECDSA(hashes.SHA256()))


def test_product_map_filters_dead_and_non_usd():
    prods = [{"product_id": "SAFE-USD", "status": "online", "base_increment": "0.01", "quote_increment": "0.00001", "quote_min_size": "1", "price": "0.0866"},
             {"product_id": "LOOM-USD", "status": "delisted", "price": "0.01"},
             {"product_id": "BTC-EUR", "status": "online", "price": "70000"},
             {"product_id": "X-USD", "status": "online", "trading_disabled": True, "price": "1"}]
    m = live.product_map(prods)
    assert list(m) == ["SAFE-USD"] and m["SAFE-USD"]["base_inc"] == "0.01" and m["SAFE-USD"]["quote_inc"] == "0.00001"


def test_holdings_ignore_dust_and_dead_listings():
    cb = paper.FakeCB()
    cb.bids["FLAT-USD"] = 10.0
    ex = live.FakeEx(cb, usd=1.25, coins={"FLAT": 0.345, "LOOM": 302.0, "DUST": 0.0004})
    st = live.load_state(Path("/nonexistent"))
    st["products"] = {"FLAT-USD": {"base_inc": "0.00000001", "quote_inc": "0.01", "quote_min": 1.0, "base_min": 0, "price": 10.0},
                      "DUST-USD": {"base_inc": "0.01", "quote_inc": "0.01", "quote_min": 1.0, "base_min": 0, "price": 1.0}}
    usd, held = live.holdings(ex, cb, st)
    assert usd == 1.25 and [h["pid"] for h in held] == ["FLAT-USD"] and abs(held[0]["value"] - 3.45) < 1e-9


def test_selftest_end_to_end(capsys):
    live.selftest()
    assert "selftest ok" in capsys.readouterr().out
