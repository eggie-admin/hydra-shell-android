from __future__ import annotations

import os
from unittest import mock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from lum_agent.agent import (
    LUM_AGENT_NAME,
    LUM_MINI_AGENT_NAME,
    LUM_MINI_MODEL,
    LUM_MODEL,
    build_lum_agent,
    build_lum_mini_agent,
    run_lum,
)
from lum_agent.doctrine import SKILLS, build_agent_instructions, build_mini_agent_instructions, load_skill
from lum_agent.router import ROUTER


def test_skill_registry_contains_python_and_audit_chain() -> None:
    assert "prime" in SKILLS
    assert "python-core" in SKILLS
    assert "python-debug" in SKILLS
    assert "source-of-truth-audit" in SKILLS
    assert "doctrine-drift" in SKILLS
    assert "enterprise-security" in SKILLS
    assert "build-evidence" in SKILLS
    assert "mini-recon" in SKILLS
    assert "rollback-planner" in SKILLS
    assert SKILLS["python-core"].default_for_python is True
    assert SKILLS["mini-recon"].mini_allowed is True
    assert SKILLS["enterprise-security"].mini_allowed is False


def test_doctrine_files_are_loadable() -> None:
    assert "composition before inheritance" in load_skill("python-core")
    assert "reproduction" in load_skill("python-debug").lower()
    assert "deterministic application" in load_skill("prime").lower()
    assert "delegate" in load_skill("enterprise-security").lower()
    assert "read-only" in load_skill("mini-recon").lower()


def test_agent_instructions_lock_authority_personality_and_workflow() -> None:
    instructions = build_agent_instructions()
    assert "default Python doctrine" in instructions
    assert "may not self-authorize" in instructions
    assert "delegate cognition" in instructions
    assert "may NOT delegate authority" in instructions
    assert "BLOCKING POLICY/GUARDRAILS" in instructions
    assert "Never invent GREEN" in instructions
    assert "human approval" in instructions.lower()

    mini = build_mini_agent_instructions()
    assert "read-only reconnaissance helper" in mini
    assert "may not write files" in mini.lower()
    assert "delegates nothing" in mini


def test_astra_primary_and_luna_mini_inventory() -> None:
    agent = build_lum_agent()
    mini = build_lum_mini_agent()
    assert LUM_AGENT_NAME == "KAI9000-Lum"
    assert LUM_MODEL == "gpt-6-astra"
    assert LUM_MINI_AGENT_NAME == "KAI9000-Lum-Mini"
    assert LUM_MINI_MODEL == "gpt-5.6-luna"
    assert agent.model == "gpt-6-astra"
    assert mini.model == "gpt-5.6-luna"

    primary_names = {getattr(item, "name", "") for item in agent.tools}
    assert {
        "list_lum_skills",
        "load_lum_skill",
        "read_source",
        "search_source",
        "python_outline",
        "python_compile",
        "propose_spell",
        "delegate_to_lum_mini",
    }.issubset(primary_names)

    mini_names = {getattr(item, "name", "") for item in mini.tools}
    assert mini_names == {
        "list_lum_skills",
        "load_lum_skill",
        "read_source",
        "search_source",
        "python_outline",
    }
    assert "python_compile" not in mini_names
    assert "propose_spell" not in mini_names
    assert "delegate_to_lum_mini" not in mini_names


def test_no_key_is_deterministic_and_emits_receipt_without_model_call() -> None:
    with mock.patch.dict(os.environ, {}, clear=True):
        result = run_lum("Explain the Python class layout")
    assert result["ok"] is True
    assert result["mode"] == "deterministic_mock"
    assert result["agent"] == "KAI9000-Lum"
    assert result["model"] is None
    assert result["configured_model"] == "gpt-6-astra"
    assert result["helper_agent"] == "KAI9000-Lum-Mini"
    assert result["execution"] == "NOT_EXECUTED"
    receipt = result["audit_receipt"]
    assert receipt["delegation_policy"] == "COGNITION_ONLY_NOT_AUTHORITY"
    assert receipt["arbitrary_shell"] is False
    assert receipt["write_authority"] is False
    assert receipt["mcp_write"] is False
    assert receipt["secret_material_present"] is False
    assert len(receipt["instruction_sha256"]) == 64


def test_lum_router_status_and_no_key_chat() -> None:
    app = FastAPI()
    app.include_router(ROUTER)
    client = TestClient(app)
    with mock.patch.dict(os.environ, {}, clear=True):
        status = client.get("/api/lum/status")
        chat = client.post("/api/lum/chat", json={"message": "inspect Python doctrine"})
    assert status.status_code == 200
    status_json = status.json()
    assert status_json["agent"] == "KAI9000-Lum"
    assert status_json["model"] == "gpt-6-astra"
    assert status_json["helper_agent"] == "KAI9000-Lum-Mini"
    assert status_json["helper_model"] == "gpt-5.6-luna"
    assert status_json["credential_exposed_to_client"] is False
    assert status_json["self_approval"] is False
    assert status_json["delegate_cognition_not_authority"] is True
    assert status_json["helper_write_authority"] is False
    assert status_json["arbitrary_shell"] is False
    assert status_json["mcp_write"] is False
    assert chat.status_code == 200
    assert chat.json()["mode"] == "deterministic_mock"
