# LuHm OS Canonical Doctrine

**Status:** normative architecture document  
**Canonical integration branch:** `luhmos-main`  
**Android application identity:** `art.eggiebagelface.luhmos`

This document defines the non-negotiable architecture and promotion rules for LuHm OS. The README is the map; this doctrine is the guardrail.

## 1. Authority model

LuHm OS separates suggestion, authorization, execution, proof, and release.

```text
Human operator
      │
      ▼
Lum / AI planning
      │ typed proposal
      ▼
Python 3 policy + control plane
      │ authorized action
      ▼
bounded worker / platform adapter / GitHub forge
      │ evidence
      ▼
CI + verification
      │
      ▼
human promotion
```

**Canonical law:** AI proposes. Python authorizes. CI proves. The human promotes.

No AI model is a root authority, signing authority, release authority, or unrestricted shell authority.

## 2. Branch doctrine

Development lanes:

- `luhmos/ai-logic`: models, routing, typed agent plans, AI policy, evaluations.
- `luhmos/backend`: Python control plane, APIs, jobs, state, authorization, adapters.
- `luhmos/frontend`: Godot/Vue/WebView UI and platform presentation.

Integration and release promotion:

```text
work lane -> luhmos-main -> luhmos/testing -> luhmos/proposed -> luhmos/beta -> luhmos/stable
```

Rules:

1. Work lanes merge into `luhmos-main` through review and CI.
2. Release maturity moves forward one channel at a time.
3. No feature development occurs directly on `beta` or `stable`.
4. Stable promotion requires reproducible evidence, not documentation claims.
5. Emergency fixes still use a bounded work lane and evidence gate.
6. Rollback targets must be explicitly identified sealed GREEN revisions.

## 3. Unix approach

LuHm OS prefers small, replaceable components connected by explicit contracts.

- Frontend presents state and requests actions.
- AI interprets intent and produces typed plans.
- Python owns application policy and authorization.
- Workers perform bounded jobs.
- Platform shells own platform lifecycle and permissions.
- CI independently verifies builds and artifacts.

Avoid hidden cross-layer authority. A UI component must not become a shell. A model adapter must not become a package manager. A build script must not become the runtime control plane.

## 4. Runtime boundaries

### Python 3

Python 3 is the canonical orchestration layer. It owns policy, state transitions, job coordination, API contracts, tool authorization, health checks, and recovery logic.

### Node/npm

Node/npm is build-time tooling unless a separately reviewed runtime requirement is approved. `npm ci` is preferred for deterministic automated dependency installation when a lockfile is present. Node is not the Android authority and npm is not an in-app package manager.

### Godot

Godot owns interactive application/runtime surfaces where appropriate and participates in Android packaging. Godot does not own secrets or AI policy.

### Kotlin / native platform code

Native platform code is a narrow bridge for capabilities that belong to Android or another host OS. Platform bridges should expose bounded functions to the shared control contract.

### Ollama and remote AI

Ollama is the preferred local inference daemon. Remote AI may provide reasoning or coding assistance when authorized. Provider choice never changes the authority model.

## 5. Lum magic doctrine

The Final Fantasy-inspired vocabulary is a typed command language over policy-approved actions.

- `LIBRA`: read-only inspection.
- `SCAN`: deeper read-only audit.
- `CURE`: minimal hotfix.
- `CURA`: bounded patch.
- `CURAGA`: broad/full mutation requiring explicit human approval.
- `ESUNA`: hardening and cleanup.
- `METEO`: stage reviewed GREEN work into the testing promotion path and invoke CI.
- `ULTIMA`: invoke a verified remote compile forge against an explicit GREEN revision.
- `PHOENIX`: human-approved rollback to an explicitly named sealed GREEN target.

Unknown spells fail closed. A spell never grants arbitrary model-generated shell execution, private-key access, branch-gate bypass, or silent stable promotion.

## 6. Android doctrine

Current active reference platform: Samsung Android 16 / ARM64.

Canonical identity:

```text
application ID: art.eggiebagelface.luhmos
release alias:  luhmos-release
target SDK:     API 36
primary ABI:    arm64-v8a
```

Android production GREEN requires, at minimum:

- successful required tests;
- correct application/package identity;
- persistent expected signer;
- install/update continuity where applicable;
- native-library and 16 KiB compatibility evidence;
- artifact SHA-256/provenance;
- appropriate APK/AAB packaging for the release lane;
- no private signing material in source or packaged assets.

A debug or ephemeral signer can prove compilation but cannot prove production release continuity.

## 7. Samsung Secure Folder doctrine

Ordinary Termux owns the local daemon/control plane. Samsung Secure Folder is a protected cockpit/client boundary.

The architecture must not depend on Secure Folder being able to inspect or control ordinary-Termux PIDs. Communication occurs through explicitly exposed local interfaces. The system must tolerate the protected cockpit being locked, stopped, or restarted without corrupting durable job state.

No root dependency is required for normal operation. Privilege-brokering experiments remain optional development lanes and must not become silent production requirements.

## 8. Secrets and signing

Private keys, keystores, passwords, API credentials, recovery secrets, and signing material never belong in:

- Git history;
- APK/AAB assets;
- public manifests;
- logs;
- AI prompts/model context;
- plaintext Source-of-Truth documents.

Public certificates, fingerprints, hashes, package IDs, aliases, and non-secret provenance may be recorded.

TLS identity and Android application signing are separate trust systems. Keys are never reused across those purposes.

Encrypted off-repository backups may exist in controlled private storage. Backup existence does not authorize exposing the decrypted material to an AI agent.

## 9. Distribution doctrine

Android has independent release lanes:

- direct/Samsung signed APK distribution;
- Google Play packaging when Play requirements are satisfied;
- signed F-Droid repository/source-build lane where policy permits.

Each lane may impose different packaging or submission rules, but all consume the same canonical application identity and verified source lineage unless a deliberate flavor/package split is documented.

## 10. Cross-platform doctrine

Platform status:

- Android/Samsung: ACTIVE.
- Apple: STAGED.
- Windows 11: STAGED.
- Ubuntu/Debian: STAGED.

The portable core is the policy/control contract and shared application logic, not a requirement that every OS use the same shell technology. Platform-specific shells should remain thin and replaceable.

## 11. Evidence states

### GREEN

Required checks actually executed and the evidence supports the claim.

### YELLOW

Work is staged, queued, partially verified, waiting for credentials/signing, or otherwise incomplete.

### RED

A required gate failed, expected evidence contradicts the claim, or the state cannot be safely verified.

Never promote YELLOW language into GREEN merely because architecture or documentation looks correct.

## 12. Milestone discipline

A sealed milestone records:

- canonical repository and revision;
- branch/channel;
- package/application identity where applicable;
- build/test evidence;
- signer fingerprint or public identity when applicable;
- artifact hashes/provenance;
- known YELLOW/RED gates;
- rollback target.

Milestones do not contain private secrets.

## 13. Recovery doctrine

Recovery should be boring.

- Preserve known GREEN revisions.
- Do not rewrite sealed history merely to make it look cleaner.
- Roll back to named revisions, never vague labels inferred by an AI.
- Durable jobs use explicit states such as queued, running, complete, failed, and interrupted.
- A restarted daemon must be able to determine what happened without relying solely on volatile memory.

## 14. Source-of-Truth hierarchy

1. Git repository: source, tests, CI, machine-readable architecture contracts.
2. Sealed milestone records: provenance and recovery anchors.
3. Controlled private storage: encrypted backups and private recovery material.

When prose and executable policy disagree, stop promotion and reconcile them. Do not silently choose whichever version is more convenient.

## 15. Final goal

LuHm OS becomes a reproducible, signed, updateable, auditable, local-first creative application ecosystem. Lum can help inspect, plan, code, patch, build, render, test, and recover it through bounded automation. The human operator retains destructive authority, signing authority, and final release promotion.

The project succeeds when recovery, builds, upgrades, and policy are as dependable as the creative surfaces are ambitious.
