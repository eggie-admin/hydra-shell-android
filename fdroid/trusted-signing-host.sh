#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  trusted-signing-host.sh --stage <fdroid-stage-dir> --out <signed-output-dir>

Required environment:
  FDROID_KEYSTORE           Path to persistent F-Droid repository keystore
  FDROID_KEYSTORE_PASS      Keystore password
  FDROID_KEY_PASS           Repository key password
  APK_SIGNER_SHA256         Expected persistent LuHm OS APK certificate SHA-256

Optional environment:
  FDROID_REPO_KEYALIAS      Defaults to luhmos-fdroid-repo
  FDROID_CONFIG_TEMPLATE    Defaults to fdroid/config.template.yml
  APKSIGNER                 Defaults to apksigner from PATH

Security contract:
  - The APK must already carry the correct persistent release signature.
  - This script NEVER converts a debug/mismatched APK into a production APK.
  - Repository signing keys are used only to sign F-Droid index material.
  - Private keys/config.yml never enter the public output.
EOF
}

STAGE=""
OUT=""
while (($#)); do
  case "$1" in
    --stage) STAGE="${2:-}"; shift 2 ;;
    --out) OUT="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

: "${FDROID_KEYSTORE:?FDROID_KEYSTORE is required}"
: "${FDROID_KEYSTORE_PASS:?FDROID_KEYSTORE_PASS is required}"
: "${FDROID_KEY_PASS:?FDROID_KEY_PASS is required}"
: "${APK_SIGNER_SHA256:?APK_SIGNER_SHA256 is required}"
FDROID_REPO_KEYALIAS="${FDROID_REPO_KEYALIAS:-luhmos-fdroid-repo}"
FDROID_CONFIG_TEMPLATE="${FDROID_CONFIG_TEMPLATE:-fdroid/config.template.yml}"
APKSIGNER="${APKSIGNER:-$(command -v apksigner || true)}"

[[ -n "$STAGE" && -d "$STAGE" ]] || { echo "Missing --stage directory" >&2; exit 2; }
[[ -n "$OUT" ]] || { echo "Missing --out directory" >&2; exit 2; }
[[ -f "$FDROID_KEYSTORE" ]] || { echo "F-Droid keystore not found" >&2; exit 3; }
[[ -f "$FDROID_CONFIG_TEMPLATE" ]] || { echo "Config template not found" >&2; exit 3; }
[[ -n "$APKSIGNER" ]] || { echo "apksigner is required" >&2; exit 4; }
for cmd in fdroid keytool jarsigner python3 sha256sum find; do
  command -v "$cmd" >/dev/null || { echo "Required command missing: $cmd" >&2; exit 4; }
done

umask 077
WORK="$(mktemp -d "${TMPDIR:-/tmp}/luhmos-fdroid-sign.XXXXXX")"
cleanup() { rm -rf "$WORK"; }
trap cleanup EXIT INT TERM

cp -a "$STAGE/repo" "$WORK/repo"
cp -a "$STAGE/metadata" "$WORK/metadata"
cp "$FDROID_CONFIG_TEMPLATE" "$WORK/config.yml"

mapfile -t APKS < <(find "$WORK/repo" -maxdepth 1 -type f -name '*.apk' -print | sort)
(( ${#APKS[@]} > 0 )) || { echo "No staged APK found" >&2; exit 5; }

normalize_fp() { tr -d ':[:space:]' | tr '[:lower:]' '[:upper:]'; }
EXPECTED_APK_FP="$(printf '%s' "$APK_SIGNER_SHA256" | normalize_fp)"

for apk in "${APKS[@]}"; do
  "$APKSIGNER" verify --verbose --print-certs "$apk" > "$WORK/apksigner.txt"
  fp="$(sed -n 's/^Signer #1 certificate SHA-256 digest: //p' "$WORK/apksigner.txt" | head -n1 | normalize_fp)"
  [[ -n "$fp" && "$fp" == "$EXPECTED_APK_FP" ]] || {
    echo "REFUSING_APK_SIGNER_MISMATCH file=$(basename "$apk") actual=$fp expected=$EXPECTED_APK_FP" >&2
    exit 6
  }
  grep -Eq 'Verified using v(2|3|4) scheme .*: true' "$WORK/apksigner.txt" || {
    echo "APK has no accepted modern signature scheme: $(basename "$apk")" >&2
    exit 6
  }
  echo "APK_PERSISTENT_SIGNER_VERIFIED file=$(basename "$apk")"
done

keytool -list -keystore "$FDROID_KEYSTORE" \
  -storepass "$FDROID_KEYSTORE_PASS" \
  -alias "$FDROID_REPO_KEYALIAS" >/dev/null

(
  cd "$WORK"
  export FDROID_KEYSTORE FDROID_KEYSTORE_PASS FDROID_KEY_PASS
  fdroid update --verbose
)

test -s "$WORK/repo/index-v2.json"
test -s "$WORK/repo/index-v1.json"
test -s "$WORK/repo/index-v1.jar"
test -s "$WORK/repo/entry.jar"
jarsigner -verify "$WORK/repo/index-v1.jar" >/dev/null
jarsigner -verify "$WORK/repo/entry.jar" >/dev/null

REPO_FP="$(keytool -list -v -keystore "$FDROID_KEYSTORE" \
  -storepass "$FDROID_KEYSTORE_PASS" \
  -alias "$FDROID_REPO_KEYALIAS" \
  | sed -n 's/^[[:space:]]*SHA256: //p' \
  | head -n1 \
  | normalize_fp)"
[[ -n "$REPO_FP" ]] || { echo "Could not derive repository fingerprint" >&2; exit 7; }

rm -rf "$OUT"
mkdir -p "$OUT"
cp -a "$WORK/repo" "$OUT/repo"
printf '%s\n' "$REPO_FP" > "$OUT/repo/repo-fingerprint-sha256.txt"
printf '%s\n' "$EXPECTED_APK_FP" > "$OUT/repo/apk-signer-sha256.txt"

OUT_DIR="$OUT" REPO_FP="$REPO_FP" APK_FP="$EXPECTED_APK_FP" APK_COUNT="${#APKS[@]}" python3 - <<'PY'
import json, os
from pathlib import Path
out = Path(os.environ['OUT_DIR'])
status = {
    'schema': 'luhmos.fdroid-signed.v1',
    'repo_url': 'https://fdroid.eggiebagelface.art/fdroid/repo/',
    'public_bootstrap_mirror': 'https://raw.githubusercontent.com/eggie-admin/hydra-shell-android/fdroid-public/fdroid/repo/',
    'apk_count': int(os.environ['APK_COUNT']),
    'repo_fingerprint_sha256': os.environ['REPO_FP'],
    'apk_signer_sha256': os.environ['APK_FP'],
    'all_apks_persistent_identity_verified': True,
    'persistent_repo_identity_verified': True,
    'signed_repo': True,
    'published': False,
    'import_verified': False,
    'upgrade_verified': False,
    'state': 'FDROID_SIGNED',
    'next_gate': 'publish only repo/ over HTTPS, import using pinned fingerprint, install on SM-S721U1, then verify a same-signer versionCode upgrade',
}
(out / 'FINAL_FORM_SIGNED_STATUS.json').write_text(json.dumps(status, indent=2) + '\n', encoding='utf-8')
PY

! find "$OUT" -type f \( -name '*.jks' -o -name '*.keystore' -o -name 'config.yml' \) -print -quit | grep -q .
(
  cd "$OUT"
  find repo -type f -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS
)

echo "FDROID_SIGNED"
echo "Repository fingerprint SHA-256: $REPO_FP"
echo "Output: $OUT"
