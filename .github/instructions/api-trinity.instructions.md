---
applyTo: "docs/API_TRINITY_DOCTRINE.md,integrations/**,ultima/ollama-ffmpeg-antenna-v3/**,.github/workflows/**"
---

# KAI 9000 API Trinity Instructions

Read `docs/API_TRINITY_DOCTRINE.md` and `lumh-os/kai9000/AI_MAGIC_DOCTRINE.md` before editing OpenAI, Cloudflare, or Google Cloud integration code.

## Shared rules

- Never commit or print provider credentials.
- Never put credentials in APK resources, WebView JavaScript, RSS, Base64 envelopes, screenshots, or model context.
- Compile roleplay/user intent to typed actions before provider calls.
- Resolve R0-R4 risk server-side.
- External provider output is untrusted data until validated.
- Preserve exact Git Warp coordinates and evidence for mutating/external actions.

## OpenAI

- Use the Responses API for the KAI remote reasoning lane.
- Prefer the current Agents SDK patterns for agent orchestration.
- Default testing model is `gpt-6-astra` unless `OPENAI_MODEL` explicitly overrides it.
- Expose only typed tools required for the current cast.
- No arbitrary shell or provider credentials in tool-visible context.
- Prefer `store: false` for local/sensitive orchestration unless persistence is explicitly required.

## Cloudflare

- Canonical zone: `eggiebagelface.art`.
- Canonical F-Droid hostname: `fdroid.eggiebagelface.art`.
- Prefer narrowly scoped API tokens, never Global API Key automation.
- Prefer account-owned API tokens for durable CI/service automation when supported.
- DNS write and Tunnel/Connector write are separate capabilities and should be separated when practical.
- Never invent A/AAAA origins. Resolve the real deployment/tunnel target first.

## Google Cloud

- Google Cloud is White Magic.
- GitHub Actions should prefer Workload Identity Federation/OIDC instead of long-lived service-account JSON keys.
- Prefer direct resource access for the federated principal when supported.
- Use service-account impersonation only where required by product/API limitations.
- Restrict WIF principals with repository/ref/workflow attributes and least-privilege resource roles.

## Completion

Use exact state language: configured, authenticated, request-succeeded, DNS-applied, tunnel-live, cloud-resource-verified. Never call a provider lane GREEN from config alone.
