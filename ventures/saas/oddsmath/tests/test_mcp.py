import io
import json

from oddsmath import mcp_server
from oddsmath.mcp_server import dispatch


def test_initialize_and_list():
    r = dispatch({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    assert r["result"]["serverInfo"]["name"] == "oddsmath"
    assert dispatch({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None
    r = dispatch({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    names = {t["name"] for t in r["result"]["tools"]}
    assert {"devig", "expected_value", "venue_fees", "arbitrage"} <= names
    assert all("inputSchema" in t for t in r["result"]["tools"])


def test_tools_call_ok_and_error():
    r = dispatch({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                  "params": {"name": "devig", "arguments": {"odds": [-110, -110]}}})
    assert r["result"]["isError"] is False
    assert r["result"]["structuredContent"]["outcomes"][0]["fair_power"] == 0.5
    assert json.loads(r["result"]["content"][0]["text"])["hold"] > 0
    r = dispatch({"jsonrpc": "2.0", "id": 4, "method": "tools/call",
                  "params": {"name": "devig", "arguments": {"odds": [-110]}}})
    assert r["result"]["isError"] is True
    r = dispatch({"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "nope"}})
    assert r["error"]["code"] == -32602
    assert dispatch({"jsonrpc": "2.0", "id": 6, "method": "bogus"})["error"]["code"] == -32601
    assert dispatch({"jsonrpc": "2.0", "id": 7, "method": "ping"})["result"] == {}


def test_serve_loop_over_streams():
    lines = [json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}), "", "not json",
             json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"})]
    out = io.StringIO()
    mcp_server.serve(io.StringIO("\n".join(lines) + "\n"), out)
    replies = [json.loads(l) for l in out.getvalue().splitlines()]
    assert len(replies) == 2
    assert "tools" in replies[0]["result"]
    assert replies[1]["error"]["code"] == -32700
