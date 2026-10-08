#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "integrations/api-spine.manifest.json"
PROJECT = ROOT / "lumh-os/kai9000/project.manifest.json"
SPINE = ROOT / "ultima/ollama-ffmpeg-antenna-v3/api_spine.py"
COMPOSITION = ROOT / "ultima/ollama-ffmpeg-antenna-v3/magic_server.py"
MAGIC = ROOT / "ultima/ollama-ffmpeg-antenna-v3/magic_chat.py"
GATEWAY = ROOT / "ultima/ollama-ffmpeg-antenna-v3/gateway.py"
LUM_ROUTER = ROOT / "ultima/ollama-ffmpeg-antenna-v3/lum_agent/router.py"
AI_FEED_ROUTER = ROOT / "ultima/ollama-ffmpeg-antenna-v3/ai_feed/router.py"
AI_STACK = ROOT / "docs/AI_STACK.md"
API_INSTRUCTIONS = ROOT / ".github/instructions/api-trinity.instructions.md"
FINAL_ROLEPLAY = ROOT / "project/hydra/source-of-truth/LUHM_CODING_ROLEPLAY_FNLMLSTN_20260918.json"
VENDOR = ROOT / "integrations/vendor-apis.manifest.json"
RUNTIME_POLICY = ROOT / "integrations/runtime-capabilities.policy.json"

EXPECTED_VENDORS = ["openai", "google", "github", "cloudflare", "hugging_face"]
EXPECTED_ROUTES = {
    "health": "GET /api/v1/health",
    "status": "GET /api/v1/status",
    "providers": "GET /api/v1/providers",
    "capabilities": "GET /api/v1/capabilities",
    "assist_plan": "POST /api/v1/assist/plan",
    "assist_query": "POST /api/v1/assist/query",
    "ai_chat": "POST /api/v1/ai/chat",
    "provider_route": "POST /api/v1/providers/route",
}
EXPECTED_PLANES = {
    "remote_assistance_v1",
    "remote_ai",
    "lum_agent",
    "magic_cast",
    "ai_feed",
    "antenna_gateway",
    "local_antenna",
    "media",
    "widget_cms",
    "local_agent",
}
EXPECTED_DEFAULTS = {
    "openai_fast": "gpt-5.6-luna",
    "openai_deep": "gpt-5.6-sol",
    "google_fast": "gemini-3.5-flash-lite",
    "google_deep": "gemini-3.8-flash",
    "google_live_api": "gemini-3.8-live",
    "hugging_face_critic": "openai/gpt-oss-20b:fastest",
}


def require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(f"LUHM_API_SPINE_RED: {message}")


def main() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    project = json.loads(PROJECT.read_text(encoding="utf-8"))
    roleplay = json.loads(FINAL_ROLEPLAY.read_text(encoding="utf-8"))
    vendor = json.loads(VENDOR.read_text(encoding="utf-8"))
    runtime = json.loads(RUNTIME_POLICY.read_text(encoding="utf-8"))
    spine = SPINE.read_text(encoding="utf-8")
    composition = COMPOSITION.read_text(encoding="utf-8")
    magic = MAGIC.read_text(encoding="utf-8")
    gateway = GATEWAY.read_text(encoding="utf-8")
    lum_router = LUM_ROUTER.read_text(encoding="utf-8")
    ai_feed_router = AI_FEED_ROUTER.read_text(encoding="utf-8")
    ai_stack = AI_STACK.read_text(encoding="utf-8")
    instructions = API_INSTRUCTIONS.read_text(encoding="utf-8")

    require(data.get("schema") == "luhm-os.api-spine.v1", "schema drift")
    require(data.get("project") == "LuHm OS", "project identity drift")
    require(data.get("machine_id") == "luhm_os", "machine identity drift")
    require(data.get("canonical_prefix") == "/api/v1", "canonical prefix drift")
    require(data.get("vendor_spine") == EXPECTED_VENDORS, "vendor spine drift")
    require(data.get("canonical_routes") == EXPECTED_ROUTES, "canonical route registry drift")
    require(set(data.get("compatibility_planes", {})) == EXPECTED_PLANES, "component/compatibility plane inventory drift")
    require(data.get("provider_defaults") == EXPECTED_DEFAULTS, "provider default registry drift")

    project_runtime = project.get("runtime", {})
    project_doctrine = project.get("doctrine", {})
    require(project.get("schema") == "luhm-os.project.v4", "project manifest schema drift")
    require(project.get("name") == "LuHm OS" and project.get("project_id") == "luhm_os", "project manifest identity drift")
    require(project_doctrine.get("api_spine") == "docs/LUHMOS_API_SPINE.md", "project doctrine API spine pointer drift")
    require(project_doctrine.get("api_spine_manifest") == "integrations/api-spine.manifest.json", "project doctrine spine manifest pointer drift")
    require(project_runtime.get("canonical_api_contract") == data.get("schema"), "project runtime spine contract drift")
    require(project_runtime.get("canonical_api_prefix") == data.get("canonical_prefix") == "/api/v1", "project runtime prefix drift")
    require(project_runtime.get("canonical_ai_route") == "/api/v1/ai/chat", "project canonical AI route drift")
    require(project_runtime.get("remote_ai_endpoint_policy") == "compatibility_only_no_new_clients", "legacy remote AI gained canonical authority")
    require(project_runtime.get("silent_cross_provider_failover") is False, "project runtime silent failover drift")

    limits = data.get("roleplay_runtime_limits", {})
    sealed = roleplay.get("final_milestone_contract", {})
    require(limits.get("default_helpers") == sealed.get("default_helpers") == 0, "default helper drift")
    require(
        limits.get("max_parallel_read_only_helpers") == sealed.get("max_parallel_read_only_helpers") == 2,
        "parallel helper drift",
    )
    require(limits.get("max_delegation_depth") == sealed.get("max_delegation_depth") == 1, "delegation depth drift")
    require(limits.get("recursive_recruiting") is sealed.get("recursive_recruiting") is False, "recursive recruiting drift")
    require(limits.get("single_parent_writer") is sealed.get("single_parent_writer") is True, "single-writer drift")
    require(data.get("authority", {}).get("helper_consensus_grants_authority") is False, "helper consensus gained authority")

    require(vendor.get("vendor_spine") == EXPECTED_VENDORS, "vendor catalog provider drift")
    routing = runtime.get("routing", {})
    require(runtime.get("schema") == "luhm-os.runtime-capabilities.v2", "runtime capability schema drift")
    require(runtime.get("api_spine_contract") == "luhm-os.api-spine.v1", "runtime capability spine binding drift")
    require(routing.get("canonical_api_prefix") == "/api/v1", "runtime canonical prefix drift")
    require(routing.get("default_helpers") == 0, "runtime default helper drift")
    require(routing.get("max_parallel_read_only_helpers") == 2, "runtime helper cap drift")
    require(routing.get("max_delegation_depth") == 1, "runtime delegation depth drift")
    require(routing.get("recursive_recruiting") is False, "runtime recursive recruiting drift")
    require(routing.get("single_parent_writer") is True, "runtime single-writer drift")
    require(data.get("migration", {}).get("new_clients_must_use_canonical_prefix") is True, "canonical client policy missing")
    require(data.get("migration", {}).get("legacy_routes_removed_in_this_milestone") is False, "unexpected breaking migration")
    require(data.get("migration", {}).get("legacy_routes_may_expand") is False, "legacy route expansion enabled")
    require(data.get("migration", {}).get("silent_cross_provider_failover") is False, "silent provider failover enabled")
    require(data.get("migration", {}).get("secrets_in_client_or_repo") is False, "client/repo secrets enabled")
    require(data.get("migration", {}).get("private_lan_public_exposure") is False, "private LAN exposure enabled")

    for needle in (
        'APIRouter(prefix="/api/v1"',
        "DEFAULT_HELPERS = 0",
        "MAX_PARALLEL_READ_ONLY_HELPERS = 2",
        "MAX_DELEGATION_DEPTH = 1",
        '@ROUTER.get("/health")',
        '@ROUTER.get("/status")',
        '@ROUTER.get("/providers")',
        '@ROUTER.get("/capabilities")',
        '@ROUTER.post("/assist/plan")',
        '@ROUTER.post("/assist/query")',
        '@ROUTER.post("/ai/chat")',
        '@ROUTER.post("/providers/route")',
    ):
        require(needle in spine, f"spine implementation missing: {needle}")

    require("API_SPINE_ROUTER" in composition, "composition root does not import API spine")
    require("APP.include_router(API_SPINE_ROUTER)" in composition, "composition root does not mount API spine")
    require(
        composition.index("APP.include_router(API_SPINE_ROUTER)") < composition.index("APP.include_router(REMOTE_AI_ROUTER)"),
        "canonical spine must be mounted before compatibility routers",
    )
    require('APP.title = "LuHm OS Remote Assistance Cockpit"' in composition, "legacy cockpit branding contract drift")

    require('APIRouter(prefix="/api/lum"' in lum_router, "Lum component plane drift")
    require('APIRouter(prefix="/api/ai"' in ai_feed_router, "AI-feed component plane drift")
    require('APIRouter(prefix="/api/magic"' in magic, "Magic component plane drift")
    require('OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-5.6-sol")' in magic, "Magic OpenAI fallback drift")
    require("gpt-6-astra" not in magic, "retired Magic model fallback returned")
    require('"gemini-3.5-flash-lite"' in gateway, "gateway Google fast fallback drift")
    require('"gemini-3.8-live"' in gateway, "gateway Google Live fallback drift")
    require("gemini-3.1-flash-live-preview" not in gateway, "retired gateway Live fallback returned")

    require("Canonical application-facing AI contract for new clients is:" in ai_stack, "AI stack canonical contract wording drift")
    require("POST /api/v1/ai/chat" in ai_stack, "AI stack does not point clients to canonical AI route")
    require("`/api/v1` is the canonical LuHm OS application API namespace for new clients." in instructions, "integration instructions lost canonical namespace")
    require("gpt-6-astra" not in instructions, "integration instructions resurrected retired OpenAI default")

    print("LUHM_API_SPINE_GREEN")
    print(f"contract={data['schema']}")
    print(f"canonical_prefix={data['canonical_prefix']}")
    print(f"providers={','.join(EXPECTED_VENDORS)}")
    print(f"component_planes={len(EXPECTED_PLANES)}")
    print("default_helpers=0")
    print("parallel_read_only_helpers_max=2")
    print("legacy_routes=preserved_compatibility_only")


if __name__ == "__main__":
    main()
