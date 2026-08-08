import importlib
import os
import sys
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
