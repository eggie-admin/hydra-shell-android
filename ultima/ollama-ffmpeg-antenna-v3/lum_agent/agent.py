from __future__ import annotations

import hashlib
import os
from typing import Any

from agents import Agent, Runner, set_tracing_disabled

from .doctrine import (
    build_agent_instructions,
    build_mini_agent_instructions,
    list_skills,
)
from .tools import LUM_TOOLS, MINI_TOOLS

LUM_AGENT_NAME = "KAI9000-Lum"
LUM_LEGACY_AGENT_NAME = "KAI9000-Lum-InApp"
LUM_MODEL = os.environ.get("LUM_OPENAI_MODEL", "gpt-6-astra")
LUM_MINI_AGENT_NAME = "KAI9000-Lum-Mini"
LUM_MINI_MODEL = os.environ.get("LUM_MINI_MODEL", "gpt-5.6-luna")
LUM_MAX_TURNS = min(max(int(os.environ.get("LUM_AGENT_MAX_TURNS", "10")), 1), 16)
LUM_MINI_MAX_TURNS = min(max(int(os.environ.get("LUM_MINI_MAX_TURNS", "4")), 1), 6)

# Source/code payloads may be sensitive even when they are not credentials. Keep
# OpenAI Agents tracing off unless the operator explicitly opts in at runtime.
set_tracing_disabled(os.environ.get("LUM_OPENAI_TRACING", "0") != "1")


def _instruction_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_lum_mini_agent() -> Agent[Any]:
    return Agent(
        name=LUM_MINI_AGENT_NAME,
        instructions=build_mini_agent_instructions(),
        model=LUM_MINI_MODEL,
        model_settings={
            "reasoning": {"effort": "none"},
            "verbosity": "low",
            "store": False,
            "max_tokens": 1200,
            "parallel_tool_calls": False,
        },
        tools=MINI_TOOLS,
    )


def build_lum_agent() -> Agent[Any]:
    mini = build_lum_mini_agent()
    mini_tool = mini.as_tool(
        tool_name="delegate_to_lum_mini",
        tool_description=(
            "Delegate one bounded read-only repository reconnaissance task. "
            "The helper cannot mutate, approve, publish, use shell, or create subagents."
        ),
        max_turns=LUM_MINI_MAX_TURNS,
        needs_approval=False,
    )
    return Agent(
        name=LUM_AGENT_NAME,
        instructions=build_agent_instructions(),
        model=LUM_MODEL,
        model_settings={
            "reasoning": {"effort": os.environ.get("LUM_REASONING_EFFORT", "medium")},
            "verbosity": "low",
            "store": False,
            "max_tokens": 2400,
            "parallel_tool_calls": False,
        },
        tools=[*LUM_TOOLS, mini_tool],
    )


def _audit_receipt(*, execution: str, resolved_model: str | None) -> dict[str, Any]:
    instructions = build_agent_instructions()
    return {
        "schema": "luhmos.lum-agent-receipt.v1",
        "agent": LUM_AGENT_NAME,
        "helper_agent": LUM_MINI_AGENT_NAME,
        "configured_model": LUM_MODEL,
        "helper_model": LUM_MINI_MODEL,
        "resolved_model": resolved_model,
        "instruction_sha256": _instruction_hash(instructions),
        "delegation_policy": "COGNITION_ONLY_NOT_AUTHORITY",
        "arbitrary_shell": False,
        "write_authority": False,
        "mcp_write": False,
        "tracing_default": False,
        "secret_material_present": False,
        "execution": execution,
    }


def run_lum(message: str) -> dict[str, Any]:
    if not os.environ.get("OPENAI_API_KEY"):
        return {
            "ok": True,
            "mode": "deterministic_mock",
            "agent": LUM_AGENT_NAME,
            "legacy_agent_alias": LUM_LEGACY_AGENT_NAME,
            "model": None,
            "configured_model": LUM_MODEL,
            "helper_agent": LUM_MINI_AGENT_NAME,
            "helper_model": LUM_MINI_MODEL,
            "assistant": (
                "LuHm OS OpenAI credential is not available to this runtime. "
                "The hardened Lum/Astra agent stack is configured, but no OpenAI model call was made."
            ),
            "skills": [item["name"] for item in list_skills()],
            "execution": "NOT_EXECUTED",
            "audit_receipt": _audit_receipt(execution="NOT_EXECUTED", resolved_model=None),
        }

    agent = build_lum_agent()
    result = Runner.run_sync(agent, message, max_turns=LUM_MAX_TURNS)
    return {
        "ok": True,
        "mode": "openai_agents_sdk",
        "agent": LUM_AGENT_NAME,
        "legacy_agent_alias": LUM_LEGACY_AGENT_NAME,
        "model": LUM_MODEL,
        "helper_agent": LUM_MINI_AGENT_NAME,
        "helper_model": LUM_MINI_MODEL,
        "assistant": str(result.final_output or "").strip(),
        "last_agent": result.last_agent.name,
        "skills": [item["name"] for item in list_skills()],
        "execution": "AGENT_COMPLETED",
        "audit_receipt": _audit_receipt(execution="AGENT_COMPLETED", resolved_model=LUM_MODEL),
    }
