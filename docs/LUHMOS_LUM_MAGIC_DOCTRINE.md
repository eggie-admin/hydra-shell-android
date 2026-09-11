# LuHm OS Lum Magic Doctrine

Milestone: `LUHMOS_LUM_MAGIC_AUTOMATION_20260910`

Lum's Final Fantasy-inspired magic vocabulary is a human-facing command language for coding automation. It is not a shell language and never bypasses branch, CI, signing, release, or human-approval policy.

## Authority

1. Professor is final authority.
2. Lum interprets spell intent and produces a typed plan.
3. Python policy code validates that plan.
4. GitHub Actions performs approved remote build/test work.
5. CI evidence, not model confidence, determines GREEN.
6. No model-generated arbitrary shell command is executable by the spell layer.
7. No spell may expose, invent, or commit credentials/private keys.
8. Stable release promotion is never implicit.

## Spellbook

### LIBRA
Read-only inspection. Check source-of-truth, branch state, diffs, CI, versions, Android package identity, signing metadata, artifact hashes, and build health. No mutation.

### SCAN
Read-only deeper audit/sanity pass. Useful before architecture changes and releases. No mutation.

### CURE
Smallest possible hotfix. Work only on the correct work lane, add or update tests, and converge through a PR to `luhmos-main`. It does not promote a release channel.

### CURA
Bounded patch. May modify multiple related files while preserving API contracts. Must pass lane CI, converge through `luhmos-main`, and may stage to `luhmos/testing` only after GREEN.

### CURAGA
Full mutation. Used for coordinated architecture changes across AI logic, frontend, backend, and/or platform lanes. Requires explicit human approval, migration notes, rollback target, tests, and CI evidence. It never auto-promotes beta or stable.

### METEO
Staging strike. Commit an already-reviewed change, converge through `luhmos-main`, stage it to `luhmos/testing`, and invoke staging CI. Any non-GREEN gate stops the spell. `METEO` does not mean production release.

### ULTIMA
Finale compile command. Invoke the approved GitHub remote compile/release forge for a selected GREEN commit. ULTIMA verifies package/application identity, release signer/certificate, target API, ABI, 16 KB native/ZIP alignment, bundled assets, artifact hash, and provenance. ULTIMA never silently merges branches, promotes stable, or substitutes a debug signer for the release signer.

### ESUNA
Hardening cleanup. Remove stale dependencies, dead deployment paths, leaked/embedded secret patterns, obsolete config, and policy drift without adding unrelated features.

### PHOENIX
Rollback/revival. Requires a named sealed GREEN commit/artifact and explicit human approval. Use an auditable revert or ref restoration. Never guess a rollback target.

## Branch routing

```text
luhmos/ai-logic  ─┐
luhmos/frontend   ├──> luhmos-main
luhmos/backend   ─┘
                     ↓
               luhmos/testing
                     ↓
               luhmos/proposed
                     ↓
                 luhmos/beta
                     ↓
                luhmos/stable
```

Spell defaults:

- `CURE`, `CURA`, `CURAGA`, `ESUNA`: appropriate work lane first.
- `METEO`: `luhmos-main` to `luhmos/testing` after GREEN.
- `ULTIMA`: remote forge against an explicit GREEN commit/ref.
- `PHOENIX`: named sealed rollback target only.

## AI routing

Lum is the user-facing agent. Fast conversational interpretation should use the speed-first model lane. Heavy architecture, debugging, audit, mutation planning, or release review should escalate to the deep reasoning lane. Model choice does not alter permissions.

Recommended internal flow:

```text
user spell/intent
    ↓
Lum parser
    ↓
Python SpellPlan
    ↓
policy gate
    ↓
read-only tools OR approved GitHub action
    ↓
CI / artifact verification
    ↓
Lum reports evidence
```

## Fail-closed laws

- Unknown spell: reject.
- Ambiguous destructive target: reject until target is explicit.
- Missing human approval for `CURAGA`, `ULTIMA`, or `PHOENIX`: block.
- Missing required GREEN evidence: block release/compile action.
- Missing persistent release signer: ULTIMA may build a clearly labeled staging artifact only if explicitly requested, never call it release GREEN.
- Dirty or divergent release lineage: stop and report.
- Private key or token in source: stop and invoke hardening/ESUNA workflow.
- AI response alone is never proof of a successful mutation.

## Android LuHm OS invariants

Canonical application ID: `art.eggiebagelface.luhmos`.

Release signing alias: `luhmos-release`.

Certificate identity contract: `CN=art.eggiebagelface.luhmos,O=Eggie Bagelface Art,C=US`.

Android release gates remain API 36, `arm64-v8a`, 16 KB compatibility, reproducible package identity, verified signing lineage, and recorded artifact SHA-256.

## Non-spell natural language

Normal language remains valid. The spell vocabulary is shorthand, not a requirement. For example, "hotfix the WebView" maps to CURE semantics; "full architecture mutation" maps to CURAGA semantics; "compile the current GREEN Samsung build" maps to ULTIMA semantics.

## Copyright / naming boundary

The system is Final Fantasy-inspired fan terminology for a private developer command vocabulary. LuHm OS implementation code, schemas, UI, orchestration, and behavior remain original project work; do not copy Square Enix game assets, source code, spell artwork, audio, logos, or proprietary UI.
