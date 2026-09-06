# KAI 9000 Hugging Face API Reroll

Status: testing doctrine for `testing/luhm-os-android`.

## Mission

Hugging Face becomes a first-class remote inference/forge lane beside OpenAI without becoming policy authority, build authority, signing authority, or Crown authority.

```text
AIRSHIP KAI9000
WARP GIT
ORCHESTRATOR LUM ROLE=SUPREME_WITCH

OPENAI       -> primary remote reasoning / typed tool lane
HUGGING_FACE -> open-model forge + catalog + alternate remote inference lane
OLLAMA       -> local inference daemon / offline fallback
PYTHON3      -> provider router + policy authority
```

## Current API baseline

Hugging Face Inference Providers exposes an OpenAI-compatible router at:

```text
https://router.huggingface.co/v1
```

KAI 9000 uses the beta Responses-compatible endpoint for the shared remote-AI contract:

```text
POST https://router.huggingface.co/v1/responses
```

The stable OpenAI-compatible chat endpoint remains available for workloads that specifically need Chat Completions:

```text
POST https://router.huggingface.co/v1/chat/completions
```

Do not assume every non-chat task is supported through the OpenAI-compatible surface. Image, video, embeddings, speech, or provider-specific jobs should use the appropriate Hugging Face Inference client/API contract instead of pretending all modalities share one endpoint.

## Authentication

Runtime credential environment variable:

```text
HF_TOKEN
```

Use a fine-grained token carrying only the permissions required for Inference Providers. The token is server-side runtime material.

Never place an HF token in:

- Git;
- Android resources;
- WebView JavaScript;
- APKs;
- prompts;
- RSS;
- Base64 manifests;
- screenshots;
- build artifacts;
- model context.

For CI/CD, prefer Hugging Face Trusted Publishers/OIDC with Inference Providers access where that path fits the workflow, rather than maintaining a long-lived broad token.

## Model routing

Testing default:

```text
openai/gpt-oss-120b:fastest
```

Lower-latency candidate:

```text
openai/gpt-oss-20b:fastest
```

The provider suffix is policy, not decoration:

- `:fastest` -> choose the currently fastest available provider for the model;
- `:cheapest` -> prefer lowest output-token price;
- `:preferred` -> follow configured provider preference order;
- `:<provider>` -> force one explicit provider when compatibility/performance must be pinned.

KAI must record the resolved model string in evidence. For deterministic release/eval workflows, pin a model revision/provider where the target API allows it instead of relying on a floating routing policy.

## Runtime router

KAI exposes:

```text
GET  /api/remote-ai/status
POST /api/remote-ai/chat
```

Provider values:

```text
auto
openai
huggingface
```

`auto` resolves in this order:

1. OpenAI when `OPENAI_API_KEY` exists;
2. Hugging Face when `HF_TOKEN` exists;
3. deterministic/local path when neither credential exists.

An upstream provider error does **not** silently forward the same prompt to a second vendor. Cross-provider failover requires a separate explicit policy decision because it changes the data processor receiving the prompt.

## OpenAI + Hugging Face relationship

The APIs are intentionally normalized at the KAI gateway, but the providers are not interchangeable authorities.

OpenAI native lane:

- current first-party Responses API;
- flagship reasoning/coding models;
- current Agents SDK and OpenAI hosted-tool ecosystem when explicitly approved.

Hugging Face lane:

- open-model catalog;
- Inference Providers routing across supported inference partners;
- OpenAI-compatible Responses/Chat interface for supported model workloads;
- future fine-tuning/model-evaluation/reference workflows under explicit provenance rules.

Provider output from either lane is untrusted advisory data until Python policy validates it.

## Download doctrine

Remote inference access does not authorize model download.

For model artifacts downloaded from the Hub:

- record model repository and license;
- pin revision/commit for reproducibility;
- do not enable arbitrary remote code merely because a model repository requests it;
- verify expected file types and hashes where practical;
- keep large weights outside APK/source control;
- treat local Ollama conversion/import as a separate forge operation.

## KAI MAGE compiler

```text
SUMMON ORACLE
  => OpenAI primary remote reasoning lane

SUMMON FORGE
  => Hugging Face model/inference lane

CAST REROLL provider=huggingface
  => select Hugging Face explicitly for this remote reasoning cast

CAST REROLL provider=auto
  => OpenAI if configured, else Hugging Face, else local deterministic path

CAST LIBRA ON MODEL
  => inspect model identity, provider availability, license, task and provenance
```

No spell can make a provider self-authorize a file mutation, deployment, DNS change, signing action, or release promotion.

## GREEN requirements

The Hugging Face reroll is runtime-green only after:

1. provider router tests pass;
2. source compiles under the declared Python runtime;
3. no HF credentials are committed or emitted;
4. `/api/remote-ai/status` reports provider configuration without revealing secrets;
5. a live authenticated HF Responses request succeeds when an authorized token is configured;
6. returned provider/model/request evidence is recorded without secret material;
7. the Android ULTIMA build remains green after the router mutation.

Until the live authenticated call is proven, report `HF_API_WIRED` rather than `HF_API_LIVE_GREEN`.
