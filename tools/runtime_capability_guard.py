#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "integrations/runtime-capabilities.policy.json"
VENDOR = ROOT / "integrations/vendor-apis.manifest.json"
REMOTE = ROOT / "ultima/ollama-ffmpeg-antenna-v3/remote_ai.py"
ASSIST = ROOT / "ultima/ollama-ffmpeg-antenna-v3/assistance.py"
GOOGLE_ASSIST = ROOT / "ultima/ollama-ffmpeg-antenna-v3/google_assist.py"


def require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(f"RUNTIME_CAPABILITY_RED: {message}")


def main() -> None:
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    vendor = json.loads(VENDOR.read_text(encoding="utf-8"))
    remote = REMOTE.read_text(encoding="utf-8")
    assist = ASSIST.read_text(encoding="utf-8")
    google_assist = GOOGLE_ASSIST.read_text(encoding="utf-8")

    require(policy.get("schema") == "luhm-os.runtime-capabilities.v1", "policy schema drift")
    require(policy.get("project") == "LuHm OS", "project branding drift")
    require(policy.get("logical_project_id") == "luhm_os", "project id drift")

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
    require("httpx.Client(" in remote, "OpenAI/HF shared HTTP pool missing")
    require("previous_response_id" in remote, "OpenAI response continuation missing")
    require("prompt_cache_key" in remote and "prompt_cache_options" in remote, "OpenAI prompt-cache fastpath missing")
    require("max_keepalive_connections=16" in remote, "remote keepalive pool drift")

    google = providers["google"]
    require(google.get("fast_model") == "gemini-3.5-flash-lite", "Google fast model drift")
    require(google.get("deep_model") == "gemini-3.8-flash", "Google deep model drift")
    require(google.get("use_client_process_cache") is True, "Google client cache disabled")
    paid_google = set(google.get("paid_capabilities", []))
    require({"context_caching", "batch_or_flex_for_offline_work", "higher_rate_limits", "advanced_models"}.issubset(paid_google), "Google paid-capability registry drift")
    require("_CLIENT_LOCK" in google_assist and "_CLIENT_SIGNATURE" in google_assist, "Google credential-aware process cache missing")
    require("def _client()" in google_assist and "gateway._google_client()" in google_assist, "Google process client reuse missing")
    require("GOOGLE_FAST_TIMEOUT_MS" in google_assist and "GOOGLE_DEEP_TIMEOUT_MS" in google_assist, "Google profile timeout contract missing")
    require("process_reuse" in google_assist and "implicit_context_cache" in google_assist, "Google reuse/cache receipt missing")

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
    require(routing.get("prefer_paid_capability_when_proven_and_task_relevant") is True, "paid capability preference disabled")
    require(routing.get("do_not_spend_more_only_to_prove_entitlement") is True, "entitlement probe may burn money")
    require(routing.get("no_silent_cross_provider_failover") is True, "silent failover drift")
    require(routing.get("max_parallel_remote_helpers") == 3, "parallelism drift")
    require(routing.get("direct_questions_bypass_mesh") is True, "direct question bypass drift")
    require(routing.get("consequential_actions_remain_crown_gated") is True, "Crown authority drift")

    require(vendor.get("project_display_name") == "LuHm OS", "vendor manifest project drift")
    require(vendor.get("vendor_spine") == ["openai", "google", "github", "cloudflare", "hugging_face"], "vendor manifest spine drift")

    print("LUHM OS RUNTIME CAPABILITY GUARD GREEN")


if __name__ == "__main__":
    main()
