#!/usr/bin/env python3
"""Fail-closed validation for the LuHm universal remote forge contract."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HEX40 = re.compile(r"[0-9a-f]{40}")


def die(message: str) -> "NoReturn":
    raise SystemExit(f"UNIVERSAL_FORGE_RED: {message}")


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        die(f"{path}: {exc}")


def find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / ".github/workflows").is_dir() and (candidate / "project").is_dir():
            return candidate
    die("repository root not found")


def main() -> int:
    game = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    repo = find_repo_root(game)
    lock_path = game / "forge/forge-lock.json"
    lock = load_json(lock_path)

    if lock.get("schema") != "luhm_os.universal_forge_lock.v1":
        die("unexpected forge lock schema")
    if lock.get("state") != "candidate_locked_not_crowned":
        die("forge authority state drift")

    actions = lock.get("actions", {})
    required_actions = {
        "actions/checkout",
        "actions/setup-python",
        "actions/setup-java",
        "actions/setup-node",
        "actions/cache",
        "actions/upload-artifact",
    }
    if set(actions) != required_actions:
        die("action lock set drift")
    for name, entry in actions.items():
        sha = entry.get("sha", "")
        version = entry.get("version", "")
        if not HEX40.fullmatch(sha):
            die(f"{name} is not pinned to an immutable 40-hex commit")
        if not re.fullmatch(r"v\d+\.\d+\.\d+", version):
            die(f"{name} lacks an exact semantic release label")

    runner = lock["runner"]
    if runner["label"] != "ubuntu-24.04" or runner["arch"] != "x86_64":
        die("runner contract drift")
    if runner.get("exact_kernel_version_pinned") is not False:
        die("hosted kernel must be capability-probed, not exact-version pinned")

    security = lock["security"]
    required_false = [
        "persist_checkout_credentials",
        "floating_action_refs",
        "pull_request_target",
        "ubuntu_latest",
        "ai_direct_shell_execution",
        "production_signing",
        "release_publish",
        "deploy",
        "crown",
    ]
    for key in required_false:
        if security.get(key) is not False:
            die(f"security lock must keep {key}=false")

    manifest = load_json(game / "source/source-manifest.json")
    if manifest.get("forge_lock") != "forge/forge-lock.json":
        die("source manifest does not bind the forge lock")
    if "forge" not in manifest.get("bundle", {}).get("include", []):
        die("source bundle does not include forge state")

    pyproject = (game / "python/pyproject.toml").read_text(encoding="utf-8")
    if 'requires = ["hatchling==1.32.3"]' not in pyproject:
        die("Python build backend is not exactly pinned")

    workflows = [
        repo / ".github/workflows/luhmos-drive-avatar-candidate.yml",
        repo / ".github/workflows/luhmos-source-vendor-gate.yml",
        repo / ".github/workflows/luhmos-universal-forge-gate.yml",
    ]
    uses_re = re.compile(r"^\s*-?\s*uses:\s+(actions/[A-Za-z0-9_.-]+)@([^\s#]+)", re.M)
    forbidden = {
        "ubuntu-latest": "floating runner label",
        "pull_request_target": "privileged PR trigger",
        "persist-credentials: true": "persisted checkout credential",
        "permissions: write-all": "broad workflow permission",
        "restore-keys:": "broad cache restore fallback",
    }
    pipe_shell = re.compile(r"(?:curl|wget)[^\n]*(?:\||\|\s*)(?:bash|sh)\b")

    seen_actions: set[str] = set()
    for workflow in workflows:
        if not workflow.is_file():
            die(f"missing locked workflow: {workflow.relative_to(repo)}")
        text = workflow.read_text(encoding="utf-8")
        if "runs-on: ubuntu-24.04" not in text:
            die(f"{workflow.name}: runner is not ubuntu-24.04")
        if "permissions:\n  contents: read" not in text:
            die(f"{workflow.name}: contents-read-only permission marker missing")
        for token, reason in forbidden.items():
            if token in text:
                die(f"{workflow.name}: forbidden {reason}")
        if pipe_shell.search(text):
            die(f"{workflow.name}: pipe-to-shell download forbidden")
        for action, ref in uses_re.findall(text):
            seen_actions.add(action)
            expected = actions.get(action, {}).get("sha")
            if not expected:
                die(f"{workflow.name}: unregistered action {action}")
            if ref != expected:
                die(f"{workflow.name}: {action} ref {ref} != locked {expected}")

    if not required_actions.issubset(seen_actions):
        die(f"locked action set not fully exercised: {sorted(required_actions - seen_actions)}")

    drive = workflows[0].read_text(encoding="utf-8")
    if lock["pinned_inputs"]["android_forge_commit"] not in drive:
        die("Android donor commit drift")
    if lock["pinned_inputs"]["avatar_sha256"] not in drive:
        die("avatar digest drift")
    if "sha256sum --check --strict" not in drive:
        die("verified download digest checks missing")

    if lock["network"].get("cache_restore_policy") != "exact_key_only":
        die("cache restore policy is not exact-key-only")
    if lock["reproducibility"].get("source_archive_mtime") != 0:
        die("source archive mtime is not normalized")

    print("LUHM_UNIVERSAL_FORGE_LOCK_GREEN")
    print(f"locked_actions={len(actions)}")
    print(f"locked_workflows={len(workflows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
