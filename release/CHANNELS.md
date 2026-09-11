# LuHm OS release channels

Canonical integration trunk: `luhmos-main`

Promotion flow:

`luhmos-main` -> `luhmos/testing` -> `luhmos/proposed` -> `luhmos/beta` -> `luhmos/stable`

## Channel rules

### luhmos-main
Integration trunk. New platform scaffolding and accepted subsystem work land here first. It is not a release channel.

### luhmos/testing
Fast validation lane. CI, emulator/device smoke tests, package identity, signing checks, ABI checks, and platform-specific build experiments happen here.

### luhmos/proposed
Release-candidate staging. Only changes that passed testing may enter. Dependency and toolchain pins are frozen unless the change is the explicit subject of the proposal.

### luhmos/beta
Human/device beta lane. Requires reproducible build evidence, checksums, signing lineage, rollback notes, and platform test evidence.

### luhmos/stable
Production release lane. Promotion-only. No direct feature development. Stable artifacts must be reproducible from the recorded source SHA and use persistent production signing identities.

## Platform policy

Android is the active implementation lane. Apple, Windows 11, and Ubuntu/Debian are staged repository contracts only until they gain real build systems and CI. A staged lane must never be reported GREEN as an installable product.

## Security

No private signing keys, TLS private keys, tokens, passwords, or secret material may be committed to any channel. Public certificates and fingerprints may be tracked. Android signing and TLS identities remain separate.
