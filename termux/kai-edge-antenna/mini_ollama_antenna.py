from __future__ import annotations

import os
import shutil
import subprocess
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

APP = FastAPI(title="KAI 9000 Mini Ollama Antenna", version="0.1.0")

LLAMA_CPP_URL = os.environ.get("KAI_LLAMA_CPP_URL", "http://127.0.0.1:8080").rstrip("/")
EDGE_GALLERY_PACKAGE = os.environ.get("KAI_EDGE_GALLERY_PACKAGE", "com.google.aiedge.gallery")
EDGE_GALLERY_MODEL = os.environ.get("KAI_EDGE_GALLERY_MODEL", "Gemma-4-E2B-it")
DEFAULT_MODEL = os.environ.get("KAI_LOCAL_MODEL_ALIAS", "kai-local")


class ChatMessage(BaseModel):
    role: str
    content: str


class OllamaChatRequest(BaseModel):
    model: str | None = None
    messages: list[ChatMessage] = Field(default_factory=list)
    stream: bool = False


class OpenAIChatRequest(BaseModel):
    model: str | None = None
    messages: list[ChatMessage] = Field(default_factory=list)
    stream: bool = False


def _loopback_only(url: str) -> bool:
    return url.startswith("http://127.0.0.1:") or url.startswith("http://localhost:")


def _package_probe() -> dict[str, Any]:
    commands = [
        ["cmd", "package", "list", "packages", EDGE_GALLERY_PACKAGE],
        ["pm", "list", "packages", EDGE_GALLERY_PACKAGE],
    ]
    for command in commands:
        binary = shutil.which(command[0])
        if not binary:
            continue
        try:
            proc = subprocess.run(
                [binary, *command[1:]],
                check=False,
                capture_output=True,
                text=True,
                timeout=5,
            )
            output = (proc.stdout or "") + (proc.stderr or "")
            if EDGE_GALLERY_PACKAGE in output:
                return {"state": "installed", "package": EDGE_GALLERY_PACKAGE, "probe": command[0]}
        except Exception:
            continue
    return {
        "state": "unknown",
        "package": EDGE_GALLERY_PACKAGE,
        "note": "Android package visibility may hide apps from an unprivileged Termux process.",
    }


def _llama_cpp_status(timeout: float = 2.0) -> dict[str, Any]:
    if not _loopback_only(LLAMA_CPP_URL):
        return {"ok": False, "url": LLAMA_CPP_URL, "error": "non_loopback_backend_rejected"}
    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.get(f"{LLAMA_CPP_URL}/v1/models")
            response.raise_for_status()
            data = response.json()
        models = [item.get("id") for item in data.get("data", []) if item.get("id")]
        return {"ok": True, "url": LLAMA_CPP_URL, "models": models}
    except Exception as exc:
        return {"ok": False, "url": LLAMA_CPP_URL, "error": str(exc)}


def _status() -> dict[str, Any]:
    llama = _llama_cpp_status()
    return {
        "schema": "kai9000.mini-ollama-antenna.v1",
        "service_ok": True,
        "bridge_state": "green" if llama.get("ok") else "yellow",
        "callable_backend": bool(llama.get("ok")),
        "default_model_alias": DEFAULT_MODEL,
        "llama_cpp": llama,
        "edge_gallery": {
            **_package_probe(),
            "mode": "manual_sandbox_runtime",
            "preferred_model": EDGE_GALLERY_MODEL,
            "http_api_assumed": False,
        },
        "policy": {
            "loopback_only": True,
            "no_remote_model_fallback": True,
            "edge_gallery_not_remote_controlled": True,
            "secure_folder_is_client_not_daemon_owner": True,
        },
    }


def _messages(messages: list[ChatMessage]) -> list[dict[str, str]]:
    clean: list[dict[str, str]] = []
    for item in messages:
        role = item.role.strip().lower()
        if role not in {"system", "user", "assistant"}:
            raise HTTPException(status_code=400, detail="unsupported_role")
        content = item.content.strip()
        if not content:
            continue
        clean.append({"role": role, "content": content})
    if not clean:
        raise HTTPException(status_code=400, detail="empty_messages")
    return clean


def _chat(messages: list[ChatMessage], requested_model: str | None) -> dict[str, Any]:
    status = _llama_cpp_status()
    if not status.get("ok"):
        raise HTTPException(
            status_code=503,
            detail={
                "error": "no_callable_local_backend",
                "edge_gallery": "manual_only",
                "next": "Start a loopback llama.cpp server or use Edge Gallery manually.",
            },
        )
    payload = {
        "model": requested_model or (status.get("models") or [DEFAULT_MODEL])[0],
        "messages": _messages(messages),
        "stream": False,
    }
    try:
        with httpx.Client(timeout=120.0) as client:
            response = client.post(f"{LLAMA_CPP_URL}/v1/chat/completions", json=payload)
            response.raise_for_status()
            return response.json()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"local_backend_error:{exc}") from exc


@APP.get("/health")
def health() -> dict[str, Any]:
    return _status()


@APP.get("/api/version")
def ollama_version() -> dict[str, str]:
    return {"version": "kai-mini-ollama-0.1.0"}


@APP.get("/api/tags")
def ollama_tags() -> dict[str, Any]:
    status = _status()
    llama_models = status["llama_cpp"].get("models", []) if status["callable_backend"] else []
    return {
        "models": [{"name": model, "model": model} for model in llama_models],
        "bridge_state": status["bridge_state"],
        "callable_backend": status["callable_backend"],
        "edge_gallery": status["edge_gallery"],
    }


@APP.post("/api/chat")
def ollama_chat(request: OllamaChatRequest) -> dict[str, Any]:
    if request.stream:
        raise HTTPException(status_code=400, detail="streaming_not_supported_by_mini_antenna")
    data = _chat(request.messages, request.model)
    choice = (data.get("choices") or [{}])[0]
    message = choice.get("message") or {}
    return {
        "model": request.model or DEFAULT_MODEL,
        "message": {"role": "assistant", "content": message.get("content", "")},
        "done": True,
        "backend": "llama.cpp",
    }


@APP.post("/v1/chat/completions")
def openai_chat(request: OpenAIChatRequest) -> dict[str, Any]:
    if request.stream:
        raise HTTPException(status_code=400, detail="streaming_not_supported_by_mini_antenna")
    return _chat(request.messages, request.model)
