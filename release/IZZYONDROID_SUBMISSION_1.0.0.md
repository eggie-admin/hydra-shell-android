# LuHm OS 1.0.0 — IzzyOnDroid submission record

## Upstream release

- Repository: https://github.com/eggie-admin/hydra-shell-android
- Canonical source branch: `luhmos-main`
- Release tag: `v1.0.0`
- Release APK: `luhmos-1.0.0.apk`
- Package ID: `art.eggiebagelface.luhmos`
- Version: `1.0.0` (`versionCode` 100)
- License: GPL-3.0-only
- Target SDK: 36
- ABI: arm64-v8a
- Root required: no

## Release identity

- Android APK signer SHA-256: `0108A9FBF1EF63183CC749B102F5FAEFEFA5AD6F1F668A2686199EC0D5671DD5`
- LuHm OS custom F-Droid repository fingerprint SHA-256: `8235EC85F755C8851009D55DC2E8CB90D09CB5DFEBE3DB4AB34802BFE393E200`

Private signing material is never committed. Public release automation must verify these fingerprints before publication.

## IzzyOnDroid request payload

Submit only after the signed `v1.0.0` GitHub Release is visible and its APK signer matches the pinned fingerprint above.

Suggested inclusion details:

- App name: LuHm OS
- Source repository: https://github.com/eggie-admin/hydra-shell-android
- Package ID: `art.eggiebagelface.luhmos`
- Release page: https://github.com/eggie-admin/hydra-shell-android/releases/tag/v1.0.0
- Direct APK: https://github.com/eggie-admin/hydra-shell-android/releases/download/v1.0.0/luhmos-1.0.0.apk
- License: GPL-3.0-only
- Fastlane metadata: `fastlane/metadata/android/en-US/`
- APK is an official upstream binary built by GitHub Actions from the tagged canonical source.
- No root, Termux, Shizuku, VNC, AcodeX, or external localhost daemon is required for the stock build.
- Optional remote AI integrations are network-backed and are disclosed as `NonFreeNet` in the custom F-Droid metadata.

IzzyOnDroid inclusion is an external maintainer decision. Do not claim inclusion until the package is visible in the IzzyOnDroid repository.

## Install after inclusion

Official IzzyOnDroid F-Droid-compatible repository:

`https://apt.izzysoft.de/fdroid/repo?fingerprint=3BF0D6ABFEAE2F401707B6D966BE743BF0EEE49C2561B9BA39073711F628937A`

In Samsung Secure Folder, add that repository to the F-Droid client, refresh, search for **LuHm OS**, verify package `art.eggiebagelface.luhmos`, then install using Android's normal package confirmation flow.
