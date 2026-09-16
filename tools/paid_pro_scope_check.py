#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SCOPE = json.loads((ROOT / "admin/paid-pro/project-scope.json").read_text())
SERVICES = json.loads((ROOT / "admin/paid-pro/service-registry.json").read_text())

errors: list[str] = []

if SCOPE.get("project_id") != "luhmos-paid-pro-samsung-android":
    errors.append("project_id drift")
if SCOPE.get("working_branch") != "luhmos/dev/samsung-android-paid-pro":
    errors.append("working_branch drift")
if SCOPE.get("release_anchor_branch") != "luhmos-main":
    errors.append("release anchor drift")
if SCOPE.get("platform_scope") != ["samsung-android"]:
    errors.append("platform scope must remain samsung-android only")
if not SCOPE.get("paid_pro_policy", {}).get("this_is_the_only_paid_pro_working_project"):
    errors.append("paid-pro exclusivity flag is not set")
if SCOPE.get("paid_pro_policy", {}).get("monthly_budget_usd") != 80.0:
    errors.append("monthly budget must remain USD 80 unless policy is explicitly changed")
if not SCOPE.get("security", {}).get("secrets_in_repo") is False:
    errors.append("secrets_in_repo must be false")

service_ids = {s.get("service_id") for s in SERVICES.get("services", [])}
required = {
    "openai-boss-lum",
    "google-drive",
    "gmail",
    "google-cloud-api",
    "cloudflare-edge",
    "sentry",
    "github-copilot",
    "github-actions-forge",
}
missing = sorted(required - service_ids)
if missing:
    errors.append("missing required service registrations: " + ", ".join(missing))

for service in SERVICES.get("services", []):
    ref = str(service.get("credential_ref", ""))
    if not ref:
        errors.append(f"{service.get('service_id')}: missing credential_ref")
    if any(marker in ref.lower() for marker in ("sk-", "password=", "token=", "secret=")):
        errors.append(f"{service.get('service_id')}: credential_ref appears to contain a raw secret")
    if service.get("authority") != "none":
        errors.append(f"{service.get('service_id')}: paid service must not carry authority")

if errors:
    print("PAID_PRO_SCOPE_RED")
    for error in errors:
        print("-", error)
    sys.exit(1)

print("PAID_PRO_SCOPE_GREEN")
print("project=luhmos-paid-pro-samsung-android")
print("working_branch=luhmos/dev/samsung-android-paid-pro")
print("release_anchor=luhmos-main")
print("platform=samsung-android")
print("monthly_budget_usd=80")
print("services=" + str(len(SERVICES.get("services", []))))
