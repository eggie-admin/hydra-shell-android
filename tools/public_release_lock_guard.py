#!/usr/bin/env python3
"""Fail closed if the locked LuHm public-release surface regains publish authority."""
from pathlib import Path
import re
import sys

FILES = {
    ".github/workflows/luhmos-main-release-launch.yml": "LUHMOS_PUBLIC_RELEASE_LAUNCH=OFF",
    ".github/workflows/luhmos-fdroid-public-release.yml": "LUHMOS_PUBLIC_PUBLISH=OFF",
    ".github/workflows/luhmos-github-release.yml": "LUHMOS_GITHUB_RELEASE_PUBLISH=OFF",
    ".github/workflows/luhmos-izzy-github-release.yml": "LUHMOS_IZZY_PUBLICATION=OFF",
}

FORBIDDEN = {
    "push trigger": re.compile(r"(?m)^  push:"),
    "workflow_run trigger": re.compile(r"(?m)^  workflow_run:"),
    "contents write": re.compile(r"(?m)^\s*contents:\s*write\s*$"),
    "actions write": re.compile(r"(?m)^\s*actions:\s*write\s*$"),
    "secret reference": re.compile(r"\$\{\{\s*secrets\."),
    "release creation/upload": re.compile(r"\bgh\s+release\s+(?:create|upload)\b"),
    "workflow dispatch command": re.compile(r"\bgh\s+workflow\s+run\b"),
    "legacy public mirror switch": re.compile(r"publish_public_mirror=true"),
}

errors: list[str] = []
for filename, marker in FILES.items():
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
    for label, pattern in FORBIDDEN.items():
        if pattern.search(text):
            errors.append(f"forbidden:{filename}:{label}")

if errors:
    print("LUHMOS_PUBLIC_RELEASE_LOCK_RED", file=sys.stderr)
    for error in errors:
        print(error, file=sys.stderr)
    raise SystemExit(1)

print("LUHMOS_PUBLIC_RELEASE_LOCK_GREEN")
print("AUTO_PUBLIC_RELEASE_DISPATCH=ABSENT")
print("GITHUB_RELEASE_PUBLISHER=LOCKED")
print("IZZY_PUBLICATION=LOCKED")
