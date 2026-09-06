# Cloudflare FQDN / DNS / TLS Doctrine v2

Date: 2026-09-06
Zone: `eggiebagelface.art`

This is the canonical Cloudflare network split for KAI 9000 publication.

## FQDN map

| FQDN | Role | Cloudflare route | Origin exposure |
|---|---|---|---|
| `eggiebagelface.art` | Coming-soon/public site | Cloudflare Workers Static Assets custom domain | none |
| `www.eggiebagelface.art` | public alias | proxied CNAME to apex | none |
| `fdroid.eggiebagelface.art` | signed F-Droid repository | proxied AAAA to Google IPv6 origin | IPv6 only, no public A |
| `admin.eggiebagelface.art` | protected cockpit | proxied CNAME to `<CF_TUNNEL_ID>.cfargotunnel.com` | none |
| `lum.eggiebagelface.lan` | private cockpit | private DNS / WARP route only | LAN only |
| `ai.eggiebagelface.lan` | private AI services | private DNS / WARP route only | LAN only |

## TLS doctrine

Cloudflare owns and renews the browser-facing edge certificate through Universal SSL. Do not try to export or persist the edge private key.

Public edge policy:

- Minimum TLS 1.2.
- TLS 1.3 enabled.
- Always Use HTTPS enabled at Cloudflare.
- HSTS enabled only after HTTPS is proven across every intended public hostname.
- `Full (strict)` for the direct `fdroid` origin.

The `fdroid` origin uses a locally generated ECDSA P-256 private key. The private key never leaves the origin. A CSR containing only the public key and requested SANs is sent to Cloudflare Origin CA. Cloudflare returns the signed Origin CA certificate. Preferred rotation validity is 365 days even though Cloudflare supports longer validity.

Certificate SAN scope should be the smallest practical scope, normally `fdroid.eggiebagelface.art`. Do not use a wildcard unless another reviewed origin genuinely needs the same key.

Let's Encrypt ECDSA DNS-01 remains the browser-trusted fallback for origins that may ever be reached without Cloudflare. Do not put a Cloudflare Origin CA certificate on a DNS-only/bypass hostname intended for direct browser access.

## Public key / private key doctrine

- TLS private key: local only, mode 0600, never Git/Drive plaintext/model-visible.
- TLS public key: carried in the CSR and returned certificate.
- DNS authenticity: Cloudflare DNSSEC + registrar DS is the DNS public-key trust layer.
- Do not publish manual DNSKEY material.
- Do not use TLSA/DANE to pin Cloudflare-proxied HTTPS hostnames because Cloudflare terminates and rotates the edge certificate.
- CAA may authorize Let's Encrypt for fallback issuance; Cloudflare may synthesize additional CAA values needed for Universal SSL issuance.

## IPv4 / IPv6 doctrine

There is no HTTP-level `IPv4 -> IPv6` redirect. IP-family selection happens before HTTP.

Canonical path:

```
IPv4 client ----\
                 > Cloudflare dual-stack edge -> IPv6-only fdroid origin
IPv6 client ----/
```

For `fdroid.eggiebagelface.art`, publish the real origin as a proxied `AAAA` only. Do not publish a public `A` record. Cloudflare's edge can still answer both A and AAAA to visitors.

## WAN -> LAN doctrine

`cloudflared` is outbound-only. Do not open inbound WAN port forwards for admin/LAN services.

`admin.eggiebagelface.art` is a published Tunnel application and must be protected by Cloudflare Access identity plus WARP/device posture. Private `.lan` hostnames are not public authoritative DNS records; they are resolved through private DNS / Zero Trust routing.

The F-Droid repository stays public and must never be placed behind identity, geo, or device-posture gates.

## Canonical DNS intent

```
www     CNAME  eggiebagelface.art                  PROXIED
fdroid  AAAA   <GCP_VM_EXTERNAL_IPV6>              PROXIED
admin   CNAME  <CF_TUNNEL_ID>.cfargotunnel.com     PROXIED
@       CAA    0 issue "letsencrypt.org"            DNS ONLY
@       CAA    0 issuewild "letsencrypt.org"        DNS ONLY
```

The apex site is attached using a Workers Static Assets custom domain rather than a hand-written origin record.

## Green gate

`CLOUDFLARE_FQDN_TLS_GREEN` requires actual evidence for all of:

- zone active;
- Universal SSL active;
- minimum TLS >= 1.2 and TLS 1.3 enabled;
- Always Use HTTPS active;
- Full (strict) on `fdroid` origin;
- Origin ECDSA P-256 certificate validates for `fdroid.eggiebagelface.art`;
- DNSSEC active and registrar DS validates;
- no public origin IPv4 A record;
- proxied fdroid AAAA resolves and public signed F-Droid index is reachable;
- admin CNAME targets the active Cloudflare Tunnel;
- Access/WARP policy is proven for admin;
- `.lan` hostnames remain private;
- no private key or API-token leakage.

Do not call the lane GREEN merely because configuration files exist.
