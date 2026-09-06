# Cloudflare OAuth-First Bootstrap Reroll v4

Date: 2026-09-06
Zone: `eggiebagelface.art`

## Goal

Remove stale assumptions that Cloudflare production control requires copying API-token secrets into GitHub or model-visible context.

Cloudflare credentials are split by purpose:

1. Human interactive bootstrap uses OAuth/browser authorization.
2. Tunnel runtime uses only its tunnel-specific credential.
3. Durable unattended CI may later use narrowly scoped account-owned API tokens.
4. Existing API-token secret values are never expected to be retrievable after creation.

## Interactive bootstrap

### Workers / public site

Use Wrangler OAuth device flow from the trusted operator machine:

```bash
bash integrations/cloudflare/bootstrap-oauth.sh wrangler-login
```

Wrangler 4.119.0+ supports OAuth device authorization, avoiding localhost callback requirements. The operator approves the request in the normal Cloudflare browser session. Do not print or export Wrangler OAuth credentials.

The apex and `www` Workers Custom Domains may then be deployed by Wrangler using the OAuth session. Cloudflare manages their DNS records and edge certificates.

### Tunnel / admin

Use:

```bash
bash integrations/cloudflare/bootstrap-oauth.sh tunnel-login
```

`cloudflared tunnel login` performs an interactive browser authorization and writes an account certificate to `~/.cloudflared/cert.pem`. Treat that file as account-wide management authority. Keep mode `0600`, never commit it, and do not copy it into an APK, chat, prompt, artifact, or public backup.

After the named admin tunnel is created, the tunnel runtime should receive only the tunnel-specific credentials file or token. It does not need the account-wide `cert.pem`.

## Google HTTPS identity

Cloudflare Access remains the policy enforcement point for `admin.eggiebagelface.art`.

Authentication chain:

```text
HTTPS
 -> Cloudflare Access
 -> Google OAuth Web client
 -> approved Google identity
 -> Cloudflare Independent MFA
 -> Authenticator-app TOTP (Google Authenticator supported)
 -> WARP/device posture
 -> Cloudflare Tunnel
 -> private admin origin
```

An already logged-in Google browser session may make the OAuth consent/login flow smoother, but session cookies, ChatGPT Google connector grants, refresh tokens, or browser credentials are never extracted or repurposed.

## API-token workaround

Do not attempt to "pull all token secrets". Cloudflare only exposes the token value when the token is created or rolled.

Instead:

- Inventory token metadata only: ID, name, status, permissions, scopes, timestamps.
- Delete/revoke obsolete tokens.
- Roll or replace a token when its secret is lost.
- Prefer separate least-privilege lanes rather than one master token.
- Prefer account-owned tokens for durable CI/CD integrations where supported.

Recommended machine lanes if unattended automation is later enabled:

```text
KAI-CF-DNS-TLS       zone/DNS/TLS settings only
KAI-CF-WORKERS       Workers deployment/custom-domain only
KAI-CF-ACCESS        Access applications/policies only
KAI-CF-ORIGIN-CA     Origin CA issuance only
KAI-CF-TUNNEL-RUN    one tunnel runtime only
```

No Global API Key.

## Final-form gate correction

Persistent APK and F-Droid signing keys do not need to exist in GitHub Actions merely to prove an already-signed release. The immutable public evidence is sufficient for preflight:

- signed bundle SHA-256;
- APK signer SHA-256;
- F-Droid repository fingerprint;
- publication manifest says `fdroid_signed=true`.

Private signing keys remain in the trusted signing vault and are needed only for future signing operations.

Likewise, `CF_API_TOKEN` is no longer a mandatory human-publication prerequisite. A live Cloudflare state created through OAuth/browser authorization can be proven by public DNS/TLS/Access evidence. A scoped API token is required only for unattended API automation.

## Green states

`CLOUDFLARE_OAUTH_BOOTSTRAP_GREEN` requires:

- Wrangler OAuth `whoami` succeeds on the operator machine;
- no OAuth credential material leaves the operator machine;
- Tunnel account login is complete if tunnel management is required;
- tunnel runtime uses tunnel-specific credentials only;
- Google Access identity and independent MFA are proven;
- public DNS/TLS state matches doctrine;
- no Global API Key;
- no token secret leakage.

`FINAL_FORM_GREEN` still requires the public F-Droid import and signed upgrade proof. OAuth bootstrap removes a credential-delivery obstacle; it does not waive public verification.
