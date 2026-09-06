# KAI 9000 / LuHm OS Testing APK Release Template

> This document is for a **testing/debug APK**, not a production release.

## Release identity

- Release name: `KAI9000_LUHM_OS_TESTING_DEBUG_<YYYYMMDD>_<RUN>`
- Branch: `testing/luhm-os-android`
- Hydra Shell commit: `<commit-sha>`
- Samsung donor: `eggie-admin/vue-headless-cms`
- Donor commit: `86507ed7c72650ff508eb9a1a9e52842eb50e821`
- Workflow: `Oni Summoning - Ultima Debug APK`
- Workflow run: `<run-number-or-url>`

## Artifact

- APK: `kai9000-luhm-os-testing-debug.apk`
- Package ID: `<aapt-package-id>`
- Version name: `<version-name>`
- Version code: `<version-code>`
- ABI: `arm64-v8a`
- SHA-256: `<sha256>`
- Signing mode: `ephemeral CI debug`

## Build matrix

- Godot: `4.7.2`
- Android platform: `36`
- Build tools: `36.1.0`
- Android Gradle Plugin: `8.13.2`
- Gradle: `8.13`
- Kotlin Android plugin: `2.2.21`
- JDK: `17`
- Python: `3.14`
- Node: `24.18.0`
- npm: `12.0.2`

## ULTIMA evidence

- [ ] doctrine preflight GREEN
- [ ] Python compile GREEN
- [ ] backend tests GREEN
- [ ] Hydra sanity audit GREEN
- [ ] Vue cockpit build GREEN
- [ ] Godot Android plugin build GREEN
- [ ] Samsung architecture gates GREEN
- [ ] Godot Android export GREEN
- [ ] APK signature verification GREEN
- [ ] 16 KiB zip alignment GREEN
- [ ] package identity recorded
- [ ] arm64-only native payload verified
- [ ] CMS asset embedded
- [ ] APK SHA-256 recorded

## Install test

Device:
- Manufacturer: Samsung
- Model: `<device-model>`
- Android: `<android-version>`

Install command, when ADB is explicitly authorized:

```bash
adb install -r kai9000-luhm-os-testing-debug.apk
```

Result:
- [ ] installs successfully
- [ ] launches successfully
- [ ] localhost cockpit reachable
- [ ] Ollama unavailable state degrades gracefully
- [ ] Secure Folder remains client-only

## Known limitations

- Debug signing only. Not production identity.
- USB/UVC camera access may remain blocked by Android/Knox permission boundaries.
- OpenAI credentials are not embedded in the APK.
- Optional AI/media services may be unavailable without affecting base launch.

## Doctrine statement

This artifact is **TESTING GREEN** only if the executed workflow and installation evidence support that statement. It is not automatically promoted, merged, published, store-submitted, or production-signed.

Canonical doctrine:
- `lumh-os/kai9000/AI_MAGIC_DOCTRINE.md`
- `lumh-os/kai9000/project.manifest.json`
- `project/hydra/samsung/android/apk/testing-ingest.manifest.json`
