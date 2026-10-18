"""Minimal MCP (Model Context Protocol) stdio server exposing the oddsmath
functions as tools. Stdlib only: newline-delimited JSON-RPC 2.0 on stdin/stdout,
protocol version 2025-06-18 (initialize, tools/list, tools/call, ping).

Run:  python -m oddsmath.mcp_server
Claude Desktop / Cursor config:
  {"mcpServers": {"oddsmath": {"command": "python", "args": ["-m", "oddsmath.mcp_server"]}}}
"""
from __future__ import annotations

import json
import sys

from . import __version__
from .app import ROUTES, handle

PROTOCOL_VERSION = "2025-06-18"

TOOLS = [
    {"name": "convert_odds", "route": "/v1/convert",
     "description": "Convert odds between american, decimal, fractional, probability and Kalshi cents.",
     "schema": {"type": "object", "properties": {
         "value": {"type": ["number", "string"]}, "odds": {"type": "array"},
         "fmt": {"type": "string", "enum": ["american", "decimal", "fractional", "prob", "cents"]}}}},
    {"name": "devig", "route": "/v1/devig",
     "description": "Remove the bookmaker margin from a full set of outcome odds (multiplicative, additive, power, shin or all).",
     "schema": {"type": "object", "required": ["odds"], "properties": {
         "odds": {"type": "array"}, "fmt": {"type": "string"}, "method": {"type": "string"},
         "labels": {"type": "array", "items": {"type": "string"}}}}},
    {"name": "expected_value", "route": "/v1/ev",
     "description": "EV, edge and fractional-Kelly stake for a bet or prediction-market contract, with Kalshi/Polymarket/Novig fees.",
     "schema": {"type": "object", "required": ["fair_prob", "offered"], "properties": {
         "fair_prob": {"type": "number"}, "offered": {"type": ["number", "string"]}, "fmt": {"type": "string"},
         "stake": {"type": "number"}, "kelly_mult": {"type": "number"}, "bankroll": {"type": "number"},
         "venue": {"type": "string"}, "side": {"type": "string"}, "category": {"type": "string"},
         "maker_fees": {"type": "boolean"}, "live": {"type": "boolean"}}}},
    {"name": "venue_fees", "route": "/v1/fees",
     "description": "Dollar fee for N contracts at a YES price on kalshi, polymarket or novig (taker or maker).",
     "schema": {"type": "object", "required": ["venue", "price"], "properties": {
         "venue": {"type": "string"}, "price": {"type": "number"}, "contracts": {"type": "number"},
         "side": {"type": "string"}, "category": {"type": "string"}, "maker_fees": {"type": "boolean"},
         "live": {"type": "boolean"}}}},
    {"name": "arbitrage", "route": "/v1/arb",
     "description": "Best quote per outcome across books; arb margin and stake split if the implied probabilities sum below 1.",
     "schema": {"type": "object", "required": ["outcomes"], "properties": {
         "outcomes": {"type": "array"}, "bankroll": {"type": "number"}, "fmt": {"type": "string"}}}},
    {"name": "complete_set", "route": "/v1/complete-set",
     "description": "Prediction-market YES+NO complete-set check net of taker fees.",
     "schema": {"type": "object", "required": ["yes_price", "no_price"], "properties": {
         "yes_price": {"type": "number"}, "no_price": {"type": "number"}, "venue": {"type": "string"},
         "contracts": {"type": "number"}, "category": {"type": "string"}, "live": {"type": "boolean"}}}},
    {"name": "parlay", "route": "/v1/parlay",
     "description": "Fair probability/odds of a parlay from leg probabilities, and EV vs an offered price.",
     "schema": {"type": "object", "required": ["probs"], "properties": {
         "probs": {"type": "array", "items": {"type": "number"}}, "offered_decimal": {"type": "number"}}}},
]
_BY_NAME = {t["name"]: t for t in TOOLS}
assert all(("POST", t["route"]) in ROUTES for t in TOOLS)


def _result(id_, result):
    return {"jsonrpc": "2.0", "id": id_, "result": result}


def _error(id_, code, message):
    return {"jsonrpc": "2.0", "id": id_, "error": {"code": code, "message": message}}


def dispatch(msg: dict) -> dict | None:
    """Handle one JSON-RPC message. Returns None for notifications."""
    method = msg.get("method")
    id_ = msg.get("id")
    params = msg.get("params") or {}
    if method == "initialize":
        return _result(id_, {"protocolVersion": PROTOCOL_VERSION,
                             "capabilities": {"tools": {"listChanged": False}},
                             "serverInfo": {"name": "oddsmath", "version": __version__}})
    if method in ("notifications/initialized", "notifications/cancelled"):
        return None
    if method == "ping":
        return _result(id_, {})
    if method == "tools/list":
        return _result(id_, {"tools": [{"name": t["name"], "description": t["description"],
                                        "inputSchema": t["schema"]} for t in TOOLS]})
    if method == "tools/call":
        name = params.get("name")
        tool = _BY_NAME.get(name)
        if tool is None:
            return _error(id_, -32602, f"unknown tool {name!r}")
        status, payload = handle("POST", tool["route"], params.get("arguments") or {})
        text = json.dumps(payload, indent=1)
        return _result(id_, {"content": [{"type": "text", "text": text}], "isError": status != 200,
                             **({"structuredContent": payload} if status == 200 else {})})
    if id_ is None:
        return None
    return _error(id_, -32601, f"method not found: {method}")


def serve(stdin=None, stdout=None) -> None:  # pragma: no cover - exercised via dispatch()
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    for line in stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            stdout.write(json.dumps(_error(None, -32700, "parse error")) + "\n")
            stdout.flush()
            continue
        resp = dispatch(msg)
        if resp is not None:
            stdout.write(json.dumps(resp) + "\n")
            stdout.flush()


if __name__ == "__main__":  # pragma: no cover
    serve()
