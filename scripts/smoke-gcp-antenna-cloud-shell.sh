#!/usr/bin/env bash
set -euo pipefail

PROJECT="${GCP_PROJECT_ID:-$(gcloud config get-value project 2>/dev/null || true)}"
INSTANCE="${KAI_GCP_INSTANCE:-}"
ZONE="${GCP_ZONE:-}"

[ -n "$PROJECT" ] || {
  echo 'RED: no active Google Cloud project. In Cloud Shell, run: gcloud config set project YOUR_PROJECT_ID' >&2
  exit 20
}

command -v gcloud >/dev/null || { echo 'RED: gcloud CLI is required' >&2; exit 21; }

echo '=== KAI9000 GOOGLE CLOUD ANTENNA DISCOVERY ==='
echo "project=$PROJECT"

if [ -n "$INSTANCE" ]; then
  if [ -z "$ZONE" ]; then
    mapfile -t matches < <(gcloud compute instances list --project="$PROJECT" \
      --filter="name=($INSTANCE) AND status=RUNNING" \
      --format='value(name,zone.basename())')
    [ "${#matches[@]}" -eq 1 ] || {
      echo "RED: instance '$INSTANCE' did not resolve to exactly one running VM" >&2
      printf '%s\n' "${matches[@]:-}"
      exit 30
    }
    INSTANCE="$(awk '{print $1}' <<<"${matches[0]}")"
    ZONE="$(awk '{print $2}' <<<"${matches[0]}")"
  fi
else
  mapfile -t candidates < <(gcloud compute instances list --project="$PROJECT" \
    --filter='status=RUNNING' \
    --format='value(name,zone.basename())')

  mapfile -t kai_candidates < <(printf '%s\n' "${candidates[@]:-}" | grep -Ei 'kai9000|antenna|debian|ubuntu' || true)
  if [ "${#kai_candidates[@]}" -eq 1 ]; then
    INSTANCE="$(awk '{print $1}' <<<"${kai_candidates[0]}")"
    ZONE="$(awk '{print $2}' <<<"${kai_candidates[0]}")"
  elif [ "${#candidates[@]}" -eq 1 ]; then
    INSTANCE="$(awk '{print $1}' <<<"${candidates[0]}")"
    ZONE="$(awk '{print $2}' <<<"${candidates[0]}")"
  else
    echo 'RED: could not safely auto-select one running VM.' >&2
    echo 'Running VM candidates:' >&2
    printf '  %s\n' "${candidates[@]:-NONE}" >&2
    echo 'Set KAI_GCP_INSTANCE and GCP_ZONE, then rerun.' >&2
    exit 31
  fi
fi

STATUS="$(gcloud compute instances describe "$INSTANCE" --project="$PROJECT" --zone="$ZONE" --format='get(status)')"
MACHINE="$(gcloud compute instances describe "$INSTANCE" --project="$PROJECT" --zone="$ZONE" --format='get(machineType.basename())')"
INTERNAL_IP="$(gcloud compute instances describe "$INSTANCE" --project="$PROJECT" --zone="$ZONE" --format='get(networkInterfaces[0].networkIP)')"
EXTERNAL_V4="$(gcloud compute instances describe "$INSTANCE" --project="$PROJECT" --zone="$ZONE" --format='get(networkInterfaces[0].accessConfigs[0].natIP)')"
EXTERNAL_V6="$(gcloud compute instances describe "$INSTANCE" --project="$PROJECT" --zone="$ZONE" --format='get(networkInterfaces[0].ipv6AccessConfigs[0].externalIpv6)')"

echo "instance=$INSTANCE"
echo "zone=$ZONE"
echo "status=$STATUS"
echo "machine=$MACHINE"
echo "internal_ipv4=$INTERNAL_IP"
echo "external_ipv4=${EXTERNAL_V4:-NONE}"
echo "external_ipv6=${EXTERNAL_V6:+PRESENT}"
[ "$STATUS" = RUNNING ] || { echo "RED: VM is $STATUS" >&2; exit 32; }

echo
echo '=== IAP GUEST SMOKE ==='

gcloud compute ssh "$INSTANCE" \
  --project="$PROJECT" \
  --zone="$ZONE" \
  --tunnel-through-iap \
  --quiet \
  --command='bash -s' <<'REMOTE'
set -uo pipefail
fail=0

green() { printf 'GREEN %-28s %s\n' "$1" "${2:-}"; }
yellow() { printf 'YELLOW %-27s %s\n' "$1" "${2:-}"; }
red() { printf 'RED %-30s %s\n' "$1" "${2:-}"; fail=1; }

echo '=== KAI9000 REMOTE ANTENNA SMOKE ==='
hostnamectl --static 2>/dev/null || hostname
uname -a
uptime

if [ -r /etc/os-release ]; then
  . /etc/os-release
  echo "guest_os_id=$ID guest_version_id=$VERSION_ID guest_pretty_name=$PRETTY_NAME"
  case "$ID:$VERSION_ID" in
    debian:12|debian:12.*)
      green OS_VERSION "$PRETTY_NAME"
      ;;
    ubuntu:26.04|ubuntu:26.04.*)
      green OS_VERSION "$PRETTY_NAME"
      ;;
    *)
      yellow OS_VERSION "unvalidated but not fatal: $PRETTY_NAME"
      ;;
  esac
else
  yellow OS_RELEASE '/etc/os-release missing'
fi

echo '--- resources ---'
df -h /
free -m || true

echo '--- network ---'
ip -br addr || true
ip -6 route || true

echo '--- listeners ---'
ss -ltnp || true

if systemctl is-active --quiet nginx 2>/dev/null; then
  green NGINX_SERVICE active
else
  red NGINX_SERVICE inactive_or_missing
fi

if curl -fsS --max-time 5 http://127.0.0.1:8080/ >/dev/null 2>&1; then
  green FDROID_ORIGIN_HTTP '127.0.0.1:8080 responds'
else
  red FDROID_ORIGIN_HTTP '127.0.0.1:8080 not responding'
fi

if [ -s /srv/kai9000/fdroid/repo/index-v1.jar ] || [ -s /srv/kai9000/fdroid/index-v1.jar ]; then
  green FDROID_INDEX present
else
  yellow FDROID_INDEX 'not staged on origin yet'
fi

if systemctl is-active --quiet cloudflared 2>/dev/null; then
  green CLOUDFLARED_SERVICE active
elif pgrep -x cloudflared >/dev/null 2>&1; then
  green CLOUDFLARED_PROCESS running
else
  yellow CLOUDFLARED_SERVICE 'not active yet'
fi

api_ok=0
for port in 8789 8791 8000; do
  if body="$(curl -fsS --max-time 5 "http://127.0.0.1:${port}/health" 2>/dev/null)"; then
    green ANTENNA_HEALTH "port=$port body=${body:0:180}"
    api_ok=1
    break
  fi
done
[ "$api_ok" -eq 1 ] || yellow ANTENNA_HEALTH 'no /health response on 8789, 8791, or 8000'

if [ "$fail" -ne 0 ]; then
  echo 'REMOTE_ANTENNA_SMOKE_RED'
  exit 50
fi

echo 'REMOTE_ANTENNA_SMOKE_GREEN'
REMOTE
