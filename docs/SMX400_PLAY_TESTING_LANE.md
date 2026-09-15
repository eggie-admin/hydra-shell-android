# Samsung SM-X400 · Unrooted Google Play Testing Lane

Milestone: `LUHMOS_SMX400_PLAY_INSTALL_PORTAL_PROPOSED_20260915`

## Purpose

Use the Samsung Galaxy Tab S10 Lite `SM-X400` as a clean, stock Android 16 compatibility cockpit for LuHm OS / KAI 9000 while keeping build authority, signing and source history remote and reproducible.

This lane does **not** replace the existing production device contract. It adds a second stock-device compatibility target for tablet UI, physical keyboard operation, remote AI/provider UX and signed install/update testing.

## Device contract

```text
manufacturer: Samsung
model: SM-X400
Android: 16
ABI: arm64-v8a
root: false
bootloader unlock: not required
Shizuku: not required
Termux runtime dependency: false
Acode runtime dependency: false
VNC/WebSocket runtime dependency: false
```

The tablet is an operator surface. It is not the canonical compiler, signing machine or source of truth.

## Authority chain

```text
Professor
   │ approves promotion/destructive actions
   ▼
GitHub / luhmos-main
   │ canonical source + CI + release evidence
   ├── OpenAI      remote reasoning / typed proposals
   ├── Hugging Face model registry / provenance-gated forge
   ├── Google Cloud optional keyless remote infrastructure
   └── Google Drive controlled recovery/artifact mirror
   ▼
Signed LuHm OS release
   ▼
SM-X400 Android package installer
```

Models propose. Application policy authorizes. CI proves. Android confirms installation. The Professor promotes.

## Bootstrap install and update portal

The safest first in-app install/update experience is a **trusted browser handoff**, not a silent package installer.

The LuHm OS cockpit exposes an `INSTALL / UPDATE` control that opens only:

`https://github.com/eggie-admin/hydra-shell-android/releases/latest`

The release page is produced by the same remote source/build system and can contain the persistently signed APK plus SHA-256 and signer evidence. The user downloads the APK and Android's normal package installer performs the final confirmation.

This deliberately avoids adding `REQUEST_INSTALL_PACKAGES` to the LuHm OS app for the bootstrap lane. It also avoids embedding GitHub credentials or release tokens in the APK.

### Why this is the sane stock-Android path

- no root;
- no silent install capability;
- no package-manager bypass;
- no private signing key on the tablet;
- Android enforces signer continuity for upgrades;
- the install source remains visible to the operator;
- rollback is a release-management problem rather than an opaque in-app mutation.

A future signed F-Droid feed may become the preferred updater once its public mirror/fingerprint gate is deliberately promoted. The direct GitHub release surface remains a useful bootstrap/recovery route.

## Remote pipeline

```text
feature branch / PR
        │
        ▼
LuHm contract CI
tests · doctrine · secret scan · donor pin
        │
        ▼
human approval
        │
        ▼
Persistently signed release forge
Godot · Android plugin · bundled cockpit
        │
        ├── APK signature evidence
        ├── SHA-256
        ├── package identity
        ├── arm64-v8a
        ├── API 36
        └── 16 KiB alignment
        │
        ▼
GitHub Release
        │
        ├── optional signed F-Droid repository
        └── optional Google Cloud mirror via OIDC
        │
        ▼
In-app INSTALL / UPDATE portal
        │
        ▼
Android user-confirmed installer
```

Google Cloud authentication uses GitHub OIDC / Workload Identity Federation where configured. Do not create a long-lived service-account JSON key merely to make the tablet installer work.

## AI/provider integration

Provider availability is additive. The base app must still boot when every remote provider is offline.

- **OpenAI**: remote reasoning, coding/review and typed tool proposals. No signing or release authority.
- **Hugging Face**: model discovery, metadata, licenses and explicitly approved inference/model supply. No policy authority.
- **Google Cloud**: optional remote compute/storage/services through bounded identities and short-lived credentials.
- **GitHub**: code/provenance/build/release authority.
- **Google Drive**: recovery/library mirror where explicitly used. Drive does not silently overwrite Git history.

No provider token belongs in committed source, bundled web assets or screenshots intended as doctrine.

## Tablet UX targets

The SM-X400 test pass should explicitly exercise:

- landscape and portrait cockpit layout;
- paired physical keyboard navigation and text entry;
- touch/trackpad behavior;
- WebView boot with no localhost dependency;
- offline startup;
- external trusted install portal handoff;
- Android package install/upgrade confirmation;
- OpenAI/Hugging Face/Google Cloud provider states failing gracefully;
- suspend/resume and rotation without losing the cockpit.

## Promotion gates

This lane stays testing-only until all of the following are evidenced:

1. source/doctrine CI GREEN;
2. donor/cockpit build GREEN;
3. no new dangerous Android permission for the bootstrap install portal;
4. signed APK evidence GREEN;
5. clean install on stock SM-X400;
6. launcher start without Termux/Acode/VNC or another daemon;
7. keyboard/touch smoke test GREEN;
8. install portal opens only the allowlisted HTTPS release origin;
9. update continuity succeeds with the same Android signing identity;
10. human approval before any public-feed promotion.

## Out of scope

Rooting, OEM unlock, automatic package installation, hidden privilege brokers, arbitrary model-generated shell commands, background self-publishing and storing signing material on the tablet are explicitly out of scope for this lane.