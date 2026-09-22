#!/usr/bin/env python3
"""Validate the LuHm Cathedral source/vendor/toolchain contract without network access."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


def die(message: str) -> "NoReturn":
    raise SystemExit(f"SOURCE_CONTRACT_RED: {message}")


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        die(f"{path}: {exc}")


def require_text(path: Path, needles: list[str]) -> None:
    if not path.is_file():
        die(f"missing source file: {path.name}")
    text = path.read_text(encoding="utf-8")
    missing = [needle for needle in needles if needle not in text]
    if missing:
        die(f"{path}: missing contract markers {missing}")


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    manifest_path = root / "source/source-manifest.json"
    catalog_path = root / "vendor/vendor-catalog.json"

    manifest = load_json(manifest_path)
    catalog = load_json(catalog_path)

    if manifest.get("schema") != "luhm_os.cathedral_source.v1":
        die("unexpected source manifest schema")
    if catalog.get("schema") != "luhm_os.vendor_catalog.v1":
        die("unexpected vendor catalog schema")

    entrypoint = root / manifest["entrypoint"]
    if not entrypoint.is_file():
        die(f"missing entrypoint: {entrypoint.relative_to(root)}")

    for rel in manifest.get("runtime_assets", []):
        if not (root / rel).is_file():
            die(f"missing runtime asset: {rel}")

    for rel in manifest.get("templates", []):
        if not (root / rel).is_file():
            die(f"missing template: {rel}")

    for lane, rel in manifest.get("language_lanes", {}).items():
        if not (root / rel).is_file():
            die(f"missing {lane} lane manifest: {rel}")

    require_text(root / manifest["toolchain_manifest"], [
        "version: 3.14.7",
        "pyyaml: 6.0.3",
        "openai: 3.14.1",
        "google-genai: 2.24.0",
        "pysimplegui: 6.3.16",
        "audited_source_commit: 858d5d45babd66dc8ea7e20b797545b154e3f4dd",
        "android_apk_bundled: false",
        "automatic_toolkit_upgrade: false",
        "version: 17",
        "com.openai:openai-java: 4.63.3",
        "com.google.genai:google-genai: 1.72.0",
        "org.snakeyaml:snakeyaml-engine: 2.10",
        "direct_shell_execution: false",
    ])
    require_text(root / "config/luhm.example.yaml", [
        "execution_posture: advisory_only",
        "direct_shell_execution: false",
        "secrets_from_environment_only: true",
    ])
    require_text(root / "python/pyproject.toml", [
        'requires-python = ">=3.14,<3.15"',
        '"PyYAML==6.0.3"',
        'openai = ["openai==3.14.1"]',
        'google = ["google-genai==2.24.0"]',
        'gui = ["PySimpleGUI==6.3.16"]',
        'luhm-minigui = "luhm_core.minimal_gui:main"',
    ])
    require_text(root / "python/src/luhm_core/minimal_gui.py", [
        "LUHM_PYSIMPLEGUI_MINIMAL_OPERATOR_V1",
        "import PySimpleGUI as sg",
        "No shell execution. No silent install. No signing or release authority.",
        "Token remains memory-only.",
    ])
    gui_text = (root / "python/src/luhm_core/minimal_gui.py").read_text(encoding="utf-8")
    if re.search(r"\bsubprocess\b|\bos\.system\s*\(|shell\s*=\s*True", gui_text):
        die("minimal GUI contains forbidden direct shell execution primitive")
    require_text(root / "java/build.gradle.kts", [
        'JavaLanguageVersion.of(17)',
        'implementation("com.openai:openai-java:4.63.3")',
        'implementation("com.google.genai:google-genai:1.72.0")',
        'implementation("org.snakeyaml:snakeyaml-engine:2.10")',
    ])

    vendors = {item["id"]: item for item in catalog.get("vendors", [])}
    if len(vendors) != len(catalog.get("vendors", [])):
        die("duplicate vendor id")

    for profile, ids in manifest.get("vendor_profiles", {}).items():
        unknown = [vendor_id for vendor_id in ids if vendor_id not in vendors]
        if unknown:
            die(f"profile {profile} references unknown vendors: {unknown}")

    for vendor_id, item in vendors.items():
        for dependency in item.get("depends_on", []):
            if dependency not in vendors:
                die(f"{vendor_id} depends on unknown vendor {dependency}")
        if item.get("enabled"):
            digest = item.get("sha256")
            local_target = item.get("local_target")
            if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
                die(f"enabled vendor {vendor_id} lacks resolved sha256")
            if not local_target:
                die(f"enabled vendor {vendor_id} lacks local target")
            local_path = root / local_target
            if not local_path.is_file():
                die(f"enabled vendor {vendor_id} bytes missing: {local_target}")
            actual = hashlib.sha256(local_path.read_bytes()).hexdigest()
            if actual != digest:
                die(f"enabled vendor {vendor_id} sha256 mismatch")

    html = entrypoint.read_text(encoding="utf-8")
    if re.search(r'<script\b[^>]*\bsrc=["\']https?://', html, re.I):
        die("runtime entrypoint contains external script dependency")
    if re.search(r'<link\b[^>]*\bhref=["\']https?://', html, re.I):
        die("runtime entrypoint contains external stylesheet dependency")

    for rel in manifest.get("templates", []):
        text = (root / rel).read_text(encoding="utf-8")
        if "LUHM_TEMPLATE_V1" not in text:
            die(f"template lacks LUHM_TEMPLATE_V1 marker: {rel}")

    print("LUHM_SOURCE_VENDOR_TOOLCHAIN_CONTRACT_GREEN")
    print(f"runtime_assets={len(manifest.get('runtime_assets', []))}")
    print(f"vendor_catalog_entries={len(vendors)}")
    print(f"language_lanes={','.join(sorted(manifest.get('language_lanes', {})))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
