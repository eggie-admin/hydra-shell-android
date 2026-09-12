#!/usr/bin/env bash
set -euo pipefail

KEY_PATH="${KAI_SSH_KEY_PATH:-$HOME/.ssh/kai9000_fastapi_cloud_ed25519}"
COMMENT="${KAI_SSH_KEY_COMMENT:-kai9000-fastapi-cloud}"

mkdir -p "$(dirname "$KEY_PATH")"
chmod 700 "$(dirname "$KEY_PATH")"

if [[ -e "$KEY_PATH" ]]; then
  echo "Key already exists: $KEY_PATH"
else
  ssh-keygen -t ed25519 -a 100 -f "$KEY_PATH" -C "$COMMENT" -N ""
  chmod 600 "$KEY_PATH"
  chmod 644 "$KEY_PATH.pub"
fi

echo "Public key to install remotely:"
cat "$KEY_PATH.pub"
echo
echo "Private key stays local: $KEY_PATH"
