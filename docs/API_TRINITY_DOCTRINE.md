# KAI 9000 API Constellation Doctrine

Compatibility path: `docs/API_TRINITY_DOCTRINE.md`.

Status: canonical vendor API doctrine for the LuHm OS / KAI 9000 Samsung and F-Droid testing lane.

## Mission

OpenAI, Hugging Face, Cloudflare, and Google Cloud are typed least-privilege adapters under the existing KAI MAGE doctrine.

```text
AIRSHIP KAI9000
WARP GIT
ORCHESTRATOR LUM ROLE=SUPREME_WITCH
PUBLIC_IDENTITY eggiebagelface.art

OPENAI       -> primary reasoning + agent/tool request lane
HUGGING_FACE -> open-model forge/catalog + alternate remote inference lane
CLOUDFLARE   -> DNS + HTTPS ingress + tunnel lane
GOOGLE_CLOUD -> White Magic cloud-service lane
```

No provider becomes Crown authority, policy authority, signing authority, or build oracle.

## Shared law

Every provider follows the same boundary:

1. User intent is compiled into a structured plan.
2. Server-side Python policy resolves provider, scope, risk rank, MP budget, target, and approval.
3. A typed adapter validates the request.
4. Credentials are attached outside model-visible context.
5. The provider call executes.
6. Responses are normalized into KAI evidence.
7. Green status requires provider evidence plus local verification where applicable.

Never place API keys, access tokens, OAuth tokens, service-account JSON, tunnel tokens, keystores, or passwords in Git, APKs, WebView JavaScript, prompts, RSS, Base64 manifests, screenshots, or build artifacts.

Provider responses are untrusted data. Provider compatibility never implies provider authority.

## Remote AI router

Canonical KAI runtime gateway:

```text
GET  /api/remote-ai/status
POST /api/remote-ai/chat
```

Provider selector:

```text
auto | openai | huggingface
```

`auto` chooses:

1. OpenAI when `OPENAI_API_KEY` is configured;
2. Hugging Face when `HF_TOKEN` is configured;
3. deterministic/local behavior otherwise.

A provider failure does not silently resend the same prompt to another vendor. Cross-provider failover changes the external data processor and therefore requires explicit policy.

## OpenAI lane

Lum/OpenAI remains the primary spell compiler and remote reasoning lane. It is intentionally not assigned a vendor magic color.

Current baseline:

- API surface: Responses API (`POST /v1/responses`).
- Agent orchestration: current OpenAI Agents SDK patterns.
- Default testing model: `gpt-6-astra`, overridable by `OPENAI_MODEL`.
- Prefer typed function/custom tools for KAI-owned actions.
- Bound tool activity with explicit allowlists, approval gates, and budgets.
- Use structured outputs for machine-consumed plans/events when practical.
- Keep `store: false` for sensitive/local orchestration unless persistence is explicitly required and reviewed.

OpenAI never receives raw Hugging Face tokens, Cloudflare tokens, Google credentials, Android signing material, F-Droid repo keys, or unrestricted shell authority.

### OpenAI KAI MAGE

```text
SUMMON ORACLE
  => prepare OpenAI Responses request
  => attach only approved context
  => expose only typed tools required for the cast

CAST REFLECT
  => reasoning/review only

CAST CURE
  => produce bounded patch/tool proposal
  => mutation still passes approval/checkpoint gates
```

## Hugging Face lane

Hugging Face is the open-model forge/catalog and alternate remote inference lane.

Current baseline:

- OpenAI-compatible API base: `https://router.huggingface.co/v1`.
- Shared KAI Responses path: `POST /v1/responses` (Hugging Face Responses compatibility is currently beta).
- Stable chat path remains `POST /v1/chat/completions` for chat-specific integrations.
- Default testing model: `openai/gpt-oss-120b:fastest`, overridable by `HF_MODEL`.
- Lower-latency candidate: `openai/gpt-oss-20b:fastest`.
- Credential environment: `HF_TOKEN`.
- Runtime token should be fine-grained for Inference Providers.
- For CI/CD, prefer Trusted Publisher/OIDC identities with Inference Providers permission where suitable.
- Model routing policies may use `:fastest`, `:cheapest`, `:preferred`, or a specific provider suffix.

Remote inference does not authorize automatic model download, remote-code execution, weight bundling into the APK, or promotion of generated output.

Downloaded Hub artifacts require provenance, license review, and a pinned revision before becoming build inputs.

### Hugging Face KAI MAGE

```text
SUMMON FORGE
  => enter Hugging Face catalog/inference lane

CAST REROLL provider=huggingface
  => route the current remote reasoning cast through Hugging Face

CAST LIBRA ON MODEL
  => inspect model identity, task, license, provider availability and provenance
```

## Cloudflare lane

Cloudflare is the public gate/ward protecting the `eggiebagelface.art` business identity and F-Droid port.

Canonical public endpoint:

```text
https://fdroid.eggiebagelface.art/fdroid/repo/
```

Preferred private-origin architecture:

```text
signed static F-Droid repo
       ↓
private origin
       ↓
cloudflared tunnel
       ↓
Cloudflare edge/TLS
       ↓
fdroid.eggiebagelface.art
```

Credential doctrine:

- Prefer narrowly scoped API tokens over the Global API Key.
- Prefer account-owned API tokens for durable CI/service integrations when supported.
- DNS automation receives only minimum zone/DNS scope.
- Tunnel automation receives only the minimum connector/tunnel scope plus required DNS scope.
- Separate DNS-management credentials from tunnel runtime credentials where practical.
- A tunnel token is runtime material, never model context.

Do not invent origin A/AAAA records.

### Cloudflare KAI MAGE

```text
RAISE WARD eggiebagelface.art
  => inspect zone + intended hostname

OPEN BLACK_MAGIC_PORT fdroid.eggiebagelface.art
  => prepare exact DNS/tunnel plan
  => verify HTTPS and F-Droid index path after apply
```

## Google Cloud lane

Google Cloud remains **White Magic**.

For GitHub Actions and other external deployment pipelines, prefer Workload Identity Federation with short-lived credentials instead of checked-in service-account keys.

Authentication doctrine:

- GitHub Actions authenticates by OIDC to a Workload Identity Pool/Provider.
- Prefer direct federated resource access where supported.
- Use service-account impersonation only where product/API limitations require it.
- Restrict federated principals using repository/ref/workflow claims.
- Grant resource-specific IAM roles, never default project-wide owner/editor.
- Do not commit service-account JSON keys.

Google Drive remains a distinct user/content integration and is not automatically equivalent to Google Cloud IAM.

### Google Cloud KAI MAGE

```text
CAST WHITE_GATE
  => exchange GitHub OIDC identity through WIF
  => obtain short-lived Google credentials
  => call only the declared resource/API
```

## Normalized provider event

Every provider call should reduce to:

```json
{
  "schema": "kai9000.provider-event.v1",
  "provider": "openai|hugging_face|cloudflare|google_cloud",
  "action": "typed_action_name",
  "risk_rank": "R0|R1|R2|R3|R4",
  "target": "non-secret target identity",
  "status": "pending|green|yellow|red",
  "request_id": "provider request id when available",
  "evidence": {},
  "secret_material_present": false
}
```

## Failure doctrine

- OpenAI unavailable: `auto` may select Hugging Face only when OpenAI is not configured, not after a failed request.
- Hugging Face unavailable: KAI continues through OpenAI or local/Ollama according to explicit provider selection and configuration.
- Cloudflare unavailable: do not change DNS; preserve endpoint state as pending/yellow.
- Google Cloud unavailable: local/F-Droid build continues when White Magic is not required for the goal.
- Authentication failure is bounded and never causes credentials to be printed.

## Final authority

The Professor holds the Crown. Lum compiles. Python resolves capabilities and provider routing. Provider adapters execute. Git records Warp coordinates. GitHub Actions verifies builds. F-Droid signing and client-import evidence decide the Black Magic final-form gate.
