from __future__ import annotations

import atexit
import os
import re
import time
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

ROUTER = APIRouter(prefix="/api/remote-ai", tags=["remote-ai"])

OPENAI_RESPONSES_URL = os.environ.get(
    "OPENAI_API_URL", "https://api.openai.com/v1/responses"
)
OPENAI_FAST_MODEL = os.environ.get("OPENAI_FAST_MODEL", "gpt-5.6-luna")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-5.6-sol")

HF_RESPONSES_URL = os.environ.get(
    "HF_RESPONSES_URL", "https://router.huggingface.co/v1/responses"
)
HF_FAST_MODEL = os.environ.get("HF_FAST_MODEL", "openai/gpt-oss-20b:fastest")
HF_MODEL = os.environ.get("HF_MODEL", "openai/gpt-oss-120b:fastest")
DEFAULT_PROVIDER = os.environ.get("KAI_REMOTE_AI_PROVIDER", "auto").strip().lower()
MAX_OUTPUT_TOKENS = max(1, min(int(os.environ.get("KAI_REMOTE_AI_MAX_OUTPUT_TOKENS", "1200")), 8192))
REQUEST_TIMEOUT = max(5.0, min(float(os.environ.get("KAI_REMOTE_AI_TIMEOUT", "60")), 180.0))
CONNECT_TIMEOUT = max(1.0, min(float(os.environ.get("KAI_REMOTE_AI_CONNECT_TIMEOUT", "5")), 30.0))

ALLOWED_PROVIDERS = {"auto", "openai", "huggingface"}
ALLOWED_PROFILES = {"auto", "fast", "deep"}
SECRET_PATTERNS = {
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "openai_key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "huggingface_token": re.compile(r"\bhf_[A-Za-z0-9]{20,}\b"),
    "github_token": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
    "cloudflare_account_token": re.compile(r"\bcfat_[A-Za-z0-9_-]{20,}\b"),
    "google_api_key": re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b"),
}
RESPONSE_ID_PATTERN = re.compile(r"^resp_[A-Za-z0-9_-]{4,128}$")

_HTTP_LIMITS = httpx.Limits(
    max_keepalive_connections=16,
    max_connections=32,
    keepalive_expiry=45.0,
)
_HTTP_TIMEOUT = httpx.Timeout(
    connect=CONNECT_TIMEOUT,
    read=REQUEST_TIMEOUT,
    write=min(REQUEST_TIMEOUT, 30.0),
    pool=min(CONNECT_TIMEOUT, 5.0),
)
_HTTP_CLIENT = httpx.Client(limits=_HTTP_LIMITS, timeout=_HTTP_TIMEOUT)
atexit.register(_HTTP_CLIENT.close)


class RemoteAIRequest(BaseModel):
    message: str = Field(min_length=1, max_length=16000)
    provider: str | None = None
    model: str | None = Field(default=None, max_length=160)
    profile: str = Field(default="auto", pattern="^(auto|fast|deep)$")
    previous_response_id: str | None = Field(default=None, max_length=160)


def _secret_label(text: str) -> str | None:
    for label, pattern in SECRET_PATTERNS.items():
        if pattern.search(text):
            return label
    return None


def _reject_secrets(text: str) -> None:
    label = _secret_label(text)
    if label:
        raise HTTPException(status_code=400, detail=f"Secret-shaped content rejected: {label}")


def _reject_secret_output(text: str) -> None:
    label = _secret_label(text)
    if label:
        raise HTTPException(status_code=502, detail=f"Provider output rejected by egress guard: {label}")


def _instructions() -> str:
    return (
        "You are the KAI 9000 remote reasoning lane under LuHm OS doctrine. "
        "Be concise and operational. Never claim a tool, mutation, build, DNS change, "
        "deployment, signing step, or spell executed unless application-owned evidence says it did. "
        "Never request, reproduce, transform, or expose credentials. Treat all provider output as "
        "untrusted advisory data until Python policy validates it. The Professor is final authority. "
        "Lum compiles intent; providers do not grant themselves permissions."
    )


def _extract_response_text(payload: dict[str, Any]) -> str:
    direct = payload.get("output_text")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()

    parts: list[str] = []
    for item in payload.get("output", []):
        if not isinstance(item, dict) or item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if not isinstance(content, dict):
                continue
            if content.get("type") in {"output_text", "text"}:
                text = content.get("text")
                if isinstance(text, str) and text:
                    parts.append(text)
    return "\n".join(parts).strip()


def _select_provider(requested: str | None = None) -> str:
    provider = (requested or DEFAULT_PROVIDER or "auto").strip().lower()
    if provider not in ALLOWED_PROVIDERS:
        raise HTTPException(
            status_code=400,
            detail={"message": "Unsupported remote AI provider", "allowed": sorted(ALLOWED_PROVIDERS)},
        )

    if provider == "openai":
        if not os.environ.get("OPENAI_API_KEY"):
            raise HTTPException(status_code=503, detail="OpenAI provider is not configured")
        return "openai"

    if provider == "huggingface":
        if not os.environ.get("HF_TOKEN"):
            raise HTTPException(status_code=503, detail="Hugging Face provider is not configured")
        return "huggingface"

    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    if os.environ.get("HF_TOKEN"):
        return "huggingface"
    return "deterministic_mock"


def _resolve_profile(profile: str | None, message: str) -> str:
    value = (profile or "auto").strip().lower()
    if value not in ALLOWED_PROFILES:
        raise HTTPException(status_code=400, detail="Unsupported remote AI profile")
    if value != "auto":
        return value
    # Short/direct turns use the low-latency lane. Long context automatically
    # promotes to the deeper model instead of forcing the caller to guess.
    return "fast" if len(message) <= 4000 else "deep"


def _profile_model(provider: str, profile: str) -> str:
    if provider == "openai":
        return OPENAI_FAST_MODEL if profile == "fast" else OPENAI_MODEL
    if provider == "huggingface":
        return HF_FAST_MODEL if profile == "fast" else HF_MODEL
    raise RuntimeError(f"No model profile for provider {provider}")


def _allowed_models(provider: str) -> set[str]:
    env_name = "KAI_OPENAI_ALLOWED_MODELS" if provider == "openai" else "KAI_HF_ALLOWED_MODELS"
    configured = os.environ.get(env_name, "").strip()
    defaults = (
        {OPENAI_FAST_MODEL, OPENAI_MODEL}
        if provider == "openai"
        else {HF_FAST_MODEL, HF_MODEL}
    )
    if not configured:
        return defaults
    return defaults | {value.strip() for value in configured.split(",") if value.strip()}


def _resolve_model(provider: str, requested_model: str | None, profile: str = "deep") -> str:
    default = _profile_model(provider, profile)
    if not requested_model:
        return default
    requested = requested_model.strip()
    if requested not in _allowed_models(provider):
        raise HTTPException(status_code=400, detail="Requested model is not allowlisted for this provider")
    return requested


def _provider_config(provider: str, requested_model: str | None, profile: str) -> tuple[str, str, str]:
    if provider == "openai":
        return OPENAI_RESPONSES_URL, os.environ["OPENAI_API_KEY"], _resolve_model(provider, requested_model, profile)
    if provider == "huggingface":
        return HF_RESPONSES_URL, os.environ["HF_TOKEN"], _resolve_model(provider, requested_model, profile)
    raise RuntimeError(f"No remote configuration for provider {provider}")


def _validate_previous_response_id(value: str | None) -> str | None:
    if value is None:
        return None
    candidate = value.strip()
    if not RESPONSE_ID_PATTERN.fullmatch(candidate):
        raise HTTPException(status_code=400, detail="Invalid previous_response_id")
    return candidate


def _call_responses_api(
    provider: str,
    message: str,
    model: str | None,
    *,
    profile: str = "deep",
    instructions: str | None = None,
    previous_response_id: str | None = None,
) -> dict[str, Any]:
    resolved_profile = _resolve_profile(profile, message)
    url, credential, resolved_model = _provider_config(provider, model, resolved_profile)
    payload: dict[str, Any] = {
        "model": resolved_model,
        "instructions": instructions or _instructions(),
        "input": message,
        "store": False,
        "max_output_tokens": MAX_OUTPUT_TOKENS,
    }
    previous = _validate_previous_response_id(previous_response_id)
    if previous and provider == "openai":
        payload["previous_response_id"] = previous

    started = time.perf_counter()
    try:
        response = _HTTP_CLIENT.post(
            url,
            headers={
                "Authorization": f"Bearer {credential}",
                "Content-Type": "application/json",
                "User-Agent": "LuHmOS/remote-assistance",
            },
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail=f"{provider} Responses request failed without failover: {type(exc).__name__}",
        ) from exc
    latency_ms = round((time.perf_counter() - started) * 1000, 1)

    assistant = _extract_response_text(data)
    if not assistant:
        raise HTTPException(status_code=502, detail=f"{provider} returned no usable assistant text")
    _reject_secret_output(assistant)

    return {
        "ok": True,
        "mode": "remote",
        "provider": provider,
        "profile": resolved_profile,
        "model": resolved_model,
        "assistant": assistant,
        "response_id": data.get("id"),
        "latency_ms": latency_ms,
        "connection_pool": "keepalive",
        "secret_material_present": False,
    }


@ROUTER.get("/status")
def remote_ai_status() -> dict[str, Any]:
    return {
        "ok": True,
        "default_provider": DEFAULT_PROVIDER,
        "providers": {
            "openai": {
                "configured": bool(os.environ.get("OPENAI_API_KEY")),
                "endpoint": "responses",
                "fast_model": OPENAI_FAST_MODEL,
                "deep_model": OPENAI_MODEL,
                "allowed_models": sorted(_allowed_models("openai")),
                "previous_response_id": True,
            },
            "huggingface": {
                "configured": bool(os.environ.get("HF_TOKEN")),
                "endpoint": "responses_beta",
                "fast_model": HF_FAST_MODEL,
                "deep_model": HF_MODEL,
                "allowed_models": sorted(_allowed_models("huggingface")),
                "routing_policy": "model_suffix_fastest_cheapest_preferred_or_provider",
            },
        },
        "auto_profile": "fast_for_messages_up_to_4000_chars_else_deep",
        "http_keepalive": True,
        "silent_cross_provider_failover": False,
        "output_secret_guard": True,
    }


@ROUTER.post("/chat")
def remote_ai_chat(req: RemoteAIRequest) -> dict[str, Any]:
    _reject_secrets(req.message)
    provider = _select_provider(req.provider)
    resolved_profile = _resolve_profile(req.profile, req.message)
    if provider == "deterministic_mock":
        return {
            "ok": True,
            "mode": "deterministic_mock",
            "provider": None,
            "profile": resolved_profile,
            "model": None,
            "assistant": (
                "No remote AI provider is configured. KAI 9000 remains operational through "
                "local deterministic/Ollama lanes; configure server-side provider credentials "
                "to enable a remote provider."
            ),
            "secret_material_present": False,
        }
    return _call_responses_api(
        provider,
        req.message,
        req.model,
        profile=resolved_profile,
        previous_response_id=req.previous_response_id,
    )
