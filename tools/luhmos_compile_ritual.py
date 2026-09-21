#!/usr/bin/env python3
"""Deterministic LuHm OS compile ritual gate.

WHAT IS THIS?
A boring little truth machine under the oni costumes. It consumes evidence and
returns the next valid gate. It never talks to GitHub, Drive, a shell, or a
compiler. Network/tool work happens outside this file and arrives as evidence.

WHY DOES IT EXIST?
So an AI helper cannot turn "looks good" into "build it". The state machine
requires source-of-truth freshness, asset provenance, canonical Git evidence,
and forge proof before it will even render a build dry-run.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ALLOWED_RIGHTS = {"KAI_OWNED", "ORIGINAL", "RIGHTS_CLEARED"}
CANONICAL_BRANCH = "luhmos-main"
FINAL_WORKFLOW = ".github/workflows/luhmos-working-demo-candidate.yml"


def _stage(name: str, verdict: str, detail: str) -> dict[str, str]:
    return {"name": name, "verdict": verdict, "detail": detail}


def _result(
    verdict: str,
    state: str,
    stages: list[dict[str, str]],
    *,
    next_gate: str,
    dry_run: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "schema": "luhm_os.compile_ritual.result.v1",
        "verdict": verdict,
        "state": state,
        "stages": stages,
        "dry_run": dry_run,
        "build_dispatched": False,
        "apk_uploaded": False,
        "next_gate": next_gate,
        "authority": {
            "canonical_merge": "NOT_TRIGGERED",
            "final_build": "NOT_TRIGGERED",
            "release_signing": "LOCKED",
            "install": "NOT_TRIGGERED",
            "deploy": "NOT_TRIGGERED",
            "public_release": "NOT_TRIGGERED",
            "crown": "NOT_TRIGGERED",
        },
    }


def evaluate(evidence: dict[str, Any]) -> dict[str, Any]:
    """Evaluate evidence. No I/O, subprocess, network, build, or mutation."""
    stages: list[dict[str, str]] = []
    sot = evidence.get("source_truth") or {}
    assets = evidence.get("assets") or {}
    github = evidence.get("github") or {}

    if sot.get("status") == "RED":
        stages.append(_stage("AUDIT_SOURCE_OF_TRUTH", "RED", "source-of-truth audit failed"))
        return _result("RED", "SOURCE_TRUTH_INVALID", stages, next_gate="REPAIR_SOURCE_TRUTH")

    if not sot.get("latest_document_observed"):
        stages.append(_stage("AUDIT_SOURCE_OF_TRUTH", "AMBER", "latest private canonical doctrine not proven"))
        return _result("AMBER", "SOURCE_TRUTH_DISCOVERY_REQUIRED", stages, next_gate="REFRESH_SOURCE_TRUTH")

    stages.append(_stage("AUDIT_SOURCE_OF_TRUTH", "GREEN", "latest private canonical doctrine observed"))

    required_assets = assets.get("required") or []
    if not required_assets:
        stages.append(_stage("VERIFY_SHIPPABLE_ASSETS", "RED", "no required asset evidence supplied"))
        return _result("RED", "ASSET_EVIDENCE_MISSING", stages, next_gate="AUDIT_ASSET_REGISTRY")

    for item in required_assets:
        rights = item.get("rights_class")
        if rights not in ALLOWED_RIGHTS or item.get("ship_allowed") is not True:
            stages.append(_stage("VERIFY_SHIPPABLE_ASSETS", "RED", f"asset blocked: {item.get('name', '<unnamed>')}"))
            return _result("RED", "ASSET_PROVENANCE_BLOCK", stages, next_gate="REMOVE_OR_CLEAR_ASSET")
        if not item.get("sha256_verified") or not item.get("exists_verified"):
            stages.append(_stage("VERIFY_SHIPPABLE_ASSETS", "RED", f"asset bytes/hash unverified: {item.get('name', '<unnamed>')}"))
            return _result("RED", "ASSET_INTEGRITY_BLOCK", stages, next_gate="VERIFY_ASSET_BYTES")

    if assets.get("blocked_material_in_ship_path") is True:
        stages.append(_stage("VERIFY_SHIPPABLE_ASSETS", "RED", "blocked/quarantined material reached ship path"))
        return _result("RED", "ASSET_FIREWALL_BREACH", stages, next_gate="PURGE_SHIP_PATH_CONTAMINATION")

    stages.append(_stage("VERIFY_SHIPPABLE_ASSETS", "GREEN", f"{len(required_assets)} required asset(s) integrity/provenance green"))

    canonical_sha = github.get("canonical_sha")
    bound_sha = sot.get("bound_canonical_sha")
    if not canonical_sha:
        stages.append(_stage("SOURCE_TRUTH_CURRENTNESS_GATE", "AMBER", "current canonical SHA missing"))
        return _result("AMBER", "GITHUB_HEAD_REFRESH_REQUIRED", stages, next_gate="REFRESH_CANONICAL_HEAD")

    if not bound_sha:
        stages.append(_stage("SOURCE_TRUTH_CURRENTNESS_GATE", "AMBER", "source of truth does not bind the current canonical SHA"))
        return _result("AMBER", "SOURCE_TRUTH_SYNC_REQUIRED", stages, next_gate=f"SYNC_SOURCE_TRUTH_TO_{canonical_sha}")

    if bound_sha != canonical_sha:
        stages.append(_stage("SOURCE_TRUTH_CURRENTNESS_GATE", "AMBER", f"source of truth binds {bound_sha}, canonical is {canonical_sha}"))
        return _result("AMBER", "SOURCE_TRUTH_SYNC_REQUIRED", stages, next_gate=f"SYNC_SOURCE_TRUTH_TO_{canonical_sha}")

    if sot.get("status") != "GREEN":
        stages.append(_stage("SOURCE_TRUTH_CURRENTNESS_GATE", "AMBER", "source-of-truth status is not GREEN"))
        return _result("AMBER", "SOURCE_TRUTH_SYNC_REQUIRED", stages, next_gate="RESOLVE_SOURCE_TRUTH_AMBER")

    stages.append(_stage("SOURCE_TRUTH_CURRENTNESS_GATE", "GREEN", f"source of truth binds canonical {canonical_sha}"))

    if github.get("canonical_branch") != CANONICAL_BRANCH:
        stages.append(_stage("AUDIT_GITHUB_CANONICAL", "RED", "canonical branch drift"))
        return _result("RED", "CANONICAL_BRANCH_DRIFT", stages, next_gate="RECONCILE_BRANCH_AUTHORITY")

    commits = github.get("last_five_commits") or []
    if len(commits) != 5 or commits[0].get("sha") != canonical_sha:
        stages.append(_stage("AUDIT_GITHUB_CANONICAL", "RED", "latest-five commit receipt incomplete or not anchored to canonical head"))
        return _result("RED", "GITHUB_HISTORY_PROOF_FAILED", stages, next_gate="REFRESH_LAST_FIVE_COMMITS")

    if github.get("source_audit") != "GREEN":
        stages.append(_stage("AUDIT_GITHUB_CANONICAL", "AMBER", "source audit is not GREEN"))
        return _result("AMBER", "SOURCE_AUDIT_REQUIRED", stages, next_gate="AUDIT_CANONICAL_SOURCE")

    stages.append(_stage("AUDIT_GITHUB_CANONICAL", "GREEN", "canonical source and latest-five commit receipt green"))

    forge = evidence.get("forge") or {}
    if forge.get("status") != "GREEN":
        stages.append(_stage("AUDIT_COMPILER_FORGE", "AMBER", "compiler forge audit is not GREEN"))
        return _result("AMBER", "FORGE_AUDIT_REQUIRED", stages, next_gate="AUDIT_COMPILER_FORGE")

    forge_requirements = {
        "workflow": FINAL_WORKFLOW,
        "actions_pinned": True,
        "toolchain_hashes_pinned": True,
        "donor_ref_pinned": True,
        "contents_read_only": True,
        "candidate_package_only": True,
        "silent_install": False,
        "public_release": False,
    }
    for key, expected in forge_requirements.items():
        if forge.get(key) != expected:
            stages.append(_stage("AUDIT_COMPILER_FORGE", "RED", f"forge contract drift: {key}"))
            return _result("RED", "FORGE_CONTRACT_DRIFT", stages, next_gate="REPAIR_FORGE_CONTRACT")

    stages.append(_stage("AUDIT_COMPILER_FORGE", "GREEN", "pinned candidate forge contract green"))

    plan = {
        "schema": "luhm_os.compile_ritual.dry_run.v1",
        "source_sha": canonical_sha,
        "canonical_branch": CANONICAL_BRANCH,
        "workflow": FINAL_WORKFLOW,
        "sequence": [
            "recheck_source_truth_binding",
            "recheck_assets",
            "recheck_canonical_head",
            "recheck_last_five_commits",
            "recheck_source_and_forge",
            "ask_professor_final_build_authorization",
            "dispatch_github_build_only_after_authorization",
            "verify_apk",
            "upload_verified_apk_to_google_drive",
        ],
        "mutation": False,
        "github_dispatch": False,
        "google_drive_upload": False,
        "final_authorization_example": f"Compile LuHm OS candidate from {canonical_sha} on GitHub and upload the verified APK to Google Drive.",
        "plain_continue_is_authorization": False,
    }
    stages.append(_stage("DRY_RUN_COMPILE_REQUEST", "GREEN", "deterministic plan rendered; no build dispatched"))
    return _result(
        "GREEN",
        "FINAL_BUILD_AUTHORIZATION_REQUIRED",
        stages,
        next_gate="ASK_PROFESSOR_FOR_FINAL_BUILD",
        dry_run=plan,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="LuHm OS Lum + mini oni compile ritual dry-run gate")
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
    result = evaluate(evidence)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
