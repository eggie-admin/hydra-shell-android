from __future__ import annotations

import json
import unittest
from pathlib import Path
from unittest import mock

import antenna
from fastapi.testclient import TestClient
import main


class Kai9000SmokeTests(unittest.TestCase):
    def test_ollama_default_is_loopback(self):
        self.assertEqual(antenna.OLLAMA_URL, "http://127.0.0.1:11434")

    def test_antenna_status_survives_offline_ollama(self):
        with mock.patch.object(antenna, "ollama_status", return_value={"ok": False, "url": antenna.OLLAMA_URL}):
            status = antenna.antenna_status()
        self.assertTrue(status["policy"]["local_first"])
        self.assertTrue(status["policy"]["ollama_loopback_default"])
        self.assertFalse(status["policy"]["github_is_source_remote_not_runtime_ai"] is False)

    def test_health_boots_without_remote_services(self):
        with mock.patch.object(main, "antenna_status", return_value={"ok": True}), mock.patch.object(
            main.ComfyClient, "health", side_effect=RuntimeError("offline test")
        ):
            client = TestClient(main.APP)
            response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["service"], "kai9000-ultima-ollama-ffmpeg-antenna-v3")

    def test_project_manifest_references_runtime(self):
        root = Path(__file__).resolve().parents[3]
        manifest = json.loads((root / "lumh-os" / "kai9000" / "project.manifest.json").read_text())
        self.assertEqual(manifest["source_path"], "ultima/ollama-ffmpeg-antenna-v3")
        self.assertEqual(manifest["ingestion"]["strategy"], "reference_not_copy")
        self.assertFalse(manifest["ingestion"]["remote_shell"])


if __name__ == "__main__":
    unittest.main()
