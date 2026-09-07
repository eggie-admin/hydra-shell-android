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

To replace an ephemeral/debug APK signature with the persistent APK identity, also set:
  APK_KEYSTORE              Path to persistent Android APK keystore
  APK_KEYSTORE_PASS         APK keystore password
  APK_KEY_ALIAS             APK signing key alias
  APK_KEY_PASS              APK key password

Optional environment:
  FDROID_REPO_KEYALIAS      Defaults to kai9000-fdroid-repo
  FDROID_CONFIG_TEMPLATE    Defaults to ./fdroid/config.template.yml
  APKSIGNER                 apksigner path, defaults to PATH
  ZIPALIGN                  zipalign path, defaults to PATH

Run only on the trusted non-public signing host. No private key, password, or
keystore is copied to the output, Git, logs, or publication host.
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
ZIPALIGN="${ZIPALIGN:-$(command -v zipalign || true)}"
[[ -n "$APKSIGNER" ]] || { echo "apksigner is required" >&2; exit 4; }

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
read_apk_fp() {
  "$APKSIGNER" verify --print-certs "$1" \
    | sed -n 's/^Signer #1 certificate SHA-256 digest: //p' \
    | head -n1 \
    | tr -d ':[:space:]' \
    | tr '[:upper:]' '[:lower:]'
}

ACTUAL_APK_FP="$(read_apk_fp "$APK")"

if [[ "$ACTUAL_APK_FP" != "$EXPECTED_APK_FP" ]]; then
  # A GitHub/debug build is allowed as INPUT only when the persistent APK key is
  # available locally so the signature can be replaced before F-Droid signing.
  : "${APK_KEYSTORE:?APK signer mismatch: set APK_KEYSTORE for trusted re-signing}"
  : "${APK_KEYSTORE_PASS:?APK_KEYSTORE_PASS is required for trusted re-signing}"
  : "${APK_KEY_ALIAS:?APK_KEY_ALIAS is required for trusted re-signing}"
  : "${APK_KEY_PASS:?APK_KEY_PASS is required for trusted re-signing}"
  [[ -f "$APK_KEYSTORE" ]] || { echo "APK keystore not found" >&2; exit 6; }
  [[ -n "$ZIPALIGN" ]] || { echo "zipalign is required before trusted APK signing" >&2; exit 6; }

  ALIGNED="$WORK/aligned.apk"
  SIGNED="$WORK/persistent-signed.apk"
  "$ZIPALIGN" -f -p 4 "$APK" "$ALIGNED"
  "$APKSIGNER" sign \
    --ks "$APK_KEYSTORE" \
    --ks-key-alias "$APK_KEY_ALIAS" \
    --ks-pass env:APK_KEYSTORE_PASS \
    --key-pass env:APK_KEY_PASS \
    --out "$SIGNED" \
    "$ALIGNED"
  "$APKSIGNER" verify --verbose --print-certs "$SIGNED" >/dev/null
  mv "$SIGNED" "$APK"
  ACTUAL_APK_FP="$(read_apk_fp "$APK")"
  echo "APK_PERSISTENT_SIGNING_APPLIED"
fi

[[ -n "$ACTUAL_APK_FP" ]] || { echo "Could not read APK signer fingerprint" >&2; exit 7; }
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
  # A custom F-Droid repository normally uses a self-signed repo certificate.
  # Cryptographic JAR verification must pass; public-WebPKI trust is not required.
  jarsigner -verify "$jar" >/dev/null
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

INDEX_JSON="$WORK/repo/index-v1.json"
SOURCE_STAGE="$STAGE" OUT_DIR="$OUT" REPO_FP="$REPO_FP" APK_FP="$ACTUAL_APK_FP" INDEX_JSON="$INDEX_JSON" \
python3 - <<'PY'
import json
import os
from pathlib import Path

index = json.loads(Path(os.environ['INDEX_JSON']).read_text(encoding='utf-8'))
packages = index.get('packages', {})
all_versions = [p for versions in packages.values() for p in versions]
latest = max(all_versions, key=lambda p: int(p.get('versionCode', 0))) if all_versions else {}
out = Path(os.environ['OUT_DIR'])
status = {
    'schema': 'kai9000.fdroid-signed.v2',
    'source_stage': os.environ['SOURCE_STAGE'],
    'repo_url': 'https://fdroid.eggiebagelface.art/fdroid/repo/',
    'version_code': int(latest.get('versionCode', 0)),
    'version': latest.get('versionName'),
    'repo_fingerprint_sha256': os.environ['REPO_FP'].upper(),
    'apk_signer_sha256': os.environ['APK_FP'].upper(),
    'persistent_apk_identity_verified': True,
    'persistent_repo_identity_verified': True,
    'signed_repo': True,
    'published': False,
    'import_verified': False,
    'upgrade_verified': False,
    'state': 'FDROID_SIGNED',
    'next_gate': 'publish repo/ to HTTPS, import with pinned fingerprint, then verify Android accepts the next versionCode as an upgrade',
}
(out / 'FINAL_FORM_SIGNED_STATUS.json').write_text(
    json.dumps(status, indent=2) + '\n', encoding='utf-8'
)
PY

# Output is public material only.
! find "$OUT" -type f \( -name '*.jks' -o -name '*.keystore' -o -name 'config.yml' \) -print -quit | grep -q .
(
  cd "$OUT"
  find repo -type f -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS
)

echo "FDROID_SIGNED"
echo "Repository fingerprint SHA-256: $REPO_FP"
echo "Output: $OUT"
