from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / "lum_agent" / "for_loop.py"
SPEC = importlib.util.spec_from_file_location("kai_for_loop", MODULE_PATH)
assert SPEC and SPEC.loader
for_loop = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(for_loop)


class ForLoopTests(unittest.TestCase):
    def test_proven_stops_immediately(self) -> None:
        result = for_loop.run_for_loop(
            lambda _: for_loop.EvidenceState(proof_complete=True)
        )
        self.assertEqual(result.condition, for_loop.Condition.PROVEN)
        self.assertEqual(result.passes, 1)

    def test_missing_evidence_never_becomes_green_by_retry(self) -> None:
        result = for_loop.run_for_loop(
            lambda _: for_loop.EvidenceState(missing_evidence=("device_proof",)),
            max_passes=3,
        )
        self.assertEqual(result.condition, for_loop.Condition.NEEDS_HUMAN)
        self.assertEqual(result.passes, 3)

    def test_blocker_fails_closed(self) -> None:
        result = for_loop.run_for_loop(
            lambda _: for_loop.EvidenceState(blockers=("unknown_provenance",))
        )
        self.assertEqual(result.condition, for_loop.Condition.BLOCKED)

    def test_crown_gate_beats_proof(self) -> None:
        result = for_loop.run_for_loop(
            lambda _: for_loop.EvidenceState(
                proof_complete=True,
                crown_required=True,
            )
        )
        self.assertEqual(result.condition, for_loop.Condition.CROWN_REQUIRED)

    def test_contradiction_prevents_green(self) -> None:
        result = for_loop.run_for_loop(
            lambda _: for_loop.EvidenceState(
                proof_complete=True,
                contradictions=("sha_mismatch",),
            ),
            max_passes=2,
        )
        self.assertEqual(result.condition, for_loop.Condition.NEEDS_HUMAN)


if __name__ == "__main__":
    unittest.main()
