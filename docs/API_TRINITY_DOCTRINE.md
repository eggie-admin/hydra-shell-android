# LuHm OS API Constellation Doctrine

**Status:** canonical vendor-adapter doctrine for the Samsung standalone APK lane.  
**Verified:** 2026-09-10 for the OpenAI and Hugging Face model/API references below.

## Mission

OpenAI, Hugging Face, Cloudflare, and Google Cloud are optional typed adapters under LuHm OS policy. No provider becomes policy authority, signing authority, build authority, release authority, root authority, or a boot dependency for the Android APK.

## Shared law

1. User intent becomes a typed plan.
2. LuHm application policy resolves provider, scope, risk, target, and approvals.
3. A bounded adapter validates the request.
4. Credentials are attached outside model-visible context and outside the distributable APK.
5. Provider output is normalized as untrusted evidence/data.
6. CI and device evidence, not provider claims, determine GREEN.

Never place API keys, access tokens, service-account JSON, tunnel tokens, keystores, signing passwords, or recovery secrets in Git, APK/AAB assets, Godot resources, WebView JavaScript/storage, prompts, screenshots, Base64 manifests, or build artifacts.

## Standalone Android boundary

The Samsung SM-S721U1 production application must install and launch without:

- a cloud credential;
- Termux or Acode/AcodeX;
- Secure Folder;
- VNC/websockify;
- an external Python/Ollama/localhost daemon;
- root or Shizuku.

Cloud/provider features are enhancements. Their absence must degrade gracefully instead of blocking base application launch.

## Remote AI gateway

Canonical application-facing contract:

```text
GET  /api/remote-ai/status
POST /api/remote-ai/chat
```

Provider selector:

```text
auto | openai | huggingface
```

`auto` chooses only among explicitly configured adapters. A failed provider request is not silently resent to another provider because that changes the external data processor receiving the prompt.

The production APK does not embed permanent vendor API keys. Remote AI may be reached through a reviewed authenticated gateway or another explicitly approved short-lived credential design.

## OpenAI lane

OpenAI is the primary remote reasoning and typed-agent lane.

Current first-party baseline verified 2026-09-10:

```text
API:        Responses API
fast model: gpt-5.6-luna
deep model: gpt-5.6-sol
```

Configuration:

```text
OPENAI_MODEL_FAST=gpt-5.6-luna
OPENAI_MODEL_DEEP=gpt-5.6-sol
```

Model IDs are runtime configuration, not architectural constants. CI/evidence should record the actual resolved model used for an evaluation or build-affecting decision.

Prefer typed tools and structured outputs for machine-consumed plans. Tool execution still passes LuHm allowlists, approval gates, and policy. Transport details such as persistent sockets remain adapter implementation choices and must be revalidated against current first-party docs before becoming normative doctrine.

OpenAI never receives Hugging Face tokens, Cloudflare/Google credentials, Android signing material, F-Droid signing keys, or unrestricted shell authority.

## Hugging Face lane

Hugging Face is the open-model forge/catalog and alternate remote inference lane.

Current verified baseline:

```text
base:      https://router.huggingface.co/v1
responses: POST /v1/responses   # documented beta
chat:      POST /v1/chat/completions
reference: openai/gpt-oss-120b:fastest
fast:      openai/gpt-oss-20b:fastest
```

The referenced `openai/gpt-oss-120b` and `openai/gpt-oss-20b` Hub repositories are Apache-2.0 models. Provider suffixes are routing policy and should be captured in evidence when reproducibility matters.

`HF_TOKEN` remains gateway/server-side secret material. Remote inference does not authorize automatic weight download, remote-code execution, or bundling model weights into the APK.

Downloaded Hub inputs require pinned revision, license, provenance, and `trust_remote_code=false` by default.

Detailed doctrine: `docs/HUGGINGFACE_API_REROLL.md`.

## Cloudflare lane

Cloudflare is an optional public ingress/security/distribution adapter. It does not define Android runtime architecture.

Prefer narrowly scoped API tokens and separate DNS/tunnel scopes. A tunnel credential is runtime infrastructure material, never model context or APK content. Do not invent origin records or silently expose private services.

## Google Cloud lane

Google Cloud remains an optional build/service adapter. For GitHub Actions, prefer Workload Identity Federation and short-lived credentials over checked-in service-account keys. Restrict principals using repository/ref/workflow claims and grant only resource-specific IAM roles.

Google Drive is a distinct content/recovery integration and is not automatically equivalent to Google Cloud IAM.

## Normalized provider event

```json
{
  "schema": "luhmos.provider-event.v2",
  "provider": "openai|hugging_face|cloudflare|google_cloud",
  "action": "typed_action_name",
  "risk_rank": "R0|R1|R2|R3|R4",
  "target": "non-secret target identity",
  "status": "pending|green|yellow|red",
  "request_id": "provider request id when available",
  "resolved_model": "model/provider identity when applicable",
  "evidence": {},
  "secret_material_present": false
}
```

## Failure doctrine

- no AI provider configured: base APK remains functional;
- selected provider unavailable: report the failure, do not silently cross-vendor replay;
- Cloudflare unavailable: preserve distribution/ingress state as pending rather than mutating DNS blindly;
- Google Cloud unavailable: local source/build work continues when the cloud lane is not required;
- authentication failure: fail closed without printing credentials.

## Final authority

The Professor holds final release authority. Lum compiles intent. LuHm application policy authorizes. Provider adapters execute bounded calls. Git records lineage. GitHub Actions proves builds. Persistent Android signing plus physical-device install/update evidence determine Samsung release GREEN.
