#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "lumh-os" / "kai9000" / "project.manifest.json"
HF_DOCTRINE = ROOT / "lumh-os" / "kai9000" / "huggingface.doctrine.json"
RUNTIME = ROOT / "ultima" / "ollama-ffmpeg-antenna-v3"
RUNTIME_MANIFEST = RUNTIME / "KAI9000_ULTIMA_OLLAMA_FFMPEG_ANTENNA_V3.manifest.json"
MAIN_PY = RUNTIME / "main.py"

# Exact fake credentials intentionally used by tests that verify prompt-secret
# rejection. Only these literal values at these literal paths are scrubbed from
# the scanner input. Any other secret-shaped value in the same file still fails.
SYNTHETIC_SECRET_FIXTURES = {
    Path("backend/tests/test_remote_ai_router.py"): (
        "hf_abcdefghijklmnopqrstuvwxyz1234567890",
    ),
}


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
    hf = load_json(HF_DOCTRINE)

    assert_equal(project.get("source_path"), "ultima/ollama-ffmpeg-antenna-v3", "source_path")
    assert_equal(project.get("ingestion", {}).get("strategy"), "reference_not_copy", "ingestion strategy")
    assert_equal(project.get("ingestion", {}).get("remote_shell"), False, "remote shell policy")
    assert_equal(project.get("ingestion", {}).get("public_ollama_exposure"), False, "public Ollama policy")
    assert_equal(project.get("runtime", {}).get("ollama"), "http://127.0.0.1:11434", "Ollama endpoint")
    assert_equal(project.get("runtime", {}).get("antenna"), "http://127.0.0.1:8797", "antenna endpoint")
    assert_equal(project.get("remote", {}).get("github", {}).get("branch"), "main", "GitHub canonical branch")
    assert_equal(project.get("remote", {}).get("google_drive", {}).get("secrets_allowed"), False, "Drive secret policy")

    project_hf = project.get("remote", {}).get("hugging_face", {})
    assert_equal(project_hf.get("role"), "forge_and_model_catalog", "Hugging Face role")
    assert_equal(project_hf.get("runtime_authority"), False, "Hugging Face runtime authority")
    assert_equal(project_hf.get("secret_store"), False, "Hugging Face secret-store policy")
    assert_equal(project_hf.get("auto_download"), False, "Hugging Face auto-download policy")
    assert_equal(project_hf.get("auto_execute_remote_code"), False, "Hugging Face remote-code execution policy")
    assert_equal(project_hf.get("revision_pin_required"), True, "Hugging Face revision pin policy")
    assert_equal(project_hf.get("doctrine"), "lumh-os/kai9000/huggingface.doctrine.json", "Hugging Face doctrine path")

    assert_equal(hf.get("role"), "forge_and_model_catalog", "HF doctrine role")
    assert_equal(hf.get("runtime_authority"), False, "HF doctrine runtime authority")
    assert_equal(hf.get("auto_download"), False, "HF doctrine auto-download")
    assert_equal(hf.get("auto_execute_remote_code"), False, "HF doctrine auto-execute")
    assert_equal(hf.get("trust_remote_code_default"), False, "HF trust_remote_code default")
    assert_equal(hf.get("download", {}).get("explicit_operator_action_required"), True, "HF explicit download approval")
    assert_equal(hf.get("download", {}).get("revision_pin_required"), True, "HF pinned revision")
    assert_equal(hf.get("download", {}).get("license_record_required"), True, "HF license record")
    assert_equal(hf.get("auth", {}).get("tokens_in_git"), False, "HF token Git policy")
    assert_equal(hf.get("auth", {}).get("tokens_in_drive_manifest"), False, "HF token Drive policy")
    assert_equal(hf.get("promotion", {}).get("operator_approval"), True, "HF model promotion approval")
    assert_equal(hf.get("offline", {}).get("existing_local_models_continue_working"), True, "HF offline doctrine")

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
        "Hugging Face token": re.compile(r"\bhf_[A-Za-z0-9]{20,}\b"),
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

        relative = path.relative_to(ROOT)
        for synthetic_value in SYNTHETIC_SECRET_FIXTURES.get(relative, ()):
            text = text.replace(synthetic_value, "SYNTHETIC_SECRET_FIXTURE")

        for label, pattern in patterns.items():
            if pattern.search(text):
                fail(f"secret-shaped value ({label}) in {relative}")


def main() -> None:
    architecture_checks()
    secret_scan()
    print("KAI9000 CI GUARD GREEN")


if __name__ == "__main__":
    main()
