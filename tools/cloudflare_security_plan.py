#!/usr/bin/env python3
"""KAI 9000 Cloudflare Edge Access Perimeter planner/applicator.

Dry-run is the default. This tool intentionally applies only low-ambiguity zone
security settings. Tunnel creation, Access policies, DNS records, registrar DS
publication, and HSTS remain separate reviewed operations.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from typing import Any

API = "https://api.cloudflare.com/client/v4"

ZONE_SETTINGS = [
    ("ssl", "strict"),
    ("always_use_https", "on"),
    ("min_tls_version", "1.2"),
    ("tls_1_3", "on"),
]


def plan(zone: str) -> dict[str, Any]:
    return {
        "schema": "kai9000.cloudflare-security-plan.v1",
        "zone": zone,
        "zone_settings": [
            {"setting": name, "value": value} for name, value in ZONE_SETTINGS
        ],
        "dnssec": {
            "desired": "active",
            "apply_separately": True,
            "registrar_ds_required": True,
        },
        "manual_review_lanes": [
            "Cloudflare Tunnel creation and connector credential delivery",
            "Access application/policy identity and device-posture values",
            "DNS records pointing public hostnames to the chosen tunnel",
            "Let's Encrypt DNS-01 origin certificate",
            "HSTS after HTTPS stability is proven",
        ],
        "forbidden": [
            "Global API Key",
            "printing credentials",
            "public WAN port forwarding to LAN",
            "publishing private .lan names in public DNS",
        ],
    }


def api_call(token: str, method: str, path: str, body: Any | None = None) -> dict[str, Any]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        f"{API}{path}",
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "KAI9000-LuHmOS/cloudflare-security",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    if not payload.get("success"):
        raise RuntimeError(f"Cloudflare API operation failed: {payload.get('errors', [])}")
    return payload


def resolve_zone_id(token: str, zone: str) -> str:
    query = urllib.parse.urlencode({"name": zone, "status": "active"})
    payload = api_call(token, "GET", f"/zones?{query}")
    results = payload.get("result", [])
    if len(results) != 1:
        raise RuntimeError(f"Expected exactly one active Cloudflare zone for {zone!r}; found {len(results)}")
    return str(results[0]["id"])


def apply_zone_baseline(token: str, zone_id: str) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    for setting, value in ZONE_SETTINGS:
        result = api_call(token, "PATCH", f"/zones/{zone_id}/settings/{setting}", {"value": value})
        item = result.get("result", {})
        evidence.append({"setting": setting, "value": item.get("value", value), "ok": True})
    return evidence


def enable_dnssec(token: str, zone_id: str) -> dict[str, Any]:
    payload = api_call(token, "PATCH", f"/zones/{zone_id}/dnssec", {"status": "active"})
    result = payload.get("result", {})
    return {
        "status": result.get("status"),
        "algorithm": result.get("algorithm"),
        "digest_type": result.get("digest_type"),
        "ds": result.get("ds"),
        "note": "Publish/verify the returned DS at the registrar before claiming DNSSEC GREEN.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--zone", default="eggiebagelface.art")
    parser.add_argument("--apply-zone-baseline", action="store_true")
    parser.add_argument("--enable-dnssec", action="store_true")
    args = parser.parse_args()

    output: dict[str, Any] = {"plan": plan(args.zone), "mode": "dry_run"}
    if not args.apply_zone_baseline and not args.enable_dnssec:
        print(json.dumps(output, indent=2))
        return 0

    token = os.environ.get("CF_API_TOKEN")
    if not token:
        print("CF_API_TOKEN is required for an apply operation", file=sys.stderr)
        return 2

    zone_id = resolve_zone_id(token, args.zone)
    output["mode"] = "apply"
    output["zone_id"] = zone_id
    if args.apply_zone_baseline:
        output["zone_settings_evidence"] = apply_zone_baseline(token, zone_id)
    if args.enable_dnssec:
        output["dnssec_evidence"] = enable_dnssec(token, zone_id)

    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
