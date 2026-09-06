# Video Forge Cathedral Android/F-Droid Architecture

## Rule zero

Node/npm is a build-time tool only. The Android APK must not embed a Node runtime, npm, a package manager, shell package installation, or writable self-updating executable code.

## Layers

1. **Python 3 control plane** — `tools/cathedral.py` owns deterministic orchestration and validation.
2. **npm/Vue build plane** — a pinned `vue-headless-cms` checkout is installed with `npm ci` and compiled with Vite.
3. **Static payload** — generated `dist/` assets are copied into `godot/web/` for encapsulation by the app shell.
4. **Godot Android shell** — Godot owns UI/native runtime and Android export. Use Gradle build templates when AAB/custom Android project behavior is required.
5. **Distribution lanes** — build separate artifacts/configurations for F-Droid and commercial stores. Never make the F-Droid variant depend on proprietary SDKs, Google Play Services, Firebase, proprietary analytics, or secret API keys.

## Reproducibility gates

- Commit `package-lock.json` for each npm project and use `npm ci`, never floating `npm install`, in CI.
- Pin Node/npm, Python, JDK, Godot, Android SDK/Build Tools/NDK, Gradle/AGP as applicable.
- Build from a clean checkout.
- Do not commit keystores, deploy tokens, `.env`, generated credentials, or signing passwords.
- Treat every native `.so` as part of the 16 KB page-size compatibility gate.
- Produce unsigned or CI-signed artifacts according to the release lane; F-Droid upstream/source builds must remain fully buildable from source.

## Release lanes

### F-Droid

FLOSS-only dependencies and source. Prefer a reproducible APK. No Play-only SDK requirements. Metadata lives separately from secrets. Build server must be able to reproduce the release from source.

### Google Play

Use Godot Gradle Android export and release signing; produce AAB for Play distribution. Keep Play-specific dependencies behind a separate flavor/build lane so the F-Droid source lane stays clean.

### Samsung / sideload

APK may be produced from the same Godot project using a separate release preset/signing lane.

## Wizard contract

```text
npm run wizard
  -> python3 tools/cathedral.py wizard
  -> doctor
  -> npm ci --ignore-scripts in pinned CMS checkout
  -> npm run build
  -> copy dist/ -> godot/web/
  -> F-Droid source gate
  -> Godot/Gradle Android build in CI
```

The wizard prepares the source tree. It does not install software on the user's Android device and it does not bypass Android package installation/security policy.
