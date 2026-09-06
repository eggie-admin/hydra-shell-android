from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
from fastapi import HTTPException


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "ultima" / "ollama-ffmpeg-antenna-v3" / "remote_ai.py"
SPEC = importlib.util.spec_from_file_location("kai9000_remote_ai", MODULE_PATH)
assert SPEC and SPEC.loader
remote_ai = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(remote_ai)


def test_auto_without_remote_credentials_uses_mock(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("HF_TOKEN", raising=False)
    assert remote_ai._select_provider("auto") == "deterministic_mock"


def test_auto_prefers_openai_when_both_are_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-placeholder")
    monkeypatch.setenv("HF_TOKEN", "test-hf-placeholder")
    assert remote_ai._select_provider("auto") == "openai"


def test_auto_uses_huggingface_when_openai_is_absent(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("HF_TOKEN", "test-hf-placeholder")
    assert remote_ai._select_provider("auto") == "huggingface"


def test_explicit_huggingface_requires_server_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("HF_TOKEN", raising=False)
    with pytest.raises(HTTPException) as exc:
        remote_ai._select_provider("huggingface")
    assert exc.value.status_code == 503


def test_unknown_provider_is_rejected() -> None:
    with pytest.raises(HTTPException) as exc:
        remote_ai._select_provider("random-vendor")
    assert exc.value.status_code == 400


def test_huggingface_token_shape_is_rejected_from_prompt() -> None:
    with pytest.raises(HTTPException) as exc:
        remote_ai._reject_secrets("use hf_abcdefghijklmnopqrstuvwxyz1234567890")
    assert exc.value.status_code == 400
