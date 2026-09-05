# Project Hydra Android Copilot Instructions

## Mission
Build Project Hydra Android as a thin, reproducible Android frontend plus a minimal Python 3 localhost backend. The local contract must later switch to an Oracle-hosted HTTPS backend by changing configuration, not application architecture.

## Hard invariants
- Android UI remains a thin shell. Do not embed LLMs, model weights, Python interpreters, or production backend logic in the APK.
- Development backend binds to `127.0.0.1:8787`.
- One server-side `OPENAI_API_KEY` is sufficient. Never place API keys, signing keys, voice recordings, model weights, or secrets in the APK, source, tests, logs, or Git history.
- Frontend/backend traffic uses HTTP locally and a replaceable base URL. Production will use HTTPS/TLS.
- Avoid `addJavascriptInterface()` unless a concrete requirement proves HTTP cannot do the job.
- Restrict WebView navigation and microphone grants to the trusted localhost origin in local mode.
- Logical agents are not separate acoustic speakers. Normalize their output through a response composer and one `CanonicalUtterance`/`VoiceBackend` pipeline.
- Never expose model chain-of-thought. Operational traces may contain IDs, tool names, status, timings, errors, and compact summaries only.
- Tools are typed, allow-listed backend functions. Validate model-requested arguments before executing. Never execute arbitrary model-generated code.
- `get_weather(location, unit)` is the canonical first function tool. `unit` must be `celsius` or `fahrenheit`.
- If `OPENAI_API_KEY` is missing, the complete UI/API/tool/audio flow must still work in deterministic mock mode.
- Keep heavyweight TTS/voice-cloning engines optional. The P0 build must compile without Piper/OpenVoice/model weights.
- CI is authoritative. Copilot is an implementation assistant, not the build oracle.

## Product feel
The UI is an original Project Hydra electric-oni / anime-waifu secretary experience for playful adult dictation/chat. Use mint/teal on black, large touch targets, mobile-first 9:16-friendly layout, clear status animation, and witty configurable persona copy. Do not directly copy a copyrighted character's visual design or dialogue.

## Required states
`idle`, `listening`, `transcribing`, `thinking`, `tool_call`, `speaking`, `interrupted`, `offline`, `error`, `retrying`.

## Required API contract
- `GET /health`
- `GET /v1/agents`
- `GET /v1/tools`
- `POST /v1/hydra/turn`
- `POST /v1/audio/speech`
- deterministic failure-injection routes for timeout/500/invalid-audio testing

## Android build target
Use the current stable Android toolchain that supports API 37. At the time of this milestone, AGP 9.3.0 requires Gradle 9.5.0 and JDK 17. Pin versions rather than using dynamic versions.

## Validation before completion
Run and fix until green:

```bash
python -m pytest backend/tests
./gradlew lintDebug testDebugUnitTest assembleDebug
```

The GitHub Actions workflow must upload an installable debug APK artifact even when release-signing secrets are absent.

## Three-pass hard audit
Before calling the milestone complete, document `docs/HARD_ARCH_AUDIT.md`:
1. Architecture/security: key custody, localhost binding, WebView origin policy, permissions, typed-tool validation, secret/log hygiene, arbitrary-code execution risk.
2. Realtime/audio/reliability: permission denial, backend unavailable/restart, timeout, malformed JSON, tool failure, duplicate taps, audio failure, barge-in, rotation/background/foreground.
3. Build/reproducibility/maintainability: clean clone, pinned versions, deterministic tests, no secret artifacts, installable CI APK, replaceable interfaces.

Use GREEN/YELLOW/RED findings and remediate RED before completion.

## Plugin Autopilot lane
- This branch contains a skills-only ChatGPT/Codex Plugin manifest at `.codex-plugin/plugin.json`.
- For Android widget/supervisor work, use `skills/android-widget-autopilot/SKILL.md` as the branch-local Autopilot workflow.
- Read repository state before writing. Prefer focused patches over broad rewrites.
- Preserve the Termux widget task/state contract and localhost-only development boundary unless the user explicitly requests a breaking change.
- Run available checks and report execution evidence. Never describe an unexecuted check as passed.
- Distinguish branch-updated, locally validated, PR-ready, merged, released, submitted, approved, and published states.
