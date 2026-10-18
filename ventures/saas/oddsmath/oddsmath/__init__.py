"""oddsmath — betting & prediction-market math as a tiny API.

Pure-stdlib Python. `core` holds the math, `app` the JSON router (WSGI +
framework-free `handle()`), `server` a local stdlib HTTP server, `worker` the
Cloudflare Python Workers entrypoint and `mcp_server` a stdio MCP server that
exposes the same functions as tools.
"""
__version__ = "0.1.0"
