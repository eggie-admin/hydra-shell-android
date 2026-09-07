# KAI 9000 Lum + Hugging Face + OpenAI hard audit

Milestone: `KAI9000_LUM_HF_OPENAI_CATHEDRAL_20260907`
Status: `MUTATION_BRANCH_GREEN_PENDING_CROWN_MERGE`

## Source-of-truth hierarchy

1. Professor holds the crown and final authority.
2. KAI 9000 APK is the active mutation target.
3. GitHub is canonical versioned source history.
4. Google Drive is the recovery mirror and approved artifact archive.
5. Cloudflare is the public edge.
6. Remote GitHub Codespaces/browser terminal is the development terminal.
7. GitHub Actions is the remote build/test/release forge.
8. Vercel is retired and forbidden.
9. Local Termux is retired from the active architecture.
10. `KAI9000_LUM_MAGIC_GRIMOIRE_HTMX_NPM_SOT_20260907` remains the deterministic Grimoire reference; historical Termux/local-server notes inside it do not override the Crown Lock.

## Source-of-truth sanity

- Google Drive folder `KAI9000_LUM_MAGIC_GRIMOIRE_HTMX_NPM_SOT_20260907` is present under the KAI 9000 source-of-truth archive.
- Its manifest declares `GREEN_10_OF_10` and exact jQuery/HTMX pins.
- The downloaded Drive `manifest.json` SHA-256 was recomputed as `61a513867f6ccadf57afeb1fe59251cdd525fe43534f4f03e248f23d4f707327`, exactly matching the package `SHA256SUMS` entry.
- The Grimoire audit itself records a 10/10 deterministic/syntax/safety pass.
- The latest Crown Lock milestone was not found as a standalone Drive item during the initial audit, so this reroll creates a new Drive cathedral folder for the current agent milestone rather than pretending Drive was already current.

## Hugging Face audit evidence

Authenticated Hugging Face account context was successfully verified without exposing the OAuth credential. Hub metadata was inspected for:

- `openai/gpt-oss-20b`: Apache-2.0, text generation, endpoints compatible, multiple live Inference Providers.
- `openai/gpt-oss-120b`: Apache-2.0, text generation, endpoints compatible, multiple live Inference Providers.
- `Qwen/Qwen2.5-3B-Instruct`: Transformers/Safetensors text-generation model; Hub metadata reports `license: other`, therefore permissive redistribution must not be assumed without license review.

Hugging Face Inference Providers currently expose an OpenAI-compatible Responses API. Provider selection supports no suffix / `:fastest`, `:cheapest`, `:preferred`, or an explicit provider. KAI keeps silent cross-provider replay disabled.

## OpenAI audit evidence

The current OpenAI Agents SDK release inspected for this audit is `openai-agents==0.22.0`. Current SDK documentation confirms:

- OpenAI Responses is the default API path for OpenAI models;
- `gpt-5.6-luna` is the fast/default agent model with reasoning effort `none` and low verbosity;
- `gpt-5.6-sol` is the explicit frontier/heavy model;
- Responses WebSocket transport is supported through `set_default_openai_responses_transport("websocket")`;
- tracing is enabled by SDK default unless explicitly disabled, so KAI continues to disable it by default for source/tool privacy;
- `store` is an explicit model setting and KAI keeps it `false`.

## Original NON-NULL findings and disposition

| Finding | Result | Mutation |
|---|---|---|
| stale `gpt-6-astra` default in `remote_ai.py` | FIXED | replaced with `gpt-5.6-luna` |
| Lum always used Luna/none | FIXED | Luna fast path + Sol medium heavy escalation + `/luna`/`/sol` overrides |
| Responses websocket doctrine not wired | FIXED | configurable `LUM_OPENAI_TRANSPORT`, default `websocket` |
| no Hugging Face skill | FIXED | added `huggingface-forge` |
| no current Crown/source-of-truth skill | FIXED | added `source-of-truth` |
| no OpenAI routing skill | FIXED | added `openai-router` |
| Android skill missing current deployment doctrine | FIXED | rerolled `android-backend` |
| no-key fallback referenced retired local/Ollama lane | FIXED | deterministic application lane wording only |
| runtime package metadata described local Ollama as active | FIXED | version `3.5.0` metadata aligned to current APK/provider doctrine |

## 10-pass hard audit

| Pass | Gate | Result | Evidence |
|---|---|---|---|
| 01 | Crown authority | GREEN | Professor final authority; no Lum self-approval or ULTIMA self-cast. |
| 02 | Source-of-truth integrity | GREEN | Drive Grimoire manifest SHA matches `SHA256SUMS`; GitHub remains canonical version history. |
| 03 | OpenAI model doctrine | GREEN | Luna default / Sol heavy route; stale model removed. |
| 04 | OpenAI Responses transport | GREEN | websocket default wired with HTTP runtime fallback. |
| 05 | Hugging Face Forge doctrine | GREEN | provenance/license/revision/provider/trust rules added. |
| 06 | Secret boundary | GREEN | credential patterns guarded; no provider secrets added to code/docs. |
| 07 | Python 3.11 | GREEN | GitHub Actions run `34165689601`, compile + focused tests + invariants + secret guard passed. |
| 08 | Python 3.14 | GREEN | GitHub Actions run `34165689601`, compile + focused tests + invariants + secret guard passed. |
| 09 | Provider failover boundary | GREEN | OpenAI preferred when configured; Hugging Face explicit/secondary; silent post-error replay remains false. |
| 10 | APK deployment doctrine | GREEN | remote GitHub terminal + Actions + Cloudflare edge; Vercel forbidden; local Termux retired. |

## Files mutated

- `lum_agent/agent.py`
- `lum_agent/doctrine.py`
- `lum_agent/router.py`
- `lum_agent/skills/source-of-truth/SKILL.md`
- `lum_agent/skills/openai-router/SKILL.md`
- `lum_agent/skills/huggingface-forge/SKILL.md`
- `lum_agent/skills/android-backend/SKILL.md`
- `remote_ai.py`
- `tests/test_lum_agent.py`
- `pyproject.toml`
- `docs/LUM_AGENT_DOCTRINE_20260907.md`
- `docs/LUM_AGENT_SKILL_CHAIN.md`
- `.github/workflows/lum-hf-openai-cathedral.yml`

## Remaining external / global gates

These do **not** invalidate the Lum mutation branch, but prevent claiming the entire KAI 9000 universe is fully promoted:

1. The working lineage repository is still `eggie-admin/hydra-shell-android`; the planned canonical `eggie-admin/KAI9000` repository has not yet been created through the available connector.
2. The external Vercel GitHub App still emits repository checks/status residue and must be removed outside repository code; tracked separately as Crown blocker issue #23.
3. No paid/live OpenAI or Hugging Face model call was made during this audit. CI proves code/SDK/route/doctrine behavior without exposing credentials, not live provider billing/network success.
4. Cloudflare live-publication/TLS/DNS proof is a separate network gate from this Lum agent audit.

## Promotion law

This branch is GREEN for code + doctrine + Python 3.11/3.14 CI. It is **not merged automatically**. Professor approval remains required to merge into `testing/luhm-os-android`, and later promotion to the canonical KAI 9000 repository remains a separate Crown action.
