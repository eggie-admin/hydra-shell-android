#!/usr/bin/env python3
"""Stage the LuHm Android WebView payload without development-only control planes.

This copies the Cathedral presentation tree into an Android plugin asset directory while
excluding Python/operator tooling. It fails closed if the staged payload contains loopback or
control-plane markers forbidden by the golden beta release boundary.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path

EXCLUDED_TOP_LEVEL = {"python", "tools", "__pycache__", ".pytest_cache"}
FORBIDDEN = {
    "loopback_ip": re.compile(r"127\.0\.0\.1"),
    "localhost": re.compile(r"\blocalhost\b", re.I),
    "loopback_word": re.compile(r"\bloopback\b", re.I),
    "pair_code": re.compile(r"LUHM_PAIR_CODE"),
    "fastapi": re.compile(r"\bFastAPI\b"),
    "pysimplegui": re.compile(r"\bPySimpleGUI\b"),
    "termux_run_command": re.compile(r"com\.termux\.RUN_COMMAND|RunCommandService"),
}
TEXT_SUFFIXES = {
    ".html", ".htm", ".js", ".mjs", ".css", ".json", ".txt", ".md",
    ".xml", ".cfg", ".toml", ".yml", ".yaml",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ignore_entries(directory: str, names: list[str]) -> set[str]:
    base = Path(directory)
    ignored: set[str] = set()
    if base.name == "cathedral-game":
        ignored.update(name for name in names if name in EXCLUDED_TOP_LEVEL)
    ignored.update(name for name in names if name in {"__pycache__", ".pytest_cache"})
    return ignored


def scan_payload(root: Path) -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if path.stat().st_size > 2_000_000:
            continue
        body = path.read_text(encoding="utf-8", errors="replace")
        for name, pattern in FORBIDDEN.items():
            if pattern.search(body):
                hits.append({"rule": name, "path": str(path.relative_to(root))})
    return hits


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    source = args.source.resolve()
    destination = args.destination.resolve()
    if not source.is_dir():
        raise SystemExit(f"source is not a directory: {source}")

    if destination.exists():
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination, ignore=ignore_entries)

    for excluded in EXCLUDED_TOP_LEVEL:
        if (destination / excluded).exists():
            raise SystemExit(f"excluded development lane leaked into payload: {excluded}")

    hits = scan_payload(destination)
    files = [path for path in sorted(destination.rglob("*")) if path.is_file()]
    receipt = {
        "schema": "luhm-os.android-cms-payload.dry-run.v1",
        "release_boundary": "NATIVE_GODOT_BRIDGE_PLUS_PACKAGED_APPASSETS",
        "development_loopback_harness_included": False,
        "excluded_top_level": sorted(EXCLUDED_TOP_LEVEL),
        "file_count": len(files),
        "total_bytes": sum(path.stat().st_size for path in files),
        "forbidden_hits": hits,
        "files": [
            {"path": str(path.relative_to(destination)), "sha256": sha256(path)}
            for path in files
        ],
    }

    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        print(json.dumps(receipt, indent=2, sort_keys=True))

    if hits:
        for hit in hits:
            print(f"forbidden release marker: {hit['rule']} in {hit['path']}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
