#!/usr/bin/env python3
"""Validate the LuHm Cathedral source/vendor contract without network access."""

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
    external_script = re.search(r'<script\b[^>]*\bsrc=["\']https?://', html, re.I)
    external_style = re.search(r'<link\b[^>]*\bhref=["\']https?://', html, re.I)
    if external_script or external_style:
        die("runtime entrypoint contains external script/style dependency")

    for rel in manifest.get("templates", []):
        text = (root / rel).read_text(encoding="utf-8")
        if "LUHM_TEMPLATE_V1" not in text:
            die(f"template lacks LUHM_TEMPLATE_V1 marker: {rel}")

    print("LUHM_SOURCE_VENDOR_CONTRACT_GREEN")
    print(f"runtime_assets={len(manifest.get('runtime_assets', []))}")
    print(f"vendor_catalog_entries={len(vendors)}")
    print(f"default_vendor_profile={manifest.get('default_vendor_profile')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
