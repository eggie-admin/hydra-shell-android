from __future__ import annotations

import os
import unittest
from contextlib import contextmanager
from types import SimpleNamespace
from unittest import mock

from fastapi import FastAPI
from fastapi.testclient import TestClient

import gateway


@contextmanager
def no_google_credentials():
    keys = [
        "GOOGLE_CLOUD_PROJECT",
        "GCP_PROJECT",
        "GCP_PROJECT_ID",
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
    ]
    with mock.patch.dict(os.environ, {"KAI_GOOGLE_AUTH": "auto"}, clear=False):
        for key in keys:
            os.environ.pop(key, None)
        yield


class Kai9000GatewayTests(unittest.TestCase):
    def setUp(self) -> None:
        app = FastAPI()
        app.include_router(gateway.ROUTER)
        self.app = app
        self.client = TestClient(app)

    def test_four_lane_contract_is_live(self):
        with no_google_credentials():
            status = self.client.get("/api/status")
            route = self.client.post(
                "/api/providers/route", json={"kind": "status", "prefer": "auto"}
            )
            director = self.client.post(
                "/api/director", json={"message": "smoke", "mode": "auto"}
            )
            google_health = self.client.get("/providers/google/health")
            google_generate = self.client.post(
                "/providers/google/generate", json={"prompt": "smoke"}
            )

        self.assertEqual(status.status_code, 200)
        self.assertEqual(route.status_code, 200)
        self.assertEqual(director.status_code, 200)
        self.assertEqual(google_health.status_code, 200)
        self.assertEqual(google_generate.status_code, 503)

        with no_google_credentials(), self.client.websocket_connect("/ws") as websocket:
            self.assertEqual(websocket.receive_json()["type"], "hello")

        with no_google_credentials(), self.client.websocket_connect(
            "/providers/gemini/live"
        ) as websocket:
            event = websocket.receive_json()
            self.assertEqual(event["type"], "provider.error")
            self.assertEqual(event["code"], "google_not_configured")

    def test_status_never_exposes_provider_credentials(self):
        with no_google_credentials():
            response = self.client.get("/api/status")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["contract"], "kai9000.antenna-gateway.v1")
        self.assertEqual(payload["lanes"]["control_ws"], "/ws")
        self.assertFalse(payload["google"]["secrets_exposed"])
        self.assertFalse(payload["google"]["android_provider_credentials"])

    def test_auto_prefers_vertex_adc_when_project_is_present(self):
        with mock.patch.dict(
            os.environ,
            {"KAI_GOOGLE_AUTH": "auto", "GOOGLE_CLOUD_PROJECT": "test-project"},
            clear=False,
        ):
            self.assertEqual(gateway.google_auth_mode(), "vertex_adc")

    def test_google_generate_refuses_unconfigured_provider(self):
        with no_google_credentials():
            response = self.client.post(
                "/providers/google/generate", json={"prompt": "smoke"}
            )
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("key", response.text.lower())

    def test_director_is_route_only_not_hidden_execution(self):
        with no_google_credentials():
            response = self.client.post(
                "/api/director", json={"message": "status please", "mode": "auto"}
            )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["execution"], "route_only")
        self.assertEqual(payload["lane"], "/api/antenna/ollama/chat")

    def test_control_websocket_ping_and_status(self):
        with no_google_credentials(), self.client.websocket_connect("/ws") as websocket:
            hello = websocket.receive_json()
            self.assertEqual(hello["type"], "hello")
            websocket.send_json({"type": "ping"})
            self.assertEqual(websocket.receive_json()["type"], "pong")
            websocket.send_json({"type": "status.get"})
            status = websocket.receive_json()
            self.assertEqual(status["type"], "status.snapshot")
            self.assertEqual(status["payload"]["contract"], "kai9000.antenna-gateway.v1")

    def test_gemini_live_socket_fails_closed_without_server_auth(self):
        with no_google_credentials(), self.client.websocket_connect(
            "/providers/gemini/live"
        ) as websocket:
            event = websocket.receive_json()
            self.assertEqual(event["type"], "provider.error")
            self.assertEqual(event["code"], "google_not_configured")
            self.assertFalse(event["secrets_exposed"])

    def test_provider_tool_call_is_never_auto_executed(self):
        call = SimpleNamespace(name="dangerous_tool", id="call-1", args={"x": 1})
        message = SimpleNamespace(
            text=None,
            server_content=None,
            tool_call=SimpleNamespace(function_calls=[call]),
        )
        event = gateway._normalize_live_message(message)
        self.assertEqual(event["type"], "provider.tool.request")
        self.assertEqual(event["execution"], "blocked_pending_policy")
        self.assertEqual(event["calls"][0]["name"], "dangerous_tool")


if __name__ == "__main__":
    unittest.main()
