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

## System-wide latency law

Optimize wall-clock time without weakening correctness, provenance, or human approval:

- resolve branch/head/crowned authority once per task;
- reuse exact `path@sha` references and do not re-fetch unchanged evidence;
- batch independent remote reads when tooling supports it;
- parallelize read/search/audit work only;
- serialize writes, approval decisions, and proof generation;
- prefer deterministic local parsing, hashing, schema checks, and allowlist checks over model calls;
- run focused changed-file tests before broad CI;
- keep helper packets compact and structured;
- use the fast parent route for ordinary reasoning/coding/triage;
- escalate to the deep route only on explicit complexity triggers;
- use on-device helpers only for bounded tasks that do not need fresh external data and only after target-device benchmarking shows they are useful.

Preferred latency ladder:

```text
DETERMINISTIC_LOCAL
→ ON_DEVICE_BOUNDED_HELPER_IF_PROVEN
→ OPENAI_FAST_PARENT
→ OPENAI_DEEP_ON_COMPLEXITY_TRIGGER
```

Complexity triggers include difficult security/release audits, architecture redesign, conflicting source-of-truth evidence, subtle multi-file debugging, and a failed fast-route attempt with fresh evidence.

Do not call a path faster because it is local, smaller, or newer. Runtime speed claims require comparable target-device measurements.

## Google AI Edge Gallery evaluation lane

Google AI Edge Gallery is an experimental external on-device AI sandbox and benchmark harness. It may be used to evaluate approved local models and helper skills, but it is not LuHm OS source authority, a production dependency, a public deployment channel, or a mutation authority.

Use it for:
- local/offline model evaluation;
- TTFT/startup latency, decode throughput, memory, and thermal measurements;
- read-only helper-skill prototypes;
- determining whether a narrow task can move from a remote round trip to a local helper.

Hard boundaries:
- no automatic shell or privileged Android actions;
- no silent install or public publish;
- no API keys, signing material, private account tokens, or sensitive user data in Gallery skills, model assets, logs, or benchmark receipts;
- no direct canonical writes, self-approval, release, billing, DNS, signing, or crown authority;
- do not vendor upstream Gallery application code into the LuHm OS APK merely because the upstream project is open source;
- any direct LiteRT or other on-device runtime integration into LuHm OS requires a separate implementation proposal, CI, licensing review, and physical-device proof.

Path-specific rules live in `.github/instructions/google-ai-edge-gallery.instructions.md`, workflow guidance in `skills/google-ai-edge-gallery/SKILL.md`, and the current proposal in `project/hydra/doctrine/proposed-source-of-truth/KAI9000_PROPOSED_GOOGLE_AI_EDGE_LOW_LATENCY_DOCTRINE_20260917.json`.

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
- the in-app proof source is `backend/candidate_workflow.py` + `backend/web/mutation-candidate.html`;
- a helper-agent summary is never a substitute for executed CI or device evidence.

CI drift rule:
- workflows must validate crowned/current authority, not legacy doctrine merely because a historical path still exists;
- if a workflow gate depends on `lumh-os/kai9000/**` or `ultima/**` as active authority, classify it as drift and repair the gate before calling exact-head CI green;
- preserve legacy files as evidence, but remove them from current authority assertions unless a later crown explicitly re-promotes them.

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
