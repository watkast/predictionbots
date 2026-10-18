"""Cloudflare Python Workers entrypoint (NOT exercised by tests; needs the
`workers` runtime module that only exists inside workerd / `wrangler dev`).

wrangler.toml points `main` here. The handler reads the raw body, calls the
pure `handle()` and returns a Response. Secrets (`PROXY_SECRET`, `API_KEYS`)
come from `wrangler secret put` and show up on `self.env`.
"""
from __future__ import annotations

try:  # pragma: no cover - only importable inside the Workers runtime
    from workers import Response, WorkerEntrypoint  # type: ignore
except ImportError:  # pragma: no cover
    Response = None  # type: ignore
    WorkerEntrypoint = object  # type: ignore

from .app import handle, render


def _env_dict(env) -> dict:
    out = {}
    for k in ("PROXY_SECRET", "API_KEYS"):
        v = getattr(env, k, None)
        if v:
            out[k] = str(v)
    return out


class Default(WorkerEntrypoint):  # pragma: no cover
    async def fetch(self, request):
        url = request.url
        path_q = url.split("//", 1)[-1].split("/", 1)[-1] if "//" in url else url
        path, _, query = ("/" + path_q).partition("?")
        body = await request.text() if request.method in ("POST", "PUT") else None
        headers = {}
        try:
            for k, v in request.headers.items():
                headers[str(k)] = str(v)
        except Exception:
            pass
        status, payload = handle(request.method, path, body, headers, _env_dict(self.env), query)
        status, ctype, raw = render(status, payload)
        return Response(raw, status=status,
                        headers={"Content-Type": ctype, "Access-Control-Allow-Origin": "*"})
