#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import os
import time

ROOT = Path(os.environ.get("LUHM_PRIVATE_ASSET_ROOT", "~/luhm-private/assets")).expanduser().resolve()
SRC = ROOT / "live2d"
OUT = ROOT / "live2d-runtime-index.json"

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
MOTION_EXTS = {".mtn"}


def relpath(path: Path, base: Path) -> str:
    return path.relative_to(base).as_posix()


def usable_existing_contract(directory: Path) -> Path | None:
    for candidate in sorted(directory.glob("*.json")):
        try:
            data = json.loads(candidate.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(data, dict) and isinstance(data.get("model"), str) and isinstance(data.get("textures"), list):
            return candidate
    return None


def build_contract(directory: Path, moc: Path) -> Path:
    existing = usable_existing_contract(directory)
    if existing:
        return existing

    textures = sorted(p for p in directory.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_EXTS)
    motions = sorted(p for p in directory.rglob("*") if p.is_file() and p.suffix.lower() in MOTION_EXTS)
    physics = next((p for p in directory.rglob("*.json") if "physics" in p.name.lower()), None)
    pose = next((p for p in directory.rglob("*.json") if "pose" in p.name.lower()), None)

    payload: dict[str, object] = {
        "name": directory.name,
        "model": relpath(moc, directory),
        "textures": [relpath(p, directory) for p in textures],
        "layout": {"center_x": 0, "y": 1, "width": 2},
    }
    if motions:
        payload["motions"] = {
            "idle": [{"file": relpath(p, directory), "fade_in": 700, "fade_out": 700} for p in motions]
        }
    if physics:
        payload["physics"] = relpath(physics, directory)
    if pose:
        payload["pose"] = relpath(pose, directory)

    out = directory / "luhm.model.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


models = []
if SRC.exists():
    for moc in sorted(SRC.rglob("*.moc")):
        directory = moc.parent
        contract = build_contract(directory, moc)
        motions = sorted(directory.rglob("*.mtn"))
        textures = sorted(p for p in directory.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_EXTS)
        root_rel = directory.relative_to(SRC).as_posix()
        entry_rel = contract.relative_to(ROOT).as_posix()
        models.append({
            "id": root_rel.replace("/", "__"),
            "label": root_rel,
            "runtime_family": "cubism2",
            "entry_path": entry_rel,
            "model_file": moc.name,
            "texture_count": len(textures),
            "motion_count": len(motions),
            "private_only": True,
        })

payload = {
    "schema": "luhm.private-live2d-runtime.v1",
    "generated_at": int(time.time()),
    "private_only": True,
    "redistribution": False,
    "runtime_family": "cubism2",
    "model_count": len(models),
    "default_index": 0,
    "models": models,
}
OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Live2D runtime index: {len(models)} models -> {OUT}")
for item in models:
    print(f"  {item['label']} textures={item['texture_count']} motions={item['motion_count']} entry={item['entry_path']}")
