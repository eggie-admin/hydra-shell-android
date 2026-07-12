#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

REPO="RikkaApps/Shizuku"
API="https://api.github.com/repos/${REPO}/releases/latest"
WORKDIR="${TMPDIR:-/data/data/com.termux/files/usr/tmp}/hydra-shizuku"
mkdir -p "$WORKDIR"

command -v curl >/dev/null || { echo "Missing curl: pkg install curl"; exit 1; }
command -v adb >/dev/null || { echo "Missing adb: pkg install android-tools"; exit 1; }

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

printf '⠹ Installing through ADB...\n'
adb devices
adb install -r "$apk_path"

printf '\nShizuku installed. Open it and choose Start via wireless debugging.\n'
printf 'APK retained at: %s\n' "$apk_path"
