# AI Stack: Lum, OpenAI, Ollama, Python 3, Cloudflare, Google Cloud and Edge Gallery

## Design principle
The AI/cloud stack is split by responsibility so no single model or provider becomes the operating system.

```text
User / Samsung cockpit
        ↓
Lum intent + KAI roleplay compiler
        ↓
Python policy + typed tools
   ↙            ↓             ↘
OpenAI       Ollama local   Provider adapters
remote AI    inference      Cloudflare / Google Cloud
   ↓            ↓             ↓
reasoning     fallback       DNS/HTTPS / White Magic
        \        |          /
          verified evidence
                ↓
         Godot / Edge Gallery
```

Canonical API doctrine: `docs/API_TRINITY_DOCTRINE.md`.

## Lum / OpenAI
Lum is the user-facing spell compiler/persona layer. OpenAI is the remote reasoning and agent lane and is intentionally not assigned a vendor magic color.

Current baseline:
- Responses API at `https://api.openai.com/v1/responses`;
- current Agents SDK patterns for agent orchestration;
- testing default model alias `gpt-6-astra`, overridable with `OPENAI_MODEL`;
- typed custom/function tools for KAI-owned actions;
- `store: false` by default for local/sensitive orchestration unless persistence is explicitly reviewed.

Use OpenAI for:
- complex coding/review tasks;
- structured intent generation;
- typed function/tool requests;
- guardrailed agent workflows;
- evidence synthesis.

OpenAI tool calls do not bypass KAI 9000 policy. Tool inputs and outputs are validated by application-owned code. High-impact actions require the doctrine's approval/checkpoint rules.

`OPENAI_API_KEY` is server-side only. It never belongs in Android resources, WebView JavaScript, source control, RSS, Base64 manifests, screenshots, CI artifacts, or debug APKs.

The APK must still launch and expose useful local/offline state when the OpenAI lane is unavailable.

## Ollama
Ollama is the local inference daemon and first offline fallback.

Canonical endpoint:
`http://127.0.0.1:11434`

Ollama responsibilities:
- fast local chat;
- lightweight director/planner tasks;
- local tool-selection proposals when supported;
- offline fallback.

Ollama has no unrestricted shell authority and is not publicly exposed.

## Python 3
Python 3 is the policy and orchestration layer.

Responsibilities:
- localhost API services;
- typed tool dispatch;
- provider adapter validation;
- device/service probes;
- RSS/feed sanitation;
- SQLite state where appropriate;
- FFmpeg wrappers;
- build/test sanity;
- OpenAI/Ollama routing;
- Cloudflare/Google Cloud request planning;
- release evidence generation.

Prefer explicit functions and data structures over generated shell strings.

## Cloudflare
Cloudflare is the controlled public DNS/HTTPS ingress lane around the canonical business identity `eggiebagelface.art`.

Canonical F-Droid host:
`fdroid.eggiebagelface.art`

Canonical repo URL:
`https://fdroid.eggiebagelface.art/fdroid/repo/`

Policy:
- narrowly scoped API tokens only;
- no Global API Key automation;
- account-owned API tokens preferred for durable CI/service integrations when supported;
- separate DNS and Tunnel/Connector capabilities where practical;
- no invented A/AAAA origins;
- private origins should prefer controlled tunnel/HTTPS ingress rather than exposing local control-plane ports.

Cloudflare credentials never enter model-visible context.

## Google Cloud / White Magic
Google Cloud is the White Magic cloud-service lane.

For GitHub Actions, prefer Workload Identity Federation (WIF) using GitHub OIDC and short-lived credentials instead of long-lived service-account JSON keys.

Policy:
- direct resource access for the federated principal where supported;
- service-account impersonation only when a target API/product requires it;
- restrict WIF by repository/ref/workflow attributes;
- grant resource-specific least-privilege IAM roles;
- never commit service-account JSON keys.

Google Drive remains a separate user/content integration and is not automatically equivalent to Google Cloud IAM.

## Godot 4
Godot 4 owns the user-visible Android runtime, game systems, JRPG/social-link experiments, avatar/UI state, and WebView/plugin integration.

Godot talks to approved localhost APIs or typed Android plugin surfaces. It does not become a credential vault or arbitrary shell host.

## Edge Gallery
Edge Gallery is the Samsung-facing media/status surface.

It may show:
- generated previews;
- local image/video cards;
- build artifacts and status summaries;
- avatar/character references;
- approved gallery items;
- widget/edge-panel state.

It does not ingest secrets and does not decide build/release status.

## Failure behavior
OpenAI unavailable → fall back to local/mock/Ollama behavior where possible.  
Ollama unavailable → UI remains responsive and reports offline state.  
Cloudflare unavailable → do not mutate DNS; preserve the last verified public state.  
Google Cloud unavailable → continue local/F-Droid work and mark White Magic pending or `not_required`.  
Optional media service unavailable → chat/build shell still launches.  
Secure Folder cannot inspect daemon PIDs → probe localhost endpoints instead.

## Final authority
The Professor defines the goal. Lum compiles. Python policy defines allowed actions. Provider adapters execute. Git records Warp coordinates. GitHub Actions verifies builds. F-Droid signing/client-import evidence decides the final Black Magic distribution gate.
