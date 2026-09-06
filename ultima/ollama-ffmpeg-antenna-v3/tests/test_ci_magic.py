from __future__ import annotations

import hashlib
import os
import tempfile
import unittest
from pathlib import Path
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
        fake_secret = "token=" + "sk-" + ("a" * 24)
        with self.assertRaises(Exception):
            magic_chat._reject_secrets(fake_secret)

    def test_openai_missing_key_is_deterministic_mock(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            result = magic_chat.magic_chat(magic_chat.MagicChatRequest(message="inspect the project"))
        self.assertTrue(result["ok"])
        self.assertEqual(result["mode"], "deterministic_mock")
        self.assertIn("INSPECT", result["assistant"])

    def test_absolute_and_traversal_paths_are_denied(self):
        with self.assertRaises(Exception):
            magic_chat._safe_path("/etc/passwd")
        with self.assertRaises(Exception):
            magic_chat._safe_path("../outside.py")

    def test_write_checkpoint_and_rollback_round_trip(self):
        old_code_root = magic_chat.CODE_ROOT
        old_checkpoint_root = magic_chat.CHECKPOINT_ROOT
        try:
            with tempfile.TemporaryDirectory() as td:
                root = Path(td).resolve()
                checkpoints = root / "checkpoints"
                checkpoints.mkdir()
                magic_chat.CODE_ROOT = root
                magic_chat.CHECKPOINT_ROOT = checkpoints

                target = root / "sample.py"
                before = b"value = 1\n"
                after = "value = 2\n"
                target.write_bytes(before)
                before_sha = hashlib.sha256(before).hexdigest()

                result = magic_chat._execute(
                    "WRITE_FILE",
                    {"path": "sample.py", "content": after, "old_sha256": before_sha},
                    "roundtrip-cast",
                )
                self.assertTrue(result["ok"])
                self.assertEqual(target.read_text(encoding="utf-8"), after)
                self.assertNotEqual(result["after_sha256"], before_sha)

                rolled = magic_chat.rollback_cast(
                    "roundtrip-cast", magic_chat.RollbackRequest(approved=True)
                )
                self.assertTrue(rolled["ok"])
                self.assertEqual(target.read_bytes(), before)
        finally:
            magic_chat.CODE_ROOT = old_code_root
            magic_chat.CHECKPOINT_ROOT = old_checkpoint_root


if __name__ == "__main__":
    unittest.main()
