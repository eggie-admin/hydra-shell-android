# LuHm OS 10× Hard System Audit — 2026-09-11

**Overall state: YELLOW**  
**Final stock-device gate:** `LUHMOS_S24FE_FDROID_PUBLIC_INSTALL_GREEN`  
**Rooted laboratory goal:** `SM-X400` with separate package `art.eggiebagelface.luhmos.rooted`

This audit reconciles the active LuHm OS / KAI 9000 project history, current GitHub source, Samsung Android donor, Godot game donors, AI-provider contracts, signing policy, F-Droid publication, and physical-device installation path.

YELLOW is intentional. The architecture and release pipeline are now substantially hardened, but documentation and source changes are not equivalent to a shipped APK. Final GREEN requires current persistent signing evidence, a current signed public F-Droid repository, and physical S24 FE install/launch/update proof.

## Final architecture

### S24 FE production

```text
Samsung SM-S721U1 / Android 16
        ↓
art.eggiebagelface.luhmos
Godot 4 + bundled web cockpit + bounded Kotlin bridge
        ↓
normal Android package lifecycle
        ↓
public signed custom F-Droid repository
```

The stock application does **not** require root, Shizuku, Termux, Acode/AcodeX, VNC, Secure Folder, or a separately started localhost daemon.

### SM-X400 rooted laboratory

```text
already-rooted Samsung SM-X400
        ↓
art.eggiebagelface.luhmos.rooted
        ↓
explicit root-aware development experiments
```

The rooted lab is not an upgrade of the stock package, does not reuse its package identity, and must not silently root or exploit a device. Root access is an explicit precondition supplied by the operator.

## Ten passes

| Pass | Gate | State | Result |
|---:|---|---|---|
| 1 | Source of Truth / branch authority | YELLOW | Canonical branch is `luhmos-main`; current hardening is on sanctioned PR #34 and must merge only after CI. |
| 2 | Device / privilege separation | YELLOW | Stock S24 FE and rooted SM-X400 now have separate package/signing/update lineages. Implementation proof for rooted lab remains future work. |
| 3 | Package / version lineage | GREEN source contract | Stock package is `art.eggiebagelface.luhmos`; baseline 100 and update target 101. Old Video Forge/KAI package lines are blocked from release. |
| 4 | Signing / secrets | YELLOW | APK and F-Droid signers are separated and fail closed. Current LuHm fingerprints still need first persistent release evidence. |
| 5 | Reproducible build | YELLOW | Godot/Gradle checksums, SDK 36, lockfile integrity, ARM64 and release export are encoded in the new forge; the forge still needs a successful current run. |
| 6 | Android / WebView security | YELLOW | Audit found and removed Termux RUN_COMMAND, Termux package query, widget daemon control, localhost health dependency and mixed-content WebView behavior from the pinned donor. Build proof is pending. |
| 7 | JRPG / dating donor provenance | GREEN source contract | Owned and third-party donors are pinned with license boundaries; external art/audio is not automatically treated as LuHm-owned. |
| 8 | AI providers / privacy | YELLOW | OpenAI/HF are optional adapters, secrets stay outside APK, cross-vendor replay is explicit, AI cannot authorize release/root/signing. Latest CI after this mutation remains required. |
| 9 | F-Droid public repository | YELLOW | Old Video Forge repo doctrine is retired. New workflow builds a persistent-signed LuHm APK, signs v2/v1 indexes, and can publish a zero-secret `fdroid-public` branch. Not yet published. |
| 10 | Physical S24 FE install / update | YELLOW | ADB verifier proves device identity, F-Droid installer source, launcher start and 100→101 update. Physical proof has not yet been run. |

## Hard findings fixed by this audit

The audit found several issues that would have made a “GREEN” claim unsafe:

- The pinned Samsung donor still requested `com.termux.permission.RUN_COMMAND`, queried Termux, and used its widget to invoke a Termux service. Those dependencies were removed on donor commit `96c23c87713800fc17c80b6a972ee2e93f1bb4b1` and donor PR #20.
- The WebView allowed compatibility mixed content. It now uses `MIXED_CONTENT_NEVER_ALLOW`, rejects cookies, geolocation, popup JavaScript and database storage, and only permits external `https`/`mailto` navigation.
- Active F-Droid manifests still described `art.eggiebagelface.videoforge.dev` and historical v6/v7 bundles. They now describe only the current LuHm stock package and explicitly mark the old signed repo as historical.
- Three legacy workflows could still forge or validate retired KAI/Video Forge package lines. They now fail closed instead of publishing.
- The former Android “release” PR workflow required production secrets but did not actually produce a persistently signed release APK. PR CI is now contract-only; the secret-bearing release forge is isolated to `.github/workflows/luhmos-fdroid-public-release.yml`.
- The old trusted F-Droid signing helper could silently re-sign an APK whose signer did not match. That behavior is removed. A signer mismatch now aborts publication.
- The old physical-device verifier depended on Termux and an obsolete package. It now uses host ADB and verifies the stock LuHm package, F-Droid install source, launcher behavior and version upgrade.

## Public F-Droid route

The first public install proof no longer waits on Cloudflare or a Google VM. The signed repository can be published to the public `fdroid-public` branch and consumed directly at:

```text
https://raw.githubusercontent.com/eggie-admin/hydra-shell-android/fdroid-public/fdroid/repo/
```

F-Droid supports custom repositories served over HTTPS. The branded endpoint remains a later mirror target:

```text
https://fdroid.eggiebagelface.art/fdroid/repo/
```

The public branch contains only signed repository output and public fingerprints. Private APK/F-Droid keystores never enter that branch.

## Production release sequence

1. Merge donor hardening or retain the exact reviewed donor commit pin.
2. Merge PR #34 after required CI is GREEN.
3. Run `LuHm OS Public F-Droid Release` once with publication disabled to prove the persistent Android signer and F-Droid repository signer.
4. Pin the resulting public APK certificate SHA-256 and F-Droid repository fingerprint in repository variables.
5. Re-run the workflow with `publish_public_mirror=true`.
6. On the physical S24 FE, add the public repo using the pinned fingerprint and install versionCode 100 through F-Droid.
7. Run `scripts/final-form-device-verify.sh baseline-check` from an ADB host.
8. Produce versionCode 101 using the same Android signing identity, publish it to the same F-Droid repository, refresh F-Droid, and upgrade.
9. Run `scripts/final-form-device-verify.sh upgrade-check`.
10. Seal `LUHMOS_S24FE_FDROID_PUBLIC_INSTALL_GREEN` only when every check above has recorded evidence.

## Rooted SM-X400 goal

The rooted tablet lane is intentionally separate. Its goal record is:

`project/hydra/samsung/android/rooted/SMX400_ROOTED_DEV_GOAL_20260911.json`

Its package is `art.eggiebagelface.luhmos.rooted`, it may declare `RequiresRoot: true` in a custom F-Droid lane, and its privileged actions must require explicit user invocation. It does not root devices, exploit Android, reuse the stock signer, or replace the S24 FE package.

## Remaining real blockers

The remaining blockers are operational evidence, not architecture ambiguity:

- PR #34 must finish CI and merge.
- The hardened donor change needs build/review evidence.
- The current LuHm Android and F-Droid persistent signing material must be available to the release forge.
- The new release workflow must succeed and establish the two public certificate fingerprints.
- The signed `fdroid-public` repository must be published.
- The S24 FE must install versionCode 100 through F-Droid, launch successfully, then upgrade to 101 with the same signer.

Until those conditions are met, the correct state is **YELLOW**, not GREEN.
