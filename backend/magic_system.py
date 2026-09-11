from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Final


class Risk(str, Enum):
    READ_ONLY = "read_only"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    RELEASE = "release"


@dataclass(frozen=True)
class SpellPlan:
    spell: str
    intent: str
    lane: str
    risk: Risk
    requires_ci_green: bool
    requires_human_approval: bool
    may_write_source: bool
    may_promote_release: bool
    action: str

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["risk"] = self.risk.value
        return data


SPELLBOOK: Final[dict[str, SpellPlan]] = {
    "libra": SpellPlan(
        spell="LIBRA",
        intent="inspect",
        lane="read-only",
        risk=Risk.READ_ONLY,
        requires_ci_green=False,
        requires_human_approval=False,
        may_write_source=False,
        may_promote_release=False,
        action="Inspect repo state, source-of-truth, CI, diffs, versions, signing metadata, and device/build health. Never mutate.",
    ),
    "scan": SpellPlan(
        spell="SCAN",
        intent="audit",
        lane="read-only",
        risk=Risk.READ_ONLY,
        requires_ci_green=False,
        requires_human_approval=False,
        may_write_source=False,
        may_promote_release=False,
        action="Run bounded sanity/audit checks and return evidence. Never mutate.",
    ),
    "cure": SpellPlan(
        spell="CURE",
        intent="hotfix",
        lane="work-lane",
        risk=Risk.LOW,
        requires_ci_green=True,
        requires_human_approval=False,
        may_write_source=True,
        may_promote_release=False,
        action="Make the smallest targeted hotfix on the appropriate work lane, add/update tests, and open or update a PR into luhmos-main.",
    ),
    "cura": SpellPlan(
        spell="CURA",
        intent="patch",
        lane="work-lane-to-testing",
        risk=Risk.MEDIUM,
        requires_ci_green=True,
        requires_human_approval=False,
        may_write_source=True,
        may_promote_release=False,
        action="Apply a bounded multi-file patch, preserve API contracts, run lane CI, converge through luhmos-main, then stage only to luhmos/testing after GREEN.",
    ),
    "curaga": SpellPlan(
        spell="CURAGA",
        intent="full-mutation",
        lane="multi-lane",
        risk=Risk.HIGH,
        requires_ci_green=True,
        requires_human_approval=True,
        may_write_source=True,
        may_promote_release=False,
        action="Perform a coordinated architecture mutation across AI/frontend/backend/platform lanes. Require explicit mutation scope, tests, migration/rollback notes, and human approval before convergence.",
    ),
    "meteo": SpellPlan(
        spell="METEO",
        intent="stage-green",
        lane="luhmos/testing",
        risk=Risk.MEDIUM,
        requires_ci_green=True,
        requires_human_approval=False,
        may_write_source=True,
        may_promote_release=False,
        action="Commit an already-reviewed change, converge it into luhmos-main, fast-forward or PR it to luhmos/testing, and invoke staging CI. Stop on any non-GREEN gate.",
    ),
    "ultima": SpellPlan(
        spell="ULTIMA",
        intent="finale-compile",
        lane="remote-forge",
        risk=Risk.RELEASE,
        requires_ci_green=True,
        requires_human_approval=True,
        may_write_source=False,
        may_promote_release=False,
        action="Invoke the approved GitHub remote compile/release forge for the selected GREEN commit. Verify package identity, signing certificate, API/ABI, 16 KB alignment, artifact hash, and provenance. ULTIMA never silently merges or promotes stable.",
    ),
    "esuna": SpellPlan(
        spell="ESUNA",
        intent="harden-cleanup",
        lane="work-lane",
        risk=Risk.MEDIUM,
        requires_ci_green=True,
        requires_human_approval=False,
        may_write_source=True,
        may_promote_release=False,
        action="Remove stale dependencies/configuration, secrets exposure, dead deployment paths, and policy drift without adding features.",
    ),
    "phoenix": SpellPlan(
        spell="PHOENIX",
        intent="rollback",
        lane="rollback",
        risk=Risk.HIGH,
        requires_ci_green=False,
        requires_human_approval=True,
        may_write_source=True,
        may_promote_release=False,
        action="Revert to a named sealed GREEN commit/artifact using an auditable revert or ref restoration. Never guess the rollback target.",
    ),
}

ALIASES: Final[dict[str, str]] = {
    "meteor": "meteo",
    "full cure": "curaga",
    "compile": "ultima",
    "status": "libra",
    "audit": "scan",
}


def normalize_spell(text: str) -> str:
    value = " ".join(text.strip().lower().split())
    return ALIASES.get(value, value)


def compile_spell(text: str) -> SpellPlan:
    key = normalize_spell(text)
    try:
        return SPELLBOOK[key]
    except KeyError as exc:
        raise ValueError(f"Unknown or unauthorized spell: {text!r}") from exc


def authorize_spell(text: str, *, human_approved: bool = False, ci_green: bool = False) -> dict[str, object]:
    plan = compile_spell(text)
    blocked: list[str] = []
    if plan.requires_human_approval and not human_approved:
        blocked.append("human_approval_required")
    if plan.requires_ci_green and not ci_green and plan.spell not in {"CURE", "CURA", "CURAGA", "METEO"}:
        blocked.append("ci_green_required")
    return {
        "ok": not blocked,
        "blocked_by": blocked,
        "plan": plan.to_dict(),
    }
