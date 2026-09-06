#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "lumh-os" / "kai9000" / "project.manifest.json"
RUNTIME = ROOT / "ultima" / "ollama-ffmpeg-antenna-v3"
RUNTIME_MANIFEST = RUNTIME / "KAI9000_ULTIMA_OLLAMA_FFMPEG_ANTENNA_V3.manifest.json"
MAIN_PY = RUNTIME / "main.py"


def fail(message: str) -> None:
    print(f"CI GUARD RED: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid JSON {path.relative_to(ROOT)}: {exc}")


def assert_equal(actual, expected, label: str) -> None:
    if actual != expected:
        fail(f"{label}: expected {expected!r}, got {actual!r}")


def architecture_checks() -> None:
    project = load_json(PROJECT)
    runtime = load_json(RUNTIME_MANIFEST)

    assert_equal(project.get("source_path"), "ultima/ollama-ffmpeg-antenna-v3", "source_path")
    assert_equal(project.get("ingestion", {}).get("strategy"), "reference_not_copy", "ingestion strategy")
    assert_equal(project.get("ingestion", {}).get("remote_shell"), False, "remote shell policy")
    assert_equal(project.get("ingestion", {}).get("public_ollama_exposure"), False, "public Ollama policy")
    assert_equal(project.get("runtime", {}).get("ollama"), "http://127.0.0.1:11434", "Ollama endpoint")
    assert_equal(project.get("runtime", {}).get("antenna"), "http://127.0.0.1:8797", "antenna endpoint")
    assert_equal(project.get("remote", {}).get("github", {}).get("branch"), "main", "GitHub canonical branch")
    assert_equal(project.get("remote", {}).get("google_drive", {}).get("secrets_allowed"), False, "Drive secret policy")

    assert_equal(runtime.get("planes", {}).get("github_remote", {}).get("branch"), "main", "runtime GitHub branch")
    assert_equal(runtime.get("planes", {}).get("github_remote", {}).get("runtime_ai"), False, "GitHub runtime AI policy")
    assert_equal(runtime.get("planes", {}).get("google_drive_backup", {}).get("secrets"), False, "runtime Drive secret policy")

    if not RUNTIME.is_dir():
        fail("canonical runtime directory missing")

    main_text = MAIN_PY.read_text(encoding="utf-8")
    if 'host="127.0.0.1"' not in main_text:
        fail("FastAPI/uvicorn must bind to 127.0.0.1")
    if 'host="0.0.0.0"' in main_text:
        fail("public 0.0.0.0 bind found in runtime")


def secret_scan() -> None:
    patterns = {
        "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
        "OpenAI-style key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
        "GitHub classic token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
        "GitHub fine-grained token": re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
        "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        "Slack bot token": re.compile(r"\bxoxb-[A-Za-z0-9-]{20,}\b"),
    }
    suffixes = {".py", ".json", ".toml", ".yml", ".yaml", ".md", ".sh", ".html", ".example"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix.lower() not in suffixes and path.name != ".env.example":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for label, pattern in patterns.items():
            if pattern.search(text):
                fail(f"secret-shaped value ({label}) in {path.relative_to(ROOT)}")


def main() -> None:
    architecture_checks()
    secret_scan()
    print("KAI9000 CI GUARD GREEN")


if __name__ == "__main__":
    main()
