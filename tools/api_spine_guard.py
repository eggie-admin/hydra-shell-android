#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "integrations/api-spine.manifest.json"
SPINE = ROOT / "ultima/ollama-ffmpeg-antenna-v3/api_spine.py"
COMPOSITION = ROOT / "ultima/ollama-ffmpeg-antenna-v3/magic_server.py"
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


def require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(f"LUHM_API_SPINE_RED: {message}")


def main() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    roleplay = json.loads(FINAL_ROLEPLAY.read_text(encoding="utf-8"))
    vendor = json.loads(VENDOR.read_text(encoding="utf-8"))
    runtime = json.loads(RUNTIME_POLICY.read_text(encoding="utf-8"))
    spine = SPINE.read_text(encoding="utf-8")
    composition = COMPOSITION.read_text(encoding="utf-8")

    require(data.get("schema") == "luhm-os.api-spine.v1", "schema drift")
    require(data.get("project") == "LuHm OS", "project identity drift")
    require(data.get("machine_id") == "luhm_os", "machine identity drift")
    require(data.get("canonical_prefix") == "/api/v1", "canonical prefix drift")
    require(data.get("vendor_spine") == EXPECTED_VENDORS, "vendor spine drift")
    require(data.get("canonical_routes") == EXPECTED_ROUTES, "canonical route registry drift")

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
    require(data.get("migration", {}).get("silent_cross_provider_failover") is False, "silent provider failover enabled")
    require(data.get("migration", {}).get("secrets_in_client_or_repo") is False, "client/repo secrets enabled")

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

    print("LUHM_API_SPINE_GREEN")
    print(f"contract={data['schema']}")
    print(f"canonical_prefix={data['canonical_prefix']}")
    print(f"providers={','.join(EXPECTED_VENDORS)}")
    print("default_helpers=0")
    print("parallel_read_only_helpers_max=2")
    print("legacy_routes=preserved_compatibility_only")


if __name__ == "__main__":
    main()
