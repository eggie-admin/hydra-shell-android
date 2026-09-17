#!/usr/bin/env python3
"""Create the LuHm GitHub Release manifest beside a built APK."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

TAG_RE = re.compile(r"^v\d+\.\d+\.\d+(?:-(?:testing|proposed|preview|beta)\.\d+)?$")
PKG_RE = re.compile(r"^art\.eggiebagelface\.luhmos(?:\.candidate)?$")
APK_RE = re.compile(r"^luhmos-[a-z0-9.-]+\.apk$")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--apk", required=True)
    p.add_argument("--tag", required=True)
    p.add_argument("--channel", choices=["testing", "proposed", "preview", "beta", "stable"], required=True)
    p.add_argument("--package-id", required=True)
    p.add_argument("--version-name", required=True)
    p.add_argument("--version-code", type=int, required=True)
    p.add_argument("--source-sha", required=True)
    p.add_argument("--forge-contract-sha256", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    apk = Path(a.apk)
    if not apk.is_file() or apk.stat().st_size <= 0:
        raise SystemExit("RELEASE_MANIFEST_RED: APK missing or empty")
    if not APK_RE.fullmatch(apk.name):
        raise SystemExit("RELEASE_MANIFEST_RED: APK asset name rejected")
    if not TAG_RE.fullmatch(a.tag):
        raise SystemExit("RELEASE_MANIFEST_RED: tag rejected")
    if not PKG_RE.fullmatch(a.package_id):
        raise SystemExit("RELEASE_MANIFEST_RED: package id rejected")
    if a.channel == "stable" and "-" in a.tag:
        raise SystemExit("RELEASE_MANIFEST_RED: stable channel requires stable tag")
    if a.channel != "stable" and f"-{a.channel}." not in a.tag:
        raise SystemExit("RELEASE_MANIFEST_RED: prerelease tag/channel mismatch")
    if not re.fullmatch(r"[0-9a-f]{40}", a.source_sha):
        raise SystemExit("RELEASE_MANIFEST_RED: source SHA rejected")
    if not re.fullmatch(r"[0-9a-f]{64}", a.forge_contract_sha256):
        raise SystemExit("RELEASE_MANIFEST_RED: forge contract digest rejected")

    payload = {
        "schema": "luhm_os.release.v1",
        "tag": a.tag,
        "channel": a.channel,
        "package_id": a.package_id,
        "version_name": a.version_name,
        "version_code": a.version_code,
        "apk_asset": apk.name,
        "apk_sha256": hashlib.sha256(apk.read_bytes()).hexdigest(),
        "source_sha": a.source_sha,
        "forge_contract_sha256": a.forge_contract_sha256,
        "install_authority": "android_user_confirmation",
        "uninstall_authority": "android_user_confirmation",
        "release_page": "https://github.com/eggie-admin/hydra-shell-android/releases",
    }
    out = Path(a.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("LUHM_RELEASE_MANIFEST_GREEN")
    print(f"apk_sha256={payload['apk_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
