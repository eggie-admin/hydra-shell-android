#!/usr/bin/env python3
"""Project Hydra stale-artifact audit.

Report-only by default. --strict fails only structural blockers:
- missing crowned source-contract/directory crown
- proposal accidentally marked crowned/sealed
- active Copilot instructions still contain known stale authority text

It never deletes, renames, builds, installs, publishes, or changes repo state.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CROWN_FILES = [
    ROOT / "project/hydra/source-of-truth/LUHMOS_HYDRA_DIRECTORY_CROWN_20260916.json",
    ROOT / "project/hydra/source-of-truth/LUHM_M1_SIGNED_SECURE_WEBVIEW_SOCKET_20260916.json",
]
PROPOSAL = ROOT / "project/hydra/doctrine/proposed-source-of-truth/KAI9000_PROPOSED_SEAL_DOCTRINE_MUTATION_AUDIT_20260916.json"
COPILOT = ROOT / ".github/copilot-instructions.md"
PROJECT_MANIFEST = ROOT / "project/hydra/project.manifest.json"

STALE_ACTIVE_MARKERS = {
    str(COPILOT.relative_to(ROOT)): [
        "current signed Crown Gate 1.0.5 lane remains the last sealed build baseline",
    ],
}
AUDIT_DEBT_MARKERS = {
    str(PROJECT_MANIFEST.relative_to(ROOT)): [
        '"preferred_public_repo": "IzzyOnDroid"',
        '"baseline_version_code": 100',
        '"device_must_be_rooted_before_install": true',
    ],
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    blockers: list[dict] = []
    debt: list[dict] = []
    checks: list[dict] = []

    for path in CROWN_FILES:
        exists = path.exists()
        checks.append({"check": "crown_present", "path": str(path.relative_to(ROOT)), "ok": exists})
        if not exists:
            blockers.append({"type": "missing_crown", "path": str(path.relative_to(ROOT))})

    if PROPOSAL.exists():
        try:
            proposal = json.loads(read_text(PROPOSAL))
            status = str(proposal.get("status", ""))
            proposal_ok = status.startswith("PROPOSED")
            checks.append({"check": "proposal_not_crowned", "status": status, "ok": proposal_ok})
            if not proposal_ok:
                blockers.append({"type": "proposal_authority_violation", "status": status})
        except json.JSONDecodeError as exc:
            blockers.append({"type": "invalid_proposal_json", "detail": str(exc)})
    else:
        blockers.append({"type": "missing_proposal", "path": str(PROPOSAL.relative_to(ROOT))})

    for rel, markers in STALE_ACTIVE_MARKERS.items():
        text = read_text(ROOT / rel)
        for marker in markers:
            found = marker in text
            checks.append({"check": "active_stale_marker_absent", "path": rel, "marker": marker, "ok": not found})
            if found:
                blockers.append({"type": "active_stale_authority", "path": rel, "marker": marker})

    for rel, markers in AUDIT_DEBT_MARKERS.items():
        text = read_text(ROOT / rel)
        for marker in markers:
            if marker in text:
                debt.append({"type": "compatibility_audit_debt", "path": rel, "marker": marker})

    report = {
        "schema": "luhm-os.stale-artifact-audit-report.v1",
        "mode": "STRICT" if args.strict else "REPORT_ONLY",
        "canonical_branch_expected": "luhmos-main",
        "blockers": blockers,
        "audit_debt": debt,
        "checks": checks,
        "mutated_repo": False,
        "verdict": "BLOCKED" if blockers else ("GREEN_WITH_DEBT" if debt else "GREEN"),
    }
    print(json.dumps(report, indent=2))

    return 1 if args.strict and blockers else 0


if __name__ == "__main__":
    raise SystemExit(main())
