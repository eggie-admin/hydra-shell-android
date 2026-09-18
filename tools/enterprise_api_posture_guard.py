#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTURE = ROOT / "integrations/enterprise-api.posture.json"
CAPS = ROOT / "integrations/runtime-capabilities.policy.json"
VENDOR = ROOT / "integrations/vendor-apis.manifest.json"
CF = ROOT / ".github/workflows/cloudflare-coming-soon.yml"
GCP = ROOT / "infra/gcp/bootstrap-github-wif.sh"
REMOTE = ROOT / "ultima/ollama-ffmpeg-antenna-v3/remote_ai.py"

CHECKOUT_SHA = "actions/checkout@11d5960a326750d5838078e36cf38b85af677262"
NODE_SHA = "actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020"


def require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(f"ENTERPRISE_API_POSTURE_RED: {message}")


def main() -> None:
    posture = json.loads(POSTURE.read_text(encoding="utf-8"))
    caps = json.loads(CAPS.read_text(encoding="utf-8"))
    vendor = json.loads(VENDOR.read_text(encoding="utf-8"))
    cf = CF.read_text(encoding="utf-8")
    gcp = GCP.read_text(encoding="utf-8")
    remote = REMOTE.read_text(encoding="utf-8")

    require(posture.get("schema") == "luhm-os.enterprise-api-posture.v1", "posture schema drift")
    require(posture.get("project") == "LuHm OS", "project branding drift")
    require(posture.get("logical_project_id") == "luhm_os", "project id drift")
    require(posture.get("classification") == "ENTERPRISE_APPROACH_NOT_ENTERPRISE_PLAN_CLAIM", "plan-tier boundary drift")
    require(posture.get("scope") == ["openai", "cloudflare", "google"], "provider scope drift")

    identities = posture.get("identity_model", {})
    require(identities.get("human_admin") == "interactive_admin_only", "human admin role drift")
    require(identities.get("runtime_service_principal") == "application_inference_only", "runtime principal drift")
    require(identities.get("ci_deploy_principal") == "deployment_pipeline_only", "CI principal drift")
    require(identities.get("audit_reader") == "read_only_security_telemetry_only", "audit principal drift")
    require(identities.get("shared_super_token") is False, "shared super-token escaped")
    require(identities.get("personal_credentials_for_production_automation") is False, "personal production credential escaped")

    shared = posture.get("shared_controls", {})
    for key in (
        "least_privilege",
        "short_lived_credentials_when_supported",
        "credential_rotation_required",
        "audit_trail_required",
        "production_mutation_requires_explicit_human_gate",
        "live_capability_must_be_proven_before_green",
    ):
        require(shared.get(key) is True, f"shared enterprise control drift: {key}")
    for key in ("credentials_in_git", "credentials_in_apk", "credentials_in_logs"):
        require(shared.get(key) is False, f"credential boundary drift: {key}")

    providers = posture.get("providers", {})
    require(set(providers) == {"openai", "cloudflare", "google"}, "posture provider set drift")

    openai = providers["openai"]
    require(openai.get("production_runtime_identity_target") == "project_scoped_service_account", "OpenAI service principal drift")
    require(openai.get("personal_api_key_for_production") is False, "OpenAI personal production key escaped")
    require(openai.get("service_account_key_permissions_target") == "restricted_minimum_required_endpoints", "OpenAI restricted-key policy drift")
    require(openai.get("model_usage_allowlist_required") is True, "OpenAI model allowlist drift")
    require(openai.get("project_rate_limits_required") is True, "OpenAI project rate-limit control drift")
    require(openai.get("project_spend_limit_required") is True, "OpenAI project spend control drift")
    require(openai.get("admin_api_identity_separate_from_runtime") is True, "OpenAI Admin API identity drift")
    require(openai.get("audit_log_reader_separate_from_runtime") is True, "OpenAI audit identity drift")
    require(openai.get("api_data_sharing_assumed_enabled") is False, "OpenAI data-sharing assumption drift")
    require(openai.get("zero_data_retention_assumed") is False, "OpenAI ZDR assumption drift")
    require("https://api.openai.com/v1/responses" in remote, "OpenAI Responses endpoint missing")
    require("httpx.Client(" in remote, "OpenAI pooled client missing")

    cloudflare = providers["cloudflare"]
    require(cloudflare.get("production_ci_identity_target") == "account_owned_api_token", "Cloudflare account-token target drift")
    require(cloudflare.get("global_api_key_allowed") is False, "Cloudflare global key escaped")
    require(cloudflare.get("deploy_token_separate_from_tunnel_token") is True, "Cloudflare tunnel/deploy credential boundary drift")
    require(cloudflare.get("deploy_token_separate_from_access_service_token") is True, "Cloudflare Access/deploy credential boundary drift")
    require(cloudflare.get("production_publish_confirmation") == "YES", "Cloudflare publish authority drift")
    require(cloudflare.get("tunnel_policy") == "outbound_only_no_router_port_forwarding", "Cloudflare private-boundary drift")
    require("X-Auth-Key" not in cf and "X-Auth-Email" not in cf, "Cloudflare legacy global-key auth present")
    require("Global API Key" not in cf, "Cloudflare global API key wording present in workflow")
    require(cf.count(CHECKOUT_SHA) == 2, "Cloudflare checkout actions are not SHA-pinned")
    require(cf.count("persist-credentials: false") == 2, "Cloudflare checkout credentials persist")
    require(NODE_SHA in cf, "Cloudflare setup-node is not SHA-pinned")
    require("wrangler@4.119.0" in cf and "wrangler@latest" not in cf, "Cloudflare Wrangler pin drift")
    require("accounts/$CLOUDFLARE_ACCOUNT_ID/tokens/verify" in cf, "Cloudflare account-token live verification missing")
    require("test \"$CONFIRM\" = YES" in cf, "Cloudflare exact publish confirmation missing")
    require("push:" not in cf, "Cloudflare workflow regained automatic push lane")

    google = providers["google"]
    require(google.get("external_ci_auth") == "github_oidc_to_workload_identity_federation", "Google WIF auth drift")
    require(google.get("service_account_key_files_allowed") is False, "Google service-account keys escaped")
    require(google.get("immutable_subject_required") is True, "Google immutable subject drift")
    require(google.get("attribute_condition_required") is True, "Google attribute condition drift")
    require(google.get("single_provider_per_pool_target") is True, "Google single-provider pool target drift")
    require(google.get("dedicated_service_account_per_pipeline_required") is True, "Google per-pipeline service account drift")
    require(google.get("service_account_id_must_be_explicit") is True, "Google explicit service-account identity drift")
    require(google.get("service_account_key_creation_org_policy_target") == "disabled", "Google key-creation org-policy target drift")
    require(google.get("service_account_key_upload_org_policy_target") == "disabled", "Google key-upload org-policy target drift")
    require(google.get("secret_manager_scope") == "secret_level_least_privilege", "Google Secret Manager scope drift")
    for needle in (
        "use_immutable_subject",
        "assertion.sub=='${IMMUTABLE_SUBJECT}'",
        "google.subject=assertion.sub",
        "principal://iam.googleapis.com/${POOL_NAME}/subject/${IMMUTABLE_SUBJECT}",
        "WIF_LEGACY_MUTABLE_REPOSITORY_BINDING_REMOVED",
        "GCP_SERVICE_ACCOUNT_ID is required",
    ):
        require(needle in gcp, f"Google enterprise WIF drift: {needle}")
    for forbidden in (
        "service-accounts keys create",
        "iam service-accounts keys create",
        "--key-file=",
    ):
        require(forbidden not in gcp, f"Google long-lived key creation escaped: {forbidden}")

    require(caps.get("project") == "LuHm OS", "runtime capability contract project drift")
    require(vendor.get("project_display_name") == "LuHm OS", "vendor contract project drift")

    authority = posture.get("authority", {})
    for value in authority.values():
        require(str(value).startswith("NOT_AUTHORIZED"), "enterprise posture granted authority")

    print("LUHM OS ENTERPRISE API POSTURE GREEN")
    print("OPENAI=ENTERPRISE_CONTROL_TARGETS_BOUND")
    print("CLOUDFLARE=ACCOUNT_SERVICE_PRINCIPAL_TARGET_BOUND")
    print("GOOGLE=KEYLESS_PIPELINE_IDENTITY_BOUND")
    print("LIVE_PROVIDER_SETTINGS=REQUIRE_EXTERNAL_VERIFICATION")


if __name__ == "__main__":
    main()
