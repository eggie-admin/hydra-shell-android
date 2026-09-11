#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HYDRA = ROOT / "project" / "hydra"
PROJECT = HYDRA / "project.manifest.json"
DIRECTORY = HYDRA / "doctrine" / "directory-structure.json"
RUNTIME = HYDRA / "runtime" / "kai9000.reference.json"
HF = HYDRA / "forge" / "hugging-face" / "reference.json"
APK = HYDRA / "samsung" / "android" / "apk" / "app.reference.json"


def fail(message: str) -> None:
    print(f"PROJECT HYDRA STRUCTURE RED: {message}", file=sys.stderr)
    raise SystemExit(1)


def load(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid JSON {path.relative_to(ROOT)}: {exc}")


def eq(actual, expected, label: str) -> None:
    if actual != expected:
        fail(f"{label}: expected {expected!r}, got {actual!r}")


def main() -> None:
    for path in (PROJECT, DIRECTORY, RUNTIME, HF, APK):
        if not path.is_file():
            fail(f"required file missing: {path.relative_to(ROOT)}")

    if (ROOT / "lumh-os" / "projects" / "hydra").exists():
        fail("obsolete plural path lumh-os/projects/hydra exists")

    project = load(PROJECT)
    directory = load(DIRECTORY)
    runtime = load(RUNTIME)
    hf = load(HF)
    apk = load(APK)

    eq(project.get("canonical_root"), "project/hydra", "canonical project root")
    eq(project.get("parent_os"), "LuHm OS", "parent OS")
    eq(project.get("branch_authority"), "luhmos-main", "branch authority")
    eq(project.get("migration", {}).get("strategy"), "reference_not_copy", "migration strategy")
    eq(project.get("migration", {}).get("destructive_move_allowed"), False, "destructive move policy")
    eq(project.get("platforms", {}).get("samsung_s24fe_stock"), "project/hydra/samsung/android/apk/app.reference.json", "Samsung APK path")

    eq(directory.get("project_namespace"), "project", "singular project namespace")
    eq(directory.get("project_slug"), "hydra", "project slug")
    eq(directory.get("canonical_root"), "project/hydra", "directory root")
    eq(directory.get("os_name"), "LuHm OS", "directory OS name")
    eq(directory.get("branch_is_os"), "luhmos-main", "directory branch authority")
    eq(directory.get("rules", {}).get("singular_project_namespace"), True, "singular namespace doctrine")
    eq(directory.get("rules", {}).get("reference_not_copy"), True, "reference doctrine")
    eq(directory.get("rules", {}).get("duplicate_runtime_forbidden"), True, "duplicate runtime doctrine")
    eq(directory.get("rules", {}).get("green_ci_required_before_legacy_prune"), True, "legacy prune gate")

    eq(runtime.get("canonical_runtime"), "ultima/ollama-ffmpeg-antenna-v3", "KAI runtime source")
    eq(runtime.get("integration_strategy"), "reference_not_copy", "KAI runtime strategy")
    eq(runtime.get("rules", {}).get("runtime_copy_under_project_hydra"), False, "KAI copy policy")
    eq(runtime.get("services", {}).get("ollama"), "http://127.0.0.1:11434", "Ollama loopback endpoint")

    eq(hf.get("role"), "forge_and_model_catalog", "Hugging Face role")
    eq(hf.get("runtime_authority"), False, "Hugging Face runtime authority")
    eq(hf.get("auto_download"), False, "Hugging Face auto-download")
    eq(hf.get("revision_pin_required"), True, "Hugging Face revision pin")

    eq(apk.get("canonical_repository"), "eggie-admin/hydra-shell-android", "APK canonical repository")
    eq(apk.get("canonical_branch"), "luhmos-main", "APK canonical branch")
    eq(apk.get("application", {}).get("name"), "LuHm OS", "APK application name")
    eq(apk.get("application", {}).get("package_id"), "art.eggiebagelface.luhmos", "APK package id")
    eq(apk.get("application", {}).get("release_signing_alias"), "luhmos-release", "APK release signer alias")
    eq(apk.get("application", {}).get("target_sdk"), 36, "APK target SDK")
    eq(apk.get("application", {}).get("primary_abi"), "arm64-v8a", "APK primary ABI")
    eq(apk.get("pinned_android_donor", {}).get("repository"), "eggie-admin/vue-headless-cms", "APK donor repository")
    eq(apk.get("pinned_android_donor", {}).get("branch"), "luhmos/s24fe-standalone-hardening-20260911", "APK donor branch")
    eq(apk.get("requirements", {}).get("normal_android_package_install"), True, "APK normal install gate")
    eq(apk.get("requirements", {}).get("launcher_start_required_for_green"), True, "APK launcher gate")
    eq(apk.get("requirements", {}).get("persistent_release_signer_required"), True, "APK persistent signer gate")
    eq(apk.get("requirements", {}).get("termux_required"), False, "APK Termux dependency policy")
    eq(apk.get("requirements", {}).get("external_localhost_daemon_required_for_launch"), False, "APK external-daemon policy")
    eq(apk.get("requirements", {}).get("arbitrary_model_shell"), False, "APK model-shell policy")

    for local_ref in (
        ROOT / runtime["policy_manifest"],
        ROOT / runtime["canonical_runtime"],
        ROOT / hf["doctrine"],
    ):
        if not local_ref.exists():
            fail(f"referenced compatibility source missing: {local_ref.relative_to(ROOT)}")

    print("PROJECT HYDRA STRUCTURE GREEN")


if __name__ == "__main__":
    main()
