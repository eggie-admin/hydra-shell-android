# LuHm OS — IzzyOnDroid Publication + Human-Code Monetization Lane

**Date:** 2026-09-11  
**Status:** YELLOW — submission candidate, not yet accepted/published

## Public distribution priority

1. **IzzyOnDroid** — preferred public F-Droid-compatible binary distribution lane.
2. **LuHm OS signed custom F-Droid repo** — bootstrap/fallback and independent trust anchor.
3. **Official F-Droid main repo** — later source-build/reproducibility lane if/when its stricter inclusion/build requirements are met.

IzzyOnDroid is a good fit because it distributes official developer-built and developer-signed APKs taken from the upstream project repository, with a preference for APKs attached to tagged releases.

## Canonical production package

```text
Name:           LuHm OS
Package:        art.eggiebagelface.luhmos
Version:        1.0.0
VersionCode:    100
Target SDK:     36
Primary ABI:    arm64-v8a
License:        GPL-3.0-only for repository-root GPL-covered source
Source:         https://github.com/eggie-admin/hydra-shell-android
Release signer: persistent luhmos-release identity
```

The stock build does not require root, Termux, Acode/AcodeX, VNC, Secure Folder, Shizuku, or a separately launched localhost daemon.

The rooted SM-X400 laboratory package is separate:

```text
art.eggiebagelface.luhmos.rooted
```

It is not submitted as an update/replacement for the stock IzzyOnDroid candidate.

## IzzyOnDroid acceptance preparation

Before submission:

- publish the exact persistently signed APK as a GitHub Release asset;
- create an immutable release tag matching the APK version;
- keep source for that exact release publicly available;
- retain the same Android signing certificate on updates;
- ensure the APK is not debuggable or testOnly;
- ensure public network traffic is HTTPS;
- keep requested permissions minimal and documented;
- remove self-updaters or keep any package-install/update feature strictly opt-in with clear provenance disclosure;
- publish Fastlane-compatible localized metadata, icon, screenshots and changelog where practical;
- preserve all third-party code/media license notices;
- provide reproducible-build information and deterministic build pins where practical;
- keep APK size controlled, preferring the arm64-v8a production artifact rather than unnecessary fat-ABI packaging.

Submission itself should use the current IzzyOnDroid Maintenance Repo process (currently hosted on Codeberg). Acceptance remains an external maintainer decision and must never be claimed GREEN until the package appears in IzzyOnDroid and installs from that repository.

## Human-code monetization doctrine

The monetization lane supports the human-authored work without turning the APK into an ad/payment container.

### Allowed

- donation/support links in F-Droid/Izzy metadata;
- Liberapay;
- Open Collective;
- a clearly identified HTTPS project support page;
- optional GitHub Sponsors/FUNDING metadata when an actual funding account exists;
- paid human services around the FOSS codebase, such as commissioned features, support, consulting, asset creation, customization, training, or hosted services, provided GPL and third-party license obligations are honored;
- public attribution/provenance identifying human-authored code, edits, architecture, art, documentation and integration where accurate.

### Not part of the Izzy candidate APK

- ad SDKs;
- analytics-for-monetization SDKs;
- proprietary in-app purchase SDKs merely to collect support payments;
- paywalls that make GPL source unavailable;
- claims that AI-generated material is human-authored;
- licensing language that attempts to revoke GPL rights for GPL-covered code;
- hidden telemetry or payment tracking.

## Donation metadata

Do **not** invent a funding account or donation URL.

Until the Professor selects and verifies a real funding endpoint, use:

```text
monetization_status: FUNDING_ENDPOINT_PENDING
```

When a real endpoint exists, add it to upstream Fastlane/F-Droid metadata and `.github/FUNDING.yml` where supported. Prefer a public project-controlled HTTPS support page, Liberapay, or Open Collective because these can be represented cleanly by F-Droid metadata.

## Ownership and provenance

`COPYRIGHT.md` remains the authorship/provenance notice. The root `LICENSE` remains GPL-3.0 for covered source. Third-party donors keep their own licenses and notices. AI-assisted development does not automatically create a copyright claim in machine-only output; human-authored selection, edits, code, documentation, architecture and integration are recorded honestly.

## Izzy-specific release contract

A release intended for IzzyOnDroid must satisfy all of the following:

```text
IZZY_SOURCE_PUBLIC
IZZY_GITHUB_RELEASE_ASSET_PRESENT
IZZY_IMMUTABLE_TAG_PRESENT
IZZY_PERSISTENT_SIGNER_VERIFIED
IZZY_NON_DEBUG_APK
IZZY_PERMISSION_REVIEW_COMPLETE
IZZY_HTTPS_NETWORK_POLICY
IZZY_METADATA_COMPLETE
IZZY_LICENSE_PROVENANCE_COMPLETE
IZZY_NO_PAYMENT_OR_AD_SDK_MONETIZATION
```

Final acceptance gate:

```text
LUHMOS_IZZYONDROID_PUBLIC_INSTALL_GREEN
```

This gate requires the LuHm OS package to be visible in IzzyOnDroid, refreshed in the user's F-Droid client, installed on the SM-S721U1 from IzzyOnDroid, launched successfully, and later upgraded with the same Android signing identity.
