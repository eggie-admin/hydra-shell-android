# eggiebagelface.art Coming Soon

Static public splash page for the Project Hydra / KAI 9000 beta period.

## Design law

- static HTML/CSS only;
- no JavaScript;
- no analytics;
- no cookies;
- no external fonts, images, scripts, styles, APIs, or trackers;
- no secrets;
- no dependency on the Google VM or private LAN;
- `fdroid.eggiebagelface.art` remains a separate hostname and is never captured by this site.

## Cloudflare platform

Use **Workers Static Assets** for new deployment. Cloudflare currently recommends Workers for new projects and static asset requests are free/unlimited under the static-assets billing model.

Preview configuration:

```text
wrangler.preview.jsonc
```

This leaves the site on a `workers.dev` preview hostname.

Production configuration:

```text
wrangler.production.jsonc
```

This binds the Worker as the origin for these exact custom domains only:

```text
eggiebagelface.art
www.eggiebagelface.art
```

Cloudflare creates/manages the custom-domain DNS/certificate binding. Do not use the production config until any conflicting apex/`www` DNS record has been reviewed.

## Manual deployment

The GitHub workflow `.github/workflows/cloudflare-coming-soon.yml` validates on source changes but only deploys from `workflow_dispatch`.

Required protected GitHub values:

```text
secret: CF_API_TOKEN
variable: CF_ACCOUNT_ID
```

The API token must be least privilege for Workers deployment/domain binding. Never use a Global API Key.

## Search-engine posture

During private beta the page emits `noindex,nofollow,noarchive` and `robots.txt` disallows crawling. Remove those controls deliberately when the real public site launches.

## Copyright

The page is original Project Hydra material and follows the repository `COPYRIGHT.md` / Project Hydra beta licensing doctrine. Third-party marks are not incorporated into the page.
