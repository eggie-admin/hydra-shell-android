# Video Forge Cathedral Android/F-Droid Architecture

## Rule zero

Node/npm is a build-time tool only. The Android APK must not embed a Node runtime, npm, a package manager, shell package installation, or writable self-updating executable code.

## Rule one

The Samsung production APK must be a normal self-contained Android application. It must install through Android package installation and launch from the Android launcher without requiring Termux, Acode/AcodeX, TigerVNC, websockify, Secure Folder, or another separately launched local daemon.

Optional external providers may augment capabilities, but the base application must still launch and expose its core UI when they are absent.

## Layers

1. **Policy/control plane** — Python 3 remains the reference orchestration implementation in source and CI. Android runtime policy must be packaged inside the application boundary or implemented through bounded native/application components. An external Python interpreter is not a production dependency.
2. **npm/Vue build plane** — a pinned web frontend checkout is installed with `npm ci` and compiled with Vite.
3. **Static payload** — generated `dist/` assets are copied into the application payload for encapsulation by the app shell.
4. **Godot Android shell** — Godot owns UI/native runtime and Android export. Kotlin/native code provides only bounded Android bridges. Use Gradle build templates when AAB/custom Android project behavior is required.
5. **Provider adapters** — AI/media/network integrations are explicit capabilities. External providers are optional unless a release flavor explicitly declares otherwise.
6. **Distribution lanes** — build separate artifacts/configurations for direct Samsung APK, F-Droid, and commercial stores. Never make the F-Droid variant depend on proprietary SDKs, Google Play Services, Firebase, proprietary analytics, or secret API keys.

## Reproducibility gates

- Commit `package-lock.json` for each npm project and use `npm ci`, never floating `npm install`, in CI.
- Pin Node/npm, Python, JDK, Godot, Android SDK/Build Tools/NDK, Gradle/AGP as applicable.
- Build from a clean checkout.
- Do not commit keystores, deploy tokens, `.env`, generated credentials, or signing passwords.
- Treat every native `.so` as part of the 16 KB page-size compatibility gate.
- Produce unsigned or CI-signed artifacts according to the release lane; F-Droid upstream/source builds must remain fully buildable from source.
- Verify `art.eggiebagelface.luhmos` identity before promotion.
- Verify the expected persistent signer for production promotion.
- Prove clean install, launcher start, and update continuity on the Samsung SM-S721U1 before standalone Android GREEN.
- Fail the release gate if the application requires a development helper app or external localhost daemon to start.

## Release lanes

### F-Droid

FLOSS-only dependencies and source. Prefer a reproducible APK. No Play-only SDK requirements. Metadata lives separately from secrets. Build server must be able to reproduce the release from source.

### Google Play

Use Godot Gradle Android export and release signing; produce AAB for Play distribution. Keep Play-specific dependencies behind a separate flavor/build lane so the F-Droid source lane stays clean.

### Samsung / sideload

Produce a release-signed APK from the same canonical source lineage. The direct APK is the primary physical-device proof lane for the SM-S721U1.

## Build contract

```text
source checkout
  -> policy/doctrine validation
  -> npm ci --ignore-scripts in pinned UI checkout
  -> npm run build
  -> bundle static UI into Android application
  -> build Android-native bridges/plugins
  -> Godot/Gradle Android build in CI
  -> verify package / signer / ABI / 16 KB / provenance
  -> physical-device install + launcher smoke test
```

Build tooling prepares and verifies the application artifact. It does not bypass Android package installation/security policy, install a terminal environment, or create a hidden package manager inside the app.
