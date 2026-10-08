from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Callable


MAX_EVIDENCE_PASSES = 10
MAX_AGENT_ROUNDS = 3


class Condition(StrEnum):
    """Terminal truth states for the deterministic LuHm FOR LOOP."""

    NULL = "NULL"
    PROVEN = "PROVEN"
    BLOCKED = "BLOCKED"
    CROWN_REQUIRED = "CROWN_REQUIRED"
    NEEDS_HUMAN = "NEEDS_HUMAN"


@dataclass(frozen=True)
class EvidenceState:
    """One normalized evidence snapshot.

    This object contains evidence state only. It carries no execution authority.
    """

    proof_complete: bool = False
    contradictions: tuple[str, ...] = ()
    blockers: tuple[str, ...] = ()
    missing_evidence: tuple[str, ...] = ()
    crown_required: bool = False


@dataclass(frozen=True)
class ForLoopResult:
    condition: Condition
    passes: int
    evidence: EvidenceState


def classify_condition(state: EvidenceState) -> Condition:
    """Classify one pass without guessing through missing or conflicting evidence."""

    if state.crown_required:
        return Condition.CROWN_REQUIRED
    if state.blockers:
        return Condition.BLOCKED
    if (
        state.proof_complete
        and not state.contradictions
        and not state.missing_evidence
    ):
        return Condition.PROVEN
    return Condition.NULL


def run_for_loop(
    inspect: Callable[[int], EvidenceState],
    *,
    max_passes: int = MAX_EVIDENCE_PASSES,
) -> ForLoopResult:
    """Run bounded evidence acquisition until a deterministic terminal state.

    NULL means "not proven yet" and must never be promoted to success by model
    confidence, retries, roleplay, provider consensus, or elapsed time.

    The caller owns evidence acquisition. This function cannot mutate source,
    execute shell commands, contact providers, or grant Crown authority.
    """

    if not 1 <= max_passes <= MAX_EVIDENCE_PASSES:
        raise ValueError(f"max_passes must be between 1 and {MAX_EVIDENCE_PASSES}")

    last = EvidenceState(missing_evidence=("initial_evidence",))

    for pass_number in range(1, max_passes + 1):
        state = inspect(pass_number)
        if not isinstance(state, EvidenceState):
            raise TypeError("inspect() must return EvidenceState")

        last = state
        condition = classify_condition(state)
        if condition is not Condition.NULL:
            return ForLoopResult(
                condition=condition,
                passes=pass_number,
                evidence=state,
            )

    return ForLoopResult(
        condition=Condition.NEEDS_HUMAN,
        passes=max_passes,
        evidence=last,
    )
