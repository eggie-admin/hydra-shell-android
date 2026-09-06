from __future__ import annotations

import json
import os
import shutil
import subprocess
from typing import Any

import httpx

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:3b")


class AntennaError(RuntimeError):
    pass


def _binary_version(name: str) -> dict[str, Any]:
    path = shutil.which(name)
    if not path:
        return {"ok": False, "path": None, "version": None}
    try:
        proc = subprocess.run(
            [path, "-version"],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
        first = (proc.stdout or proc.stderr).splitlines()[0]
        return {"ok": True, "path": path, "version": first}
    except Exception as exc:
        return {"ok": False, "path": path, "error": str(exc)}


def ollama_status(timeout: float = 4.0) -> dict[str, Any]:
    try:
        with httpx.Client(timeout=timeout) as client:
            r = client.get(f"{OLLAMA_URL}/api/tags")
            r.raise_for_status()
            data = r.json()
        models = [item.get("name") for item in data.get("models", []) if item.get("name")]
        return {
            "ok": True,
            "url": OLLAMA_URL,
            "default_model": OLLAMA_MODEL,
            "models": models,
        }
    except Exception as exc:
        return {
            "ok": False,
            "url": OLLAMA_URL,
            "default_model": OLLAMA_MODEL,
            "error": str(exc),
        }


def antenna_status() -> dict[str, Any]:
    return {
        "schema": "kai9000.local-antenna.v1",
        "ollama": ollama_status(),
        "ffmpeg": _binary_version("ffmpeg"),
        "ffprobe": _binary_version("ffprobe"),
        "policy": {
            "local_first": True,
            "ollama_loopback_default": True,
            "ffmpeg_local_binary": True,
            "github_is_source_remote_not_runtime_ai": True,
            "google_drive_is_backup_not_execution_plane": True,
        },
    }


def ollama_chat(message: str, model: str | None = None, timeout: float = 120.0) -> dict[str, Any]:
    chosen = model or OLLAMA_MODEL
    payload = {
        "model": chosen,
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are the local KAI 9000 antenna model. "
                    "Prefer concise technical planning. Never claim remote side effects."
                ),
            },
            {"role": "user", "content": message},
        ],
    }
    try:
        with httpx.Client(timeout=timeout) as client:
            r = client.post(f"{OLLAMA_URL}/api/chat", json=payload)
            r.raise_for_status()
            data = r.json()
        return {
            "ok": True,
            "model": chosen,
            "message": (data.get("message") or {}).get("content", ""),
            "raw": data,
        }
    except Exception as exc:
        raise AntennaError(str(exc)) from exc
