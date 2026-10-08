#!/usr/bin/env python3
from pathlib import Path
import json, os, time

ROOT = Path(os.environ.get("LUHM_PRIVATE_ASSET_ROOT", "~/luhm-private/assets")).expanduser().resolve()
OUT = ROOT / "luhm-manifest.json"

ADULT_MARKERS = ("topless", "nude", "nsfw", "18+", "adult", "uncensor")

def kind_for(path: Path) -> str:
    s = path.suffix.lower()
    n = path.name.lower()
    if s in {".moc", ".moc3"}: return "live2d_model"
    if "motion" in n or s in {".mtn"}: return "motion"
    if s in {".png", ".jpg", ".jpeg", ".webp", ".gif"}: return "image"
    if s in {".wav", ".ogg", ".mp3", ".m4a"}: return "audio"
    if s == ".pck": return "package"
    if s in {".json", ".txt", ".dat"}: return "data"
    if s in {".zip", ".7z", ".rar"}: return "archive"
    return "other"

files = []
if ROOT.exists():
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path == OUT:
            continue
        rel = path.relative_to(ROOT).as_posix()
        lower = rel.lower()
        files.append({
            "path": rel,
            "bytes": path.stat().st_size,
            "mtime": int(path.stat().st_mtime),
            "kind": kind_for(path),
            "adult_flag": any(marker in lower for marker in ADULT_MARKERS)
        })

packs = sorted({f["path"].split("/", 1)[0] for f in files if "/" in f["path"]})
manifest = {
    "title": "LuHm Private Asset Cache",
    "generated_at": int(time.time()),
    "root": str(ROOT),
    "private_only": True,
    "redistribution": False,
    "note": "Private educational/runtime index. Third-party assets remain local and are not committed to GitHub or bundled into the signed Firefox shell.",
    "packs": packs,
    "files": files
}
ROOT.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(f"indexed {len(files)} files across {len(packs)} packs -> {OUT}")
