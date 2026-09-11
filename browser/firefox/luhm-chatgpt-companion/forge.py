#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
VERSION = "0.3.3"
SEALED_COMMANDS = [
    "PET LUM",
    "ROLL D20",
    "GACHA PULL",
    "DATE EVENT",
    "SUMMON IMAGE",
    "CAST ULTIMA",
    "SAVEPOINT",
]
ALLOWED_HOSTS = {
    "https://chatgpt.com/*",
    "https://chat.openai.com/*",
    "http://127.0.0.1:8799/*",
    "http://localhost:8799/*",
}
FORBIDDEN_ASSET_EXTS = {
    ".png", ".jpg", ".jpeg", ".webp", ".gif",
    ".wav", ".mp3", ".ogg", ".oga", ".opus", ".m4a", ".aac", ".flac", ".webm",
    ".moc", ".moc3", ".mtn", ".pck", ".pak", ".cpk",
    ".acb", ".awb", ".hca", ".wem", ".bnk", ".adx", ".at3", ".at9", ".xma",
}
PACKAGE_FILES = [
    "manifest.json",
    "background.js",
    "content.js",
    "content.css",
    "popup.html",
    "popup.js",
    "popup.css",
    "icons/luhm.svg",
    "voice/lum-voice-profile.json",
    "AI_MANIFEST.json",
    "LUM_FIREFOX_JP_VOICE_TTL_20260911.json",
]


def load_text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def load_json(rel: str) -> dict:
    return json.loads(load_text(rel))


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def runtime_text() -> str:
    return "\n".join(load_text(name) for name in ("background.js", "content.js", "popup.js"))


def pass_1_manifest_scope() -> str:
    manifest = load_json("manifest.json")
    check(manifest.get("manifest_version") == 3, "manifest_version must be 3")
    check(manifest.get("version") == VERSION, f"manifest version must be {VERSION}")
    check("gecko_android" in manifest.get("browser_specific_settings", {}), "Firefox Android target missing")
    check(manifest.get("browser_specific_settings", {}).get("gecko", {}).get("data_collection_permissions", {}).get("required") == ["none"], "data collection declaration must be none")
    return "Firefox Android MV3 scope/version sealed"


def pass_2_permissions_hosts() -> str:
    manifest = load_json("manifest.json")
    perms = set(manifest.get("permissions", []))
    check(perms <= {"storage", "tabs"}, f"unexpected permissions: {sorted(perms)}")
    hosts = set(manifest.get("host_permissions", []))
    check(hosts == ALLOWED_HOSTS, f"host permissions drift: {sorted(hosts)}")
    return "permissions minimal; ChatGPT + loopback asset host only"


def pass_3_command_seal() -> str:
    content = load_text("content.js")
    popup = load_text("popup.html")
    for command in SEALED_COMMANDS:
        check(command in content, f"sealed command missing from content: {command}")
        check(command in popup, f"sealed command missing from popup: {command}")
    return "sealed command whitelist intact"


def pass_4_no_auto_send() -> str:
    text = runtime_text()
    forbidden = [
        r"requestSubmit\s*\(",
        r"\.submit\s*\(",
        r"data-testid\s*=\s*['\"]send",
        r"send-button",
        r"KeyboardEvent\s*\([^\n]*Enter",
        r"dispatchEvent\s*\([^\n]*(?:submit|Enter)",
    ]
    for pattern in forbidden:
        check(not re.search(pattern, text, re.I), f"auto-send pattern found: {pattern}")
    check("You choose Send" in text, "human-send UX marker missing")
    return "no prompt auto-submit path detected"


def pass_5_credentials_and_exfil() -> str:
    text = runtime_text()
    forbidden_tokens = [
        "OPENAI_API_KEY", "HF_TOKEN", "AMO_JWT", "Authorization: Bearer",
        "document.cookie", "chrome.cookies", "browser.cookies",
    ]
    for token in forbidden_tokens:
        check(token not in text, f"credential/exfil token in extension runtime: {token}")
    urls = re.findall(r"https?://[^\s'\"`)}]+", text)
    for url in urls:
        check(url.startswith("http://127.0.0.1:8799") or url.startswith("http://localhost:8799"), f"unexpected runtime URL: {url}")
    return "no credentials or non-loopback runtime exfil path"


def pass_6_voice_privacy_contract() -> str:
    content = load_text("content.js")
    voice = load_json("voice/lum-voice-profile.json")
    check(voice.get("original_voice_direction") is True, "voice must remain original")
    check(voice.get("imitate_specific_actor_or_character_voice") is False, "specific voice imitation must remain false")
    for marker in ("LUM-JP:", "LUM-EN:", "LUM-EMOTION:"):
        check(marker in content, f"voice marker missing: {marker}")
    check("if (!voiceModeEnabled) return;" in content, "newest assistant reader lacks explicit voice-mode gate")
    check("luhm_voice_mode_enabled" not in content, "voice mode must be session-only, not persisted")
    return "voice mode is explicit/session-only with JP+EN contract"


def pass_7_ttl_cache_logic() -> str:
    seal = load_json("LUM_FIREFOX_JP_VOICE_TTL_20260911.json")
    check(seal.get("assets", {}).get("drive_sync_ttl_seconds") == 21600, "Drive TTL drift")
    check(seal.get("assets", {}).get("generated_tts_ttl_seconds") == 604800, "TTS TTL drift")
    sync = load_text("termux/sync-voice-cache")
    tts = load_text("termux/hf-tts-cache.py")
    bg = load_text("background.js")
    check('LUHM_AUDIO_SYNC_TTL_SECONDS:-21600' in sync, "audio sync TTL missing")
    check('LUHM_TTS_TTL_SECONDS", "604800"' in tts, "TTS TTL missing")
    check("cache_expired" in bg and "expires_at" in bg, "runtime cache expiry enforcement missing")
    return "Drive/audio and generated-TTS TTLs enforced"


def pass_8_copyright_isolation() -> str:
    offenders = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if "dist" in path.parts or ".git" in path.parts:
            continue
        if path.suffix.lower() in FORBIDDEN_ASSET_EXTS:
            offenders.append(path.relative_to(ROOT).as_posix())
    check(not offenders, f"private/game asset bytes found in public shell tree: {offenders}")
    return "no third-party raster/audio/game binary assets in shell tree"


def pass_9_scope_prune() -> str:
    runtime = runtime_text() + "\n" + load_text("termux/luhm-private-bridge")
    for token in ("TERMINAL_URL", "LUHM_OPEN_TERMINAL", "ttyd", "127.0.0.1:7681", "Edge Gallery", "Ollama"):
        check(token not in runtime, f"out-of-scope runtime token remains: {token}")
    ai = load_json("AI_MANIFEST.json")
    check(ai.get("scope") == "private Firefox Android ChatGPT companion only", "AI manifest scope drift")
    return "Firefox companion scope isolated; terminal/OS inference lanes pruned"


def syntax_check() -> None:
    for rel in ("manifest.json", "voice/lum-voice-profile.json", "AI_MANIFEST.json", "LUM_FIREFOX_JP_VOICE_TTL_20260911.json"):
        load_json(rel)
    for path in (ROOT / "termux").glob("*.py"):
        subprocess.run([sys.executable, "-m", "py_compile", str(path)], check=True, stdout=subprocess.DEVNULL)
    bash = shutil.which("bash")
    if bash:
        for path in (ROOT / "termux").iterdir():
            if path.is_file() and path.suffix == "":
                subprocess.run([bash, "-n", str(path)], check=True, stdout=subprocess.DEVNULL)
    node = shutil.which("node")
    if node:
        for rel in ("background.js", "content.js", "popup.js"):
            subprocess.run([node, "--check", str(ROOT / rel)], check=True, stdout=subprocess.DEVNULL)


def package_xpi() -> tuple[Path, str]:
    DIST.mkdir(exist_ok=True)
    xpi = DIST / f"luhm-chatgpt-companion-firefox-{VERSION}-unsigned.xpi"
    if xpi.exists():
        xpi.unlink()
    timestamp = (2026, 9, 11, 0, 0, 0)
    with zipfile.ZipFile(xpi, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for rel in sorted(PACKAGE_FILES):
            path = ROOT / rel
            check(path.is_file(), f"package input missing: {rel}")
            info = zipfile.ZipInfo(rel, date_time=timestamp)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, path.read_bytes())
    digest = hashlib.sha256(xpi.read_bytes()).hexdigest()
    return xpi, digest


def pass_10_syntax_and_package() -> str:
    syntax_check()
    xpi, digest = package_xpi()
    with zipfile.ZipFile(xpi) as archive:
        names = set(archive.namelist())
    check("manifest.json" in names, "XPI missing manifest")
    check(not any(name.startswith("termux/") for name in names), "Termux helpers leaked into XPI")
    check(not any(Path(name).suffix.lower() in FORBIDDEN_ASSET_EXTS for name in names), "forbidden private asset leaked into XPI")
    (DIST / "SHA256SUMS.txt").write_text(f"{digest}  {xpi.name}\n", encoding="utf-8")
    return f"syntax green; deterministic XPI built sha256={digest}"


PASSES = [
    (1, "manifest_scope", pass_1_manifest_scope),
    (2, "permissions_hosts", pass_2_permissions_hosts),
    (3, "command_seal", pass_3_command_seal),
    (4, "no_auto_send", pass_4_no_auto_send),
    (5, "credentials_exfil", pass_5_credentials_and_exfil),
    (6, "voice_privacy", pass_6_voice_privacy_contract),
    (7, "ttl_cache", pass_7_ttl_cache_logic),
    (8, "copyright_isolation", pass_8_copyright_isolation),
    (9, "scope_prune", pass_9_scope_prune),
    (10, "syntax_package", pass_10_syntax_and_package),
]


def main() -> int:
    parser = argparse.ArgumentParser(description="LuHm Firefox Witching Hour forge")
    parser.add_argument("--audit-only", action="store_true", help="run ten passes but still validates package inputs")
    args = parser.parse_args()
    DIST.mkdir(exist_ok=True)
    results = []
    green = True
    for number, name, fn in PASSES:
        try:
            detail = fn()
            results.append({"pass": number, "name": name, "status": "PASS", "detail": detail})
            print(f"PASS {number:02d} {name}: {detail}")
        except Exception as exc:
            green = False
            results.append({"pass": number, "name": name, "status": "FAIL", "detail": str(exc)})
            print(f"FAIL {number:02d} {name}: {exc}", file=sys.stderr)
    report = {
        "seal": "LUM_FIREFOX_WITCHING_HOUR_10PASS_20260911",
        "version": VERSION,
        "status": "GREEN" if green else "FAIL",
        "passes": results,
        "forge": "stdlib-only; same entry point for local Samsung/Termux and GitHub Actions",
    }
    (DIST / "witching-hour-audit.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"WITCHING_HOUR_{report['status']}")
    return 0 if green else 1


if __name__ == "__main__":
    raise SystemExit(main())
