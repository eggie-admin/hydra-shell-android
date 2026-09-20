#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CROWN = ROOT / "docs/CROWN_SOURCE_OF_TRUTH_20260919.json"
CODING = ROOT / "lumh-os/kai9000/CODING_ROLEPLAY_DOCTRINE.md"
QUEST = ROOT / "docs/QUESTFORGE_ROLEPLAY_DOCTRINE.md"
CAMPAIGN = ROOT / "docs/QUESTFORGE_IRON_SAINT_CANON_20260919.json"
LUM_REF = ROOT / "project/hydra/samsung/android/apk/lum-mona-outfit.reference.json"
DEMO_DIR = ROOT / "luhmos/demo"
DEMO = DEMO_DIR / "index.html"
STYLE = DEMO_DIR / "style.css"
APP = DEMO_DIR / "app.js"
ASSET_DATA = DEMO_DIR / "asset-data.js"
MANIFEST = DEMO_DIR / "demo.manifest.json"
ASSET_REGISTRY = DEMO_DIR / "asset.registry.json"
MODEL_EXTS = {".glb", ".gltf", ".vrm", ".obj", ".fbx", ".blend"}
SOURCE_FILES = [DEMO, STYLE, APP, ASSET_DATA, MANIFEST, ASSET_REGISTRY]

class AuditError(RuntimeError):
    pass

def need(cond, msg):
    if not cond:
        raise AuditError(msg)

def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def embedded_json(html, element_id):
    pattern = rf'<script id="{re.escape(element_id)}" type="application/json">\s*(\{{.*?\}})\s*</script>'
    match = re.search(pattern, html, re.S)
    need(match is not None, f"embedded {element_id} missing")
    return json.loads(match.group(1))

def asset_data_json(text):
    match = re.match(r'^\s*window\.LUHM_ASSET_REGISTRY\s*=\s*(\{.*\});\s*$', text, re.S)
    need(match is not None, "asset-data.js does not contain the canonical registry payload")
    return json.loads(match.group(1))

def repo_model_binaries():
    found = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if ".git" in rel.parts or "dist" in rel.parts:
            continue
        if path.suffix.lower() in MODEL_EXTS:
            found.append(rel.as_posix())
    return sorted(found)

def audit():
    crown = load_json(CROWN)
    manifest = load_json(MANIFEST)
    assets = load_json(ASSET_REGISTRY)
    campaign = load_json(CAMPAIGN)
    lum_ref = load_json(LUM_REF)
    coding = CODING.read_text(encoding="utf-8")
    quest = QUEST.read_text(encoding="utf-8")
    html = DEMO.read_text(encoding="utf-8")

    need(crown["status"] == "CROWNED", "crown is not CROWNED")
    need(crown["authority"]["human_final_authority"] == "Professor", "Professor authority mismatch")
    need(crown["authority"]["boss_ai"] == "Lum", "Lum boss mismatch")
    need(crown["agent_mesh"]["version"] == "LUHM Agent Mesh v1", "agent mesh mismatch")
    need(crown["agent_mesh"]["max_parallelism"] == 3, "parallelism mismatch")
    need(crown["roleplay_systems"]["hard_separation"] is True, "roleplay separation not hard")
    need(crown["roleplay_systems"]["coding_roleplay"]["system"] == "ENGINEERING_DSL", "coding roleplay mismatch")
    need(crown["roleplay_systems"]["questforge"]["system"] == "FICTIONAL_TABLETOP", "Questforge mode mismatch")
    need(crown["roleplay_systems"]["questforge"]["engineering_authority"] is False, "Questforge gained engineering authority")
    need(crown["repository"]["active_development_branch"] == "testing/luhm-os-android", "active branch mismatch")
    need(crown["repository"]["vercel_active_architecture"] is False, "Vercel unexpectedly active")
    need(crown["runtime_truth"]["recheck_live"] is True, "runtime recheck contract missing")
    need("engineering roleplay only" in coding.lower(), "coding doctrine boundary missing")
    need("engineering_authority = none" in quest.lower(), "Questforge no-authority boundary missing")
    need(campaign["id"] == manifest["questforge"]["canon_id"], "campaign canon mismatch")

    source = manifest["source_of_truth"]
    need(source["crown_id"] == crown["id"], "demo crown id mismatch")
    need(source["human_final_authority"] == crown["authority"]["human_final_authority"], "demo authority mismatch")
    need(source["boss_ai"] == crown["authority"]["boss_ai"], "demo boss mismatch")
    need(source["agent_mesh_version"] == crown["agent_mesh"]["version"], "demo mesh mismatch")
    need(source["max_parallelism"] == crown["agent_mesh"]["max_parallelism"], "demo parallelism mismatch")
    need(source["coding_roleplay_system"] == crown["roleplay_systems"]["coding_roleplay"]["system"], "demo coding roleplay mismatch")
    need(source["questforge_system"] == crown["roleplay_systems"]["questforge"]["system"], "demo Questforge mismatch")
    need(source["roleplay_hard_separation"] == crown["roleplay_systems"]["hard_separation"], "demo roleplay wall mismatch")
    need(source["device"]["model"] == crown["kai9000"]["device"]["model"], "demo device mismatch")

    need(manifest["assets"]["registry_id"] == assets["id"], "asset registry id mismatch")
    need(manifest["assets"]["public_forge_bundle_count"] == len(assets["public"]), "public bundle count mismatch")
    need(manifest["assets"]["private_original_art_index_count"] == len(assets["private_art"]["entries"]), "private art index count mismatch")
    need(manifest["assets"]["three_d_source_registry_count"] == assets["three_d"]["source_registry_count"] == len(assets["three_d"]["sources"]), "3D source registry count mismatch")
    need(manifest["assets"]["rights_wall_enforced"] is True, "demo rights wall missing")
    need(assets["rights"]["third_party_private_reference_public_redistribution"] is False, "private reference redistribution enabled")
    need(assets["rights"]["community_license_receipt_required"] is True, "community license gate missing")

    for item in assets["public"]:
        src = ROOT / item["path"]
        demo_copy = DEMO_DIR / "assets" / src.name
        need(item["bundle"] is True and item["public_safe"] is True, f"unsafe public bundle declaration: {item['path']}")
        need(src.is_file(), f"public source asset missing: {item['path']}")
        need(demo_copy.is_file(), f"demo public asset missing: {demo_copy.relative_to(ROOT)}")
        need(sha(src) == item["sha256"], f"public source asset hash mismatch: {item['path']}")
        need(sha(demo_copy) == item["sha256"], f"demo public asset hash mismatch: {demo_copy.relative_to(ROOT)}")

    need(assets["private_art"]["binary_status"] == "NOT_IN_PUBLIC_GIT", "private art public Git boundary drift")
    need(assets["private_art"]["mount"] == "LOCAL_FILE_PICKER_ONLY", "private art local mount boundary drift")
    need(manifest["assets"]["private_art_binary_status"] == "LOCAL_ONLY_NOT_IN_PUBLIC_GIT", "demo private-art status mismatch")
    need(manifest["demo_contract"]["private_assets_never_auto_uploaded"] is True, "private asset upload boundary missing")
    need(assets["forge"]["private_drive_fetch"] is False and assets["forge"]["private_publish"] is False, "forge private-asset boundary drift")

    lum = assets["lum_reference"]
    need(lum["repo"] == "project/hydra/samsung/android/apk/lum-mona-outfit.reference.json", "Lum reference path mismatch")
    need(lum["sha256"] == lum_ref["integrity"]["sha256"], "Lum reference hash mismatch")
    need(lum["drive_file_id"] == lum_ref["drive_reference"]["file_id"], "Lum Drive reference mismatch")
    need(lum["bundle_mode"] == lum_ref["integration"]["bundle_mode"] == "reference_not_copy", "Lum reference bundling policy drift")

    campaign_ids = [x["generation_id"] for x in campaign["canonical_visuals"]]
    need(assets["questforge"]["generation_ids"] == campaign_ids, "Questforge visual generation ids drifted")
    need(len(campaign_ids) == manifest["questforge"]["visual_reference_count"], "Questforge visual count mismatch")
    need(assets["questforge"]["repo_binary_status"] == "NOT_STORED", "Questforge binary persistence falsely claimed")
    need(manifest["questforge"]["visual_binaries_in_repo"] is False, "demo falsely claims Questforge binaries in repo")

    models = repo_model_binaries()
    need(len(models) == assets["three_d"]["repo_binary_count"] == manifest["assets"]["repo_model_binary_count"], f"3D binary inventory drift: {models}")
    if not models:
        need(assets["three_d"]["runtime"] == "NOT_CLAIMED", "3D source registry falsely claims runtime")
        need(manifest["assets"]["three_d_runtime_status"] == "REGISTRY_ONLY_NO_APPROVED_BINARY_IN_GIT", "demo falsely claims 3D runtime")
    need(all(x.get("name") and x.get("license") and x.get("role") for x in assets["three_d"]["sources"]), "3D registry missing provenance fields")

    need(embedded_json(html, "demo-manifest") == manifest, "embedded manifest differs from canonical demo manifest")
    need(asset_data_json(ASSET_DATA.read_text(encoding="utf-8")) == assets, "asset-data.js differs from canonical asset registry")
    for path in SOURCE_FILES:
        text = path.read_text(encoding="utf-8")
        need("https://" not in text.lower() and "http://" not in text.lower(), f"demo source contains an external URL: {path.name}")
        need(re.search(r"\bULTIMA\b", text, re.I) is None, f"legacy convergence token surfaced in new demo source: {path.name}")
    need(manifest["demo_contract"]["no_real_tool_execution"] is True, "demo tool boundary missing")
    need(manifest["evidence"]["android_green"] == "PENDING_DEVICE_VALIDATION", "demo falsely claims Android GREEN")

    print("DEMO_SOURCE_AUDIT_GREEN")
    print("DEMO_ASSET_RIGHTS_AUDIT_GREEN")
    print(f"PUBLIC_ASSETS_VERIFIED={len(assets['public'])}")
    print(f"PRIVATE_ART_INDEXED={len(assets['private_art']['entries'])}")
    print(f"QUESTFORGE_VISUAL_REFS={len(campaign_ids)}")
    print(f"THREED_SOURCE_MATCHES={len(assets['three_d']['sources'])}")
    print(f"THREED_REPO_BINARIES={len(models)}")
    return crown, manifest, assets, campaign

def build(out):
    crown, manifest, assets, campaign = audit()
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    for src in [DEMO, STYLE, APP, ASSET_DATA, MANIFEST, ASSET_REGISTRY]:
        shutil.copy2(src, out / src.name)
    bundle_dir = out / "assets"
    bundle_dir.mkdir()
    for item in assets["public"]:
        src = DEMO_DIR / "assets" / Path(item["path"]).name
        shutil.copy2(src, bundle_dir / src.name)

    artifact_files = ["index.html", "style.css", "app.js", "asset-data.js", "demo.manifest.json", "asset.registry.json"]
    artifact_files += [f"assets/{Path(x['path']).name}" for x in assets["public"]]
    receipt = {
        "schema": "luhm-os.demo-build-receipt.v2",
        "demo_id": manifest["id"],
        "asset_registry_id": assets["id"],
        "git_sha": os.getenv("GITHUB_SHA", "LOCAL"),
        "source_crown_id": crown["id"],
        "campaign_canon_id": campaign["id"],
        "asset_truth": {
            "public_assets_bundled": len(assets["public"]),
            "private_art_indexed_not_bundled": len(assets["private_art"]["entries"]),
            "questforge_visual_references_not_bundled": len(assets["questforge"]["generation_ids"]),
            "three_d_source_matches": len(assets["three_d"]["sources"]),
            "three_d_repo_binaries": assets["three_d"]["repo_binary_count"],
            "three_d_runtime_claimed": False
        },
        "source_sha256": {p.name: sha(p) for p in [CROWN, CODING, QUEST, CAMPAIGN, LUM_REF, MANIFEST, ASSET_REGISTRY, DEMO, STYLE, APP, ASSET_DATA]},
        "artifact_sha256": {}
    }
    for rel in artifact_files:
        receipt["artifact_sha256"][rel] = sha(out / rel)
    (out / "build-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print("DEMO_COMPILE_GREEN")

def verify(out):
    _, _, assets, _ = audit()
    receipt = load_json(out / "build-receipt.json")
    for rel, expected in receipt["artifact_sha256"].items():
        need((out / rel).is_file(), f"artifact file missing: {rel}")
        need(sha(out / rel) == expected, f"artifact hash mismatch: {rel}")
    need((out / "index.html").read_bytes() == DEMO.read_bytes(), "built HTML differs from source")
    for item in assets["public"]:
        rel = f"assets/{Path(item['path']).name}"
        need(sha(out / rel) == item["sha256"], f"bundled public asset mismatch: {rel}")
    print("DEMO_ARTIFACT_VERIFY_GREEN")
    print("DEMO_PUBLIC_ASSET_BUNDLE_GREEN")
    print("DEMO_PRIVATE_ASSET_POLICY_GREEN")
    print("DEMO_3D_RUNTIME_PENDING_NO_BINARY")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["audit", "build", "verify"])
    parser.add_argument("--out", default="dist/luhm-os-demo")
    args = parser.parse_args()
    out = ROOT / args.out
    try:
        {"audit": audit, "build": lambda: build(out), "verify": lambda: verify(out)}[args.mode]()
    except AuditError as exc:
        raise SystemExit(f"DEMO_AUDIT_RED: {exc}")

if __name__ == "__main__":
    main()
