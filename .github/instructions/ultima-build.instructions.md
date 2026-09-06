---
applyTo: ".github/workflows/**,backend/**,tools/**,tests/**,lumh-os/**,project/hydra/**,release/**"
---

# ULTIMA Build Instructions

For any build, CI, Android, Python, Godot, release, or doctrine mutation:

1. Read `lumh-os/kai9000/AI_MAGIC_DOCTRINE.md` and `project/hydra/samsung/android/apk/testing-ingest.manifest.json` first.
2. Work only in `testing/luhm-os-android` unless the user explicitly names another branch.
3. Keep the Samsung APK donor pinned to `eggie-admin/vue-headless-cms@86507ed7c72650ff508eb9a1a9e52842eb50e821` unless the task is explicitly a donor promotion.
4. Prefer a minimal patch that preserves loopback-only local services and the Secure Folder client boundary.
5. Run the fastest relevant check first, then the full required gate. Do not remove verification to make CI faster.
6. Never add secrets or proprietary runtime assets to source, logs, artifacts, manifests, Base64 payloads, or APK contents.
7. Copilot may write or repair code. Copilot may not declare a build green. Only executed CI/build evidence may do that.
8. ULTIMA for Android requires an installable APK plus SHA-256, signature, package identity, 16 KiB zip alignment, and architecture evidence.
9. External hosting/deployment statuses are non-authoritative for Android doctrine.
10. Use `release/TESTING_APK_DEBUG_TEMPLATE.md` when documenting a testing APK artifact.
