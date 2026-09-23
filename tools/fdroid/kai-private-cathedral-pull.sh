#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
umask 077

REPO="${LUHM_GITHUB_REPO:-eggie-admin/hydra-shell-android}"
ROOT="${LUHM_FDROID_PRIVATE_ROOT:-$HOME/luhmos-private-fdroid}"
PORT="${LUHM_FDROID_PORT:-8796}"
mkdir -p "$ROOT/download" "$ROOT/live"

need() { command -v "$1" >/dev/null 2>&1 || { echo "Missing $1" >&2; exit 1; }; }
need gh
need unzip
need python

gh auth status >/dev/null 2>&1 || {
  echo "GitHub CLI is not authenticated. Run: gh auth login" >&2
  exit 1
}

latest_tag="$({ gh api "repos/$REPO/releases?per_page=100" --jq '[.[] | select(.draft == true) | select(.name | startswith("LuHm Cathedral Private"))] | sort_by(.created_at) | last | .tag_name'; } 2>/dev/null)"
if [[ -z "$latest_tag" || "$latest_tag" == "null" ]]; then
  echo "No private Cathedral draft release found." >&2
  exit 1
fi

echo "Pulling $latest_tag"
rm -rf "$ROOT/download"/* "$ROOT/live"/*
gh release download "$latest_tag" --repo "$REPO" --pattern 'LUHMOS_CATHEDRAL_PRIVATE_FDROID_*.zip' --dir "$ROOT/download"
zip_path="$(find "$ROOT/download" -maxdepth 1 -type f -name 'LUHMOS_CATHEDRAL_PRIVATE_FDROID_*.zip' -print -quit)"
test -n "$zip_path"
unzip -q "$zip_path" -d "$ROOT/live"
test -s "$ROOT/live/fdroid/repo/index-v1.jar"
test -s "$ROOT/live/fdroid/repo/index-v2.json"

cat <<MSG
PRIVATE CATHEDRAL REPO READY
Tag: $latest_tag
Path: $ROOT/live/fdroid/repo
F-Droid custom repo URL: http://127.0.0.1:$PORT/fdroid/repo

To serve now:
  python -m http.server $PORT --bind 127.0.0.1 --directory "$ROOT/live"
MSG
