#!/usr/bin/env python3
from __future__ import annotations

import json
import mimetypes
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

ROOT = Path(os.environ.get("LUHM_PRIVATE_ASSET_ROOT", "~/luhm-private/assets")).expanduser().resolve()
OUT = ROOT / "destiny-audio-index.json"

PLAYABLE_EXTS = {".wav", ".mp3", ".ogg", ".oga", ".opus", ".m4a", ".aac", ".flac", ".webm"}
GAME_AUDIO_EXTS = {".acb", ".awb", ".hca", ".wem", ".bnk", ".adx", ".at3", ".at9", ".xma"}
CONTAINER_EXTS = {".pck", ".pak", ".cpk", ".zip", ".7z", ".rar"}

TAG_PATTERNS = {
    "voice": r"voice|vo_|dialog|speech|talk|char|character",
    "battle": r"battle|combat|attack|skill|hit|damage|fight",
    "victory": r"victory|win|clear|result|success|fanfare",
    "summon": r"summon|gacha|pull|draw|recruit",
    "ui": r"ui|button|click|tap|menu|select|confirm",
    "date": r"date|love|affection|heart|romance",
    "ultima": r"ultima|special|ultimate|burst|limit",
    "bgm": r"bgm|music|theme|stage|lobby",
}


def run_probe(path: Path) -> dict:
    probe = shutil.which("ffprobe")
    if not probe:
        return {}
    try:
        proc = subprocess.run(
            [probe, "-v", "error", "-show_entries", "format=duration,format_name", "-of", "json", str(path)],
            capture_output=True,
            text=True,
            timeout=8,
            check=True,
        )
        data = json.loads(proc.stdout or "{}")
        fmt = data.get("format") or {}
        return {
            "duration_sec": round(float(fmt.get("duration", 0.0)), 3) if fmt.get("duration") else None,
            "format_name": fmt.get("format_name"),
        }
    except Exception:
        return {}


def vgmstream_available() -> bool:
    return bool(shutil.which("vgmstream-cli") or shutil.which("vgmstream"))


def classify(path: Path) -> tuple[str, bool]:
    ext = path.suffix.lower()
    if ext in PLAYABLE_EXTS:
        return "playable_audio", True
    if ext in GAME_AUDIO_EXTS:
        return "game_audio_container", False
    if ext in CONTAINER_EXTS:
        return "archive_or_package", False
    mime, _ = mimetypes.guess_type(path.name)
    if mime and mime.startswith("audio/"):
        return "playable_audio", True
    return "other", False


def tags_for(rel: str) -> list[str]:
    lower = rel.lower()
    tags = [name for name, pattern in TAG_PATTERNS.items() if re.search(pattern, lower)]
    return sorted(set(tags))


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    rows = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path == OUT:
            continue
        kind, directly_playable = classify(path)
        if kind == "other":
            continue
        rel = path.relative_to(ROOT).as_posix()
        row = {
            "path": rel,
            "bytes": path.stat().st_size,
            "mtime": int(path.stat().st_mtime),
            "extension": path.suffix.lower(),
            "kind": kind,
            "directly_playable": directly_playable,
            "tags": tags_for(rel),
        }
        if directly_playable:
            row.update({k: v for k, v in run_probe(path).items() if v is not None})
        rows.append(row)

    manifest = {
        "schema": "luhm.private-destiny-audio.v1",
        "generated_at": int(time.time()),
        "private_only": True,
        "redistribution": False,
        "root": str(ROOT),
        "ffprobe_available": bool(shutil.which("ffprobe")),
        "vgmstream_available": vgmstream_available(),
        "recognized_count": len(rows),
        "playable_count": sum(1 for row in rows if row["directly_playable"]),
        "game_audio_container_count": sum(1 for row in rows if row["kind"] == "game_audio_container"),
        "files": rows,
        "event_preferences": {
            "pet": ["ui", "voice"],
            "gacha": ["summon", "ui"],
            "legendary": ["victory", "summon"],
            "date": ["date", "voice"],
            "battle": ["battle"],
            "ultima": ["ultima", "battle", "victory"],
        },
        "note": "Private educational index only. Audio bytes stay in the user's local cache and are not committed to GitHub or bundled into the Firefox shell.",
    }
    OUT.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"indexed {len(rows)} recognized audio/package files -> {OUT}")


if __name__ == "__main__":
    main()
