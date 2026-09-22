#!/usr/bin/env python3
"""Fail closed around LuHm OS public-release authority.

Normal public surfaces remain locked read-only. The GitHub beta publisher is
allowed only as a manual, evidence-bound publisher with no signing secrets.
"""
from pathlib import Path
import re

LOCKED_FILES = {
    ".github/workflows/luhmos-main-release-launch.yml": "LUHMOS_PUBLIC_RELEASE_LAUNCH=OFF",
    ".github/workflows/luhmos-fdroid-public-release.yml": "LUHMOS_PUBLIC_PUBLISH=OFF",
    ".github/workflows/luhmos-izzy-github-release.yml": "LUHMOS_IZZY_PUBLICATION=OFF",
}

PUBLISHER = Path(".github/workflows/luhmos-github-release.yml")

AUTO_FORBIDDEN = {
    "push trigger": re.compile(r"(?m)^  push:"),
    "workflow_run trigger": re.compile(r"(?m)^  workflow_run:"),
    "schedule trigger": re.compile(r"(?m)^  schedule:"),
    "actions write": re.compile(r"(?m)^\s*actions:\s*write\s*$"),
    "workflow dispatch command": re.compile(r"\bgh\s+workflow\s+run\b"),
    "legacy public mirror switch": re.compile(r"publish_public_mirror=true"),
}

errors: list[str] = []

for filename, marker in LOCKED_FILES.items():
    path = Path(filename)
    if not path.is_file():
        errors.append(f"missing:{filename}")
        continue
    text = path.read_text(encoding="utf-8")
    if "workflow_dispatch:" not in text:
        errors.append(f"not_manual:{filename}")
    if "contents: read" not in text:
        errors.append(f"not_read_only:{filename}")
    if marker not in text:
        errors.append(f"missing_lock_marker:{filename}:{marker}")
    if re.search(r"\$\{\{\s*secrets\.", text):
        errors.append(f"secret_reference:{filename}")
    if re.search(r"\bgh\s+release\s+(?:create|upload)\b", text):
        errors.append(f"release_authority:{filename}")
    for label, pattern in AUTO_FORBIDDEN.items():
        if pattern.search(text):
            errors.append(f"forbidden:{filename}:{label}")

if not PUBLISHER.is_file():
    errors.append(f"missing:{PUBLISHER}")
else:
    text = PUBLISHER.read_text(encoding="utf-8")

    required = [
        "workflow_dispatch:",
        "actions: read",
        "contents: write",
        "acknowledge_public_beta_release",
        "source_run_id",
        "artifact_name",
        "release_sha",
        "LUHMOS_PUBLISHER_SIGNING_SECRETS=NONE",
        "LUHMOS_PUBLIC_BETA_AUTHORITY=EXPLICIT",
        "LuHm OS Signed Beta Candidate",
        "release-manifest.json",
        "sbom.spdx.json",
        "provenance.json",
        "evidence-sha256.txt",
        "luhm-os.signed-beta-artifact.v2",
        "LUHMOS_ANDROID_CERT_SHA256",
        "git rev-parse refs/remotes/origin/luhmos/beta",
        "LUHMOS_ENTERPRISE_SIGNED_ARTIFACT_EVIDENCE_GREEN",
        "LUHMOS_RELEASE_NAMESPACE_CLEAR",
        "gh release create",
        "--prerelease",
        "LUHMOS_PUBLIC_BETA_GITHUB_RELEASE_GREEN",
        "persist-credentials: false",
    ]
    for marker in required:
        if marker not in text:
            errors.append(f"publisher_missing:{marker}")

    if re.search(r"\$\{\{\s*secrets\.", text):
        errors.append("publisher_may_not_reference_signing_or_other_secrets")
    if "--clobber" in text:
        errors.append("publisher_may_not_clobber_release_assets")
    if "contents: read" in text:
        errors.append("publisher_permission_contract_ambiguous_contents_read")
    for label, pattern in AUTO_FORBIDDEN.items():
        if pattern.search(text):
            errors.append(f"publisher_forbidden:{label}")

if errors:
    print("LUHMOS_PUBLIC_RELEASE_LOCK_RED")
    for error in errors:
        print(error)
    raise SystemExit(1)

print("LUHMOS_PUBLIC_RELEASE_LOCK_GREEN")
print("AUTO_PUBLIC_RELEASE_DISPATCH=ABSENT")
print("GITHUB_BETA_PUBLISHER=MANUAL_EVIDENCE_BOUND")
print("GITHUB_BETA_PUBLISHER_SIGNING_SECRETS=ABSENT")
print("GITHUB_BETA_SBOM_PROVENANCE=REQUIRED")
print("FDROID_PUBLICATION=LOCKED")
print("IZZY_PUBLICATION=LOCKED")
