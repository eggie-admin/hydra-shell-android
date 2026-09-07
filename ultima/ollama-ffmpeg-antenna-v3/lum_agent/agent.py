from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from agents import (
    Agent,
    Runner,
    SQLiteSession,
    set_default_openai_responses_transport,
    set_tracing_disabled,
)

from .doctrine import build_agent_instructions, list_skills
from .tools import LUM_TOOLS

LUM_AGENT_NAME = "KAI9000-Lum-InApp"
LUM_LUNA_MODEL = os.environ.get("LUM_OPENAI_MODEL", "gpt-5.6-luna")
LUM_SOL_MODEL = os.environ.get("LUM_OPENAI_SOL_MODEL", "gpt-5.6-sol")
# Backwards-compatible alias used by status/tests: the default model remains Luna.
LUM_MODEL = LUM_LUNA_MODEL
LUM_MAX_TURNS = min(max(int(os.environ.get("LUM_AGENT_MAX_TURNS", "8")), 1), 16)
LUM_TRANSPORT = os.environ.get("LUM_OPENAI_TRANSPORT", "websocket").strip().lower()
if LUM_TRANSPORT not in {"http", "websocket"}:
    LUM_TRANSPORT = "websocket"

LUM_SESSION_DB = os.environ.get(
    "KAI_LUM_SESSION_DB", "/tmp/kai9000-lum-sessions.sqlite3"
).strip()
SESSION_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]{1,64}$")

HEAVY_TASK_PATTERN = re.compile(
    r"\b(?:"
    r"deep research|architecture|architect|hard audit|10[- ]?pass|root cause|"
    r"complex debug|migration|dependency conflict|race condition|threat model|"
    r"security review|compile failure|build failure|system audit"
    r")\b",
    re.IGNORECASE,
)

# KAI prefers the Responses API websocket transport for persistent interactive
# Lum use. HTTP remains available through LUM_OPENAI_TRANSPORT=http.
set_default_openai_responses_transport(LUM_TRANSPORT)

# Source/code payloads may be sensitive even when they are not credentials. Keep
# OpenAI Agents tracing off unless the operator explicitly opts in at runtime.
set_tracing_disabled(os.environ.get("LUM_OPENAI_TRACING", "0") != "1")


def validate_session_id(session_id: str) -> str:
    value = session_id.strip()
    if not SESSION_ID_PATTERN.fullmatch(value):
        raise ValueError("session_id must be 1-64 characters: letters, numbers, dot, underscore, hyphen")
    return value


def _build_session(session_id: str) -> SQLiteSession:
    value = validate_session_id(session_id)
    if LUM_SESSION_DB != ":memory:":
        Path(LUM_SESSION_DB).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
    return SQLiteSession(value, LUM_SESSION_DB)


def route_lum_message(message: str) -> dict[str, str]:
    text = message.strip()
    lowered = text.lower()

    if lowered.startswith("/sol "):
        return {
            "model": LUM_SOL_MODEL,
            "reasoning_effort": "medium",
            "route": "explicit_sol",
            "message": text[5:].lstrip(),
        }

    if lowered.startswith("/luna "):
        return {
            "model": LUM_LUNA_MODEL,
            "reasoning_effort": "none",
            "route": "explicit_luna",
            "message": text[6:].lstrip(),
        }

    if HEAVY_TASK_PATTERN.search(text):
        return {
            "model": LUM_SOL_MODEL,
            "reasoning_effort": "medium",
            "route": "heavy_sol",
            "message": text,
        }

    return {
        "model": LUM_LUNA_MODEL,
        "reasoning_effort": "none",
        "route": "fast_luna",
        "message": text,
    }


def build_lum_agent(
    *, model: str | None = None, reasoning_effort: str = "none"
) -> Agent[Any]:
    return Agent(
        name=LUM_AGENT_NAME,
        instructions=build_agent_instructions(),
        model=model or LUM_LUNA_MODEL,
        model_settings={
            "reasoning": {"effort": reasoning_effort},
            "verbosity": "low",
            "store": False,
            "max_tokens": 2000,
            "parallel_tool_calls": True,
        },
        tools=LUM_TOOLS,
    )


def run_lum(message: str, *, session_id: str = "kai9000-default") -> dict[str, Any]:
    session_id = validate_session_id(session_id)
    route = route_lum_message(message)

    if not os.environ.get("OPENAI_API_KEY"):
        return {
            "ok": True,
            "mode": "deterministic_mock",
            "agent": LUM_AGENT_NAME,
            "model": None,
            "planned_model": route["model"],
            "reasoning_effort": route["reasoning_effort"],
            "route": route["route"],
            "transport": LUM_TRANSPORT,
            "session_id": session_id,
            "session_memory": "sqlite_when_openai_ready",
            "assistant": (
                "LuHm OS OpenAI credential is not available to this runtime. "
                "I can still expose doctrine, skills, inspection tools, and the deterministic "
                "spell compiler, but no OpenAI model call was made."
            ),
            "skills": [item["name"] for item in list_skills()],
            "execution": "NOT_EXECUTED",
        }

    agent = build_lum_agent(
        model=route["model"], reasoning_effort=route["reasoning_effort"]
    )
    session = _build_session(session_id)
    result = Runner.run_sync(
        agent,
        route["message"],
        max_turns=LUM_MAX_TURNS,
        session=session,
    )
    return {
        "ok": True,
        "mode": "openai_agents_sdk",
        "agent": LUM_AGENT_NAME,
        "model": route["model"],
        "reasoning_effort": route["reasoning_effort"],
        "route": route["route"],
        "transport": LUM_TRANSPORT,
        "session_id": session_id,
        "session_memory": "sqlite",
        "assistant": str(result.final_output or "").strip(),
        "last_agent": result.last_agent.name,
        "skills": [item["name"] for item in list_skills()],
        "execution": "AGENT_COMPLETED",
    }
