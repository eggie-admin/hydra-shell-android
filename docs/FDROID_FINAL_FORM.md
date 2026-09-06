# KAI 9000 F-Droid Final Form

## Final goal

The final distribution goal for the LuHm OS / KAI 9000 Samsung lane is a **signed, addable F-Droid repository** that a user can import into an F-Droid client.

The APK is an intermediate artifact. The final artifact is the published F-Droid repository and its stable trust identity.

## Roleplay compiler

```text
AIRSHIP KAI9000
WARP GIT
BLACK_MAGIC FDROID
FINAL_FORM SIGNED_FDROID_REPOSITORY
```

Canonical phrases:

- **Enter Black Magic** = enter the F-Droid packaging/index/signing lane.
- **Forge the repository** = stage APK + metadata and run the F-Droid repo generator.
- **Airship passport** = persistent signing identity used for trusted updates.
- **Open the port** = publish the generated repository at an HTTPS endpoint suitable for F-Droid client import.
- **ULTIMA BLACK GREEN** = repository indexes, signing identity, package metadata, APK identity, fingerprint, publish endpoint, and client-import evidence are all verified.

Roleplay does not bypass key custody or publication gates.

## F-Droid repository shape

F-Droid supports simple binary repositories. The canonical working tree is:

```text
fdroid/
├── config.yml
├── metadata/
│   └── art.eggiebagelface.videoforge.dev.yml
└── repo/
    ├── art.eggiebagelface.videoforge.dev_<versionCode>.apk
    ├── index-v2.json
    ├── index-v1.jar
    ├── entry.jar / entry.json where generated
    ├── icons/
    └── other fdroidserver-generated index/signature files
```

The public endpoint should conventionally end in:

```text
/fdroid/repo/
```

## Two persistent signing identities

A reusable repository needs two stable identities.

### 1. APK signing identity

Android updates require subsequent APK versions to use a compatible persistent app signing certificate.

The current Oni Summoning testing workflow intentionally generates an **ephemeral debug APK key**. That is acceptable for smoke testing but is not a final update identity.

Before the long-lived F-Droid lane is called GREEN, replace ephemeral APK signing with a persistent, separately protected testing/release signing identity.

### 2. F-Droid repository signing identity

`fdroid init` / fdroidserver uses a repository key to sign the repository index. This fingerprint is what identifies and authenticates the custom repository to clients.

The repo key and passwords must never be committed to Git, embedded in the APK, Base64-backed up in source, exposed to a model, or printed to logs.

These two identities are separate concerns even if both use Java keystores.

## Current package

Pinned Samsung donor:

- repository: `eggie-admin/vue-headless-cms`
- commit: `86507ed7c72650ff508eb9a1a9e52842eb50e821`
- package: `art.eggiebagelface.videoforge.dev`
- version: `0.6.0-dev`
- versionCode: `6`

The donor already carries private F-Droid metadata for this package. This lane is a private/custom repository and does not imply acceptance into the official f-droid.org catalog.

## Build pipeline

```text
Copilot / code mutation
        ↓
Git Warp checkpoint
        ↓
Oni Summoning ULTIMA APK forge
        ↓
verified APK + evidence
        ↓
Black Magic F-Droid stage
        ↓
repo/ + metadata/ staging bundle
        ↓
trusted signing host / protected CI secret boundary
        ↓
fdroid update
        ↓
signed index + repository fingerprint
        ↓
HTTPS /fdroid/repo/
        ↓
F-Droid client import test
        ↓
ULTIMA FINAL FORM GREEN
```

## Current evidence

The first Oni Summoning workflow run completed successfully on commit `f04fa27c3ac4eff8de8b7dfe093659dd9e532152`.

Successful gates included:

- doctrine + Python preflight;
- Godot 4.7.2 installation and verification;
- Vue cockpit build;
- Godot Android plugin build;
- Samsung architecture checks;
- debug APK export;
- APK signing verification;
- 16 KiB zip alignment verification;
- APK evidence upload;
- Final ULTIMA testing gate.

That proves the APK forge. It does **not** yet prove the persistent signing and published F-Droid repository goal.

## Final-form GREEN requirements

Black Magic is GREEN only when all of these are proven:

1. APK was built from declared Git Warp coordinates.
2. APK package/version/ABI and SHA-256 are recorded.
3. APK uses the intended persistent app-signing identity for update continuity.
4. F-Droid metadata matches the package/version.
5. F-Droid repo staging bundle is generated.
6. A persistent F-Droid repo signing key signs the indexes.
7. Repository fingerprint is recorded and backed up separately from secrets.
8. Generated repository indexes validate.
9. Repository is published over HTTPS at an addable endpoint.
10. F-Droid client can add the repo and see/install KAI 9000.
11. A subsequent version can update the installed package without signing mismatch.

Until all requirements are met, report the precise state such as `APK_GREEN`, `FDROID_STAGED`, `FDROID_SIGNED`, `FDROID_PUBLISHED`, or `FDROID_IMPORT_VERIFIED` rather than claiming final-form GREEN.
