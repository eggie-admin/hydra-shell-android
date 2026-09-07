# Lum Android Backend Skill

KAI 9000 APK is the active mutation target. Android is the authenticated cockpit/client, not the provider-secret store and not a local build server.

## Active lanes

- `/api/*`: HTTPS request/response commands, jobs, config, health.
- `/ws`: Samsung real-time control/status event stream when enabled.
- `/api/lum/*`: server-side OpenAI Lum agent.
- `/api/remote-ai/*`: explicit provider router for OpenAI or Hugging Face advisory requests.
- Terminal UI: remote GitHub Codespaces/browser terminal, not local Termux.

## Current deployment doctrine

- GitHub is canonical source history.
- GitHub Actions is the remote build/test/release forge.
- Cloudflare is the public edge.
- Google Drive is the recovery mirror.
- Vercel is retired and forbidden.
- Local Termux is retired from the active architecture.

Historical Termux/VNC/websockify/AcodeX artifacts may be consulted only for recovery or migration evidence. Do not reintroduce them as an APK runtime dependency.

## Security

- No OpenAI, Hugging Face, Google, GitHub, Cloudflare, SSH, signing, or private-key secret belongs in APK assets, HTML, JavaScript, logs, manifests, or agent state.
- The Android app authenticates to KAI/application services, not directly to provider secrets.
- Provider adapters own authentication, retries, routing, rate limits, and observability behind application policy.
- Provider tool calls do not bypass deterministic application authorization.
- Public-key metadata may be published where appropriate; private keys remain private.

## Crown boundary

The Professor is final authority. Lum may inspect, draft, test, and propose. Merge, release, publication, destructive mutation, spending, and ULTIMA require explicit human authorization and execution evidence.

## Deployment truth

Local/CI smoke is not proof that a public endpoint or Cloudflare binding is live. Report repository/CI GREEN separately from live-network GREEN.
