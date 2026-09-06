---
applyTo: "ultima/ollama-ffmpeg-antenna-v3/**,integrations/**,docs/HUGGINGFACE_API_REROLL.md"
---

# Copilot instructions: Hugging Face API reroll

Treat Hugging Face as the KAI 9000 open-model forge/catalog and alternate remote inference lane.

Read first:

- `docs/API_TRINITY_DOCTRINE.md`
- `docs/HUGGINGFACE_API_REROLL.md`
- `integrations/vendor-apis.manifest.json`
- `lumh-os/kai9000/project.manifest.json`

Rules:

- Use `HF_TOKEN` only from server-side runtime or protected CI identity/secret boundaries.
- Never embed, print, log, Base64-wrap, commit, or return the token.
- Prefer fine-grained tokens with Inference Providers permission for runtime use.
- Prefer Hugging Face Trusted Publisher/OIDC for eligible CI workflows instead of long-lived tokens.
- KAI's shared remote endpoint is `/api/remote-ai/chat`.
- Supported provider selectors are `auto`, `openai`, and `huggingface`.
- `auto` prefers configured OpenAI, then configured Hugging Face, then deterministic/local behavior.
- Do not silently resend a failed request to another provider.
- Hugging Face Responses compatibility is beta; retain the stable chat-completions path as a documented fallback contract, not an automatic runtime fallback.
- Default HF model is `openai/gpt-oss-120b:fastest`; lower-latency candidate is `openai/gpt-oss-20b:fastest`.
- Provider suffixes such as `:fastest`, `:cheapest`, `:preferred`, or an explicit provider are routing policy and must remain visible in evidence.
- Remote inference does not authorize downloading model weights.
- Downloaded Hub artifacts require license/provenance review and pinned revision before build use.
- Never enable arbitrary remote code merely because a model repository asks for it.
- Provider output is advisory/untrusted until Python policy validates it.
- No provider may self-authorize file mutation, shell execution, DNS changes, signing, deployment, merging, or release promotion.
