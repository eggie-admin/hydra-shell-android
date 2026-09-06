# Cloudflare EAP Security Reroll

Status: testing doctrine for `eggiebagelface.art`.

EAP in this doctrine means **Edge Access Perimeter**. It is not 802.1X/EAP Wi-Fi authentication.

## Mission

Cloudflare is the outer security ward for KAI 9000. It protects the public business domain, the F-Droid endpoint, and authenticated WAN-to-LAN access without exposing the LAN or origin control plane directly.

```text
Internet / enrolled device
        ↓
Cloudflare edge
  DNSSEC + Universal TLS
  DDoS + WAF
  Access / device posture where private
        ↓
Cloudflare Tunnel / WARP
        ↓
private origin or LAN
        ↓
KAI 9000 services
```

## 1. Tunnel / VPN replacement

Use Cloudflare Tunnel (`cloudflared`) as the default server-side connector. It establishes outbound-only connections to Cloudflare, so the router/firewall does not need inbound NAT or port forwarding.

For remote user-to-LAN access, enrolled clients use the Cloudflare One Client (WARP) and Zero Trust private-network/private-hostname routing.

WAN-to-LAN doctrine:

```text
WARP client
   -> Cloudflare Zero Trust
   -> identity + country + device posture policy
   -> cloudflared outbound tunnel
   -> lum.eggiebagelface.lan / ai.eggiebagelface.lan
```

Do not publish `.lan` names in public DNS. They remain private routing names.

Standard Tunnel is appropriate for user-initiated access to LAN services. If KAI later requires bidirectional site-to-site or server-initiated private networking, evaluate Cloudflare Mesh rather than pretending Tunnel provides that behavior.

## 2. Public versus private applications

Public and private policy must not be mixed.

Public:
- `eggiebagelface.art`
- `www.eggiebagelface.art`
- `fdroid.eggiebagelface.art`

These remain broadly reachable so the business site and F-Droid repository work normally. They receive DDoS/WAF/TLS protection but are not globally location-locked.

Private/admin:
- future `admin.eggiebagelface.art` or another explicitly declared admin hostname;
- private cockpit routes;
- private `.lan` services through WARP.

Private/admin access requires identity plus additional signals. Preferred policy:

```text
ALLOW only when
  authenticated_identity == approved
  AND country == US
  AND WARP/device posture == healthy
```

Location is an additional signal, not the sole authentication factor.

## 3. SSL/TLS manager

Use the term TLS for the protocol. "SSL" remains only where vendor UI/API names use it.

### Visitor -> Cloudflare

- Cloudflare Universal SSL/TLS remains enabled.
- Universal certificates are automatically managed and support ECDSA on the Free plan.
- Minimum visitor TLS: 1.2.
- TLS 1.3: enabled.
- Always Use HTTPS: enabled after the active certificate is verified.
- HSTS: staged only after HTTPS is proven stable. Do not preload during testing.

### Cloudflare -> origin

Encryption mode: **Full (strict)**.

Preferred origin certificate for this project: Let’s Encrypt public CA using ACME DNS-01 with a narrowly scoped Cloudflare DNS token.

Origin key algorithm:

```text
ECDSA P-256 / secp256r1
```

Let’s Encrypt DNS-01 is preferred because it works without opening inbound port 80 and supports wildcard issuance. The DNS credential must be scoped only to the DNS changes required for validation and must never be committed.

Cloudflare Origin CA remains an acceptable fallback for origins that are exclusively reached through Cloudflare, but the selected KAI doctrine is Let’s Encrypt for the origin when practical.

## 4. DDoS and WAF

Cloudflare autonomous DDoS protection remains enabled at defaults. Free-plan WAF managed protection remains enabled.

Add custom rules only where they improve a positive security model. Do not create broad allow rules that bypass the WAF.

Suggested private/admin rule posture:
- challenge/block unexpected countries before the application;
- rate-limit authentication and API abuse where plan capabilities permit;
- deny obvious scanner paths on admin hosts;
- keep public F-Droid download paths free of identity/location requirements.

Never expose the origin merely to "make DDoS work". Hidden origins are preferred.

## 5. Location lock

Location lock applies to admin/private surfaces, not the public business site or public F-Droid repository.

Cloudflare Access should combine:
- approved identity;
- country `US` for the current administrative policy;
- WARP and/or device posture where available.

The country rule is defense-in-depth. VPNs, mobile networks, travel, and geolocation errors mean country alone is not sufficient authentication.

## 6. IPv4 -> IPv6 doctrine

There is no meaningful HTTP redirect that converts an IPv4 connection into IPv6.

Correct architecture:

```text
visitor IPv4 or IPv6
        ↓
Cloudflare dual-stack edge
        ↓
Tunnel, or IPv6-only origin transport
```

For the strict-free Google VM lane, do not allocate a billable external IPv4. The VM may retain external IPv6 for outbound connectivity while public DNS points to a Cloudflare Tunnel CNAME instead of exposing the origin address.

If a direct-origin fallback is ever used, publish proxied AAAA only and no public A record.

## 7. DNS public-key security

Enable DNSSEC for `eggiebagelface.art`. Cloudflare signs the zone, publishes DNSKEY records, and provides the DS value that must be installed at the registrar. Cloudflare currently uses DNSSEC Algorithm 13 (ECDSA Curve P-256 with SHA-256) where supported.

Do not hand-author Cloudflare DNSKEY material.

CAA may be used to authorize Let’s Encrypt for origin certificate issuance. Because Cloudflare Universal SSL can use multiple partner CAs and automatically supplements CAA when Universal SSL is active, do not create a brittle CAA policy that prevents Cloudflare edge-certificate renewal.

Do not publish TLSA/DANE records for Cloudflare-proxied public HTTPS hostnames in this baseline. Cloudflare terminates edge TLS and rotates edge certificates, so pinning a specific origin/edge certificate in TLSA would be the wrong trust boundary.

## 8. WAN-to-LAN firewall law

Preferred LAN firewall stance:

```text
INBOUND WAN -> LAN: deny
PORT FORWARDING: none
cloudflared egress: allow required Cloudflare tunnel destinations/port 7844 TCP+UDP
LAN services: bind private/loopback as appropriate
```

Only services explicitly named in the tunnel configuration may be published.

For the KAI Android control plane, keep ordinary Termux services on loopback and do not route AcodeX/VNC/WebSocket publicly merely because Tunnel exists.

## 9. API token split

Never use a Global API Key in automation.

Separate capabilities where practical:

- DNS/ACME token: zone read + DNS edit for `eggiebagelface.art` only.
- Zone-security token: only settings/DNSSEC/rules permissions needed for the zone baseline.
- Tunnel token: connector/tunnel runtime only.
- Zero Trust admin token: Access apps/policies/groups only when automating those resources.

No Cloudflare credential is model-visible.

## 10. KAI MAGE

```text
CAST RAISE_WARD eggiebagelface.art
  => Full(strict) + TLS1.2 floor + TLS1.3 + HTTPS

CAST SIGN_DNS
  => DNSSEC zone signing
  => registrar DS verification required

CAST OPEN_TUNNEL
  => outbound-only cloudflared connector
  => no WAN port-forward

CAST LOCATION_LOCK target=admin
  => identity + US + WARP/device posture

CAST WAN_TO_LAN
  => enrolled WARP client -> Zero Trust -> Tunnel -> private hostname

CAST ECDSA_ORIGIN
  => Let’s Encrypt DNS-01
  => ECDSA P-256 origin certificate
```

## GREEN gates

`CLOUDFLARE_SECURITY_GREEN` requires evidence for all required lanes:

1. zone is active on Cloudflare;
2. Universal SSL active;
3. Full (strict) active;
4. TLS minimum >= 1.2 and TLS 1.3 enabled;
5. DNSSEC enabled and registrar DS validates;
6. tunnel connected and origin not directly exposed;
7. DDoS/WAF protections active;
8. admin/private Access policy proven with identity + location + device signal;
9. public business/F-Droid routes remain reachable;
10. no Cloudflare secrets in Git/APK/log/model context.

Until live API and DNS evidence prove these gates, report `CLOUDFLARE_SECURITY_WIRED`, not `CLOUDFLARE_SECURITY_GREEN`.
