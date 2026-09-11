# LuHm OS · KAI 9000 · Project Hydra

**LuHm OS** = **Linux / Unix approach Hydra manifest**.  
**KAI 9000** = working title for the local-first AI, media, game, and device subsystem.  
**Project Hydra** = the integration architecture joining AI logic, backend services, frontend/cockpit surfaces, build forges, and platform targets.

`luhmos-main` is the **canonical integration branch**. Work is developed in bounded lanes, proven by CI, merged here, then promoted through explicit release channels. Main is not a scratch branch and stable is never a shortcut.

## Final goal

Build a **local-first, Unix-shaped creative operating environment** whose first production target is a **proper self-contained Samsung Android APK** that installs through the normal Android package installer, launches without a development terminal, and updates under one persistent signing identity.

The final system should provide:

- one Lum user-facing AI agent with typed, policy-gated tools;
- Python 3 as the reference orchestration and authorization layer, with Android runtime behavior packaged or migrated into APK-safe components rather than requiring an external interpreter;
- AI provider adapters that may use packaged/local or authorized remote inference without making an external daemon mandatory for app launch;
- Godot 4 plus bundled web/Vue surfaces for the interactive cockpit;
- FFmpeg/media capabilities only when packaged in an Android-compatible form or delegated through an explicitly optional provider;
- deterministic GitHub CI for compilation, testing, provenance, and artifacts;
- persistent Android signing identity for update continuity;
- a signed F-Droid repository as the independent Android distribution lane where policy permits;
- staged platform homes for Android, Apple, Windows 11, and Ubuntu/Debian;
- no requirement for a model to receive unrestricted shell, root, signing keys, or production authority.

The architecture should remain understandable with ordinary Unix ideas: small components, explicit interfaces, text/configuration where practical, replaceable processes, observable state, least privilege, and boring recovery paths.

## Branch workflow

```text
WORK LANES

luhmos/ai-logic  ─┐
luhmos/frontend  ─┼── PR + CI ──> luhmos-main
luhmos/backend   ─┘                    │
                                      ▼
RELEASE PROMOTION

luhmos-main
    │
    ▼
luhmos/testing
    │
    ▼
luhmos/proposed
    │
    ▼
luhmos/beta
    │
    ▼
luhmos/stable
```

### Work-lane responsibilities

**`luhmos/ai-logic`**
- Lum agent behavior and routing
- typed tool/spell plans
- model/provider adapters
- AI policy and evaluation
- no direct production authority

**`luhmos/backend`**
- Python 3 control-plane contracts and reference implementation
- APIs, jobs, authorization, policy enforcement, state, and platform adapters
- Android production logic must be packaged or bridged inside the application boundary rather than requiring Termux or another external runtime
- the final application-policy authority for privileged actions

**`luhmos/frontend`**
- Godot/Vue/WebView cockpit
- Android/platform presentation
- media/game/UI surfaces
- consumes typed application APIs
- never owns private credentials or unrestricted shell authority

**`luhmos-main`** integrates proven work. Release branches only receive forward promotion. Feature work does not target `beta` or `stable` directly.

Canonical topology: `project/hydra/LUHMOS_BRANCH_TOPOLOGY.json`  
Human workflow contract: `docs/LUHMOS_WORK_LANES.md`  
CI enforcement: `.github/workflows/luhmos-lane-gates.yml`

## Unix approach

LuHm OS follows Unix-style separation of concerns without requiring Unix userland applications on Android.

```text
USER / LUM
    │
    ▼
ANDROID APPLICATION
Godot · bundled Vue/WebView · Kotlin bridge
    │ typed requests
    ▼
APPLICATION POLICY / CONTROL CONTRACT
state · jobs · authorization
    │
    ├── packaged/local capability adapters
    ├── authorized remote AI when configured
    ├── media workers packaged for Android when supported
    ├── GitHub remote build forge
    └── Android platform adapters
```

Core laws:

1. **Standalone first on Android.** The installed APK must launch without Termux, Acode/AcodeX, VNC, a WebSocket desktop bridge, or Secure Folder.
2. **One job per layer.** UI presents, AI proposes, policy authorizes, bounded workers execute.
3. **Least privilege.** No automatic root and no model-generated arbitrary shell execution.
4. **Explicit interfaces.** Cross-layer work uses typed requests, manifests, APIs, files, or bounded worker contracts.
5. **Replaceable parts.** AI providers, UI, media workers, and platform adapters can evolve without replacing the whole cathedral.
6. **Observable state.** Health checks, CI evidence, hashes, signatures, manifests, and logs establish GREEN.
7. **Fail closed.** Unknown commands, missing signing identity, failed tests, or unverifiable artifacts stop promotion.
8. **Secrets stay outside source.** Private keys, API credentials, keystores, and passwords never belong in Git, APK assets, logs, or AI prompts.

## Lum magic automation

The Final Fantasy-inspired command language is a **typed automation vocabulary**, not a shell language.

```text
LIBRA   = read-only inspection
SCAN    = deeper audit
CURE    = smallest hotfix
CURA    = bounded patch
CURAGA  = full mutation; human approval required
ESUNA   = hardening / cleanup
METEO   = stage reviewed GREEN work into testing + CI
ULTIMA  = invoke the verified remote compile forge on an explicit GREEN ref
PHOENIX = rollback to an explicitly named sealed GREEN target
```

A spell compiles into a policy-checked action plan. It cannot override branch gates, CI, signing requirements, or human approval. `ULTIMA` means **compile and prove**, not “merge everything.”

Doctrine: `docs/LUHMOS_LUM_MAGIC_DOCTRINE.md`.  
Machine contract: `project/hydra/LUHMOS_LUM_MAGIC_MANIFEST.json`.

## Android / Samsung current platform

Samsung Android is the first fully active platform lane.

Canonical target and identity:

```text
device:                 Samsung SM-S721U1 (S24 FE)
Android:                16
package/application ID: art.eggiebagelface.luhmos
release signing alias:  luhmos-release
target SDK:             API 36
primary ABI:            arm64-v8a
```

The production target is one normal installable APK that the user can **Install → Open**. The application must not require Termux, Acode, AcodeX, TigerVNC, websockify, Secure Folder, or another localhost daemon in order to start and perform its core functions.

Production Android GREEN requires:

- a successful clean install on the SM-S721U1;
- successful launch from the Android launcher with no development-runtime dependency;
- canonical package identity `art.eggiebagelface.luhmos`;
- persistent `luhmos-release` signer and update continuity evidence;
- successful required tests;
- SHA-256/provenance for the artifact;
- arm64-v8a and 16 KiB/native-library compatibility evidence;
- no private signing material or credentials in Git or packaged assets.

Optional external services may augment the application, but absence of those services must not prevent the base application from launching.

## Distribution lanes

Android distribution is deliberately multi-lane:

```text
GitHub CI artifact
      │
      ├── Samsung / direct signed APK lane
      ├── Google Play AAB lane when release policy is satisfied
      └── signed F-Droid repository lane
```

The long-lived Android identities are the APK/app signing identity and the F-Droid repository signing identity. They are separate trust anchors and neither is stored in source control.

Canonical F-Droid goal: `docs/FDROID_FINAL_FORM.md`  
Machine-readable goal: `fdroid/final-goal.manifest.json`

## Platform roadmap

```text
Android / Samsung    ACTIVE
Apple                STAGED SCAFFOLD
Windows 11           STAGED SCAFFOLD
Ubuntu / Debian      STAGED SCAFFOLD
```

The goal is not to force identical platform shells. The portable asset is the policy/control contract and shared application logic. Each platform may use the native shell that makes the most sense while preserving the same security and agent boundaries.

## Milestones

### M0 · Doctrine and Source of Truth
- establish LuHm OS naming, architecture, security boundaries, manifests, and reproducible repository doctrine
- **state: established**

### M1 · Local Cathedral
- historical development baseline for local AI/control-plane experiments
- Termux/AcodeX/VNC/WebSocket work is retained only as migration history and is not a production dependency
- **state: historical GREEN baseline; superseded for Android runtime architecture**

### M2 · Samsung Android Forge
- Godot/Android application shell
- canonical package `art.eggiebagelface.luhmos`
- API 36 / ARM64 / 16 KiB baseline
- deterministic GitHub build lane
- ULTIMA identity forge has produced GREEN compile evidence
- **state: GREEN forge, standalone device-install gate still active**

### M3 · Standalone Install, Persistent Signing and Distribution
- produce a self-contained APK requiring no Termux/Acode/AcodeX runtime
- prove clean install and launcher start on SM-S721U1
- prove persistent `luhmos-release` signer
- produce install/update continuity evidence
- maintain 16 KiB/native compatibility
- harden direct/Samsung, Play, and F-Droid packaging lanes
- **state: active gate**

### M4 · Lum Typed Agent
- one visible Lum personality
- local/remote model routing
- typed tool authorization
- Final Fantasy-inspired magic automation
- CI-backed GitHub forge invocation
- **state: active development**

### M5 · Video Forge Cathedral
- media orchestration
- authored creative asset workflow
- Godot media/game presentation
- deterministic render/build provenance
- **state: developing**

### M6 · Cross-platform LuHm OS
- mature Android implementation
- activate Apple, Windows 11, and Ubuntu/Debian platform shells
- preserve shared agent/security/control contracts
- **state: staged**

### FINAL · Reproducible Creative Cathedral
A signed, updateable, auditable, local-first application ecosystem where Lum can help plan, code, build, render, inspect, and recover the system through bounded automation while the human operator retains release, signing, and destructive authority.

## Definition of GREEN

A claim is GREEN only when evidence exists. Depending on the lane that means tests actually ran, builds actually completed, artifacts exist, expected package identity is verified, signing identity is verified, hashes/provenance are recorded, and required policy gates passed.

Documentation intent is not build evidence. A compile-GREEN APK is not yet standalone-install GREEN until physical-device installation and launch evidence exists.

## Source of Truth

Repository doctrine is authoritative for code-adjacent contracts and machine-readable manifests. Sealed milestones and private backup material may be mirrored to controlled private storage. Secrets are never copied into public doctrine.

Key repository references:

- `ARCHITECTURE.md`
- `AGENTS.md`
- `SECURITY.md`
- `docs/LUHMOS_CANONICAL_DOCTRINE.md`
- `docs/LUHMOS_WORK_LANES.md`
- `project/hydra/project.manifest.json`
- `project/hydra/LUHMOS_BRANCH_TOPOLOGY.json`
- `project/hydra/samsung/android/apk/app.reference.json`
- `docs/LUHMOS_S24FE_STANDALONE_APK_GOAL_20260910.md`
- `docs/FDROID_FINAL_FORM.md`
- `fdroid/final-goal.manifest.json`

## Development principle

> **AI proposes. Policy authorizes. CI proves. The human promotes.**

That is the center of LuHm OS.

## Copyright and licensing

Copyright © 2026 Eggie Bagelface in copyrightable original Project Hydra / LuHm OS / KAI 9000 material, subject to `COPYRIGHT.md`.

This repository is multi-license by component. Material governed by the root `LICENSE` remains under that license; third-party material remains under its own license; separately owned branding, artwork, characters, and specifically marked material retain their applicable terms. Existing open-source rights are not revoked or narrowed.

See `COPYRIGHT.md`, `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md`, and `SUPPORT.md` for the controlling details.
