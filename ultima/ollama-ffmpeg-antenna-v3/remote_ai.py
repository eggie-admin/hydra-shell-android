from __future__ import annotations

import os
import re
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

ROUTER = APIRouter(prefix="/api/remote-ai", tags=["remote-ai"])

OPENAI_RESPONSES_URL = os.environ.get(
    "OPENAI_API_URL", "https://api.openai.com/v1/responses"
)
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-5.6-sol")

HF_RESPONSES_URL = os.environ.get(
    "HF_RESPONSES_URL", "https://router.huggingface.co/v1/responses"
)
HF_MODEL = os.environ.get("HF_MODEL", "openai/gpt-oss-120b:fastest")
DEFAULT_PROVIDER = os.environ.get("KAI_REMOTE_AI_PROVIDER", "auto").strip().lower()
MAX_OUTPUT_TOKENS = max(1, min(int(os.environ.get("KAI_REMOTE_AI_MAX_OUTPUT_TOKENS", "1600")), 8192))
REQUEST_TIMEOUT = max(5.0, min(float(os.environ.get("KAI_REMOTE_AI_TIMEOUT", "90")), 180.0))

ALLOWED_PROVIDERS = {"auto", "openai", "huggingface"}
SECRET_PATTERNS = {
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "openai_key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "huggingface_token": re.compile(r"\bhf_[A-Za-z0-9]{20,}\b"),
    "github_token": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
    "cloudflare_account_token": re.compile(r"\bcfat_[A-Za-z0-9_-]{20,}\b"),
    "google_api_key": re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b"),
}


class RemoteAIRequest(BaseModel):
    message: str = Field(min_length=1, max_length=16000)
    provider: str | None = None
    model: str | None = Field(default=None, max_length=160)


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


def _allowed_models(provider: str) -> set[str]:
    env_name = "KAI_OPENAI_ALLOWED_MODELS" if provider == "openai" else "KAI_HF_ALLOWED_MODELS"
    configured = os.environ.get(env_name, "").strip()
    defaults = {OPENAI_MODEL} if provider == "openai" else {HF_MODEL}
    if not configured:
        return defaults
    return defaults | {value.strip() for value in configured.split(",") if value.strip()}


def _resolve_model(provider: str, requested_model: str | None) -> str:
    default = OPENAI_MODEL if provider == "openai" else HF_MODEL
    if not requested_model:
        return default
    requested = requested_model.strip()
    if requested not in _allowed_models(provider):
        raise HTTPException(status_code=400, detail="Requested model is not allowlisted for this provider")
    return requested


def _provider_config(provider: str, requested_model: str | None) -> tuple[str, str, str]:
    if provider == "openai":
        return OPENAI_RESPONSES_URL, os.environ["OPENAI_API_KEY"], _resolve_model(provider, requested_model)
    if provider == "huggingface":
        return HF_RESPONSES_URL, os.environ["HF_TOKEN"], _resolve_model(provider, requested_model)
    raise RuntimeError(f"No remote configuration for provider {provider}")


def _call_responses_api(provider: str, message: str, model: str | None) -> dict[str, Any]:
    url, credential, resolved_model = _provider_config(provider, model)
    payload = {
        "model": resolved_model,
        "instructions": _instructions(),
        "input": message,
        "store": False,
        "max_output_tokens": MAX_OUTPUT_TOKENS,
    }
    try:
        response = httpx.post(
            url,
            headers={
                "Authorization": f"Bearer {credential}",
                "Content-Type": "application/json",
                "User-Agent": "KAI9000-LuHmOS/remote-ai",
            },
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail=f"{provider} Responses request failed without failover: {type(exc).__name__}",
        ) from exc

    assistant = _extract_response_text(data)
    if not assistant:
        raise HTTPException(status_code=502, detail=f"{provider} returned no usable assistant text")
    _reject_secret_output(assistant)

    return {
        "ok": True,
        "mode": "remote",
        "provider": provider,
        "model": resolved_model,
        "assistant": assistant,
        "response_id": data.get("id"),
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
                "default_model": OPENAI_MODEL,
                "allowed_models": sorted(_allowed_models("openai")),
            },
            "huggingface": {
                "configured": bool(os.environ.get("HF_TOKEN")),
                "endpoint": "responses_beta",
                "default_model": HF_MODEL,
                "allowed_models": sorted(_allowed_models("huggingface")),
                "routing_policy": "model_suffix_fastest_cheapest_preferred_or_provider",
            },
        },
        "silent_cross_provider_failover": False,
        "output_secret_guard": True,
    }


@ROUTER.post("/chat")
def remote_ai_chat(req: RemoteAIRequest) -> dict[str, Any]:
    _reject_secrets(req.message)
    provider = _select_provider(req.provider)
    if provider == "deterministic_mock":
        return {
            "ok": True,
            "mode": "deterministic_mock",
            "provider": None,
            "model": None,
            "assistant": (
                "No remote AI provider is configured. KAI 9000 remains operational through "
                "local deterministic/Ollama lanes; configure server-side provider credentials "
                "to enable a remote provider."
            ),
            "secret_material_present": False,
        }
    return _call_responses_api(provider, req.message, req.model)
