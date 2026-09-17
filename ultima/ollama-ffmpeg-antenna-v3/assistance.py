from __future__ import annotations

import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

import gateway
import remote_ai

ROUTER = APIRouter(prefix="/api/assist", tags=["luhm-remote-assistance"])

MAX_PARALLEL = 3
MAX_GITHUB_REFS = 12
ALLOWED_TASKS = {"direct", "build", "research", "audit"}
ALLOWED_MODES = {"auto", "single", "mesh"}


class AssistRequest(BaseModel):
    message: str = Field(min_length=1, max_length=16000)
    task: str = Field(default="direct", pattern="^(direct|build|research|audit)$")
    mode: str = Field(default="auto", pattern="^(auto|single|mesh)$")
    critic: bool = False
    github_refs: list[str] = Field(default_factory=list)
    previous_response_id: str | None = Field(default=None, max_length=160)


def _github_context(refs: list[str]) -> dict[str, Any]:
    if len(refs) > MAX_GITHUB_REFS:
        raise HTTPException(status_code=400, detail=f"At most {MAX_GITHUB_REFS} GitHub references are allowed")
    clean: list[str] = []
    for value in refs:
        item = str(value).strip()
        if not item or len(item) > 500 or "\n" in item or "\r" in item:
            raise HTTPException(status_code=400, detail="Invalid GitHub evidence reference")
        remote_ai._reject_secrets(item)
        clean.append(item)
    return {
        "blade": "context",
        "provider": "github",
        "policy": "evidence_by_reference_not_full_history_copy",
        "references": clean,
        "repository": os.environ.get("GITHUB_REPOSITORY"),
        "sha": os.environ.get("GITHUB_SHA"),
        "mutation_authority": False,
    }


def _configured() -> dict[str, bool]:
    return {
        "openai": bool(os.environ.get("OPENAI_API_KEY")),
        "google": bool(gateway.google_status()["configured"]),
        "huggingface": bool(os.environ.get("HF_TOKEN")),
        "github": True,
    }


def _actual_mode(task: str, requested_mode: str) -> str:
    # Direct questions bypass the mesh entirely. Complex work uses the mesh by
    # default, but callers can explicitly request a single advisory provider.
    if task == "direct":
        return "single"
    if requested_mode == "auto":
        return "mesh"
    return requested_mode


def _single_primary(task: str, ready: dict[str, bool]) -> tuple[str | None, str]:
    if task == "research":
        order = ("google", "openai", "huggingface")
    else:
        order = ("openai", "google", "huggingface")
    for provider in order:
        if ready.get(provider):
            profile = "deep" if task in {"build", "audit"} and provider != "google" else "fast"
            return provider, profile
    return None, "fast"


def _plan(task: str, mode: str, critic: bool) -> dict[str, Any]:
    task = task.strip().lower()
    mode = mode.strip().lower()
    if task not in ALLOWED_TASKS or mode not in ALLOWED_MODES:
        raise HTTPException(status_code=400, detail="Unsupported assistance route")

    ready = _configured()
    actual_mode = _actual_mode(task, mode)
    calls: list[dict[str, str]] = []

    if actual_mode == "single":
        provider, profile = _single_primary(task, ready)
        if provider:
            calls.append({"blade": "research" if provider == "google" else "build", "provider": provider, "profile": profile})
    else:
        # Default blades: Context is GitHub references and therefore has no
        # model call; Build and Research run concurrently when configured.
        if ready["openai"]:
            calls.append({"blade": "build", "provider": "openai", "profile": "deep" if task in {"build", "audit"} else "fast"})
        if ready["google"]:
            calls.append({"blade": "research", "provider": "google", "profile": "fast"})
        if critic and ready["huggingface"]:
            calls.append({"blade": "critic", "provider": "huggingface", "profile": "fast"})

    calls = calls[:MAX_PARALLEL]
    return {
        "task": task,
        "requested_mode": mode,
        "mode": actual_mode,
        "direct_questions_bypass_mesh": task == "direct",
        "parallelism_max": MAX_PARALLEL,
        "calls": calls,
        "configured": ready,
        "execution": "advisory_only",
        "crown_gate": True,
    }


def _helper_instructions(blade: str) -> str:
    return (
        f"You are the LuHm OS {blade} helper. Speak to Lum, the boss agent, not directly to the Professor. "
        "Return concise advisory evidence and concrete next steps. Do not recruit helpers. "
        "Do not claim execution, mutation, deployment, signing, release, or Crown authority. "
        "Credentials and private keys must never be requested or reproduced."
    )


def _helper_message(message: str, github_context: dict[str, Any]) -> str:
    refs = github_context.get("references") or []
    if not refs:
        return message
    rendered = "\n".join(f"- {item}" for item in refs)
    return f"{message}\n\nGitHub evidence references (resolve only when needed):\n{rendered}"


def _call_openai(message: str, profile: str, blade: str, previous_response_id: str | None) -> dict[str, Any]:
    return remote_ai._call_responses_api(
        "openai",
        message,
        None,
        profile=profile,
        instructions=_helper_instructions(blade),
        previous_response_id=previous_response_id,
    )


def _call_huggingface(message: str, profile: str, blade: str) -> dict[str, Any]:
    return remote_ai._call_responses_api(
        "huggingface",
        message,
        None,
        profile=profile,
        instructions=_helper_instructions(blade),
    )


def _call_google(message: str, blade: str) -> dict[str, Any]:
    started = time.perf_counter()
    result = gateway._google_generate(
        f"{_helper_instructions(blade)}\n\nTask:\n{message}",
        None,
    )
    result["latency_ms"] = round((time.perf_counter() - started) * 1000, 1)
    result["profile"] = "fast"
    return result


def _execute_call(call: dict[str, str], message: str, previous_response_id: str | None) -> dict[str, Any]:
    provider = call["provider"]
    blade = call["blade"]
    profile = call["profile"]
    try:
        if provider == "openai":
            payload = _call_openai(message, profile, blade, previous_response_id)
        elif provider == "google":
            payload = _call_google(message, blade)
        elif provider == "huggingface":
            payload = _call_huggingface(message, profile, blade)
        else:  # pragma: no cover - guarded by the deterministic planner
            raise RuntimeError("Unknown assistance provider")
        return {
            "blade": blade,
            "provider": provider,
            "status": "GREEN",
            "payload": payload,
        }
    except HTTPException as exc:
        return {
            "blade": blade,
            "provider": provider,
            "status": "RED",
            "error": {"status_code": exc.status_code, "detail": str(exc.detail)},
        }
    except Exception as exc:  # provider SDKs have heterogeneous exception trees
        return {
            "blade": blade,
            "provider": provider,
            "status": "RED",
            "error": {"type": type(exc).__name__},
        }


@ROUTER.get("/status")
def assistance_status() -> dict[str, Any]:
    ready = _configured()
    return {
        "ok": True,
        "service": "LuHm OS Remote Assistance",
        "contract": "luhm-os.remote-assistance.v1",
        "boss": "Lum",
        "human_authority": "Professor",
        "default_blades": {
            "context": "github_evidence_by_reference",
            "build": "openai",
            "research": "google",
            "critic": "huggingface_conditional",
        },
        "configured": ready,
        "direct_questions_bypass_mesh": True,
        "parallelism_max": MAX_PARALLEL,
        "helpers_may_recruit": False,
        "consequential_actions": "crown_gated",
        "remote_execution_authority": False,
    }


@ROUTER.post("/route")
def assistance_route(req: AssistRequest) -> dict[str, Any]:
    remote_ai._reject_secrets(req.message)
    context = _github_context(req.github_refs)
    return {"ok": True, "context": context, **_plan(req.task, req.mode, req.critic)}


@ROUTER.post("/query")
def assistance_query(req: AssistRequest) -> dict[str, Any]:
    remote_ai._reject_secrets(req.message)
    context = _github_context(req.github_refs)
    plan = _plan(req.task, req.mode, req.critic)
    message = _helper_message(req.message, context)
    calls = plan["calls"]

    if not calls:
        return {
            "ok": True,
            "context": context,
            **plan,
            "helpers": [],
            "state": "NO_REMOTE_PROVIDER_CONFIGURED",
        }

    started = time.perf_counter()
    helpers: list[dict[str, Any]] = []
    if len(calls) == 1:
        helpers.append(_execute_call(calls[0], message, req.previous_response_id))
    else:
        workers = min(MAX_PARALLEL, len(calls))
        with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="luhm-assist") as pool:
            futures = {
                pool.submit(_execute_call, call, message, req.previous_response_id): call
                for call in calls
            }
            for future in as_completed(futures):
                helpers.append(future.result())
        order = {call["provider"]: index for index, call in enumerate(calls)}
        helpers.sort(key=lambda item: order.get(str(item.get("provider")), 99))

    return {
        "ok": not any(item.get("status") == "RED" for item in helpers),
        "context": context,
        **plan,
        "helpers": helpers,
        "wall_latency_ms": round((time.perf_counter() - started) * 1000, 1),
        "silent_cross_provider_failover": False,
    }
