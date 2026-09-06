#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HYDRA = ROOT / "project" / "hydra"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def expect(actual, expected, label: str) -> None:
    if actual != expected:
        raise SystemExit(f"PROJECT HYDRA STRUCTURE RED: {label}: expected {expected!r}, got {actual!r}")


def main() -> None:
    project = load(HYDRA / "project.manifest.json")
    doctrine = load(HYDRA / "doctrine" / "directory-structure.json")
    samsung = load(HYDRA / "samsung" / "android" / "apk" / "app.reference.json")
    kai = load(HYDRA / "runtime" / "kai9000.reference.json")
    hf = load(HYDRA / "forge" / "hugging-face" / "reference.json")

    expect(project.get("name"), "Project Hydra", "project name")
    expect(project.get("canonical_root"), "project/hydra", "project root")
    expect(project.get("parent_os"), "LumH OS", "parent OS")
    expect(project.get("branch_authority"), "main", "branch authority")
    expect(project.get("migration", {}).get("strategy"), "reference_not_copy", "migration strategy")
    expect(project.get("migration", {}).get("destructive_move_allowed"), False, "destructive migration")

    expect(doctrine.get("branch_is_os"), "main", "OS branch")
    expect(doctrine.get("os_name"), "LumH OS", "OS name")
    expect(doctrine.get("project_namespace"), "project", "project namespace")
    expect(doctrine.get("project_slug"), "hydra", "project slug")
    expect(doctrine.get("canonical_root"), "project/hydra", "doctrine root")
    expect(
        doctrine.get("required_paths"),
        [
            "project/hydra/doctrine",
            "project/hydra/runtime",
            "project/hydra/forge",
            "project/hydra/samsung/android/apk",
        ],
        "required paths",
    )
    rules = doctrine.get("rules", {})
    expect(rules.get("singular_project_namespace"), True, "single project namespace")
    expect(rules.get("reference_not_copy"), True, "reference-not-copy doctrine")
    expect(rules.get("duplicate_runtime_forbidden"), True, "duplicate runtime doctrine")
    expect(rules.get("destructive_relocation_during_reroll"), False, "destructive reroll doctrine")
    expect(rules.get("green_ci_required_before_legacy_prune"), True, "legacy prune gate")
    expect(rules.get("secrets_in_repo"), False, "secret doctrine")

    expect(samsung.get("role"), "Samsung Android APK forge and cockpit surface", "Samsung role")
    expect(samsung.get("integration_strategy"), "reference_not_copy", "Samsung integration strategy")
    expect(samsung.get("source", {}).get("repository"), "eggie-admin/vue-headless-cms", "Samsung source repo")
    expect(samsung.get("integration_baseline", {}).get("branch"), "main", "Samsung integration baseline branch")
    expect(samsung.get("requirements", {}).get("installable_apk_required_for_green"), True, "APK evidence gate")
    expect(samsung.get("requirements", {}).get("loopback_only_local_services"), True, "Samsung loopback")
    expect(samsung.get("requirements", {}).get("automatic_root"), False, "Samsung automatic root")
    expect(samsung.get("requirements", {}).get("arbitrary_model_shell"), False, "Samsung model shell")
    expect(samsung.get("requirements", {}).get("secrets_in_apk_or_repo"), False, "Samsung secret policy")

    expect(kai.get("integration_strategy"), "reference_not_copy", "KAI integration")
    expect(kai.get("policy_manifest"), "lumh-os/kai9000/project.manifest.json", "KAI policy manifest")
    expect(kai.get("canonical_runtime"), "ultima/ollama-ffmpeg-antenna-v3", "KAI runtime")
    expect(kai.get("services", {}).get("ollama"), "http://127.0.0.1:11434", "KAI Ollama endpoint")
    expect(kai.get("rules", {}).get("public_ollama_exposure"), False, "KAI public Ollama policy")
    expect(kai.get("rules", {}).get("remote_shell"), False, "KAI remote shell policy")
    expect(kai.get("rules", {}).get("runtime_copy_under_project_hydra"), False, "KAI runtime copy policy")

    expect(hf.get("integration_strategy"), "reference_not_copy", "HF integration")
    expect(hf.get("role"), "forge_and_model_catalog", "HF role")
    expect(hf.get("runtime_authority"), False, "HF runtime authority")
    expect(hf.get("secret_store"), False, "HF secret store")
    expect(hf.get("auto_download"), False, "HF auto-download")
    expect(hf.get("auto_execute_remote_code"), False, "HF auto-execute")
    expect(hf.get("revision_pin_required"), True, "HF revision pin")
    expect(hf.get("license_record_required"), True, "HF license record")
    expect(hf.get("preferred_live_runtime"), "Ollama", "HF preferred runtime")

    for required in doctrine.get("required_paths", []):
        if not (ROOT / required).exists():
            raise SystemExit(f"PROJECT HYDRA STRUCTURE RED: required path missing: {required}")

    for legacy in doctrine.get("legacy_compatibility_sources", []):
        if not (ROOT / legacy).exists():
            raise SystemExit(f"PROJECT HYDRA STRUCTURE RED: compatibility source missing: {legacy}")

    duplicate = ROOT / "lumh-os" / "projects" / "hydra"
    if duplicate.exists():
        raise SystemExit("PROJECT HYDRA STRUCTURE RED: duplicate lumh-os/projects/hydra namespace exists")

    print("PROJECT HYDRA STRUCTURE GREEN")


if __name__ == "__main__":
    main()
