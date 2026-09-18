from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "ultima" / "ollama-ffmpeg-antenna-v3"
if str(RUNTIME) not in sys.path:
    sys.path.insert(0, str(RUNTIME))

api_spine = importlib.import_module("api_spine")


def all_ready() -> dict[str, bool]:
    return {"openai": True, "google": True, "huggingface": True, "github": True}


def request(task: str = "build", mode: str = "auto", critic: bool = False):
    return api_spine.SpineAssistRequest(message="audit the API", task=task, mode=mode, critic=critic)


def test_auto_recruits_zero_helpers(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(api_spine, "_configured", all_ready)
    plan = api_spine._plan(request(task="build", mode="auto"))
    assert plan["mode"] == "parent"
    assert plan["default_helpers"] == 0
    assert plan["helpers"] == []
    assert plan["primary"]["provider"] == "openai"


def test_direct_bypasses_mesh_even_if_mesh_requested(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(api_spine, "_configured", all_ready)
    plan = api_spine._plan(request(task="direct", mode="mesh", critic=True))
    assert plan["mode"] == "parent"
    assert plan["helpers"] == []
    assert plan["primary"] is not None


def test_explicit_mesh_is_capped_at_two(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(api_spine, "_configured", all_ready)
    plan = api_spine._plan(request(task="audit", mode="mesh", critic=True))
    assert plan["mode"] == "mesh"
    assert len(plan["helpers"]) == 2
    assert plan["parallel_read_only_helpers_max"] == 2
    assert plan["delegation_depth_max"] == 1
    assert plan["recursive_recruiting"] is False
    assert plan["helper_consensus_grants_authority"] is False


def test_canonical_route_registry_is_v1() -> None:
    paths = {route.path for route in api_spine.ROUTER.routes}
    assert {
        "/api/v1/health",
        "/api/v1/status",
        "/api/v1/providers",
        "/api/v1/capabilities",
        "/api/v1/assist/plan",
        "/api/v1/assist/query",
        "/api/v1/ai/chat",
        "/api/v1/providers/route",
    }.issubset(paths)
