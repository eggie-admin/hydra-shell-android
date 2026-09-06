#!/usr/bin/env python3
"""Inventory Cloudflare API token metadata without exposing credential values.

Cloudflare token secrets are shown only when created/rolled and are not returned by
list endpoints. This tool intentionally whitelists metadata fields and never prints
the bearer token used to authenticate the request.
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
SAFE_TOKEN_FIELDS = (
    "id",
    "name",
    "status",
    "issued_on",
    "modified_on",
    "last_used_on",
    "expires_on",
    "not_before",
)


def api_get(bearer: str, path: str) -> dict[str, Any]:
    req = urllib.request.Request(
        f"{API}{path}",
        headers={
            "Authorization": f"Bearer {bearer}",
            "Accept": "application/json",
            "User-Agent": "KAI9000-LuHmOS/cloudflare-token-inventory",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        payload = json.load(response)
    if not payload.get("success"):
        raise RuntimeError(f"Cloudflare API read failed: {payload.get('errors', [])}")
    return payload


def safe_policy(policy: Any) -> Any:
    if not isinstance(policy, dict):
        return None
    groups = []
    for group in policy.get("permission_groups") or []:
        if isinstance(group, dict):
            groups.append({k: group.get(k) for k in ("id", "name") if group.get(k) is not None})
    out: dict[str, Any] = {
        "effect": policy.get("effect"),
        "permission_groups": groups,
    }
    resources = policy.get("resources")
    if isinstance(resources, dict):
        out["resources"] = resources
    return out


def sanitize_token(item: Any) -> dict[str, Any]:
    if not isinstance(item, dict):
        return {}
    out = {key: item.get(key) for key in SAFE_TOKEN_FIELDS if item.get(key) is not None}
    policies = [safe_policy(p) for p in item.get("policies") or []]
    out["policies"] = [p for p in policies if p is not None]
    condition = item.get("condition")
    if isinstance(condition, dict):
        out["condition"] = condition
    return out


def list_all(bearer: str, base_path: str, include_expired: bool) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    page = 1
    while True:
        query = urllib.parse.urlencode(
            {"page": page, "per_page": 50, "include_expired": str(include_expired).lower()}
        )
        payload = api_get(bearer, f"{base_path}?{query}")
        rows.extend(sanitize_token(item) for item in payload.get("result") or [])
        info = payload.get("result_info") or {}
        total_pages = int(info.get("total_pages") or 1)
        if page >= total_pages:
            break
        page += 1
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", choices=("user", "account", "both"), default="both")
    parser.add_argument("--account-id", default=os.environ.get("CF_ACCOUNT_ID", ""))
    parser.add_argument("--include-expired", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args()

    bearer = os.environ.get("CF_TOKEN_AUDITOR") or os.environ.get("CF_API_TOKEN")
    if not bearer:
        print("CF_TOKEN_AUDITOR (preferred) or CF_API_TOKEN is required", file=sys.stderr)
        return 2

    report: dict[str, Any] = {
        "schema": "kai9000.cloudflare-token-inventory.v1",
        "secrets_included": False,
        "warning": "Cloudflare token secret values are not retrievable; this report contains metadata only.",
    }

    if args.scope in ("user", "both"):
        report["user_tokens"] = list_all(bearer, "/user/tokens", args.include_expired)

    if args.scope in ("account", "both"):
        if args.account_id:
            report["account_tokens"] = list_all(
                bearer, f"/accounts/{args.account_id}/tokens", args.include_expired
            )
        elif args.scope == "account":
            print("--account-id or CF_ACCOUNT_ID is required for account token inventory", file=sys.stderr)
            return 2
        else:
            report["account_tokens"] = []
            report["account_inventory_note"] = "Skipped because CF_ACCOUNT_ID was not supplied."

    encoded = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(encoded + "\n")
        print(f"TOKEN_METADATA_INVENTORY_WRITTEN={args.output}")
    else:
        print(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
