#!/usr/bin/env bash
set -euo pipefail
umask 077

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
V6_BUNDLE="${KAI_V6_SIGNED_BUNDLE:-$HOME/storage/downloads/KAI9000_FDROID_SIGNED_20260906.zip}"
V7_STAGE_ZIP="${KAI_V7_STAGE_BUNDLE:-$HOME/storage/downloads/KAI9000_UPGRADE_V7_STAGED_20260906.zip}"
OUT_ZIP="${KAI_V7_SIGNED_BUNDLE:-$HOME/storage/downloads/KAI9000_FDROID_SIGNED_V7_20260906.zip}"
V6_SHA="fa350eeb2a2945b3b0e664f459ae1706cd3c19d0c02913e799e7ea005c6f3028"
V7_STAGE_SHA="5ce52890a4ea3357815990e54bd44eb5b241b346de11eaaa910afa322e80ebdc"
APK_FP="A5E9364D5C21A119FE1D17FD39EE7BAE8192A872CE58A3E7A865248E0B070407"
REPO_FP="BFB900A9EC913D35C22F1DC3DE7B152D1AF5CA11B7B07E5FAFDD06B44811F66D"
PACKAGE="art.eggiebagelface.videoforge.dev"

usage() {
  cat <<EOF
usage: $0 [--v6 PATH] [--v7-stage PATH] [--out PATH]

This script never contains signing secrets. Before running, unlock/mount the
persistent APK and F-Droid keystores locally and export the variables required
by fdroid/trusted-signing-host.sh.
EOF
}
while (($#)); do
  case "$1" in
    --v6) V6_BUNDLE="${2:-}"; shift 2 ;;
    --v7-stage) V7_STAGE_ZIP="${2:-}"; shift 2 ;;
    --out) OUT_ZIP="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

for cmd in sha256sum unzip zip python3; do
  command -v "$cmd" >/dev/null || { echo "RED: missing command: $cmd" >&2; exit 3; }
done
[ -s "$V6_BUNDLE" ] || { echo "RED: missing v6 signed bundle: $V6_BUNDLE" >&2; exit 3; }
[ -s "$V7_STAGE_ZIP" ] || { echo "RED: missing v7 staging bundle: $V7_STAGE_ZIP" >&2; exit 3; }

echo "$V6_SHA  $V6_BUNDLE" | sha256sum -c --strict
echo "$V7_STAGE_SHA  $V7_STAGE_ZIP" | sha256sum -c --strict
echo 'UPGRADE_INPUT_BUNDLES_GREEN'

WORK="$(mktemp -d "${TMPDIR:-/tmp}/kai9000-upgrade-sign.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT INT TERM
mkdir -p "$WORK/v6" "$WORK/v7" "$WORK/stage/repo" "$WORK/stage/metadata" "$WORK/signed"
unzip -q "$V6_BUNDLE" -d "$WORK/v6"
unzip -q "$V7_STAGE_ZIP" -d "$WORK/v7"

python3 - "$WORK/v6/FINAL_FORM_SIGNED_STATUS.json" "$APK_FP" "$REPO_FP" <<'PY'
import json, sys
p, apk, repo = sys.argv[1:]
s=json.load(open(p, encoding='utf-8'))
assert s.get('state') == 'FDROID_SIGNED'
assert s.get('apk_signer_sha256','').upper() == apk
assert s.get('repo_fingerprint_sha256','').upper() == repo
print('V6_LIFETIME_TRUST_GREEN')
PY

V6_APK="$(find "$WORK/v6/repo" -maxdepth 1 -type f -name "${PACKAGE}_6.apk" -print -quit)"
V7_APK="$(find "$WORK/v7/fdroid-v7-stage/repo" -maxdepth 1 -type f -name "${PACKAGE}_7.apk" -print -quit)"
[ -s "$V6_APK" ] || { echo 'RED: v6 APK absent' >&2; exit 4; }
[ -s "$V7_APK" ] || { echo 'RED: v7 APK absent' >&2; exit 4; }
cp "$V6_APK" "$WORK/stage/repo/"
cp "$V7_APK" "$WORK/stage/repo/"
cp "$WORK/v7/fdroid-v7-stage/metadata/${PACKAGE}.yml" "$WORK/stage/metadata/"

echo 'V6_V7_COMBINED_STAGE_GREEN'
APK_SIGNER_SHA256="$APK_FP" \
  bash "$ROOT/fdroid/trusted-signing-host.sh" --stage "$WORK/stage" --out "$WORK/signed"

python3 - "$WORK/signed/FINAL_FORM_SIGNED_STATUS.json" "$APK_FP" "$REPO_FP" <<'PY'
import json, sys
p, apk, repo = sys.argv[1:]
s=json.load(open(p, encoding='utf-8'))
assert s.get('state') == 'FDROID_SIGNED'
assert s.get('version_code') == 7
assert s.get('apk_count', 0) >= 2
assert s.get('apk_signer_sha256','').upper() == apk
assert s.get('repo_fingerprint_sha256','').upper() == repo
assert s.get('all_apks_persistent_identity_verified') is True
print('V6_TO_V7_SIGNED_REPOSITORY_GREEN')
PY

test -s "$WORK/signed/repo/${PACKAGE}_6.apk"
test -s "$WORK/signed/repo/${PACKAGE}_7.apk"
mkdir -p "$(dirname "$OUT_ZIP")"
rm -f "$OUT_ZIP"
(cd "$WORK/signed" && zip -q -r "$OUT_ZIP" .)
OUT_SHA="$(sha256sum "$OUT_ZIP" | awk '{print $1}')"

echo 'FDROID_V7_SIGNED'
echo "signed_bundle=$OUT_ZIP"
echo "signed_bundle_sha256=$OUT_SHA"
echo "apk_signer_sha256=$APK_FP"
echo "repo_fingerprint_sha256=$REPO_FP"
echo
printf 'Next publication cast:\nKAI_SIGNED_BUNDLE=%q KAI_EXPECTED_BUNDLE_SHA256=%q bash %q\n' \
  "$OUT_ZIP" "$OUT_SHA" "$ROOT/scripts/cast-ultima-live.sh"
