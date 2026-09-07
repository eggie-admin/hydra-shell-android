# Lum Agent Live Next Gate

The doctrine-driven in-app Lum agent is code/CI green. The next gate is deliberately separate:

`LIVE_OPENAI_REQUEST_WITH_REUSED_LUHM_OS_KEY`

This gate must run only on a trusted server runtime where the existing `OPENAI_API_KEY` is already configured. The key value must not be copied into GitHub, Android, JavaScript, logs, Drive manifests, or chat.

A successful live gate should prove only:

1. `/api/lum/status` reports the credential configured without returning it.
2. `/api/lum/chat` returns `mode=openai_agents_sdk`.
3. Agent identity is `KAI9000-Lum-InApp`.
4. Model is the configured `LUM_OPENAI_MODEL`.
5. A harmless Python doctrine prompt returns a non-empty answer.
6. No mutation is executed during the smoke.

Until that trusted-runtime test is executed, live OpenAI operation remains `NOT_PROVEN`.
