from __future__ import annotations

import os
from unittest import mock

from fastapi.testclient import TestClient

from lum_agent.agent import (
    LUM_AGENT_NAME,
    LUM_DEEP_MODEL,
    LUM_FAST_MODEL,
    LUM_MODEL,
    build_lum_agent,
    run_lum,
)
from lum_agent.doctrine import SKILLS, build_agent_instructions, load_skill
from lum_agent.mesh import PASS_ORDER, run_ten_pass_mesh
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
    assert LUM_FAST_MODEL == "gpt-5.6-luna"
    assert LUM_DEEP_MODEL == "gpt-5.6-sol"
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
    assert status_json["mesh"]["max_remote_model_calls"] == 1
    assert len(status_json["mesh"]["passes"]) == 10
    assert chat.status_code == 200
    assert chat.json()["mode"] == "deterministic_mock"


def test_ten_pass_mesh_normalizes_dedupes_and_calls_boss_once() -> None:
    calls: list[tuple[str, str]] = []

    def fake_boss(prompt: str, route: str) -> dict[str, object]:
        calls.append((prompt, route))
        return {
            "ok": True,
            "mode": "test",
            "agent": "Lum",
            "model": "gpt-5.6-luna",
            "assistant": "Two relevant feed items survived normalization.",
            "execution": "AGENT_COMPLETED",
        }

    result = run_ten_pass_mesh(
        query="OpenAI agent pipeline",
        items=[
            {
                "title": "OpenAI agent pipeline update",
                "link": "https://example.test/a",
                "summary": "Agent pipeline details",
                "published": "2026-09-16",
            },
            {
                "title": "OpenAI agent pipeline update duplicate",
                "link": "https://example.test/a",
                "summary": "duplicate link",
            },
            {
                "title": "LuHm mesh",
                "link": "https://example.test/b",
                "summary": "OpenAI helper agent mesh",
            },
        ],
        max_items=10,
        invoke_boss=fake_boss,
    )

    assert result["pass_count"] == 10
    assert [entry["pass"] for entry in result["passes"]] == list(PASS_ORDER)
    assert result["normalized_count"] == 2
    assert result["selected_count"] == 2
    assert result["remote_model_calls"] == 1
    assert len(calls) == 1
    assert calls[0][1] == "fast"
    assert "luhmos.lum-mesh.rss-evidence.v1" in calls[0][0]
    assert result["authority"]["mutation_authority"] is False


def test_mesh_router_inline_json_dry_run_is_ten_pass_green() -> None:
    app = FastAPI()
    app.include_router(ROUTER)
    client = TestClient(app)
    payload = {
        "query": "LuHm agent mesh",
        "items": [
            {
                "title": "LuHm mesh candidate",
                "link": "https://example.test/lum",
                "summary": "RSS JSON evidence for the Lum boss",
            }
        ],
    }
    with mock.patch.dict(os.environ, {}, clear=True):
        response = client.post("/api/lum/mesh", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["pass_count"] == 10
    assert body["remote_model_calls"] == 0
    assert body["boss"]["execution"] == "NOT_EXECUTED"
    assert body["route"] == "fast"


def test_mesh_accepts_inline_rss_and_preserves_provenance() -> None:
    xml = """<?xml version='1.0'?>
    <rss version='2.0'><channel><title>Test</title>
      <item><title>Agent news</title><link>https://example.test/rss-1</link>
      <description>OpenAI agent mesh evidence</description><pubDate>2026-09-16</pubDate></item>
    </channel></rss>"""

    def fake_boss(prompt: str, route: str) -> dict[str, object]:
        return {
            "ok": True,
            "mode": "test",
            "agent": "Lum",
            "model": "gpt-5.6-luna",
            "assistant": "RSS evidence accepted.",
            "execution": "AGENT_COMPLETED",
        }

    result = run_ten_pass_mesh(
        query="agent mesh",
        rss_xml=xml,
        invoke_boss=fake_boss,
    )
    assert result["source_kind"] == "rss_xml"
    assert result["evidence"][0]["link"] == "https://example.test/rss-1"
    assert result["pass_count"] == 10
