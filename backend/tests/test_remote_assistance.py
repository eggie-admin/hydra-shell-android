from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest
from fastapi import HTTPException

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "ultima" / "ollama-ffmpeg-antenna-v3"
if str(RUNTIME) not in sys.path:
    sys.path.insert(0, str(RUNTIME))

assistance = importlib.import_module("assistance")


def all_ready() -> dict[str, bool]:
    return {"openai": True, "google": True, "huggingface": True, "github": True}


def test_direct_questions_bypass_mesh(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(assistance, "_configured", all_ready)
    plan = assistance._plan("direct", "mesh", critic=True)
    assert plan["mode"] == "single"
    assert plan["direct_questions_bypass_mesh"] is True
    assert len(plan["calls"]) == 1
    assert plan["calls"][0]["provider"] == "openai"
    assert plan["calls"][0]["profile"] == "fast"


def test_complex_auto_uses_build_and_research_blades(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(assistance, "_configured", all_ready)
    plan = assistance._plan("build", "auto", critic=False)
    assert plan["mode"] == "mesh"
    assert plan["parallelism_max"] == 3
    assert [item["blade"] for item in plan["calls"]] == ["build", "research"]
    assert [item["provider"] for item in plan["calls"]] == ["openai", "google"]
    assert plan["calls"][0]["profile"] == "deep"


def test_conditional_critic_is_third_and_final_parallel_call(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(assistance, "_configured", all_ready)
    plan = assistance._plan("audit", "mesh", critic=True)
    assert [item["provider"] for item in plan["calls"]] == ["openai", "google", "huggingface"]
    assert len(plan["calls"]) == assistance.MAX_PARALLEL == 3


def test_research_single_prefers_google(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(assistance, "_configured", all_ready)
    plan = assistance._plan("research", "single", critic=False)
    assert plan["calls"] == [{"blade": "research", "provider": "google", "profile": "fast"}]


def test_github_context_is_reference_first(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_REPOSITORY", "eggie-admin/hydra-shell-android")
    monkeypatch.setenv("GITHUB_SHA", "abc123")
    context = assistance._github_context([
        "eggie-admin/hydra-shell-android@abc123:README.md",
        "https://github.com/eggie-admin/hydra-shell-android/pull/81",
    ])
    assert context["provider"] == "github"
    assert context["policy"] == "evidence_by_reference_not_full_history_copy"
    assert context["resolution"] == "bounded_exact_sha_on_demand"
    assert context["mutation_authority"] is False
    assert len(context["references"]) == 2


def test_github_context_rejects_reference_sprawl() -> None:
    refs = [f"repo@sha:file-{index}" for index in range(assistance.MAX_GITHUB_REFS + 1)]
    with pytest.raises(HTTPException) as exc:
        assistance._github_context(refs)
    assert exc.value.status_code == 400


def test_exact_sha_parser_rejects_mutable_ref_and_accepts_canonical_ref() -> None:
    sha = "a" * 40
    assert assistance._parse_exact_github_ref(
        f"eggie-admin/hydra-shell-android@{sha}:README.md"
    ) == (sha, "README.md")
    assert assistance._parse_exact_github_ref(
        f"https://github.com/eggie-admin/hydra-shell-android/blob/{sha}/docs/API_TRINITY_DOCTRINE.md"
    ) == (sha, "docs/API_TRINITY_DOCTRINE.md")
    assert assistance._parse_exact_github_ref(
        "eggie-admin/hydra-shell-android@luhmos-main:README.md"
    ) is None


def test_github_path_guard_rejects_traversal_and_key_material() -> None:
    assert assistance._safe_repo_path("../secret") is None
    assert assistance._safe_repo_path("keys/operator.pem") is None
    assert assistance._safe_repo_path("docs/README.md") == "docs/README.md"


def test_helper_message_resolves_bounded_context_once(monkeypatch: pytest.MonkeyPatch) -> None:
    sha = "b" * 40
    ref = f"eggie-admin/hydra-shell-android@{sha}:README.md"
    monkeypatch.setattr(
        assistance,
        "_resolve_github_references",
        lambda refs: [{"reference": ref, "status": "GREEN", "text": "SOURCE EVIDENCE", "truncated": False}],
    )
    message, resolved = assistance._helper_message("audit this", assistance._github_context([ref]))
    assert "SOURCE EVIDENCE" in message
    assert ref in message
    assert len(resolved) == 1


def test_no_refs_add_zero_github_resolution_work(monkeypatch: pytest.MonkeyPatch) -> None:
    def should_not_run(refs):
        raise AssertionError("resolver should not run without refs")
    monkeypatch.setattr(assistance, "_resolve_github_references", should_not_run)
    message, resolved = assistance._helper_message("direct", assistance._github_context([]))
    assert message == "direct"
    assert resolved == []


def test_no_configured_provider_does_not_invent_remote_green(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        assistance,
        "_configured",
        lambda: {"openai": False, "google": False, "huggingface": False, "github": True},
    )
    plan = assistance._plan("build", "auto", critic=True)
    assert plan["calls"] == []
    assert plan["execution"] == "advisory_only"
    assert plan["crown_gate"] is True
