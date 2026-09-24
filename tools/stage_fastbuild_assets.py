#!/usr/bin/env python3
"""Verify and stage LuHm public-safe fast-build assets.

This intentionally stages only LuHm-original proxy art into runtime assets.
Community files in the pack remain source/reference material and are never auto-enabled.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
import zipfile
from pathlib import Path

EXPECTED_SCHEMA = "luhm-os.fastbuild-assets.v1"
EXPECTED_STATUS = "PROPOSED_PUBLIC_SAFE_SOURCE_CACHE"


def sha256File(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def loadJson(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def verifyManifest(root: Path, manifest: dict) -> None:
    if manifest.get("schema") != EXPECTED_SCHEMA:
        raise SystemExit("unexpected fastbuild asset schema")
    if manifest.get("status") != EXPECTED_STATUS:
        raise SystemExit("fastbuild asset cache is not in proposed public-safe state")
    excluded = set(manifest.get("rights_gate", {}).get("exclude", []))
    if "THIRD_PARTY_PRIVATE_REFERENCE" not in excluded:
        raise SystemExit("private-reference exclusion is missing")
    for row in manifest.get("files", []):
        relative = Path(row["path"])
        path = root / relative
        if not path.is_file():
            raise SystemExit(f"asset missing from cache pack: {relative}")
        if path.stat().st_size != int(row["bytes"]):
            raise SystemExit(f"asset size mismatch: {relative}")
        if sha256File(path) != row["sha256"]:
            raise SystemExit(f"asset sha256 mismatch: {relative}")


def stageAssets(pack: Path, manifestPath: Path, destination: Path, receiptPath: Path | None) -> dict:
    manifest = loadJson(manifestPath)
    expectedPackHash = manifest.get("pack_sha256")
    actualPackHash = sha256File(pack)
    if expectedPackHash != actualPackHash:
        raise SystemExit("fastbuild pack sha256 mismatch")

    with tempfile.TemporaryDirectory(prefix="luhm-fastbuild-") as tempName:
        tempRoot = Path(tempName)
        with zipfile.ZipFile(pack) as archive:
            archive.extractall(tempRoot)
        internalManifest = loadJson(tempRoot / "manifest.json")
        internalManifest["pack_sha256"] = expectedPackHash
        if internalManifest != manifest:
            raise SystemExit("external and packed fastbuild manifests differ")
        verifyManifest(tempRoot, manifest)

        if destination.exists():
            shutil.rmtree(destination)
        destination.mkdir(parents=True, exist_ok=True)

        staged = []
        for source in sorted((tempRoot / "original").glob("*.webp")):
            target = destination / source.name
            shutil.copy2(source, target)
            staged.append({
                "path": target.name,
                "bytes": target.stat().st_size,
                "sha256": sha256File(target),
            })

    receipt = {
        "schema": "luhm-os.fastbuild-assets.stage-receipt.v1",
        "pack_sha256": actualPackHash,
        "runtime_rights": "LUHM_ORIGINAL_ONLY",
        "community_plugins_auto_enabled": False,
        "private_reference_assets_included": False,
        "staged": staged,
    }
    if receiptPath:
        receiptPath.parent.mkdir(parents=True, exist_ok=True)
        receiptPath.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pack", type=Path)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    receipt = stageAssets(
        args.pack.resolve(),
        args.manifest.resolve(),
        args.destination.resolve(),
        args.receipt.resolve() if args.receipt else None,
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
