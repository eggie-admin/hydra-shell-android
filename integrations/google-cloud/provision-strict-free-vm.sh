#!/usr/bin/env bash
set -euo pipefail

: "${GCP_PROJECT:?Set GCP_PROJECT to the Google Cloud project ID}"

REGION="${GCP_REGION:-us-central1}"
ZONE="${GCP_ZONE:-us-central1-a}"
INSTANCE="${KAI_GCP_INSTANCE:-kai9000-free}"
NETWORK="${KAI_GCP_NETWORK:-kai9000-free}"
SUBNET="${KAI_GCP_SUBNET:-kai9000-free-v6}"

case "$REGION" in
  us-west1|us-central1|us-east1) ;;
  *) echo "RED: $REGION is outside the Compute Engine e2-micro Free Tier regions" >&2; exit 2 ;;
esac

case "$ZONE" in
  "$REGION"-*) ;;
  *) echo "RED: zone $ZONE is not inside region $REGION" >&2; exit 2 ;;
esac

command -v gcloud >/dev/null || { echo 'RED: gcloud CLI is required' >&2; exit 2; }

gcloud config set project "$GCP_PROJECT" >/dev/null

echo '=== KAI 9000 WHITE MAGIC STRICT-FREE PREFLIGHT ==='
echo "project=$GCP_PROJECT region=$REGION zone=$ZONE instance=$INSTANCE"
echo 'machine=e2-micro disk=pd-standard:30GB external_ipv4=FALSE external_ipv6=TRUE'
echo 'Cloud DNS is intentionally NOT created in strict-free mode.'

# Enable only the API needed for this lane.
gcloud services enable compute.googleapis.com --project="$GCP_PROJECT"

if ! gcloud compute networks describe "$NETWORK" --project="$GCP_PROJECT" >/dev/null 2>&1; then
  gcloud compute networks create "$NETWORK" \
    --project="$GCP_PROJECT" \
    --subnet-mode=custom
fi

if ! gcloud compute networks subnets describe "$SUBNET" --region="$REGION" --project="$GCP_PROJECT" >/dev/null 2>&1; then
  gcloud compute networks subnets create "$SUBNET" \
    --project="$GCP_PROJECT" \
    --network="$NETWORK" \
    --region="$REGION" \
    --range=10.42.0.0/24 \
    --stack-type=IPV4_IPV6 \
    --ipv6-access-type=EXTERNAL
fi

if ! gcloud compute firewall-rules describe kai9000-web-v6 --project="$GCP_PROJECT" >/dev/null 2>&1; then
  gcloud compute firewall-rules create kai9000-web-v6 \
    --project="$GCP_PROJECT" \
    --network="$NETWORK" \
    --direction=INGRESS \
    --allow=tcp:80,tcp:443 \
    --source-ranges='::/0' \
    --target-tags=kai9000-web
fi

if gcloud compute instances describe "$INSTANCE" --zone="$ZONE" --project="$GCP_PROJECT" >/dev/null 2>&1; then
  echo "YELLOW: instance $INSTANCE already exists; skipping create"
else
  gcloud compute instances create "$INSTANCE" \
    --project="$GCP_PROJECT" \
    --zone="$ZONE" \
    --machine-type=e2-micro \
    --provisioning-model=STANDARD \
    --image-family=debian-12 \
    --image-project=debian-cloud \
    --boot-disk-type=pd-standard \
    --boot-disk-size=30GB \
    --subnet="$SUBNET" \
    --stack-type=IPV4_IPV6 \
    --ipv6-network-tier=PREMIUM \
    --no-address \
    --tags=kai9000-web \
    --metadata=startup-script='#!/bin/sh
set -eu
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y nginx
cat >/var/www/html/index.html <<EOF
<!doctype html><html><head><meta charset="utf-8"><title>KAI 9000</title></head><body><h1>KAI 9000</h1><p>LuHm OS / Project Hydra testing origin.</p><p>Public identity: eggiebagelface.art</p></body></html>
EOF
systemctl enable --now nginx'
fi

MACHINE="$(gcloud compute instances describe "$INSTANCE" --zone="$ZONE" --project="$GCP_PROJECT" --format='get(machineType.basename())')"
DISK="$(gcloud compute disks describe "$INSTANCE" --zone="$ZONE" --project="$GCP_PROJECT" --format='get(type.basename(),sizeGb)' | tr ';' ' ')"
IPV4="$(gcloud compute instances describe "$INSTANCE" --zone="$ZONE" --project="$GCP_PROJECT" --format='get(networkInterfaces[0].accessConfigs[0].natIP)')"
IPV6="$(gcloud compute instances describe "$INSTANCE" --zone="$ZONE" --project="$GCP_PROJECT" --format='get(networkInterfaces[0].ipv6AccessConfigs[0].externalIpv6)')"

[ "$MACHINE" = e2-micro ] || { echo "RED: machine type drifted to $MACHINE" >&2; exit 3; }
case "$DISK" in pd-standard*30*) ;; *) echo "RED: disk drifted from pd-standard 30GB: $DISK" >&2; exit 3 ;; esac
[ -z "$IPV4" ] || { echo "RED: external IPv4 was attached: $IPV4" >&2; exit 3; }
[ -n "$IPV6" ] || { echo 'RED: no external IPv6 found' >&2; exit 3; }

cat <<EOF
WHITE_MAGIC_STRICT_FREE_STAGED
VM IPv6: $IPV6

Cloudflare DNS intent (apply separately):
  AAAA eggiebagelface.art        -> $IPV6  proxied=true
  AAAA fdroid.eggiebagelface.art -> $IPV6  proxied=true
  CNAME www.eggiebagelface.art   -> eggiebagelface.art proxied=true

No Google Cloud DNS zone was created.
No external IPv4 was attached.
EOF
