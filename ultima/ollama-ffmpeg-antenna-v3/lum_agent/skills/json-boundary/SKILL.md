# Lum JSON Boundary Skill

JSON is a transport contract, not the application's internal type system.

## Boundary rule

DECODE -> VALIDATE -> TYPED OBJECT -> OPERATE -> SERIALIZE

- Reject malformed or unexpected input at the edge.
- Use stable schemas for cross-language contracts.
- Prefer explicit versioned envelopes for long-lived SDK/API messages.
- Treat unknown fields deliberately instead of accidentally.
- Keep timestamps, IDs, status enums, and error shapes consistent.
- Never use Base64 as encryption, authentication, authorization, or integrity protection.
- Never serialize secrets into logs, manifests, Android assets, browser state, or agent state.

## Debugging

When a JSON boundary fails, report the field/path and safe validation error. Do not dump credentials or entire sensitive payloads.
