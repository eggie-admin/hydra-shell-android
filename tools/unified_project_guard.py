#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "lumh-os/kai9000/project.manifest.json"
VENDORS = ROOT / "integrations/vendor-apis.manifest.json"
FASTPATH = ROOT / ".github/workflows/project-hydra-fastpath-gate.yml"
LOCAL_CI = ROOT / ".github/workflows/hydra-local.yml"

NAME = "LuHm OS"
PID = "luhm_os"
SPINE = ["openai", "google", "github", "cloudflare", "hugging_face"]


def req(ok: bool, msg: str) -> None:
    if not ok:
        raise SystemExit(f"LUHM_UNIFIED_PROJECT_RED: {msg}")


def main() -> None:
    project = json.loads(PROJECT.read_text(encoding="utf-8"))
    vendors = json.loads(VENDORS.read_text(encoding="utf-8"))

    req(project.get("schema") == "luhm-os.project.v4", "project schema drift")
    req(project.get("name") == NAME, "project display name drift")
    req(project.get("project_id") == PID, "project id drift")
    req(project.get("identity", {}).get("canonical_display_name") == NAME, "canonical identity drift")
    req(project.get("identity", {}).get("canonical_machine_id") == PID, "canonical machine identity drift")
    req(project.get("identity", {}).get("legacy_alias_policy") == "component_or_history_only_not_independent_vendor_project", "legacy alias policy drift")
    for component in ("kai9000", "hydra", "cathedral"):
        req(project.get("components", {}).get(component, {}).get("is_independent_vendor_project") is False, f"{component} became a peer project")

    req(vendors.get("schema") == "luhm-os.vendor-apis.v7", "vendor schema drift")
    req(vendors.get("project_display_name") == NAME, "vendor project display name drift")
    req(vendors.get("project_id") == PID, "vendor project id drift")
    req(vendors.get("vendor_spine") == SPINE, "vendor spine drift")
    unified = vendors.get("unified_project", {})
    req(unified.get("policy") == "one_logical_project_many_vendor_transport_bindings", "unified-project policy drift")
    req(unified.get("new_vendor_resources_must_use_display_name") == NAME, "new vendor resource naming drift")
    for provider in SPINE:
        binding = vendors.get("providers", {}).get(provider, {})
        req(binding.get("project_label") == NAME, f"{provider} branding drift")
        req(binding.get("logical_project_id") == PID, f"{provider} logical project id drift")

    req(vendors["providers"]["openai"].get("legacy_project_policy") == "do_not_target_for_new_keys_or_new_work", "OpenAI legacy Project Hydra routing drift")
    req(project.get("remote", {}).get("github", {}).get("branch") == "luhmos-main", "canonical GitHub branch drift")
    req("gpt-6-astra" not in PROJECT.read_text(encoding="utf-8"), "retired OpenAI model resurrected")

    fastpath = FASTPATH.read_text(encoding="utf-8")
    req("name: LuHm OS Fastpath Gate" in fastpath, "Fastpath workflow branding drift")
    req("name: Project Hydra Fastpath Gate" not in fastpath, "Project Hydra escaped into workflow branding")
    req("group: luhm-os-fastpath-" in fastpath, "Fastpath concurrency branding drift")

    local_ci = LOCAL_CI.read_text(encoding="utf-8")
    req("name: LuHm OS Local CI" in local_ci, "Local CI branding drift")
    req("branches: [luhmos-main]" in local_ci, "Local CI canonical branch drift")
    req("branches: [main, hydra-ollama-local-001]" not in local_ci, "legacy Local CI branches resurrected")
    req("actions/checkout@11d5960a326750d5838078e36cf38b85af677262" in local_ci, "Local CI checkout action is not pinned")
    req("actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065" in local_ci, "Local CI setup-python action is not pinned")
    req("persist-credentials: false" in local_ci, "Local CI checkout credentials persist")
    req("uses: actions/checkout@v4" not in local_ci, "floating checkout action resurrected")
    req("uses: actions/setup-python@v5" not in local_ci, "floating setup-python action resurrected")

    print("LUHM_UNIFIED_PROJECT=GREEN")
    print("PROJECT=LuHm OS")
    print("PROJECT_ID=luhm_os")
    print("LEGACY_NAMES=COMPONENT_OR_HISTORY_ONLY")
    print("VENDOR_SPINE=openai,google,github,cloudflare,hugging_face")


if __name__ == "__main__":
    main()
