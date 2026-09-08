# KAI 9000 Android official-repo mutation lane

This lane is a clean-room KAI implementation informed by Android's public reference repositories. It does not vendor their application code.

## Reference repositories

- `android/nowinandroid` — Gradle repository management, modular project organization, JDK 17 gate.
- `android/architecture-samples` — version-catalog and app architecture conventions.
- `android/platform-samples` — Android platform feature examples, especially window insets, widgets, camera, Bluetooth, storage and predictive back.
- `android/compose-samples` — UI reference only; Compose is not required by this first native KAI harness.

All four repositories are Android/Open Source Project reference material and are used as design references. Any future copied code must retain its original Apache-2.0 notice and be listed here with an exact file path and source commit.

## KAI doctrine retained

- Android 16 / SDK 36 target.
- Portrait-first phone shell.
- Ordinary owner-profile app, never an Android HOME launcher.
- `MAIN + LAUNCHER`, no `HOME` category.
- System status/navigation bars retained.
- Loopback-only cockpit navigation in the native WebView.
- Termux remains the daemon/control-plane owner.
- Godot remains the canonical runtime lane; this native project is a development/reference lane until explicitly promoted.
- No secrets, keystores, API keys, Node runtime or package manager inside the APK.

## Why this exists

The previous Godot export exposed how a single Android export option could accidentally add `android.intent.category.HOME`. This lane makes the Android package contract visible in a normal Android Studio/Gradle project so package identity, launcher behavior, orientation, network policy and SDK levels can be audited directly before those rules are mirrored back into the Godot export pipeline.
