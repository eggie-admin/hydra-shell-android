from __future__ import annotations

import hmac
import os
import secrets
import time
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

APP_NAME = "LuHm OS Local Harness"
APP_VERSION = "1.0.11"
HARNESS_PORT = 8791
PAIR_SCHEMA = "luhm_os.local_harness_pair.v1"
SESSION_TTL_SECONDS = 900
TICKET_TTL_SECONDS = 30
PAIR_CODE = os.environ.get("LUHM_PAIR_CODE", "")
ALLOWED_ORIGINS = [
    "https://appassets.androidplatform.net",
    "http://127.0.0.1",
    "http://localhost",
]
_sessions: dict[str, float] = {}
_tickets: dict[str, float] = {}

app = FastAPI(title=APP_NAME, version=APP_VERSION, docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-LuHm-Request", "Authorization"],
)


def _now() -> float:
    return time.time()


def _purge() -> None:
    now = _now()
    for store in (_sessions, _tickets):
        stale = [key for key, expires in store.items() if expires <= now]
        for key in stale:
            store.pop(key, None)


def _bearer(request: Request) -> str:
    value = request.headers.get("Authorization", "")
    prefix = "Bearer "
    return value[len(prefix):].strip() if value.startswith(prefix) else ""


def _require_session(request: Request) -> tuple[str, float] | None:
    _purge()
    token = _bearer(request)
    expires = _sessions.get(token)
    if not token or expires is None or expires <= _now():
        return None
    return token, expires


@app.get("/health")
def health() -> dict[str, object]:
    _purge()
    return {
        "ok": True,
        "service": "luhm_local_harness",
        "version": APP_VERSION,
        "network_posture": "local_first",
        "public_backend_fallback": False,
        "private_lan_origin_source": "protected_local_config_only",
        "port": HARNESS_PORT,
        "cockpit": "/cockpit",
        "auth": "ephemeral_local_pairing",
        "pairing_available": bool(PAIR_CODE and len(PAIR_CODE) == 6 and PAIR_CODE.isdigit()),
        "termux_role": "external_loopback_host_only",
        "direct_shell_execution": False,
    }


@app.get("/api/runtime")
def runtime() -> dict[str, object]:
    return {
        "frontend": "packaged_appassets",
        "backend": "local_system",
        "release_authority": "github_releases",
        "browser_secrets": False,
        "direct_shell_execution": False,
        "committed_private_hostnames": False,
        "harness_port": HARNESS_PORT,
        "cockpit_path": "/cockpit",
        "termux_bridge": "loopback_http_only",
        "termux_run_command_permission_required": False,
    }


@app.post("/auth/pair")
async def pair(request: Request) -> JSONResponse:
    if not (PAIR_CODE and len(PAIR_CODE) == 6 and PAIR_CODE.isdigit()):
        return JSONResponse({"ok": False, "error": "pairing_unavailable"}, status_code=503)
    body: Any = await request.json()
    code = str(body.get("code", "")) if isinstance(body, dict) else ""
    if not hmac.compare_digest(code, PAIR_CODE):
        return JSONResponse({"ok": False, "error": "pairing_rejected"}, status_code=401)
    _purge()
    token = secrets.token_urlsafe(32)
    expires = int(_now() + SESSION_TTL_SECONDS)
    _sessions[token] = float(expires)
    return JSONResponse(
        {
            "schema": PAIR_SCHEMA,
            "ok": True,
            "token": token,
            "expires_at": expires,
            "storage": "memory_only",
            "authority": "operator_ui_session_only",
        },
        headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"},
    )


@app.get("/auth/status")
def auth_status(request: Request) -> JSONResponse:
    current = _require_session(request)
    if current is None:
        return JSONResponse({"ok": False, "authenticated": False}, status_code=401)
    _, expires = current
    return JSONResponse(
        {"ok": True, "authenticated": True, "expires_at": int(expires)},
        headers={"Cache-Control": "no-store"},
    )


@app.post("/auth/ticket")
def auth_ticket(request: Request) -> JSONResponse:
    if _require_session(request) is None:
        return JSONResponse({"ok": False, "error": "session_required"}, status_code=401)
    ticket = secrets.token_urlsafe(24)
    expires = int(_now() + TICKET_TTL_SECONDS)
    _tickets[ticket] = float(expires)
    return JSONResponse(
        {"ok": True, "ticket": ticket, "expires_at": expires, "single_use": True},
        headers={"Cache-Control": "no-store"},
    )


@app.post("/auth/logout")
def auth_logout(request: Request) -> JSONResponse:
    token = _bearer(request)
    if token:
        _sessions.pop(token, None)
    return JSONResponse({"ok": True, "logged_out": True}, headers={"Cache-Control": "no-store"})


_COCKPIT_HTML = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>LuHm Local System Harness</title>
<style>
:root{color-scheme:dark;font-family:system-ui,sans-serif;background:#05040a;color:#f7edf8}
body{margin:0;padding:18px;background:radial-gradient(circle at 70% 0,#4f287044,transparent 32%),#05040a}
main{max-width:760px;margin:auto}.card{border:1px solid #ffffff18;border-radius:18px;background:#100b18dd;padding:14px;margin:10px 0}
h1{font-size:20px;margin:0 0 4px}.muted{color:#aa9db0;font-size:12px}.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:8px}
b{display:block;color:#8defff;font-size:11px;letter-spacing:.08em}.ok{color:#9aefb8}.warn{color:#ffd071}
@media(max-width:520px){.grid{grid-template-columns:1fr}}
</style></head><body><main>
<h1>LUHM // LOCAL SYSTEM HARNESS</h1><div class="muted">Loopback cockpit · authenticated one-time view · no direct shell execution</div>
<section class="grid">
<div class="card"><b>BACKEND</b><span class="ok">127.0.0.1:8791</span></div>
<div class="card"><b>ANDROID WEBVIEW</b><span class="ok">ATTACHED LOOPBACK ONLY</span></div>
<div class="card"><b>TERMUX ROLE</b><span>EXTERNAL LOCAL HOST</span></div>
<div class="card"><b>RUN_COMMAND</b><span class="warn">NOT REQUIRED / NOT GRANTED</span></div>
</section>
<section class="card"><b>AUTHORITY</b><p>Operator login unlocks SYSTEM and ADMIN presentation surfaces only. It does not grant AI-to-shell, silent install, signing, release, deployment, DNS, or billing authority.</p></section>
<section class="card"><b>SESSION</b><p>Pair code is ephemeral. Browser token is memory-only. Cockpit tickets are one-time and short-lived. Harness restart invalidates every session.</p></section>
</main></body></html>"""


@app.get("/cockpit", response_class=HTMLResponse)
def cockpit(ticket: str = "") -> HTMLResponse:
    _purge()
    expires = _tickets.pop(ticket, None)
    if not ticket or expires is None or expires <= _now():
        return HTMLResponse(
            "<!doctype html><meta name='viewport' content='width=device-width'><body style='background:#05040a;color:#eee;font-family:system-ui;padding:20px'>Operator ticket required.</body>",
            status_code=401,
            headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"},
        )
    return HTMLResponse(
        _COCKPIT_HTML,
        headers={
            "Cache-Control": "no-store",
            "X-Content-Type-Options": "nosniff",
            "Referrer-Policy": "no-referrer",
            "Content-Security-Policy": (
                "default-src 'none'; style-src 'unsafe-inline'; "
                "frame-ancestors https://appassets.androidplatform.net"
            ),
        },
    )
