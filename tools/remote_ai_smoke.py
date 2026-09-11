#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "ultima" / "ollama-ffmpeg-antenna-v3" / "remote_ai.py"
SPEC = importlib.util.spec_from_file_location("kai_remote_ai", MODULE)
assert SPEC and SPEC.loader
remote_ai = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(remote_ai)


def run(provider: str) -> dict[str, object]:
    env = "OPENAI_API_KEY" if provider == "openai" else "HF_TOKEN"
    if not os.environ.get(env):
        return {"provider": provider, "status": "SKIPPED", "reason": f"{env} not configured"}

    started = time.monotonic()
    try:
        result = remote_ai._call_responses_api(
            provider,
            "Reply with exactly the word GREEN and no other text.",
            None,
        )
        latency_ms = round((time.monotonic() - started) * 1000)
        text = str(result.get("assistant", "")).strip()
        return {
            "provider": provider,
            "status": "GREEN" if text == "GREEN" else "YELLOW",
            "model": result.get("model"),
            "latency_ms": latency_ms,
            "response_id_present": bool(result.get("response_id")),
            "content_match": text == "GREEN",
            "secret_material_present": False,
        }
    except Exception as exc:
        return {
            "provider": provider,
            "status": "RED",
            "error_type": type(exc).__name__,
            "secret_material_present": False,
        }


def main() -> int:
    results = [run("openai"), run("huggingface")]
    print(json.dumps({"schema": "luhmos.remote-ai-smoke.v1", "results": results}, indent=2))
    return 1 if any(item["status"] == "RED" for item in results) else 0


if __name__ == "__main__":
    sys.exit(main())
