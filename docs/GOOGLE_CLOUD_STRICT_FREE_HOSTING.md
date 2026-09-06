# KAI 9000 Google Cloud Strict-Free Hosting

Status: testing doctrine for `testing/luhm-os-android`.

## Mission

Host the public KAI 9000 / Project Hydra origin on the Google Cloud Compute Engine Free Tier while keeping the intended monthly infrastructure cost at `$0`.

```text
AIRSHIP KAI9000
WARP GIT
WHITE_MAGIC GOOGLE_CLOUD
PUBLIC_IDENTITY eggiebagelface.art

COMPUTE_ORIGIN Google Compute Engine
AUTHORITATIVE_DNS Cloudflare Free
```

## Why DNS stays outside Google Cloud

Google Cloud DNS does not have a free tier. A managed zone is billable even with minimal traffic, so Cloud DNS is prohibited in `STRICT_FREE` mode.

`eggiebagelface.art` therefore remains on a free authoritative DNS provider. The current KAI doctrine uses Cloudflare Free for the public DNS/proxy layer.

This means **Google Cloud hosts the website/F-Droid origin**, while **Cloudflare hosts the authoritative DNS zone**.

## Free Compute contract

KAI pins the Compute Engine lane to the documented Free Tier envelope:

- one non-preemptible `e2-micro` equivalent per month;
- region restricted to `us-west1`, `us-central1`, or `us-east1`;
- `30 GB` `pd-standard` boot disk maximum;
- no GPU or TPU;
- conservative outbound-data guard of `1 GB/month` for this VM lane.

Default KAI coordinates:

```text
region = us-central1
zone   = us-central1-a
machine = e2-micro
boot_disk = pd-standard:30GB
```

Free Tier eligibility and limits can change. Recheck Google's current Free Tier page before production provisioning or after material changes to the billing account.

## IPv6-only public origin

Google currently bills external IPv4 addresses attached to standard VMs. External IPv6 addresses assigned to VMs are not charged.

Therefore strict-free doctrine requires:

```text
external_ipv4 = FALSE
external_ipv6 = TRUE
```

The VM uses an external-IPv6-capable subnet. Cloudflare receives proxied `AAAA` records for public web traffic.

Cloudflare's proxy then remains the visitor-facing edge. Visitors can use ordinary IPv4 or IPv6 connectivity while the Google origin itself avoids a billable VM external IPv4 address.

## DNS intent

After provisioning returns the VM's real external IPv6 address, apply:

```text
AAAA  eggiebagelface.art         -> <GCP_VM_EXTERNAL_IPV6>  proxied
AAAA  fdroid.eggiebagelface.art  -> <GCP_VM_EXTERNAL_IPV6>  proxied
CNAME www.eggiebagelface.art     -> eggiebagelface.art      proxied
```

Do not commit a fake origin address. The template lives at:

`integrations/cloudflare/eggiebagelface-art-strict-free-dns.template.json`

## Provisioning

Provisioner:

`integrations/google-cloud/provision-strict-free-vm.sh`

Required environment:

```text
GCP_PROJECT=<google-cloud-project-id>
```

Optional overrides are accepted only when they remain inside strict-free doctrine:

```text
GCP_REGION=us-central1
GCP_ZONE=us-central1-a
KAI_GCP_INSTANCE=kai9000-free
```

The provisioner:

1. enables Compute Engine;
2. creates a custom VPC and external-IPv6-capable subnet;
3. permits inbound HTTP/HTTPS over IPv6;
4. creates one `e2-micro` Debian VM;
5. uses `pd-standard` 30 GB;
6. explicitly requests no external IPv4;
7. verifies machine, disk, IPv4 absence, and external IPv6 after creation;
8. prints the exact Cloudflare DNS intent.

It intentionally does not create Cloud DNS, Cloud NAT, a load balancer, GPU/TPU resources, or an external IPv4 address.

## Authentication

GitHub automation should use Google Cloud Workload Identity Federation (OIDC). Do not commit a service-account JSON key.

Existing WIF template:

`integrations/google-cloud/github-wif.template.yml`

The provisioning identity must receive only the Google Cloud permissions required for the KAI project and its declared Compute resources.

## Cost doctrine

`STRICT_FREE` is an architectural target, not a promise that Google can never generate a charge.

Important constraints:

- the Free Tier is usage-limited and subject to change;
- egress above the applicable free allowance can become billable;
- using an external IPv4 becomes billable;
- switching machine, disk, region, or adding other services can become billable;
- ordinary budget alerts are not a universal hard project-wide billing cap;
- current spend-cap functionality does not provide a general hard cap for persistent Compute Engine resources.

Required operational discipline:

```text
NO IPV4
NO CLOUD DNS
NO CLOUD NAT
NO LOAD BALANCER
NO GPU / TPU
NO DISK > 30GB
NO MACHINE != e2-micro
NO REGION OUTSIDE FREE-TIER REGIONS
EGRESS < 1GB / MONTH FOR KAI VM GUARD
```

Enable billing notifications and inspect actual billing reports even when expected cost is `$0`.

## KAI MAGE compiler

```text
CAST WHITE_GATE
  => GitHub OIDC -> Google WIF

CAST FREE_VM
  => validate strict-free manifest
  => provision e2-micro IPv6-only public origin
  => verify no external IPv4

RAISE BANNER eggiebagelface.art
  => apply proxied Cloudflare AAAA record to verified VM IPv6

OPEN BLACK_MAGIC_PORT fdroid.eggiebagelface.art
  => apply proxied Cloudflare AAAA record to the same verified origin

CAST ULTIMA
  => requires live HTTPS + DNS + cost guard + F-Droid evidence
```

## Green states

```text
WHITE_MAGIC_STRICT_FREE_STAGED
WHITE_MAGIC_VM_PROVISIONED
DNS_READY
HTTPS_GREEN
FDROID_PUBLISHED
FINAL_FORM_GREEN
```

Do not report `WHITE_MAGIC_VM_PROVISIONED` until the Google API actually returns the VM and the post-create cost invariants pass.
