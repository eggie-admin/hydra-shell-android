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
PHASE="${KAI_PUBLICATION_PHASE:-baseline}"
BUNDLE="${KAI_SIGNED_BUNDLE:-}"
EXPECTED_APK_SIGNER="A5E9364D5C21A119FE1D17FD39EE7BAE8192A872CE58A3E7A865248E0B070407"
EXPECTED_REPO_FP="BFB900A9EC913D35C22F1DC3DE7B152D1AF5CA11B7B07E5FAFDD06B44811F66D"

BASELINE_NAME="KAI9000_FDROID_SIGNED_BASELINE_V6_20260907.zip"
BASELINE_SHA="703ba08ca4c030c5cf0a553ece8da8e910c3b48549f10bfe02b9feb4c938547d"
BASELINE_STATUS="FINAL_FORM_BASELINE_V6_STATUS.json"
BASELINE_STATE="FDROID_SIGNED_BASELINE_V6_READY"

UPGRADE_NAME="KAI9000_FDROID_SIGNED_V6_V7_20260907.zip"
UPGRADE_SHA="6cb100f525229e5d6445aa8f2dfb5f39b8895073efb278fc39f609cc64799b7d"
UPGRADE_STATUS="FINAL_FORM_SIGNED_V6_V7_STATUS.json"
UPGRADE_STATE="FDROID_SIGNED_V6_V7_READY"

usage() {
  cat <<EOF
usage: $0 [--phase baseline|upgrade] [--bundle PATH] [--project ID]

The cast self-bootstraps human OAuth when required:
  Cloudflare: cloudflared tunnel login
  Google:     gcloud auth login --no-launch-browser

Google project selection order:
  1. --project
  2. GCP_PROJECT
  3. active gcloud configured project
  4. the only project visible to the active Google identity

Default publication sequence:
  baseline -> $HOME/storage/downloads/$BASELINE_NAME
  upgrade  -> $HOME/storage/downloads/$UPGRADE_NAME
EOF
}

while (($#)); do
  case "$1" in
    --phase) PHASE="${2:-}"; shift 2 ;;
    --bundle) BUNDLE="${2:-}"; shift 2 ;;
    --project) PROJECT="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

case "$PHASE" in
  baseline)
    EXPECTED_BUNDLE_SHA256="$BASELINE_SHA"
    STATUS_FILE="$BASELINE_STATUS"
    EXPECTED_STATE="$BASELINE_STATE"
    EXPECTED_VERSION_CODE=6
    DEFAULT_BUNDLE="$HOME/storage/downloads/$BASELINE_NAME"
    ;;
  upgrade)
    EXPECTED_BUNDLE_SHA256="$UPGRADE_SHA"
    STATUS_FILE="$UPGRADE_STATUS"
    EXPECTED_STATE="$UPGRADE_STATE"
    EXPECTED_VERSION_CODE=7
    DEFAULT_BUNDLE="$HOME/storage/downloads/$UPGRADE_NAME"
    ;;
  *)
    echo "RED: --phase must be baseline or upgrade" >&2
    exit 2
    ;;
esac

BUNDLE="${BUNDLE:-$DEFAULT_BUNDLE}"
[ -s "$BUNDLE" ] || { echo "RED: signed $PHASE bundle not found: $BUNDLE" >&2; exit 2; }

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
  echo "RED: signed $PHASE bundle SHA-256 mismatch" >&2
  exit 5
}
echo "SIGNED_BUNDLE_SHA256_GREEN phase=$PHASE"

WORK="$(mktemp -d "${TMPDIR:-/tmp}/kai9000-live.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT INT TERM
unzip -q "$BUNDLE" -d "$WORK/signed"

test -s "$WORK/signed/$STATUS_FILE"
test -d "$WORK/signed/repo"
python3 - "$WORK/signed/$STATUS_FILE" "$PHASE" "$EXPECTED_STATE" "$EXPECTED_VERSION_CODE" "$EXPECTED_APK_SIGNER" "$EXPECTED_REPO_FP" <<'PY'
import json, sys
p, phase, state, expected_code, apk, repo = sys.argv[1:]
s = json.load(open(p, encoding='utf-8'))
assert s.get('state') == state
assert s.get('signed_repo') is True
assert s.get('apk_signer_sha256', '').upper() == apk
assert s.get('repo_fingerprint_sha256', '').upper() == repo
code = int(expected_code)
if phase == 'baseline':
    assert int(s.get('version_code')) == code
else:
    assert int(s.get('latest_version_code')) == code
print('PERSISTENT_SIGNED_EVIDENCE_GREEN')
PY

test -s "$WORK/signed/repo/index-v1.jar"
test -s "$WORK/signed/repo/index-v1.json"
test -s "$WORK/signed/repo/repo-fingerprint-sha256.txt"
grep -qi "$EXPECTED_REPO_FP" "$WORK/signed/repo/repo-fingerprint-sha256.txt"
python3 - "$WORK/signed/repo/index-v1.json" "$PHASE" <<'PY'
import json, sys
idx=json.load(open(sys.argv[1], encoding='utf-8'))
vs=idx['packages']['art.eggiebagelface.videoforge.dev']
codes=sorted(int(v['versionCode']) for v in vs)
if sys.argv[2] == 'baseline':
    assert codes == [6], codes
else:
    assert codes == [6,7], codes
print('LOCAL_INDEX_PHASE_GREEN', codes)
PY

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

if [ "$PHASE" = baseline ]; then
  if cloudflared tunnel route dns "$TUNNEL_ID" "$FDROID_HOST"; then
    echo 'FDROID_TUNNEL_DNS_ROUTE_GREEN'
  else
    echo 'YELLOW: DNS route create returned non-zero; public fingerprint proof will decide whether an existing route is valid' >&2
  fi
else
  echo 'FDROID_TUNNEL_DNS_ROUTE_REUSED'
fi

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
for _ in $(seq 1 24); do
  PUBLIC_FP="$(curl -fsSL --max-time 15 "$PUBLIC_URL/repo-fingerprint-sha256.txt" 2>/dev/null | tr -d ':[:space:]' | tr '[:lower:]' '[:upper:]' || true)"
  [ "$PUBLIC_FP" = "$EXPECTED_REPO_FP" ] && break
  sleep 5
done
[ "$PUBLIC_FP" = "$EXPECTED_REPO_FP" ] || {
  echo 'RED: tunnel configured but public F-Droid fingerprint is not reachable yet' >&2
  exit 7
}

curl -fsSL --max-time 30 "$PUBLIC_URL/index-v1.jar" -o "$WORK/public-index-v1.jar"
PUBLIC_INDEX_GREEN=0
for _ in $(seq 1 24); do
  if curl -fsSL --max-time 30 "$PUBLIC_URL/index-v1.json" -o "$WORK/public-index-v1.json"; then
    if python3 - "$WORK/public-index-v1.json" "$PHASE" <<'PY'
import json, sys
idx=json.load(open(sys.argv[1], encoding='utf-8'))
codes=sorted(int(v['versionCode']) for v in idx['packages']['art.eggiebagelface.videoforge.dev'])
expected=[6] if sys.argv[2]=='baseline' else [6,7]
assert codes == expected, (codes, expected)
print('PUBLIC_INDEX_PHASE_GREEN', codes)
PY
    then
      PUBLIC_INDEX_GREEN=1
      break
    fi
  fi
  sleep 5
done
[ "$PUBLIC_INDEX_GREEN" -eq 1 ] || { echo "RED: public index did not converge to $PHASE phase" >&2; exit 8; }
test -s "$WORK/public-index-v1.jar"
test -s "$WORK/public-index-v1.json"

echo 'FDROID_PUBLISHED'
echo "publication_phase=$PHASE"
echo "repo_url=${PUBLIC_URL}/"
echo "repo_fingerprint_sha256=$EXPECTED_REPO_FP"
echo 'origin_public_ip_record=NONE'
echo 'origin_web_ingress=NONE'
echo 'google_admin=IAP_ONLY'
if [ "$PHASE" = baseline ]; then
  echo 'FDROID_BASELINE_V6_PUBLISHED'
  echo 'next_gate=FDROID_IMPORT_VERIFIED with installed versionCode 6'
else
  echo 'FDROID_UPGRADE_V7_PUBLISHED'
  echo 'next_gate=UPGRADE_VERIFIED with installed versionCode 7'
fi
