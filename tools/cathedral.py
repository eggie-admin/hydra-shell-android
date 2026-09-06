#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CMS_DIR = Path(os.environ.get("CATHEDRAL_CMS_DIR", ROOT / "vendor" / "vue-headless-cms"))
WEB_OUT = ROOT / "godot" / "web"


def run(*cmd: str, cwd: Path | None = None) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, cwd=str(cwd or ROOT), check=True)


def have(name: str) -> bool:
    return shutil.which(name) is not None


def doctor() -> int:
    checks = {
        "python3": have("python3"),
        "node": have("node"),
        "npm": have("npm"),
        "git": have("git"),
        "java": have("java"),
        "godot": have("godot") or have("godot4"),
    }
    print(json.dumps(checks, indent=2))
    return 0 if all(checks.values()) else 2


def cms_install() -> None:
    if not (CMS_DIR / "package-lock.json").exists():
        raise SystemExit(f"Missing {CMS_DIR / 'package-lock.json'}; use a pinned CMS checkout.")
    run("npm", "ci", "--ignore-scripts", cwd=CMS_DIR)


def cms_build() -> None:
    cms_install()
    run("npm", "run", "build", cwd=CMS_DIR)
    dist = CMS_DIR / "dist"
    if not dist.is_dir():
        raise SystemExit("CMS build did not produce dist/")
    if WEB_OUT.exists():
        shutil.rmtree(WEB_OUT)
    shutil.copytree(dist, WEB_OUT)
    print(f"CMS payload staged at {WEB_OUT}")


def fdroid_check() -> int:
    problems: list[str] = []
    for forbidden in ("google-services.json", "firebase", "play-services"):
        for p in ROOT.rglob("*"):
            if forbidden.lower() in p.name.lower():
                problems.append(str(p.relative_to(ROOT)))
    for secret_name in (".env", "release.keystore", "upload-keystore.jks"):
        if (ROOT / secret_name).exists():
            problems.append(secret_name)
    if problems:
        print("F-Droid gate failed:\n- " + "\n- ".join(sorted(set(problems))))
        return 3
    print("F-Droid source gate: PASS")
    return 0


def build() -> None:
    if doctor() != 0:
        raise SystemExit("Toolchain doctor failed")
    cms_build()
    if fdroid_check() != 0:
        raise SystemExit("F-Droid source gate failed")
    print("Build-time payload is ready. Android packaging stays in Godot/Gradle; Node is not shipped in the APK.")


def wizard() -> None:
    print("Video Forge Cathedral wizard")
    print("1. doctor")
    print("2. CMS npm ci + Vite build")
    print("3. stage static payload into godot/web")
    print("4. run F-Droid source gate")
    print("5. export/sign Android with Godot/Gradle in CI")
    build()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["wizard", "doctor", "cms-install", "cms-build", "fdroid-check", "build"])
    args = parser.parse_args()
    rc = 0
    if args.command == "wizard": wizard()
    elif args.command == "doctor": rc = doctor()
    elif args.command == "cms-install": cms_install()
    elif args.command == "cms-build": cms_build()
    elif args.command == "fdroid-check": rc = fdroid_check()
    elif args.command == "build": build()
    raise SystemExit(rc)


if __name__ == "__main__":
    main()
