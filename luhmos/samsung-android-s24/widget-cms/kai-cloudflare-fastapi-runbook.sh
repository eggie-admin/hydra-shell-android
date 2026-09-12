#!/usr/bin/env bash
set -euo pipefail

echo "=== KAI Vue CMS Mutation :: local build ==="
uv sync
npm --prefix frontend install
npm --prefix frontend run build
uv run python -m pytest

echo
echo "=== FastAPI Cloud read-only probes ==="
uv run fastapi cloud deploy --help || true
uv run fastapi cloud whoami --json || true
uv run fastapi cloud apps get --json || true

echo
echo "Next deploy command, only after auth/link/secrets are good:"
echo "uv run fastapi cloud deploy . --json"
