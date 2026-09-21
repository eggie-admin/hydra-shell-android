---
applyTo: "project/hydra/integrations/google-ai-edge/**,docs/GOOGLE_AI_EDGE_GALLERY.md,skills/google-ai-edge-gallery/**"
---

# Google AI Edge Gallery lane

Treat Google AI Edge Gallery as an experimental on-device benchmark and skill-prototyping harness, never as LuHm OS source authority.

Use it for bounded local evaluation only:

- benchmark approved models on Android hardware;
- compare startup latency, token/decode throughput, memory, and thermal behavior;
- prototype read-only helper skills;
- validate whether a local/offline helper can replace a remote call for a narrow task class;
- capture exact model/runtime/device receipts before claiming a speedup.

Hard boundaries:

- do not vendor Google AI Edge Gallery application code into the LuHm OS APK merely because the upstream project is open source;
- do not treat its app, models, skills, or benchmark results as source-of-truth authority;
- no silent install, public publish, shell execution, privilege bridge, self-approval, or automatic canonical mutation;
- no API keys, account tokens, signing material, private prompts, or user secrets in Gallery skills, sample assets, logs, receipts, or Git;
- a local helper may propose or summarize, but Project Hydra mutation still uses the human-approved loopback gateway and normal proof contract.

Latency rule:

1. deterministic local validation first;
2. on-device helper only when the task is bounded and does not require fresh external data;
3. fast OpenAI parent route for ordinary reasoning/coding/triage;
4. deep route only for genuinely difficult architecture, security, release, or multi-file debugging.

Do not describe a route as faster until comparable measurements exist for the exact target hardware and task.
