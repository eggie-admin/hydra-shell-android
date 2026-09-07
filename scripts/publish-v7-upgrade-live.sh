#!/usr/bin/env bash
set -euo pipefail
umask 077

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT="${GCP_PROJECT:-}"
ZONE="${GCP_ZONE:-us-central1-a}"
INSTANCE="${KAI_GCP_INSTANCE:-kai9000-free}"
TUNNEL_NAME="${CF_FDROID_TUNNEL_NAME:-kai9000-fdroid-origin}"
HOST="fdroid.eggiebagelface.art"
BASE="https://${HOST}/fdroid/repo"
BUNDLE="${KAI_SIGNED_BUNDLE:-$HOME/storage/downloads/KAI9000_FDROID_SIGNED_V7_20260906.zip}"
EXPECTED_SHA="${KAI_EXPECTED_BUNDLE_SHA256:-}"
APK_FP="A5E9364D5C21A119FE1D17FD39EE7BAE8192A872CE58A3E7A865248E0B070407"
REPO_FP="BFB900A9EC913D35C22F1DC3DE7B152D1AF5CA11B7B07E5FAFDD06B44811F66D"
PACKAGE="art.eggiebagelface.videoforge.dev"

while (($#)); do
  case "$1" in
    --bundle) BUNDLE="${2:-}"; shift 2 ;;
    --bundle-sha256) EXPECTED_SHA="${2:-}"; shift 2 ;;
    --project) PROJECT="${2:-}"; shift 2 ;;
    *) echo "usage: $0 [--bundle PATH] [--bundle-sha256 SHA256] [--project ID]" >&2; exit 2 ;;
  esac
done

[ -s "$BUNDLE" ] || { echo "RED: signed v7 bundle absent: $BUNDLE" >&2; exit 2; }
[ -n "$EXPECTED_SHA" ] || { echo 'RED: pass --bundle-sha256 or KAI_EXPECTED_BUNDLE_SHA256' >&2; exit 2; }
for cmd in gcloud cloudflared python3 sha256sum unzip tar curl; do
  command -v "$cmd" >/dev/null || { echo "RED: missing command: $cmd" >&2; exit 3; }
done

echo "$EXPECTED_SHA  $BUNDLE" | sha256sum -c --strict
WORK="$(mktemp -d "${TMPDIR:-/tmp}/kai9000-v7-publish.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT INT TERM
mkdir -p "$WORK/signed"
unzip -q "$BUNDLE" -d "$WORK/signed"

python3 - "$WORK/signed/FINAL_FORM_SIGNED_STATUS.json" "$APK_FP" "$REPO_FP" <<'PY'
import json, sys
p, apk, repo = sys.argv[1:]
s=json.load(open(p, encoding='utf-8'))
assert s.get('state') == 'FDROID_SIGNED'
assert s.get('version_code') == 7
assert s.get('apk_count', 0) >= 2
assert s.get('apk_signer_sha256','').upper() == apk
assert s.get('repo_fingerprint_sha256','').upper() == repo
assert s.get('all_apks_persistent_identity_verified') is True
assert s.get('published') is False
print('SIGNED_V7_UPGRADE_EVIDENCE_GREEN')
PY

test -s "$WORK/signed/repo/${PACKAGE}_6.apk"
test -s "$WORK/signed/repo/${PACKAGE}_7.apk"
test -s "$WORK/signed/repo/index-v1.jar"
test -s "$WORK/signed/repo/index-v1.json"
grep -qi "$REPO_FP" "$WORK/signed/repo/repo-fingerprint-sha256.txt"

ACTIVE="$(gcloud auth list --filter=status:ACTIVE --format='value(account)' 2>/dev/null | head -n1 || true)"
[ -n "$ACTIVE" ] || bash "$ROOT/integrations/google-cloud/bootstrap-oauth.sh" login-remote
if [ ! -s "$HOME/.cloudflared/cert.pem" ]; then
  bash "$ROOT/integrations/cloudflare/bootstrap-oauth.sh" tunnel-login
fi

if [ -z "$PROJECT" ]; then
  PROJECT="$(gcloud config get-value project 2>/dev/null || true)"
fi
if [ -z "$PROJECT" ] || [ "$PROJECT" = '(unset)' ]; then
  mapfile -t PROJECTS < <(gcloud projects list --format='value(projectId)' | sed '/^$/d')
  [ "${#PROJECTS[@]}" -eq 1 ] || { echo 'RED: select Google project with --project' >&2; exit 4; }
  PROJECT="${PROJECTS[0]}"
fi

gcloud compute instances describe "$INSTANCE" --project="$PROJECT" --zone="$ZONE" >/dev/null
TUNNEL_ID="$(cloudflared tunnel list --output json | python3 -c '
import json,sys
name=sys.argv[1]
for x in json.load(sys.stdin):
    if x.get("name") == name:
        print(x.get("id") or x.get("uuid") or ""); break
' "$TUNNEL_NAME")"
[ -n "$TUNNEL_ID" ] || { echo 'RED: existing F-Droid tunnel not found; publish v6 first' >&2; exit 4; }
cloudflared tunnel info "$TUNNEL_ID" >/dev/null

tar -C "$WORK/signed/repo" -czf "$WORK/repo-v7.tar.gz" .
gcloud compute scp "$WORK/repo-v7.tar.gz" "$INSTANCE:/tmp/kai9000-repo-v7.tar.gz" \
  --project="$PROJECT" --zone="$ZONE" --tunnel-through-iap

REMOTE="$(cat <<'REMOTE'
set -euo pipefail
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
IN="/srv/kai9000/fdroid.incoming.v7.$STAMP"
OLD="/srv/kai9000/fdroid.previous.v6.$STAMP"
sudo mkdir -p "$IN"
sudo tar -xzf /tmp/kai9000-repo-v7.tar.gz -C "$IN"
sudo test -s "$IN/__PACKAGE___6.apk"
sudo test -s "$IN/__PACKAGE___7.apk"
sudo grep -qi '__REPO_FP__' "$IN/repo-fingerprint-sha256.txt"
if sudo test -e /srv/kai9000/fdroid; then sudo mv /srv/kai9000/fdroid "$OLD"; fi
sudo mv "$IN" /srv/kai9000/fdroid
sudo chown -R www-data:www-data /srv/kai9000/fdroid
curl -fsS http://127.0.0.1:8080/fdroid/repo/repo-fingerprint-sha256.txt | grep -qi '__REPO_FP__'
sudo systemctl is-active --quiet kai9000-cloudflared-fdroid.service
printf 'V7_ORIGIN_ATOMIC_SWAP_GREEN\n'
REMOTE
)"
REMOTE="${REMOTE//__PACKAGE__/$PACKAGE}"
REMOTE="${REMOTE//__REPO_FP__/$REPO_FP}"
gcloud compute ssh "$INSTANCE" --project="$PROJECT" --zone="$ZONE" --tunnel-through-iap --command="$REMOTE"

for _ in $(seq 1 18); do
  if curl -fsSL --max-time 15 "$BASE/index-v1.json" -o "$WORK/public-index.json" 2>/dev/null; then
    if python3 - "$WORK/public-index.json" "$PACKAGE" "$APK_FP" <<'PY'
import json,sys
p,pkg,fp=sys.argv[1:]
j=json.load(open(p,encoding='utf-8'))
versions=j.get('packages',{}).get(pkg,[])
v7=[x for x in versions if int(x.get('versionCode',0))==7]
assert v7, 'versionCode 7 absent'
assert (v7[0].get('signer') or '').upper()==fp or (v7[0].get('sig') or '').upper()==fp
PY
    then break; fi
  fi
  sleep 5
done

PUBLIC_FP="$(curl -fsSL --max-time 20 "$BASE/repo-fingerprint-sha256.txt" | tr -d ':[:space:]' | tr '[:lower:]' '[:upper:]')"
[ "$PUBLIC_FP" = "$REPO_FP" ] || { echo 'RED: public repo fingerprint mismatch' >&2; exit 7; }
python3 - "$WORK/public-index.json" "$PACKAGE" <<'PY'
import json,sys
j=json.load(open(sys.argv[1],encoding='utf-8'))
vs=j.get('packages',{}).get(sys.argv[2],[])
assert any(int(x.get('versionCode',0))==6 for x in vs)
assert any(int(x.get('versionCode',0))==7 for x in vs)
print('PUBLIC_V6_V7_INDEX_GREEN')
PY

echo 'FDROID_V7_PUBLISHED'
echo "repo_url=${BASE}/"
echo 'next_gate=refresh F-Droid on Samsung, install update, then run scripts/final-form-device-verify.sh upgrade-check'
