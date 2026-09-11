# Android lane

Status: ACTIVE IMPLEMENTATION

Reference device family: Samsung Android 16 / arm64-v8a, including SM-S721U1.

Canonical application ID: `art.eggiebagelface.luhmos`.

Current implementation remains under the existing Project Hydra / Samsung Android source tree and pinned Godot/UI donor workflow. This directory is the platform boundary marker, not a duplicate source tree.

Release gates:
- target SDK/API 36
- arm64-v8a
- 16 KB page-size/alignment verification
- Godot/Gradle export
- persistent release signing before beta/stable
- APK for testing/F-Droid-style lanes where appropriate
- AAB for Google Play release lane
- Secure Folder is protected cockpit/client
- ordinary Termux owns daemon/control-plane processes

Do not duplicate the existing Android implementation here until a deliberate migration PR moves source paths with CI green.
