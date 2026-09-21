#!/usr/bin/env python3
"""Deterministic Project Hydra fast-path doctrine guard.

This validates latency policy without granting authority or claiming runtime speed.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "project/hydra/project.manifest.json"
POLICY = ROOT / "project/hydra/runtime/performance.policy.json"


def load(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FASTPATH_GUARD_RED: {message}")


def main() -> int:
    manifest = load(MANIFEST)
    policy = load(POLICY)

    require(manifest.get("branch_authority") == "luhmos-main", "canonical branch drift")
    require(policy.get("canonical_branch") == "luhmos-main", "performance policy branch drift")

    authority = manifest.get("authority", {})
    require(authority.get("final") == "Professor", "human authority drift")
    require(authority.get("physical_device_proof_required_for_final_android_green") is True,
            "physical device proof must remain required")
    require(authority.get("secrets_in_repo") is False, "secrets-in-repo invariant weakened")

    android = manifest.get("android_goal", {})
    require(android.get("root_required") is False, "root unexpectedly required")
    require(android.get("normal_package_install") is True, "normal Android install contract changed")

    ai = manifest.get("ai_provider_goal", {})
    require(ai.get("cloud_ai_required_for_base_launch") is False,
            "base launch must remain cloud-independent")
    require(ai.get("static_vendor_secrets_in_apk") is False,
            "static vendor secrets in APK must remain forbidden")
    require(ai.get("openai_api_surface") == "Responses API", "unexpected primary OpenAI API surface")
    require(ai.get("model_ids_are_runtime_configurable") is True, "model IDs must remain runtime configurable")

    invariants = policy.get("invariants", {})
    require(invariants.get("human_approval_required_for_reckoning") is True,
            "RECKONING approval requirement weakened")
    require(invariants.get("public_publish_default") is False, "public publish default changed")
    require(invariants.get("silent_install") is False, "silent install enabled")
    require(invariants.get("ai_output_direct_to_shell") is False, "AI-to-shell enabled")
    require(invariants.get("helper_consensus_grants_authority") is False,
            "helper consensus cannot grant authority")

    routing = policy.get("execution_routing", {})
    require(routing.get("default_helpers") == 0, "default helper fan-out must remain zero")
    require(0 <= int(routing.get("max_parallel_read_only_helpers", -1)) <= 2,
            "read-only helper parallelism exceeds bounded fast path")
    require(int(routing.get("max_delegation_depth", -1)) <= 1,
            "delegation depth exceeds bounded fast path")
    require(int(routing.get("max_ai_rounds", -1)) <= 3,
            "AI round budget exceeds bounded fast path")
    require(routing.get("parallel_reads") is True, "independent read parallelism disabled")
    require(routing.get("parallel_writes") is False, "parallel writes forbidden")
    require(routing.get("single_parent_writer") is True, "single writer contract weakened")
    require(routing.get("deterministic_local_validation_first") is True,
            "deterministic validation must precede remote AI")
    require(routing.get("provider_racing_for_consensus") is False,
            "provider racing for consensus is forbidden")
    require(routing.get("speculative_duplicate_model_calls") is False,
            "speculative duplicate model calls are forbidden")

    source = policy.get("source_resolution", {})
    require(source.get("resolve_once_per_exact_head") is True, "authority must resolve once per head")
    require(source.get("immutable_git_blob_reuse") is True, "immutable blob reuse disabled")
    require(source.get("repeat_same_path_same_sha_fetch") is False,
            "duplicate same-path same-SHA fetches enabled")
    require(source.get("refresh_mutable_refs_before_mutation") is True,
            "mutable refs must refresh before mutation")

    ci = policy.get("ci_strategy", {})
    require(ci.get("focused_changed_path_tests_first") is True,
            "focused tests must run before broad CI")
    require(ci.get("full_exact_head_ci_after_focused_green") is True,
            "exact-head CI requirement weakened")
    require(ci.get("do_not_remove_required_checks_for_speed") is True,
            "speed policy cannot remove required checks")

    runtime = policy.get("runtime_strategy", {})
    require(runtime.get("base_launch_network_independent") is True,
            "base launch became network-dependent")
    require(runtime.get("background_update_check") is False,
            "background update checking enabled")
    require(runtime.get("idle_agent_mesh") is False,
            "idle agent mesh must remain disabled")
    require(runtime.get("one_proof_payload_many_views") is True,
            "proof payload fan-out contract weakened")

    promotion = policy.get("promotion", {})
    status = policy.get("status")
    if status == "PROPOSED_ACTIVE_ON_CANDIDATE_BRANCH":
        require(promotion.get("candidate_branch_only") is True,
                "candidate policy must remain candidate-only")
    elif status == "SEALED_ACTIVE_CANONICAL":
        require(promotion.get("candidate_branch_only") is False,
                "canonical policy still marked candidate-only")
        canonical = policy.get("canonical_state", {})
        require(canonical.get("promoted") is True, "canonical policy missing promotion receipt")
        require(canonical.get("runtime_speedup_proven") is False,
                "canonical metadata cannot claim unmeasured runtime speedup")
        require(canonical.get("benchmark_receipt_pending") is True,
                "benchmark pending state unexpectedly closed")
    else:
        require(False, f"unsupported performance policy status: {status!r}")

    require(promotion.get("canonical_merge_requires_explicit_current_professor_authorization") is True,
            "canonical merge authorization weakened")
    require(promotion.get("source_of_truth_crown_requires_explicit_current_professor_authorization") is True,
            "crown authorization weakened")
    for forbidden in ("release_promotion", "apk_install", "persistent_signing", "public_publish", "dns_mutation", "billing_mutation"):
        require(promotion.get(forbidden) is False, f"{forbidden} unexpectedly authorized")

    print("PROJECT_HYDRA_FASTPATH_GUARD_GREEN")
    print(f"policy_status={status}")
    print("authority=Professor")
    print("branch=luhmos-main")
    print("helpers=0_default/2_parallel_readonly_max")
    print("delegation_depth=1_max")
    print("ai_rounds=3_max")
    print("parallel_writes=false")
    print("cloud_required_for_base_launch=false")
    print("ai_to_shell=false")
    print("public_publish=false")
    print("runtime_speed_claim=MEASUREMENT_REQUIRED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
