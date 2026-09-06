---
applyTo: "integrations/cloudflare/**,docs/CLOUDFLARE_*.md,tools/cloudflare_*.py,.github/workflows/*cloudflare*"
---

# Cloudflare Security Instructions

Treat `docs/CLOUDFLARE_EAP_SECURITY_REROLL.md` and `integrations/cloudflare/security.manifest.json` as canonical.

Rules:

- EAP means Edge Access Perimeter, not 802.1X EAP.
- Prefer Cloudflare Tunnel for public/private origin connectivity; no WAN port-forwarding.
- Keep `.lan` private and never publish it in authoritative public DNS.
- Public business/F-Droid routes must remain reachable without admin-only Access policies.
- Admin/private routes require authenticated identity plus location and WARP/device-posture signals.
- Cloudflare edge TLS: Full (strict), minimum TLS 1.2, TLS 1.3 enabled.
- Preferred origin certificate: Let's Encrypt DNS-01, ECDSA P-256.
- Keep Universal SSL enabled unless a reviewed replacement is already active.
- Enable DNSSEC only with registrar DS verification in the evidence plan.
- DNSSEC is the public-key DNS trust layer. Do not invent or commit DNSKEY private material.
- Do not add TLSA/DANE pins to proxied HTTPS hostnames in this baseline.
- Do not create a public A record or paid IPv4 requirement for the strict-free Google VM lane.
- "IPv4 to IPv6" means dual-stack Cloudflare edge plus Tunnel/IPv6-only origin, not an HTTP redirect.
- DDoS/WAF protections stay enabled. Avoid broad allow rules that bypass security products.
- Never use the Cloudflare Global API Key in automation. Split least-privilege tokens by DNS/ACME, zone security, Tunnel, and Access administration.
- Never print or commit Cloudflare tokens, tunnel credentials, origin private keys, or ACME credentials.
- HSTS preload is forbidden during testing. Stage HSTS only after HTTPS is stable and reviewed.
- No Cloudflare change is GREEN without live API/DNS/TLS/tunnel evidence.
