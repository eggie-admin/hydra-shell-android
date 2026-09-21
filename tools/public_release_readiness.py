#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ruleset-count", type=int, default=0)
    parser.add_argument("--signer-secrets-ready", choices=("true", "false"), default="false")
    parser.add_argument("--git-restore-green", choices=("true", "false"), default="false")
    parser.add_argument("--source-sbom-green", choices=("true", "false"), default="false")
    parser.add_argument("--benchmark-green", choices=("true", "false"), default="false")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--output", default="release/LUHM_OS_PUBLIC_RELEASE_READINESS.json")
    args = parser.parse_args()

    enterprise = load("project/hydra/runtime/enterprise.policy.json")
    topology = load("project/hydra/LUHMOS_BRANCH_TOPOLOGY.json")
    channels = load("admin/release/release-channels.json")
    publication = load("fdroid/publication.manifest.json")

    expected_order = ["testing", "proposed", "beta", "stable"]
    topology_order = [branch.split("/")[-1] for branch in topology["promotion_order"][1:]]
    deterministic_checks = {
        "enterprise_policy_active": enterprise.get("status") == "SEALED_ACTIVE_CANONICAL",
        "canonical_branch": topology.get("canonical_integration") == "luhmos-main",
        "promotion_order_aligned": channels.get("promotion_order") == expected_order and topology_order == expected_order,
        "package_identity": channels.get("package") == "art.eggiebagelface.luhmos" == publication.get("package_id"),
        "source_publication_separated": bool(channels.get("semantics", {}).get("source_lane_is_not_publication")),
        "signing_host_present": (ROOT / "fdroid/trusted-signing-host.sh").is_file(),
        "github_release_guard_present": (ROOT / ".github/workflows/luhmos-github-release.yml").is_file(),
        "fdroid_publication_contract_present": (ROOT / "fdroid/publication.manifest.json").is_file(),
    }

    preflight = {
        "source_sbom_green": args.source_sbom_green == "true",
        "git_restore_drill_green": args.git_restore_green == "true",
        "routing_benchmark_green": args.benchmark_green == "true",
    }

    external = {
        "github_ruleset_count": args.ruleset_count,
        "server_side_governance_green": args.ruleset_count > 0,
        "release_signer_secrets_ready": args.signer_secrets_ready == "true",
        "signed_release_apk_present": False,
        "artifact_bound_sbom_present": False,
        "artifact_bound_provenance_present": False,
        "physical_samsung_install_launch_green": False,
        "same_signer_upgrade_green": False,
        "izzyondroid_accepted": False,
    }

    blockers: list[str] = []
    if not all(deterministic_checks.values()):
        blockers.append("deterministic_source_contract_failure")
    if not preflight["source_sbom_green"]:
        blockers.append("source_sbom_preflight_missing")
    if not preflight["git_restore_drill_green"]:
        blockers.append("git_restore_drill_missing")
    if not preflight["routing_benchmark_green"]:
        blockers.append("runtime_routing_benchmark_missing")
    if not external["server_side_governance_green"]:
        blockers.append("server_side_branch_ruleset_missing")
    if not external["release_signer_secrets_ready"]:
        blockers.append("persistent_release_signer_not_configured_or_not_proven")
    if not external["signed_release_apk_present"]:
        blockers.append("signed_release_apk_missing")
    if not external["artifact_bound_sbom_present"]:
        blockers.append("artifact_bound_sbom_missing")
    if not external["artifact_bound_provenance_present"]:
        blockers.append("artifact_bound_provenance_missing")
    if not external["physical_samsung_install_launch_green"]:
        blockers.append("physical_samsung_install_launch_proof_missing")

    receipt = {
        "schema": "luhm-os.public-release-readiness.v1",
        "project": "LuHm OS",
        "package": "art.eggiebagelface.luhmos",
        "source_sha": os.environ.get("GITHUB_SHA"),
        "source_ref": os.environ.get("GITHUB_REF_NAME"),
        "deterministic_checks": deterministic_checks,
        "preflight_evidence": preflight,
        "external_and_artifact_gates": external,
        "public_release_ready": not blockers,
        "blockers": blockers,
        "result": "PUBLIC_RELEASE_GREEN" if not blockers else "ENTERPRISE_PREFLIGHT_GREEN_PUBLIC_RELEASE_BLOCKED",
        "evidence_boundary": "Source/preflight evidence never implies signed artifact, physical device, IzzyOnDroid, or public-release GREEN.",
    }

    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))

    if not all(deterministic_checks.values()):
        return 1
    if args.strict and blockers:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
