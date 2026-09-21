# LuHm OS Coming Soon

Static public face for **LuHm OS** at `eggiebagelface.art`.

This directory is intentionally safe to live in the public repository. It is not the private development cockpit and must never become a carrier for private source, prompts, credentials, operator controls, unpublished binaries, private model material, or internal service topology.

## Public-face law

- static HTML/CSS only;
- no JavaScript;
- no forms, logins, consoles, analytics, cookies, trackers, or public APIs;
- no external fonts, images, scripts, styles, media, embeds, or fetches;
- no secrets or environment-derived content;
- no source maps;
- no links or route hints to private development surfaces;
- no dependency on the private LAN, operator workstation, Google VM, or internal services;
- `fdroid.eggiebagelface.art` remains a separate hostname and is never captured by this site;
- private development is a separate access-gated origin and is not built from this public asset directory.

## Private-development boundary

The private cockpit must be published only through an identity-aware access layer in front of its origin. The origin stays non-public and accepts no direct Internet traffic. Authentication must happen before application content is returned, and the origin must validate the access assertion or otherwise fail closed.

Cloudflare Access + Tunnel is the intended transport pattern because it allows an outbound-only connector and deny-by-default identity policy without router port forwarding. The private hostname/path is deliberately not recorded in this public directory.

No public page should contain a hidden admin route. A hidden route is discoverable; an independently authenticated origin is the boundary.

## Cloudflare public platform

The coming-soon face uses Workers Static Assets. `public/_headers` supplies response hardening for the static files.

Preview configuration:

```text
wrangler.preview.jsonc
```

Production configuration:

```text
wrangler.production.jsonc
```

Production binds only:

```text
eggiebagelface.art
www.eggiebagelface.art
```

Do not add the private development origin to this Worker configuration.

## Deployment authority

`.github/workflows/cloudflare-coming-soon.yml` validates source changes automatically but deploys only through explicit `workflow_dispatch`.

Required protected GitHub values:

```text
secret: CF_API_TOKEN
variable: CF_ACCOUNT_ID
```

The token must be least privilege for Workers deployment/domain binding. Never use a Global API Key.

Public publish remains Crown-gated. A successful source validation is not authorization to bind the production domain.

## Search-engine posture

During development the page emits `noindex,nofollow,noarchive,nosnippet,noimageindex`, and `robots.txt` disallows crawling. Remove those controls only as an explicit launch mutation.

## Rights boundary

The public page is original LuHm OS / Eggie Bagelface material. Publication of the page does not grant a license to private code, unreleased assets, model materials, private prompts, internal services, or operator tooling. Third-party marks and donor code must not be copied into the public face without separate provenance and license review.
