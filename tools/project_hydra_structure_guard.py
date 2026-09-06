#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HYDRA = ROOT / "lumh-os" / "projects" / "hydra"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def expect(actual, expected, label: str) -> None:
    if actual != expected:
        raise SystemExit(f"PROJECT HYDRA STRUCTURE RED: {label}: expected {expected!r}, got {actual!r}")


def main() -> None:
    project = load(HYDRA / "project.manifest.json")
    doctrine = load(HYDRA / "doctrine" / "directory.doctrine.json")
    samsung = load(HYDRA / "platforms" / "samsung-android-apk" / "platform.manifest.json")
    kai = load(HYDRA / "subsystems" / "kai9000" / "reference.json")
    hf = load(HYDRA / "integrations" / "hugging-face" / "reference.json")

    expect(project.get("name"), "Project Hydra", "project name")
    expect(project.get("canonical_root"), "lumh-os/projects/hydra", "project root")
    expect(project.get("parent_os"), "LumH OS", "parent OS")
    expect(project.get("branch_authority"), "main", "branch authority")
    expect(project.get("migration", {}).get("strategy"), "reference_not_copy", "migration strategy")
    expect(project.get("migration", {}).get("destructive_move_allowed"), False, "destructive migration")

    expect(
        doctrine.get("canonical_chain"),
        ["main", "lumh-os", "projects", "hydra", "platforms", "samsung-android-apk"],
        "canonical chain",
    )
    expect(doctrine.get("rules", {}).get("one_project_root"), True, "single project root")
    expect(doctrine.get("rules", {}).get("reference_not_copy"), True, "reference-not-copy doctrine")
    expect(doctrine.get("rules", {}).get("secrets_forbidden"), True, "secret doctrine")

    expect(samsung.get("canonical_path"), "lumh-os/projects/hydra/platforms/samsung-android-apk", "Samsung APK path")
    expect(samsung.get("implementation", {}).get("forge_repository"), "eggie-admin/vue-headless-cms", "APK forge repo")
    expect(samsung.get("implementation", {}).get("integration_strategy"), "reference_not_copy", "APK reference strategy")
    expect(samsung.get("security", {}).get("loopback_first"), True, "Samsung loopback")
    expect(samsung.get("security", {}).get("automatic_root"), False, "Samsung automatic root")
    expect(samsung.get("green_gate", {}).get("installable_apk_required_for_apk_release"), True, "APK evidence gate")

    expect(kai.get("canonical_registry"), "lumh-os/kai9000/project.manifest.json", "KAI registry reference")
    expect(kai.get("runtime"), "ultima/ollama-ffmpeg-antenna-v3", "KAI runtime reference")
    expect(kai.get("ingestion_strategy"), "reference_not_copy", "KAI ingestion")

    expect(hf.get("role"), "forge_and_model_catalog", "HF role")
    expect(hf.get("runtime_authority"), False, "HF runtime authority")
    expect(hf.get("auto_download"), False, "HF auto-download")
    expect(hf.get("revision_pin_required"), True, "HF revision pin")

    for legacy in [
        ROOT / "lumh-os" / "kai9000" / "project.manifest.json",
        ROOT / "ultima" / "ollama-ffmpeg-antenna-v3",
        ROOT / "samsung-sm-x400",
    ]:
        if not legacy.exists():
            raise SystemExit(f"PROJECT HYDRA STRUCTURE RED: compatibility source missing: {legacy.relative_to(ROOT)}")

    print("PROJECT HYDRA STRUCTURE GREEN")


if __name__ == "__main__":
    main()
