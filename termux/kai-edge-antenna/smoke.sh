#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "=== KAI EDGE ANTENNA STATIC SMOKE ==="

python3 -m py_compile mini_ollama_antenna.py
python3 -m json.tool edge-gallery-profile.json >/dev/null
python3 -m json.tool KAI9000_EDGE_GALLERY_MINI_OLLAMA_ANTENNA_20260911.manifest.json >/dev/null
bash -n kai-edge-antenna

urls="$(grep -R -nE 'https?://' mini_ollama_antenna.py kai-edge-antenna 2>/dev/null || true)"
if printf '%s\n' "$urls" | grep -vE 'https?://(127\.0\.0\.1|localhost)(:|/|$)' | grep -q 'https\?\?*://' ; then
  echo "Unexpected non-loopback runtime URL detected" >&2
  printf '%s\n' "$urls" >&2
  exit 1
fi

if grep -R -nE 'requestSubmit\(|\.submit\(' . 2>/dev/null; then
  echo "Unexpected browser-style auto-submit token detected" >&2
  exit 1
fi

grep -q 'no_callable_local_backend' mini_ollama_antenna.py
grep -q 'secure_folder_is_client_not_daemon_owner' mini_ollama_antenna.py
grep -q 'preferred_model_ready_in_ui' edge-gallery-profile.json
grep -q 'secure_folder_profile_confirmed": false' edge-gallery-profile.json

echo "STATIC_SMOKE_GREEN"
