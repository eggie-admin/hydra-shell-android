#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REMOTE = ROOT / "ultima/ollama-ffmpeg-antenna-v3/remote_ai.py"
GOOGLE = ROOT / "ultima/ollama-ffmpeg-antenna-v3/google_assist.py"
ASSIST = ROOT / "ultima/ollama-ffmpeg-antenna-v3/assistance.py"
SERVER = ROOT / "ultima/ollama-ffmpeg-antenna-v3/magic_server.py"
MANIFEST = ROOT / "integrations/vendor-apis.manifest.json"


def require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(f"REMOTE_ASSISTANCE_RED: {message}")


def main() -> None:
    remote = REMOTE.read_text(encoding="utf-8")
    google = GOOGLE.read_text(encoding="utf-8")
    assist = ASSIST.read_text(encoding="utf-8")
    server = SERVER.read_text(encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    for needle in (
        'OPENAI_FAST_MODEL = os.environ.get("OPENAI_FAST_MODEL", "gpt-5.6-luna")',
        'OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-5.6-sol")',
        'HF_FAST_MODEL = os.environ.get("HF_FAST_MODEL", "openai/gpt-oss-20b:fastest")',
        "httpx.Client(",
        "max_keepalive_connections=16",
        "previous_response_id",
        '"connection_pool": "keepalive"',
    ):
        require(needle in remote, f"remote fastpath drift: {needle}")
    require("gpt-6-astra" not in remote, "retired OpenAI model resurrected in active remote router")

    for needle in (
        'GOOGLE_FAST_MODEL = os.environ.get("KAI_GOOGLE_FAST_TEXT_MODEL", "gemini-3.5-flash-lite")',
        'GOOGLE_DEEP_MODEL = os.environ.get("KAI_GOOGLE_DEEP_TEXT_MODEL", "gemini-3.8-flash")',
        'GOOGLE_LIVE_API_MODEL = os.environ.get("KAI_GEMINI_LIVE_API_MODEL", "gemini-3.8-live")',
        "_CLIENT_LOCK = threading.Lock()",
        "_CLIENT_SIGNATURE",
        '"client_cache": "process_reuse"',
    ):
        require(needle in google, f"Google assistance fastpath drift: {needle}")

    for needle in (
        "MAX_PARALLEL = 3",
        '"context": "github_evidence_by_reference"',
        '"build": "openai"',
        '"research": "google"',
        '"critic": "huggingface_conditional"',
        "if task == \"direct\":",
        "ThreadPoolExecutor(max_workers=workers",
        '"execution": "advisory_only"',
        '"crown_gate": True',
        '"silent_cross_provider_failover": False',
        "import google_assist",
        "google_assist.generate(",
    ):
        require(needle in assist, f"assistance mesh drift: {needle}")

    require("MAX_GITHUB_REFS = 12" in assist, "GitHub context budget drift")
    require("evidence_by_reference_not_full_history_copy" in assist, "GitHub evidence-copy policy drift")

    boot_defaults = (
        'os.environ.setdefault("OPENAI_FAST_MODEL", "gpt-5.6-luna")',
        'os.environ.setdefault("OPENAI_MODEL", "gpt-5.6-sol")',
        'os.environ.setdefault("KAI_GOOGLE_FAST_TEXT_MODEL", "gemini-3.5-flash-lite")',
        'os.environ.setdefault("KAI_GOOGLE_DEEP_TEXT_MODEL", "gemini-3.8-flash")',
        'os.environ.setdefault("KAI_GEMINI_LIVE_API_MODEL", "gemini-3.8-live")',
    )
    magic_import = server.find("from magic_chat import ROUTER as MAGIC_ROUTER")
    require(magic_import >= 0, "compatibility import missing")
    for needle in boot_defaults:
        position = server.find(needle)
        require(position >= 0, f"server model/bootstrap contract missing: {needle}")
        require(position < magic_import, f"provider default must be fixed before compatibility imports: {needle}")
    require("from assistance import ROUTER as ASSISTANCE_ROUTER" in server, "assistance router not mounted")
    require("APP.include_router(ASSISTANCE_ROUTER)" in server, "assistance endpoint not active")
    require('APP.title = "LuHm OS Remote Assistance Cockpit"' in server, "runtime branding drift")

    contract = manifest.get("remote_assistance", {})
    require(contract.get("contract") == "luhm-os.remote-assistance.v1", "manifest assistance contract drift")
    require(contract.get("status_endpoint") == "/api/assist/status", "assistance status endpoint drift")
    require(contract.get("route_endpoint") == "/api/assist/route", "assistance route endpoint drift")
    require(contract.get("query_endpoint") == "/api/assist/query", "assistance query endpoint drift")
    require(contract.get("boss") == "Lum", "boss-agent drift")
    require(contract.get("human_authority") == "Professor", "human authority drift")
    require(contract.get("direct_questions_bypass_mesh") is True, "direct-question mesh bypass drift")
    require(contract.get("helpers_may_recursively_recruit") is False, "recursive helper recruitment drift")
    require(contract.get("parallelism_max") == 3, "manifest parallelism drift")

    blades = contract.get("default_blades", {})
    require(blades.get("context", {}).get("provider") == "github", "Context blade provider drift")
    require(blades.get("context", {}).get("policy") == "evidence_by_reference_not_full_history_copy", "Context evidence policy drift")
    require(blades.get("build", {}).get("provider") == "openai", "Build blade provider drift")
    require(blades.get("build", {}).get("fast_model") == "gpt-5.6-luna", "OpenAI fast model doctrine drift")
    require(blades.get("build", {}).get("deep_model") == "gpt-5.6-sol", "OpenAI deep model doctrine drift")
    research = blades.get("research", {})
    require(research.get("provider") == "google", "Research blade provider drift")
    require(research.get("fast_model") == "gemini-3.5-flash-lite", "Google fast model doctrine drift")
    require(research.get("deep_model") == "gemini-3.8-flash", "Google deep model doctrine drift")
    require(research.get("api_key_live_model") == "gemini-3.8-live", "Google API Live model doctrine drift")
    require(research.get("vertex_live_model") == "gemini-live-2.5-flash-native-audio", "Google Vertex Live model doctrine drift")
    require(blades.get("critic", {}).get("provider") == "hugging_face", "Critic blade provider drift")
    require(blades.get("critic", {}).get("conditional") is True, "Critic conditional policy drift")

    latency = contract.get("latency_policy", {})
    for key in (
        "openai_http_keepalive",
        "openai_previous_response_id_reuse",
        "google_client_process_reuse",
        "short_direct_turns_use_fast_profile",
        "complex_build_and_audit_use_deep_profile",
        "complex_helpers_run_in_parallel",
        "provider_network_latency_is_measured_not_assumed",
    ):
        require(latency.get(key) is True, f"latency policy drift: {key}")

    authority = contract.get("authority", {})
    require(authority.get("provider_outputs_are_advisory") is True, "provider authority drift")
    require(authority.get("remote_execution_authority") is False, "remote execution authority escaped")
    require(authority.get("consequential_actions_are_crown_gated") is True, "Crown gate drift")
    require(authority.get("silent_cross_provider_failover") is False, "silent failover drift")

    providers = manifest.get("providers", {})
    require(providers.get("openai", {}).get("assistance_role") == "build_and_reasoning_primary", "OpenAI assistance role drift")
    google_provider = providers.get("google", {})
    require(google_provider.get("assistance_role") == "research_realtime_multimodal_advisory", "Google assistance role drift")
    google_models = google_provider.get("assistance_models", {})
    require(google_models.get("fast_text") == "gemini-3.5-flash-lite", "Google provider fast model drift")
    require(google_models.get("deep_text") == "gemini-3.8-flash", "Google provider deep model drift")
    require(google_models.get("api_key_live") == "gemini-3.8-live", "Google provider API Live model drift")
    require(google_models.get("vertex_live") == "gemini-live-2.5-flash-native-audio", "Google provider Vertex Live model drift")
    require(providers.get("github", {}).get("assistance_role") == "context_evidence_ci_by_reference", "GitHub assistance role drift")
    require(providers.get("hugging_face", {}).get("assistance_role") == "conditional_critic_and_alternate_inference", "Hugging Face assistance role drift")
    require(providers.get("cloudflare", {}).get("assistance_role") == "edge_transport_not_reasoning", "Cloudflare assistance boundary drift")

    print("LUHM OS REMOTE ASSISTANCE FASTPATH GREEN")


if __name__ == "__main__":
    main()
