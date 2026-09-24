#!/usr/bin/env python3
"""Verify and stage LuHm public-safe source-native fast-build assets.

Only files explicitly marked LUHM_ORIGINAL in the manifest may enter the runtime
staging directory. Private references, mixed-license runtime packs and community
plugins remain outside the Android payload.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

EXPECTED_SCHEMA = "luhm-os.fastbuild-assets.v2"
EXPECTED_STATUS = "PROPOSED_PUBLIC_SAFE_SOURCE_CACHE"


def sha256File(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def gitBlobSha1(path: Path) -> str:
    body = path.read_bytes()
    framed = b"blob " + str(len(body)).encode("ascii") + b"\0" + body
    return hashlib.sha1(framed).hexdigest()


def loadJson(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def stageAssets(repoRoot: Path, manifestPath: Path, destination: Path, receiptPath: Path | None) -> dict:
    manifest = loadJson(manifestPath)
    if manifest.get("schema") != EXPECTED_SCHEMA:
        raise SystemExit("unexpected fastbuild asset schema")
    if manifest.get("status") != EXPECTED_STATUS:
        raise SystemExit("fastbuild asset cache is not in proposed public-safe state")

    rights = manifest.get("rights_gate", {})
    excluded = set(rights.get("hard_exclude", []))
    if "THIRD_PARTY_PRIVATE_REFERENCE" not in excluded:
        raise SystemExit("private-reference exclusion is missing")
    if rights.get("private_pck_files_in_public_git") is not False:
        raise SystemExit("private PCK exclusion must remain false")
    if rights.get("community_plugins_auto_enabled") is not False:
        raise SystemExit("community plugin auto-enable must remain false")

    runtimeRows = manifest.get("runtime_files", [])
    if not runtimeRows:
        raise SystemExit("no runtime fastbuild assets declared")

    checked: list[tuple[dict, Path]] = []
    for row in runtimeRows:
        if row.get("rights") != "LUHM_ORIGINAL":
            raise SystemExit(f"non-original runtime asset blocked: {row.get('path')}")
        relative = Path(row["path"])
        source = repoRoot / relative
        if not source.is_file():
            raise SystemExit(f"runtime asset missing: {relative}")
        actualBlob = gitBlobSha1(source)
        if actualBlob != row.get("git_blob_sha1"):
            raise SystemExit(f"git blob mismatch: {relative}")
        checked.append((row, source))

    atlasMetaPath = repoRoot / manifest["atlas"]["metadata"]
    atlasMeta = loadJson(atlasMetaPath)
    regions = atlasMeta.get("regions", {})
    if atlasMeta.get("region_count") != len(regions):
        raise SystemExit("atlas region count mismatch")
    if len(regions) != int(manifest.get("atlas", {}).get("regions", 0)):
        raise SystemExit("manifest/atlas logical count mismatch")

    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True, exist_ok=True)

    staged = []
    for row, source in checked:
        target = destination / source.name
        shutil.copy2(source, target)
        staged.append({
            "source": row["path"],
            "path": target.name,
            "role": row.get("role"),
            "bytes": target.stat().st_size,
            "sha256": sha256File(target),
            "git_blob_sha1": gitBlobSha1(target),
        })

    logicalCount = int(manifest.get("logical_asset_count", 0))
    expectedLogical = len(regions) + 2
    if logicalCount != expectedLogical:
        raise SystemExit(f"logical asset count mismatch: {logicalCount} != {expectedLogical}")

    receipt = {
        "schema": "luhm-os.fastbuild-assets.stage-receipt.v2",
        "runtime_rights": "LUHM_ORIGINAL_ONLY",
        "logical_asset_count": logicalCount,
        "atlas_regions": len(regions),
        "staged_file_count": len(staged),
        "community_plugins_auto_enabled": False,
        "private_reference_assets_included": False,
        "mixed_license_runtime_assets_included": False,
        "staged": staged,
    }
    if receiptPath:
        receiptPath.parent.mkdir(parents=True, exist_ok=True)
        receiptPath.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_root", type=Path)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    receipt = stageAssets(
        args.repo_root.resolve(),
        args.manifest.resolve(),
        args.destination.resolve(),
        args.receipt.resolve() if args.receipt else None,
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
