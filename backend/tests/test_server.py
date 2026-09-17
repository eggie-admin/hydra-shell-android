import importlib
import os
import sys
import urllib.error
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
os.environ.setdefault("HYDRA_OLLAMA_MODEL", "test-model")
os.environ.setdefault("HYDRA_FAST_MODEL", "fast-test-model")
os.environ.setdefault("HYDRA_DEEP_MODEL", "deep-test-model")

server = importlib.import_module("server")


def test_health(monkeypatch):
    monkeypatch.setattr(server, "ollama_alive", lambda: True)
    client = server.app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    body = response.get_json()
    assert body["status"] == "ok"
    assert body["ollama"] is True
    assert body["fast_model"] == "fast-test-model"
    assert body["deep_model"] == "deep-test-model"


def test_fast_turn(monkeypatch):
    monkeypatch.setattr(server, "ollama_alive", lambda: True)
    monkeypatch.setattr(
        server,
        "chat_with_ollama",
        lambda messages, model: (f"Local and green on {model}.", [{"stage": "ollama", "latency_ms": 1, "tool_calls": 0}]),
    )
    client = server.app.test_client()
    response = client.post(
        "/v1/hydra/turn",
        json={"conversation_id": "test", "message": "hello", "speak": False, "mode": "fast"},
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["text"] == "Local and green on fast-test-model."
    assert body["provider"] == "ollama-local"
    assert body["voice"]["speaker"] == "hydra"
    assert body["model"] == "fast-test-model"


def test_deep_turn(monkeypatch):
    monkeypatch.setattr(server, "ollama_alive", lambda: True)
    monkeypatch.setattr(server, "chat_with_ollama", lambda messages, model: (model, []))
    client = server.app.test_client()
    response = client.post("/v1/hydra/turn", json={"message": "build it", "mode": "deep"})
    assert response.status_code == 200
    assert response.get_json()["model"] == "deep-test-model"


def test_system_status(monkeypatch):
    monkeypatch.setattr(
        server,
        "service_status",
        lambda: {
            "hydra": {"online": True, "port": 8787},
            "ollama": {"online": True, "port": 11434},
            "axs": {"online": True, "port": 8767, "http_status": 200},
            "vnc": {"online": True, "port": 5901, "display": ":1"},
            "tts": {"online": False},
        },
    )
    client = server.app.test_client()
    response = client.get("/v1/system/status")
    assert response.status_code == 200
    body = response.get_json()
    assert body["services"]["axs"]["online"] is True
    assert body["services"]["vnc"]["display"] == ":1"


def test_axs_probe_redacts_exception_details(monkeypatch):
    monkeypatch.setattr(server, "AXS_HOST", "127.0.0.1")
    monkeypatch.setattr(server, "tcp_probe", lambda host, port, timeout=0.5: True)

    def boom(*args, **kwargs):
        raise urllib.error.URLError("sensitive local path")

    monkeypatch.setattr(server.urllib.request, "urlopen", boom)
    result = server.axs_probe()
    assert result["http_ok"] is False
    assert result["http_error"] == "probe_failed"
    assert result["http_error_type"] == "URLError"
    assert "detail" not in result


def test_service_tool(monkeypatch):
    monkeypatch.setattr(server, "service_status", lambda: {"axs": {"online": True}})
    result = server.run_tool("get_service_status", {})
    assert result["ok"] is True
    assert result["services"]["axs"]["online"] is True


def test_unknown_tool_is_rejected():
    result = server.run_tool("rm_everything", {})
    assert result["ok"] is False
    assert "Unknown tool" in result["error"]


def test_tool_arguments_rejected():
    result = server.run_tool("get_local_time", {"oops": True})
    assert result["ok"] is False
    assert "does not accept arguments" in result["error"]


def test_empty_message_rejected():
    client = server.app.test_client()
    response = client.post("/v1/hydra/turn", json={"message": ""})
    assert response.status_code == 400


def test_invalid_non_loopback_ollama_is_rejected(monkeypatch):
    monkeypatch.setattr(server, "OLLAMA_BASE", "http://192.168.1.20:11434")
    assert server.ollama_alive() is False
    client = server.app.test_client()
    response = client.post("/v1/hydra/turn", json={"message": "hello"})
    assert response.status_code == 503
    body = response.get_json()
    assert body["error"] == "ollama_unavailable"


def test_service_status_reports_non_loopback_policy_errors(monkeypatch):
    monkeypatch.setattr(server, "OLLAMA_BASE", "http://10.0.0.9:11434")
    monkeypatch.setattr(server, "AXS_HOST", "10.0.0.10")
    monkeypatch.setattr(server, "VNC_HOST", "10.0.0.11")
    status = server.service_status()
    assert status["ollama"]["fail_closed"] is True
    assert "loopback" in status["ollama"]["policy_error"].lower()
    assert "loopback" in status["axs"]["policy_error"].lower()
    assert status["axs"]["online"] is False
    assert "loopback" in status["vnc"]["policy_error"].lower()
    assert status["vnc"]["online"] is False
