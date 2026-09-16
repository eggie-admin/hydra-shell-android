from __future__ import annotations

import os
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from magic_chat import _reject_secrets

from .agent import LUM_AGENT_NAME, LUM_MODEL, run_lum
from .doctrine import list_skills
from .mesh import HELPER_MAX_TURNS, MAX_HELPERS_PER_TURN, MESH_SPEC

ROUTER = APIRouter(prefix="/api/lum", tags=["lum-agent"])


class LumChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=16000)


@ROUTER.get("/status")
def lum_status() -> dict[str, Any]:
    return {
        "ok": True,
        "agent": LUM_AGENT_NAME,
        "model": LUM_MODEL,
        "sdk": "openai-agents",
        "mesh": {
            "topology": MESH_SPEC.topology,
            "delegation_depth": MESH_SPEC.delegation_depth,
            "helpers": [MESH_SPEC.context, MESH_SPEC.build, MESH_SPEC.critic],
            "max_helpers_per_turn": MAX_HELPERS_PER_TURN,
            "helper_max_turns": HELPER_MAX_TURNS,
        },
        "reasoning_effort": "none",
        "verbosity": "low",
        "credential_env": "OPENAI_API_KEY",
        "credential_configured": bool(os.environ.get("OPENAI_API_KEY")),
        "credential_exposed_to_client": False,
        "skills": [item["name"] for item in list_skills()],
        "mutation_authority": "deterministic_magic_cast_gateway",
        "self_approval": False,
    }


@ROUTER.post("/chat")
def lum_chat(req: LumChatRequest) -> dict[str, Any]:
    _reject_secrets(req.message)
    try:
        return run_lum(req.message)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Lum agent request failed: {type(exc).__name__}",
        ) from exc
