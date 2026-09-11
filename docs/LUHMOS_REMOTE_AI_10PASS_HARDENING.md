# LuHm OS Remote AI 10-Pass Hardening Gate

Status: normative audit gate for the Lum remote-AI toolchain.

A remote-AI milestone is GREEN only when all applicable passes are GREEN and any intentionally unavailable live-provider credential is recorded as YELLOW rather than silently treated as success.

## Pass 1 · Canonical endpoint and model

OpenAI uses `https://api.openai.com/v1/responses` with canonical default `gpt-5.6-sol`. Hugging Face uses the reviewed router endpoint and pinned/default model policy. Runtime defaults, templates, and manifests must agree.

## Pass 2 · Credential isolation

Provider credentials are server-side environment/secret material only. They never enter prompts, model-visible context, source control, APK assets, public manifests, or logs.

## Pass 3 · Prompt ingress secret guard

Secret-shaped user input is rejected before a remote provider call.

## Pass 4 · Provider egress secret guard

Provider output is untrusted and scanned for secret-shaped material before it reaches the application response or logs. A match fails closed.

## Pass 5 · Provider allowlist

Only `auto`, `openai`, and `huggingface` are accepted remote provider selectors. Unknown providers fail with a bounded client error.

## Pass 6 · Model allowlist

Per-request model overrides are denied unless explicitly allowlisted through provider-specific configuration. Canonical defaults remain automatically allowed.

## Pass 7 · Failure isolation

A failing selected provider does not silently hop to another remote provider. Remote failure never grants additional authority. No usable provider output is treated as a failed call.

## Pass 8 · Credential-safe live smoke

`python3 tools/remote_ai_smoke.py` may probe configured providers with a fixed `GREEN` response challenge. Its output records only provider, model, status, latency, response-ID presence, and content-match metadata. It never prints credentials or full provider response bodies. Missing credentials are `SKIPPED/YELLOW`, not GREEN.

## Pass 9 · CI and regression proof

The router unit tests, Python compilation, secret guard, branch topology gate, PR guardrails, and relevant Cathedral CI must pass on the exact mutation revision before merge.

## Pass 10 · Promotion and Source-of-Truth seal

The reviewed AI work lane merges into `luhmos-main`, then only the allowed release channel is promoted. The milestone records exact commit SHAs, tests/workflow evidence, provider-live-smoke state, remaining YELLOW gates, and rollback target in Git and controlled Google Drive Source of Truth.

## Authority law

**AI proposes. Python authorizes. CI proves. The human promotes.**

No successful provider response, model identity, spell, or AI-generated plan can replace application-owned authorization or release evidence.
