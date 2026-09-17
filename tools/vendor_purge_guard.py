from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = bytes((118, 101, 114, 99, 101, 108)).decode("ascii")
SKIP_DIRS = {".git"}
SKIP_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".mp4", ".apk", ".zip", ".jar", ".aar", ".so", ".woff", ".woff2", ".ttf", ".otf"}

hits: list[str] = []
for path in ROOT.rglob("*"):
    if not path.is_file():
        continue
    if any(part in SKIP_DIRS for part in path.parts):
        continue
    if path.suffix.lower() in SKIP_SUFFIXES:
        continue
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        continue
    if FORBIDDEN.casefold() in text.casefold() or FORBIDDEN.casefold() in path.as_posix().casefold():
        hits.append(path.relative_to(ROOT).as_posix())

if hits:
    print("LUHM_VENDOR_PURGE_GUARD=RED")
    for hit in sorted(set(hits)):
        print(hit)
    raise SystemExit(1)

print("LUHM_VENDOR_PURGE_GUARD=GREEN")
