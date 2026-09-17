---
applyTo: ".github/**,backend/**,project/hydra/**,skills/**,docs/AI_STACK.md"
---

# LuHm fast-agent path rules

Use the crowned Project Hydra source-of-truth before any proposed doctrine or legacy material. Resolve authority once, then carry compact exact source references forward rather than repeatedly scanning the whole repository.

For AI-assisted work on these paths:

1. Prefer the smallest reversible delta.
2. Use structured JSON for helper handoffs and evidence summaries.
3. Read-only helpers may run in parallel. Competing writes may not.
4. One parent Lum owns the final plan and single write sequence.
5. Never let helper consensus create approval, signing, merge, install, publish, deploy, billing, or crown authority.
6. Keep OpenAI/GitHub/cloud credentials outside Git, prompts, APK assets, HTML proofs, logs, and test fixtures.
7. Treat ChatGPT/Codex paid-plan access as a human operator lane, not as an OpenAI API credential or APK entitlement.
8. Programmatic OpenAI calls use separately configured server-side API billing/credentials.
9. Prefer the fast OpenAI route from the active AI stack for ordinary classification, schema filling, short coding assistance, diff review, and proof summarization. Escalate to the deep route only when complexity materially warrants it.
10. Do not hard-code an OpenAI runtime model identifier into a GitHub Copilot agent profile unless that identifier is explicitly supported by the Copilot environment being targeted.

## Mutation boundary

The active bounded mutation gateway is `backend/candidate_workflow.py` on loopback. AI output never pipes directly to shell. Successful writes require explicit human approval, preimage SHA re-check, checkpoint, atomic replacement, and post-write SHA verification.

After a successful bounded mutation, prefer one canonical proof payload rendered as JSON, scriptless HTML, and chat-safe text with one shared SHA-256 digest. Proof artifacts must exclude approval tokens, secrets, and staged file content.

## Fast helper packet

Helpers should return compact objects shaped like:

```json
{
  "request_id": "...",
  "lane": "MINI",
  "authority": "READ_ONLY",
  "source_refs": ["path@sha"],
  "intent": "...",
  "findings": [],
  "proposed_actions": [],
  "validation": [],
  "proof_required": false,
  "stop_reason": "RETURN_TO_PARENT"
}
```

If current evidence is insufficient, return `stop_reason: NEED_FRESH_EVIDENCE` instead of inventing GREEN.
