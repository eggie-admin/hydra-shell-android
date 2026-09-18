from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

import assistance
import gateway
import google_assist
import remote_ai

ROUTER = APIRouter(prefix="/api/v1", tags=["luhm-api-spine"])

CONTRACT = "luhm-os.api-spine.v1"
DEFAULT_HELPERS = 0
MAX_PARALLEL_READ_ONLY_HELPERS = 2
MAX_DELEGATION_DEPTH = 1
ALLOWED_TASKS = {"direct", "build", "research", "audit"}
ALLOWED_MODES = {"auto", "single", "mesh"}


class SpineAssistRequest(BaseModel):
    message: str = Field(min_length=1, max_length=16000)
    task: str = Field(default="direct", pattern="^(direct|build|research|audit)$")
    mode: str = Field(default="auto", pattern="^(auto|single|mesh)$")
    critic: bool = False
    github_refs: list[str] = Field(default_factory=list)
    previous_response_id: str | None = Field(default=None, max_length=160)


class SpineRouteRequest(BaseModel):
    kind: str = Field(default="generate", pattern="^(generate|realtime|status|media)$")
    prefer: str = Field(default="auto", pattern="^(auto|local|google)$")


def _boss_instructions() -> str:
    return (
        "You are a bounded LuHm OS provider lane speaking to Lum, the parent agent. "
        "Return advisory evidence only. Never recruit helpers, claim execution, grant authority, "
        "or request/reproduce credentials. The Professor remains final authority."
    )


def _configured() -> dict[str, bool]:
    return assistance._configured()


def _primary_lane(task: str, ready: dict[str, bool]) -> dict[str, str] | None:
    provider, profile = assistance._single_primary(task, ready)
    if not provider:
        return None
    return {"provider": provider, "profile": profile, "role": "parent_provider_lane"}


def _helper_calls(task: str, critic: bool, ready: dict[str, bool]) -> list[dict[str, str]]:
    calls: list[dict[str, str]] = []
    if task == "research":
        preferred = (
            ("research", "google", "fast"),
            ("build", "openai", "fast"),
        )
    else:
        preferred = (
            ("build", "openai", "deep" if task in {"build", "audit"} else "fast"),
            ("research", "google", "deep" if task == "audit" else "fast"),
        )

    for blade, provider, profile in preferred:
        if ready.get(provider):
            calls.append({"blade": blade, "provider": provider, "profile": profile})
        if len(calls) == MAX_PARALLEL_READ_ONLY_HELPERS:
            break

    if critic and ready.get("huggingface") and len(calls) < MAX_PARALLEL_READ_ONLY_HELPERS:
        calls.append({"blade": "critic", "provider": "huggingface", "profile": "fast"})
    return calls[:MAX_PARALLEL_READ_ONLY_HELPERS]


def _plan(req: SpineAssistRequest) -> dict[str, Any]:
    remote_ai._reject_secrets(req.message)
    context = assistance._github_context(req.github_refs)
    ready = _configured()

    # Sealed roleplay law: no helper mesh is recruited by default. Auto and
    # single use one bounded parent-provider lane. Only an explicit mesh
    # request may recruit read-only helpers, and that mesh is capped at two.
    explicit_mesh = req.mode == "mesh" and req.task != "direct"
    primary = None if explicit_mesh else _primary_lane(req.task, ready)
    helpers = _helper_calls(req.task, req.critic, ready) if explicit_mesh else []

    return {
        "contract": CONTRACT,
        "task": req.task,
        "requested_mode": req.mode,
        "mode": "mesh" if explicit_mesh else "parent",
        "context": context,
        "primary": primary,
        "helpers": helpers,
        "default_helpers": DEFAULT_HELPERS,
        "parallel_read_only_helpers_max": MAX_PARALLEL_READ_ONLY_HELPERS,
        "delegation_depth_max": MAX_DELEGATION_DEPTH,
        "recursive_recruiting": False,
        "helper_consensus_grants_authority": False,
        "single_parent_writer": True,
        "execution": "advisory_only",
        "crown_gate": True,
        "configured": ready,
    }


def _call_primary(lane: dict[str, str], message: str, previous_response_id: str | None) -> dict[str, Any]:
    provider = lane["provider"]
    profile = lane["profile"]
    try:
        if provider == "openai":
            payload = remote_ai._call_responses_api(
                "openai",
                message,
                None,
                profile=profile,
                instructions=_boss_instructions(),
                previous_response_id=previous_response_id,
            )
        elif provider == "google":
            payload = google_assist.generate(
                f"{_boss_instructions()}\n\nTask:\n{message}",
                profile=profile,
            )
        elif provider == "huggingface":
            payload = remote_ai._call_responses_api(
                "huggingface",
                message,
                None,
                profile=profile,
                instructions=_boss_instructions(),
            )
        else:
            return {"status": "RED", "provider": provider, "error": "unsupported_provider"}
        return {"status": "GREEN", "provider": provider, "profile": profile, "payload": payload}
    except Exception as exc:
        status_code = getattr(exc, "status_code", None)
        return {
            "status": "RED",
            "provider": provider,
            "profile": profile,
            "error": {"type": type(exc).__name__, "status_code": status_code},
        }


@ROUTER.get("/health")
def health() -> dict[str, Any]:
    return {
        "ok": True,
        "service": "LuHm OS API Spine",
        "contract": CONTRACT,
        "canonical_prefix": "/api/v1",
        "execution": "advisory_and_component_routing_only",
        "crown_gate": True,
    }


@ROUTER.get("/status")
def status() -> dict[str, Any]:
    return {
        **health(),
        "providers": _configured(),
        "roleplay_limits": {
            "default_helpers": DEFAULT_HELPERS,
            "parallel_read_only_helpers_max": MAX_PARALLEL_READ_ONLY_HELPERS,
            "delegation_depth_max": MAX_DELEGATION_DEPTH,
            "recursive_recruiting": False,
            "single_parent_writer": True,
        },
        "compatibility": {
            "remote_assistance": "/api/assist/*",
            "remote_ai": "/api/remote-ai/*",
            "antenna_gateway": "/api/status and /api/providers/route",
            "local_agent": "backend/server.py /v1/*",
            "widget_cms": "widget-cms /api/pages*",
        },
    }


@ROUTER.get("/providers")
def providers() -> dict[str, Any]:
    google = google_assist.status()
    remote = remote_ai.remote_ai_status()
    return {
        "ok": True,
        "contract": CONTRACT,
        "configured": _configured(),
        "providers": {
            "openai": remote["providers"]["openai"],
            "google": {
                "configured": google["configured"],
                "fast_model": google["fast_model"],
                "deep_model": google["deep_model"],
                "api_key_live_model": google["api_key_live_model"],
            },
            "huggingface": remote["providers"]["huggingface"],
            "github": {"configured": True, "role": "context_evidence_by_reference"},
            "cloudflare": {"configured": None, "role": "edge_transport_not_reasoning"},
        },
        "secret_material_present": False,
    }


@ROUTER.get("/capabilities")
def capabilities() -> dict[str, Any]:
    return {
        "ok": True,
        "contract": CONTRACT,
        "canonical": {
            "health": "GET /api/v1/health",
            "status": "GET /api/v1/status",
            "providers": "GET /api/v1/providers",
            "capabilities": "GET /api/v1/capabilities",
            "assist_plan": "POST /api/v1/assist/plan",
            "assist_query": "POST /api/v1/assist/query",
            "ai_chat": "POST /api/v1/ai/chat",
            "provider_route": "POST /api/v1/providers/route",
        },
        "component_planes": {
            "media": "compatibility endpoints under /api/* in main.py",
            "cms": "separate content plane under /api/pages*",
            "local_agent": "local-only compatibility plane under /v1/*",
        },
        "new_clients_must_use": "/api/v1",
    }


@ROUTER.post("/assist/plan")
def assist_plan(req: SpineAssistRequest) -> dict[str, Any]:
    return {"ok": True, **_plan(req)}


@ROUTER.post("/assist/query")
def assist_query(req: SpineAssistRequest) -> dict[str, Any]:
    plan = _plan(req)
    context = plan["context"]
    message = assistance._helper_message(req.message, context)
    started = time.perf_counter()

    if plan["primary"]:
        primary = _call_primary(plan["primary"], message, req.previous_response_id)
        return {
            "ok": primary.get("status") == "GREEN",
            **plan,
            "primary_result": primary,
            "helper_results": [],
            "wall_latency_ms": round((time.perf_counter() - started) * 1000, 1),
            "silent_cross_provider_failover": False,
        }

    calls = plan["helpers"]
    if not calls:
        return {
            "ok": True,
            **plan,
            "primary_result": None,
            "helper_results": [],
            "state": "NO_REMOTE_PROVIDER_CONFIGURED",
            "wall_latency_ms": round((time.perf_counter() - started) * 1000, 1),
        }

    results: list[dict[str, Any]] = []
    workers = min(MAX_PARALLEL_READ_ONLY_HELPERS, len(calls))
    with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="luhm-spine") as pool:
        futures = {
            pool.submit(assistance._execute_call, call, message, req.previous_response_id): call
            for call in calls
        }
        for future in as_completed(futures):
            results.append(future.result())
    order = {call["provider"]: index for index, call in enumerate(calls)}
    results.sort(key=lambda item: order.get(str(item.get("provider")), 99))

    return {
        "ok": not any(item.get("status") == "RED" for item in results),
        **plan,
        "primary_result": None,
        "helper_results": results,
        "wall_latency_ms": round((time.perf_counter() - started) * 1000, 1),
        "silent_cross_provider_failover": False,
    }


@ROUTER.post("/ai/chat")
def ai_chat(req: remote_ai.RemoteAIRequest) -> dict[str, Any]:
    return remote_ai.remote_ai_chat(req)


@ROUTER.post("/providers/route")
def provider_route(req: SpineRouteRequest) -> dict[str, Any]:
    legacy = gateway.RouteRequest(kind=req.kind, prefer=req.prefer)
    return {"contract": CONTRACT, **gateway.api_provider_route(legacy)}
