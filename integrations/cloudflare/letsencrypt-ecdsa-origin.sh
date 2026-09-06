#!/usr/bin/env bash
set -euo pipefail

# KAI 9000 Let's Encrypt ECDSA origin certificate helper.
# Dry-run unless APPLY=1. Requires certbot + certbot-dns-cloudflare.

DOMAIN="${DOMAIN:-eggiebagelface.art}"
EMAIL="${LE_EMAIL:-}"
TOKEN="${CF_DNS_API_TOKEN:-}"
APPLY="${APPLY:-0}"

if [[ "$APPLY" != "1" ]]; then
  cat <<EOF
DRY RUN
Would request a Let's Encrypt wildcard/origin certificate for:
  $DOMAIN
  *.$DOMAIN
using DNS-01, ECDSA P-256 (secp256r1), and a scoped Cloudflare DNS token.
Set APPLY=1, LE_EMAIL and CF_DNS_API_TOKEN on the trusted origin/signing host to execute.
EOF
  exit 0
fi

command -v certbot >/dev/null || { echo "certbot missing" >&2; exit 2; }
[[ -n "$EMAIL" ]] || { echo "LE_EMAIL is required" >&2; exit 2; }
[[ -n "$TOKEN" ]] || { echo "CF_DNS_API_TOKEN is required" >&2; exit 2; }

CREDS="$(mktemp)"
trap 'rm -f "$CREDS"' EXIT
chmod 600 "$CREDS"
printf 'dns_cloudflare_api_token = %s\n' "$TOKEN" > "$CREDS"

certbot certonly \
  --non-interactive \
  --agree-tos \
  --email "$EMAIL" \
  --dns-cloudflare \
  --dns-cloudflare-credentials "$CREDS" \
  --dns-cloudflare-propagation-seconds 20 \
  --key-type ecdsa \
  --elliptic-curve secp256r1 \
  --cert-name "$DOMAIN" \
  -d "$DOMAIN" \
  -d "*.$DOMAIN"

printf 'LETSENCRYPT_ECDSA_ORIGIN_CERT_ISSUED domain=%s\n' "$DOMAIN"
