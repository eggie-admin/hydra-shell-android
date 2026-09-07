# Lum Agent Skill Chain

Milestone: `KAI9000_LUM_HF_OPENAI_CATHEDRAL_20260907`

Canonical in-app flow:

```text
User request
  -> Crown / source-of-truth doctrine
  -> Prime authority boundary
  -> OpenAI router classification
  -> load only relevant specialist skill(s)
  -> read-only evidence tools
  -> Python AST/source inspection when coding
  -> deterministic compile/test evidence
  -> proposal
  -> deterministic application approval gate for mutation
  -> execution
  -> exact result/evidence
```

## Routing defaults

1. `gpt-5.6-luna`, reasoning `none`, verbosity `low` for normal work.
2. `gpt-5.6-sol`, reasoning `medium` for hard architecture/debug/audit/migration/security/build work.
3. `/luna` and `/sol` are explicit Professor/operator overrides.
4. OpenAI Responses WebSocket is preferred for interactive Lum; HTTP is a configured fallback.
5. No silent OpenAI -> Hugging Face failover after a provider error.

## Skill selection

1. `prime` for authority/evidence/secret rules.
2. `source-of-truth` for Crown Lock, GitHub/Drive roles, Cloudflare edge, remote terminal, and retired lanes.
3. `openai-router` for Luna/Sol routing and Responses transport.
4. `huggingface-forge` for Hub provenance, license, revision, provider selection, or artifact review.
5. `python-core` for Python design and implementation.
6. `python-debug` when diagnosing failures.
7. `json-boundary` when data crosses process/language/API boundaries.
8. `jquery-plugin` when the Python-owned browser plugin contract is involved.
9. `android-backend` when Samsung APK, remote terminal, Cloudflare, antenna, or provider boundaries are involved.

## Hugging Face law

Hugging Face is the Forge, not Crown authority. Model/repository metadata can inform a skill, but the committed GitHub skill is the versioned KAI source. Review license, revision, provider availability, and trust boundaries before adoption. Do not download or execute remote repository code merely because a model card suggests it.

## Non-negotiable rules

- Professor is final authority.
- KAI 9000 APK is the active mutation target.
- Read before write.
- AST/source evidence before structural Python claims where practical.
- Compile is not an integration test.
- A proposed spell is not execution.
- No agent self-approval.
- No ULTIMA self-cast from the in-app agent.
- No secrets in source, prompt doctrine, client code, logs, Drive manifests, or agent state.
- Vercel remains purged from active doctrine.
- Local Termux remains retired from active doctrine.
- Failed or missing evidence is reported as red/yellow, never silently promoted to green.
