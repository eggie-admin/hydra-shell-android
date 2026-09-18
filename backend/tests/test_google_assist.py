from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "ultima" / "ollama-ffmpeg-antenna-v3"
if str(RUNTIME) not in sys.path:
    sys.path.insert(0, str(RUNTIME))

google_assist = importlib.import_module("google_assist")


def reset_cache() -> None:
    google_assist._CLIENT = None
    google_assist._CLIENT_SIGNATURE = None


def test_current_google_assistance_models() -> None:
    assert google_assist.GOOGLE_FAST_MODEL == "gemini-3.5-flash-lite"
    assert google_assist.GOOGLE_DEEP_MODEL == "gemini-3.8-flash"
    assert google_assist.GOOGLE_LIVE_API_MODEL == "gemini-3.8-live"


def test_profile_resolution() -> None:
    assert google_assist._resolve_model("fast") == "gemini-3.5-flash-lite"
    assert google_assist._resolve_model("deep") == "gemini-3.8-flash"
    assert google_assist._timeout_ms("fast") == google_assist.GOOGLE_FAST_TIMEOUT_MS
    assert google_assist._timeout_ms("deep") == google_assist.GOOGLE_DEEP_TIMEOUT_MS


def test_google_client_reuses_same_auth_signature(monkeypatch: pytest.MonkeyPatch) -> None:
    reset_cache()
    created: list[object] = []
    monkeypatch.setattr(google_assist.gateway, "google_auth_mode", lambda: "api_key")
    monkeypatch.setattr(google_assist.gateway, "_project_id", lambda: None)
    monkeypatch.setattr(google_assist.gateway, "_api_key", lambda: "placeholder-key")

    def factory() -> object:
        client = object()
        created.append(client)
        return client

    monkeypatch.setattr(google_assist.gateway, "_google_client", factory)
    first = google_assist._client()
    second = google_assist._client()
    assert first is second
    assert len(created) == 1


def test_google_client_refreshes_when_auth_signature_changes(monkeypatch: pytest.MonkeyPatch) -> None:
    reset_cache()
    project = {"value": "project-a"}
    created: list[object] = []
    monkeypatch.setattr(google_assist.gateway, "google_auth_mode", lambda: "vertex_adc")
    monkeypatch.setattr(google_assist.gateway, "_project_id", lambda: project["value"])
    monkeypatch.setattr(google_assist.gateway, "_api_key", lambda: None)

    def factory() -> object:
        client = object()
        created.append(client)
        return client

    monkeypatch.setattr(google_assist.gateway, "_google_client", factory)
    first = google_assist._client()
    project["value"] = "project-b"
    second = google_assist._client()
    assert first is not second
    assert len(created) == 2


def test_generate_uses_fast_model_timeout_and_cache_receipt(monkeypatch: pytest.MonkeyPatch) -> None:
    class Usage:
        cached_content_token_count = 123

    class Response:
        text = "GREEN"
        usage_metadata = Usage()

    class Models:
        def generate_content(self, *, model: str, contents: str, config: object) -> Response:
            assert model == "gemini-3.5-flash-lite"
            assert contents == "hello"
            assert getattr(config.http_options, "timeout") == google_assist.GOOGLE_FAST_TIMEOUT_MS
            return Response()

    class Client:
        models = Models()

    monkeypatch.setattr(google_assist, "_client", lambda: Client())
    monkeypatch.setattr(google_assist.gateway, "google_auth_mode", lambda: "api_key")
    result = google_assist.generate("hello", "fast")
    assert result["text"] == "GREEN"
    assert result["model"] == "gemini-3.5-flash-lite"
    assert result["profile"] == "fast"
    assert result["client_cache"] == "process_reuse"
    assert result["timeout_ms"] == google_assist.GOOGLE_FAST_TIMEOUT_MS
    assert result["implicit_context_cache"] is True
    assert result["cached_input_tokens"] == 123
    assert result["secret_material_present"] is False
