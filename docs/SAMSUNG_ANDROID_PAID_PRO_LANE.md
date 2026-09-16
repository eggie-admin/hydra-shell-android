# LuHm OS Paid Pro Samsung Android Lane

Status: ACTIVE DEVELOPMENT LANE

This branch is the only paid-Pro working development lane for LuHm OS in `eggie-admin/hydra-shell-android`.

## Canonical refs

- Control/bootstrap branch: `main`
- Product/release anchor: `luhmos-main`
- Paid Pro working branch: `luhmos/dev/samsung-android-paid-pro`
- Platform scope: Samsung Android only

The paid-Pro branch is for development, test, CI, paid service orchestration, and Samsung Android build-readiness work. It does not silently replace `luhmos-main` as the release anchor.

## Strict paid-service law

All billable or subscription-backed service use must be registered in `admin/paid-pro/service-registry.json` before use. Provider availability does not grant permission to spend money. Unknown billing state is fail-closed. The project monthly budget ceiling is USD 80 unless Professor explicitly changes the policy.

Raw API keys, OAuth refresh secrets, signing keys, passwords, recovery codes, payment credentials, and private key material are forbidden from Git source. Source may contain only credential references and secretless capability metadata.

## Approved service families

The registry currently covers OpenAI Boss Lum, Google Drive, Gmail, Google Cloud APIs, Cloudflare edge/security services, Sentry, GitHub Copilot, and GitHub Actions remote build forge. These services are capabilities, never authority.

## Samsung Android only

This lane may contain Android source, Termux/KAI 9000 integration, Samsung device compatibility work, Godot/Android shell work, local proxy/antenna source, CI/eval fixtures, build-readiness checks, and source-safe release tooling.

Do not use this lane as the active paid development lane for iOS, desktop Linux, Windows, macOS, or a generic web product. Public web material for `eggiebagelface.art` is allowed only when it directly supports the Samsung Android product, install/update handoff, docs, authenticated service edge, or source-safe control plane.

## AI/tool chain

Default development flow:

`USER -> TITAN local policy -> local Ollama concierge when useful -> OpenAI Boss Lum when justified -> at most one bounded helper -> local deterministic tool adapter -> proof receipt`

GitHub Copilot is an assistive development capability. GitHub Actions is the remote build/test forge. Neither may merge, sign, install, publish, or promote release refs without the required Professor authorization.

## Security boundary

- Ollama remains loopback-only.
- Remote services are outbound-only from local adapters where practical.
- Cloudflare public zone is `eggiebagelface.art`; private `.lan` names remain private.
- No public SSH, Ollama, VNC, AXS, or local tool-RPC bind is authorized by this lane.
- PRIVATE data remains a separate classification from PERSONAL paid-service entitlements.
- GAME -> ADMIN escalation remains forbidden.

## Promotion rule

Source tests may become GREEN without promoting the product release. Build/sign/install/push-to-release/merge/publish remain separate gated actions. `luhmos-main` stays the canonical release anchor until Professor explicitly promotes a reviewed candidate.
