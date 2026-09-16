from __future__ import annotations

import os
from typing import Any

from agents import Agent, Runner, set_tracing_disabled

from .doctrine import build_agent_instructions, list_skills
from .tools import LUM_TOOLS

LUM_AGENT_NAME = "KAI9000-Lum-InApp"
LUM_FAST_MODEL = os.environ.get(
    "LUM_OPENAI_MODEL_FAST",
    os.environ.get("LUM_OPENAI_MODEL", "gpt-5.6-luna"),
)
LUM_DEEP_MODEL = os.environ.get("LUM_OPENAI_MODEL_DEEP", "gpt-5.6-sol")
# Backward-compatible export used by the existing status surface.
LUM_MODEL = LUM_FAST_MODEL
LUM_MAX_TURNS = min(max(int(os.environ.get("LUM_AGENT_MAX_TURNS", "8")), 1), 16)

# Source/code payloads may be sensitive even when they are not credentials. Keep
# OpenAI Agents tracing off unless the operator explicitly opts in at runtime.
set_tracing_disabled(os.environ.get("LUM_OPENAI_TRACING", "0") != "1")


def build_lum_agent(
    *,
    model: str | None = None,
    reasoning_effort: str | None = None,
) -> Agent[Any]:
    resolved_model = model or LUM_FAST_MODEL
    resolved_effort = reasoning_effort or (
        "medium" if resolved_model == LUM_DEEP_MODEL else "none"
    )
    return Agent(
        name=LUM_AGENT_NAME,
        instructions=build_agent_instructions(),
        model=resolved_model,
        model_settings={
            "reasoning": {"effort": resolved_effort},
            "verbosity": "low",
            "store": False,
            "max_tokens": 2000,
            "parallel_tool_calls": True,
        },
        tools=LUM_TOOLS,
    )


def run_lum(
    message: str,
    *,
    model: str | None = None,
    reasoning_effort: str | None = None,
    max_turns: int | None = None,
) -> dict[str, Any]:
    resolved_model = model or LUM_FAST_MODEL
    resolved_turns = LUM_MAX_TURNS if max_turns is None else min(max(max_turns, 1), 16)

    if not os.environ.get("OPENAI_API_KEY"):
        return {
            "ok": True,
            "mode": "deterministic_mock",
            "agent": LUM_AGENT_NAME,
            "model": None,
            "assistant": (
                "LuHm OS OpenAI credential is not available to this runtime. "
                "I can still expose the doctrine index and deterministic spell compiler, "
                "but no OpenAI model call was made."
            ),
            "skills": [item["name"] for item in list_skills()],
            "execution": "NOT_EXECUTED",
        }

    agent = build_lum_agent(
        model=resolved_model,
        reasoning_effort=reasoning_effort,
    )
    result = Runner.run_sync(agent, message, max_turns=resolved_turns)
    return {
        "ok": True,
        "mode": "openai_agents_sdk",
        "agent": LUM_AGENT_NAME,
        "model": resolved_model,
        "assistant": str(result.final_output or "").strip(),
        "last_agent": result.last_agent.name,
        "skills": [item["name"] for item in list_skills()],
        "execution": "AGENT_COMPLETED",
    }
