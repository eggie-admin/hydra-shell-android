#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "integrations/vendor-apis.manifest.json"
DOCTRINE = ROOT / "docs/API_TRINITY_DOCTRINE.md"
CF_DEPLOY = ROOT / ".github/workflows/cloudflare-coming-soon.yml"
CF_AUDIT = ROOT / ".github/workflows/cloudflare-ultima-audit.yml"
GCP = ROOT / ".github/workflows/google-white-magic-strict-free-vm.yml"

EXPECTED_SPINE = ["openai", "google", "github", "cloudflare", "hugging_face"]


def require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(f"VENDOR_API_PIPELINE_RED: {message}")


def contains(path: Path, needle: str) -> bool:
    return needle in path.read_text(encoding="utf-8")


def main() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    require(data.get("schema") == "kai9000.vendor-apis.v6", "manifest schema drift")
    require(data.get("vendor_spine") == EXPECTED_SPINE, "five-vendor spine drift")

    providers = data.get("providers", {})
    require(set(providers) == set(EXPECTED_SPINE), "provider key drift")

    openai = providers["openai"]
    require(openai.get("api") == "responses", "OpenAI must use Responses API")
    require(openai.get("endpoint") == "https://api.openai.com/v1/responses", "OpenAI endpoint drift")
    require(openai.get("fast_model") == "gpt-5.6-luna", "OpenAI fast model drift")
    require(openai.get("default_model") == "gpt-5.6-sol", "OpenAI default model drift")
    require(openai.get("credential_env") == "OPENAI_API_KEY", "OpenAI credential contract drift")
    require(openai.get("project_label") == "LuHm OS", "OpenAI project branding drift")
    require(openai.get("persist_project_identifier") is False, "OpenAI project identifiers must not be persisted")

    google = providers["google"]
    cloud = google.get("cloud", {})
    require(cloud.get("auth") == "github_oidc_to_workload_identity_federation", "Google auth drift")
    require(cloud.get("issuer") == "https://token.actions.githubusercontent.com", "Google OIDC issuer drift")
    require(cloud.get("attribute_condition_required") is True, "Google WIF attribute condition must be required")
    require(cloud.get("subject_policy") == "immutable_owner_and_repository_ids_when_issued_by_github", "Google WIF subject policy drift")
    require(cloud.get("long_lived_service_account_json_in_repo") is False, "Google service-account JSON must stay out of repo")
    require(cloud.get("deployment_confirmation") == "PROVISION", "Google deploy confirmation drift")

    github = providers["github"]
    require(github.get("repository") == "eggie-admin/hydra-shell-android", "GitHub repository drift")
    require(github.get("canonical_branch") == "luhmos-main", "GitHub canonical branch drift")
    require(github.get("actions_oidc_issuer") == "https://token.actions.githubusercontent.com", "GitHub OIDC issuer drift")
    require(github.get("pull_request_before_canonical_mutation_required") is True, "GitHub PR gate drift")
    require(github.get("direct_push_should_be_blocked") is True, "GitHub direct-push policy drift")
    observed = github.get("observed_2026_09_17", {})
    require(observed.get("canonical_branch_protected") is False, "recorded GitHub protection state changed; refresh audit")
    require(observed.get("repository_rulesets") == "NONE", "recorded GitHub ruleset state changed; refresh audit")
    require(observed.get("external_governance_state") == "RED_EXTERNAL", "GitHub external governance debt must remain explicit")

    cloudflare = providers["cloudflare"]
    require(cloudflare.get("api_base") == "https://api.cloudflare.com/client/v4", "Cloudflare API base drift")
    require(cloudflare.get("credential_strategy") == "narrowly_scoped_api_tokens", "Cloudflare token policy drift")
    require(cloudflare.get("tunnel_token_is_separate_runtime_secret") is True, "Cloudflare tunnel token boundary drift")
    require(cloudflare.get("production_publish_confirmation") == "YES", "Cloudflare publish confirmation drift")
    require(cloudflare.get("wrangler_version") == "4.119.0", "Cloudflare Wrangler pin drift")
    require(cloudflare.get("router_port_forwarding_required") is False, "Cloudflare router-forwarding drift")

    hf = providers["hugging_face"]
    require(hf.get("api") == "responses_beta", "Hugging Face Responses status drift")
    require(hf.get("base_url") == "https://router.huggingface.co/v1", "Hugging Face router base drift")
    require(hf.get("responses_endpoint") == "https://router.huggingface.co/v1/responses", "Hugging Face Responses endpoint drift")
    require(hf.get("chat_endpoint") == "https://router.huggingface.co/v1/chat/completions", "Hugging Face chat endpoint drift")
    require(hf.get("default_model") == "openai/gpt-oss-120b:fastest", "Hugging Face default model drift")
    require(hf.get("lower_latency_candidate") == "openai/gpt-oss-20b:fastest", "Hugging Face fast model drift")
    require(hf.get("credential_env") == "HF_TOKEN", "Hugging Face credential contract drift")
    require(hf.get("auto_execute_remote_code") is False, "Hugging Face remote code must stay disabled")

    shared = data.get("shared_policy", {})
    for key in (
        "typed_actions_only",
        "approval_binds_exact_plan",
        "execution_evidence_required_for_green",
        "canonical_merge_requires_explicit_professor_authority",
        "deploy_requires_explicit_professor_authority",
        "public_release_requires_explicit_professor_authority",
        "crown_requires_explicit_professor_authority",
    ):
        require(shared.get(key) is True, f"shared policy drift: {key}")
    require(shared.get("remote_provider_failure_does_not_grant_fallback_authority") is True, "cross-provider authority drift")

    doctrine = DOCTRINE.read_text(encoding="utf-8")
    for heading in ("## OpenAI lane", "## Google lane", "## GitHub lane", "## Cloudflare lane", "## Hugging Face lane"):
        require(heading in doctrine, f"missing doctrine heading: {heading}")

    cf_deploy = CF_DEPLOY.read_text(encoding="utf-8")
    require("wrangler@latest" not in cf_deploy, "Cloudflare deploy uses floating Wrangler")
    require(cf_deploy.count("wrangler@4.119.0") == 2, "Cloudflare preview/publish pin mismatch")
    require("test \"$CONFIRM\" = YES" in cf_deploy, "Cloudflare explicit publish confirmation missing")

    cf_audit = CF_AUDIT.read_text(encoding="utf-8")
    require(cf_audit.count("wrangler@4.119.0") == 2, "Cloudflare audit pin mismatch")

    gcp = GCP.read_text(encoding="utf-8")
    require("id-token: write" in gcp, "Google workflow OIDC permission missing")
    require("confirm_provision" in gcp and "PROVISION" in gcp, "Google explicit provision confirmation missing")
    require("google-github-actions/auth@v3" in gcp, "Google auth action contract drift")
    require("GCP_WORKLOAD_IDENTITY_PROVIDER" in gcp, "Google WIF provider variable missing")

    print("LUHM_VENDOR_API_PIPELINE=GREEN")
    print("VENDOR_SPINE=openai,google,github,cloudflare,hugging_face")
    print("GITHUB_EXTERNAL_GOVERNANCE=RED_EXTERNAL_RECORDED")
    print("GOOGLE_WIF_LIVE_STATE=UNVERIFIED_RECORDED")
    print("CLOUDFLARE_LIVE_ACCOUNT=UNVERIFIED_RECORDED")
    print("HUGGING_FACE_LIVE_ACCOUNT=UNVERIFIED_RECORDED")


if __name__ == "__main__":
    main()
