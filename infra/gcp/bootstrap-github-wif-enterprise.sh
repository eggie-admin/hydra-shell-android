#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ACCOUNT_ID="${GCP_SERVICE_ACCOUNT_ID:-}"

if [[ -z "$SERVICE_ACCOUNT_ID" ]]; then
  echo 'GCP_SERVICE_ACCOUNT_ID is required for the LuHm OS enterprise bootstrap.' >&2
  echo 'Use a dedicated identity such as luhmos-ci-deploy; no default service account will be selected.' >&2
  exit 2
fi

if [[ ! "$SERVICE_ACCOUNT_ID" =~ ^luhmos-[a-z0-9-]+$ ]]; then
  echo 'GCP_SERVICE_ACCOUNT_ID must begin with luhmos- and contain only lowercase letters, digits, or hyphens.' >&2
  exit 2
fi

if [[ "$SERVICE_ACCOUNT_ID" == "luhmos-admin" || "$SERVICE_ACCOUNT_ID" == "luhmos-owner" ]]; then
  echo 'Refusing an administrative service-account identity for a deployment pipeline.' >&2
  exit 2
fi

export GCP_SERVICE_ACCOUNT_ID="$SERVICE_ACCOUNT_ID"
export LUHMOS_RELEASE_REF="${LUHMOS_RELEASE_REF:-refs/heads/luhmos-main}"

echo 'LUHMOS_ENTERPRISE_WIF_PREFLIGHT_GREEN'
exec "$SCRIPT_DIR/bootstrap-github-wif.sh"
