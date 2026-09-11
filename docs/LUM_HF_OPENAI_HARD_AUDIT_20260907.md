# KAI 9000 Lum + Hugging Face + OpenAI hard audit

Milestone: `KAI9000_LUM_HF_OPENAI_CATHEDRAL_20260907`

This document is intentionally created on the testing lineage before any promotion. It records the audit gate and the exact non-null findings that require mutation.

## Source-of-truth hierarchy

1. Professor holds the crown and final authority.
2. KAI 9000 APK is the active mutation target.
3. GitHub is canonical versioned source history.
4. Google Drive is the recovery mirror and artifact source of truth.
5. Cloudflare is the public edge.
6. Remote GitHub terminal / Codespaces is the development terminal.
7. Historical deployment providers are outside the active architecture and are not status authorities.
8. `KAI9000_LUM_MAGIC_GRIMOIRE_HTMX_NPM_SOT_20260907` remains the deterministic Grimoire reference; stale deployment notes inside it are historical only.

## Hard-audit findings

### PASS: Grimoire integrity

The Drive Grimoire SOT is sealed GREEN 10/10 for deterministic generation, syntax, regression tests, dynamic-code safety, and companion consistency. Historical implementation notes are not active deployment authority.

### PASS: OpenAI Agents SDK version

`openai-agents==0.22.0` remains the released SDK baseline inspected for this audit.

### PASS: Lum secret boundary

The in-app Lum agent keeps provider credentials server-side and tracing disabled by default. The Professor remains final authority; Lum does not self-authorize mutation or ULTIMA.

### FINDING 01: stale OpenAI model default

`remote_ai.py` still defaulted to `gpt-6-astra`, which conflicts with the current Lum doctrine and current OpenAI model catalog. The canonical fast/default model is `gpt-5.6-luna`; heavy architecture/debug/audit work escalates to `gpt-5.6-sol`.

### FINDING 02: Lum did not implement the Luna -> Sol escalation contract

`lum_agent/agent.py` always used Luna with reasoning effort `none`. Current doctrine requires speed-first Luna plus explicit or heuristic Sol escalation for heavyweight work.

### FINDING 03: OpenAI Responses websocket doctrine was not wired

The current Agents SDK supports the Responses API over websocket transport. KAI prefers websocket transport for persistent interactive Lum use while retaining HTTP as a configurable fallback.

### FINDING 04: no Hugging Face Forge skill in the Lum registry

Hugging Face is connected and authenticated, but Lum had no dedicated skill describing provenance, license, immutable revision, provider routing, or `trust_remote_code` boundaries.

### FINDING 05: current deployment doctrine missing from Lum skills

The Android backend skill did not explicitly encode the Crown Lock, remote GitHub terminal, and Cloudflare public edge.

### FINDING 06: deterministic no-key message referenced retired runtime wording

The remote provider mock message still described stale local runtime language. The active doctrine is the deterministic application lane plus explicitly configured provider lanes.

## Hugging Face evidence used for reroll

- `openai/gpt-oss-120b`: Apache-2.0, endpoints compatible, multiple live Inference Providers.
- `openai/gpt-oss-20b`: Apache-2.0, endpoints compatible, multiple live Inference Providers.
- `Qwen/Qwen2.5-3B-Instruct`: Transformers/Safetensors text-generation model; its Hub metadata reports `license: other`, so it must not be treated as a permissively licensed default without license review.
- Hugging Face Responses API is beta and uses OpenAI-compatible clients. Provider suffix policies include `:fastest`, `:cheapest`, `:preferred`, or an explicit provider.

## Mutation decision

Sanity check is **NON-NULL**, therefore this audit authorizes the testing-branch reroll requested by the Professor:

- add `source-of-truth` skill;
- add `openai-router` skill;
- add `huggingface-forge` skill;
- reroll `android-backend` skill;
- implement Luna/Sol routing in Lum;
- enable configurable OpenAI Responses websocket transport;
- correct the stale remote OpenAI model default;
- remove stale runtime wording from the remote provider fallback.

No merge to `main`, publication, paid provider call, Hugging Face model download, or ULTIMA self-approval is authorized by this audit alone.
