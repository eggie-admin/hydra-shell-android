# IzzyOnDroid App Inclusion Draft — LuHm OS

> Submit through the current IzzyOnDroid Maintenance Repo on Codeberg only after the
> canonical developer-signed GitHub Release exists and all PENDING fields below are
> replaced with evidence.

## App

- **Name:** LuHm OS
- **Application ID:** `art.eggiebagelface.luhmos`
- **Source:** https://github.com/eggie-admin/hydra-shell-android
- **Website:** https://eggiebagelface.art/
- **License:** GPL-3.0-only for GPL-covered repository source; third-party components retain their licenses
- **Category:** Development / Multimedia
- **Latest planned release:** `1.0.0` / versionCode `100`
- **APK architecture:** `arm64-v8a`
- **Target SDK:** 36
- **Release tag:** `v1.0.0` — PENDING
- **GitHub release URL:** PENDING
- **APK asset:** `luhmos-1.0.0.apk` — PENDING
- **APK SHA-256:** PENDING
- **Signing certificate SHA-256:** PENDING

## Short description

Standalone Godot creative AI and game cockpit for Samsung Android.

## FOSS/runtime statement

LuHm OS is a standalone Android application built around Godot 4 with bundled web
assets and bounded Android-native bridges. The stock package does not require root,
Termux, Acode/AcodeX, VNC, Samsung Secure Folder, Shizuku, or an externally launched
localhost daemon.

The source repository is public. Release APKs are built by the project release forge
and signed by the persistent developer signing identity. Updates preserve that identity.

## Network / AntiFeature disclosure

The app includes optional integrations with external network AI providers such as
OpenAI and Hugging Face. Those services are not required for base application launch.
`NonFreeNet` disclosure is appropriate for those optional non-free network services.

No ad SDK is intentionally included. No analytics-for-monetization SDK is intentionally
included. No proprietary payment SDK is required for donations/support.

## Permissions / security

Current release gates require:

- non-debuggable APK;
- no `testOnly` flag;
- no Termux RunCommand permission/package dependency;
- HTTPS for public network traffic;
- WebView mixed content disabled;
- origin-locked WebView bridge;
- cookies disabled in the bundled cockpit WebView;
- target SDK 36;
- arm64-v8a production artifact;
- Android 16 / 16 KiB compatibility evidence.

Exact permission list from release APK: **PENDING RELEASE EVIDENCE**.

## Self-update / installer behavior

The IzzyOnDroid candidate must not bypass IzzyOnDroid screening. Any historical
in-app updater code is not part of the canonical public distribution path unless it is
strictly opt-in, clearly identifies its source/provenance, and survives inclusion review.
The preferred update mechanism for this public lane is the F-Droid client receiving
new developer-signed releases through IzzyOnDroid.

## Reproducibility / provenance

The build pins Godot, Android build tools, Gradle distribution hashes, npm lockfile
provenance, Android package identity, signer identity, and 16 KiB zip alignment checks.
A reproducibility report should be attached or linked once the first persistent release
artifact is produced.

Godot/JRPG/dating-sim donor provenance is recorded in:

`project/hydra/games/GODOT4_JRPG_DATING_DONORS_20260910.json`

## Human-code support / donation

The project accepts the concept of voluntary external support for human-authored code,
architecture, documentation, art, integration, support and commissioned work while
preserving GPL and third-party license obligations.

**Funding endpoint:** PENDING. No donation link should be invented or submitted until
an actual project-controlled endpoint exists.

No payment/ad SDK is needed inside the APK for this support lane.

## Rooted laboratory build

A separate rooted-development package is planned for already-rooted Samsung SM-X400
lab devices:

`art.eggiebagelface.luhmos.rooted`

It has separate signing/update lineage and is **not** this submission.

## Maintainer checklist before filing

- [ ] PR #34 merged to `luhmos-main`
- [ ] Android donor hardening accepted/pinned
- [ ] persistent `luhmos-release` signing identity available
- [ ] release APK passes package/signature/permission/16 KiB gates
- [ ] GitHub `v1.0.0` release exists
- [ ] `luhmos-1.0.0.apk` attached to that release
- [ ] APK SHA-256 inserted above
- [ ] signing certificate SHA-256 inserted above
- [ ] exact permissions reviewed and explained
- [ ] release APK scanned for unwanted trackers/payment/ad libraries
- [ ] release notes and changelog published
- [ ] Fastlane/F-Droid metadata reviewed
- [ ] funding endpoint either verified and disclosed, or intentionally omitted
- [ ] current IzzyOnDroid inclusion policy rechecked immediately before submission
