# Hydra hard architecture audit

## Architecture and security

- **GREEN:** Android remains a thin client; the backend binds to `127.0.0.1:8787`.
- **GREEN:** `OPENAI_API_KEY` is read only from the backend environment and is never returned in responses.
- **GREEN:** RSS is size-limited, sanitized, deduplicated, and never executed as instructions.
- **GREEN:** The only tool is typed and allow-listed; arbitrary model-generated code is not supported.
- **YELLOW:** OpenAI mode requires deployment-level TLS and secret rotation controls.

## Realtime, audio, and reliability

- **GREEN:** Deterministic mock mode works without credentials; malformed JSON, oversized bodies, invalid audio, and unavailable OpenAI responses fail safely.
- **YELLOW:** Android permission, lifecycle, barge-in, and duplicate-tap handling belong to the future thin client.

## Build, reproducibility, and maintainability

- **GREEN:** Backend uses Python standard library only and has deterministic tests.
- **YELLOW:** Android Gradle project and installable CI APK are not yet present in this early repository.
- **RED:** No production deployment or privileged Android mutation is attested; writes, publishing, merging, and deployment remain disabled.

No RED finding is enabled by this implementation.
