import importlib
import os
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
os.environ.setdefault("HYDRA_OLLAMA_MODEL", "test-model")

server = importlib.import_module("server")


def test_health(monkeypatch):
    monkeypatch.setattr(server, "ollama_alive", lambda: True)
    client = server.app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    body = response.get_json()
    assert body["status"] == "ok"
    assert body["ollama"] is True


def test_turn(monkeypatch):
    monkeypatch.setattr(server, "ollama_alive", lambda: True)
    monkeypatch.setattr(server, "chat_with_ollama", lambda messages: ("Local and green.", [{"stage": "ollama", "latency_ms": 1, "tool_calls": 0}]))
    client = server.app.test_client()
    response = client.post("/v1/hydra/turn", json={"conversation_id": "test", "message": "hello", "speak": False})
    assert response.status_code == 200
    body = response.get_json()
    assert body["text"] == "Local and green."
    assert body["provider"] == "ollama-local"
    assert body["voice"]["speaker"] == "hydra"


def test_unknown_tool_is_rejected():
    result = server.run_tool("rm_everything", {})
    assert result["ok"] is False
    assert "Unknown tool" in result["error"]


def test_empty_message_rejected():
    client = server.app.test_client()
    response = client.post("/v1/hydra/turn", json={"message": ""})
    assert response.status_code == 400
