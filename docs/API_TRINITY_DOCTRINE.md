# LuHm OS API Constellation Doctrine

**Status:** proposal-synced vendor-adapter doctrine for the Samsung standalone APK lane.  
**Verified:** 2026-09-17 against current first-party documentation where available.

## Mission

The LuHm OS vendor spine is deliberately narrow:

```text
OpenAI + Google + GitHub + Cloudflare + Hugging Face
```

Each vendor is a bounded adapter under LuHm OS policy. No provider becomes Crown authority, signing authority, release authority, root authority, or an Android boot dependency.

## Shared law

1. User intent becomes a typed plan.
2. LuHm policy resolves provider, scope, risk, target, and approvals.
3. A bounded adapter validates the request.
4. Credentials are attached outside model-visible context and outside the distributable APK.
5. Provider output is normalized as untrusted evidence/data.
6. CI and device evidence, not provider claims, determine GREEN.
7. A failed vendor call never silently grants authority to another vendor.
8. Canonical merge, deploy, public release, and Crown each require explicit Professor authority.

Never place API keys, access tokens, service-account JSON, tunnel tokens, keystores, signing passwords, or recovery secrets in Git, APK/AAB assets, Godot resources, WebView JavaScript/storage, prompts, screenshots, Base64 manifests, or build artifacts.

## Standalone Android boundary

The Samsung application must install and launch without a cloud credential, Termux/Acode/VNC bridge, external localhost daemon, root, or Shizuku. Vendor features are enhancements and must fail closed without blocking the base cockpit.

## OpenAI lane

OpenAI is the primary remote reasoning and typed-agent lane.

Current baseline verified 2026-09-17:

```text
API:        Responses API
fast model: gpt-5.6-luna
deep model: gpt-5.6-sol
endpoint:   https://api.openai.com/v1/responses
```

Configuration remains server-side:

```text
OPENAI_MODEL_FAST=gpt-5.6-luna
OPENAI_MODEL_DEEP=gpt-5.6-sol
OPENAI_API_KEY=<protected secret store only>
```

Model IDs are runtime configuration, not architectural constants. Record the resolved model in evidence for build-affecting or evaluation decisions. Prefer typed tools and structured outputs. Tool execution still passes LuHm allowlists, policy, and approval gates.

The connected OpenAI Platform project label is `LuHm OS`; persistent project identifiers are not committed to public source merely for branding consistency.

## Google lane

Google has two intentionally separate sublanes.

### Google Cloud

GitHub Actions authenticates to Google Cloud with OIDC and Workload Identity Federation instead of checked-in service-account JSON. The issuer is:

```text
https://token.actions.githubusercontent.com
```

The Google-side provider must have an attribute condition. For GitHub repositories using immutable OIDC subject claims, trust policy should bind the immutable owner and repository identities and the intended workflow/ref scope rather than relying only on mutable repository names.

Provisioning remains manual and requires the typed confirmation `PROVISION`. Resource IAM stays least-privilege. The live Google Cloud trust policy is external state and must not be claimed GREEN unless it is read back from Google Cloud.

### Google Drive

Google Drive is the recovery mirror and approved artifact/archive lane. GitHub remains canonical versioned source history. Drive is not a secret store and Drive access does not imply Google Cloud IAM authority.

## GitHub lane

GitHub is the canonical versioned source, CI forge, pull-request evidence surface, and OIDC issuer for Google Cloud federation.

Canonical branch:

```text
luhmos-main
```

Desired server-side governance:

```text
pull request required before canonical mutation
block direct push
block force push
block branch deletion
bypass policy chosen explicitly by Professor
required status-check selection chosen explicitly by Professor
```

Observed on 2026-09-17: `luhmos-main` reports `protected=false` and the repository rulesets endpoint returns an empty list. This is tracked as `RED_EXTERNAL`; workflow-level locks remain useful but are not a substitute for server-side branch governance.

GitHub Actions workflows that request OIDC tokens use `id-token: write`; this permits token minting, not arbitrary repository writes. Workflow permissions stay minimal and credentials remain outside repository content.

## Cloudflare lane

Cloudflare is the public edge, DNS/tunnel security boundary, and optional static distribution lane. It does not define Android runtime architecture.

Use narrowly scoped API tokens. DNS capability and tunnel capability are separate concerns. A tunnel token is runtime infrastructure material and never model context or APK content.

Production static publication requires an explicit typed `YES` confirmation. The Wrangler version used for deploy and dry-run validation is pinned to `4.119.0` in this candidate so the validation toolchain and mutation toolchain cannot drift apart silently.

Do not invent origin records, expose private `.lan` names publicly, or require router port forwarding. Live Cloudflare account token scopes and tunnel state remain external state until read back through an authorized account connector.

## Hugging Face lane

Hugging Face is the open-model catalog and alternate remote inference lane.

Current baseline verified 2026-09-17:

```text
base:      https://router.huggingface.co/v1
responses: POST /v1/responses   # beta
chat:      POST /v1/chat/completions
reference: openai/gpt-oss-120b:fastest
fast:      openai/gpt-oss-20b:fastest
```

The Responses API is OpenAI-SDK compatible. `:fastest`, `:cheapest`, and `:preferred` are routing policies; a specific provider suffix can be used when reproducibility requires it. Evidence should record the resolved provider when provider choice matters.

`HF_TOKEN` is server/gateway secret material with only the inference-provider permission needed. Remote inference does not authorize automatic weight download, remote-code execution, or bundling model weights into the APK. Downloaded Hub inputs require pinned revision, license/provenance review, and `trust_remote_code=false` by default.

## Remote AI gateway

Only OpenAI and Hugging Face participate in the AI-provider selector:

```text
GET  /api/remote-ai/status
POST /api/remote-ai/chat
provider = auto | openai | huggingface
```

Google, GitHub, and Cloudflare are infrastructure/content/control adapters and are not silently treated as replacement LLM processors. `auto` chooses only among explicitly configured AI adapters. A failed provider request is not silently resent to another provider because that changes the external data processor receiving the prompt.

## Normalized provider event

```json
{
  "schema": "luhmos.provider-event.v3",
  "provider": "openai|google|github|cloudflare|hugging_face",
  "lane": "optional vendor sublane",
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

## Drift policy

A vendor lane is GREEN only for what was actually verified. Static source checks may prove the repository contract, but they do not prove live Cloudflare token scopes, Google IAM/WIF conditions, Hugging Face account state, or GitHub server protection unless those external surfaces are read back.

Current known external debt is carried explicitly rather than painted green:

- GitHub server-side canonical branch governance is RED_EXTERNAL until protection/rulesets are active and read back.
- Google Cloud WIF trust conditions are UNVERIFIED until read back from Google Cloud.
- Cloudflare live token/tunnel state is UNVERIFIED without an authorized account connector.
- Hugging Face live account state is UNVERIFIED when account-level read actions are unavailable.

## Final authority

Professor holds final release authority. Lum compiles intent. LuHm policy authorizes. Vendor adapters execute bounded calls. Git records lineage. GitHub Actions proves builds. Persistent Android signing plus physical-device install/update evidence determine Samsung release GREEN.
