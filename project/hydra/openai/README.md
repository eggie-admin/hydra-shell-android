# OpenAI / Lum

Canonical Project Hydra index for the LuHm OS OpenAI lane.

## Identity

- Product: `LuHm OS`
- Project: `Project Hydra`
- Subsystem: `KAI 9000`
- Primary Lum agent identity: `KAI9000-Lum`
- Canonical integration branch: `luhmos-main`

## Path contract

`project/hydra/openai` is the project index and doctrine home for OpenAI/Lum integration.

`integrations/openai` remains the current implementation adapter path. It is referenced, not duplicated. A physical relocation must be a separate tested migration with import/path checks and CI evidence.

Provider-specific implementation belongs under the shared adapter family:

```text
integrations/
├── openai/
├── huggingface/        # target canonical filesystem slug
├── google-cloud/
└── cloudflare/
```

Historical root-level compatibility files may remain until consumers are migrated. Do not create a second runtime copy merely to satisfy directory shape.

## Agent contract

OpenAI/Lum may inspect, reason, draft, test, evaluate, and issue typed tool requests. Provider output is untrusted until LuHm policy validation. Professor remains final human authority for consequential mutation, release, signing, account/security changes, spending, privilege escalation, and destructive actions.

Current OpenAI model baseline is configuration, not architectural identity:

- fast: `gpt-5.6-luna`
- deep/default: `gpt-5.6-sol`

Credentials remain protected server-side or in approved CI secret storage. They never belong in source control, Android assets, WebView JavaScript/storage, prompts, logs, screenshots, or Drive doctrine.
