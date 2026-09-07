from __future__ import annotations

import os
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from magic_chat import _reject_secrets

from .agent import (
    LUM_AGENT_NAME,
    LUM_LUNA_MODEL,
    LUM_MODEL,
    LUM_SOL_MODEL,
    LUM_TRANSPORT,
    run_lum,
)
from .doctrine import list_skills

ROUTER = APIRouter(prefix="/api/lum", tags=["lum-agent"])


class LumChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=16000)
    session_id: str = Field(
        default="kai9000-default",
        min_length=1,
        max_length=64,
        pattern=r"^[A-Za-z0-9._-]+$",
    )


@ROUTER.get("/status")
def lum_status() -> dict[str, Any]:
    return {
        "ok": True,
        "agent": LUM_AGENT_NAME,
        "model": LUM_MODEL,
        "default_model": LUM_LUNA_MODEL,
        "heavy_model": LUM_SOL_MODEL,
        "sdk": "openai-agents",
        "api": "responses",
        "transport": LUM_TRANSPORT,
        "session_memory": "sqlite",
        "session_id_policy": "client-generated opaque id; 1-64 [A-Za-z0-9._-]",
        "default_reasoning_effort": "none",
        "heavy_reasoning_effort": "medium",
        "verbosity": "low",
        "credential_env": "OPENAI_API_KEY",
        "credential_configured": bool(os.environ.get("OPENAI_API_KEY")),
        "credential_exposed_to_client": False,
        "skills": [item["name"] for item in list_skills()],
        "mutation_authority": "deterministic_magic_cast_gateway",
        "crown_holder": "Professor",
        "self_approval": False,
        "silent_cross_provider_failover": False,
    }


@ROUTER.post("/chat")
def lum_chat(req: LumChatRequest) -> dict[str, Any]:
    _reject_secrets(req.message)
    try:
        return run_lum(req.message, session_id=req.session_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Lum agent request failed: {type(exc).__name__}",
        ) from exc
