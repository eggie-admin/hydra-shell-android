# AI Stack: Lum, OpenAI, Hugging Face, Ollama, Python 3 and Edge Gallery

## Design principle

The AI stack is split by responsibility so no single model or vendor becomes the operating system.

```text
User / Samsung cockpit
        ↓
Lum intent layer
        ↓
Python policy + provider router + typed tools
   ↙               ↓                ↘
OpenAI        Hugging Face          Ollama
primary        forge/API             local
remote         alternate             inference
reasoning      remote lane           daemon
      \            |              /
       \           |             /
          normalized result
                 ↓
          Godot / Edge Gallery
```

## Lum / provider router

Lum is the user-facing spell compiler/persona layer. Python owns provider selection and policy.

Canonical remote endpoint:

```text
POST /api/remote-ai/chat
```

Provider selector:

```text
auto | openai | huggingface
```

`auto` prefers configured OpenAI, then configured Hugging Face, then deterministic/local behavior. A failed provider request is not silently replayed to a different external provider.

## OpenAI

OpenAI is the primary remote reasoning and agent lane.

Use OpenAI for:

- complex coding/review tasks;
- structured intent generation;
- typed function/tool requests;
- guardrailed agent workflows;
- current first-party Responses/Agents capabilities.

Current testing default model: `gpt-6-astra`.

`OPENAI_API_KEY` is server-side only. It never belongs in Android resources, WebView JavaScript, source control, build artifacts, Base64 manifests, or debug APKs.

## Hugging Face

Hugging Face is the open-model forge/catalog and alternate remote inference lane.

Current API base:

```text
https://router.huggingface.co/v1
```

KAI shared Responses path:

```text
https://router.huggingface.co/v1/responses
```

Testing default model:

```text
openai/gpt-oss-120b:fastest
```

Lower-latency candidate:

```text
openai/gpt-oss-20b:fastest
```

`HF_TOKEN` is server-side only and should be fine-grained for Inference Providers. For eligible CI, prefer Trusted Publisher/OIDC identities with inference permission instead of long-lived broad tokens.

Hugging Face remote inference does not authorize automatic model download, remote-code execution, or bundling weights into the APK. Downloaded model artifacts require license/provenance review and a pinned revision.

## Ollama

Ollama is the local inference daemon and first offline model lane.

Canonical endpoint:

```text
http://127.0.0.1:11434
```

Responsibilities:

- fast local chat;
- lightweight director/planner tasks;
- local tool-selection proposals when supported;
- offline fallback.

Ollama has no unrestricted shell authority and is not publicly exposed.

## Python 3

Python 3 is the policy and orchestration layer.

Responsibilities:

- localhost API services;
- OpenAI/Hugging Face/Ollama provider routing;
- typed tool dispatch;
- device/service probes;
- RSS/feed sanitation;
- SQLite state where appropriate;
- FFmpeg wrappers;
- build/test sanity;
- release evidence generation.

Prefer explicit functions and data structures over generated shell strings.

## Godot 4

Godot 4 owns the user-visible Android runtime, game systems, JRPG/social-link experiments, avatar/UI state, and WebView/plugin integration.

Godot talks to approved localhost APIs or typed Android plugin surfaces. It does not become a credential vault or arbitrary shell host.

## Edge Gallery

Edge Gallery is the Samsung-facing media/status surface.

It may show generated previews, local image/video cards, build artifacts, status summaries, avatar/character references, approved gallery items, and widget/edge-panel state.

It does not ingest secrets and does not decide build/release status.

## Failure behavior

- OpenAI not configured -> `auto` may select configured Hugging Face.
- Hugging Face not configured -> `auto` may select configured OpenAI.
- Neither remote provider configured -> deterministic/local/Ollama behavior remains available.
- Remote provider call fails after selection -> report failure; do not silently send the prompt to the other vendor.
- Ollama unavailable -> UI remains responsive and reports offline state.
- Optional media service unavailable -> chat/build shell still launches.
- Secure Folder cannot inspect daemon PIDs -> probe localhost endpoints instead.

## Final authority

The Professor defines the goal. Lum compiles intent. Python policy selects capabilities/providers. Models propose. Tools execute. CI verifies builds. Signing and F-Droid client evidence determine release-green.
