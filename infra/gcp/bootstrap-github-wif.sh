#!/usr/bin/env bash
set -euo pipefail

REPO="${GITHUB_REPOSITORY:-eggie-admin/hydra-shell-android}"
RELEASE_REF="${LUHMOS_RELEASE_REF:-refs/heads/luhmos-main}"
POOL_ID="${GCP_WIF_POOL_ID:-github-luhmos}"
PROVIDER_ID="${GCP_WIF_PROVIDER_ID:-hydra-shell-android}"
SERVICE_ACCOUNT_ID="${GCP_SERVICE_ACCOUNT_ID:-watchdog-bot}"

command -v gcloud >/dev/null || { echo 'gcloud is required' >&2; exit 2; }

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

echo "ACTIVE_GOOGLE_ACCOUNT=$ACCOUNT"
echo "GCP_PROJECT_ID=$PROJECT_ID"
echo "GITHUB_REPOSITORY=$REPO"
echo "ALLOWED_REF=$RELEASE_REF"

PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')"
[[ -n "$PROJECT_NUMBER" ]] || { echo 'Could not resolve project number' >&2; exit 4; }

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
    --attribute-mapping='google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner,attribute.ref=assertion.ref' \
    --attribute-condition="assertion.repository=='${REPO}' && assertion.ref=='${RELEASE_REF}'"
else
  echo 'Workload Identity provider already exists; leaving its immutable identity in place.'
fi

gcloud iam service-accounts add-iam-policy-binding "$SA_EMAIL" \
  --project="$PROJECT_ID" \
  --role='roles/iam.workloadIdentityUser' \
  --member="principalSet://iam.googleapis.com/${POOL_NAME}/attribute.repository/${REPO}" \
  >/dev/null

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
  '- no Google service-account JSON key is created or stored.'
