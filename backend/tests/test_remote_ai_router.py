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


def test_canonical_openai_model_is_current() -> None:
    assert remote_ai.OPENAI_MODEL == "gpt-5.6-sol"


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
    fake_hf_token = "hf_" + ("a" * 32)
    with pytest.raises(HTTPException) as exc:
        remote_ai._reject_secrets("use " + fake_hf_token)
    assert exc.value.status_code == 400


def test_secret_shaped_provider_output_is_rejected() -> None:
    fake_openai_key = "sk-" + ("a" * 32)
    with pytest.raises(HTTPException) as exc:
        remote_ai._reject_secret_output(fake_openai_key)
    assert exc.value.status_code == 502


def test_openai_model_override_must_be_allowlisted(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("KAI_OPENAI_ALLOWED_MODELS", raising=False)
    with pytest.raises(HTTPException) as exc:
        remote_ai._resolve_model("openai", "some-unreviewed-model")
    assert exc.value.status_code == 400


def test_openai_model_override_can_be_explicitly_allowlisted(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KAI_OPENAI_ALLOWED_MODELS", "gpt-5.6-luna,gpt-5.6-terra")
    assert remote_ai._resolve_model("openai", "gpt-5.6-luna") == "gpt-5.6-luna"


def test_default_models_remain_allowlisted(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("KAI_OPENAI_ALLOWED_MODELS", raising=False)
    monkeypatch.delenv("KAI_HF_ALLOWED_MODELS", raising=False)
    assert remote_ai.OPENAI_MODEL in remote_ai._allowed_models("openai")
    assert remote_ai.HF_MODEL in remote_ai._allowed_models("huggingface")


def test_empty_provider_text_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "placeholder")

    class Response:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {"id": "resp_test", "output": []}

    monkeypatch.setattr(remote_ai.httpx, "post", lambda *args, **kwargs: Response())
    with pytest.raises(HTTPException) as exc:
        remote_ai._call_responses_api("openai", "hello", None)
    assert exc.value.status_code == 502


def test_provider_error_does_not_silently_failover(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "placeholder")

    def fail(*args, **kwargs):
        raise remote_ai.httpx.ConnectError("offline")

    monkeypatch.setattr(remote_ai.httpx, "post", fail)
    with pytest.raises(HTTPException) as exc:
        remote_ai._call_responses_api("openai", "hello", None)
    assert exc.value.status_code == 502
    assert "without failover" in str(exc.value.detail)
