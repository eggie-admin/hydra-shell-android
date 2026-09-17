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


def require_text(path: Path, needles: list[str]) -> None:
    if not path.is_file():
        die(f"missing required file: {path}")
    text = path.read_text(encoding="utf-8")
    missing = [needle for needle in needles if needle not in text]
    if missing:
        die(f"{path}: missing contract markers {missing}")


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
    for required in ["enterprise-distribution.js", "distribution"]:
        if required not in manifest.get("bundle", {}).get("include", []):
            die(f"source bundle missing enterprise distribution input {required}")

    pyproject = (game / "python/pyproject.toml").read_text(encoding="utf-8")
    if 'requires = ["hatchling==1.32.3"]' not in pyproject:
        die("Python build backend is not exactly pinned")

    wizard = lock.get("wizard", {})
    if wizard.get("schema") != "luhm_os.npm_compile_wizard.v1":
        die("npm wizard schema drift")
    if wizard.get("zero_dependency") is not True:
        die("npm wizard must remain zero-dependency")
    if wizard.get("npm_install_lifecycle_device_mutation") is not False:
        die("npm install lifecycle must never mutate a device")
    if wizard.get("install_default") != "staged_only":
        die("wizard install default must stay staged-only")
    if wizard.get("explicit_install_apply_flag") != "--apply":
        die("wizard explicit apply flag drift")
    if wizard.get("candidate_package") != "art.eggiebagelface.luhmos.candidate":
        die("candidate package drift")
    if wizard.get("production_package") != "art.eggiebagelface.luhmos":
        die("production package drift")

    distribution = lock.get("distribution", {})
    if distribution.get("schema") != "luhm_os.enterprise_distribution.v1":
        die("enterprise distribution schema drift")
    if distribution.get("release_provider") != "github_releases":
        die("release provider must be GitHub Releases")
    if distribution.get("release_repository") != "eggie-admin/hydra-shell-android":
        die("release repository drift")
    for key in ["arbitrary_apk_url", "downgrade_allowed", "silent_install", "silent_uninstall", "public_backend_fallback"]:
        if distribution.get(key) is not False:
            die(f"enterprise distribution must keep {key}=false")
    for key in ["release_asset_sha256_required", "same_android_signer_required"]:
        if distribution.get(key) is not True:
            die(f"enterprise distribution must keep {key}=true")

    dist_contract = load_json(game / distribution["contract"])
    if dist_contract.get("schema") != distribution["schema"]:
        die("distribution contract schema mismatch")
    release = dist_contract.get("release", {})
    if release.get("provider") != "github_releases" or release.get("repository") != "eggie-admin/hydra-shell-android":
        die("distribution release authority drift")
    if release.get("manifest_asset") != "luhmos-release.json":
        die("release manifest asset drift")
    if dist_contract.get("local_harness", {}).get("public_backend_fallback") is not False:
        die("local harness may not fall back to a public backend")

    package = load_json(repo / wizard["package_manifest"])
    package_lock = load_json(repo / wizard["package_lock"])
    if package.get("private") is not True:
        die("root npm package must remain private")
    if package.get("version") != "1.0.10":
        die("root npm package version drift")
    if package.get("dependencies") or package.get("devDependencies"):
        die("root compile wizard must remain dependency-free")
    required_scripts = {"start", "options", "test", "dryrun", "audit", "build", "install"}
    scripts = package.get("scripts", {})
    if not required_scripts.issubset(scripts):
        die(f"npm command surface incomplete: {sorted(required_scripts - set(scripts))}")
    if package_lock.get("lockfileVersion") != 3:
        die("package-lock version drift")
    if set(package_lock.get("packages", {})) != {""}:
        die("package-lock is no longer zero-dependency")

    wizard_path = repo / wizard["entrypoint"]
    test_path = repo / wizard["test_file"]
    require_text(wizard_path, [
        "LUHM_COMPILE_WIZARD_V1",
        "INSTALL_STAGED_CROWN_REQUIRED",
        "art.eggiebagelface.luhmos.candidate",
        "npm_command === 'install'",
        "requestedApply(args)",
        "adb",
    ])
    require_text(test_path, [
        "ordinary npm install lifecycle cannot mutate a device",
        "device mutation requires explicit apply flag",
        "wizard accepts only the collision-free candidate package",
    ])
    require_text(game / distribution["runtime_client"], [
        "LUHM_OS_ENTERPRISE_DISTRIBUTION_V1",
        "api.github.com/repos/",
        "/releases/download/",
        "luhmos-release.json",
        "app.uninstall.open",
        "lum.eggiebagelface.lan",
    ])
    require_text(game / distribution["runtime_test"], [
        "pins updates to the LuHm GitHub Releases lane",
        "branded uninstall is explicit and delegates to native Android",
        "local harness probes only approved local origins",
    ])
    require_text(game / distribution["native_patch"], [
        "LUHM_ENTERPRISE_DISTRIBUTION_NATIVE_V1",
        "RELEASE_HOST",
        "expectedSha256",
        "Intent.ACTION_DELETE",
    ])
    require_text(game / distribution["release_manifest_builder"], [
        "luhm_os.release.v1",
        "apk_sha256",
        "release_page",
    ])
    require_text(game / distribution["local_backend_harness"], [
        '"local_first"',
        '"public_backend_fallback": False',
        '"https://appassets.androidplatform.net"',
    ])

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

    universal = workflows[2].read_text(encoding="utf-8")
    for marker in [
        "npm ci --ignore-scripts --offline",
        "npm test",
        "npm run dryrun",
        "tools/luhm-compile-wizard.mjs",
        "package-lock.json",
    ]:
        if marker not in universal:
            die(f"universal forge workflow missing npm wizard marker: {marker}")

    drive = workflows[0].read_text(encoding="utf-8")
    if lock["pinned_inputs"]["android_forge_commit"] not in drive:
        die("Android donor commit drift")
    if lock["pinned_inputs"]["avatar_sha256"] not in drive:
        die("avatar digest drift")
    if "sha256sum --check --strict" not in drive:
        die("verified download digest checks missing")
    for marker in [
        "patch-enterprise-android.py",
        "enterprise-distribution.js",
        "enterprise-distribution.test.mjs",
        "LUHM_ENTERPRISE_ANDROID_PATCH_GREEN",
        "luhmos-release.json",
    ]:
        if marker not in drive:
            die(f"Android candidate workflow missing enterprise marker: {marker}")

    if lock["network"].get("cache_restore_policy") != "exact_key_only":
        die("cache restore policy is not exact-key-only")
    if lock["network"].get("runtime_update_remote_authority") != "github_releases_only":
        die("runtime update authority is not GitHub Releases only")
    if lock["network"].get("local_backend_public_fallback") is not False:
        die("runtime local backend public fallback must stay disabled")
    if lock["reproducibility"].get("source_archive_mtime") != 0:
        die("source archive mtime is not normalized")

    print("LUHM_UNIVERSAL_FORGE_LOCK_GREEN")
    print(f"locked_actions={len(actions)}")
    print(f"locked_workflows={len(workflows)}")
    print(f"wizard_commands={','.join(wizard['commands'])}")
    print("enterprise_distribution=GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
