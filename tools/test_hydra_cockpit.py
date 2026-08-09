#!/usr/bin/env python3
from __future__ import annotations

import json
import threading
import unittest
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import hydra_cockpit


class FakeOllama(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def do_GET(self):
        if self.path == "/api/tags":
            data = json.dumps({"models": [{"name": "qwen3.5:2b-q4_K_M"}]}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        self.send_error(404)

    def do_POST(self):
        if self.path != "/api/chat":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        body = json.loads(self.rfile.read(length))
        assert body["model"] == "qwen3.5:2b-q4_K_M"
        lines = [
            {"model": body["model"], "message": {"content": "Hello "}, "done": False},
            {"model": body["model"], "message": {"content": "Professor."}, "done": True},
        ]
        data = b"".join((json.dumps(item) + "\n").encode() for item in lines)
        self.send_response(200)
        self.send_header("Content-Type", "application/x-ndjson")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


class CockpitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ollama = ThreadingHTTPServer(("127.0.0.1", 0), FakeOllama)
        cls.ollama_thread = threading.Thread(target=cls.ollama.serve_forever, daemon=True)
        cls.ollama_thread.start()
        hydra_cockpit.OLLAMA_URL = f"http://127.0.0.1:{cls.ollama.server_port}"

        cls.gateway = ThreadingHTTPServer(("127.0.0.1", 0), hydra_cockpit.Handler)
        cls.gateway_thread = threading.Thread(target=cls.gateway.serve_forever, daemon=True)
        cls.gateway_thread.start()
        cls.base = f"http://127.0.0.1:{cls.gateway.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.gateway.shutdown()
        cls.gateway.server_close()
        cls.ollama.shutdown()
        cls.ollama.server_close()

    def test_health_lists_default_model(self):
        with urllib.request.urlopen(self.base + "/health", timeout=3) as response:
            payload = json.loads(response.read())
        self.assertTrue(payload["gateway"])
        self.assertTrue(payload["ollama"])
        self.assertIn("qwen3.5:2b-q4_K_M", payload["models"])

    def test_chat_stream(self):
        request = urllib.request.Request(
            self.base + "/api/chat",
            data=json.dumps({
                "message": "Are we green?",
                "model": "qwen3.5:2b-q4_K_M",
                "history": [],
            }).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=3) as response:
            chunks = [json.loads(line) for line in response if line.strip()]
        self.assertEqual("".join(item["delta"] for item in chunks), "Hello Professor.")
        self.assertTrue(chunks[-1]["done"])

    def test_ui_is_mobile_cockpit(self):
        with urllib.request.urlopen(self.base + "/", timeout=3) as response:
            html = response.read().decode()
        self.assertIn("LUM COCKPIT", html)
        self.assertIn("viewport-fit=cover", html)
        self.assertIn("/api/chat", html)

    def test_final_mic_transcript_auto_submits_once(self):
        with urllib.request.urlopen(self.base + "/", timeout=3) as response:
            html = response.read().decode()
        self.assertIn("async function submitMessage()", html)
        self.assertIn("if(busy)return", html)
        self.assertIn("setMicState('listening')", html)
        self.assertIn("setMicState('sending')", html)
        self.assertIn("void submitMessage()", html)
        self.assertNotIn(
            "rec.onresult=e=>{promptEl.value=e.results[0][0].transcript;promptEl.focus()}",
            html,
        )

    def test_cross_origin_chat_is_refused(self):
        request = urllib.request.Request(
            self.base + "/api/chat",
            data=b'{"message":"hello"}',
            headers={"Content-Type": "application/json", "Origin": "https://example.invalid"},
            method="POST",
        )
        with self.assertRaises(urllib.error.HTTPError) as caught:
            urllib.request.urlopen(request, timeout=3)
        self.assertEqual(caught.exception.code, 403)


if __name__ == "__main__":
    unittest.main()
