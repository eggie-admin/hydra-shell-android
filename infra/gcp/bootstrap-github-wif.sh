#!/usr/bin/env bash
set -euo pipefail

REPO="${GITHUB_REPOSITORY:-eggie-admin/hydra-shell-android}"
RELEASE_REF="${LUHMOS_RELEASE_REF:-refs/heads/luhmos-main}"
POOL_ID="${GCP_WIF_POOL_ID:-github-luhmos}"
PROVIDER_ID="${GCP_WIF_PROVIDER_ID:-hydra-shell-android}"
SERVICE_ACCOUNT_ID="${GCP_SERVICE_ACCOUNT_ID:-watchdog-bot}"
GITHUB_API_VERSION="2026-03-10"

command -v gcloud >/dev/null || { echo 'gcloud is required' >&2; exit 2; }
command -v curl >/dev/null || { echo 'curl is required' >&2; exit 2; }
command -v python3 >/dev/null || { echo 'python3 is required' >&2; exit 2; }

PROJECT_ID="${GCP_PROJECT_ID:-$(gcloud config get-value project 2>/dev/null || true)}"
if [[ -z "$PROJECT_ID" || "$PROJECT_ID" == '(unset)' ]]; then
  echo 'No Google Cloud project selected.' >&2
  echo 'Set GCP_PROJECT_ID or run: gcloud config set project PROJECT_ID' >&2
  exit 2
fi

ACCOUNT="$(gcloud auth list --filter=status:ACTIVE --format='value(account)' | head -n1)"
[[ -n "$ACCOUNT" ]] || {
  echo 'No active Google Cloud identity. Authenticate once in Google Cloud Shell or with gcloud auth login.' >&2
  exit 3
}

REPO_OWNER="${REPO%%/*}"
REPO_NAME="${REPO#*/}"
[[ -n "$REPO_OWNER" && -n "$REPO_NAME" && "$REPO_OWNER" != "$REPO_NAME" ]] || {
  echo 'GITHUB_REPOSITORY must be owner/repository.' >&2
  exit 4
}

CURL_HEADERS=(
  -H 'Accept: application/vnd.github+json'
  -H "X-GitHub-Api-Version: ${GITHUB_API_VERSION}"
  -H 'User-Agent: LuHm-OS-WIF-bootstrap'
)
if [[ -n "${GITHUB_TOKEN:-}" ]]; then
  CURL_HEADERS+=( -H "Authorization: Bearer ${GITHUB_TOKEN}" )
fi

REPO_JSON="$(curl -fsSL "${CURL_HEADERS[@]}" "https://api.github.com/repos/${REPO}")" || {
  echo 'Unable to read GitHub repository identity; refusing WIF mutation.' >&2
  exit 5
}
OIDC_JSON="$(curl -fsSL "${CURL_HEADERS[@]}" "https://api.github.com/repos/${REPO}/actions/oidc/customization/sub")" || {
  echo 'Unable to read GitHub OIDC subject configuration; refusing WIF mutation.' >&2
  exit 5
}

IDENTITY_FIELDS="$(printf '%s' "$REPO_JSON" | python3 -c '
import json, sys
d = json.load(sys.stdin)
owner = d.get("owner") or {}
values = [owner.get("login"), owner.get("id"), d.get("name"), d.get("id")]
if any(v in (None, "") for v in values):
    raise SystemExit(2)
print("\t".join(str(v) for v in values))
')" || {
  echo 'GitHub repository identity response was incomplete; refusing WIF mutation.' >&2
  exit 5
}
IFS=$'\t' read -r ACTUAL_OWNER OWNER_ID ACTUAL_REPO REPO_ID <<< "$IDENTITY_FIELDS"
[[ "$ACTUAL_OWNER/$ACTUAL_REPO" == "$REPO" ]] || {
  echo 'GitHub repository identity mismatch; refusing WIF mutation.' >&2
  exit 5
}

IMMUTABLE_SUBJECT_ENABLED="$(printf '%s' "$OIDC_JSON" | python3 -c '
import json, sys
d = json.load(sys.stdin)
print("true" if d.get("use_immutable_subject") is True else "false")
')"
if [[ "$IMMUTABLE_SUBJECT_ENABLED" != true ]]; then
  echo 'GITHUB_OIDC_IMMUTABLE_SUBJECT=REQUIRED_NOT_CONFIRMED' >&2
  echo 'Enable the repository immutable OIDC subject before running this bootstrap.' >&2
  echo 'No Google Cloud WIF resources were mutated.' >&2
  exit 6
fi

IMMUTABLE_SUBJECT="repo:${ACTUAL_OWNER}@${OWNER_ID}/${ACTUAL_REPO}@${REPO_ID}:ref:${RELEASE_REF}"
ATTRIBUTE_CONDITION="assertion.sub=='${IMMUTABLE_SUBJECT}'"

echo "ACTIVE_GOOGLE_ACCOUNT=$ACCOUNT"
echo "GCP_PROJECT_ID=$PROJECT_ID"
echo "GITHUB_REPOSITORY=$REPO"
echo "ALLOWED_REF=$RELEASE_REF"
echo 'GITHUB_OIDC_IMMUTABLE_SUBJECT=CONFIRMED'
echo 'GITHUB_OIDC_EXACT_SUBJECT=RESOLVED_NOT_PRINTED'

PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')"
[[ -n "$PROJECT_NUMBER" ]] || { echo 'Could not resolve project number' >&2; exit 7; }

SA_EMAIL="${SERVICE_ACCOUNT_ID}@${PROJECT_ID}.iam.gserviceaccount.com"
POOL_NAME="projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}"
PROVIDER_NAME="${POOL_NAME}/providers/${PROVIDER_ID}"

echo 'Enabling required Google Cloud APIs...'
gcloud services enable \
  iam.googleapis.com \
  iamcredentials.googleapis.com \
  sts.googleapis.com \
  secretmanager.googleapis.com \
  --project="$PROJECT_ID"

if ! gcloud iam service-accounts describe "$SA_EMAIL" --project="$PROJECT_ID" >/dev/null 2>&1; then
  gcloud iam service-accounts create "$SERVICE_ACCOUNT_ID" \
    --project="$PROJECT_ID" \
    --display-name='LuHm OS GitHub OIDC'
fi

if ! gcloud iam workload-identity-pools describe "$POOL_ID" \
  --project="$PROJECT_ID" --location=global >/dev/null 2>&1; then
  gcloud iam workload-identity-pools create "$POOL_ID" \
    --project="$PROJECT_ID" \
    --location=global \
    --display-name='LuHm OS GitHub Actions'
fi

if ! gcloud iam workload-identity-pools providers describe "$PROVIDER_ID" \
  --project="$PROJECT_ID" --location=global --workload-identity-pool="$POOL_ID" >/dev/null 2>&1; then
  gcloud iam workload-identity-pools providers create-oidc "$PROVIDER_ID" \
    --project="$PROJECT_ID" \
    --location=global \
    --workload-identity-pool="$POOL_ID" \
    --display-name='LuHm OS GitHub Actions' \
    --issuer-uri='https://token.actions.githubusercontent.com/' \
    --attribute-mapping='google.subject=assertion.sub' \
    --attribute-condition="$ATTRIBUTE_CONDITION"
else
  PROVIDER_JSON="$(gcloud iam workload-identity-pools providers describe "$PROVIDER_ID" \
    --project="$PROJECT_ID" --location=global --workload-identity-pool="$POOL_ID" --format=json)"
  SUBJECT_MAPPING="$(printf '%s' "$PROVIDER_JSON" | python3 -c '
import json, sys
d=json.load(sys.stdin)
print((d.get("attributeMapping") or {}).get("google.subject", ""))
')"
  [[ "$SUBJECT_MAPPING" == 'assertion.sub' ]] || {
    echo 'Existing WIF provider does not map google.subject=assertion.sub; refusing partial repair.' >&2
    exit 8
  }
  gcloud iam workload-identity-pools providers update-oidc "$PROVIDER_ID" \
    --project="$PROJECT_ID" \
    --location=global \
    --workload-identity-pool="$POOL_ID" \
    --attribute-condition="$ATTRIBUTE_CONDITION" \
    >/dev/null
  echo 'WIF_PROVIDER_EXACT_SUBJECT_CONDITION_RECONCILED'
fi

EXACT_MEMBER="principal://iam.googleapis.com/${POOL_NAME}/subject/${IMMUTABLE_SUBJECT}"
gcloud iam service-accounts add-iam-policy-binding "$SA_EMAIL" \
  --project="$PROJECT_ID" \
  --role='roles/iam.workloadIdentityUser' \
  --member="$EXACT_MEMBER" \
  >/dev/null

echo 'WIF_EXACT_SUBJECT_BINDING_GREEN'

LEGACY_MUTABLE_MEMBER="principalSet://iam.googleapis.com/${POOL_NAME}/attribute.repository/${REPO}"
export LEGACY_MUTABLE_MEMBER
POLICY_JSON="$(gcloud iam service-accounts get-iam-policy "$SA_EMAIL" --project="$PROJECT_ID" --format=json)"
if printf '%s' "$POLICY_JSON" | python3 -c '
import json, os, sys
d=json.load(sys.stdin)
target=os.environ["LEGACY_MUTABLE_MEMBER"]
found=any(target in (b.get("members") or []) for b in d.get("bindings") or [])
raise SystemExit(0 if found else 1)
'; then
  gcloud iam service-accounts remove-iam-policy-binding "$SA_EMAIL" \
    --project="$PROJECT_ID" \
    --role='roles/iam.workloadIdentityUser' \
    --member="$LEGACY_MUTABLE_MEMBER" \
    >/dev/null
  echo 'WIF_LEGACY_MUTABLE_REPOSITORY_BINDING_REMOVED'
else
  echo 'WIF_LEGACY_MUTABLE_REPOSITORY_BINDING=ABSENT'
fi

SIGNING_SECRETS=(
  luhmos-android-keystore-b64
  luhmos-android-keystore-password
  luhmos-android-key-password
  luhmos-fdroid-keystore-b64
  luhmos-fdroid-keystore-password
  luhmos-fdroid-key-password
)

FOUND_ALL_SIGNING_SECRETS=true
for secret in "${SIGNING_SECRETS[@]}"; do
  if gcloud secrets describe "$secret" --project="$PROJECT_ID" >/dev/null 2>&1; then
    gcloud secrets add-iam-policy-binding "$secret" \
      --project="$PROJECT_ID" \
      --member="serviceAccount:${SA_EMAIL}" \
      --role='roles/secretmanager.secretAccessor' \
      >/dev/null
    echo "SECRET_ACCESS_BOUND=$secret"
  else
    FOUND_ALL_SIGNING_SECRETS=false
    echo "SIGNING_SECRET_NOT_PRESENT=$secret"
  fi
done

cat <<EOF

GCP_WIF_BOOTSTRAP_GREEN

GitHub repository variables:
GCP_PROJECT_ID=${PROJECT_ID}
GCP_WIF_PROVIDER=${PROVIDER_NAME}
GCP_SERVICE_ACCOUNT=${SA_EMAIL}
GCP_SIGNING_SECRETS_ENABLED=${FOUND_ALL_SIGNING_SECRETS}
EOF

if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
  echo 'Authenticated GitHub CLI detected; writing public repository variables automatically.'
  gh variable set GCP_PROJECT_ID --repo "$REPO" --body "$PROJECT_ID"
  gh variable set GCP_WIF_PROVIDER --repo "$REPO" --body "$PROVIDER_NAME"
  gh variable set GCP_SERVICE_ACCOUNT --repo "$REPO" --body "$SA_EMAIL"
  gh variable set GCP_SIGNING_SECRETS_ENABLED --repo "$REPO" --body "$FOUND_ALL_SIGNING_SECRETS"
  echo 'GITHUB_REPOSITORY_VARIABLES_GREEN'
else
  echo 'GitHub CLI is not authenticated; copy the four public values above into GitHub Actions repository variables.'
fi

echo
printf '%s\n' \
  'Security boundary:' \
  "- repository: ${REPO}" \
  "- branch: ${RELEASE_REF}" \
  '- issuer: https://token.actions.githubusercontent.com/' \
  '- immutable GitHub OIDC subject required and exact-subject Google binding used' \
  '- no Google service-account JSON key is created or stored.'
