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
DEMO = ROOT / "luhmos/demo/index.html"
MANIFEST = ROOT / "luhmos/demo/demo.manifest.json"

class AuditError(RuntimeError):
    pass

def need(cond, msg):
    if not cond:
        raise AuditError(msg)

def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def embedded_manifest(html):
    match = re.search(r'<script id="demo-manifest" type="application/json">\s*(\{.*?\})\s*</script>', html, re.S)
    need(match is not None, "embedded demo manifest missing")
    return json.loads(match.group(1))

def audit():
    crown = load_json(CROWN)
    manifest = load_json(MANIFEST)
    campaign = load_json(CAMPAIGN)
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
    need(embedded_manifest(html) == manifest, "embedded manifest differs from canonical demo manifest")
    need("https://" not in html.lower() and "http://" not in html.lower(), "demo contains an external URL")
    forbidden = "ulti" + "ma"
    need(forbidden not in html.lower(), "legacy convergence term surfaced in new demo")
    need(manifest["demo_contract"]["no_real_tool_execution"] is True, "demo tool boundary missing")
    need(manifest["evidence"]["android_green"] == "PENDING_DEVICE_VALIDATION", "demo falsely claims Android GREEN")

    print("DEMO_SOURCE_AUDIT_GREEN")
    return crown, manifest, campaign

def build(out):
    crown, manifest, campaign = audit()
    out.mkdir(parents=True, exist_ok=True)
    shutil.copy2(DEMO, out / "index.html")
    shutil.copy2(MANIFEST, out / "demo.manifest.json")
    receipt = {
        "schema": "luhm-os.demo-build-receipt.v1",
        "demo_id": manifest["id"],
        "git_sha": os.getenv("GITHUB_SHA", "LOCAL"),
        "source_crown_id": crown["id"],
        "campaign_canon_id": campaign["id"],
        "source_sha256": {
            "crown": sha(CROWN),
            "coding_roleplay": sha(CODING),
            "questforge_roleplay": sha(QUEST),
            "campaign": sha(CAMPAIGN),
            "manifest": sha(MANIFEST),
            "html": sha(DEMO)
        },
        "artifact_sha256": {}
    }
    receipt["artifact_sha256"]["index.html"] = sha(out / "index.html")
    receipt["artifact_sha256"]["demo.manifest.json"] = sha(out / "demo.manifest.json")
    (out / "build-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print("DEMO_COMPILE_GREEN")

def verify(out):
    audit()
    receipt = load_json(out / "build-receipt.json")
    need(receipt["artifact_sha256"]["index.html"] == sha(out / "index.html"), "built HTML hash mismatch")
    need(receipt["artifact_sha256"]["demo.manifest.json"] == sha(out / "demo.manifest.json"), "built manifest hash mismatch")
    need((out / "index.html").read_bytes() == DEMO.read_bytes(), "built HTML differs from source")
    print("DEMO_ARTIFACT_VERIFY_GREEN")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["audit", "build", "verify"])
    parser.add_argument("--out", default="dist/luhm-os-demo")
    args = parser.parse_args()
    out = ROOT / args.out
    try:
        {"audit": lambda: audit(), "build": lambda: build(out), "verify": lambda: verify(out)}[args.mode]()
    except AuditError as exc:
        raise SystemExit(f"DEMO_AUDIT_RED: {exc}")

if __name__ == "__main__":
    main()
