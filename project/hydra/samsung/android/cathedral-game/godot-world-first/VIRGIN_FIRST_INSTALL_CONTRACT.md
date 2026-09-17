# LuHm OS 1.0.9 Virgin First-Install Contract

Candidate state: `AMBER_PENDING_PHYSICAL_FIRST_INSTALL_PROOF`

This candidate is intended to prove a true Android first install. It must not depend on any previously installed LuHm OS package, migrated app data, pre-existing save file, shell bridge, network bridge, or elevated privilege.

## Required package identity

- package: `art.eggiebagelface.luhmos`
- versionName: `1.0.9`
- versionCode: `109`
- minSdk: `24`
- targetSdk: `36`
- ABI: `arm64-v8a`
- expected release signer SHA-256: `598d7272d62dbebb71972d6164822636ad1439cd35631d0cd43321d003c92142`

The release signer remains the persistent LuHm OS signer even for a virgin first install. A clean install does not require signer continuity with an installed package, but retaining the canonical signer preserves future update continuity.

## Fresh profile acceptance

On a profile where `art.eggiebagelface.luhmos` is not installed and `user://luhmos_physical_proof.cfg` does not exist:

1. Android Package Installer requires visible human confirmation.
2. Install succeeds without uninstall/migration helper requirements.
3. LuHm OS launches in portrait.
4. Full Cockpit proof text reports `INSTALL: VIRGIN_FIRST_RUN`.
5. `SAVEPOINT: 0` and `RESTORED SESSION: NONE` are visible before the first save.
6. `SPRITE_BUBBLE -> WIDGET_DECK -> FULL_COCKPIT` works.
7. `GAME / ADMIN / SYSTEM` remain presentation realms only.
8. A local SAVEPOINT changes install state to `LOCAL_STATE_SEALED`.
9. Relaunch can report `RESTORED_LOCAL_STATE` with the prior savepoint/session receipt.

## Hard prohibitions

- no silent install
- no public publish
- no shell execution
- no browser-stored API keys
- no network requirement for first render
- no privilege bridge
- no automatic deletion of an existing LuHm OS profile merely to manufacture a clean test

CI may prove source/build/package/signature properties. Only a real clean Android profile can prove the virgin-install milestone GREEN.
