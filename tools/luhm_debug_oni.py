#!/usr/bin/env python3
"""LuHm OS proposed debugging oni.

Read-only repository auditor. It never shells out, writes project files, changes refs,
uses secrets, signs artifacts, publishes releases, or grants itself authority.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOT = ROOT / "project/hydra/source-of-truth"
ANDROID = ROOT / "project/hydra/samsung/android"


@dataclass(frozen=True)
class Finding:
    name: str
    status: str
    evidence: str


def text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return ""


def contains(path: Path, needle: str) -> bool:
    return needle in text(path)


def main() -> int:
    findings: list[Finding] = []

    golden = SOT / "LUHM_OS_GOLDEN_BETA_NO_BACKTRACK_CROWN_20260922.json"
    pipeline = SOT / "LUHM_OS_PIPELINE_UNIFICATION_CROWN_20260921.json"
    sot_readme = SOT / "README.md"
    cage = ANDROID / "forge/scripts/cage_manager.gd"
    bridge = ANDROID / "forge/scripts/web_cms_bridge.gd"
    cathedral = ANDROID / "cathedral-game/crown-cathedral.js"
    pysimple = SOT / "LUHM_OS_PYSIMPLEGUI_MINIMAL_GUI_PROPOSAL_20260922.json"
    harness = ANDROID / "cathedral-game/python/src/luhm_core/local_harness.py"

    for name, path in (
        ("golden_crown_present", golden),
        ("pipeline_crown_present", pipeline),
        ("sot_readme_present", sot_readme),
    ):
        findings.append(Finding(name, "GREEN" if path.is_file() else "RED", str(path.relative_to(ROOT))))

    if golden.is_file():
        g = text(golden)
        invariants = {
            "golden_version": '"version_name": "1.0.10-beta.1"',
            "golden_code": '"version_code": 110',
            "golden_package": "art.eggiebagelface.luhmos",
            "golden_sha": "a2243d68fa1aaa2f554ef74d9a1edd32530c12ac",
        }
        for key, needle in invariants.items():
            findings.append(Finding(key, "GREEN" if needle in g else "RED", needle))

    findings.append(Finding(
        "native_3d_harness_marker",
        "GREEN" if contains(cage, "LUHM_NATIVE_3D_HARNESS_V1") else "YELLOW",
        str(cage.relative_to(ROOT)),
    ))
    findings.append(Finding(
        "multi_tier_bridge_marker",
        "GREEN" if contains(bridge, "LUHM_MULTI_TIER_BRIDGE_V1") else "YELLOW",
        str(bridge.relative_to(ROOT)),
    ))
    findings.append(Finding(
        "cathedral_world_bridge_marker",
        "GREEN" if contains(cathedral, "LUHM_NATIVE_3D_WORLD_BRIDGE_V1") else "YELLOW",
        str(cathedral.relative_to(ROOT)),
    ))
    findings.append(Finding(
        "pysimplegui_is_proposal_only",
        "GREEN" if contains(pysimple, "PROPOSED_NOT_CROWNED") else "YELLOW",
        str(pysimple.relative_to(ROOT)),
    ))

    # The frozen Crown bans a public Android loopback control plane. A development-only
    # local harness is therefore never promoted silently; it is reported as YELLOW.
    harness_text = text(harness)
    loopback = bool(re.search(r"127\.0\.0\.1|localhost|loopback", harness_text, re.I))
    findings.append(Finding(
        "loopback_release_conflict",
        "YELLOW" if loopback else "GREEN",
        "development harness contains loopback semantics; explicit architecture Crown required before release"
        if loopback else "no loopback marker found in local harness",
    ))

    # Lightweight tracked-secret smell scan. Do not print matching values.
    secret_patterns = [re.compile(r"sk-proj-[A-Za-z0-9_-]{20,}"), re.compile(r"AIza[0-9A-Za-z_-]{20,}")]
    secret_hits: list[str] = []
    for base in (ROOT / "project", ROOT / "tools"):
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.stat().st_size > 2_000_000:
                continue
            body = text(path)
            if any(p.search(body) for p in secret_patterns):
                secret_hits.append(str(path.relative_to(ROOT)))
    findings.append(Finding(
        "tracked_secret_smell",
        "RED" if secret_hits else "GREEN",
        ", ".join(secret_hits) if secret_hits else "no OpenAI/Google key-shaped strings found in scanned tracked text",
    ))

    red = sum(f.status == "RED" for f in findings)
    yellow = sum(f.status == "YELLOW" for f in findings)
    result = "RED" if red else ("YELLOW" if yellow else "GREEN")
    report = {
        "schema": "luhm-os.debug-oni.dry-run.v1",
        "oni": "Kuroko",
        "mode": "READ_ONLY_DRY_RUN",
        "authority": "NONE",
        "recursive_recruiting": False,
        "mutation": False,
        "release_publish": False,
        "result": result,
        "red": red,
        "yellow": yellow,
        "findings": [asdict(f) for f in findings],
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 2 if red else 0


if __name__ == "__main__":
    raise SystemExit(main())
