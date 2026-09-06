#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-status}"

secure_gcloud_dir() {
  umask 077
  mkdir -p "$HOME/.config/gcloud"
  chmod 700 "$HOME/.config" "$HOME/.config/gcloud" 2>/dev/null || true
}

case "$MODE" in
  login)
    command -v gcloud >/dev/null || { echo 'gcloud is required' >&2; exit 2; }
    secure_gcloud_dir
    echo 'Authenticating gcloud as the human operator. Do not use this credential for unattended workloads.'
    gcloud auth login
    gcloud auth list --filter=status:ACTIVE --format='value(account)'
    echo 'GOOGLE_CLOUD_OPERATOR_OAUTH_GREEN'
    ;;

  login-remote)
    command -v gcloud >/dev/null || { echo 'gcloud is required' >&2; exit 2; }
    secure_gcloud_dir
    echo 'Remote/browser-assisted gcloud authentication.'
    gcloud auth login --no-launch-browser
    gcloud auth list --filter=status:ACTIVE --format='value(account)'
    echo 'GOOGLE_CLOUD_OPERATOR_OAUTH_GREEN'
    ;;

  status)
    command -v gcloud >/dev/null || { echo 'gcloud: missing'; exit 0; }
    echo '=== active account ==='
    gcloud auth list --filter=status:ACTIVE --format='value(account)' || true
    echo '=== active project ==='
    gcloud config get-value project 2>/dev/null || true
    ;;

  logout)
    command -v gcloud >/dev/null || { echo 'gcloud is required' >&2; exit 2; }
    ACTIVE="$(gcloud auth list --filter=status:ACTIVE --format='value(account)' | head -n1)"
    [ -n "$ACTIVE" ] || { echo 'No active gcloud account'; exit 0; }
    gcloud auth revoke "$ACTIVE"
    echo 'GOOGLE_CLOUD_OPERATOR_OAUTH_REVOKED'
    ;;

  *)
    echo "usage: $0 {login|login-remote|status|logout}" >&2
    exit 2
    ;;
esac
