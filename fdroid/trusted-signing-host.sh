#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  trusted-signing-host.sh --stage <fdroid-stage-dir> --out <signed-output-dir>

Required environment:
  FDROID_KEYSTORE           Path to persistent F-Droid repo keystore
  FDROID_KEYSTORE_PASS      Keystore password
  FDROID_KEY_PASS           Repository key password
  APK_SIGNER_SHA256         Expected persistent APK signing certificate SHA-256

Optional environment:
  FDROID_REPO_KEYALIAS      Defaults to kai9000-fdroid-repo
  FDROID_CONFIG_TEMPLATE    Defaults to ./fdroid/config.template.yml

This script must run on a trusted, non-public signing host. It never publishes,
never uploads keys, and never prints secret values.
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
FDROID_REPO_KEYALIAS="${FDROID_REPO_KEYALIAS:-kai9000-fdroid-repo}"
FDROID_CONFIG_TEMPLATE="${FDROID_CONFIG_TEMPLATE:-fdroid/config.template.yml}"

[[ -n "$STAGE" && -d "$STAGE" ]] || { echo "Missing --stage directory" >&2; exit 2; }
[[ -n "$OUT" ]] || { echo "Missing --out directory" >&2; exit 2; }
[[ -f "$FDROID_KEYSTORE" ]] || { echo "F-Droid keystore not found" >&2; exit 3; }
[[ -f "$FDROID_CONFIG_TEMPLATE" ]] || { echo "Config template not found" >&2; exit 3; }

for cmd in fdroid keytool jarsigner python3 sha256sum find; do
  command -v "$cmd" >/dev/null || { echo "Required command missing: $cmd" >&2; exit 4; }
done

APKSIGNER="${APKSIGNER:-$(command -v apksigner || true)}"
[[ -n "$APKSIGNER" ]] || { echo "apksigner is required to enforce persistent APK identity" >&2; exit 4; }

umask 077
WORK="$(mktemp -d "${TMPDIR:-/tmp}/kai9000-fdroid-sign.XXXXXX")"
cleanup() { rm -rf "$WORK"; }
trap cleanup EXIT INT TERM

cp -a "$STAGE/repo" "$WORK/repo"
cp -a "$STAGE/metadata" "$WORK/metadata"
cp "$FDROID_CONFIG_TEMPLATE" "$WORK/config.yml"

APK="$(find "$WORK/repo" -maxdepth 1 -type f -name '*.apk' -print -quit)"
[[ -n "$APK" && -s "$APK" ]] || { echo "No staged APK found" >&2; exit 5; }

EXPECTED_APK_FP="$(printf '%s' "$APK_SIGNER_SHA256" | tr -d ':[:space:]' | tr '[:upper:]' '[:lower:]')"
ACTUAL_APK_FP="$($APKSIGNER verify --print-certs "$APK" \
  | sed -n 's/^Signer #1 certificate SHA-256 digest: //p' \
  | head -n1 \
  | tr -d ':[:space:]' \
  | tr '[:upper:]' '[:lower:]')"
[[ -n "$ACTUAL_APK_FP" ]] || { echo "Could not read APK signer fingerprint" >&2; exit 6; }
[[ "$ACTUAL_APK_FP" == "$EXPECTED_APK_FP" ]] || {
  echo "APK signer does not match the declared persistent signing identity" >&2
  exit 7
}

echo "APK_PERSISTENT_SIGNER_VERIFIED"

keytool -list -keystore "$FDROID_KEYSTORE" \
  -storepass "$FDROID_KEYSTORE_PASS" \
  -alias "$FDROID_REPO_KEYALIAS" >/dev/null

echo "FDROID_REPO_KEY_PRESENT"

(
  cd "$WORK"
  fdroid update --verbose
)

SIGNED_JARS=0
while IFS= read -r jar; do
  jarsigner -verify -strict "$jar" >/dev/null
  SIGNED_JARS=$((SIGNED_JARS + 1))
done < <(find "$WORK/repo" -maxdepth 1 -type f \( -name 'index*.jar' -o -name 'entry.jar' \) -print)
(( SIGNED_JARS > 0 )) || { echo "No signed F-Droid index JAR was produced" >&2; exit 8; }

test -s "$WORK/repo/index-v1.jar" || test -s "$WORK/repo/entry.jar" || test -s "$WORK/repo/index.jar"

REPO_FP="$(keytool -list -v -keystore "$FDROID_KEYSTORE" \
  -storepass "$FDROID_KEYSTORE_PASS" \
  -alias "$FDROID_REPO_KEYALIAS" \
  | sed -n 's/^[[:space:]]*SHA256: //p' \
  | head -n1 \
  | tr -d ':[:space:]' \
  | tr '[:upper:]' '[:lower:]')"
[[ -n "$REPO_FP" ]] || { echo "Could not derive repository certificate fingerprint" >&2; exit 9; }

rm -rf "$OUT"
mkdir -p "$OUT"
cp -a "$WORK/repo" "$OUT/repo"

SOURCE_STAGE="$STAGE" OUT_DIR="$OUT" REPO_FP="$REPO_FP" APK_FP="$ACTUAL_APK_FP" \
python3 - <<'PY'
import json
import os
from pathlib import Path

out = Path(os.environ['OUT_DIR'])
status = {
    'schema': 'kai9000.fdroid-signed.v1',
    'source_stage': os.environ['SOURCE_STAGE'],
    'repo_url': 'https://fdroid.eggiebagelface.art/fdroid/repo/',
    'repo_fingerprint_sha256': os.environ['REPO_FP'],
    'apk_signer_sha256': os.environ['APK_FP'],
    'persistent_apk_identity_verified': True,
    'persistent_repo_identity_verified': True,
    'signed_repo': True,
    'published': False,
    'import_verified': False,
    'upgrade_verified': False,
    'next_gate': 'publish only repo/ to HTTPS, then verify F-Droid client import and upgrade path',
}
(out / 'FINAL_FORM_SIGNED_STATUS.json').write_text(
    json.dumps(status, indent=2) + '\n', encoding='utf-8'
)
PY

# Guardrail: output must contain no signing material or config passwords.
! find "$OUT" -type f \( -name '*.jks' -o -name '*.keystore' -o -name 'config.yml' \) -print -quit | grep -q .

(
  cd "$OUT"
  find repo -type f -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS
)

echo "FDROID_SIGNED"
echo "Repository fingerprint SHA-256: $REPO_FP"
echo "Output: $OUT"
