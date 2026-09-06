# KAI 9000 API Trinity Doctrine

Status: canonical vendor API doctrine for the LuHm OS / KAI 9000 Samsung and F-Droid testing lane.

## Mission

Reroll OpenAI, Cloudflare, and Google Cloud as typed, least-privilege adapters under the existing KAI MAGE doctrine.

```text
AIRSHIP KAI9000
WARP GIT
ORCHESTRATOR LUM ROLE=SUPREME_WITCH
PUBLIC_IDENTITY eggiebagelface.art

OPENAI      -> reasoning + agent/tool request lane
CLOUDFLARE  -> DNS + HTTPS ingress + tunnel lane
GOOGLE_CLOUD -> White Magic cloud-service lane
```

No provider becomes Crown authority, policy authority, signing authority, or build oracle.

## Shared law

All three providers follow the same boundary:

1. User intent is compiled into a structured plan.
2. Server-side policy resolves provider, scope, risk rank, MP budget, target, and approval.
3. A typed adapter validates the request.
4. Credentials are attached outside model-visible context.
5. The provider call executes.
6. Responses are normalized into KAI evidence.
7. Green status requires provider evidence plus local verification where applicable.

Never place API keys, OAuth tokens, service-account JSON, tunnel tokens, keystores, or passwords in Git, APKs, WebView JavaScript, prompts, RSS, Base64 manifests, screenshots, or build artifacts.

## OpenAI lane

Lum/OpenAI remains the spell compiler and remote reasoning lane. It is intentionally not assigned a vendor magic color.

Current integration baseline:

- API surface: Responses API (`POST /v1/responses`).
- Agent orchestration: current OpenAI Agents SDK patterns.
- Default model alias for the testing reroll: `gpt-6-astra`, overridable by `OPENAI_MODEL`.
- Prefer typed custom/function tools for KAI-owned actions.
- Use hosted tools only when they directly fit the task and their data boundary is acceptable.
- Bound model tool activity with explicit tool allowlists, `tool_choice`, and maximum tool-call budgets where tools are exposed.
- Use structured outputs for machine-consumed plans/events when practical.
- Keep `store: false` for sensitive/local orchestration unless persistence is explicitly required and reviewed.

OpenAI never receives raw Cloudflare tokens, Google credentials, Android signing material, F-Droid repo keys, or unrestricted shell authority.

### OpenAI KAI MAGE

```text
SUMMON ORACLE
  => prepare Responses API request
  => attach only approved context
  => expose only typed tools required for the cast
  => enforce MP/tool-call/output budgets

CAST REFLECT
  => reasoning/review only

CAST CURE
  => produce bounded patch/tool proposal
  => mutation still passes normal approval/checkpoint gates
```

## Cloudflare lane

Cloudflare is the public gate/ward protecting the `eggiebagelface.art` business identity and F-Droid port.

Canonical public endpoint:

```text
https://fdroid.eggiebagelface.art/fdroid/repo/
```

Preferred architecture for a privately hosted F-Droid origin:

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
- DNS-only automation should receive only the minimum zone/DNS write scope for `eggiebagelface.art`.
- Tunnel automation receives only the minimum Cloudflare Tunnel/Connector scope plus required DNS scope.
- Separate DNS-management credentials from tunnel runtime credentials where practical.
- A tunnel token is runtime material, not a repository secret or model input.

Canonical F-Droid DNS intent:

```text
record: fdroid.eggiebagelface.art
purpose: custom F-Droid repository
preferred transport: proxied HTTPS via Cloudflare Tunnel when privately hosted
```

Do not invent origin A/AAAA records. Deployment resolves the real origin/tunnel target first.

### Cloudflare KAI MAGE

```text
RAISE WARD eggiebagelface.art
  => inspect zone + intended hostname

OPEN BLACK_MAGIC_PORT fdroid.eggiebagelface.art
  => prepare exact DNS/tunnel plan
  => require scoped Cloudflare capability
  => verify HTTPS and F-Droid index path after apply

APPEASE GODS
  => DNS + TLS + canonical business identity + repo fingerprint agree
```

## Google Cloud lane

Google Cloud remains **White Magic**.

For GitHub Actions and other external deployment pipelines, prefer Workload Identity Federation (WIF) with short-lived credentials instead of checked-in service-account keys.

Authentication doctrine:

- GitHub Actions authenticates by OIDC to a Google Cloud Workload Identity Pool/Provider.
- Prefer direct resource access for the federated principal when the target Google Cloud API supports it.
- Use service-account impersonation only where product/API limitations require it.
- Restrict the federated principal using repository, branch/ref, workflow, and other available OIDC attributes/conditions.
- Grant resource-specific IAM roles rather than project-wide owner/editor roles.
- Do not commit service-account JSON keys.

Google Cloud roles are selected per capability. Examples may include narrowly scoped access to Cloud Storage, Artifact Registry, Secret Manager, Cloud Run, or another explicitly chosen service. There is no default broad Google Cloud role for KAI 9000.

Google Drive remains a distinct user/content integration and is not automatically equivalent to Google Cloud IAM.

### Google Cloud KAI MAGE

```text
CAST WHITE_GATE
  => exchange GitHub OIDC identity through WIF
  => obtain short-lived Google credentials
  => call only the declared resource/API

CAST WHITE_MIRROR
  => copy approved release/evidence artifact to an authorized Google destination
  => no secret material
```

## Normalized provider event

Every provider call should be reducible to:

```json
{
  "schema": "kai9000.provider-event.v1",
  "provider": "openai|cloudflare|google_cloud",
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

- OpenAI unavailable: KAI continues through Ollama/local deterministic paths where possible.
- Cloudflare unavailable: do not change DNS; preserve the existing endpoint and publish state as pending/yellow.
- Google Cloud unavailable: local/F-Droid build continues; White Magic is marked pending or `not_required` according to the goal.
- Provider authentication failure is not retried indefinitely and never causes credentials to be printed.

## Final authority

The Professor holds the Crown. Lum compiles. Python policy resolves capabilities. Provider adapters execute. Git records Warp coordinates. GitHub Actions verifies builds. F-Droid signing and client-import evidence decide the Black Magic final-form gate.
