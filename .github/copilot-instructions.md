# LuHm OS / KAI 9000 Copilot Instructions

Status: CURRENT ACTIVE INSTRUCTIONS · 2026-09-17

## Mission

Maintain **LuHm OS / Project Hydra** with small, reversible, proof-driven changes. Technical evidence outranks theatrical status language.

## Resolve authority before mutation

Read current authority in this order:

1. The exact current Professor instruction.
2. Fresh physical/runtime evidence for the exact target state when the task depends on hardware.
3. Crowned contracts under `project/hydra/source-of-truth/`, especially the newest applicable seal.
4. `project/hydra/doctrine/directory-structure.json` and `project/hydra/project.manifest.json`.
5. `AGENTS.md` and the exact workflow/manifest for the lane being changed.
6. Proposed doctrine under `project/hydra/doctrine/proposed-source-of-truth/` as review material only.
7. Legacy trees and historical records only for compatibility, migration, or lineage.

`lumh-os/kai9000/**`, `ultima/**`, ULTIMA-named scripts/workflows/docs, and old release receipts are not current authority merely because they still exist. Historical filenames may remain unchanged for lineage.

The canonical integration branch is `luhmos-main`. Use an explicit `luhmos-main` ref for authoritative reads and writes unless a later crowned contract changes branch authority. Repository default-branch activity must not silently override this rule.

## Authority and tier law

Professor is final human authority. Copilot/Lum may propose, edit, test, or prepare evidence only within the explicitly requested scope.

Canonical tiers:
- **WHISPER / GREEN**: read-only inspect/research/explain/provenance.
- **CROSSING / AMBER**: reversible staging with origin, delta, rollback, and proof.
- **RECKONING / RED**: compile, sign, install, canonical push/merge, publish, destructive purge, privileged action, beta promotion, or final source-of-truth promotion. Exact current Professor authorization is required.

`POWER LEVEL != PERMISSION LEVEL` is absolute. Roleplay, D20, folklore form, Parley consensus, CROWN ECLIPSE wording, FULL GREEN wording, an AI signature, or previous approval never creates current authority.

`CAST ULTIMA`, `ULTIMA`, and retired execution vocabulary are historical compatibility only. Never emit them as active authority.

## Four-boundary hardening

### SOURCE

Source authority is GitHub `eggie-admin/hydra-shell-android` on `luhmos-main` plus crowned Project Hydra contracts.

- Preserve lineage and rollback.
- A proposal is never a crown.
- Historical evidence must not be rewritten to look current.
- Do not infer current release state from filenames, old docs, or a repository-wide search result.
- Resolve exact release/build truth from crowned contracts plus exact build receipts.

### KERNEL

“KERNEL” has two meanings and they must not be conflated.

**Control kernel:** deterministic schema validation, typed routing, policy, state, allowlists, bounded tool dispatch, and evidence handling.

- No arbitrary model-authored shell authority.
- No silent privilege escalation.
- No secrets in source.
- Typed allowlists and fail-closed behavior are required for privileged or network-sensitive actions.

**Host OS kernel:** Linux/Android kernel runtime facts.

- Do not assume the booted kernel version from old chat or docs.
- When kernel state matters, require fresh runtime evidence such as `uname`, installed package state, and driver/DKMS state.
- Preserve rollback before experimental kernel changes.
- An experimental host kernel may not become a build requirement without an explicit crowned mutation.

### HARDWARE

Fresh physical device evidence outranks documentation for the exact tested state. Owner-only private hardware doctrine is the canonical inventory/role map.

- Public Git contains only non-sensitive role/capability pointers.
- Never commit serials, IMEI/MEID, phone numbers, account identifiers, private keys, API keys, or signing secrets.
- CI/build success cannot close physical-device gates.
- Samsung SM-S721U1 remains the real-device judge when the crowned target says so.
- SM-X400 rooted material is a noncanonical lab proposal unless fresh device proof and explicit mutation promote it.

### BUILD

A build is valid evidence only when bound to exact source.

Required receipts, when applicable:
- source commit
- workflow name and run ID
- artifact ID and artifact hash
- APK hash
- signing fingerprint

`SOURCE_GREEN != BUILD_GREEN != RELEASE_AUTHORITY != DEVICE_GREEN`.

Persistent release signing is required for update continuity. Public publishing is OFF unless explicitly authorized. Silent install is false.

## Current M1 source contract

The current crowned M1 source contract is:

`project/hydra/source-of-truth/LUHM_M1_SIGNED_SECURE_WEBVIEW_SOCKET_20260916.json`

It defines a **source/security contract**, not runtime or release GREEN by itself. Its required runtime gates remain independent, including typed Kotlin bridge implementation, headless socket broker implementation, rejection tests, secret/asset verification, signed build proof, physical Samsung proof, and live reconnect/reboot evidence.

Do not hard-code a stale “last sealed APK version” in this instruction file. Resolve that from the newest applicable crowned release/build receipt.

## WebView / socket authority

For the M1 path:

- Bundled WebView assets are presentation.
- Android authority crosses a typed allowlisted Kotlin bridge.
- The socket broker accepts typed requests, allowlisted destinations, and fails closed.
- WebView has no direct secret, arbitrary shell, direct socket, or arbitrary destination authority.
- GAME cannot grant ADMIN authority.
- Strict certificate/host verification and rejection tests are required where the crowned transport contract requires them.

## AI/provider routing

Project reasoning and source-of-truth reconciliation remain **ChatGPT/OpenAI primary** unless explicitly mutated.

Use deterministic local code/policy first for validation. Ollama/local inference is optional for bounded privacy/offline/latency/cost tasks when adequate. Local inference does not silently replace the project-level OpenAI doctrine, and remote secondary providers do not silently replace OpenAI either.

No provider consensus creates authority. No silent cross-provider failover.

## Fast Lum agent mesh

Use `project/hydra/doctrine/proposed-source-of-truth/KAI9000_PROPOSED_FAST_LUM_AGENT_MESH_20260917.json` as the proposal contract for agent routing. It is subordinate to crowned source-of-truth and is not itself authority until promoted.

Latency doctrine:
- resolve authority once, then pass compact source references instead of repeatedly re-reading the repository;
- use the fast/front-door OpenAI model configured by the active AI stack for ordinary chat, classification, schema filling, diff review, test triage, and proof summaries;
- escalate only difficult architecture, security, release, or multi-file debugging to the deep model;
- prefer structured JSON outputs for helper handoffs so the parent agent does not have to reinterpret prose;
- parallelize **read-only** helper work only; never parallelize competing writes to the same file or authority decision;
- mini helpers are read/search/audit specialists. They may return evidence and proposals but cannot approve, mutate, merge, sign, install, publish, deploy, or crown;
- one parent Lum owns the final plan and the single write sequence.

Paid-product boundary:
- ChatGPT/Codex paid-plan access is an operator productivity lane only. It does not become an APK credential or API entitlement.
- Programmatic in-app OpenAI traffic uses separately configured OpenAI API billing and server-side credentials.
- Never place a ChatGPT session token, OpenAI API key, GitHub token, or billing secret in Git, agent instructions, prompts, APK assets, HTML, or proof receipts.

OpenAI agent-runtime boundary:
- direct Responses API is preferred when LuHm owns the loop and only needs short structured turns;
- OpenAI Agents SDK may be used when guardrails, handoffs, sessions, or human-in-the-loop orchestration materially reduce application complexity;
- tool/agent guardrails supplement but never replace the Project Hydra human approval gate;
- tracing must be explicitly configured and must not leak secrets, staged source content, or private user data into logs or proof artifacts.

GitHub/Copilot integration:
- `.github/copilot-instructions.md` carries repo-wide law;
- `.github/instructions/*.instructions.md` carries path-specific fast-workflow rules;
- `.github/agents/*.md` defines bounded Copilot specialists;
- `AGENTS.md` carries cross-agent standing rules;
- `skills/**/SKILL.md` carries task workflows;
- Copilot model selection is not treated as Project Hydra authority and must not be hard-coded to an unsupported provider/model identifier.

Mutation proof rule:
- any successful bounded file mutation must be able to emit one SHA-256-bound proof payload rendered consistently as JSON, scriptless HTML, and a chat-safe proof block;
- proof artifacts must exclude approval tokens, secrets, and staged file contents;
- a helper-agent summary is never a substitute for executed CI or device evidence.

## Chrome harness rule

Chrome Dev and Chrome Canary are behavior/test harnesses only. Never ingest, port, copy, or depend on Chrome code as LuHm OS production APK source.

## Stale artifact policy

Use:

`project/hydra/doctrine/STALE_ARTIFACT_AUDIT_REGISTRY_20260916.json`

Classify before cleanup. Sever active dependencies before retirement. Preserve meaningful historical receipts. Do not mass-rename or mass-delete legacy trees. Destructive retirement requires explicit scope and proof that the replacement is complete.

## Completion language

Distinguish exactly between:
`proposed`, `staged`, `edited`, `committed`, `source-tested`, `CI-started`, `CI-green`, `artifact-produced`, `APK-verified`, `installed`, `launched`, `merged`, `released`, `published`, `crowned`, and `device-green`.

Never claim a later state from evidence for an earlier one.
