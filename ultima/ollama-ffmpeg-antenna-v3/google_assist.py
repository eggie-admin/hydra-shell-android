from __future__ import annotations

import hashlib
import os
import threading
import time
from typing import Any

from fastapi import HTTPException

import gateway

GOOGLE_FAST_MODEL = os.environ.get("KAI_GOOGLE_FAST_TEXT_MODEL", "gemini-3.5-flash-lite")
GOOGLE_DEEP_MODEL = os.environ.get("KAI_GOOGLE_DEEP_TEXT_MODEL", "gemini-3.8-flash")
GOOGLE_LIVE_API_MODEL = os.environ.get("KAI_GEMINI_LIVE_API_MODEL", "gemini-3.8-live")
GOOGLE_FAST_TIMEOUT_MS = max(5000, min(int(os.environ.get("KAI_GOOGLE_FAST_TIMEOUT_MS", "30000")), 120000))
GOOGLE_DEEP_TIMEOUT_MS = max(15000, min(int(os.environ.get("KAI_GOOGLE_DEEP_TIMEOUT_MS", "90000")), 300000))

_CLIENT_LOCK = threading.Lock()
_CLIENT: Any | None = None
_CLIENT_SIGNATURE: tuple[str, str | None, str, str | None] | None = None


def _credential_fingerprint() -> str | None:
    key = gateway._api_key()
    if not key:
        return None
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def _signature() -> tuple[str, str | None, str, str | None]:
    return (
        gateway.google_auth_mode(),
        gateway._project_id(),
        gateway.GOOGLE_LOCATION,
        _credential_fingerprint(),
    )


def _client() -> Any:
    global _CLIENT, _CLIENT_SIGNATURE
    signature = _signature()
    if _CLIENT is not None and signature == _CLIENT_SIGNATURE:
        return _CLIENT
    with _CLIENT_LOCK:
        signature = _signature()
        if _CLIENT is None or signature != _CLIENT_SIGNATURE:
            _CLIENT = gateway._google_client()
            _CLIENT_SIGNATURE = signature
    return _CLIENT


def _resolve_model(profile: str) -> str:
    value = profile.strip().lower()
    if value == "fast":
        return GOOGLE_FAST_MODEL
    if value == "deep":
        return GOOGLE_DEEP_MODEL
    raise HTTPException(status_code=400, detail="Unsupported Google assistance profile")


def _timeout_ms(profile: str) -> int:
    return GOOGLE_FAST_TIMEOUT_MS if profile.strip().lower() == "fast" else GOOGLE_DEEP_TIMEOUT_MS


def generate(prompt: str, profile: str = "fast") -> dict[str, Any]:
    resolved_model = _resolve_model(profile)
    timeout_ms = _timeout_ms(profile)
    try:
        from google.genai import types
    except ImportError as exc:  # pragma: no cover - dependency guard
        raise HTTPException(status_code=503, detail="google-genai is not installed") from exc

    started = time.perf_counter()
    try:
        response = _client().models.generate_content(
            model=resolved_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                http_options=types.HttpOptions(timeout=timeout_ms),
            ),
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Google assistance request failed without provider failover: {type(exc).__name__}",
        ) from exc

    usage = getattr(response, "usage_metadata", None)
    cached_tokens = getattr(usage, "cached_content_token_count", None) if usage is not None else None
    return {
        "ok": True,
        "provider": "google",
        "auth_mode": gateway.google_auth_mode(),
        "profile": profile,
        "model": resolved_model,
        "text": getattr(response, "text", None) or "",
        "latency_ms": round((time.perf_counter() - started) * 1000, 1),
        "client_cache": "process_reuse",
        "timeout_ms": timeout_ms,
        "implicit_context_cache": True,
        "cached_input_tokens": cached_tokens,
        "secret_material_present": False,
    }


def status() -> dict[str, Any]:
    base = gateway.google_status()
    return {
        **base,
        "fast_model": GOOGLE_FAST_MODEL,
        "deep_model": GOOGLE_DEEP_MODEL,
        "api_key_live_model": GOOGLE_LIVE_API_MODEL,
        "client_cache": "process_reuse",
        "fast_timeout_ms": GOOGLE_FAST_TIMEOUT_MS,
        "deep_timeout_ms": GOOGLE_DEEP_TIMEOUT_MS,
        "implicit_context_cache": True,
    }
