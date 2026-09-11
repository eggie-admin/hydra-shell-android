# LuHm OS Hugging Face Provider Doctrine

**Status:** canonical optional remote-provider doctrine for the Samsung standalone APK lane.  
**Verified:** 2026-09-10 against current Hugging Face Inference Providers documentation and Hub metadata.

## Mission

Hugging Face is an open-model forge/catalog and optional remote inference lane beside OpenAI. It is not policy authority, signing authority, build authority, release authority, secret storage, or a required Android runtime dependency.

The LuHm OS APK must install and launch with no Hugging Face token and no Hugging Face network availability.

## Current API baseline

Hugging Face Inference Providers exposes an OpenAI-compatible router:

```text
https://router.huggingface.co/v1
```

Current documented Responses-compatible path:

```text
POST https://router.huggingface.co/v1/responses
```

The Responses interface is currently documented as beta. The OpenAI-compatible chat endpoint remains:

```text
POST https://router.huggingface.co/v1/chat/completions
```

Use task-appropriate Hugging Face clients/APIs for modalities that are not covered by the chosen compatible endpoint.

## Authentication

Gateway credential:

```text
HF_TOKEN
```

Use a fine-grained token with only the required Inference Providers permission. Prefer short-lived/OIDC-style CI authorization where supported.

Never place a Hugging Face token in:

- Git;
- APK/AAB resources or assets;
- Godot resources;
- WebView JavaScript or storage;
- prompts or model context;
- screenshots or logs;
- Base64 manifests;
- build artifacts.

The production Android app may call an approved authenticated gateway, but it must not ship a permanent Hugging Face secret.

## Reference models

Current verified Hub repositories:

```text
openai/gpt-oss-120b
openai/gpt-oss-20b
```

Both are recorded by the Hub as Apache-2.0 text-generation models and currently expose live Inference Providers.

LuHm routing references:

```text
HF_MODEL=openai/gpt-oss-120b:fastest
HF_MODEL_FAST=openai/gpt-oss-20b:fastest
```

Provider suffixes such as `:fastest`, `:cheapest`, `:preferred`, or an explicit provider are routing policy. For reproducible tests, record the resolved model/provider and pin a revision or provider where the target surface permits it.

Model IDs are configuration, not permanent architecture. A model rename, removal, or better replacement must not require an APK architecture rewrite.

## Runtime router

Application-facing contract:

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

`auto` may select Hugging Face only when it is explicitly configured. An upstream provider error does not silently resend the same prompt to another vendor.

No provider configured is a valid state. Base application launch and non-cloud game/UI functions remain available.

## Forge and download doctrine

Remote inference access does not authorize model download or redistribution.

Before a Hub artifact becomes a build/runtime input, record:

- repository ID;
- immutable revision/commit;
- license;
- expected files and hashes where practical;
- runtime target;
- approval/evidence timestamp.

Default to `trust_remote_code=false`. Large model weights stay outside APK/source control unless a future on-device model lane explicitly approves packaging/download, licensing, storage, RAM/VRAM budget, and update behavior.

## Relationship to OpenAI

The Hugging Face Responses-compatible interface may use the OpenAI SDK, but this does not make the providers interchangeable authorities.

OpenAI remains the primary remote reasoning lane. Hugging Face remains the open-model forge/catalog and alternate inference lane. Outputs from both are untrusted advisory data until LuHm application policy validates them.

## GREEN requirements

Hugging Face integration can be called runtime GREEN only when:

1. adapter/router tests pass;
2. no secret material is committed or emitted;
3. provider status does not reveal credentials;
4. an authorized live request succeeds when the lane is intentionally configured;
5. provider/model/request evidence is recorded without secrets;
6. base Android launch remains independent of Hugging Face;
7. the Samsung standalone APK gates still pass.

Until a live authenticated request is proven for the current configuration, use `HF_API_WIRED`, not `HF_API_LIVE_GREEN`.
