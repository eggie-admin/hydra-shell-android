#!/usr/bin/env bash
set -euo pipefail
umask 077

REPO="${GITHUB_REPOSITORY:-eggie-admin/hydra-shell-android}"
RELEASE_REF="${LUHMOS_RELEASE_REF:-luhmos-main}"
BUNDLE_NAME="LuHmOS_1.0.0_SIGNING_BOOTSTRAP_PRIVATE.zip"
BUNDLE="${1:-}"

say() { printf '\n== %s ==\n' "$*"; }
die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
need() { command -v "$1" >/dev/null 2>&1 || die "required command missing: $1"; }

say 'LuHm OS 1.0.0 Samsung release bootstrap'
printf '%s\n' \
  'This ceremony does not touch Termux.' \
  'It stores signing values in Google Secret Manager and GitHub Actions encrypted secrets,' \
  'configures keyless GitHub->Google OIDC, proves the HTTPS trust path, and launches the signed release.'

need gcloud
need git
need unzip
need curl
need python3

if ! command -v gh >/dev/null 2>&1; then
  say 'Installing GitHub CLI in Cloud Shell'
  sudo apt-get update -qq
  sudo apt-get install -y gh
fi

if [[ -z "$BUNDLE" ]]; then
  BUNDLE="$(find "$HOME" -maxdepth 3 -type f -name "$BUNDLE_NAME" -print -quit 2>/dev/null || true)"
fi
[[ -n "$BUNDLE" && -f "$BUNDLE" ]] || die "Upload $BUNDLE_NAME to Cloud Shell, then rerun this script (optionally pass its path)."

PROJECT_ID="${GCP_PROJECT_ID:-$(gcloud config get-value project 2>/dev/null || true)}"
if [[ -z "$PROJECT_ID" || "$PROJECT_ID" == '(unset)' ]]; then
  die 'No Google Cloud project selected. Run: gcloud config set project YOUR_PROJECT_ID'
fi

ACCOUNT="$(gcloud auth list --filter=status:ACTIVE --format='value(account)' | head -n1)"
if [[ -z "$ACCOUNT" ]]; then
  say 'Authorizing Google Cloud once'
  gcloud auth login
  ACCOUNT="$(gcloud auth list --filter=status:ACTIVE --format='value(account)' | head -n1)"
fi
[[ -n "$ACCOUNT" ]] || die 'Google Cloud authentication did not complete.'
printf 'Google account: %s\nProject: %s\n' "$ACCOUNT" "$PROJECT_ID"

if ! gh auth status -h github.com >/dev/null 2>&1; then
  say 'Authorizing GitHub once over HTTPS'
  gh auth login --hostname github.com --git-protocol https --web --scopes repo,workflow
fi
gh auth status -h github.com >/dev/null 2>&1 || die 'GitHub HTTPS authentication did not complete.'

gh repo view "$REPO" >/dev/null 2>&1 || die "GitHub account cannot administer $REPO"

WORK="$(mktemp -d "${TMPDIR:-/tmp}/luhmos-release-bootstrap.XXXXXX")"
cleanup() { rm -rf "$WORK"; }
trap cleanup EXIT INT TERM
unzip -q "$BUNDLE" -d "$WORK"
PRIVATE_FILE="$WORK/GITHUB_ACTIONS_SECRETS_PRIVATE.txt"
PUBLIC_FILE="$WORK/PUBLIC_SIGNING_FINGERPRINTS.txt"
[[ -f "$PRIVATE_FILE" && -f "$PUBLIC_FILE" ]] || die 'Signing bootstrap bundle is missing required manifest files.'

EXPECTED_PRIVATE=(
  LUHMOS_ANDROID_KEYSTORE_B64
  LUHMOS_ANDROID_KEYSTORE_PASSWORD
  LUHMOS_ANDROID_KEY_PASSWORD
  LUHMOS_FDROID_KEYSTORE_B64
  LUHMOS_FDROID_KEYSTORE_PASSWORD
  LUHMOS_FDROID_KEY_PASSWORD
)

declare -A PRIVATE=()
while IFS='=' read -r key value; do
  [[ "$key" =~ ^LUHMOS_(ANDROID|FDROID)_ ]] || continue
  PRIVATE["$key"]="$value"
done < "$PRIVATE_FILE"
for key in "${EXPECTED_PRIVATE[@]}"; do
  [[ -n "${PRIVATE[$key]:-}" ]] || die "bundle does not contain $key"
done

declare -A PUBLIC=()
while IFS='=' read -r key value; do
  case "$key" in
    LUHMOS_ANDROID_CERT_SHA256|LUHMOS_FDROID_REPO_FINGERPRINT_SHA256)
      PUBLIC["$key"]="$value"
      ;;
  esac
done < "$PUBLIC_FILE"
[[ -n "${PUBLIC[LUHMOS_ANDROID_CERT_SHA256]:-}" ]] || die 'missing public Android signer fingerprint'
[[ -n "${PUBLIC[LUHMOS_FDROID_REPO_FINGERPRINT_SHA256]:-}" ]] || die 'missing public F-Droid repository fingerprint'

say 'Enabling Secret Manager and storing persistent signing identities'
gcloud services enable secretmanager.googleapis.com --project="$PROJECT_ID" >/dev/null

declare -A GCP_NAMES=(
  [LUHMOS_ANDROID_KEYSTORE_B64]=luhmos-android-keystore-b64
  [LUHMOS_ANDROID_KEYSTORE_PASSWORD]=luhmos-android-keystore-password
  [LUHMOS_ANDROID_KEY_PASSWORD]=luhmos-android-key-password
  [LUHMOS_FDROID_KEYSTORE_B64]=luhmos-fdroid-keystore-b64
  [LUHMOS_FDROID_KEYSTORE_PASSWORD]=luhmos-fdroid-keystore-password
  [LUHMOS_FDROID_KEY_PASSWORD]=luhmos-fdroid-key-password
)

for key in "${EXPECTED_PRIVATE[@]}"; do
  secret="${GCP_NAMES[$key]}"
  if ! gcloud secrets describe "$secret" --project="$PROJECT_ID" >/dev/null 2>&1; then
    gcloud secrets create "$secret" --project="$PROJECT_ID" --replication-policy=automatic >/dev/null
  fi
  printf '%s' "${PRIVATE[$key]}" | gcloud secrets versions add "$secret" --project="$PROJECT_ID" --data-file=- >/dev/null
  printf 'Secret Manager: %s = stored\n' "$secret"
done

say 'Configuring repository-scoped GitHub OIDC trust'
GCP_PROJECT_ID="$PROJECT_ID" GITHUB_REPOSITORY="$REPO" LUHMOS_RELEASE_REF="refs/heads/${RELEASE_REF}" \
  bash infra/gcp/bootstrap-github-wif.sh | tee "$WORK/wif-bootstrap-public.log"

PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')"
WIF_PROVIDER="projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/github-luhmos/providers/hydra-shell-android"
SERVICE_ACCOUNT="watchdog-bot@${PROJECT_ID}.iam.gserviceaccount.com"

gh variable set GCP_PROJECT_ID --repo "$REPO" --body "$PROJECT_ID"
gh variable set GCP_WIF_PROVIDER --repo "$REPO" --body "$WIF_PROVIDER"
gh variable set GCP_SERVICE_ACCOUNT --repo "$REPO" --body "$SERVICE_ACCOUNT"
gh variable set GCP_SIGNING_SECRETS_ENABLED --repo "$REPO" --body 'true'
gh variable set LUHMOS_ANDROID_CERT_SHA256 --repo "$REPO" --body "${PUBLIC[LUHMOS_ANDROID_CERT_SHA256]}"
gh variable set LUHMOS_FDROID_REPO_FINGERPRINT_SHA256 --repo "$REPO" --body "${PUBLIC[LUHMOS_FDROID_REPO_FINGERPRINT_SHA256]}"

say 'Mirroring signing values into GitHub Actions encrypted secrets for the established release forge'
for key in "${EXPECTED_PRIVATE[@]}"; do
  printf '%s' "${PRIVATE[$key]}" | gh secret set "$key" --repo "$REPO"
  printf 'GitHub Actions secret: %s = stored\n' "$key"
done

# Values are no longer needed in shell memory after both vaults have accepted them.
for key in "${EXPECTED_PRIVATE[@]}"; do
  unset 'PRIVATE[$key]'
done

say 'Proving keyless GitHub to Google HTTPS authentication'
gh workflow run luhmos-gcp-oidc-smoke.yml --repo "$REPO" --ref "$RELEASE_REF"
sleep 3
SMOKE_RUN="$(gh run list --repo "$REPO" --workflow luhmos-gcp-oidc-smoke.yml --branch "$RELEASE_REF" --event workflow_dispatch --limit 1 --json databaseId --jq '.[0].databaseId')"
[[ -n "$SMOKE_RUN" ]] || die 'could not identify OIDC smoke run'
gh run watch "$SMOKE_RUN" --repo "$REPO" --exit-status

say 'Launching LuHm OS 1.0.0 signed F-Droid release'
gh workflow run luhmos-fdroid-public-release.yml --repo "$REPO" --ref "$RELEASE_REF" -f publish_public_mirror=true
sleep 3
RELEASE_RUN="$(gh run list --repo "$REPO" --workflow luhmos-fdroid-public-release.yml --branch "$RELEASE_REF" --event workflow_dispatch --limit 1 --json databaseId --jq '.[0].databaseId')"
[[ -n "$RELEASE_RUN" ]] || die 'could not identify signed release run'
gh run watch "$RELEASE_RUN" --repo "$REPO" --exit-status

say 'Waiting for immutable GitHub v1.0.0 release and public F-Droid index'
FDROID_URL='https://raw.githubusercontent.com/eggie-admin/hydra-shell-android/fdroid-public/fdroid/repo/'
while :; do
  github_green=false
  fdroid_green=false

  if gh release view v1.0.0 --repo "$REPO" >/dev/null 2>&1; then
    github_green=true
  fi

  if curl --fail --silent --show-error --location "${FDROID_URL}index-v2.json" -o "$WORK/index-v2.json" 2>/dev/null; then
    if python3 - "$WORK/index-v2.json" <<'PY'
import json, sys
p=sys.argv[1]
data=json.load(open(p, encoding='utf-8'))
text=json.dumps(data, separators=(',', ':'))
raise SystemExit(0 if 'art.eggiebagelface.luhmos' in text and ('"100"' in text or ':100' in text) else 1)
PY
    then
      fdroid_green=true
    fi
  fi

  if [[ "$github_green" == true && "$fdroid_green" == true ]]; then
    break
  fi
  printf 'Install gate: GitHub release=%s F-Droid package=%s\n' "$github_green" "$fdroid_green"
  sleep 30
done

say 'LUHMOS_SAMSUNG_INSTALL_READY'
printf '%s\n' \
  'Package: art.eggiebagelface.luhmos' \
  'Version: 1.0.0 (100)' \
  "F-Droid repository: ${FDROID_URL}" \
  "APK signer SHA-256: ${PUBLIC[LUHMOS_ANDROID_CERT_SHA256]}" \
  "F-Droid repository fingerprint SHA-256: ${PUBLIC[LUHMOS_FDROID_REPO_FINGERPRINT_SHA256]}" \
  '' \
  'Samsung Secure Folder final user action:' \
  '1. Open the Secure Folder copy of F-Droid.' \
  "2. Add repository: ${FDROID_URL}" \
  '3. Refresh repositories and search for LuHm OS.' \
  '4. Verify package art.eggiebagelface.luhmos, version 1.0.0, then tap Install.'
