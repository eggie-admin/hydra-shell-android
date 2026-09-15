# Samsung Universal APK Dungeon

Date: 2026-09-15
State: testing mutation

This lane merges the Samsung development dungeon into the LuHm OS integration dungeon without creating a second Android product identity.

## One APK family

Use one LuHm OS Android package for the supported stock Samsung ARM64 devices:

- Galaxy S24 FE family (`SM-S721*`), including the existing S24 phone work.
- Samsung tablet test lane (`SM-X400`).
- Galaxy S10 Lite family (`SM-G770*`) as the older unrooted compatibility target.

The Android source candidate now makes API 24 the explicit minimum, API 36 the target, and `arm64-v8a` the production ABI. Screen-size support remains enabled from small through xlarge.

The package stays `art.eggiebagelface.luhmos`. Update continuity comes from the same persistent release signer, not per-device APK forks.

## Samsung Secure Folder

The S24 Secure Folder lane is a protected cockpit/client instance of the same signed LuHm OS APK. It is not a build forge and does not own release signing material. Secure Folder keeps its own app data, while the owner-profile install and Secure Folder install remain separate Android instances of the same package.

The install path remains ordinary Android user-controlled installation. The app does not add a broad package-install permission and does not attempt a silent cross-profile install.

## Universal install portal

The cockpit Settings page exposes `INSTALL / UPDATE`, which hands off over HTTPS to the canonical GitHub Releases `latest` page. Android/browser/package-installer UI keeps final authority over the actual installation or update.

This is the bootstrap lane. A signed F-Droid feed and Google Play testing can remain additional distribution lanes after explicit promotion. They are not required for base app launch.

## Device proof

A device is not declared GREEN from the model name alone. Runtime `deviceSnapshot()` evidence records manufacturer, model, SDK, ABI and WebView package/version. Physical smoke testing still proves install, launch, rotation/input where applicable, offline base launch and same-signer update continuity.

## Source-of-truth split

- GitHub: versioned source, CI, release and provenance.
- Google Drive: recovery mirror / dungeon archive.
- Google Cloud: optional keyless OIDC infrastructure.
- OpenAI and Hugging Face: bounded reasoning/provider roles, not release authority.

The universal-Samsung mutation stays in draft/testing until the Professor promotes it.
