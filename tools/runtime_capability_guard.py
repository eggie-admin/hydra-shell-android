#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "integrations/runtime-capabilities.policy.json"
VENDOR = ROOT / "integrations/vendor-apis.manifest.json"
API_SPINE = ROOT / "integrations/api-spine.manifest.json"
REMOTE = ROOT / "ultima/ollama-ffmpeg-antenna-v3/remote_ai.py"
ASSIST = ROOT / "ultima/ollama-ffmpeg-antenna-v3/assistance.py"
GOOGLE_ASSIST = ROOT / "ultima/ollama-ffmpeg-antenna-v3/google_assist.py"


def require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(f"RUNTIME_CAPABILITY_RED: {message}")


def main() -> None:
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    vendor = json.loads(VENDOR.read_text(encoding="utf-8"))
    spine = json.loads(API_SPINE.read_text(encoding="utf-8"))
    remote = REMOTE.read_text(encoding="utf-8")
    assist = ASSIST.read_text(encoding="utf-8")
    google_assist = GOOGLE_ASSIST.read_text(encoding="utf-8")

    require(policy.get("schema") == "luhm-os.runtime-capabilities.v2", "policy schema drift")
    require(policy.get("project") == "LuHm OS", "project branding drift")
    require(policy.get("logical_project_id") == "luhm_os", "project id drift")
    require(policy.get("api_spine_contract") == "luhm-os.api-spine.v1", "API spine binding drift")
    require(spine.get("schema") == policy.get("api_spine_contract"), "API spine/runtime contract mismatch")
    require(spine.get("canonical_prefix") == "/api/v1", "API spine canonical prefix drift")

    privacy = policy.get("privacy", {})
    require(privacy.get("account_specific_plan_names_in_public_source") is False, "personal plan names must stay private")
    require(privacy.get("billing_amounts_in_public_source") is False, "billing amounts must stay private")
    require(privacy.get("credentials_in_public_source") is False, "credentials must stay private")

    providers = policy.get("providers", {})
    require(set(providers) == {"openai", "google", "github", "cloudflare", "hugging_face"}, "provider spine drift")

    openai = providers["openai"]
    require(openai.get("chat_subscription_is_not_api_billing") is True, "ChatGPT/API billing boundary drift")
    require(openai.get("fast_model") == "gpt-5.6-luna", "OpenAI fast model drift")
    require(openai.get("deep_model") == "gpt-5.6-sol", "OpenAI deep model drift")
    require(openai.get("use_http_keepalive") is True, "OpenAI keepalive disabled")
    require(openai.get("use_previous_response_id_for_followups") is True, "OpenAI response reuse disabled")
    require("httpx.Client(" in remote and "previous_response_id" in remote, "OpenAI runtime does not implement paid-capability fastpath")

    google = providers["google"]
    require(google.get("fast_model") == "gemini-3.5-flash-lite", "Google fast model drift")
    require(google.get("deep_model") == "gemini-3.8-flash", "Google deep model drift")
    require(google.get("use_client_process_cache") is True, "Google client cache disabled")
    paid_google = set(google.get("paid_capabilities", []))
    require({"context_caching", "batch_or_flex_for_offline_work", "higher_rate_limits", "advanced_models"}.issubset(paid_google), "Google paid-capability registry drift")
    for needle in (
        'GOOGLE_FAST_MODEL = os.environ.get("KAI_GOOGLE_FAST_TEXT_MODEL", "gemini-3.5-flash-lite")',
        'GOOGLE_DEEP_MODEL = os.environ.get("KAI_GOOGLE_DEEP_TEXT_MODEL", "gemini-3.8-flash")',
        'GOOGLE_LIVE_API_MODEL = os.environ.get("KAI_GEMINI_LIVE_API_MODEL", "gemini-3.8-live")',
        "_CLIENT_LOCK = threading.Lock()",
        "_CLIENT_SIGNATURE",
        "def _client()",
        '"client_cache": "process_reuse"',
    ):
        require(needle in google_assist, f"Google assistance fastpath drift: {needle}")
    require("import google_assist" in assist, "Google assistance module not mounted on orchestration hot path")
    require("google_assist.generate(" in assist, "Google assistance cache bypassed by orchestration")

    github = providers["github"]
    require(github.get("public_repository_standard_actions_are_preferred") is True, "GitHub public Actions preference drift")
    require(github.get("larger_paid_runners_are_not_assumed") is True, "GitHub paid runner assumption escaped")
    require(github.get("context_policy") == "resolve_evidence_by_reference_not_full_history_copy", "GitHub context policy drift")
    require("MAX_GITHUB_REFS = 12" in assist, "GitHub evidence budget drift")

    cloudflare = providers["cloudflare"]
    require(cloudflare.get("paid_workers_features_may_be_used_when_verified") is True, "Cloudflare paid Workers path disabled")
    require(cloudflare.get("production_publish_still_requires") == "YES", "Cloudflare publish gate drift")
    require(cloudflare.get("private_lan_exposure") is False, "Cloudflare private LAN exposure drift")

    hf = providers["hugging_face"]
    require(hf.get("critic_is_conditional") is True, "HF critic must remain conditional")
    require(hf.get("gpu_or_paid_jobs_never_auto_launch") is True, "HF paid jobs gained auto-launch authority")
    require(hf.get("fast_model") == "openai/gpt-oss-20b:fastest", "HF fast critic model drift")

    routing = policy.get("routing", {})
    require(routing.get("canonical_api_prefix") == "/api/v1", "canonical API prefix drift")
    require(routing.get("default_helpers") == 0, "default helper recruitment drift")
    require(routing.get("max_parallel_read_only_helpers") == 2, "parallel helper cap drift")
    require(routing.get("max_delegation_depth") == 1, "delegation depth drift")
    require(routing.get("recursive_recruiting") is False, "recursive helper recruitment drift")
    require(routing.get("single_parent_writer") is True, "single-parent-writer drift")
    require(routing.get("prefer_paid_capability_when_proven_and_task_relevant") is True, "paid capability preference disabled")
    require(routing.get("do_not_spend_more_only_to_prove_entitlement") is True, "entitlement probe may burn money")
    require(routing.get("no_silent_cross_provider_failover") is True, "silent failover drift")
    require(routing.get("direct_questions_bypass_mesh") is True, "direct question bypass drift")
    require(routing.get("consequential_actions_remain_crown_gated") is True, "Crown authority drift")

    spine_limits = spine.get("roleplay_runtime_limits", {})
    require(spine_limits.get("default_helpers") == routing.get("default_helpers"), "spine/runtime default-helper mismatch")
    require(
        spine_limits.get("max_parallel_read_only_helpers") == routing.get("max_parallel_read_only_helpers"),
        "spine/runtime parallel-helper mismatch",
    )
    require(spine_limits.get("max_delegation_depth") == routing.get("max_delegation_depth"), "spine/runtime depth mismatch")
    require(spine_limits.get("recursive_recruiting") is routing.get("recursive_recruiting") is False, "spine/runtime recursion mismatch")
    require(spine_limits.get("single_parent_writer") is routing.get("single_parent_writer") is True, "spine/runtime writer mismatch")

    require(vendor.get("project_display_name") == "LuHm OS", "vendor manifest project drift")
    require(vendor.get("vendor_spine") == ["openai", "google", "github", "cloudflare", "hugging_face"], "vendor manifest spine drift")
    require(spine.get("vendor_spine") == vendor.get("vendor_spine"), "API spine/vendor catalog mismatch")

    print("LUHM OS RUNTIME CAPABILITY GUARD GREEN")
    print("API_SPINE=luhm-os.api-spine.v1")
    print("CANONICAL_PREFIX=/api/v1")
    print("HELPERS=default:0,max_read_only:2,depth:1")


if __name__ == "__main__":
    main()
