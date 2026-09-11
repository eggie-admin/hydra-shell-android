# AI Stack: Lum, OpenAI, Hugging Face, optional local AI, Python policy and Godot 4

## Status

Canonical AI/provider architecture for the LuHm OS Samsung standalone APK lane.

The base Android application must install and launch without Termux, Acode/AcodeX, Secure Folder, VNC, Ollama, Python daemons, cloud credentials, or any other separately started runtime.

## Design principle

```text
User
  ↓
LuHm OS Android APK
Godot 4 UI/game runtime + bounded Kotlin bridges
  ↓ typed requests
application policy/control contract
  ├── packaged/offline deterministic features
  └── optional authenticated AI gateway
         ├── OpenAI
         └── Hugging Face
```

No provider, model, framework, or UI surface becomes operating-system authority, signing authority, release authority, or unrestricted shell authority.

## Lum / provider routing

Lum is the user-facing intent and typed-plan layer. Provider selection is policy, not personality.

Canonical application-facing contract remains:

```text
GET  /api/remote-ai/status
POST /api/remote-ai/chat
```

Provider values:

```text
auto | openai | huggingface
```

`auto` selects only among explicitly configured remote adapters. A failed request is not silently replayed to another vendor because that would change the external data processor receiving the prompt.

If no remote provider is configured, the APK still launches and keeps non-cloud features available.

## OpenAI / Lum speed doctrine

OpenAI is the primary remote reasoning/agent lane.

Verified against current first-party OpenAI model and API documentation on 2026-09-11:

```text
Lum default/front door:       gpt-5.6-luna
Lum default reasoning effort: none
Lum default output verbosity: low
Lum API surface:              Responses API
Lum transport:                streaming
Lum paid latency mode:        service_tier=fast
Deep architecture/review:     gpt-5.6-sol
```

GPT-5.6 Luna is the fastest and lowest-cost model in the GPT-5.6 family. Fast mode may be requested per Responses API call with `service_tier=fast` (or `priority`; the returned service tier may normalize to the provider's served tier).

Configuration remains overridable rather than compiled into application code:

```text
OPENAI_MODEL_FAST=gpt-5.6-luna
OPENAI_MODEL_DEEP=gpt-5.6-sol
OPENAI_REASONING_FAST=none
OPENAI_VERBOSITY_FAST=low
OPENAI_SERVICE_TIER_FAST=fast
```

### Routing rule

Use Luna for the overwhelming majority of interactive Lum traffic:

- chat and command parsing;
- intent classification;
- typed tool selection;
- status/help/UI responses;
- short coding assists;
- deterministic orchestration proposals;
- high-volume agent turns.

Escalate to Sol only when the task crosses a deliberate complexity threshold, for example:

- architecture redesign;
- difficult multi-file debugging;
- release/security audits;
- high-consequence code review;
- deep research/synthesis;
- a failed Luna attempt where more reasoning is actually useful.

Do not use GPT-6/Astra as Lum's default front door merely because it is more capable. Capability escalation is explicit and exceptional; latency remains the primary interactive objective.

### Fast mode policy

`service_tier=fast` is a paid API latency optimization, not a correctness requirement. The application may fall back to the normal/default service tier if Fast mode is unavailable, rate-limited, or deliberately disabled for cost control.

Fast mode does not change Lum's authority. Faster inference never grants permission to mutate source, root a device, sign artifacts, publish releases, or execute unrestricted shell commands.

### ChatGPT Pro versus OpenAI API billing

ChatGPT Pro and the OpenAI API are separate billing systems. A ChatGPT Pro subscription does not fund arbitrary API calls made by the LuHm OS APK or its gateway.

ChatGPT Pro can provide access to paid ChatGPT/Work/Codex experiences, but a programmatic in-app Lum agent uses the OpenAI API and therefore requires separately configured API billing/credits and a server-side/project API credential.

`OPENAI_API_KEY` is secret server/gateway material. It never belongs in Android resources, WebView JavaScript, Godot project resources, Git, APK/AAB artifacts, Base64 manifests, prompts, screenshots, logs, or model context.

The production APK must not require a permanent OpenAI key to boot.

## Hugging Face

Hugging Face is the open-model forge/catalog and alternate remote inference lane.

Verified against current Hugging Face Inference Providers documentation on 2026-09-10:

```text
OpenAI-compatible base: https://router.huggingface.co/v1
Responses endpoint:      POST /v1/responses   (beta)
Chat endpoint:           POST /v1/chat/completions
```

Current reference models:

```text
openai/gpt-oss-120b:fastest   # remote quality/reference lane
openai/gpt-oss-20b:fastest    # lower-latency candidate
```

Both referenced Hub repositories are Apache-2.0 models. Provider suffixes such as `:fastest`, `:cheapest`, `:preferred`, or an explicit provider are routing policy and must be recorded in evidence when reproducibility matters.

`HF_TOKEN` is secret gateway material. It is never stored in the APK, Git, prompts, WebView storage, logs, screenshots, build artifacts, or model context.

Remote inference permission does not authorize automatic model download. Any downloaded Hub artifact requires repository, revision, license, file provenance, and `trust_remote_code=false` by default.

## Optional local AI

Local inference remains an optional integration lane, not a production boot dependency.

Historical Ollama/localhost work may be reused as development or desktop integration reference, but the Samsung S24 FE production APK must not require an external Ollama daemon or Termux process to launch.

If a future on-device model is packaged or downloaded, it requires an explicit Android storage/runtime design, license/provenance record, device-resource budget, and release-gate review.

## Python 3

Python 3 remains the canonical reference language for policy, provider adapters, tests, build orchestration, evidence generation, and backend services.

For Android production, no external Python interpreter may be required. Policy logic used at runtime must either be migrated to packaged app code, deliberately bundled inside the application boundary, or hosted behind an optional authenticated network adapter.

## Godot 4

Godot 4 owns the user-visible Android runtime and game/application systems, including JRPG, dating/social-link, avatar, media, and UI state.

Godot must not hold permanent cloud credentials or become an arbitrary shell. Android-specific secure/platform capabilities are exposed through bounded native bridges.

Game donor and licensing provenance is defined in:

```text
project/hydra/games/GODOT4_JRPG_DATING_DONORS_20260910.json
```

## Failure behavior

- no cloud provider configured -> APK still opens;
- OpenAI unavailable -> report OpenAI unavailable;
- Fast mode unavailable -> fall back to normal OpenAI service tier unless policy says fail closed;
- Luna insufficient for a task -> policy may explicitly escalate to Sol;
- Hugging Face unavailable -> report Hugging Face unavailable;
- selected provider fails -> do not silently resend to another provider;
- optional local model unavailable -> keep base UI/game/runtime functional;
- optional media/provider integrations fail -> degrade gracefully rather than blocking launcher start.

## Security boundary

Cloud credentials stay outside the distributable application. A remote AI feature may use an authenticated gateway or another reviewed short-lived credential design, but static vendor secrets are never bundled into the APK.

## Final authority

The Professor defines the goal. Lum compiles intent. Application policy authorizes. Models propose. Bounded tools execute. CI proves. Persistent signing and physical-device install/update evidence decide Android release GREEN.
