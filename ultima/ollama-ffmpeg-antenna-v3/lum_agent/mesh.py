from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from agents import Agent

from .doctrine import build_agent_instructions
from .tools import (
    list_lum_skills,
    load_lum_skill,
    propose_spell,
    python_compile,
    python_outline,
    read_source,
    search_source,
)

HELPER_MODEL = os.environ.get("LUM_HELPER_MODEL", os.environ.get("LUM_OPENAI_MODEL", "gpt-5.6-luna"))
HELPER_MAX_TURNS = min(max(int(os.environ.get("LUM_HELPER_MAX_TURNS", "2")), 1), 4)
MAX_HELPERS_PER_TURN = min(max(int(os.environ.get("LUM_MAX_HELPERS_PER_TURN", "2")), 1), 3)


@dataclass(frozen=True, slots=True)
class MeshSpec:
    boss: str = "KAI9000-Lum-Boss"
    context: str = "Lum-Context-Blade"
    build: str = "Lum-Build-Blade"
    critic: str = "Lum-Critic-Blade"
    topology: str = "hub-and-spoke"
    delegation_depth: int = 1


MESH_SPEC = MeshSpec()


def _fast_settings(max_tokens: int) -> dict[str, Any]:
    return {
        "reasoning": {"effort": "none"},
        "verbosity": "low",
        "store": False,
        "max_tokens": max_tokens,
        "parallel_tool_calls": True,
    }


def route_hint(message: str) -> str:
    """Cheap deterministic hint. It never authorizes an action."""
    text = message.casefold()
    if any(word in text for word in ("build", "compile", "test", "python", "code", "patch", "repo")):
        return "build"
    if any(word in text for word in ("verify", "audit", "sanity", "risk", "contradiction", "review")):
        return "critic"
    if any(word in text for word in ("doctrine", "source of truth", "context", "history", "file", "where")):
        return "context"
    return "direct"


def build_context_blade() -> Agent[Any]:
    return Agent(
        name=MESH_SPEC.context,
        instructions=(
            "You are Lum's context blade. Solve only bounded retrieval and evidence tasks. "
            "Use read/search/doctrine tools only when needed. Return compact facts with provenance. "
            "Do not write files, execute mutations, recruit other agents, or answer the Professor directly."
        ),
        model=HELPER_MODEL,
        model_settings=_fast_settings(900),
        tools=[list_lum_skills, load_lum_skill, read_source, search_source],
    )


def build_build_blade() -> Agent[Any]:
    return Agent(
        name=MESH_SPEC.build,
        instructions=(
            "You are Lum's build blade. Inspect source, outline Python, compile individual files, "
            "and produce a terse implementation/test recommendation. Never self-authorize mutation, "
            "never run arbitrary shell, never publish, and never recruit another agent."
        ),
        model=HELPER_MODEL,
        model_settings=_fast_settings(1100),
        tools=[read_source, search_source, python_outline, python_compile, propose_spell],
    )


def build_critic_blade() -> Agent[Any]:
    return Agent(
        name=MESH_SPEC.critic,
        instructions=(
            "You are Lum's critic blade. Check one proposed claim or plan for stale evidence, "
            "authority drift, missing tests, unsafe side effects, or unsupported completion claims. "
            "Be concise. Do not execute, publish, mutate, or recruit another agent."
        ),
        model=HELPER_MODEL,
        model_settings=_fast_settings(800),
        tools=[load_lum_skill, read_source, search_source],
    )


def build_boss_tools() -> list[Any]:
    context = build_context_blade()
    build = build_build_blade()
    critic = build_critic_blade()
    return [
        context.as_tool(
            tool_name="ask_context_blade",
            tool_description="Retrieve only the minimum doctrine/source context needed for this turn.",
            max_turns=HELPER_MAX_TURNS,
        ),
        build.as_tool(
            tool_name="ask_build_blade",
            tool_description="Inspect or compile bounded code/build evidence and return a terse recommendation.",
            max_turns=HELPER_MAX_TURNS,
        ),
        critic.as_tool(
            tool_name="ask_critic_blade",
            tool_description="Critique a proposed claim or action when verification materially reduces risk.",
            max_turns=HELPER_MAX_TURNS,
        ),
        propose_spell,
    ]


def build_boss_instructions() -> str:
    return (
        build_agent_instructions()
        + "\n\nLUHM BOSS MESH V1:\n"
        + "You alone own the user-facing answer. Helpers are disposable bounded tools, not peers.\n"
        + f"Topology: {MESH_SPEC.topology}; delegation depth={MESH_SPEC.delegation_depth}; "
          f"helper budget={MAX_HELPERS_PER_TURN}.\n"
        + "Default to zero helpers for simple chat. Use one helper for a focused evidence task. "
          "Use two only when independent subtasks materially reduce latency or uncertainty. "
          "Never call all helpers by default. Never let a helper authorize or execute a mutation. "
          "For consequential actions, use critic evidence before proposing the deterministic approval gateway. "
          "Do not expose internal helper chatter. Synthesize one compact answer."
    )
