from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

APP_NAME = "LuHm OS Local Harness"
APP_VERSION = "1.0.10"
ALLOWED_ORIGINS = [
    "https://appassets.androidplatform.net",
    "https://lum.eggiebagelface.lan",
]

app = FastAPI(title=APP_NAME, version=APP_VERSION, docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-LuHm-Request"],
)


@app.get("/health")
def health() -> dict[str, object]:
    return {
        "ok": True,
        "service": "luhm_local_harness",
        "version": APP_VERSION,
        "network_posture": "local_first",
        "public_backend_fallback": False,
    }


@app.get("/api/runtime")
def runtime() -> dict[str, object]:
    return {
        "frontend": "packaged_appassets",
        "backend": "local_system",
        "release_authority": "github_releases",
        "browser_secrets": False,
        "direct_shell_execution": False,
    }
