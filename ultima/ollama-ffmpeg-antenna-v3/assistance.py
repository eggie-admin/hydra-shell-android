from __future__ import annotations

import atexit
import os
import re
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

import google_assist
import remote_ai

ROUTER = APIRouter(prefix="/api/assist", tags=["luhm-remote-assistance"])

MAX_PARALLEL = 3
MAX_GITHUB_REFS = 12
MAX_RESOLVED_GITHUB_REFS = 4
MAX_GITHUB_REF_BYTES = 16_384
MAX_GITHUB_CONTEXT_CHARS = 32_000
CANONICAL_GITHUB_REPO = "eggie-admin/hydra-shell-android"
ALLOWED_TASKS = {"direct", "build", "research", "audit"}
ALLOWED_MODES = {"auto", "single", "mesh"}
EXACT_REF_RE = re.compile(r"^eggie-admin/hydra-shell-android@([0-9a-f]{40}):(.+)$")
BLOB_REF_RE = re.compile(r"^https://github\.com/eggie-admin/hydra-shell-android/blob/([0-9a-f]{40})/(.+)$")

_GITHUB_HTTP = httpx.Client(
    limits=httpx.Limits(max_keepalive_connections=8, max_connections=8, keepalive_expiry=60.0),
    timeout=httpx.Timeout(5.0, connect=3.0),
    follow_redirects=True,
    http2=True,
    headers={"User-Agent": "LuHmOS/github-evidence"},
)
atexit.register(_GITHUB_HTTP.close)


class AssistRequest(BaseModel):
    message: str = Field(min_length=1, max_length=16000)
    task: str = Field(default="direct", pattern="^(direct|build|research|audit)$")
    mode: str = Field(default="auto", pattern="^(auto|single|mesh)$")
    critic: bool = False
    github_refs: list[str] = Field(default_factory=list)
    previous_response_id: str | None = Field(default=None, max_length=160)


def _safe_repo_path(path: str) -> str | None:
    clean = urllib.parse.unquote(path).strip().lstrip("/")
    if not clean or len(clean) > 500:
        return None
    parts = clean.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        return None
    lower = clean.lower()
    if lower.startswith(".git/") or "/.git/" in lower:
        return None
    if any(token in lower for token in ("/.secrets/", "/private_key", ".pem", ".p12", ".pfx")):
        return None
    return clean


def _parse_exact_github_ref(value: str) -> tuple[str, str] | None:
    match = EXACT_REF_RE.fullmatch(value) or BLOB_REF_RE.fullmatch(value)
    if not match:
        return None
    sha, path = match.groups()
    safe_path = _safe_repo_path(path)
    if safe_path is None:
        return None
    return sha, safe_path


@lru_cache(maxsize=64)
def _fetch_exact_github_excerpt(sha: str, path: str) -> dict[str, Any]:
    safe_path = _safe_repo_path(path)
    if safe_path is None or not re.fullmatch(r"[0-9a-f]{40}", sha):
        return {"status": "REJECTED", "reason": "invalid_exact_sha_or_path"}
    quoted = urllib.parse.quote(safe_path, safe="/")
    url = f"https://raw.githubusercontent.com/{CANONICAL_GITHUB_REPO}/{sha}/{quoted}"
    try:
        with _GITHUB_HTTP.stream("GET", url, headers={"Range": f"bytes=0-{MAX_GITHUB_REF_BYTES - 1}"}) as response:
            if response.status_code not in {200, 206}:
                return {"status": "UNRESOLVED", "http_status": response.status_code}
            data = bytearray()
            truncated = False
            for chunk in response.iter_bytes():
                remaining = MAX_GITHUB_REF_BYTES - len(data)
                if remaining <= 0:
                    truncated = True
                    break
                if len(chunk) > remaining:
                    data.extend(chunk[:remaining])
                    truncated = True
                    break
                data.extend(chunk)
            try:
                text = bytes(data).decode("utf-8")
            except UnicodeDecodeError:
                return {"status": "SKIPPED_BINARY"}
            if remote_ai._secret_label(text):
                return {"status": "SKIPPED_SECRET_SHAPED_CONTENT"}
            return {
                "status": "GREEN",
                "sha": sha,
                "path": safe_path,
                "text": text,
                "truncated": truncated,
                "bytes": len(data),
            }
    except httpx.HTTPError as exc:
        return {"status": "UNRESOLVED", "error_type": type(exc).__name__}


def _resolve_github_references(refs: list[str]) -> list[dict[str, Any]]:
    candidates: list[tuple[str, str, str]] = []
    for raw in refs:
        parsed = _parse_exact_github_ref(raw)
        if parsed is not None:
            sha, path = parsed
            candidates.append((raw, sha, path))
        if len(candidates) >= MAX_RESOLVED_GITHUB_REFS:
            break
    if not candidates:
        return []

    results: dict[str, dict[str, Any]] = {}
    with ThreadPoolExecutor(max_workers=min(MAX_RESOLVED_GITHUB_REFS, len(candidates)), thread_name_prefix="luhm-github") as pool:
        futures = {
            pool.submit(_fetch_exact_github_excerpt, sha, path): raw
            for raw, sha, path in candidates
        }
        for future in as_completed(futures):
            results[futures[future]] = future.result()
    return [{"reference": raw, **results[raw]} for raw, _, _ in candidates]


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
        "resolution": "bounded_exact_sha_on_demand",
        "references": clean,
        "repository": os.environ.get("GITHUB_REPOSITORY") or CANONICAL_GITHUB_REPO,
        "sha": os.environ.get("GITHUB_SHA"),
        "mutation_authority": False,
    }


def _configured() -> dict[str, bool]:
    return {
        "openai": bool(os.environ.get("OPENAI_API_KEY")),
        "google": bool(google_assist.status()["configured"]),
        "huggingface": bool(os.environ.get("HF_TOKEN")),
        "github": True,
    }


def _actual_mode(task: str, requested_mode: str) -> str:
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
            profile = "deep" if task in {"build", "audit"} else "fast"
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
        if ready["openai"]:
            calls.append({"blade": "build", "provider": "openai", "profile": "deep" if task in {"build", "audit"} else "fast"})
        if ready["google"]:
            calls.append({"blade": "research", "provider": "google", "profile": "deep" if task == "audit" else "fast"})
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


def _helper_message(message: str, github_context: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    refs = github_context.get("references") or []
    if not refs:
        return message, []
    resolved = _resolve_github_references(refs)
    blocks: list[str] = []
    used = 0
    for item in resolved:
        if item.get("status") != "GREEN":
            continue
        text = str(item.get("text") or "")
        allowance = MAX_GITHUB_CONTEXT_CHARS - used
        if allowance <= 0:
            break
        excerpt = text[:allowance]
        used += len(excerpt)
        blocks.append(f"[{item['reference']}]\n{excerpt}")

    rendered_refs = "\n".join(f"- {item}" for item in refs)
    if not blocks:
        return (
            f"{message}\n\nGitHub evidence references (not resolved; do not infer their contents):\n{rendered_refs}",
            resolved,
        )
    evidence = "\n\n".join(blocks)
    return (
        f"{message}\n\nGitHub evidence references:\n{rendered_refs}\n\nBounded exact-SHA evidence excerpts:\n{evidence}",
        resolved,
    )


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


def _call_google(message: str, profile: str, blade: str) -> dict[str, Any]:
    return google_assist.generate(
        f"{_helper_instructions(blade)}\n\nTask:\n{message}",
        profile=profile,
    )


def _execute_call(call: dict[str, str], message: str, previous_response_id: str | None) -> dict[str, Any]:
    provider = call["provider"]
    blade = call["blade"]
    profile = call["profile"]
    try:
        if provider == "openai":
            payload = _call_openai(message, profile, blade, previous_response_id)
        elif provider == "google":
            payload = _call_google(message, profile, blade)
        elif provider == "huggingface":
            payload = _call_huggingface(message, profile, blade)
        else:
            raise RuntimeError("Unknown assistance provider")
        return {"blade": blade, "provider": provider, "status": "GREEN", "payload": payload}
    except HTTPException as exc:
        return {"blade": blade, "provider": provider, "status": "RED", "error": {"status_code": exc.status_code, "detail": str(exc.detail)}}
    except Exception as exc:
        return {"blade": blade, "provider": provider, "status": "RED", "error": {"type": type(exc).__name__}}


@ROUTER.get("/status")
def assistance_status() -> dict[str, Any]:
    ready = _configured()
    google = google_assist.status()
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
        "models": {
            "openai_fast": remote_ai.OPENAI_FAST_MODEL,
            "openai_deep": remote_ai.OPENAI_MODEL,
            "google_fast": google["fast_model"],
            "google_deep": google["deep_model"],
            "google_api_live": google["api_key_live_model"],
            "huggingface_fast": remote_ai.HF_FAST_MODEL,
            "huggingface_deep": remote_ai.HF_MODEL,
        },
        "configured": ready,
        "direct_questions_bypass_mesh": True,
        "parallelism_max": MAX_PARALLEL,
        "github_resolution": "bounded_exact_sha_on_demand",
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
    message, resolved_context = _helper_message(req.message, context)
    calls = plan["calls"]

    if not calls:
        return {"ok": True, "context": context, "resolved_context": resolved_context, **plan, "helpers": [], "state": "NO_REMOTE_PROVIDER_CONFIGURED"}

    started = time.perf_counter()
    helpers: list[dict[str, Any]] = []
    if len(calls) == 1:
        helpers.append(_execute_call(calls[0], message, req.previous_response_id))
    else:
        workers = min(MAX_PARALLEL, len(calls))
        with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="luhm-assist") as pool:
            futures = {pool.submit(_execute_call, call, message, req.previous_response_id): call for call in calls}
            for future in as_completed(futures):
                helpers.append(future.result())
        order = {call["provider"]: index for index, call in enumerate(calls)}
        helpers.sort(key=lambda item: order.get(str(item.get("provider")), 99))

    return {
        "ok": not any(item.get("status") == "RED" for item in helpers),
        "context": context,
        "resolved_context": resolved_context,
        **plan,
        "helpers": helpers,
        "wall_latency_ms": round((time.perf_counter() - started) * 1000, 1),
        "silent_cross_provider_failover": False,
    }
