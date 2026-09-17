import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("lum_agent_mesh", HERE / "mesh.py")
mesh = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(mesh)


class LumAgentMeshTests(unittest.TestCase):
    def setUp(self):
        self.boss = mesh.LumBoss()

    def test_direct_bypasses_mesh(self):
        d = self.boss.route(mesh.TaskPacket("1", "simple question"))
        self.assertEqual(d.route, mesh.Blade.DIRECT)
        self.assertEqual(d.helpers, ())
        self.assertFalse(d.critic_required)
        self.assertFalse(d.tool_edge_allowed)

    def test_context_build_research_are_bounded(self):
        d = self.boss.route(mesh.TaskPacket(
            "2", "triage complex work",
            needs_context=True,
            needs_build=True,
            needs_research=True,
        ))
        self.assertEqual(
            d.helpers,
            (mesh.Blade.CONTEXT, mesh.Blade.BUILD, mesh.Blade.RESEARCH),
        )
        self.assertLessEqual(len(d.helpers), 3)
        self.assertTrue(d.critic_required)

    def test_consequential_action_fails_closed_without_crown(self):
        d = self.boss.route(mesh.TaskPacket(
            "3", "push candidate",
            tier=mesh.Tier.RECKONING,
            consequential=True,
            read_only=False,
        ))
        self.assertEqual(d.terminal, mesh.Terminal.CROWN_REQUIRED)
        self.assertFalse(d.tool_edge_allowed)
        self.assertTrue(d.critic_required)

    def test_explicit_crown_can_open_deterministic_tool_edge(self):
        d = self.boss.route(mesh.TaskPacket(
            "4", "stage authorized candidate",
            tier=mesh.Tier.RECKONING,
            consequential=True,
            explicit_professor_authorization=True,
            read_only=False,
        ))
        self.assertEqual(d.terminal, mesh.Terminal.CONTINUE)
        self.assertTrue(d.tool_edge_allowed)
        self.assertTrue(d.critic_required)

    def test_helper_history_must_be_none(self):
        with self.assertRaises(ValueError):
            self.boss.route(mesh.TaskPacket("5", "bad history", helper_history="FULL_CHAT"))

    def test_consequential_requires_reckoning(self):
        with self.assertRaises(ValueError):
            self.boss.route(mesh.TaskPacket(
                "6", "wrong tier",
                tier=mesh.Tier.WHISPER,
                consequential=True,
            ))

    def test_null_never_becomes_green(self):
        loop = mesh.EvidenceLoop()
        state = loop.add_evidence(mesh.EvidenceRef("ref:1", "test"), proven=None)
        self.assertEqual(state, mesh.Terminal.CONTINUE)
        self.assertNotEqual(state, mesh.Terminal.PROVEN)

    def test_evidence_can_prove(self):
        loop = mesh.EvidenceLoop()
        state = loop.add_evidence(mesh.EvidenceRef("ref:2", "test"), proven=True)
        self.assertEqual(state, mesh.Terminal.PROVEN)

    def test_round_budget_stops_recursive_debate(self):
        loop = mesh.EvidenceLoop()
        self.assertEqual(loop.add_agent_round(), mesh.Terminal.CONTINUE)
        self.assertEqual(loop.add_agent_round(), mesh.Terminal.CONTINUE)
        self.assertEqual(loop.add_agent_round(), mesh.Terminal.CONTINUE)
        self.assertEqual(loop.add_agent_round(), mesh.Terminal.NEEDS_HUMAN)

    def test_hard_budget_contract(self):
        b = mesh.TaskBudget()
        b.validate()
        self.assertEqual(b.max_helpers_per_turn, 3)
        self.assertEqual(b.max_parallel_read_only_helpers, 2)
        self.assertEqual(b.max_delegation_depth, 1)
        self.assertEqual(b.max_evidence_passes, 10)


if __name__ == "__main__":
    unittest.main(verbosity=2)
