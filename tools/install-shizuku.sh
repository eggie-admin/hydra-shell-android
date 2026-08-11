#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

REPO="RikkaApps/Shizuku"
API="https://api.github.com/repos/${REPO}/releases/latest"
WORKDIR="${TMPDIR:-/data/data/com.termux/files/usr/tmp}/hydra-shizuku"
mkdir -p "$WORKDIR"

command -v curl >/dev/null || { echo "Missing curl: pkg install curl"; exit 1; }
command -v adb >/dev/null || { echo "Missing adb: pkg install android-tools"; exit 1; }
command -v python >/dev/null || { echo "Missing python: pkg install python"; exit 1; }

printf '⠋ Querying latest Shizuku release...\n'
release_json="$(curl -fsSL -H 'Accept: application/vnd.github+json' "$API")"

apk_url="$(printf '%s' "$release_json" | python -c '
import json,sys
r=json.load(sys.stdin)
assets=r.get("assets",[])
for a in assets:
    n=a.get("name","").lower()
    if n.endswith(".apk") and "shizuku" in n:
        print(a["browser_download_url"])
        break
else:
    raise SystemExit("No Shizuku APK asset found in latest release")
')"

apk_name="${apk_url##*/}"
apk_path="$WORKDIR/$apk_name"

printf '⠙ Downloading %s...\n' "$apk_name"
curl -fL --retry 3 -o "$apk_path" "$apk_url"

printf '⠹ Checking ADB target gate...\n'
adb_output="$(adb devices 2>&1)"
target_count="$(printf '%s\n' "$adb_output" | awk '
  /^List of devices attached/ {seen=1; next}
  seen && NF >= 2 && $1 !~ /^\*/ {n++}
  END {print n+0}
')"
authorized_count="$(printf '%s\n' "$adb_output" | awk '
  /^List of devices attached/ {seen=1; next}
  seen && $2 == "device" {n++}
  END {print n+0}
')"
serial="$(printf '%s\n' "$adb_output" | awk '
  /^List of devices attached/ {seen=1; next}
  seen && $2 == "device" {print $1; exit}
')"

if [ "$target_count" -ne 1 ] || [ "$authorized_count" -ne 1 ] || [ -z "$serial" ]; then
  printf 'Blocked: expected exactly one connected ADB target and it must be authorized.\n' >&2
  printf 'targets_total=%s authorized=%s\n' "$target_count" "$authorized_count" >&2
  exit 1
fi

printf '⠸ Installing through the single authorized ADB target...\n'
adb -s "$serial" install -r "$apk_path"

printf '\nShizuku installed. Open it and choose Start via wireless debugging.\n'
printf 'APK retained at: %s\n' "$apk_path"
