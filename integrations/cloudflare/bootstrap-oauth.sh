#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-status}"
WRANGLER_VERSION="${WRANGLER_VERSION:-4.119.0}"
WRANGLER="npx -y wrangler@${WRANGLER_VERSION}"

secure_local_dirs() {
  umask 077
  mkdir -p "$HOME/.config/.wrangler/config" "$HOME/.cloudflared"
  chmod 700 "$HOME/.config" "$HOME/.config/.wrangler" "$HOME/.config/.wrangler/config" "$HOME/.cloudflared" 2>/dev/null || true
}

harden_wrangler_credentials() {
  local p
  for p in \
    "$HOME/.config/.wrangler/config/default.toml" \
    "$HOME/.config/.wrangler/config/default.enc"; do
    [ ! -f "$p" ] || chmod 600 "$p"
  done
}

case "$MODE" in
  wrangler-login)
    command -v npx >/dev/null || { echo 'npx is required' >&2; exit 2; }
    secure_local_dirs
    echo 'Opening Cloudflare OAuth device authorization. Approve in your normal browser session.'
    if [ "${KAI_WRANGLER_USE_KEYRING:-0}" = "1" ]; then
      $WRANGLER login --device --use-keyring
    else
      $WRANGLER login --device
    fi
    harden_wrangler_credentials
    $WRANGLER whoami
    echo 'CLOUDFLARE_WRANGLER_OAUTH_GREEN'
    ;;

  wrangler-status)
    command -v npx >/dev/null || { echo 'npx is required' >&2; exit 2; }
    $WRANGLER whoami
    ;;

  wrangler-logout)
    command -v npx >/dev/null || { echo 'npx is required' >&2; exit 2; }
    $WRANGLER logout
    echo 'CLOUDFLARE_WRANGLER_OAUTH_LOGGED_OUT'
    ;;

  tunnel-login)
    command -v cloudflared >/dev/null || { echo 'cloudflared is required' >&2; exit 2; }
    secure_local_dirs
    echo 'Cloudflare Tunnel browser authorization will create an account-wide cert.pem.'
    echo 'Treat cert.pem as Crown authority: local 0600 only, never Git/chat/artifacts.'
    cloudflared tunnel login
    CERT="$HOME/.cloudflared/cert.pem"
    test -s "$CERT" || { echo 'cloudflared login did not produce cert.pem' >&2; exit 3; }
    chmod 600 "$CERT"
    echo 'CLOUDFLARE_TUNNEL_ACCOUNT_LOGIN_GREEN'
    ;;

  status)
    echo '=== Wrangler OAuth ==='
    if command -v npx >/dev/null; then
      $WRANGLER whoami || true
    else
      echo 'npx: missing'
    fi
    echo
    echo '=== cloudflared account certificate ==='
    if [ -s "$HOME/.cloudflared/cert.pem" ]; then
      stat -c 'path=%n mode=%a size=%s' "$HOME/.cloudflared/cert.pem" 2>/dev/null || ls -l "$HOME/.cloudflared/cert.pem"
    else
      echo 'cert.pem: absent'
    fi
    ;;

  *)
    echo "usage: $0 {wrangler-login|wrangler-status|wrangler-logout|tunnel-login|status}" >&2
    exit 2
    ;;
esac
