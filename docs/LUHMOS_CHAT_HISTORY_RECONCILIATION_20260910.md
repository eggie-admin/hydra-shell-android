# LuHm OS Chat-History Reconciliation — 2026-09-10

**Purpose:** convert the relevant LuHm OS / KAI 9000 ChatGPT project history into a compact current Source of Truth without allowing superseded experiments to keep mutating production architecture.

This record is a reconciliation document, not build evidence. Git source, CI, artifact hashes, signer identity, and physical-device proof remain authoritative for GREEN claims.

## Current canon accepted

### Product target

- Product: **LuHm OS**, with **KAI 9000** retained as subsystem/working-title vocabulary.
- Canonical repository: `eggie-admin/hydra-shell-android`.
- Canonical integration branch: `luhmos-main`.
- Active device: Samsung **SM-S721U1 / Galaxy S24 FE**.
- Android: **16**.
- Canonical application ID: `art.eggiebagelface.luhmos`.
- Target SDK: **36**.
- Primary ABI: **arm64-v8a**.
- Release signing alias: `luhmos-release`.

### North-star Android gate

The production goal is a normal Android APK:

```text
tap/install -> Android package install -> launcher icon -> open -> base app works
```

Production GREEN requires persistent signer continuity, clean install, direct launcher start, update continuity, package identity evidence, artifact SHA-256/provenance, and 16 KiB/native compatibility evidence.

A successful debug/ephemeral compile is useful build evidence but is not the final standalone release GREEN.

### Standalone boundary

The following are retired as production dependencies:

- Termux / Termux:API / Termux:Widget;
- Acode / AcodeX / AXS;
- TigerVNC;
- websockify or a desktop bridge;
- Samsung Secure Folder as required cockpit/runtime;
- separately launched localhost daemons;
- root or Shizuku for ordinary operation.

They may remain in historical commits, migration notes, or development references. They do not define current production architecture.

### Android application architecture

- Godot 4: primary user-visible Android/game runtime and packaging surface.
- Vue/Web assets: bundled application UI where used, not an external development server requirement.
- Kotlin/native Android: narrow platform bridge only.
- Python 3: canonical reference language for policy, backend adapters, build orchestration, tests, and evidence. Android production may not require an externally installed Python runtime.
- Node/npm: build-time tooling only unless a separately reviewed packaged runtime requirement exists.

## Godot 4 game/JRPG/dating-sim lineage

### Owned donor

The current owned prototype donor is:

```text
repo:   eggie-admin/3d-chat-interface
branch: kai9000-jrpg-dating-cathedral-20260906
commit: 457c31f2bcb040aba3d6a0b36a25cf1a63587359
```

Verified donor code includes JRPG cockpit, battle director, overworld/map code, dating director, roleplay director, Lum avatar stage, original fanfare, Cathedral direction/content, Godot project/export configuration, and an S24 FE build helper.

This donor's historical Gemma/Ollama/local-WebSocket setup is not inherited as a production dependency.

### Third-party framework donors

`kuryart/godot-jrpg`

- MIT licensed;
- current observed main revision during reconciliation: `6d62e6e75d9533240eddc289a991607f39ef5780`;
- Godot 4.6+ 2D JRPG framework reference;
- integrate selectively and pin exact revision before vendoring;
- donor sample assets retain their own credited licenses and must not be reclassified as LuHm-owned art.

`nathanhoad/godot_dialogue_manager`

- MIT licensed;
- current observed main revision during reconciliation: `934ff537cee96e1484a2430066b685283999d40c`;
- Dialogue Manager 4 targets Godot 4.6+;
- use as the single dialogue runtime rather than creating competing dialogue engines;
- relationship/social/game state remains LuHm-owned state, exposed to the stateless dialogue runtime.

Machine-readable donor record:

`project/hydra/games/GODOT4_JRPG_DATING_DONORS_20260910.json`

### Owned social/dating layer

Current owned direction includes relationship ranks, flags, gifts, social events/rewards, dating/roleplay direction, story routing, save integration, and UI. Items that are planned but not present in a pinned commit must remain labeled planned/evolving rather than falsely claimed as implemented.

## OpenAI provider reconciliation

Current first-party OpenAI model documentation was rechecked on 2026-09-10.

Canonical references:

```text
fast/default interactive: gpt-5.6-luna
deep architecture/review: gpt-5.6-sol
API surface:              Responses API
```

These are runtime-configurable model references, not immutable architecture. Evidence records the actual resolved model used.

The previous chat-era `gpt-6-astra` identifier is **retired/superseded** and must not be treated as current Source of Truth.

OpenAI credentials are not APK content. Base application launch does not depend on OpenAI availability.

## Hugging Face provider reconciliation

Current Hugging Face Inference Providers documentation and Hub metadata were rechecked on 2026-09-10.

Canonical provider reference:

```text
base:      https://router.huggingface.co/v1
responses: POST /v1/responses   # beta
chat:      POST /v1/chat/completions
```

Reference model repositories:

```text
openai/gpt-oss-120b
openai/gpt-oss-20b
```

Both are recorded as Apache-2.0 models. `:fastest`/`:cheapest`/`:preferred` or explicit-provider suffixes are routing policy, not ownership or license changes.

HF tokens are not APK content. Model-download authority is separate from inference authority. Downloaded models require pinned revision, license, provenance, hashes where practical, and `trust_remote_code=false` by default.

## Historical artifacts retained, not promoted

The following families are retained as provenance/history but do not override current canon unless explicitly re-adopted:

- old `testing/luhm-os-android` assumptions that conflict with `luhmos-main` branch doctrine;
- prior package IDs such as `art.eggiebagelface.videoforge.dev` or KAI dev package identities;
- SM-X400-first device assumptions;
- Termux/AcodeX/VNC/Secure-Folder runtime ownership doctrine;
- rooted or Shizuku-required production approaches;
- direct WebView/server development scaffolds that require external daemons;
- ephemeral/debug APK signer claims presented as production signing proof;
- stale provider/model identifiers;
- donor/sample art, audio, or copyrighted corpus material without explicit license/provenance approval.

Sealed historical milestone files remain valid as records of what was proven at the time. They are not automatically the current architecture.

## Source-of-Truth precedence

When project chat, memory, old docs, and current code disagree, use this order:

1. current Git source and machine-readable contracts on the sanctioned branch;
2. current canonical doctrine and explicit sealed milestone records;
3. CI/artifact/signature/device evidence for factual GREEN claims;
4. prior chat history only as design/provenance input;
5. superseded historical experiments as archival context only.

A chat decision becomes durable architecture only after it is reconciled into repository doctrine/contracts and survives CI/review.

## Current milestone state

**Sealed goal:** `LUHMOS_S24FE_STANDALONE_APK_GOAL_20260910`.

**Next GREEN gate:** `LUHMOS_S24FE_STANDALONE_APK_GREEN`.

That next gate means the canonical LuHm OS package is persistently signed, installs normally on the SM-S721U1, launches from the Android launcher without development runtimes, and demonstrates signed update continuity with recorded evidence.
