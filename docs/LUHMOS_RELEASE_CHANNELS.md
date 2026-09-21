# LuHm OS Samsung Android Release Channels

Canonical product anchor: `luhmos-main`
Paid-Pro working branch: `luhmos/dev/samsung-android-paid-pro`
Platform scope: Samsung Android only
Package: `art.eggiebagelface.luhmos`

## Promotion ladder

`luhmos/dev/samsung-android-paid-pro` -> `luhmos/testing` -> `luhmos/proposed` -> `luhmos/preview` -> `luhmos/beta` -> `luhmos/stable` -> reviewed promotion back to `luhmos-main`

Promotion is forward-only. Fixes start in the paid-Pro development branch and re-enter the ladder. A downstream lane never silently pushes code backward into an earlier lane.

## Channel contracts

| Channel | Branch | Release tag pattern | GitHub release state | Purpose |
|---|---|---|---|---|
| Testing | `luhmos/testing` | `vX.Y.Z-testing.N` | draft/prerelease | CI, emulator/device smoke tests, experimental Samsung Android validation |
| Proposed | `luhmos/proposed` | `vX.Y.Z-proposed.N` | draft/prerelease | review candidate after testing evidence exists |
| Preview | `luhmos/preview` | `vX.Y.Z-preview.N` | prerelease | early usable preview for controlled testers |
| Beta | `luhmos/beta` | `vX.Y.Z-beta.N` | prerelease | broader pre-stable Samsung Android validation |
| Stable | `luhmos/stable` | `vX.Y.Z` | normal release | physically proven, signed, reviewed release |

`luhmos-main` remains the canonical product/release anchor. The channel branches are promotion lanes, not separate products.

## Required evidence per promotion

Every promotion must preserve source commit SHA, build workflow run, artifact SHA-256, Android signer fingerprint, package/version metadata, test summary, known blockers, and the Professor approval gate when the action is RECKONING-tier.

Stable additionally requires physical Samsung install/update acceptance, launch/render proof, CROWN/HUD behavior where applicable, save/reload persistence, and reboot/return proof for the chosen release target.

## GitHub Releases policy

Non-stable lanes are prereleases. Testing and Proposed default to draft prereleases. Preview and Beta may be published prereleases after review. Stable is the only channel that may create a normal non-prerelease release.

The repository control branch `main` owns the release-channel controller workflow. Product code stays on the LuHm OS channel branches. Release automation may create tags and release pages, but successful CI never grants merge, signing, publishing, install, or Crown authority by itself.

## Safety

No API tokens, Android signing keys, Cloudflare secrets, Google credentials, payment data, or private CA material may be committed to any public branch. Paid service status never grants execution authority.

## Legacy lane preservation

The pre-reroll heads of Testing, Proposed, Beta, and Stable were archived on 2026-09-16 before the canonical channel reset. Those archive branches are history only and must not be used as current release inputs.
