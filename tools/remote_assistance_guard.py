#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REMOTE = ROOT / "ultima/ollama-ffmpeg-antenna-v3/remote_ai.py"
ASSIST = ROOT / "ultima/ollama-ffmpeg-antenna-v3/assistance.py"
SERVER = ROOT / "ultima/ollama-ffmpeg-antenna-v3/magic_server.py"


def require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(f"REMOTE_ASSISTANCE_RED: {message}")


def main() -> None:
    remote = REMOTE.read_text(encoding="utf-8")
    assist = ASSIST.read_text(encoding="utf-8")
    server = SERVER.read_text(encoding="utf-8")

    for needle in (
        'OPENAI_FAST_MODEL = os.environ.get("OPENAI_FAST_MODEL", "gpt-5.6-luna")',
        'OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-5.6-sol")',
        'HF_FAST_MODEL = os.environ.get("HF_FAST_MODEL", "openai/gpt-oss-20b:fastest")',
        "httpx.Client(",
        "max_keepalive_connections=16",
        "previous_response_id",
        '"connection_pool": "keepalive"',
    ):
        require(needle in remote, f"remote fastpath drift: {needle}")

    require("gpt-6-astra" not in remote, "retired OpenAI model resurrected in active remote router")

    for needle in (
        "MAX_PARALLEL = 3",
        '"context": "github_evidence_by_reference"',
        '"build": "openai"',
        '"research": "google"',
        '"critic": "huggingface_conditional"',
        "if task == \"direct\":",
        "ThreadPoolExecutor(max_workers=workers",
        '"execution": "advisory_only"',
        '"crown_gate": True',
        '"silent_cross_provider_failover": False',
    ):
        require(needle in assist, f"assistance mesh drift: {needle}")

    require("MAX_GITHUB_REFS = 12" in assist, "GitHub context budget drift")
    require("evidence_by_reference_not_full_history_copy" in assist, "GitHub evidence-copy policy drift")

    fast_pos = server.find('os.environ.setdefault("OPENAI_FAST_MODEL", "gpt-5.6-luna")')
    deep_pos = server.find('os.environ.setdefault("OPENAI_MODEL", "gpt-5.6-sol")')
    magic_import = server.find("from magic_chat import ROUTER as MAGIC_ROUTER")
    require(fast_pos >= 0 and deep_pos >= 0 and magic_import >= 0, "server model/bootstrap contract missing")
    require(fast_pos < magic_import and deep_pos < magic_import, "model defaults must be fixed before compatibility imports")
    require("from assistance import ROUTER as ASSISTANCE_ROUTER" in server, "assistance router not mounted")
    require("APP.include_router(ASSISTANCE_ROUTER)" in server, "assistance endpoint not active")
    require('APP.title = "LuHm OS Remote Assistance Cockpit"' in server, "runtime branding drift")

    print("LUHM OS REMOTE ASSISTANCE FASTPATH GREEN")


if __name__ == "__main__":
    main()
