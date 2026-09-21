#!/usr/bin/env python3
"""Read-only guard for the LuHm Cathedral toy GUI mutation."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "project/hydra/samsung/android/cathedral-game"
FINAL = GAME / "final-form.css"
APK = GAME / "apk-install-gui.css"


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise SystemExit(f"TOY_GUI_GUARD_RED missing {label}: {needle}")


def reject(text: str, needle: str, label: str) -> None:
    if needle.lower() in text.lower():
        raise SystemExit(f"TOY_GUI_GUARD_RED forbidden {label}: {needle}")


def main() -> None:
    final = FINAL.read_text(encoding="utf-8")
    apk = APK.read_text(encoding="utf-8")

    require(final, "KAI9000_TOY_GUI_MUTATION_V1", "toy marker")
    require(final, '.controls button[data-a="explore"]:before', "existing action selector")
    require(final, '.controls button[data-a="save"]:before', "save action selector")
    require(final, "#luhmPetBubble", "draggable pet selector")
    require(final, "width:86px", "mobile pet size")
    require(final, "@media(prefers-reduced-motion:reduce)", "reduced-motion support")

    require(apk, "KAI9000_TOY_GUI_MUTATION_V1", "APK toy marker")
    require(apk, ".luhm-apk-dock", "APK dock selector")
    require(apk, "position:relative", "mobile document-flow dock")
    require(apk, "HUMAN GATE", "human-gate label")

    combined = final + "\n" + apk
    for needle, label in (
        ("http://", "remote HTTP asset"),
        ("https://", "remote HTTPS asset"),
        ("javascript:", "javascript URL"),
        ("eval(", "eval"),
        ("child_process", "shell bridge"),
        ("os.execute", "OS execute bridge"),
        ("com.termux", "retired Termux capability"),
    ):
        reject(combined, needle, label)

    print("LUHMOS_TOY_GUI_GUARD_GREEN")
    print("GUI_MUTATION=VISUAL_ONLY")
    print("NETWORK_ASSETS=ABSENT")
    print("SHELL_BRIDGE=ABSENT")
    print("INSTALL_AUTHORITY=UNCHANGED")


if __name__ == "__main__":
    main()
