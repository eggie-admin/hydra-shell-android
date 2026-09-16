from __future__ import annotations

import os
from typing import Any

from agents import Agent, Runner, set_tracing_disabled

from .doctrine import list_skills
from .mesh import MESH_SPEC, build_boss_instructions, build_boss_tools, route_hint

LUM_AGENT_NAME = "KAI9000-Lum-Boss"
LUM_MODEL = os.environ.get("LUM_OPENAI_MODEL", "gpt-5.6-luna")
LUM_MAX_TURNS = min(max(int(os.environ.get("LUM_AGENT_MAX_TURNS", "6")), 1), 12)

# Source/code payloads may be sensitive even when they are not credentials. Keep
# OpenAI Agents tracing off unless the operator explicitly opts in at runtime.
set_tracing_disabled(os.environ.get("LUM_OPENAI_TRACING", "0") != "1")


def build_lum_agent() -> Agent[Any]:
    return Agent(
        name=LUM_AGENT_NAME,
        instructions=build_boss_instructions(),
        model=LUM_MODEL,
        model_settings={
            "reasoning": {"effort": "none"},
            "verbosity": "low",
            "store": False,
            "max_tokens": 1800,
            "parallel_tool_calls": True,
        },
        tools=build_boss_tools(),
    )


def run_lum(message: str) -> dict[str, Any]:
    hint = route_hint(message)
    if not os.environ.get("OPENAI_API_KEY"):
        return {
            "ok": True,
            "mode": "deterministic_mock",
            "agent": LUM_AGENT_NAME,
            "model": None,
            "route_hint": hint,
            "mesh": {
                "topology": MESH_SPEC.topology,
                "delegation_depth": MESH_SPEC.delegation_depth,
                "helpers": [MESH_SPEC.context, MESH_SPEC.build, MESH_SPEC.critic],
            },
            "assistant": (
                "LuHm OS OpenAI credential is not available to this runtime. "
                "The bounded Lum Boss mesh is loaded, but no OpenAI model call was made."
            ),
            "skills": [item["name"] for item in list_skills()],
            "execution": "NOT_EXECUTED",
        }

    agent = build_lum_agent()
    routed_input = (
        f"ROUTE_HINT={hint}. Treat this as a cheap hint, not authority.\n"
        f"Professor message:\n{message}"
    )
    result = Runner.run_sync(agent, routed_input, max_turns=LUM_MAX_TURNS)
    return {
        "ok": True,
        "mode": "openai_agents_sdk_mesh",
        "agent": LUM_AGENT_NAME,
        "model": LUM_MODEL,
        "route_hint": hint,
        "assistant": str(result.final_output or "").strip(),
        "last_agent": result.last_agent.name,
        "skills": [item["name"] for item in list_skills()],
        "execution": "AGENT_COMPLETED",
    }
