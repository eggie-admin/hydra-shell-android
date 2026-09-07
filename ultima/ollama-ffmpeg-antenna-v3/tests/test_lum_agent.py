from __future__ import annotations

import os
from unittest import mock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from lum_agent.agent import (
    LUM_AGENT_NAME,
    LUM_LUNA_MODEL,
    LUM_MODEL,
    LUM_SOL_MODEL,
    LUM_TRANSPORT,
    build_lum_agent,
    route_lum_message,
    run_lum,
)
from lum_agent.doctrine import SKILLS, build_agent_instructions, load_skill
from lum_agent.router import ROUTER


def test_skill_registry_contains_python_and_provider_chain() -> None:
    assert "prime" in SKILLS
    assert "source-of-truth" in SKILLS
    assert "openai-router" in SKILLS
    assert "huggingface-forge" in SKILLS
    assert "python-core" in SKILLS
    assert "python-debug" in SKILLS
    assert SKILLS["python-core"].default_for_python is True
    assert SKILLS["python-debug"].default_for_python is True


def test_doctrine_files_are_loadable() -> None:
    assert "composition before inheritance" in load_skill("python-core")
    assert "reproduction" in load_skill("python-debug").lower()
    assert "deterministic application" in load_skill("prime").lower()
    assert "Professor" in load_skill("source-of-truth")
    assert "gpt-5.6-luna" in load_skill("openai-router")
    assert "trust_remote_code=false" in load_skill("huggingface-forge")


def test_agent_instructions_lock_authority_python_and_source_of_truth() -> None:
    instructions = build_agent_instructions()
    assert "default coding language is Python 3" in instructions
    assert "may not self-authorize" in instructions
    assert "DOCTRINE -> INSPECT" in instructions
    assert "human approval" in instructions.lower()
    assert "Professor holds the crown" in instructions
    assert "Hugging Face is a Forge" in instructions


def test_fast_default_model_and_tool_inventory() -> None:
    agent = build_lum_agent()
    assert LUM_AGENT_NAME == "KAI9000-Lum-InApp"
    assert LUM_MODEL == "gpt-5.6-luna"
    assert LUM_LUNA_MODEL == "gpt-5.6-luna"
    assert LUM_SOL_MODEL == "gpt-5.6-sol"
    assert LUM_TRANSPORT in {"http", "websocket"}
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


def test_luna_sol_routing_contract() -> None:
    fast = route_lum_message("Explain this Python function")
    assert fast["model"] == "gpt-5.6-luna"
    assert fast["reasoning_effort"] == "none"
    assert fast["route"] == "fast_luna"

    heavy = route_lum_message("Run a hard audit of this architecture")
    assert heavy["model"] == "gpt-5.6-sol"
    assert heavy["reasoning_effort"] == "medium"
    assert heavy["route"] == "heavy_sol"

    forced_luna = route_lum_message("/luna hard audit this architecture")
    assert forced_luna["model"] == "gpt-5.6-luna"
    assert forced_luna["route"] == "explicit_luna"

    forced_sol = route_lum_message("/sol summarize this file")
    assert forced_sol["model"] == "gpt-5.6-sol"
    assert forced_sol["route"] == "explicit_sol"


def test_no_key_is_deterministic_and_does_not_call_model() -> None:
    with mock.patch.dict(os.environ, {}, clear=True):
        result = run_lum("Run a hard audit of the Python architecture")
    assert result["ok"] is True
    assert result["mode"] == "deterministic_mock"
    assert result["model"] is None
    assert result["planned_model"] == "gpt-5.6-sol"
    assert result["reasoning_effort"] == "medium"
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
    assert status_json["default_model"] == "gpt-5.6-luna"
    assert status_json["heavy_model"] == "gpt-5.6-sol"
    assert status_json["credential_exposed_to_client"] is False
    assert status_json["self_approval"] is False
    assert status_json["silent_cross_provider_failover"] is False
    assert "huggingface-forge" in status_json["skills"]
    assert chat.status_code == 200
    assert chat.json()["mode"] == "deterministic_mock"
