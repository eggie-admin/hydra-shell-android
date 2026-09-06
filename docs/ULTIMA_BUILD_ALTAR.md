# ULTIMA Build Altar

## Purpose
The ULTIMA build altar is the final testing gate for the LuHm OS / KAI 9000 Samsung APK lane.

It has one job: turn a code change into a verified testing APK as quickly as possible without weakening doctrine.

## The summon

```text
Copilot patch
    ↓
Doctrine preflight
    ↓
Pinned Samsung donor checkout
    ↓
Vue cockpit build
    ↓
Godot Android plugin build
    ↓
Godot 4 Android debug export
    ↓
APK signature + package + alignment + SHA-256 evidence
    ↓
ULTIMA_TESTING_GREEN
```

## Oni Summoning
“Oni Summoning” is the compile workflow name, not a privilege bypass.

Canonical workflow:
`.github/workflows/oni-ultima-debug-apk.yml`

It runs two major jobs in parallel:

1. **Doctrine + Python preflight**
   - compiles Python;
   - runs backend tests;
   - runs the Hydra sanity harness;
   - verifies doctrine/manifests;
   - rejects forbidden secret/deployment markers.

2. **Godot Android debug forge**
   - checks out the pinned public Samsung build candidate;
   - restores npm, Gradle, and Godot caches;
   - builds the Vue cockpit;
   - builds the Android plugin;
   - runs Samsung architecture gates;
   - exports an ephemeral-debug-signed APK;
   - verifies the APK and uploads evidence.

The final `ultima-gate` succeeds only when both jobs succeed.

## Pinned altar

- Donor: `eggie-admin/vue-headless-cms`
- Donor commit: `86507ed7c72650ff508eb9a1a9e52842eb50e821`
- Godot: `4.7.2`
- Android API: `36`
- Build tools: `36.1.0`
- Android Gradle Plugin: `8.13.2`
- Gradle: `8.13`
- Kotlin Android: `2.2.21`
- JDK: `17`
- Python: `3.14`
- Node: `24.18.0`
- npm: `12.0.2`

## Speed doctrine
Speed comes from eliminating repeated work, not deleting checks.

- cancel superseded runs on the same branch;
- cache npm downloads;
- use Gradle's native Actions cache;
- cache verified Godot archives;
- run preflight and APK compile in parallel;
- pin the donor so dependency exploration is unnecessary;
- use debug signing for testing builds;
- upload only the APK and evidence needed for the testing decision.

## GREEN evidence
A testing APK is GREEN only when the workflow produces:

- `kai9000-luhm-os-testing-debug.apk`;
- APK SHA-256;
- signing verification output;
- zipalign 16 KiB verification;
- `aapt` package/badging evidence;
- APK content listing showing arm64 and embedded CMS assets;
- successful doctrine preflight.

A green chat response is not evidence. A Copilot suggestion is not evidence. A third-party hosting status is not evidence.

## Secrets
The testing build uses an ephemeral debug keystore generated inside CI. It is not a production signing identity.

Never commit:
- OpenAI API keys;
- OAuth tokens;
- release signing keys;
- keystore passwords;
- private voice recordings;
- proprietary game runtime assets;
- model weights.

## Promotion
This workflow only proves **TESTING GREEN**. It does not merge, release, publish, or submit the APK.

Promotion remains a separate explicit action after review and device validation.
