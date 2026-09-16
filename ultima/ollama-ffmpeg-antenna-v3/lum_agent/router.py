from __future__ import annotations

import json
import os
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from magic_chat import _reject_secrets

from .agent import (
    LUM_AGENT_NAME,
    LUM_DEEP_MODEL,
    LUM_FAST_MODEL,
    LUM_MODEL,
    run_lum,
)
from .doctrine import list_skills
from .mesh import PASS_ORDER, run_ten_pass_mesh

ROUTER = APIRouter(prefix="/api/lum", tags=["lum-agent"])


class LumChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=16000)


class LumMeshRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000)
    rss_url: str | None = Field(default=None, max_length=2000)
    rss_xml: str | None = Field(default=None, max_length=1_100_000)
    items: list[dict[str, Any]] | None = None
    max_items: int = Field(default=12, ge=1, le=25)
    deep: bool = False


@ROUTER.get("/status")
def lum_status() -> dict[str, Any]:
    return {
        "ok": True,
        "agent": LUM_AGENT_NAME,
        "model": LUM_MODEL,
        "fast_model": LUM_FAST_MODEL,
        "deep_model": LUM_DEEP_MODEL,
        "sdk": "openai-agents",
        "reasoning_effort": "none",
        "verbosity": "low",
        "credential_env": "OPENAI_API_KEY",
        "credential_configured": bool(os.environ.get("OPENAI_API_KEY")),
        "credential_exposed_to_client": False,
        "skills": [item["name"] for item in list_skills()],
        "mesh": {
            "enabled": True,
            "endpoint": "/api/lum/mesh",
            "passes": list(PASS_ORDER),
            "max_remote_model_calls": 1,
            "rss_network_policy": "https_allowlist_only",
            "rss_allowlist_env": "LUM_RSS_ALLOWED_HOSTS",
        },
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


@ROUTER.post("/mesh")
def lum_mesh(req: LumMeshRequest) -> dict[str, Any]:
    """Ten logic passes, one Lum boss call maximum.

    RSS/XML or JSON is normalized before it reaches the model. The model is not
    allowed to fetch arbitrary RSS URLs itself; server-side RSS fetches require
    an explicit LUM_RSS_ALLOWED_HOSTS entry.
    """

    _reject_secrets(req.query)
    if req.rss_xml:
        _reject_secrets(req.rss_xml)
    if req.items:
        _reject_secrets(json.dumps(req.items, ensure_ascii=False))

    def invoke_boss(prompt: str, route: str) -> dict[str, Any]:
        # Egress guard after RSS normalization and before model context.
        _reject_secrets(prompt)
        if route == "deep":
            return run_lum(
                prompt,
                model=LUM_DEEP_MODEL,
                reasoning_effort="medium",
                max_turns=6,
            )
        return run_lum(
            prompt,
            model=LUM_FAST_MODEL,
            reasoning_effort="none",
            max_turns=4,
        )

    try:
        return run_ten_pass_mesh(
            query=req.query,
            rss_url=req.rss_url,
            rss_xml=req.rss_xml,
            items=req.items,
            max_items=req.max_items,
            deep=req.deep,
            invoke_boss=invoke_boss,
        )
    except HTTPException:
        raise
    except (ValueError, httpx.HTTPError) as exc:  # type: ignore[name-defined]
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Lum mesh request failed: {type(exc).__name__}",
        ) from exc
