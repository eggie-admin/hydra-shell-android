#!/usr/bin/env bash
set -euo pipefail
umask 077

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT="${GCP_PROJECT:-}"
ZONE="${GCP_ZONE:-us-central1-a}"
INSTANCE="${KAI_GCP_INSTANCE:-kai9000-free}"
TUNNEL_NAME="${CF_FDROID_TUNNEL_NAME:-kai9000-fdroid-origin}"
FDROID_HOST="fdroid.eggiebagelface.art"
PUBLIC_URL="https://${FDROID_HOST}/fdroid/repo"
BUNDLE="${KAI_SIGNED_BUNDLE:-$HOME/storage/downloads/KAI9000_FDROID_SIGNED_20260906.zip}"
EXPECTED_BUNDLE_SHA256="fa350eeb2a2945b3b0e664f459ae1706cd3c19d0c02913e799e7ea005c6f3028"
EXPECTED_APK_SIGNER="A5E9364D5C21A119FE1D17FD39EE7BAE8192A872CE58A3E7A865248E0B070407"
EXPECTED_REPO_FP="BFB900A9EC913D35C22F1DC3DE7B152D1AF5CA11B7B07E5FAFDD06B44811F66D"

usage() {
  cat <<EOF
usage: $0 [--bundle PATH] [--project ID]

The cast self-bootstraps human OAuth when required:
  Cloudflare: cloudflared tunnel login
  Google:     gcloud auth login --no-launch-browser

Google project selection order:
  1. --project
  2. GCP_PROJECT
  3. active gcloud configured project
  4. the only project visible to the active Google identity

Default signed bundle path:
  $HOME/storage/downloads/KAI9000_FDROID_SIGNED_20260906.zip
EOF
}

while (($#)); do
  case "$1" in
    --bundle) BUNDLE="${2:-}"; shift 2 ;;
    --project) PROJECT="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

[ -s "$BUNDLE" ] || { echo "RED: signed bundle not found: $BUNDLE" >&2; exit 2; }

for cmd in gcloud cloudflared python3 sha256sum unzip tar curl; do
  command -v "$cmd" >/dev/null || { echo "RED: missing command: $cmd" >&2; exit 3; }
done

# Human OAuth only. Never print/export bearer tokens, browser cookies, OAuth refresh tokens,
# credential JSON contents, Cloudflare account cert contents, or signing-key material.
ACTIVE_GCLOUD="$(gcloud auth list --filter=status:ACTIVE --format='value(account)' 2>/dev/null | head -n1 || true)"
if [ -z "$ACTIVE_GCLOUD" ]; then
  echo 'Google Cloud operator OAuth is absent. Starting browser-assisted login.'
  bash "$REPO_ROOT/integrations/google-cloud/bootstrap-oauth.sh" login-remote
  ACTIVE_GCLOUD="$(gcloud auth list --filter=status:ACTIVE --format='value(account)' 2>/dev/null | head -n1 || true)"
fi
[ -n "$ACTIVE_GCLOUD" ] || { echo 'RED: Google OAuth login did not produce an active identity' >&2; exit 4; }
echo 'GOOGLE_OPERATOR_OAUTH_PRESENT'

if [ ! -s "$HOME/.cloudflared/cert.pem" ]; then
  echo 'Cloudflare Tunnel operator OAuth is absent. Starting browser authorization.'
  bash "$REPO_ROOT/integrations/cloudflare/bootstrap-oauth.sh" tunnel-login
fi
test -s "$HOME/.cloudflared/cert.pem" || { echo 'RED: Cloudflare tunnel login did not produce cert.pem' >&2; exit 4; }
chmod 600 "$HOME/.cloudflared/cert.pem"
echo 'CLOUDFLARE_TUNNEL_OAUTH_PRESENT'

# Resolve the Google project without guessing across multiple projects.
if [ -z "$PROJECT" ]; then
  CONFIGURED_PROJECT="$(gcloud config get-value project 2>/dev/null || true)"
  if [ -n "$CONFIGURED_PROJECT" ] && [ "$CONFIGURED_PROJECT" != '(unset)' ]; then
    PROJECT="$CONFIGURED_PROJECT"
  else
    mapfile -t VISIBLE_PROJECTS < <(gcloud projects list --format='value(projectId)' 2>/dev/null | sed '/^$/d')
    if [ "${#VISIBLE_PROJECTS[@]}" -eq 1 ]; then
      PROJECT="${VISIBLE_PROJECTS[0]}"
    elif [ "${#VISIBLE_PROJECTS[@]}" -eq 0 ]; then
      echo 'RED: active Google identity has no visible project; create/select a project first' >&2
      exit 4
    else
      echo 'RED: multiple Google Cloud projects are visible; rerun with --project PROJECT_ID' >&2
      printf 'visible_project=%s\n' "${VISIBLE_PROJECTS[@]}" >&2
      exit 4
    fi
  fi
fi

gcloud projects describe "$PROJECT" --format='value(projectId)' >/dev/null
GCP_PROJECT="$PROJECT" gcloud config set project "$PROJECT" >/dev/null
echo "GOOGLE_PROJECT_SELECTED=$PROJECT"

ACTUAL_BUNDLE_SHA="$(sha256sum "$BUNDLE" | awk '{print $1}')"
[ "$ACTUAL_BUNDLE_SHA" = "$EXPECTED_BUNDLE_SHA256" ] || {
  echo "RED: signed bundle SHA-256 mismatch" >&2
  exit 5
}
echo 'SIGNED_BUNDLE_SHA256_GREEN'

WORK="$(mktemp -d "${TMPDIR:-/tmp}/kai9000-live.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT INT TERM
unzip -q "$BUNDLE" -d "$WORK/signed"

test -s "$WORK/signed/FINAL_FORM_SIGNED_STATUS.json"
test -d "$WORK/signed/repo"
python3 - "$WORK/signed/FINAL_FORM_SIGNED_STATUS.json" "$EXPECTED_APK_SIGNER" "$EXPECTED_REPO_FP" <<'PY'
import json, sys
p, apk, repo = sys.argv[1:]
s = json.load(open(p, encoding='utf-8'))
assert s.get('state') == 'FDROID_SIGNED'
assert s.get('fdroid_signed') is True
assert s.get('apk_signer_sha256', '').upper() == apk
assert s.get('repo_fingerprint_sha256', '').upper() == repo
print('PERSISTENT_SIGNED_EVIDENCE_GREEN')
PY

test -s "$WORK/signed/repo/index-v1.jar"
test -s "$WORK/signed/repo/index-v1.json"
test -s "$WORK/signed/repo/repo-fingerprint-sha256.txt"
grep -qi "$EXPECTED_REPO_FP" "$WORK/signed/repo/repo-fingerprint-sha256.txt"
tar -C "$WORK/signed/repo" -czf "$WORK/repo.tar.gz" .

# Provision/reconcile Google strict-free origin. It removes legacy public web ingress
# and proves IAP-only SSH plus loopback nginx.
GCP_PROJECT="$PROJECT" GCP_ZONE="$ZONE" KAI_GCP_INSTANCE="$INSTANCE" \
  bash "$REPO_ROOT/integrations/google-cloud/provision-strict-free-vm.sh"

# Create or reuse a locally-managed F-Droid tunnel under the operator OAuth account cert.
TUNNEL_ID="$(cloudflared tunnel list --output json | python3 -c '
import json,sys
name=sys.argv[1]
for x in json.load(sys.stdin):
    if x.get("name") == name:
        print(x.get("id") or x.get("uuid") or "")
        break
' "$TUNNEL_NAME")"

if [ -z "$TUNNEL_ID" ]; then
  echo "Creating dedicated tunnel: $TUNNEL_NAME"
  cloudflared tunnel create "$TUNNEL_NAME" >/dev/null
  TUNNEL_ID="$(cloudflared tunnel list --output json | python3 -c '
import json,sys
name=sys.argv[1]
for x in json.load(sys.stdin):
    if x.get("name") == name:
        print(x.get("id") or x.get("uuid") or "")
        break
' "$TUNNEL_NAME")"
fi
[ -n "$TUNNEL_ID" ] || { echo 'RED: unable to resolve F-Droid tunnel UUID' >&2; exit 6; }
CRED="$HOME/.cloudflared/${TUNNEL_ID}.json"
test -s "$CRED" || { echo "RED: tunnel credential missing: $CRED" >&2; exit 6; }
chmod 600 "$CRED"
echo "FDROID_TUNNEL_ID=$TUNNEL_ID"

# Create canonical CNAME. If a conflicting old A/AAAA exists, fail closed rather than
# overwrite a live record blindly.
cloudflared tunnel route dns "$TUNNEL_ID" "$FDROID_HOST"
echo 'FDROID_TUNNEL_DNS_ROUTE_GREEN'

cat >"$WORK/config.yml" <<EOF
tunnel: $TUNNEL_ID
credentials-file: /etc/cloudflared/${TUNNEL_ID}.json
protocol: quic
ingress:
  - hostname: $FDROID_HOST
    service: http://127.0.0.1:8080
  - service: http_status:404
EOF

# Transfer only public signed repo data plus this one tunnel runtime credential through
# Google IAP. The Cloudflare account-wide cert.pem never leaves the operator machine.
gcloud compute scp "$WORK/repo.tar.gz" \
  "$INSTANCE:/tmp/kai9000-repo.tar.gz" \
  --project="$PROJECT" --zone="$ZONE" --tunnel-through-iap

gcloud compute scp "$CRED" \
  "$INSTANCE:/tmp/${TUNNEL_ID}.json" \
  --project="$PROJECT" --zone="$ZONE" --tunnel-through-iap

gcloud compute scp "$WORK/config.yml" \
  "$INSTANCE:/tmp/kai9000-cloudflared.yml" \
  --project="$PROJECT" --zone="$ZONE" --tunnel-through-iap

gcloud compute scp "$REPO_ROOT/integrations/google-cloud/nginx-fdroid-origin.conf" \
  "$INSTANCE:/tmp/kai9000-fdroid-nginx.conf" \
  --project="$PROJECT" --zone="$ZONE" --tunnel-through-iap

REMOTE_SCRIPT="$(cat <<'REMOTE'
set -euo pipefail
sudo install -d -m 0700 /etc/cloudflared
sudo install -m 0600 "/tmp/__TUNNEL_ID__.json" "/etc/cloudflared/__TUNNEL_ID__.json"
sudo install -m 0600 /tmp/kai9000-cloudflared.yml /etc/cloudflared/config.yml

sudo install -d -m 0755 /usr/share/keyrings
curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg | sudo tee /usr/share/keyrings/cloudflare-main.gpg >/dev/null
echo 'deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared any main' | sudo tee /etc/apt/sources.list.d/cloudflared.list >/dev/null
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y nginx cloudflared ca-certificates

sudo install -m 0644 /tmp/kai9000-fdroid-nginx.conf /etc/nginx/sites-available/kai9000-fdroid
sudo ln -sfn /etc/nginx/sites-available/kai9000-fdroid /etc/nginx/sites-enabled/kai9000-fdroid
sudo rm -f /etc/nginx/sites-enabled/default

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
INCOMING="/srv/kai9000/fdroid.incoming.$STAMP"
PREVIOUS="/srv/kai9000/fdroid.previous.$STAMP"
sudo mkdir -p "$INCOMING"
sudo tar -xzf /tmp/kai9000-repo.tar.gz -C "$INCOMING"
sudo test -s "$INCOMING/index-v1.jar"
sudo test -s "$INCOMING/index-v1.json"
sudo grep -qi '__REPO_FP__' "$INCOMING/repo-fingerprint-sha256.txt"
if sudo test -e /srv/kai9000/fdroid; then sudo mv /srv/kai9000/fdroid "$PREVIOUS"; fi
sudo mv "$INCOMING" /srv/kai9000/fdroid
sudo chown -R www-data:www-data /srv/kai9000/fdroid

sudo nginx -t
sudo systemctl enable --now nginx
curl -fsS http://127.0.0.1:8080/fdroid/repo/repo-fingerprint-sha256.txt | grep -qi '__REPO_FP__'

sudo cloudflared --config /etc/cloudflared/config.yml tunnel ingress validate
sudo tee /etc/systemd/system/kai9000-cloudflared-fdroid.service >/dev/null <<'UNIT'
[Unit]
Description=KAI9000 F-Droid Cloudflare Tunnel
After=network-online.target nginx.service
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/cloudflared --config /etc/cloudflared/config.yml tunnel run
Restart=on-failure
RestartSec=5s
NoNewPrivileges=true
PrivateTmp=true
ProtectHome=true
ProtectSystem=strict
ReadOnlyPaths=/srv/kai9000/fdroid

[Install]
WantedBy=multi-user.target
UNIT
sudo systemctl daemon-reload
sudo systemctl enable --now kai9000-cloudflared-fdroid.service
sudo systemctl is-active --quiet kai9000-cloudflared-fdroid.service
printf 'ORIGIN_LOCAL_AND_TUNNEL_SERVICE_GREEN\n'
REMOTE
)"
REMOTE_SCRIPT="${REMOTE_SCRIPT//__TUNNEL_ID__/$TUNNEL_ID}"
REMOTE_SCRIPT="${REMOTE_SCRIPT//__REPO_FP__/$EXPECTED_REPO_FP}"

gcloud compute ssh "$INSTANCE" \
  --project="$PROJECT" --zone="$ZONE" --tunnel-through-iap \
  --command="$REMOTE_SCRIPT"

cloudflared tunnel info "$TUNNEL_ID" >/dev/null
echo 'FDROID_TUNNEL_CONTROL_PLANE_GREEN'

PUBLIC_FP=""
for _ in $(seq 1 18); do
  PUBLIC_FP="$(curl -fsSL --max-time 15 "$PUBLIC_URL/repo-fingerprint-sha256.txt" 2>/dev/null | tr -d ':[:space:]' | tr '[:lower:]' '[:upper:]' || true)"
  [ "$PUBLIC_FP" = "$EXPECTED_REPO_FP" ] && break
  sleep 5
done
[ "$PUBLIC_FP" = "$EXPECTED_REPO_FP" ] || {
  echo 'RED: tunnel configured but public F-Droid fingerprint is not reachable yet' >&2
  exit 7
}

curl -fsSL --max-time 30 "$PUBLIC_URL/index-v1.jar" -o "$WORK/public-index-v1.jar"
curl -fsSL --max-time 30 "$PUBLIC_URL/index-v1.json" -o "$WORK/public-index-v1.json"
test -s "$WORK/public-index-v1.jar"
test -s "$WORK/public-index-v1.json"

echo 'FDROID_PUBLISHED'
echo "repo_url=${PUBLIC_URL}/"
echo "repo_fingerprint_sha256=$EXPECTED_REPO_FP"
echo 'origin_public_ip_record=NONE'
echo 'origin_web_ingress=NONE'
echo 'google_admin=IAP_ONLY'
echo 'next_gate=FDROID_IMPORT_VERIFIED then UPGRADE_VERIFIED'
