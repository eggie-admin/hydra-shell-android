#!/usr/bin/env python3
"""Emit a secret-free runner observation bound to the immutable LuHm forge contract."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command(*argv: str) -> str:
    result = subprocess.run(argv, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return result.stdout.strip().splitlines()[0] if result.stdout.strip() else "unavailable"


def read_mem_kib() -> int:
    for line in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
        if line.startswith("MemTotal:"):
            return int(line.split()[1])
    return 0


def os_release() -> dict[str, str]:
    result: dict[str, str] = {}
    path = Path("/etc/os-release")
    if not path.is_file():
        return result
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        result[key] = value.strip().strip('"')
    return result


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: forge-fingerprint.py GAME_ROOT OUTPUT_JSON")

    game = Path(sys.argv[1]).resolve()
    output = Path(sys.argv[2]).resolve()
    lock_path = game / "forge/forge-lock.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8"))

    bound_files = {
        "forge_lock": lock_path,
        "source_manifest": game / "source/source-manifest.json",
        "toolchain_manifest": game / "source/toolchain-manifest.yaml",
        "vendor_catalog": game / "vendor/vendor-catalog.json",
        "python_manifest": game / "python/pyproject.toml",
        "java_manifest": game / "java/build.gradle.kts",
    }
    digests = {name: sha256(path) for name, path in bound_files.items()}
    contract_material = json.dumps({"lock": lock, "bound_file_sha256": digests}, sort_keys=True, separators=(",", ":")).encode()
    contract_digest = hashlib.sha256(contract_material).hexdigest()

    root_disk = shutil.disk_usage("/")
    observation = {
        "schema": "luhm_os.forge_fingerprint.v1",
        "source_sha": os.environ.get("LUHM_SOURCE_SHA") or os.environ.get("GITHUB_SHA") or "local",
        "contract_sha256": contract_digest,
        "bound_file_sha256": digests,
        "runner": {
            "system": platform.system(),
            "machine": platform.machine(),
            "kernel_release": platform.release(),
            "kernel_version": platform.version(),
            "cpu_threads": os.cpu_count() or 0,
            "memory_kib": read_mem_kib(),
            "root_free_kib": root_disk.free // 1024,
            "os_release": os_release(),
        },
        "tools": {
            "python": command(sys.executable, "--version"),
            "java": command("java", "-version"),
            "javac": command("javac", "-version"),
            "node": command("node", "--version"),
            "git": command("git", "--version"),
            "bash": command("bash", "--version"),
            "tar": command("tar", "--version"),
        },
        "authority": {
            "merge": "NOT_TRIGGERED",
            "deploy": "NOT_TRIGGERED",
            "release_signing": "NOT_TRIGGERED",
            "crown": "NOT_TRIGGERED",
        },
    }

    runner_lock = lock["runner"]
    if observation["runner"]["system"] != runner_lock["os"]:
        raise SystemExit("FORGE_FINGERPRINT_RED: runner OS drift")
    if observation["runner"]["machine"] != runner_lock["arch"]:
        raise SystemExit("FORGE_FINGERPRINT_RED: runner architecture drift")
    if observation["runner"]["cpu_threads"] < runner_lock["minimum_cpu_threads"]:
        raise SystemExit("FORGE_FINGERPRINT_RED: insufficient CPU threads")
    if observation["runner"]["memory_kib"] < runner_lock["minimum_memory_kib"]:
        raise SystemExit("FORGE_FINGERPRINT_RED: insufficient memory")
    if observation["runner"]["root_free_kib"] < runner_lock["minimum_root_free_kib"]:
        raise SystemExit("FORGE_FINGERPRINT_RED: insufficient root disk")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(observation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("LUHM_FORGE_FINGERPRINT_GREEN")
    print(f"contract_sha256={contract_digest}")
    print(f"output={output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
