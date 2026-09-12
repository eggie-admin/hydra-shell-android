# KAI Vue CMS Mutation

Clean donor-purged scaffold for a Vue 3 CMS front end served by a FastAPI backend, with optional Cloudflare Tunnel/WARP lane, Cloudflare trust material refresh, and Let's Encrypt DNS-01 instructions.

## Source-of-truth guardrails

- Chrome Dev and Chrome Canary are behavior/test harnesses only.
- Future APK builds stay donor-purged and KAI-owned.
- No Chrome/Canary source code, assets, snippets, or hidden dependencies are ingested into this app.
- Secrets, keys, Cloudflare tokens, cert private keys, tunnel credentials, and deploy tokens stay outside git.

## Local dev

```bash
uv sync
npm --prefix frontend install
npm --prefix frontend run dev
uv run fastapi dev app/main.py
```

The Vue dev server defaults to `http://127.0.0.1:5173`. The FastAPI API defaults to `http://127.0.0.1:8000`.

## Build full-stack static frontend into FastAPI

```bash
npm --prefix frontend install
npm --prefix frontend run build
uv run fastapi dev app/main.py
```

FastAPI will serve `frontend/dist` at `/` when it exists. API routes remain under `/api/*`.

## FastAPI Cloud deployment lane

Read-only inspection first:

```bash
rg --files -g 'pyproject.toml' -g '.fastapicloud/**' -g '.fastapicloudignore' -g '.gitignore'
uv run fastapi cloud deploy --help
uv run fastapi cloud whoami --json
uv run fastapi cloud apps get --json
```

Deploy only after the project is linked and secrets are set:

```bash
uv run fastapi cloud deploy . --json
```

## FastAPI Cloud custom domain lane

FastAPI Cloud manages the app deployment and can report the DNS records needed for the custom hostname.
It does not directly edit Cloudflare DNS.

```bash
uv run fastapi cloud domains --help
uv run fastapi cloud domains list --app-id "$FASTAPI_CLOUD_APP_ID" --json
uv run fastapi cloud domains add cms.eggiebagelface.art --app-id "$FASTAPI_CLOUD_APP_ID" --standard --json
uv run fastapi cloud domains get cms.eggiebagelface.art --app-id "$FASTAPI_CLOUD_APP_ID" --json
```

Use exactly the DNS records returned by `domains get`.

## Private Cloudflare Tunnel lane

Use this if the CMS is on a private origin you control, not inside FastAPI Cloud itself.

```bash
sudo bash infra/cloudflare/install-cloudflared-ubuntu.sh
cloudflared tunnel login
cloudflared tunnel create kai-vue-cms
cp infra/cloudflare/cloudflared-config.example.yml ~/.cloudflared/config.yml
cloudflared tunnel route dns kai-vue-cms cms.eggiebagelface.art
cloudflared tunnel run kai-vue-cms
```

For a Zero Trust private hostname or private CIDR, configure Cloudflare One policies and WARP enrollment in the Cloudflare dashboard.

## Let's Encrypt DNS-01 lane using Cloudflare

Use only for origins where you need a publicly trusted certificate. FastAPI Cloud already provides HTTPS for the deployed app.

```bash
sudo bash infra/letsencrypt/issue-letsencrypt-cloudflare.sh cms.eggiebagelface.art
```

The script expects `/etc/letsencrypt/cloudflare.ini` with a restricted Cloudflare API token. Never commit that file.

## Refresh Cloudflare public trust material

```bash
sudo bash scripts/update-cloudflare-public-trust.sh
```

This refreshes:

- Cloudflare IP ranges into `/etc/kai9000/cloudflare/`
- Cloudflare Authenticated Origin Pull CA cert into `/etc/nginx/certs/cloudflare.crt`

It does not fetch private keys. It does not expose secrets.
