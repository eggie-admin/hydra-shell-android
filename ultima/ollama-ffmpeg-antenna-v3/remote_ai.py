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
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-6-astra")

HF_RESPONSES_URL = os.environ.get(
    "HF_RESPONSES_URL", "https://router.huggingface.co/v1/responses"
)
HF_MODEL = os.environ.get("HF_MODEL", "openai/gpt-oss-120b:fastest")
DEFAULT_PROVIDER = os.environ.get("KAI_REMOTE_AI_PROVIDER", "auto").strip().lower()
MAX_OUTPUT_TOKENS = int(os.environ.get("KAI_REMOTE_AI_MAX_OUTPUT_TOKENS", "1600"))

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
    model: str | None = None


def _reject_secrets(text: str) -> None:
    for label, pattern in SECRET_PATTERNS.items():
        if pattern.search(text):
            raise HTTPException(status_code=400, detail=f"Secret-shaped content rejected: {label}")


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


def _provider_config(provider: str, requested_model: str | None) -> tuple[str, str, str]:
    if provider == "openai":
        return OPENAI_RESPONSES_URL, os.environ["OPENAI_API_KEY"], requested_model or OPENAI_MODEL
    if provider == "huggingface":
        return HF_RESPONSES_URL, os.environ["HF_TOKEN"], requested_model or HF_MODEL
    raise RuntimeError(f"No remote configuration for provider {provider}")


def _call_responses_api(provider: str, message: str, model: str | None) -> dict[str, Any]:
    url, credential, resolved_model = _provider_config(provider, model)
    payload = {
        "model": resolved_model,
        "instructions": _instructions(),
        "input": message,
        "store": False,
        "max_output_tokens": max(1, min(MAX_OUTPUT_TOKENS, 8192)),
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
            timeout=90,
        )
        response.raise_for_status()
        data = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail=f"{provider} Responses request failed without failover: {type(exc).__name__}",
        ) from exc

    return {
        "ok": True,
        "mode": "remote",
        "provider": provider,
        "model": resolved_model,
        "assistant": _extract_response_text(data),
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
            },
            "huggingface": {
                "configured": bool(os.environ.get("HF_TOKEN")),
                "endpoint": "responses_beta",
                "default_model": HF_MODEL,
                "routing_policy": "model_suffix_fastest_cheapest_preferred_or_provider",
            },
        },
        "silent_cross_provider_failover": False,
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
                "local deterministic/Ollama lanes; configure OPENAI_API_KEY or HF_TOKEN on the "
                "server side to enable a remote provider."
            ),
            "secret_material_present": False,
        }
    return _call_responses_api(provider, req.message, req.model)
