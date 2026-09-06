# Cloudflare SSL Manager + Google HTTPS Auth Doctrine v3

Date: 2026-09-06
Zone: `eggiebagelface.art`

This document extends the FQDN/TLS v2 doctrine. It does not replace the public/private routing split.

## Canonical trust path

```text
PUBLIC WEB / FDROID
client -> Cloudflare edge TLS -> Full (strict) -> reviewed origin

ADMIN
https://admin.eggiebagelface.art
  -> Cloudflare Access
  -> Google OAuth login
  -> Cloudflare independent MFA
  -> TOTP authenticator app (Google Authenticator supported)
  -> US location defense-in-depth
  -> WARP/device posture
  -> Cloudflare Tunnel
  -> private admin origin
```

## SSL Manager doctrine

Cloudflare owns and renews browser-facing edge certificates. Never attempt to export the Cloudflare edge private key.

- Minimum edge TLS: 1.2.
- TLS 1.3: enabled.
- Always Use HTTPS: enabled at Cloudflare.
- HSTS: enable only after every intended public hostname is proven HTTPS-clean.
- `fdroid.eggiebagelface.art`: Full (strict) to its origin.
- F-Droid origin key: local ECDSA P-256, mode 0600, never committed, never uploaded plaintext.
- Cloudflare Origin CA: CSR-only issuance; the private key remains local.
- DNSSEC + registrar DS is the DNS public-key trust layer.
- No TLSA/DANE pin for Cloudflare-proxied HTTPS.

## Google HTTPS login

Cloudflare Access uses Google as the identity provider for the admin surface only. Public website and F-Droid routes must not require login.

Cloudflare's Google IdP integration requires a Google OAuth Web application with:

```text
Authorized JavaScript origin:
https://<CF_TEAM_NAME>.cloudflareaccess.com

Authorized redirect URI:
https://<CF_TEAM_NAME>.cloudflareaccess.com/cdn-cgi/access/callback
```

The OAuth Client ID may be stored as configuration. The OAuth Client Secret is a secret and must live only in the protected provider/CI secret boundary.

"Use active login" means the browser may use the user's already-authenticated Google session during the normal Google OAuth authorization flow. It does NOT mean extracting Google cookies, Drive connector credentials, refresh tokens, or another application's OAuth session.

Access policy must still restrict the authorized Google identity, even though the Google IdP can authenticate any Google account when configured without Workspace group restrictions.

## Google Authenticator / MFA

Google Authenticator is used as a TOTP authenticator, not as the OAuth identity provider.

Canonical admin MFA is Cloudflare independent MFA:

- authenticator application/TOTP allowed;
- Google Authenticator is an acceptable authenticator app;
- require MFA on every admin Access login (`session_duration = 0m`) unless a later usability review deliberately relaxes it;
- do not export TOTP seeds or recovery material to Git, logs, prompts, or plaintext Drive files;
- hardware/FIDO2 can be added later as a stronger second-factor option.

This independent-MFA design avoids relying on Google to send an MFA method claim that Cloudflare can enforce.

## API token doctrine

Existing Cloudflare token secret values are NOT recoverable. Cloudflare lists token metadata, but a token secret is only shown when the token is created or rolled.

Therefore `pull all api tokens` compiles to:

```text
INVENTORY token metadata
  -> id
  -> name
  -> status
  -> issued/modified/last-used/expiry
  -> policy/resource metadata when returned

NEVER pull/display
  -> secret token value
  -> Global API Key
  -> OAuth Client Secret
  -> Tunnel credential
  -> TOTP seed
```

If an existing token secret is unavailable, roll or replace that token. Rolling invalidates the previous secret.

### Bootstrap and durable tokens

1. Human performs the one unavoidable bootstrap in the Cloudflare dashboard using the active Cloudflare login.
2. Prefer a short-lived/IP-restricted bootstrap token with only the permissions needed to inventory/create the scoped tokens.
3. For durable CI, prefer account-owned API tokens when the required endpoint supports them.
4. Use separate least-privilege lanes where practical:
   - DNS/TLS publication;
   - Workers deployment;
   - Zero Trust/Access administration;
   - Origin CA issuance;
   - Tunnel connector/runtime.
5. Do not use the Global API Key.
6. Token values are written directly into the provider/CI secret store and are never echoed by automation.

The existing `CF_API_TOKEN` variable remains a compatibility name until the deployment workflows are migrated to narrower per-lane credentials. It must never be a Global API Key.

## Connected-login boundary

A Google account is connected to ChatGPT for Google Drive, but that OAuth grant is not a Google Cloud OAuth client credential and cannot be transplanted into Cloudflare Access. Likewise, no Cloudflare control connector is currently available in this chat.

Do not treat an active browser or connector login as permission to scrape cookies, session tokens, API secrets, or recovery codes.

## Green gate

`CLOUDFLARE_SSL_GOOGLE_AUTH_GREEN` requires real evidence for all of:

- edge TLS settings active;
- Full (strict) proven for F-Droid origin;
- Google IdP configured and Cloudflare Test succeeds;
- admin app restricts the approved Google identity;
- Cloudflare independent MFA enabled and TOTP enrollment proven;
- admin login successfully completes Google OAuth + independent MFA;
- WARP/device posture policy passes;
- token inventory succeeds without exposing token values;
- only required scoped tokens remain active;
- no Global API Key used;
- no secret leakage.

Configuration files alone are not GREEN.
