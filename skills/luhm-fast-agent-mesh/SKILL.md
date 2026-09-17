---
name: luhm-fast-agent-mesh
description: Use for fast, proof-driven Project Hydra AI work that benefits from a parent Lum agent plus read-only helper agents.
---

# LuHm Fast Agent Mesh

Use this Skill when the task benefits from parallel read-only analysis, compact JSON handoffs, and one controlled mutation owner.

## Source contract

Read in this order:

1. the exact current Professor instruction;
2. fresh hardware/runtime evidence when the requested state depends on it;
3. newest applicable files under `project/hydra/source-of-truth/`;
4. `project/hydra/doctrine/directory-structure.json` and `project/hydra/project.manifest.json`;
5. `AGENTS.md`, `.github/copilot-instructions.md`, and exact lane manifests/workflows;
6. proposed doctrine only as proposal material;
7. legacy material only for compatibility/history.

The source law is: AI proposes. Policy authorizes. CI proves. The human promotes.

## Fast parent loop

1. **Resolve once**: identify exact branch, head SHA, applicable crown/source contracts, target files, and relevant tests.
2. **Shard reads**: delegate narrow read-only work to mini helpers when it reduces wall-clock time.
3. **Normalize**: require helpers to return compact structured evidence, not essays.
4. **Plan once**: parent Lum combines evidence into the smallest safe delta.
5. **Write once**: serialize writes. Never let two helpers edit the same path or independently decide authority.
6. **Validate**: run existing focused gates first, then exact-head CI where required.
7. **Prove**: for bounded mutation workflow changes, emit one SHA-256-bound proof payload rendered as JSON, scriptless HTML, and chat-safe text.
8. **Stop correctly**: if evidence is missing, report the missing gate instead of inventing GREEN.

## Mini helper roles

Mini helpers are role-specialists, not independent authorities:

- `SOURCE`: exact current source refs, topology, and authority order;
- `DIFF`: smallest safe delta and drift review;
- `TEST`: changed-file to existing-test/workflow mapping;
- `PROOF`: executed-evidence normalization into receipts.

Mini helpers are read/search only. They cannot mutate source, execute arbitrary shell, approve, sign, install, merge, publish, deploy, promote, crown, or change billing/DNS/runtime state.

## OpenAI routing

Use the active AI stack configuration rather than hard-coded secrets.

Fast/front-door lane:

```text
OPENAI_MODEL_FAST
OPENAI_REASONING_FAST
OPENAI_VERBOSITY_FAST
OPENAI_SERVICE_TIER_FAST
```

The current source default is `gpt-5.6-luna` with low-latency settings. Escalate to the deep model only for work where additional reasoning materially improves correctness, such as difficult multi-file debugging, security/release audits, or architecture redesign.

Prefer direct Responses API when LuHm owns a short structured loop. Use the OpenAI Agents SDK only when handoffs, guardrails, sessions, or human-in-the-loop orchestration materially reduce complexity. Agent/SDK guardrails never replace Project Hydra approval policy.

## Paid-product boundary

Paid ChatGPT/Codex access improves the human operator workflow but does not become API billing, an APK credential, or a source-of-truth authority. Programmatic OpenAI traffic uses separately configured server-side API billing and credentials.

Never write API keys, ChatGPT session material, GitHub tokens, signing keys, or billing secrets into Git, prompts, examples, tests, HTML receipts, APK resources, logs, or doctrine.

## Mutation proof boundary

The active bounded mutation gateway is `backend/candidate_workflow.py` on loopback. AI output does not pipe directly to shell.

A successful file mutation requires:

```text
stage
→ explicit human approval
→ preimage SHA re-check
→ checkpoint
→ atomic replacement
→ post-write SHA verification
→ proof
```

Proof receipts must exclude approval tokens and staged file contents.

## Compact handoff object

```json
{
  "request_id": "...",
  "lane": "FAST|MINI|DEEP",
  "authority": "READ_ONLY|PROPOSE_ONLY|HUMAN_GATE_REQUIRED",
  "source_refs": ["path@sha"],
  "intent": "...",
  "findings": [],
  "proposed_actions": [],
  "validation": [],
  "proof_required": true,
  "stop_reason": "CONTINUE|RETURN_TO_PARENT|NEED_FRESH_EVIDENCE|HUMAN_GATE"
}
```

## Completion vocabulary

Use exact state words: `proposed`, `staged`, `edited`, `committed`, `source-tested`, `CI-started`, `CI-green`, `artifact-produced`, `APK-verified`, `installed`, `launched`, `merged`, `released`, `published`, `crowned`, `device-green`.

Never claim a later state from evidence for an earlier one.
