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

echo '=== KAI 9000 WHITE MAGIC STRICT-FREE / TUNNEL PREFLIGHT ==='
echo "project=$GCP_PROJECT region=$REGION zone=$ZONE instance=$INSTANCE"
echo 'machine=e2-micro disk=pd-standard:30GB external_ipv4=FALSE external_ipv6=EGRESS_ONLY'
echo 'public_web_ingress=FALSE public_ssh=FALSE admin=IAP_SSH fdroid=Cloudflare_Tunnel'
echo 'Cloud DNS is intentionally NOT created in strict-free mode.'

# Compute is required for the VM. IAP is the only inbound administrative lane.
gcloud services enable compute.googleapis.com iap.googleapis.com --project="$GCP_PROJECT"

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

# Remove the superseded public-web rule if an earlier doctrine created it.
if gcloud compute firewall-rules describe kai9000-web-v6 --project="$GCP_PROJECT" >/dev/null 2>&1; then
  echo 'Removing legacy ::/0 web ingress rule kai9000-web-v6'
  gcloud compute firewall-rules delete kai9000-web-v6 --project="$GCP_PROJECT" --quiet
fi

# IAP is the only inbound administrative path. No direct public SSH rule.
if ! gcloud compute firewall-rules describe kai9000-iap-ssh --project="$GCP_PROJECT" >/dev/null 2>&1; then
  gcloud compute firewall-rules create kai9000-iap-ssh \
    --project="$GCP_PROJECT" \
    --network="$NETWORK" \
    --direction=INGRESS \
    --allow=tcp:22 \
    --source-ranges=35.235.240.0/20 \
    --target-tags=kai9000-iap
fi

if gcloud compute instances describe "$INSTANCE" --zone="$ZONE" --project="$GCP_PROJECT" >/dev/null 2>&1; then
  echo "YELLOW: instance $INSTANCE already exists; reconciling tags"
  gcloud compute instances add-tags "$INSTANCE" \
    --project="$GCP_PROJECT" \
    --zone="$ZONE" \
    --tags=kai9000-iap >/dev/null
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
    --tags=kai9000-iap \
    --metadata=startup-script='#!/bin/sh
set -eu
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y nginx curl ca-certificates
mkdir -p /srv/kai9000/fdroid
chown -R www-data:www-data /srv/kai9000/fdroid
rm -f /etc/nginx/sites-enabled/default
cat >/etc/nginx/sites-available/kai9000-fdroid <<"EOF"
server {
    listen 127.0.0.1:8080;
    server_name localhost;
    root /srv/kai9000/fdroid;
    autoindex off;
    location = / { return 302 /fdroid/repo/; }
    location /fdroid/repo/ { alias /srv/kai9000/fdroid/; try_files $uri =404; }
}
EOF
ln -sf /etc/nginx/sites-available/kai9000-fdroid /etc/nginx/sites-enabled/kai9000-fdroid
nginx -t
systemctl enable --now nginx'
fi

MACHINE="$(gcloud compute instances describe "$INSTANCE" --zone="$ZONE" --project="$GCP_PROJECT" --format='get(machineType.basename())')"
DISK="$(gcloud compute disks describe "$INSTANCE" --zone="$ZONE" --project="$GCP_PROJECT" --format='get(type.basename(),sizeGb)' | tr ';' ' ')"
IPV4="$(gcloud compute instances describe "$INSTANCE" --zone="$ZONE" --project="$GCP_PROJECT" --format='get(networkInterfaces[0].accessConfigs[0].natIP)')"
IPV6="$(gcloud compute instances describe "$INSTANCE" --zone="$ZONE" --project="$GCP_PROJECT" --format='get(networkInterfaces[0].ipv6AccessConfigs[0].externalIpv6)')"

[ "$MACHINE" = e2-micro ] || { echo "RED: machine type drifted to $MACHINE" >&2; exit 3; }
case "$DISK" in pd-standard*30*) ;; *) echo "RED: disk drifted from pd-standard 30GB: $DISK" >&2; exit 3 ;; esac
[ -z "$IPV4" ] || { echo "RED: external IPv4 was attached: $IPV4" >&2; exit 3; }
[ -n "$IPV6" ] || { echo 'RED: no external IPv6 found for outbound Internet/Tunnel connectivity' >&2; exit 3; }

echo '=== IAP PROBE ==='
gcloud compute ssh "$INSTANCE" \
  --project="$GCP_PROJECT" \
  --zone="$ZONE" \
  --tunnel-through-iap \
  --command='printf "GOOGLE_IAP_SSH_GREEN\n"; ss -ltn | grep -q "127.0.0.1:8080" && printf "LOCAL_NGINX_GREEN\n"'

cat <<EOF
WHITE_MAGIC_STRICT_FREE_TUNNEL_READY
VM IPv6 exists for outbound connectivity only: $IPV6
Public DNS MUST NOT contain this origin IPv6.

Canonical ingress:
  fdroid.eggiebagelface.art CNAME -> <FDROID_TUNNEL_ID>.cfargotunnel.com
  public web ports on VM -> NONE
  public SSH on VM -> NONE
  operator SSH -> Google IAP only

No Google Cloud DNS zone was created.
No external IPv4 was attached.
EOF
