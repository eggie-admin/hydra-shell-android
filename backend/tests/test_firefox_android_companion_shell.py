from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SHELL = ROOT / "samsung-sm-x400" / "frontend" / "widget" / "firefox-android-companion"


def _read(path: str) -> str:
    return (SHELL / path).read_text(encoding="utf-8")


def test_manifest_is_mv3_and_localhost_scoped() -> None:
    manifest = json.loads(_read("manifest.json"))
    assert manifest["manifest_version"] == 3
    assert manifest["permissions"] == ["storage"]
    assert set(manifest["host_permissions"]) == {
        "http://127.0.0.1/*",
        "https://chatgpt.com/*",
        "https://chat.openai.com/*",
    }
    assert set(manifest["content_scripts"][0]["matches"]) == {
        "https://chatgpt.com/*",
        "https://chat.openai.com/*",
    }


def test_runtime_manifest_keeps_fail_closed_contract() -> None:
    runtime_manifest = json.loads(_read("companion-shell.manifest.json"))
    assert runtime_manifest["runtimeBoundary"]["localhostOnly"] is True
    assert runtime_manifest["runtimeBoundary"]["allowedHost"] == "127.0.0.1"
    assert runtime_manifest["terminalLauncher"]["allowShellExecution"] is False
    assert runtime_manifest["ux"] == {
        "touchFriendlyControls": True,
        "failClosedDomHandling": True,
        "manualSendOnly": True,
    }


def test_background_disallows_remote_and_exec_patterns() -> None:
    background = _read("background.js")
    assert "ALLOWED_ASSET_PREFIXES = [\"/data/\", \"/images/\"]" in background
    assert "bridge-origin-not-allowed" in background
    assert "terminal-url-not-allowed" in background
    forbidden = (
        "eval(",
        "Function(",
        "nativeMessaging",
        "document.cookie",
        "browser.cookies",
    )
    for token in forbidden:
        assert token not in background


def test_content_script_is_manual_send_and_fail_closed() -> None:
    content = _read("content-script.js")
    assert "composer-not-found" in content
    assert "setPromptOnly" in content
    forbidden = (
        ".submit(",
        "KeyboardEvent",
        "Enter",
        "document.cookie",
        "localStorage",
        "sessionStorage",
    )
    for token in forbidden:
        assert token not in content


def test_styles_are_touch_friendly() -> None:
    css = _read("styles.css")
    assert "position: fixed;" in css
    assert "min-height: 44px;" in css
