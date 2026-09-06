# LuHm OS / KAI 9000 Copilot Instructions

## Mission
Build and maintain the Samsung Android testing lane for **LuHm OS** (Linux / Unix approach Hydra manifest), working title **KAI 9000**. Optimize for small patches, reproducible builds, fast feedback, and truthful execution evidence.

Read these before mutation:
- `lumh-os/kai9000/AI_MAGIC_DOCTRINE.md`
- `lumh-os/kai9000/project.manifest.json`
- `project/hydra/samsung/android/apk/testing-ingest.manifest.json`
- `docs/ULTIMA_BUILD_ALTAR.md`
- `AGENTS.md`

## Branch doctrine
- Current integration lane: `testing/luhm-os-android`.
- Do not promote to another branch automatically.
- Preserve rollback points and current user work.
- Prefer focused patches over tree-wide rewrites.

## ULTIMA doctrine
ULTIMA means convergence on a verified final artifact. It is not permission to bypass tests or approvals.

For the Android goal, ULTIMA is GREEN only when:
1. doctrine/preflight checks pass;
2. the pinned Samsung donor builds;
3. an installable debug APK exists;
4. APK identity, signature, SHA-256 and alignment evidence exist;
5. required security boundaries remain intact.

Copilot proposes and edits. GitHub Actions compiles and verifies. CI is the build oracle.

## Android source topology
This repository is the orchestration/doctrine altar. The pinned APK body is:
- repository: `eggie-admin/vue-headless-cms`
- ref: `86507ed7c72650ff508eb9a1a9e52842eb50e821`
- Godot project: `godot/`
- Android plugin: `godot/android-plugin/`

Do not silently copy the donor tree into this repository. Update the pin only as an explicit reviewed mutation.

## Pinned testing toolchain
Use the proven donor build matrix unless a separate toolchain-upgrade task explicitly changes it:
- Godot: 4.7.2
- Android platform: API 36
- Android build tools: 36.1.0
- Android Gradle Plugin: 8.13.2
- Gradle: 8.13
- Kotlin Android plugin: 2.2.21
- JDK: 17
- Python: 3.14
- Node: 24.18.0
- npm in APK forge: 12.0.2

Pin versions. Never substitute dynamic `latest` dependencies in release/build logic.

## Fast-build policy
- Use dependency caches instead of vendoring generated dependency trees.
- Cancel superseded CI runs on the same ref.
- Run Python/doctrine preflight and APK build as parallel jobs.
- Do not redownload verified Godot archives when cache hits are available.
- Never skip APK verification to save time.

Canonical workflow: `.github/workflows/oni-ultima-debug-apk.yml`.

## AI architecture
- **Lum/OpenAI**: remote spell compiler, coding/reasoning and typed tool-request layer. OpenAI credentials are server-side only and are never stored in source or APK.
- **Ollama**: localhost-first Android/local inference daemon at `127.0.0.1:11434`.
- **Python 3**: orchestration, policy, tests, feed normalization, local backend and build sanity.
- **Godot 4**: native Android cockpit/game/UI shell and Android plugin host.
- **Edge Gallery**: Samsung-facing local media/gallery surface. It consumes approved local/reference content and does not become a remote hosting authority.

For OpenAI agent work use typed function tools and guardrails. Never translate free text directly into an executable shell command or privilege escalation.

## Samsung trust boundary
- Ordinary Termux owns local daemon/control-plane processes.
- Samsung Secure Folder is a protected cockpit/client.
- Local services bind to loopback.
- No automatic root.
- Stock Shizuku is preferred when privilege brokering is required.
- No arbitrary model-authored shell.
- Camera/USB permission work remains isolated from the green control plane.

Canonical local ports:
- AcodeX/AXS `127.0.0.1:8767`
- TigerVNC `127.0.0.1:5901`
- WebSocket bridge `127.0.0.1:6080`
- Hydra cockpit `127.0.0.1:8787`
- Ollama `127.0.0.1:11434`

## Secrets and external status
Never commit API keys, OAuth tokens, signing secrets, voice recordings, model weights, proprietary game assets or credentials. Base64 is encoding, not encryption.

External hosting/deployment statuses have zero authority over Android GREEN. Android authority comes from repository CI, reproducible build evidence, installable APK evidence, package identity, and device/emulator validation.

## Completion language
Distinguish exactly between: edited, committed, CI-started, CI-green, artifact-produced, APK-verified, installed, proposed, merged, released, published.

Never claim a state without evidence.
