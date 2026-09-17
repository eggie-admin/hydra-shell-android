#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "integrations/vendor-apis.manifest.json"
PROJECT_MANIFEST = ROOT / "lumh-os/kai9000/project.manifest.json"
DOCTRINE = ROOT / "docs/API_TRINITY_DOCTRINE.md"
CF_DEPLOY = ROOT / ".github/workflows/cloudflare-coming-soon.yml"
CF_AUDIT = ROOT / ".github/workflows/cloudflare-ultima-audit.yml"
GCP_PROVISION = ROOT / ".github/workflows/google-white-magic-strict-free-vm.yml"
GCP_OIDC_SMOKE = ROOT / ".github/workflows/luhmos-gcp-oidc-smoke.yml"
GCP_BOOTSTRAP = ROOT / "infra/gcp/bootstrap-github-wif.sh"
REMOTE_AI_SMOKE = ROOT / ".github/workflows/kai9000-remote-ai-smoke.yml"

EXPECTED_SPINE = ["openai", "google", "github", "cloudflare", "hugging_face"]
EXPECTED_GCP_VARS = ["GCP_PROJECT_ID", "GCP_WIF_PROVIDER", "GCP_SERVICE_ACCOUNT"]
PROJECT_NAME = "LuHm OS"
PROJECT_ID = "luhm_os"


def require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(f"VENDOR_API_PIPELINE_RED: {message}")


def require_project_binding(provider: dict, provider_name: str) -> None:
    require(provider.get("project_label") == PROJECT_NAME, f"{provider_name} project label drift")
    require(provider.get("logical_project_id") == PROJECT_ID, f"{provider_name} logical project id drift")


def main() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    require(data.get("schema") == "luhm-os.vendor-apis.v7", "manifest schema drift")
    require(data.get("project_display_name") == PROJECT_NAME, "canonical project display name drift")
    require(data.get("project_id") == PROJECT_ID, "canonical project id drift")
    require(data.get("vendor_spine") == EXPECTED_SPINE, "five-vendor spine drift")

    unified = data.get("unified_project", {})
    require(unified.get("display_name") == PROJECT_NAME, "unified project name drift")
    require(unified.get("machine_id") == PROJECT_ID, "unified project machine id drift")
    require(unified.get("policy") == "one_logical_project_many_vendor_transport_bindings", "unified project policy drift")
    require(unified.get("new_vendor_resources_must_use_display_name") == PROJECT_NAME, "new vendor project naming drift")
    require(unified.get("immutable_or_breaking_vendor_ids_may_remain_as_transport_bindings") is True, "transport binding policy drift")
    aliases = set(unified.get("legacy_aliases", []))
    require({"Project Hydra", "KAI 9000", "Hydra"}.issubset(aliases), "legacy alias registry drift")
    require(unified.get("legacy_alias_policy") == "history_or_component_only_never_new_vendor_target", "legacy alias policy drift")

    project = json.loads(PROJECT_MANIFEST.read_text(encoding="utf-8"))
    require(project.get("schema") == "luhm-os.project.v4", "project manifest schema drift")
    require(project.get("name") == PROJECT_NAME, "project manifest name drift")
    require(project.get("project_id") == PROJECT_ID, "project manifest id drift")
    identity = project.get("identity", {})
    require(identity.get("canonical_display_name") == PROJECT_NAME, "project identity display-name drift")
    require(identity.get("canonical_machine_id") == PROJECT_ID, "project identity machine-id drift")
    require(identity.get("legacy_alias_policy") == "component_or_history_only_not_independent_vendor_project", "legacy project authority drift")
    components = project.get("components", {})
    for component in ("kai9000", "hydra", "cathedral"):
        require(components.get(component, {}).get("is_independent_vendor_project") is False, f"{component} escaped unified project")
    require(project.get("remote", {}).get("github", {}).get("branch") == "luhmos-main", "project manifest GitHub branch drift")
    project_openai = project.get("remote", {}).get("openai", {})
    require(project_openai.get("project_label") == PROJECT_NAME, "project manifest OpenAI label drift")
    require(project_openai.get("fast_model") == "gpt-5.6-luna", "project manifest OpenAI fast model drift")
    require(project_openai.get("default_model") == "gpt-5.6-sol", "project manifest OpenAI default model drift")
    require("gpt-6-astra" not in PROJECT_MANIFEST.read_text(encoding="utf-8"), "retired OpenAI model resurrected")

    providers = data.get("providers", {})
    require(set(providers) == set(EXPECTED_SPINE), "provider key drift")
    for provider_name in EXPECTED_SPINE:
        require_project_binding(providers[provider_name], provider_name)

    openai = providers["openai"]
    require(openai.get("api") == "responses", "OpenAI must use Responses API")
    require(openai.get("endpoint") == "https://api.openai.com/v1/responses", "OpenAI endpoint drift")
    require(openai.get("fast_model") == "gpt-5.6-luna", "OpenAI fast model drift")
    require(openai.get("default_model") == "gpt-5.6-sol", "OpenAI default model drift")
    require(openai.get("credential_env") == "OPENAI_API_KEY", "OpenAI credential contract drift")
    require(openai.get("persist_project_identifier") is False, "OpenAI project identifiers must not be persisted")
    require(openai.get("observed_primary_project") == PROJECT_NAME, "OpenAI primary project target drift")
    require(openai.get("observed_legacy_project") == "Project Hydra", "OpenAI legacy-project observation drift")
    require(openai.get("legacy_project_policy") == "do_not_target_for_new_keys_or_new_work", "OpenAI legacy-project routing drift")
    require(openai.get("live_inference_state") == "NOT_VERIFIED_SECRET_ABSENT_IN_CI_SMOKE", "OpenAI live-inference debt must remain explicit until exercised")

    google = providers["google"]
    cloud = google.get("cloud", {})
    require(cloud.get("auth") == "github_oidc_to_workload_identity_federation", "Google auth drift")
    require(cloud.get("issuer") == "https://token.actions.githubusercontent.com", "Google OIDC issuer drift")
    require(cloud.get("attribute_condition_required") is True, "Google WIF attribute condition must be required")
    require(cloud.get("immutable_github_subject_required") is True, "Google must require immutable GitHub subject")
    require(cloud.get("subject_policy") == "exact_immutable_github_sub_for_luhmos_main", "Google WIF subject policy drift")
    require(cloud.get("bootstrap") == "infra/gcp/bootstrap-github-wif.sh", "Google bootstrap path drift")
    require(cloud.get("canonical_repository_variables") == EXPECTED_GCP_VARS, "Google repository variable drift")
    require(cloud.get("gcp_project_id_is_transport_identifier") is True, "Google project ID must remain transport identity")
    require(cloud.get("desired_display_name") == PROJECT_NAME, "Google desired project branding drift")
    require(cloud.get("repository_variables_state") == "NOT_CONFIGURED_IN_CI_PREFLIGHT", "Google repository-variable debt must remain explicit until configured")
    require(cloud.get("live_oidc_auth_state") == "NOT_VERIFIED_AUTH_JOB_SKIPPED", "Google live OIDC debt must remain explicit until exercised")
    require(cloud.get("long_lived_service_account_json_in_repo") is False, "Google service-account JSON must stay out of repo")
    require(cloud.get("deployment_confirmation") == "PROVISION", "Google deploy confirmation drift")
    require(google.get("drive", {}).get("human_facing_root") == PROJECT_NAME, "Google Drive project root drift")

    github = providers["github"]
    require(github.get("repository") == "eggie-admin/hydra-shell-android", "GitHub repository drift")
    require(github.get("repository_slug_is_transport_identifier") is True, "GitHub repository slug boundary drift")
    require(github.get("canonical_branch") == "luhmos-main", "GitHub canonical branch drift")
    require(github.get("actions_oidc_issuer") == "https://token.actions.githubusercontent.com", "GitHub OIDC issuer drift")
    require(github.get("repository_created_before_2026_07_15_immutable_default_rollout") is True, "GitHub OIDC rollout classification drift")
    require(github.get("immutable_oidc_subject_required") is True, "GitHub immutable subject requirement drift")
    require(github.get("immutable_oidc_subject_live_state") == "UNVERIFIED_CONNECTOR_ENDPOINT_UNAVAILABLE", "GitHub immutable-subject live state must remain explicit")
    require(github.get("pull_request_before_canonical_mutation_required") is True, "GitHub PR gate drift")
    require(github.get("direct_push_should_be_blocked") is True, "GitHub direct-push policy drift")
    require(github.get("force_push_should_be_blocked") is True, "GitHub force-push policy drift")
    require(github.get("branch_deletion_should_be_blocked") is True, "GitHub deletion policy drift")
    observed = github.get("observed_2026_09_17", {})
    require(observed.get("canonical_branch_protected") is False, "recorded GitHub protection state changed; refresh audit")
    require(observed.get("repository_rulesets") == "NONE", "recorded GitHub ruleset state changed; refresh audit")
    require(observed.get("external_governance_state") == "RED_EXTERNAL", "GitHub external governance debt must remain explicit")

    cloudflare = providers["cloudflare"]
    require(cloudflare.get("api_base") == "https://api.cloudflare.com/client/v4", "Cloudflare API base drift")
    require(cloudflare.get("zone") == "eggiebagelface.art", "Cloudflare zone drift")
    require(cloudflare.get("worker_service_name_is_transport_identifier") is True, "Cloudflare worker-name boundary drift")
    require(cloudflare.get("credential_strategy") == "narrowly_scoped_api_tokens", "Cloudflare token policy drift")
    require(cloudflare.get("tunnel_token_is_separate_runtime_secret") is True, "Cloudflare tunnel token boundary drift")
    require(cloudflare.get("production_publish_confirmation") == "YES", "Cloudflare publish confirmation drift")
    require(cloudflare.get("wrangler_version") == "4.119.0", "Cloudflare Wrangler pin drift")
    require(cloudflare.get("router_port_forwarding_required") is False, "Cloudflare router-forwarding drift")

    hf = providers["hugging_face"]
    require(hf.get("account") == "eggiebagelface", "Hugging Face account transport binding drift")
    require(hf.get("organization") is None, "Hugging Face organization state drift")
    require(hf.get("account_is_transport_identity") is True, "Hugging Face account boundary drift")
    require(hf.get("api") == "responses_beta", "Hugging Face Responses status drift")
    require(hf.get("base_url") == "https://router.huggingface.co/v1", "Hugging Face router base drift")
    require(hf.get("responses_endpoint") == "https://router.huggingface.co/v1/responses", "Hugging Face Responses endpoint drift")
    require(hf.get("chat_endpoint") == "https://router.huggingface.co/v1/chat/completions", "Hugging Face chat endpoint drift")
    require(hf.get("default_model") == "openai/gpt-oss-120b:fastest", "Hugging Face default model drift")
    require(hf.get("lower_latency_candidate") == "openai/gpt-oss-20b:fastest", "Hugging Face fast model drift")
    require(hf.get("credential_env") == "HF_TOKEN", "Hugging Face credential contract drift")
    require(hf.get("auto_execute_remote_code") is False, "Hugging Face remote code must stay disabled")
    require(hf.get("live_inference_state") == "NOT_VERIFIED_SECRET_ABSENT_IN_CI_SMOKE", "Hugging Face live-inference debt must remain explicit until exercised")

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
    require("before GitHub's 2026-07-15 automatic immutable-subject rollout" in doctrine, "GitHub OIDC rollout caveat missing")
    require("OpenAI live inference is `NOT_VERIFIED`" in doctrine, "OpenAI live-inference debt missing from doctrine")
    require("Google Cloud live OIDC authentication is `NOT_CONFIGURED`" in doctrine, "Google live-auth debt missing from doctrine")
    require("Hugging Face live inference is `NOT_VERIFIED`" in doctrine, "Hugging Face live-inference debt missing from doctrine")

    cf_deploy = CF_DEPLOY.read_text(encoding="utf-8")
    require("wrangler@latest" not in cf_deploy, "Cloudflare deploy uses floating Wrangler")
    require(cf_deploy.count("wrangler@4.119.0") == 2, "Cloudflare preview/publish pin mismatch")
    require("test \"$CONFIRM\" = YES" in cf_deploy, "Cloudflare explicit publish confirmation missing")

    cf_audit = CF_AUDIT.read_text(encoding="utf-8")
    require(cf_audit.count("wrangler@4.119.0") == 2, "Cloudflare audit pin mismatch")

    gcp = GCP_PROVISION.read_text(encoding="utf-8")
    require("id-token: write" in gcp, "Google workflow OIDC permission missing")
    require("confirm_provision" in gcp and "PROVISION" in gcp, "Google explicit provision confirmation missing")
    require("google-github-actions/auth@7c6bc770dae815cd3e89ee6cdf493a5fab2cc093" in gcp, "Google auth action must be SHA pinned")
    require("google-github-actions/setup-gcloud@aa5489c8933f4cc7a4f7d45035b3b1440c9c10db" in gcp, "Google setup-gcloud action must be SHA pinned")
    require("GCP_WIF_PROVIDER" in gcp and "GCP_WORKLOAD_IDENTITY_PROVIDER" not in gcp, "Google WIF provider variable drift")
    require("GCP_SERVICE_ACCOUNT" in gcp, "Google service-account variable missing")

    gcp_smoke = GCP_OIDC_SMOKE.read_text(encoding="utf-8")
    require("branches:\n      - luhmos/gcp-oidc-auth\n      - luhmos-main" in gcp_smoke, "Google OIDC smoke canonical branch drift")
    for var in EXPECTED_GCP_VARS:
        require(var in gcp_smoke, f"Google OIDC smoke missing {var}")
    require("GCP_WORKLOAD_IDENTITY_PROVIDER" not in gcp_smoke, "Google OIDC smoke contains legacy provider variable")
    require("google-github-actions/auth@7c6bc770dae815cd3e89ee6cdf493a5fab2cc093" in gcp_smoke, "Google OIDC smoke auth action must be SHA pinned")

    bootstrap = GCP_BOOTSTRAP.read_text(encoding="utf-8")
    for needle in (
        "/actions/oidc/customization/sub",
        "use_immutable_subject",
        "GITHUB_OIDC_IMMUTABLE_SUBJECT=REQUIRED_NOT_CONFIRMED",
        "IMMUTABLE_SUBJECT=",
        "assertion.sub=='${IMMUTABLE_SUBJECT}'",
        "principal://iam.googleapis.com/${POOL_NAME}/subject/${IMMUTABLE_SUBJECT}",
        "providers update-oidc",
        "WIF_LEGACY_MUTABLE_REPOSITORY_BINDING_REMOVED",
    ):
        require(needle in bootstrap, f"Google immutable-subject bootstrap drift: {needle}")
    require("principalSet://iam.googleapis.com/${POOL_NAME}/attribute.repository/${REPO}" in bootstrap, "legacy mutable binding cleanup target missing")

    smoke = REMOTE_AI_SMOKE.read_text(encoding="utf-8")
    require("branches: [luhmos-main]" in smoke, "remote AI canonical push branch drift")
    require("OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}" in smoke, "OpenAI smoke credential wiring missing")
    require("HF_TOKEN: ${{ secrets.HF_TOKEN }}" in smoke, "Hugging Face smoke credential wiring missing")
    require("OPENAI_MODEL: gpt-5.6-sol" in smoke, "OpenAI smoke model drift")
    require("HF_MODEL: openai/gpt-oss-120b:fastest" in smoke, "Hugging Face smoke model drift")
    require("actions/checkout@11d5960a326750d5838078e36cf38b85af677262" in smoke, "remote AI checkout must be SHA pinned")
    require("actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065" in smoke, "remote AI setup-python must be SHA pinned")
    require("actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02" in smoke, "remote AI upload-artifact must be SHA pinned")
    require("persist-credentials: false" in smoke, "remote AI checkout credentials must not persist")

    print("LUHM_VENDOR_API_PIPELINE=GREEN")
    print("UNIFIED_PROJECT=LuHm OS")
    print("UNIFIED_PROJECT_ID=luhm_os")
    print("VENDOR_SPINE=openai,google,github,cloudflare,hugging_face")
    print("OPENAI_LEGACY_PROJECT=RECORDED_DO_NOT_TARGET")
    print("GITHUB_EXTERNAL_GOVERNANCE=RED_EXTERNAL_RECORDED")
    print("GITHUB_IMMUTABLE_OIDC=UNVERIFIED_EXTERNAL_RECORDED")
    print("GOOGLE_WIF_LIVE_STATE=UNVERIFIED_RECORDED_FAIL_CLOSED_BOOTSTRAP")
    print("OPENAI_LIVE_INFERENCE=NOT_VERIFIED_RECORDED")
    print("CLOUDFLARE_LIVE_ACCOUNT=UNVERIFIED_RECORDED")
    print("HUGGING_FACE_LIVE_INFERENCE=NOT_VERIFIED_RECORDED")


if __name__ == "__main__":
    main()
