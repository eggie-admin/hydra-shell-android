from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ACTIVE_FILES = [
    ROOT / "README.md",
    ROOT / "SUPPORT.md",
    ROOT / "ARCHITECTURE.md",
    ROOT / ".github" / "copilot-instructions.md",
    ROOT / "docs" / "LUHM_OS_KAI9000_OVERVIEW.md",
    ROOT / "docs" / "HYDRA_PROFESSOR_GREEN_FULL_GREEN.md",
]
ACTIVE_DIRS = [
    ROOT / "backend",
    ROOT / "tools",
    ROOT / "integrations" / "cloudflare",
]

EDITOR_PATTERNS = [
    re.compile(r"aco" + r"dex", re.I),
    re.compile(r"\baxs\b", re.I),
    re.compile(r"876" + r"7"),
]
HOST_PATTERNS = [
    re.compile(r"ver" + r"cel\.app", re.I),
    re.compile(r"@ver" + r"cel\b", re.I),
    re.compile(r"\bnpx\s+ver" + r"cel\b", re.I),
    re.compile(r"\bver" + r"cel\s+deploy\b", re.I),
    re.compile(r"\bVER" + r"CEL_(?:TOKEN|ORG_ID|PROJECT_ID)\b"),
    re.compile(r"(?:^|/)ver" + r"cel\.json$", re.I),
]

TEXT_SUFFIXES = {
    ".md",
    ".py",
    ".sh",
    ".html",
    ".js",
    ".css",
    ".json",
    ".yml",
    ".yaml",
    ".toml",
    ".txt",
}


def iter_active_files() -> list[Path]:
    files = [p for p in ACTIVE_FILES if p.is_file()]
    for directory in ACTIVE_DIRS:
        if not directory.is_dir():
            continue
        for path in directory.rglob("*"):
            if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
                files.append(path)
    return sorted(set(files))


def main() -> int:
    failures: list[str] = []
    self_path = Path(__file__).resolve()

    for path in iter_active_files():
        if path.resolve() == self_path:
            continue
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")

        for pattern in EDITOR_PATTERNS:
            if pattern.search(text):
                failures.append(f"retired_editor_bridge:{rel}:{pattern.pattern}")

        for pattern in HOST_PATTERNS:
            if pattern.search(text) or pattern.search(rel):
                failures.append(f"retired_external_host:{rel}:{pattern.pattern}")

    if failures:
        print("RETIRED_LANE_GUARD=RED")
        for failure in failures:
            print(failure)
        return 1

    print("RETIRED_LANE_GUARD=GREEN")
    print("ACTIVE_EDITOR_BRIDGE_DEPENDENCY=ABSENT")
    print("ACTIONABLE_EXTERNAL_HOST_DEPENDENCY=ABSENT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
