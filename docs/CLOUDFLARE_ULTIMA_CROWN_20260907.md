# KAI 9000 Cloudflare ULTIMA Crown Doctrine

Milestone: `KAI9000_CLOUDFLARE_ULTIMA_CROWN_20260907`

Crown holder: **Professor**. AI agents may build, test, inspect, and propose or apply explicitly authorized repository changes, but may not self-promote, self-publish, or override the Professor.

## Active architecture

```text
Samsung KAI 9000 APK
        |
        | remote operator / cockpit
        v
GitHub repository + Codespaces
        |
        | GitHub Actions
        v
Cloudflare Workers Static Assets
        |
        v
eggiebagelface.art + www.eggiebagelface.art
```

### Active public-edge law

- Cloudflare is the only public deployment edge in this doctrine.
- Local VNC/websockify/AcodeX publication is not part of the public Cloudflare path.
- Public origin IP publication for the Coming Soon site is not required.
- Historical deployment providers are outside the active architecture and are not status authorities.

## Coming Soon deployment

The public Coming Soon site is a static HTML/CSS asset bundle deployed with Cloudflare Workers Static Assets.

Production domains:

```text
eggiebagelface.art
www.eggiebagelface.art
```

The GitHub workflow `.github/workflows/cloudflare-coming-soon.yml` is the only repository publication lane for this static gate. Production deployment requires an explicit `workflow_dispatch` request and `confirm_publish=YES`.

Required protected GitHub configuration:

```text
secret: CF_API_TOKEN
variable: CF_ACCOUNT_ID
```

The token must be scoped only to the Cloudflare account/zone permissions required for Workers deployment and custom-domain binding. Global API Keys are forbidden.

## TLS and certificate law

Cloudflare terminates public edge TLS for the Coming Soon Worker custom domains.

Required posture:

- Cloudflare-managed edge certificates.
- TLS 1.2 minimum or stronger.
- TLS 1.3 enabled.
- HTTPS-only after certificate activation is proven.
- HSTS only after all production HTTPS routes are proven stable.
- Do not export or archive Cloudflare edge private keys.

Public certificates, CA certificates, certificate chains, signatures, and fingerprints are public metadata. They do not require secrecy. Private key material does.

## Key-pair doctrine

Private keys remain local to the trusted key owner or an approved encrypted secret/signing store.

Never commit or upload these as plaintext:

- APK signing private key;
- SSH private key;
- origin TLS private key;
- API tokens;
- OAuth client secrets;
- passkeys/TOTP seeds;
- Cloudflare credentials.

Public keys and fingerprints may be published or mirrored when useful.

For SSH identity verification, publish only the SSH public-key fingerprint through an `SSHFP` record and enable DNSSEC before relying on DNSSEC-validated SSHFP.

## DNS law

- DNSSEC: enabled and registrar DS validated.
- Do not hand-author Cloudflare DNSKEY material.
- Do not publish private `.lan` hostnames in public DNS.
- Do not publish private keys or API tokens in TXT records.
- CAA records must not prevent Cloudflare-managed edge-certificate renewal.
- If an explicitly selected Let's Encrypt certificate lane is used, authorize `letsencrypt.org` without blocking the CA(s) required by the active Cloudflare edge product.
- Do not pin Cloudflare-proxied edge certificates with TLSA in this baseline.

## Origin law

The Coming Soon Worker has no customer-managed public web origin.

If a future origin is introduced:

1. generate its private key locally on the trusted origin;
2. generate a CSR locally;
3. obtain a certificate from an approved CA;
4. use Cloudflare Full (strict) when Cloudflare proxies that origin;
5. never upload the origin private key to Git, Drive, DNS, APK assets, or model context.

## ULTIMA verification gates

Repository-side `CLOUDFLARE_ULTIMA_REPO_GREEN` requires:

1. static Coming Soon HTML and robots files exist;
2. no scripts, trackers, external assets, API keys, or private keys are embedded;
3. production Wrangler config binds only the apex and `www` custom domains;
4. no unapproved external deployment dependency exists in the active Coming Soon lane;
5. Wrangler configuration parses and dry-run packaging succeeds;
6. production deployment remains human-gated;
7. credentials are sourced only from protected GitHub secret/variable stores.

Live `CLOUDFLARE_ULTIMA_GREEN` additionally requires evidence from Cloudflare/public DNS that:

1. the zone is active;
2. both custom domains are bound to the Worker;
3. edge certificates are active;
4. HTTPS succeeds on apex and `www`;
5. DNSSEC is active and DS validates at the registrar;
6. the active DNS/certificate configuration has no conflicting stale external binding;
7. no Cloudflare credential has leaked into Git/APK/log/model context.

Repository green must never be mislabeled as live Cloudflare green without that external evidence.

## Final law

```text
Professor = crown holder
LuHm OS = product trunk
GitHub = canonical source + remote terminal/build forge
Cloudflare = public edge
Google Drive = recovery mirror
```
