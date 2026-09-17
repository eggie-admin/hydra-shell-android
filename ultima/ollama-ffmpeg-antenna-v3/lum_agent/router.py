from __future__ import annotations

import os
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from magic_chat import _reject_secrets

from .agent import (
    LUM_AGENT_NAME,
    LUM_LEGACY_AGENT_NAME,
    LUM_MINI_AGENT_NAME,
    LUM_MINI_MODEL,
    LUM_MODEL,
    run_lum,
)
from .doctrine import list_skills

ROUTER = APIRouter(prefix="/api/lum", tags=["lum-agent"])


class LumChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=16000)


@ROUTER.get("/status")
def lum_status() -> dict[str, Any]:
    return {
        "ok": True,
        "agent": LUM_AGENT_NAME,
        "legacy_agent_alias": LUM_LEGACY_AGENT_NAME,
        "model": LUM_MODEL,
        "helper_agent": LUM_MINI_AGENT_NAME,
        "helper_model": LUM_MINI_MODEL,
        "sdk": "openai-agents",
        "reasoning_effort": os.environ.get("LUM_REASONING_EFFORT", "medium"),
        "verbosity": "low",
        "credential_env": "OPENAI_API_KEY",
        "credential_configured": bool(os.environ.get("OPENAI_API_KEY")),
        "credential_exposed_to_client": False,
        "skills": [item["name"] for item in list_skills()],
        "mutation_authority": "deterministic_magic_cast_gateway",
        "self_approval": False,
        "delegate_cognition_not_authority": True,
        "helper_write_authority": False,
        "arbitrary_shell": False,
        "mcp_write": False,
        "tracing_default": False,
        "deployment_lane": "staging",
    }


@ROUTER.post("/chat")
def lum_chat(req: LumChatRequest) -> dict[str, Any]:
    # Application-owned blocking ingress guard. Secret-shaped input is rejected
    # before any model or helper agent is invoked.
    _reject_secrets(req.message)
    try:
        return run_lum(req.message)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Lum agent request failed: {type(exc).__name__}",
        ) from exc
