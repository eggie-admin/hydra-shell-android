# Lum Android Backend Skill

Android is a thin authenticated cockpit, not the provider-secret store.

## Lanes

- `/api/*`: HTTPS request/response commands, jobs, config, health.
- `/ws`: Samsung real-time control/status event stream.
- `/providers/google/*`: server-side Google HTTPS/gRPC adapter.
- `/providers/gemini/live`: server-to-server Gemini Live WebSocket bridge.
- `/api/lum/*`: server-side OpenAI Lum agent.

## Security

- No OpenAI, Google, GitHub, Cloudflare, or signing secret belongs in APK assets, HTML, JavaScript, logs, manifests, or agent state.
- The Android app authenticates to KAI, not directly to provider secrets.
- KAI owns provider authentication, retries, routing, rate limits, observability, and policy.
- Provider tool calls do not bypass deterministic application authorization.

## Deployment truth

Local/CI smoke is not proof that a remote VM exists or that a public endpoint is live. Report those gates separately.
