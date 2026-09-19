# LuHm OS / KAI 9000 Copilot Instructions

## Mission
Build and maintain the Samsung Android testing lane for **LuHm OS / KAI 9000**. Optimize for small patches, reproducible builds, fast feedback, and truthful execution evidence.

Read these before mutation:
- `docs/CROWN_SOURCE_OF_TRUTH_20260919.json`
- `lumh-os/kai9000/CODING_ROLEPLAY_DOCTRINE.md`
- `lumh-os/kai9000/AI_MAGIC_DOCTRINE.md`
- `lumh-os/kai9000/project.manifest.json`
- `project/hydra/samsung/android/apk/testing-ingest.manifest.json`
- `docs/ULTIMA_BUILD_ALTAR.md`
- `AGENTS.md`

## Branch doctrine
- Current integration lane: `testing/luhm-os-android`.
- Do not promote to `luhmos-main` or `main` automatically.
- Preserve rollback points and current user work.
- Prefer focused patches over tree-wide rewrites.
- When the Professor explicitly says `push`, `ship`, `set sail`, or otherwise authorizes repo mutation, prepare and push the bounded change to the testing lane, then report commit SHA and CI state.

## KAI coding-roleplay compiler
Treat KAI coding-roleplay language as coding/orchestration DSL in engineering context.

**Questforge and other fun/tabletop roleplay are a separate system.** They are governed by `docs/QUESTFORGE_ROLEPLAY_DOCTRINE.md` and must never compile into engineering actions, Git operations, shell execution, Android operations, CI actions, publishing, account changes, credentials, or infrastructure mutations.

Canonical engineering tokens:
- **KAI 9000 / Airship** = integration/runtime vehicle.
- **Warp** = Git transport through refs, branches, commits, PRs, merges, checkpoints, and history.
- **GitHub / Blue Magic** = hosted source of truth, collaboration, Actions/CI, and evidence surface.
- **Set sail / Airship launch** = begin execution from the current verified checkpoint.
- **Warp coordinates** = repository + branch/ref + commit SHA + target lane.
- **Altar** = reproducible build/test environment.
- **Oni** = bounded worker agents/tools.
- **Lum / Supreme Witch** = top-level AI orchestrator and spell compiler. This never overrides the Professor, policy gates, credentials, CI, signing authority, or repository permissions.
- **Save Crystal** = non-destructive rollback checkpoint.
- **Green rune** = actual passed execution evidence.
- **ULTIMA** = final convergence requiring evidence from every required lane.

Never interpret coding roleplay as permission escalation. Never interpret fictional/game roleplay as coding roleplay.

## ULTIMA doctrine
ULTIMA is GREEN only when:
1. donor/quarantine preflight passes with `DONOR_PURGED_BEFORE_APK=true`;
2. the KAI-owned Android source builds;
3. an installable debug APK exists;
4. APK identity, signature, SHA-256 and 16K alignment evidence exist;
5. required Samsung/loopback security boundaries remain intact.

Copilot proposes and edits. GitHub Actions compiles and verifies. CI is the build oracle.

## Canonical Android source topology
The future APK body is KAI-owned and lives in this repository:
- native project: `luhmos/samsung-android-s24/native-cathedral/`
- cockpit assets: `luhmos/samsung-android-s24/live2d-chat/`
- active APK workflow: `.github/workflows/kai9000-ultima-apk.yml`

Do not check out or package a historical donor repository in the active APK workflow.

## Chrome Dev / Canary doctrine
- Chrome Dev and Chrome Canary are behavior/test harnesses only.
- Never ingest, port, copy, vendor, or package Chrome Dev/Canary binaries or source into the KAI APK.
- Upstream Chromium source may be consulted only as an explicit reference with license/provenance notes where reused implementation details require them.
- Browser harness behavior may guide compatibility tests, WebView assumptions, and debugging, but KAI implementation remains KAI-owned.

## Historical donor doctrine
- Historical KAI donor material is reference/provenance only, not an active release input.
- Do not copy donor trees into `app/src`, assets, resources, generated release inputs, or APK bundles.
- Do not vendor donor `.apk`, `.aar`, `.jar`, or `.so` files.
- Preserve `THANKS.md` as the friendly attribution/thank-you record.
- Any retained concept must be reimplemented in the KAI-owned tree and documented for provenance/license obligations when applicable.

## Pinned testing toolchain
- Android platform: API 36
- Android build tools: 36.1.0
- Android Gradle Plugin: 8.13.2
- Gradle: 8.13
- Kotlin Android plugin: 2.2.21
- JDK: 17
- Python: 3.14

Pin versions. Never substitute dynamic `latest` dependencies in release/build logic.

## Fast-build policy
- Use dependency caches instead of vendoring dependency trees.
- Cancel superseded CI runs on the same ref.
- Run doctrine/preflight before APK artifact claims.
- Never skip APK verification to save time.
- Canonical workflow: `.github/workflows/kai9000-ultima-apk.yml`.

## AI architecture
- **Lum/OpenAI**: remote reasoning/spell compiler and typed tool-request layer.
- **GitHub Copilot**: implementation, code repair, focused edits, tests, documentation, commit/PR preparation, CI repair, and push-ready handoff under Professor authorization.
- **Ollama**: localhost-first Android/local inference daemon.
- **Python 3**: orchestration, policy, tests, feed normalization, local backend and build sanity.
- **Native Android/Kotlin**: KAI-owned Android shell/runtime bridge.

Never translate free text directly into privilege escalation or unreviewed shell execution.

## Samsung trust boundary
- Ordinary Termux owns local daemon/control-plane processes.
- Samsung Secure Folder is a protected cockpit/client.
- Local services bind to loopback.
- No automatic root.
- Stock Shizuku is preferred only when privileged Android operations explicitly require it.
- Camera/USB permission work remains isolated from the green control plane.

Historical/recheck-only endpoints are governed by the Crown source of truth. Do not revive AcodeX/AXS or other historical services unless a fresh Crown explicitly authorizes it.

## Secrets and external status
Never commit API keys, OAuth tokens, signing secrets, voice recordings, model weights, proprietary game assets, browser donor payloads, or credentials. Base64 is encoding, not encryption.

External hosting/deployment status has zero authority over Android GREEN. Android authority comes from repository CI, donor-purge evidence, reproducible build evidence, installable APK evidence, package identity, signature, SHA-256, alignment, and device/emulator validation.

## Completion language
Distinguish exactly between: edited, committed, pushed, CI-started, CI-green, artifact-produced, APK-verified, installed, merged, released, published.

Never claim a state without evidence.
