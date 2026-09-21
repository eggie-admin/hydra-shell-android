from __future__ import annotations

import os
from unittest import mock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from lum_agent.agent import LUM_AGENT_NAME, LUM_MODEL, build_lum_agent, run_lum
from lum_agent.astra import (
    CRITIC_ROLE,
    DEFAULT_ONI_ROLES,
    MAX_DELEGATION_DEPTH,
    MAX_PARALLEL_HELPERS,
    ONI_READ_TOOL_NAMES,
    astra_roles_for_message,
    build_oni_agent,
)
from lum_agent.doctrine import SKILLS, build_agent_instructions, load_skill
from lum_agent.router import ROUTER


def _tool_names(agent) -> set[str]:
    return {getattr(item, "name", "") for item in agent.tools}


def _oni_tool_names(agent) -> set[str]:
    return {name for name in _tool_names(agent) if name.startswith("oni_")}


def test_skill_registry_contains_python_chain() -> None:
    assert "prime" in SKILLS
    assert "python-core" in SKILLS
    assert "python-debug" in SKILLS
    assert SKILLS["python-core"].default_for_python is True
    assert SKILLS["python-debug"].default_for_python is True


def test_doctrine_files_are_loadable() -> None:
    assert "composition before inheritance" in load_skill("python-core")
    assert "reproduction" in load_skill("python-debug").lower()
    assert "deterministic application" in load_skill("prime").lower()


def test_agent_instructions_lock_authority_and_python() -> None:
    instructions = build_agent_instructions()
    assert "default coding language is Python 3" in instructions
    assert "may not self-authorize" in instructions
    assert "DOCTRINE -> INSPECT" in instructions
    assert "human approval" in instructions.lower()


def test_fast_default_model_and_tool_inventory() -> None:
    agent = build_lum_agent()
    assert LUM_AGENT_NAME == "KAI9000-Lum-InApp"
    assert LUM_MODEL == "gpt-5.6-luna"
    assert agent.model == "gpt-5.6-luna"
    names = _tool_names(agent)
    assert {
        "list_lum_skills",
        "load_lum_skill",
        "read_source",
        "search_source",
        "python_outline",
        "python_compile",
        "propose_spell",
    }.issubset(names)
    assert _oni_tool_names(agent) == {"oni_context", "oni_build", "oni_research"}


def test_astra_default_mesh_is_bounded_to_three_helpers() -> None:
    assert DEFAULT_ONI_ROLES == ("Context", "Build", "Research")
    assert MAX_PARALLEL_HELPERS == 3
    assert MAX_DELEGATION_DEPTH == 1
    roles = astra_roles_for_message("inspect this implementation")
    assert roles == DEFAULT_ONI_ROLES
    assert len(roles) <= MAX_PARALLEL_HELPERS


def test_critic_is_conditional_and_replaces_one_default_role() -> None:
    normal = build_lum_agent("inspect this implementation")
    critical = build_lum_agent("perform a security audit of this release architecture")
    assert "oni_critic" not in _oni_tool_names(normal)
    assert "oni_critic" in _oni_tool_names(critical)
    assert len(_oni_tool_names(critical)) == MAX_PARALLEL_HELPERS
    assert CRITIC_ROLE in astra_roles_for_message("security audit")


def test_oni_helpers_are_read_only_and_cannot_recruit() -> None:
    assert ONI_READ_TOOL_NAMES == {"read_source", "search_source", "python_outline"}
    for role in (*DEFAULT_ONI_ROLES, CRITIC_ROLE):
        helper = build_oni_agent(role)
        names = _tool_names(helper)
        assert names == ONI_READ_TOOL_NAMES
        assert "python_compile" not in names
        assert "propose_spell" not in names
        assert not any(name.startswith("oni_") for name in names)


def test_lum_remains_single_boss_in_manager_instructions() -> None:
    agent = build_lum_agent("security audit")
    instructions = str(agent.instructions)
    assert "Lum remains the single Boss" in instructions
    assert "cannot recruit other helpers" in instructions
    assert "ASTRA" in instructions


def test_no_key_is_deterministic_and_does_not_call_model() -> None:
    with mock.patch.dict(os.environ, {}, clear=True):
        result = run_lum("Explain the Python class layout")
    assert result["ok"] is True
    assert result["mode"] == "deterministic_mock"
    assert result["model"] is None
    assert result["execution"] == "NOT_EXECUTED"
    assert result["single_boss"] is True
    assert result["astra"]["max_parallel_helpers"] == 3
    assert result["astra"]["recursive_recruitment"] is False


def test_lum_router_status_and_no_key_chat() -> None:
    app = FastAPI()
    app.include_router(ROUTER)
    client = TestClient(app)
    with mock.patch.dict(os.environ, {}, clear=True):
        status = client.get("/api/lum/status")
        chat = client.post("/api/lum/chat", json={"message": "inspect Python doctrine"})
    assert status.status_code == 200
    status_json = status.json()
    assert status_json["agent"] == "KAI9000-Lum-InApp"
    assert status_json["credential_exposed_to_client"] is False
    assert status_json["self_approval"] is False
    assert status_json["single_boss"] is True
    assert status_json["astra"]["active_roles"] == ["Context", "Build", "Research"]
    assert status_json["astra"]["max_delegation_depth"] == 1
    assert chat.status_code == 200
    chat_json = chat.json()
    assert chat_json["mode"] == "deterministic_mock"
    assert chat_json["single_boss"] is True
