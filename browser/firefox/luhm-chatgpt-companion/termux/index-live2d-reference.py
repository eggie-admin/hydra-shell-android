#!/usr/bin/env python3
from pathlib import Path
import json, os, time

ROOT = Path(os.environ.get("LUHM_PRIVATE_ASSET_ROOT", "~/luhm-private/assets")).expanduser().resolve()
SRC = ROOT / "live2d"
OUT = ROOT / "live2d-reference-index.json"
KEYWORDS = tuple(x.strip().lower() for x in os.environ.get(
    "LUHM_LIVE2D_PREFERRED_KEYWORDS",
    "topless,nude,nsfw,uncensor,adult,busty,oppai,special,skin"
).split(",") if x.strip())

def is_model(p: Path) -> bool:
    n = p.name.lower()
    return p.suffix.lower() in {".moc", ".moc3"} or n == "model.json" or n.endswith(".model3.json")

def kind(p: Path) -> str:
    n, s = p.name.lower(), p.suffix.lower()
    if s in {".moc", ".moc3"}: return "model"
    if "motion" in n or s == ".mtn": return "motion"
    if "physics" in n: return "physics"
    if "pose" in n: return "pose"
    if "expression" in n or "exp" in n: return "expression"
    if s in {".png", ".jpg", ".jpeg", ".webp"}: return "texture"
    if s in {".json", ".txt", ".dat"}: return "config"
    return "other"

models = []
if SRC.exists():
    roots = sorted({p.parent for p in SRC.rglob("*") if p.is_file() and is_model(p)})
    for directory in roots:
        rel = directory.relative_to(SRC).as_posix()
        low = rel.lower()
        files = []
        for p in sorted(directory.rglob("*")):
            if p.is_file():
                files.append({"path": p.relative_to(SRC).as_posix(), "kind": kind(p), "bytes": p.stat().st_size})
        modern = any(f["path"].lower().endswith((".moc3", ".model3.json")) for f in files)
        tags = [k for k in KEYWORDS if k in low]
        models.append({
            "id": rel.replace("/", "__"),
            "root": rel,
            "runtime_family": "cubism3plus" if modern else "legacy",
            "preferred_reference": bool(tags),
            "reference_tags": tags,
            "private_only": True,
            "files": files,
        })

models.sort(key=lambda x: (not x["preferred_reference"], x["root"].lower()))
payload = {
    "schema": "luhm.private-live2d-reference.v1",
    "generated_at": int(time.time()),
    "private_only": True,
    "redistribution": False,
    "adult_reference_policy": "Private reference lane. Use only adult-design references.",
    "model_count": len(models),
    "preferred_count": sum(1 for m in models if m["preferred_reference"]),
    "models": models,
}
OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
print(f"Live2D index: {payload['model_count']} models / {payload['preferred_count']} preferred -> {OUT}")
