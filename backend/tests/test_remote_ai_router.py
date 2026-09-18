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


def test_canonical_openai_models_are_current() -> None:
    assert remote_ai.OPENAI_FAST_MODEL == "gpt-5.6-luna"
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


def test_short_auto_profile_uses_fast_lane() -> None:
    assert remote_ai._resolve_profile("auto", "hello") == "fast"
    assert remote_ai._resolve_model("openai", None, "fast") == "gpt-5.6-luna"
    assert remote_ai._profile_max_output_tokens("fast") == 512


def test_long_auto_profile_uses_deep_lane() -> None:
    message = "x" * 4001
    assert remote_ai._resolve_profile("auto", message) == "deep"
    assert remote_ai._resolve_model("openai", None, "deep") == "gpt-5.6-sol"
    assert remote_ai._profile_max_output_tokens("deep") == 1200


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
    monkeypatch.setenv("KAI_OPENAI_ALLOWED_MODELS", "gpt-5.6-terra")
    assert remote_ai._resolve_model("openai", "gpt-5.6-terra") == "gpt-5.6-terra"


def test_default_models_remain_allowlisted(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("KAI_OPENAI_ALLOWED_MODELS", raising=False)
    monkeypatch.delenv("KAI_HF_ALLOWED_MODELS", raising=False)
    assert remote_ai.OPENAI_FAST_MODEL in remote_ai._allowed_models("openai")
    assert remote_ai.OPENAI_MODEL in remote_ai._allowed_models("openai")
    assert remote_ai.HF_FAST_MODEL in remote_ai._allowed_models("huggingface")
    assert remote_ai.HF_MODEL in remote_ai._allowed_models("huggingface")


def test_empty_provider_text_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "placeholder")

    class Response:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {"id": "resp_test", "output": []}

    monkeypatch.setattr(remote_ai._HTTP_CLIENT, "post", lambda *args, **kwargs: Response())
    with pytest.raises(HTTPException) as exc:
        remote_ai._call_responses_api("openai", "hello", None)
    assert exc.value.status_code == 502


def test_provider_error_does_not_silently_failover(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "placeholder")

    def fail(*args, **kwargs):
        raise remote_ai.httpx.ConnectError("offline")

    monkeypatch.setattr(remote_ai._HTTP_CLIENT, "post", fail)
    with pytest.raises(HTTPException) as exc:
        remote_ai._call_responses_api("openai", "hello", None)
    assert exc.value.status_code == 502
    assert "without failover" in str(exc.value.detail)


def test_previous_response_id_and_openai_fastpath_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "placeholder")
    captured: dict = {}

    class Response:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {
                "id": "resp_next",
                "output_text": "GREEN",
                "service_tier": "default",
                "usage": {"input_tokens_details": {"cached_tokens": 77}},
            }

    def post(*args, **kwargs):
        captured.update(kwargs.get("json") or {})
        return Response()

    monkeypatch.setattr(remote_ai._HTTP_CLIENT, "post", post)
    result = remote_ai._call_responses_api(
        "openai",
        "continue",
        None,
        profile="fast",
        previous_response_id="resp_previous1234",
    )
    assert captured["previous_response_id"] == "resp_previous1234"
    assert captured["model"] == "gpt-5.6-luna"
    assert captured["max_output_tokens"] == 512
    assert captured["prompt_cache_options"] == {"mode": "implicit", "ttl": "30m"}
    assert captured["prompt_cache_key"].startswith("luhm-os:fast:gpt-5.6-luna:")
    assert captured["reasoning"] == {"effort": "none"}
    assert captured["text"] == {"verbosity": "low"}
    assert captured["service_tier"] == "auto"
    assert result["response_id"] == "resp_next"
    assert result["connection_pool"] == "keepalive_http2"
    assert result["cached_input_tokens"] == 77
    assert result["service_tier"] == "default"


def test_huggingface_payload_does_not_receive_openai_only_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HF_TOKEN", "placeholder")
    captured: dict = {}

    class Response:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {"id": "hf_resp", "output_text": "GREEN"}

    def post(*args, **kwargs):
        captured.update(kwargs.get("json") or {})
        return Response()

    monkeypatch.setattr(remote_ai._HTTP_CLIENT, "post", post)
    result = remote_ai._call_responses_api("huggingface", "check", None, profile="fast")
    assert captured["model"] == "openai/gpt-oss-20b:fastest"
    assert "prompt_cache_key" not in captured
    assert "prompt_cache_options" not in captured
    assert "reasoning" not in captured
    assert "text" not in captured
    assert "service_tier" not in captured
    assert result["prompt_cache"] == "provider_managed"


def test_invalid_previous_response_id_is_rejected() -> None:
    with pytest.raises(HTTPException) as exc:
        remote_ai._validate_previous_response_id("not-a-response-id")
    assert exc.value.status_code == 400
