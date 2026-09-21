#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "project/hydra/project.manifest.json"
PERF = ROOT / "project/hydra/runtime/performance.policy.json"
ENTERPRISE = ROOT / "project/hydra/runtime/enterprise.policy.json"
CODEOWNERS = ROOT / ".github/CODEOWNERS"


def load(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"ENTERPRISE_GUARD_RED: {message}")


def main() -> int:
    manifest = load(MANIFEST)
    perf = load(PERF)
    ent = load(ENTERPRISE)

    require(manifest.get("branch_authority") == "luhmos-main", "canonical branch drift")
    require(manifest.get("authority", {}).get("final") == "Professor", "human authority drift")
    require(manifest.get("authority", {}).get("secrets_in_repo") is False, "secrets-in-repo invariant weakened")
    require(manifest.get("authority", {}).get("physical_device_proof_required_for_final_android_green") is True,
            "physical-device proof invariant weakened")

    require(ent.get("schema") == "luhm-os.project-hydra.enterprise-policy.v1", "enterprise schema drift")
    require(ent.get("canonical_branch") == "luhmos-main", "enterprise canonical branch drift")
    require(ent.get("human_authority") == "Professor", "enterprise human authority drift")
    require("not a compliance certification" in ent.get("scope_note", "").lower(),
            "enterprise proposal must not masquerade as compliance certification")

    src = ent.get("source_governance", {})
    require(src.get("server_side_branch_protection_required_for_enterprise_green") is True,
            "server-side governance must remain an enterprise-green requirement")
    require(src.get("server_side_branch_protection_observed") is False,
            "proposal must not falsely claim external branch protection")
    require(src.get("direct_canonical_write_default") is False, "direct canonical writes must default off")
    require(src.get("history_rewrite_default") is False, "history rewrite must default off")

    supply = ent.get("supply_chain", {})
    for key in (
        "sbom_required_for_release_candidate",
        "artifact_sha256_required",
        "provenance_receipt_required_for_release_candidate",
        "pin_external_actions_to_immutable_sha",
    ):
        require(supply.get(key) is True, f"supply-chain control missing: {key}")

    secrets = ent.get("secrets_and_identity", {})
    require(secrets.get("secrets_in_repository") is False, "secrets may not enter repository")
    require(secrets.get("release_signing_material_never_printed") is True, "release signing redaction weakened")

    ai = ent.get("ai_governance", {})
    require(ai.get("ai_self_approval") is False, "AI self-approval enabled")
    require(ai.get("ai_output_direct_to_shell") is False, "AI-to-shell enabled")
    require(ai.get("helper_consensus_grants_authority") is False, "helper consensus granted authority")

    bounds = ent.get("promotion_boundaries", {})
    for key in (
        "canonical_merge", "source_of_truth_crown", "release_promotion", "persistent_signing",
        "apk_install", "public_publish", "deploy", "dns_mutation", "billing_mutation"
    ):
        require(bounds.get(key) is False, f"proposal illegally grants {key}")

    measurement = perf.get("measurement_law", {})
    require(measurement.get("performance_claim_requires_measurement") is True,
            "measurement law weakened")
    require(perf.get("promotion", {}).get("public_publish") is False,
            "performance policy silently opens public publish")

    require(CODEOWNERS.exists(), "CODEOWNERS missing")
    codeowners = CODEOWNERS.read_text(encoding="utf-8")
    require("@eggie-admin" in codeowners, "canonical owner missing from CODEOWNERS")
    require("project/hydra/source-of-truth" in codeowners, "source-of-truth ownership rule missing")

    print("PROJECT_HYDRA_ENTERPRISE_SOURCE_GATE_GREEN")
    print("EXTERNAL_BRANCH_PROTECTION_PENDING")
    print("RUNTIME_BENCHMARK_PENDING")
    print("RELEASE_SBOM_PROVENANCE_PENDING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
