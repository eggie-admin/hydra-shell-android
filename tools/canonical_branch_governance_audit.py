#!/usr/bin/env python3
"""Read-only audit of canonical branch governance on GitHub.

This tool never mutates repository settings. It verifies that the canonical
branch is protected at the GitHub server layer and reports repository rulesets
for operator review.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

DEFAULT_REPO = "eggie-admin/hydra-shell-android"
DEFAULT_BRANCH = "luhmos-main"
API_ROOT = "https://api.github.com"


def github_get(path: str) -> object:
    req = urllib.request.Request(
        f"{API_ROOT}{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "luhmos-canonical-governance-audit",
        },
    )
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=15) as response:
        return json.load(response)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--branch", default=DEFAULT_BRANCH)
    args = parser.parse_args()

    try:
        branch = github_get(f"/repos/{args.repo}/branches/{args.branch}")
        rulesets = github_get(f"/repos/{args.repo}/rulesets")
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"CANONICAL_GOVERNANCE_AUDIT=ERROR\nerror={exc}", file=sys.stderr)
        return 2

    protected = bool(branch.get("protected")) if isinstance(branch, dict) else False
    active_rulesets = []
    if isinstance(rulesets, list):
        active_rulesets = [
            item.get("name", "unnamed")
            for item in rulesets
            if isinstance(item, dict) and item.get("enforcement") == "active"
        ]

    print(f"repo={args.repo}")
    print(f"branch={args.branch}")
    print(f"branch_protected={str(protected).lower()}")
    print(f"active_rulesets={json.dumps(active_rulesets)}")

    if not protected:
        print("CANONICAL_BRANCH_SERVER_LOCK=RED", file=sys.stderr)
        print("required_action=enable branch protection or an applicable active ruleset", file=sys.stderr)
        return 1

    print("CANONICAL_BRANCH_SERVER_LOCK=GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
