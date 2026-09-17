"""LuHm Agent Mesh v1 deterministic policy core.

One Boss speaks to the Professor. Helpers are bounded blades. This module owns
routing policy only: it performs no network, shell, install, publish, or repo
mutation. Provider clients live outside this boundary.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
import argparse
import json
from typing import Iterable


class Tier(str, Enum):
    WHISPER = "WHISPER"
    CROSSING = "CROSSING"
    RECKONING = "RECKONING"


class Blade(str, Enum):
    DIRECT = "DIRECT"
    CONTEXT = "CONTEXT"
    BUILD = "BUILD"
    RESEARCH = "RESEARCH"
    CRITIC = "CRITIC"
    TOOL_EXECUTOR = "TOOL_EXECUTOR"


class Terminal(str, Enum):
    PROVEN = "PROVEN"
    BLOCKED = "BLOCKED"
    CROWN_REQUIRED = "CROWN_REQUIRED"
    NEEDS_HUMAN = "NEEDS_HUMAN"
    CONTINUE = "CONTINUE"


@dataclass(frozen=True)
class TaskBudget:
    max_helpers_per_turn: int = 3
    max_parallel_read_only_helpers: int = 2
    max_delegation_depth: int = 1
    max_countervoices: int = 1
    max_ai_to_ai_rounds: int = 3
    max_evidence_passes: int = 10

    def validate(self) -> None:
        if self.max_helpers_per_turn != 3:
            raise ValueError("LuHm Agent Mesh v1 hard cap is 3 helpers")
        if self.max_parallel_read_only_helpers != 2:
            raise ValueError("LuHm Agent Mesh v1 read-only parallel cap is 2")
        if self.max_delegation_depth != 1:
            raise ValueError("recursive helper delegation is forbidden")
        if self.max_ai_to_ai_rounds > 3:
            raise ValueError("Parley round budget cannot exceed 3")
        if self.max_evidence_passes > 10:
            raise ValueError("FOR LOOP evidence budget cannot exceed 10")


@dataclass(frozen=True)
class EvidenceRef:
    ref: str
    kind: str
    summary: str = ""
    sha256: str | None = None


@dataclass(frozen=True)
class TaskPacket:
    task_id: str
    goal: str
    tier: Tier = Tier.WHISPER
    needs_context: bool = False
    needs_build: bool = False
    needs_research: bool = False
    consequential: bool = False
    explicit_professor_authorization: bool = False
    read_only: bool = True
    helper_history: str = "NONE"
    evidence_refs: tuple[EvidenceRef, ...] = ()

    def validate(self) -> None:
        if not self.task_id.strip() or not self.goal.strip():
            raise ValueError("task_id and goal are required")
        if self.helper_history != "NONE":
            raise ValueError("helpers receive typed packets, not copied chat history")
        if self.consequential and self.tier is not Tier.RECKONING:
            raise ValueError("consequential work must be classified RECKONING")


@dataclass(frozen=True)
class RouteDecision:
    boss: str
    route: Blade
    helpers: tuple[Blade, ...]
    critic_required: bool
    tool_edge_allowed: bool
    terminal: Terminal
    reason: str
    budget: TaskBudget = field(default_factory=TaskBudget)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["route"] = self.route.value
        d["helpers"] = [x.value for x in self.helpers]
        d["terminal"] = self.terminal.value
        return d


class LumBoss:
    """Deterministic routing spine. Provider-independent and fail-closed."""

    name = "Lum"

    def __init__(self, budget: TaskBudget | None = None) -> None:
        self.budget = budget or TaskBudget()
        self.budget.validate()

    def route(self, packet: TaskPacket) -> RouteDecision:
        packet.validate()

        requested: list[Blade] = []
        if packet.needs_context:
            requested.append(Blade.CONTEXT)
        if packet.needs_build:
            requested.append(Blade.BUILD)
        if packet.needs_research:
            requested.append(Blade.RESEARCH)

        # Direct questions bypass the mesh entirely.
        if not requested and not packet.consequential:
            return RouteDecision(
                boss=self.name,
                route=Blade.DIRECT,
                helpers=(),
                critic_required=False,
                tool_edge_allowed=False,
                terminal=Terminal.CONTINUE,
                reason="direct fastpath: no helper or tool edge required",
                budget=self.budget,
            )

        if len(requested) > self.budget.max_helpers_per_turn:
            return RouteDecision(
                boss=self.name,
                route=Blade.DIRECT,
                helpers=tuple(requested[: self.budget.max_helpers_per_turn]),
                critic_required=True,
                tool_edge_allowed=False,
                terminal=Terminal.NEEDS_HUMAN,
                reason="helper request exceeds hard budget",
                budget=self.budget,
            )

        critic = packet.consequential or len(requested) > 1
        tool_allowed = (
            packet.consequential
            and packet.tier is Tier.RECKONING
            and packet.explicit_professor_authorization
        )

        if packet.consequential and not tool_allowed:
            return RouteDecision(
                boss=self.name,
                route=requested[0] if requested else Blade.CRITIC,
                helpers=tuple(requested),
                critic_required=True,
                tool_edge_allowed=False,
                terminal=Terminal.CROWN_REQUIRED,
                reason="RECKONING action lacks exact Professor authorization",
                budget=self.budget,
            )

        primary = requested[0] if requested else Blade.TOOL_EXECUTOR
        return RouteDecision(
            boss=self.name,
            route=primary,
            helpers=tuple(requested),
            critic_required=critic,
            tool_edge_allowed=tool_allowed,
            terminal=Terminal.CONTINUE,
            reason="bounded typed route selected; helpers return evidence to Lum Boss",
            budget=self.budget,
        )


@dataclass
class EvidenceLoop:
    """FOR LOOP truth accumulator below the Boss Spine."""

    budget: TaskBudget = field(default_factory=TaskBudget)
    passes: int = 0
    agent_rounds: int = 0
    terminal: Terminal = Terminal.CONTINUE
    evidence: list[EvidenceRef] = field(default_factory=list)

    def add_evidence(self, evidence: EvidenceRef, *, proven: bool | None = None, blocked: bool = False) -> Terminal:
        if self.terminal is not Terminal.CONTINUE:
            return self.terminal
        if self.passes >= self.budget.max_evidence_passes:
            self.terminal = Terminal.NEEDS_HUMAN
            return self.terminal
        self.passes += 1
        self.evidence.append(evidence)
        if blocked:
            self.terminal = Terminal.BLOCKED
        elif proven is True:
            self.terminal = Terminal.PROVEN
        # proven=None deliberately remains CONTINUE. NULL never becomes GREEN.
        return self.terminal

    def add_agent_round(self) -> Terminal:
        if self.agent_rounds >= self.budget.max_ai_to_ai_rounds:
            self.terminal = Terminal.NEEDS_HUMAN
            return self.terminal
        self.agent_rounds += 1
        return self.terminal


def smoke_cases() -> list[dict]:
    boss = LumBoss()
    cases: Iterable[TaskPacket] = (
        TaskPacket("direct", "answer a simple question"),
        TaskPacket("context", "restore source truth", needs_context=True),
        TaskPacket("research", "check current docs", needs_research=True),
        TaskPacket("build", "inspect build candidate", needs_build=True),
        TaskPacket(
            "blocked-mutation",
            "push release",
            tier=Tier.RECKONING,
            consequential=True,
            read_only=False,
        ),
        TaskPacket(
            "authorized-mutation",
            "stage explicitly authorized candidate action",
            tier=Tier.RECKONING,
            consequential=True,
            explicit_professor_authorization=True,
            read_only=False,
        ),
    )
    return [{"task_id": c.task_id, **boss.route(c).to_dict()} for c in cases]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    if args.smoke:
        print(json.dumps({"seal": "LUHM_AGENT_MESH_V1", "cases": smoke_cases()}, indent=2))
        return 0
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
