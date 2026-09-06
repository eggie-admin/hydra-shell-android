#!/usr/bin/env bash
set -euo pipefail

# Publishes the already-signed KAI 9000 F-Droid bundle to a trusted HTTPS origin.
# This script never handles signing keys. It only accepts the immutable signed bundle.
#
# Usage:
#   scripts/publish_fdroid_origin.sh \
#     --bundle KAI9000_FDROID_SIGNED_20260906.zip \
#     --target kaiadmin@[2001:db8::1] \
#     --remote-root /srv/kai9000/fdroid
#
# Optional environment:
#   FDROID_PUBLIC_URL=https://fdroid.eggiebagelface.art/fdroid/repo/
#   EXPECTED_BUNDLE_SHA256=fa350eeb2a2945b3b0e664f459ae1706cd3c19d0c02913e799e7ea005c6f3028

BUNDLE=""
TARGET=""
REMOTE_ROOT="/srv/kai9000/fdroid"
PUBLIC_URL="${FDROID_PUBLIC_URL:-https://fdroid.eggiebagelface.art/fdroid/repo/}"
EXPECTED_BUNDLE_SHA256="${EXPECTED_BUNDLE_SHA256:-fa350eeb2a2945b3b0e664f459ae1706cd3c19d0c02913e799e7ea005c6f3028}"
EXPECTED_APK_SIGNER="A5E9364D5C21A119FE1D17FD39EE7BAE8192A872CE58A3E7A865248E0B070407"
EXPECTED_REPO_FP="BFB900A9EC913D35C22F1DC3DE7B152D1AF5CA11B7B07E5FAFDD06B44811F66D"

while (($#)); do
  case "$1" in
    --bundle) BUNDLE="${2:-}"; shift 2 ;;
    --target) TARGET="${2:-}"; shift 2 ;;
    --remote-root) REMOTE_ROOT="${2:-}"; shift 2 ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done

[[ -n "$BUNDLE" && -f "$BUNDLE" ]] || { echo "Missing --bundle" >&2; exit 2; }
[[ -n "$TARGET" ]] || { echo "Missing --target" >&2; exit 2; }
for cmd in sha256sum unzip python3 rsync ssh curl; do
  command -v "$cmd" >/dev/null || { echo "Missing command: $cmd" >&2; exit 3; }
done

ACTUAL_BUNDLE_SHA="$(sha256sum "$BUNDLE" | awk '{print $1}')"
[[ "$ACTUAL_BUNDLE_SHA" == "$EXPECTED_BUNDLE_SHA256" ]] || {
  echo "Signed bundle SHA-256 mismatch" >&2
  exit 4
}

echo "SIGNED_BUNDLE_SHA256_GREEN"

WORK="$(mktemp -d "${TMPDIR:-/tmp}/kai9000-publish.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT INT TERM
unzip -q "$BUNDLE" -d "$WORK"

test -s "$WORK/FINAL_FORM_SIGNED_STATUS.json"
test -d "$WORK/repo"
python3 - "$WORK/FINAL_FORM_SIGNED_STATUS.json" "$EXPECTED_APK_SIGNER" "$EXPECTED_REPO_FP" <<'PY'
import json, sys
status = json.load(open(sys.argv[1], encoding='utf-8'))
assert status.get('fdroid_signed') is True
assert status.get('state') == 'FDROID_SIGNED'
assert status.get('apk_signer_sha256','').upper() == sys.argv[2]
assert status.get('repo_fingerprint_sha256','').upper() == sys.argv[3]
assert status.get('published') is False
print('FDROID_SIGNED_INPUT_GREEN')
PY

test -s "$WORK/repo/index-v1.jar"
test -s "$WORK/repo/index-v1.json"
test -s "$WORK/repo/repo-fingerprint-sha256.txt"
grep -qi "$EXPECTED_REPO_FP" "$WORK/repo/repo-fingerprint-sha256.txt"
APK="$(find "$WORK/repo" -maxdepth 1 -type f -name '*.apk' -print -quit)"
test -s "$APK"

echo "PUBLICATION_PAYLOAD_GREEN"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
REMOTE_STAGE="${REMOTE_ROOT}.incoming.${STAMP}"
REMOTE_BACKUP="${REMOTE_ROOT}.previous.${STAMP}"

# The remote user needs permission to manage REMOTE_ROOT. Use a dedicated publish account.
ssh "$TARGET" "set -e; mkdir -p '$REMOTE_STAGE'"
rsync -a --delete --chmod=F644,D755 "$WORK/repo/" "$TARGET:$REMOTE_STAGE/"

# Verify immutable fingerprints and required files on the remote before atomic activation.
ssh "$TARGET" "set -euo pipefail; \
  test -s '$REMOTE_STAGE/index-v1.jar'; \
  test -s '$REMOTE_STAGE/index-v1.json'; \
  test -s '$REMOTE_STAGE/repo-fingerprint-sha256.txt'; \
  grep -qi '$EXPECTED_REPO_FP' '$REMOTE_STAGE/repo-fingerprint-sha256.txt'; \
  find '$REMOTE_STAGE' -maxdepth 1 -type f -name '*.apk' -size +1M | grep -q .; \
  if [ -e '$REMOTE_ROOT' ]; then mv '$REMOTE_ROOT' '$REMOTE_BACKUP'; fi; \
  mv '$REMOTE_STAGE' '$REMOTE_ROOT'"

echo "ORIGIN_ATOMIC_SWAP_GREEN"

# Public verification is deliberately after the swap. Failure here means origin published
# but DNS/TLS/routing is not yet green; do not claim FINAL_FORM_GREEN.
BASE="${PUBLIC_URL%/}"
curl --fail --silent --show-error --location --max-time 30 "$BASE/index-v1.jar" -o "$WORK/public-index-v1.jar"
curl --fail --silent --show-error --location --max-time 30 "$BASE/index-v1.json" -o "$WORK/public-index-v1.json"
PUBLIC_FP="$(curl --fail --silent --show-error --location --max-time 30 "$BASE/repo-fingerprint-sha256.txt" | tr -d ':[:space:]' | tr '[:lower:]' '[:upper:]')"
[[ "$PUBLIC_FP" == "$EXPECTED_REPO_FP" ]] || { echo "Public repository fingerprint mismatch" >&2; exit 5; }

echo "FDROID_PUBLISHED"
echo "repo_url=$PUBLIC_URL"
echo "repo_fingerprint_sha256=$EXPECTED_REPO_FP"
echo "next_gate=F-Droid client import then signed upgrade-path verification"
