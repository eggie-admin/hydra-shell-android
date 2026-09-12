#!/usr/bin/env bash
set -euo pipefail

DOMAIN="${1:-}"
EMAIL="${LETSENCRYPT_EMAIL:-}"
CREDS="${CLOUDFLARE_CERTBOT_CREDS:-/etc/letsencrypt/cloudflare.ini}"

if [[ -z "$DOMAIN" ]]; then
  echo "Usage: sudo $0 cms.example.com" >&2
  exit 2
fi
if [[ -z "$EMAIL" ]]; then
  echo "Set LETSENCRYPT_EMAIL first." >&2
  exit 2
fi
if [[ "${EUID}" -ne 0 ]]; then
  echo "Run with sudo." >&2
  exit 1
fi
if [[ ! -f "$CREDS" ]]; then
  echo "Missing $CREDS. Copy cloudflare.ini.example and add a restricted token." >&2
  exit 1
fi
chmod 600 "$CREDS"

apt-get update
apt-get install -y certbot python3-certbot-dns-cloudflare

certbot certonly \
  --dns-cloudflare \
  --dns-cloudflare-credentials "$CREDS" \
  --dns-cloudflare-propagation-seconds 60 \
  --non-interactive \
  --agree-tos \
  --email "$EMAIL" \
  -d "$DOMAIN"

echo "Issued: /etc/letsencrypt/live/$DOMAIN/fullchain.pem"
echo "Private key: /etc/letsencrypt/live/$DOMAIN/privkey.pem"
