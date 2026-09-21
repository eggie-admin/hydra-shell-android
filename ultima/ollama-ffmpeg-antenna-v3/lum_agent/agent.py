from __future__ import annotations

import os
from typing import Any

from agents import Agent, Runner, set_tracing_disabled

from .doctrine import build_agent_instructions, list_skills
from .tools import LUM_TOOLS

LUM_AGENT_NAME = "KAI9000-Lum-InApp"
LUM_MODEL = os.environ.get("LUM_OPENAI_MODEL", "gpt-5.6-luna")
LUM_MAX_TURNS = min(max(int(os.environ.get("LUM_AGENT_MAX_TURNS", "8")), 1), 16)

# Source/code payloads may be sensitive even when they are not credentials. Keep
# OpenAI Agents tracing off unless the operator explicitly opts in at runtime.
set_tracing_disabled(os.environ.get("LUM_OPENAI_TRACING", "0") != "1")


def build_lum_agent() -> Agent[Any]:
    return Agent(
        name=LUM_AGENT_NAME,
        instructions=build_agent_instructions(),
        model=LUM_MODEL,
        model_settings={
            "reasoning": {"effort": "none"},
            "verbosity": "low",
            "store": False,
            "max_tokens": 2000,
            "parallel_tool_calls": True,
        },
        tools=LUM_TOOLS,
    )


def run_lum(message: str) -> dict[str, Any]:
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

    agent = build_lum_agent()
    result = Runner.run_sync(agent, message, max_turns=LUM_MAX_TURNS)
    return {
        "ok": True,
        "mode": "openai_agents_sdk",
        "agent": LUM_AGENT_NAME,
        "model": LUM_MODEL,
        "assistant": str(result.final_output or "").strip(),
        "last_agent": result.last_agent.name,
        "skills": [item["name"] for item in list_skills()],
        "execution": "AGENT_COMPLETED",
    }
