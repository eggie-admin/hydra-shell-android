#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-pull-root}"
DOMAIN="${CF_ORIGIN_DOMAIN:-eggiebagelface.art}"
OUT_DIR="${CF_ORIGIN_OUT_DIR:-build/cloudflare-origin-ca}"
ROOT_URL="https://developers.cloudflare.com/ssl/static/origin_ca_ecc_root.pem"
API_BASE="https://api.cloudflare.com/client/v4"
mkdir -p "$OUT_DIR"

need() {
  command -v "$1" >/dev/null || {
    echo "Missing required command: $1" >&2
    exit 2
  }
}

need curl
need openssl
need python3

pull_root() {
  local root="$OUT_DIR/cloudflare-origin-ecc-root.pem"
  curl --fail --silent --show-error --location "$ROOT_URL" -o "$root"
  openssl x509 -in "$root" -noout -subject -issuer -fingerprint -sha256
  echo "CLOUDFLARE_ORIGIN_ECC_ROOT_PULLED"
}

resolve_zone_id() {
  : "${CF_API_TOKEN:?CF_API_TOKEN is required}"
  python3 - "$DOMAIN" <<'PY'
import json, os, sys, urllib.parse, urllib.request
name = sys.argv[1]
url = 'https://api.cloudflare.com/client/v4/zones?' + urllib.parse.urlencode({'name': name, 'status': 'active', 'per_page': 50})
req = urllib.request.Request(url, headers={'Authorization': f"Bearer {os.environ['CF_API_TOKEN']}", 'Accept': 'application/json'})
with urllib.request.urlopen(req) as r:
    payload = json.load(r)
if not payload.get('success') or not payload.get('result'):
    raise SystemExit('Could not resolve active Cloudflare zone')
print(payload['result'][0]['id'])
PY
}

issue_origin_cert() {
  : "${CF_API_TOKEN:?CF_API_TOKEN is required}"
  umask 077
  pull_root >/dev/null

  local key="$OUT_DIR/origin-p256.key"
  local csr="$OUT_DIR/origin-p256.csr"
  local cert="$OUT_DIR/origin-p256.pem"
  local response="$OUT_DIR/origin-ca-response.json"
  local fullchain="$OUT_DIR/origin-p256-fullchain.pem"

  if [[ ! -s "$key" ]]; then
    openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-256 -out "$key"
    chmod 600 "$key"
  fi

  openssl req -new -sha256 \
    -key "$key" \
    -subj "/CN=$DOMAIN" \
    -addext "subjectAltName=DNS:$DOMAIN,DNS:*.$DOMAIN" \
    -out "$csr"

  python3 - "$csr" "$DOMAIN" "$OUT_DIR/request.json" <<'PY'
import json, pathlib, sys
csr_path, domain, out = sys.argv[1:]
payload = {
    'csr': pathlib.Path(csr_path).read_text(),
    'hostnames': [domain, f'*.{domain}'],
    'request_type': 'origin-ecc',
    'requested_validity': 365,
}
pathlib.Path(out).write_text(json.dumps(payload), encoding='utf-8')
PY

  curl --fail --silent --show-error \
    -X POST "$API_BASE/certificates" \
    -H "Authorization: Bearer $CF_API_TOKEN" \
    -H 'Content-Type: application/json' \
    --data-binary "@$OUT_DIR/request.json" \
    -o "$response"

  python3 - "$response" "$cert" <<'PY'
import json, pathlib, sys
payload = json.loads(pathlib.Path(sys.argv[1]).read_text())
if not payload.get('success'):
    raise SystemExit('Cloudflare Origin CA issuance failed')
result = payload.get('result') or {}
certificate = result.get('certificate')
if not certificate:
    raise SystemExit('Cloudflare Origin CA response had no certificate')
pathlib.Path(sys.argv[2]).write_text(certificate.rstrip() + '\n', encoding='utf-8')
print('certificate_id=' + str(result.get('id', '')))
print('expires_on=' + str(result.get('expires_on', '')))
PY

  cat "$cert" "$OUT_DIR/cloudflare-origin-ecc-root.pem" > "$fullchain"
  openssl verify -CAfile "$OUT_DIR/cloudflare-origin-ecc-root.pem" "$cert"
  openssl x509 -in "$cert" -noout -subject -issuer -dates -fingerprint -sha256

  rm -f "$OUT_DIR/request.json"
  chmod 600 "$key"
  echo "CLOUDFLARE_ORIGIN_ECC_CERT_ISSUED"
  echo "private_key=$key"
  echo "certificate=$cert"
  echo "fullchain=$fullchain"
}

list_origin_certs() {
  : "${CF_API_TOKEN:?CF_API_TOKEN is required}"
  local zone_id="${CF_ZONE_ID:-$(resolve_zone_id)}"
  CF_ZONE_ID="$zone_id" python3 <<'PY'
import json, os, urllib.parse, urllib.request
url = 'https://api.cloudflare.com/client/v4/certificates?' + urllib.parse.urlencode({'zone_id': os.environ['CF_ZONE_ID'], 'per_page': 50})
req = urllib.request.Request(url, headers={'Authorization': f"Bearer {os.environ['CF_API_TOKEN']}", 'Accept': 'application/json'})
with urllib.request.urlopen(req) as r:
    payload = json.load(r)
if not payload.get('success'):
    raise SystemExit('Cloudflare Origin CA list failed')
for item in payload.get('result') or []:
    print(json.dumps({
        'id': item.get('id'),
        'hostnames': item.get('hostnames'),
        'request_type': item.get('request_type'),
        'expires_on': item.get('expires_on'),
    }, sort_keys=True))
PY
}

case "$MODE" in
  pull-root) pull_root ;;
  issue) issue_origin_cert ;;
  list) list_origin_certs ;;
  *)
    echo "Usage: $0 [pull-root|issue|list]" >&2
    exit 2
    ;;
esac
