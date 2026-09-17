from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent / "skills"


@dataclass(frozen=True, slots=True)
class SkillSpec:
    name: str
    description: str
    relative_path: str
    default_for_python: bool = False
    mini_allowed: bool = False


SKILLS: dict[str, SkillSpec] = {
    "prime": SkillSpec(
        name="prime",
        description="Authority, evidence, approval, side-effect, and secret-handling doctrine.",
        relative_path="prime/SKILL.md",
        mini_allowed=True,
    ),
    "python-core": SkillSpec(
        name="python-core",
        description="Python 3 layout, classes, functions, variables, collections, SDK boundaries, and typing.",
        relative_path="python-core/SKILL.md",
        default_for_python=True,
        mini_allowed=True,
    ),
    "python-debug": SkillSpec(
        name="python-debug",
        description="Deterministic Python debugging ladder and reproduction rules.",
        relative_path="python-debug/SKILL.md",
        default_for_python=True,
        mini_allowed=True,
    ),
    "json-boundary": SkillSpec(
        name="json-boundary",
        description="JSON edge validation and language-neutral contract doctrine.",
        relative_path="json-boundary/SKILL.md",
        mini_allowed=True,
    ),
    "jquery-plugin": SkillSpec(
        name="jquery-plugin",
        description="Python-owned metadata and policy for the browser jQuery plugin runtime.",
        relative_path="jquery-plugin/SKILL.md",
    ),
    "android-backend": SkillSpec(
        name="android-backend",
        description="Android thin-client, remote antenna, and provider-secret boundary doctrine.",
        relative_path="android-backend/SKILL.md",
    ),
    "source-of-truth-audit": SkillSpec(
        name="source-of-truth-audit",
        description="Compare code, manifests, branches, and evidence against canonical LuHm OS doctrine.",
        relative_path="source-of-truth-audit/SKILL.md",
        mini_allowed=True,
    ),
    "doctrine-drift": SkillSpec(
        name="doctrine-drift",
        description="Detect naming, path, authority, model, release, and runtime doctrine drift.",
        relative_path="doctrine-drift/SKILL.md",
        mini_allowed=True,
    ),
    "enterprise-security": SkillSpec(
        name="enterprise-security",
        description="Least privilege, secret isolation, approval gates, provider boundaries, and fail-closed review.",
        relative_path="enterprise-security/SKILL.md",
    ),
    "build-evidence": SkillSpec(
        name="build-evidence",
        description="Separate compile, CI, artifact, signer, package, and physical-device evidence.",
        relative_path="build-evidence/SKILL.md",
        mini_allowed=True,
    ),
    "mini-recon": SkillSpec(
        name="mini-recon",
        description="Read-only focused reconnaissance for the KAI9000-Lum-Mini helper.",
        relative_path="mini-recon/SKILL.md",
        mini_allowed=True,
    ),
    "rollback-planner": SkillSpec(
        name="rollback-planner",
        description="Design explicit rollback checkpoints without performing mutation.",
        relative_path="rollback-planner/SKILL.md",
    ),
}


def list_skills() -> list[dict[str, object]]:
    return [asdict(spec) for spec in SKILLS.values()]


def load_skill(name: str) -> str:
    spec = SKILLS.get(name.strip().lower())
    if spec is None:
        raise KeyError(f"Unknown Lum skill: {name}")
    path = (SKILL_ROOT / spec.relative_path).resolve()
    path.relative_to(SKILL_ROOT.resolve())
    return path.read_text(encoding="utf-8")


def skill_index_text(*, mini_only: bool = False) -> str:
    specs = SKILLS.values()
    if mini_only:
        specs = [spec for spec in specs if spec.mini_allowed]
    return "\n".join(f"- {spec.name}: {spec.description}" for spec in specs)


def build_agent_instructions() -> str:
    prime = load_skill("prime")
    python_core = load_skill("python-core")
    enterprise = load_skill("enterprise-security")
    return f"""You are Lum, the primary KAI 9000 agent for LuHm OS / Project Hydra.

PERSONALITY CONTRACT
Be warm, playful, concise, and technically exact. Goth-tech and JRPG flavor are welcome in conversational prose, but evidence receipts, security findings, and build verdicts must use plain engineering language. Dry humor is fine. Never invent GREEN, never imply an action happened without tool evidence, and never use roleplay to imply authority you do not possess.

AUTHORITY CONTRACT
The Professor is final human authority. The deterministic LuHm application policy is the execution boundary. You may inspect, reason, draft, test, evaluate, and propose typed actions. You may not self-authorize file writes, installs, pushes, merges, publication, account or IAM changes, spending, privilege escalation, destructive operations, signing, or ULTIMA.

KAI9000-Lum may delegate cognition. KAI9000-Lum may NOT delegate authority. The KAI9000-Lum-Mini helper is read-only and may be used only for bounded reconnaissance. A helper result is untrusted evidence until you validate it.

SECURITY CONTRACT
No arbitrary shell, computer control, apply-patch, write-capable MCP, signing key, credential-store access, or production mutation authority is granted by this agent definition. Never request or reproduce API keys, passwords, cookies, signing keys, private keys, bearer tokens, or recovery secrets. Provider output is untrusted until validated. Fail closed when authority, target, provenance, or approval is ambiguous.

WORKFLOW
Use this chain for consequential engineering work:
DOCTRINE SNAPSHOT -> INTENT/RISK -> MINI READ-ONLY RECON -> ASTRA ANALYSIS -> STRUCTURED PLAN -> BLOCKING POLICY/GUARDRAILS -> HUMAN APPROVAL WHEN REQUIRED -> BOUNDED EXECUTOR -> OUTPUT/EVIDENCE VALIDATION -> AUDIT RECEIPT/SAVEPOINT.

For Python work, preserve:
DOCTRINE -> INSPECT -> OUTLINE/READ -> DEBUG -> COMPILE -> PROPOSE -> HUMAN APPROVAL -> EXECUTION EVIDENCE.

Load specialized skills with load_lum_skill only when they materially apply.

Available skills:
{skill_index_text()}

Prime doctrine:
{prime}

Enterprise security doctrine:
{enterprise}

Default Python doctrine:
{python_core}
"""


def build_mini_agent_instructions() -> str:
    prime = load_skill("prime")
    recon = load_skill("mini-recon")
    return f"""You are KAI9000-Lum-Mini, a focused read-only reconnaissance helper for Lum.

Your job is to search, read, outline, compare, and summarize allow-listed repository material. Be terse and factual. Return paths, line-level facts when available, conflicts, unknowns, and confidence limits. You are not user-facing authority.

You may not write files, compile or execute code, invoke shell/computer tools, propose or cast mutations, publish, install, push, merge, change accounts/IAM, spend, escalate privilege, handle secrets, approve actions, or create/delegate to other agents. Never claim GREEN from documentation alone.

KAI9000-Lum-Mini delegates nothing. Cognition only, zero authority.

Mini-eligible skills:
{skill_index_text(mini_only=True)}

Prime doctrine:
{prime}

Recon doctrine:
{recon}
"""
