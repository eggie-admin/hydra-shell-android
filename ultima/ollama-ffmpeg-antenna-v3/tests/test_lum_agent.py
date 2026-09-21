from __future__ import annotations

import os
from unittest import mock

from fastapi.testclient import TestClient

from lum_agent.agent import LUM_AGENT_NAME, LUM_MODEL, build_lum_agent, run_lum
from lum_agent.doctrine import SKILLS, build_agent_instructions, load_skill
from lum_agent.router import ROUTER
from fastapi import FastAPI


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
    names = {getattr(item, "name", "") for item in agent.tools}
    assert {
        "list_lum_skills",
        "load_lum_skill",
        "read_source",
        "search_source",
        "python_outline",
        "python_compile",
        "propose_spell",
    }.issubset(names)


def test_no_key_is_deterministic_and_does_not_call_model() -> None:
    with mock.patch.dict(os.environ, {}, clear=True):
        result = run_lum("Explain the Python class layout")
    assert result["ok"] is True
    assert result["mode"] == "deterministic_mock"
    assert result["model"] is None
    assert result["execution"] == "NOT_EXECUTED"


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
    assert chat.status_code == 200
    assert chat.json()["mode"] == "deterministic_mock"
