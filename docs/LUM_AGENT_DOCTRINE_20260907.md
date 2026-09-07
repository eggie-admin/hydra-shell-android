# KAI9000 Lum In-App Agent Doctrine

Status: CODE_AND_CI_GREEN
Date: 2026-09-07

## Identity

- App-side agent name: `KAI9000-Lum-InApp`
- Credential contract: reuse existing protected server-side `OPENAI_API_KEY`
- No new OpenAI key is required by this architecture.
- No claim is made that the remote OpenAI Platform key label was renamed.

## Runtime

- OpenAI Agents SDK: `openai-agents==0.22.0`
- Default model: `gpt-5.6-luna`
- Reasoning effort: `none`
- Verbosity: `low`
- Tracing: disabled by default
- Store: false
- Agent max turns: 8 by default

## Python-first skill chain

```text
DOCTRINE
  -> INSPECT
  -> OUTLINE / READ
  -> DEBUG
  -> COMPILE
  -> PROPOSE
  -> HUMAN APPROVAL
  -> EXECUTION EVIDENCE
```

Bundled skills:

- `prime`
- `python-core`
- `python-debug`
- `json-boundary`
- `jquery-plugin`
- `android-backend`

Bundled tools:

- `list_lum_skills`
- `load_lum_skill`
- `read_source`
- `search_source`
- `python_outline`
- `python_compile`
- `propose_spell`

## Authority boundary

Lum is a reasoning, inspection, debugging, and proposal agent. It does not directly own mutation authority.

The existing deterministic magic cast gateway remains authoritative for mutation. `WRITE_FILE` requires application-controlled human approval and SHA/checkpoint protection. ULTIMA remains human-only and disabled in the in-app agent runtime.

## Secret boundary

Provider credentials remain server-side. They are never embedded into Android assets, HTML, JavaScript, Git, agent doctrine, logs, or Drive manifests.

## CI evidence

Antenna + Lum smoke run `34158459126` passed on Python 3.11 and Python 3.14.

ULTIMA Final Form run `34158801803` passed on commit `35ce6524b031b5cbc395b2e168e74d246f8de9de` after replacing a brittle grep assertion with deterministic Python source assertions.

The CI smoke deliberately supplied no OpenAI API key. Therefore this seal proves app structure, SDK installation, compile, tests, FastAPI routes, doctrine boundaries, and deterministic no-key behavior. It does not claim a live OpenAI model request succeeded.
