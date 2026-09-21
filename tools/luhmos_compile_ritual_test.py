from __future__ import annotations

import copy
import unittest

from tools.luhmos_compile_ritual import evaluate

SHA = "38c5b8c4264351fb500672b47f92ac9d21b4df0a"


def green_evidence() -> dict:
    return {
        "source_truth": {
            "status": "GREEN",
            "latest_document_observed": True,
            "bound_canonical_sha": SHA,
        },
        "assets": {
            "blocked_material_in_ship_path": False,
            "required": [
                {
                    "name": "KAI9000_LUM_AVATAR_ACTUAL_ANIMATED.mp4",
                    "rights_class": "KAI_OWNED",
                    "ship_allowed": True,
                    "exists_verified": True,
                    "sha256_verified": True,
                }
            ],
        },
        "github": {
            "canonical_branch": "luhmos-main",
            "canonical_sha": SHA,
            "source_audit": "GREEN",
            "last_five_commits": [
                {"sha": SHA},
                {"sha": "2" * 40},
                {"sha": "3" * 40},
                {"sha": "4" * 40},
                {"sha": "5" * 40},
            ],
        },
        "forge": {
            "status": "GREEN",
            "workflow": ".github/workflows/luhmos-working-demo-candidate.yml",
            "actions_pinned": True,
            "toolchain_hashes_pinned": True,
            "donor_ref_pinned": True,
            "contents_read_only": True,
            "candidate_package_only": True,
            "silent_install": False,
            "public_release": False,
        },
    }


class CompileRitualTests(unittest.TestCase):
    def test_stale_source_truth_blocks_before_github_and_forge(self) -> None:
        evidence = green_evidence()
        evidence["source_truth"]["status"] = "AMBER"
        evidence["source_truth"]["bound_canonical_sha"] = None
        result = evaluate(evidence)
        self.assertEqual(result["verdict"], "AMBER")
        self.assertEqual(result["state"], "SOURCE_TRUTH_SYNC_REQUIRED")
        self.assertFalse(result["build_dispatched"])
        self.assertIsNone(result["dry_run"])
        self.assertEqual([s["name"] for s in result["stages"]], [
            "AUDIT_SOURCE_OF_TRUTH",
            "VERIFY_SHIPPABLE_ASSETS",
            "SOURCE_TRUTH_CURRENTNESS_GATE",
        ])

    def test_blocked_asset_fails_closed(self) -> None:
        evidence = green_evidence()
        evidence["assets"]["required"][0]["rights_class"] = "PRIVATE_REFERENCE"
        evidence["assets"]["required"][0]["ship_allowed"] = False
        result = evaluate(evidence)
        self.assertEqual(result["verdict"], "RED")
        self.assertEqual(result["state"], "ASSET_PROVENANCE_BLOCK")
        self.assertFalse(result["build_dispatched"])

    def test_full_green_yields_authorization_gate_not_build(self) -> None:
        result = evaluate(green_evidence())
        self.assertEqual(result["verdict"], "GREEN")
        self.assertEqual(result["state"], "FINAL_BUILD_AUTHORIZATION_REQUIRED")
        self.assertFalse(result["build_dispatched"])
        self.assertFalse(result["apk_uploaded"])
        self.assertIsNotNone(result["dry_run"])
        self.assertFalse(result["dry_run"]["github_dispatch"])
        self.assertFalse(result["dry_run"]["google_drive_upload"])
        self.assertFalse(result["dry_run"]["plain_continue_is_authorization"])
        self.assertIn(SHA, result["dry_run"]["final_authorization_example"])

    def test_continue_never_becomes_compile_authority(self) -> None:
        evidence = green_evidence()
        evidence["user_phrase"] = "continue"
        result = evaluate(copy.deepcopy(evidence))
        self.assertEqual(result["state"], "FINAL_BUILD_AUTHORIZATION_REQUIRED")
        self.assertFalse(result["build_dispatched"])

    def test_forge_drift_blocks(self) -> None:
        evidence = green_evidence()
        evidence["forge"]["donor_ref_pinned"] = False
        result = evaluate(evidence)
        self.assertEqual(result["verdict"], "RED")
        self.assertEqual(result["state"], "FORGE_CONTRACT_DRIFT")
        self.assertFalse(result["build_dispatched"])


if __name__ == "__main__":
    unittest.main()
