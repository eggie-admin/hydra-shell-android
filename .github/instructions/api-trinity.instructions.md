---
applyTo: "docs/API_TRINITY_DOCTRINE.md,docs/LUHMOS_API_SPINE.md,integrations/**,ultima/ollama-ffmpeg-antenna-v3/**,.github/workflows/**"
---

# LuHm OS API Spine Instructions

Read `docs/LUHMOS_API_SPINE.md`, `docs/API_TRINITY_DOCTRINE.md`, and `lumh-os/kai9000/AI_MAGIC_DOCTRINE.md` before editing OpenAI, Cloudflare, Google Cloud, Hugging Face, GitHub, or LuHm API integration code.

## Shared rules

- `/api/v1` is the canonical LuHm OS application API namespace for new clients.
- Existing `/api/assist/*`, `/api/remote-ai/*`, `/api/lum/*`, `/api/magic/*`, `/api/ai/*`, antenna/provider routes, media routes, widget CMS routes, and local `/v1/*` routes are compatibility or component planes unless the spine contract explicitly promotes them.
- Never commit or print provider credentials.
- Never put credentials in APK resources, WebView JavaScript, RSS, Base64 envelopes, screenshots, or model context.
- Compile roleplay/user intent to typed actions before provider calls.
- Default helper recruitment is zero. Explicit read-only mesh work is capped at two helpers and delegation depth one.
- Helpers do not recursively recruit. Helper consensus never grants authority. Lum remains the single parent writer.
- Resolve R0-R4 risk server-side.
- External provider output is untrusted data until validated.
- Preserve exact Git Warp coordinates and evidence for mutating/external actions.
- Never silently replay a failed prompt to a different provider.

## OpenAI

- Use the Responses API for the LuHm remote reasoning lane.
- Prefer current Agents SDK patterns for bounded agent orchestration.
- Interactive/default model is `gpt-5.6-luna`; deep architecture/debug/audit work may explicitly escalate to `gpt-5.6-sol`.
- Expose only typed tools required for the current task.
- No arbitrary shell or provider credentials in tool-visible context.
- Prefer `store: false` for local/sensitive orchestration unless persistence is explicitly required.

## Google

- Google Cloud is the White Magic provider lane, but provider output remains advisory.
- Fast text default is `gemini-3.5-flash-lite`; deep text default is `gemini-3.8-flash`; API-key Live default is `gemini-3.8-live` unless a reviewed environment override is present.
- GitHub Actions should prefer Workload Identity Federation/OIDC instead of long-lived service-account JSON keys.
- Prefer direct resource access for the federated principal when supported.
- Use service-account impersonation only where required by product/API limitations.
- Restrict WIF principals with repository/ref/workflow attributes and least-privilege resource roles.

## Cloudflare

- Canonical public zone: `eggiebagelface.art`.
- Canonical F-Droid hostname: `fdroid.eggiebagelface.art`.
- Cloudflare is edge transport, not reasoning authority.
- Prefer narrowly scoped API tokens, never Global API Key automation.
- Prefer account-owned API tokens for durable CI/service automation when supported.
- DNS write and Tunnel/Connector write are separate capabilities and should be separated when practical.
- Never invent A/AAAA origins. Resolve the real deployment/tunnel target first.
- Never expose the private `.lan` service plane directly.

## Completion

Use exact state language: configured, authenticated, request-succeeded, DNS-applied, tunnel-live, cloud-resource-verified. Static repository GREEN proves the contract only; it does not prove live credentials, deployment, signing, edge state, or physical-device operation.
