# LuHm OS · KAI 9000 · Project Hydra

**LuHm OS** = Linux / Unix approach Hydra manifest.  
**KAI 9000** = working title for the local-first AI/media/game subsystem.  
**Project Hydra** = integration architecture.  
**Samsung Android APK** = the current device-facing testing platform.

## Current lane

```text
testing/luhm-os-android
        │
        ├── doctrine + manifests
        ├── Python/Ollama localhost plane
        ├── Samsung/Termux trust contract
        ├── Copilot agent instructions
        ├── Oni Summoning / ULTIMA debug APK forge
        └── Black Magic / F-Droid repository lane
```

This branch is testing-only. Nothing here is automatically promoted or released.

## Mission
Build a reproducible Samsung Android cockpit that combines local AI, OpenAI-assisted coding/reasoning, Godot 4 UI/game systems, Python 3 orchestration, Ollama, FFmpeg/media tooling, Edge Gallery/widget surfaces, and controlled cloud integrations without giving models unrestricted device authority.

Project overview: `docs/LUHM_OS_KAI9000_OVERVIEW.md`  
Build altar: `docs/ULTIMA_BUILD_ALTAR.md`  
Fast build guide: `docs/BUILD_FAST.md`

## Final form

The distribution goal is no longer merely an APK artifact. **Final form is a signed custom F-Droid repository that can be added/imported into an F-Droid client.**

```text
AIRSHIP KAI9000
WARP GIT
BLACK_MAGIC FDROID
FINAL_FORM SIGNED_FDROID_REPOSITORY
```

Canonical final-form doctrine: `docs/FDROID_FINAL_FORM.md`  
Machine-readable goal: `fdroid/final-goal.manifest.json`  
Black Magic staging workflow: `.github/workflows/oni-black-magic-fdroid-stage.yml`

The long-lived repository requires two protected persistent identities: an APK signing identity for Android update continuity and an F-Droid repository signing identity for index/fingerprint trust. Neither belongs in Git, APKs, logs, Base64 backups, or model context.

## Canonical doctrine

- `lumh-os/kai9000/AI_MAGIC_DOCTRINE.md`
- `lumh-os/kai9000/project.manifest.json`
- `project/hydra/project.manifest.json`
- `project/hydra/samsung/android/apk/app.reference.json`
- `project/hydra/samsung/android/apk/testing-ingest.manifest.json`
- `fdroid/final-goal.manifest.json`

## APK source and build
This repository is the Android **orchestration altar**. The current APK body remains pinned in the public Samsung build candidate:

`eggie-admin/vue-headless-cms@86507ed7c72650ff508eb9a1a9e52842eb50e821`

That candidate contains the Vue cockpit, Godot 4 project, Godot Android v2 plugin, Samsung widget surface, Android export preset, private F-Droid metadata, and build sanity tools.

Canonical compile workflow:

`.github/workflows/oni-ultima-debug-apk.yml`

Testing output:

`kai9000-luhm-os-testing-debug.apk`

Android GREEN requires executed CI plus an installable APK, package identity, signature evidence, SHA-256, and 16 KiB alignment evidence.

After a successful push-triggered APK run, the Black Magic workflow stages the verified APK and donor metadata into a private F-Droid repository input bundle.

Release/debug template:
`release/TESTING_APK_DEBUG_TEMPLATE.md`

## Copilot compile architecture
Copilot is the implementation assistant. GitHub Actions is the deterministic build oracle.

Copilot reads:
- `.github/copilot-instructions.md`
- `.github/instructions/ultima-build.instructions.md`
- `AGENTS.md`

The lightweight setup workflow prepares Python, Java, Node, Gradle, doctrine references, and the pinned Samsung source without running the full APK export.

## AI stack
- **Lum / OpenAI**: remote reasoning, coding/spell compiler, typed agent/tool requests. Credentials remain server-side.
- **Ollama**: local inference at `127.0.0.1:11434`.
- **Python 3**: orchestration, policy, tests, feeds, local backend.
- **Godot 4**: Android cockpit/game/UI runtime.
- **Edge Gallery**: Samsung-facing local media/gallery surface.

More: `docs/AI_STACK.md`

## Samsung trust lane
Ordinary Termux owns the daemon/control plane. Samsung Secure Folder is a protected cockpit/client.

Canonical local services:
- AcodeX/AXS `127.0.0.1:8767`
- TigerVNC `127.0.0.1:5901`
- WebSocket bridge `127.0.0.1:6080`
- Hydra cockpit `127.0.0.1:8787`
- Ollama `127.0.0.1:11434`

No automatic root. Stock Shizuku is preferred when scoped privilege brokering is required. USB/UVC camera permission work stays isolated from the green control plane.

## Community and security
- `CONTRIBUTING.md`
- `SECURITY.md`
- `SUPPORT.md`
- `CODE_OF_CONDUCT.md`

## Copyright and licensing

Copyright © 2026 Eggie Bagelface in copyrightable original Project Hydra / LuHm OS / KAI 9000 material, subject to the scope and exclusions in `COPYRIGHT.md`.

This repository is **multi-license by component**:

- material governed by the root `LICENSE` remains GNU GPLv3;
- third-party material remains under its own license;
- independently owned Project Hydra beta material may be marked for noncommercial use under `docs/PROJECT_HYDRA_BETA_LICENSING.md`;
- Project Hydra branding, original artwork, character assets, and other separately owned material are not automatically licensed merely because GPL-covered source code is available.

Existing GPL rights are not revoked or narrowed. Commercial use of separately owned Project Hydra material marked `PROJECT HYDRA NONCOMMERCIAL BETA` requires separate permission.
