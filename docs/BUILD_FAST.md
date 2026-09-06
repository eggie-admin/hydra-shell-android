# Fast Build Guide

## Goal
Get from patch to verified Samsung testing APK with the shortest safe feedback loop.

## Local fast lane
Run the cheap checks first:

```bash
python -m compileall -q backend tools ultima/ollama-ffmpeg-antenna-v3
python -m pytest -q backend/tests
bash tests/hydra-sanity-audit-test.sh
```

If these fail, fix them before spending Android build minutes.

## GitHub compile lane
Use:

`Actions → Oni Summoning - Ultima Debug APK → Run workflow`

Target branch:
`testing/luhm-os-android`

The workflow checks out the exact Samsung donor commit referenced by doctrine, restores caches, and builds the testing APK.

## Cache strategy
The workflow intentionally caches only disposable build inputs:

- npm download cache;
- Gradle dependency/build cache through `gradle/actions/setup-gradle`;
- verified Godot editor/export-template archives.

Do not cache secrets, keystores, generated APK signatures, user data, or private model assets.

## Why the donor stays pinned
The Android source currently lives in `eggie-admin/vue-headless-cms`. Pulling a fixed commit gives the compile bot a deterministic body and keeps Hydra Shell focused on policy/orchestration.

Changing the donor pin is a dependency promotion and should be reviewed like a source update.

## Debug build contract
Testing output:
`kai9000-luhm-os-testing-debug.apk`

Expected evidence:
- SHA-256 file;
- APK signature report;
- 16 KiB zipalign report;
- package badging report;
- APK contents report.

Debug signing is ephemeral CI signing. Never use a debug artifact as a production release identity.

## Speed rules for agents
- inspect before editing;
- edit the smallest surface;
- do not regenerate lock files unless required;
- do not bump toolchain versions during unrelated fixes;
- do not disable tests to make a build pass;
- do not download model weights in CI;
- do not start optional cloud integrations during APK compilation;
- cancel stale runs and repair the newest failure.
