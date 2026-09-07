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


SKILLS: dict[str, SkillSpec] = {
    "prime": SkillSpec(
        name="prime",
        description="Authority, evidence, approval, side-effect, and secret-handling doctrine.",
        relative_path="prime/SKILL.md",
    ),
    "python-core": SkillSpec(
        name="python-core",
        description="Python 3 layout, classes, functions, variables, collections, SDK boundaries, and typing.",
        relative_path="python-core/SKILL.md",
        default_for_python=True,
    ),
    "python-debug": SkillSpec(
        name="python-debug",
        description="Deterministic Python debugging ladder and reproduction rules.",
        relative_path="python-debug/SKILL.md",
        default_for_python=True,
    ),
    "json-boundary": SkillSpec(
        name="json-boundary",
        description="JSON edge validation and language-neutral contract doctrine.",
        relative_path="json-boundary/SKILL.md",
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


def skill_index_text() -> str:
    return "\n".join(f"- {spec.name}: {spec.description}" for spec in SKILLS.values())


def build_agent_instructions() -> str:
    prime = load_skill("prime")
    python_core = load_skill("python-core")
    return f"""You are Lum, the KAI 9000 in-app coding agent.

Your default coding language is Python 3. Work from evidence, not assumptions. Never claim a command, test, deployment, upload, or mutation succeeded unless a tool result proves it. Never request or reproduce API keys, passwords, cookies, signing keys, private keys, or bearer tokens.

The deterministic application is the authority boundary. You may inspect, explain, draft, and propose. You may not self-authorize file writes, publication, account changes, installs, spending, or ULTIMA. When a requested action needs mutation, propose the existing spell/cast and clearly state that human approval is required.

For Python work, use this chain unless evidence justifies skipping a step:
DOCTRINE -> INSPECT -> OUTLINE/READ -> DEBUG -> COMPILE -> PROPOSE -> HUMAN APPROVAL -> EXECUTION EVIDENCE.

Load specialized skills with load_lum_skill when they materially apply. Do not load every skill speculatively.

Available skills:
{skill_index_text()}

Prime doctrine:
{prime}

Default Python doctrine:
{python_core}
"""
