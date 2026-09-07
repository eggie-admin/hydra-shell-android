# Lum OpenAI Router Skill

## Default path

- Default model: `gpt-5.6-luna`.
- Default reasoning effort: `none`.
- Default verbosity: `low`.
- Default API shape: OpenAI Responses through the Agents SDK.
- Preferred interactive transport: Responses over WebSocket.
- HTTP remains a runtime-configurable fallback.

## Heavy escalation

Escalate to `gpt-5.6-sol` with reasoning effort `medium` for genuinely heavyweight work such as:

- hard architecture audits;
- deep debugging and root-cause analysis;
- migrations and dependency-conflict resolution;
- threat modeling/security review;
- complex compile/build failures;
- explicit 10-pass or deep-research requests.

Explicit operator overrides take precedence:

- `/luna ...` forces Luna.
- `/sol ...` forces Sol.

Do not escalate ordinary chat, simple code edits, status checks, or deterministic tool work just because Sol is available.

## Privacy and state

- `store=false` unless the application deliberately changes policy.
- Tracing is disabled by default because source/tool payloads may be sensitive even when they are not credentials.
- Provider credentials remain outside the APK and outside model-visible state.

## Provider boundary

OpenAI is the primary Lum reasoning provider. Hugging Face is a separate advisory/provider lane and Forge. Never silently replay a failed OpenAI request to Hugging Face unless the application explicitly authorizes cross-provider failover.

A model response is not execution evidence and cannot grant itself mutation authority.
