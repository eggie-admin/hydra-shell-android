from __future__ import annotations

import os
import unittest
from unittest import mock

import magic_chat


class MagicPolicyTests(unittest.TestCase):
    def test_mutating_spells_require_approval(self):
        self.assertTrue(magic_chat.SPELLS["WRITE_FILE"]["approval"])
        self.assertTrue(magic_chat.SPELLS["ULTIMA"]["approval"])
        self.assertTrue(magic_chat.SPELLS["ULTIMA"]["disabled"])

    def test_read_spells_do_not_require_approval(self):
        self.assertFalse(magic_chat.SPELLS["INSPECT"]["approval"])
        self.assertFalse(magic_chat.SPELLS["READ_FILE"]["approval"])
        self.assertFalse(magic_chat.SPELLS["SEARCH_TEXT"]["approval"])

    def test_secret_shaped_content_is_rejected(self):
        with self.assertRaises(Exception):
            magic_chat._reject_secrets("token=sk-abcdefghijklmnopqrstuvwxyz123456")

    def test_openai_missing_key_is_deterministic_mock(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            result = magic_chat.magic_chat(magic_chat.MagicChatRequest(message="inspect the project"))
        self.assertTrue(result["ok"])
        self.assertEqual(result["mode"], "deterministic_mock")
        self.assertIn("INSPECT", result["assistant"])

    def test_absolute_path_is_denied(self):
        with self.assertRaises(Exception):
            magic_chat._safe_path("/etc/passwd")


if __name__ == "__main__":
    unittest.main()
