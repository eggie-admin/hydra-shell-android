# LUHMOS_S24FE_STANDALONE_APK_GOAL_20260910

**Seal date:** 2026-09-10 America/Detroit  
**Repository:** `eggie-admin/hydra-shell-android`  
**Canonical integration branch:** `luhmos-main`  
**Seal work branch:** `luhmos/standalone-apk-seal-20260910`  
**Pre-seal source baseline:** `c70de68a02136b3ea6a25c791f8744321d792f24`  
**State:** SEALED GOAL / implementation YELLOW  
**Next GREEN milestone:** `LUHMOS_S24FE_STANDALONE_APK_GREEN`

## Goal

LuHm OS must become a proper Android application for the Samsung Galaxy S24 FE target (`SM-S721U1`, Android 16):

```text
APK -> Android package installer -> Install -> launcher icon -> Open
```

Core application launch and ordinary operation must not require a development helper application or a separately launched terminal/control-plane process.

## Canonical Android identity

```text
application ID: art.eggiebagelface.luhmos
release alias:  luhmos-release
target SDK:     API 36
primary ABI:    arm64-v8a
device:         Samsung SM-S721U1 / Galaxy S24 FE
Android:        16
```

## Production runtime exclusions

The following are retired from the production Android dependency graph:

- Termux;
- Termux:API / Termux:Widget;
- Acode;
- AcodeX / AXS;
- TigerVNC;
- websockify / desktop WebSocket bridge;
- Samsung Secure Folder as a required cockpit/runtime boundary;
- an external localhost daemon required for application startup;
- root or Shizuku as an ordinary-runtime requirement.

Historical records may remain for provenance and migration analysis. They are not current architecture requirements.

## Canonical application shape

- Godot 4 owns the Android application shell/runtime.
- Vue/WebView cockpit assets are bundled in the application artifact.
- Kotlin/native Android code is a bounded platform bridge.
- Node/npm remains build-time only.
- Python 3 remains the reference policy/control implementation, but Android production behavior must be packaged within the APK boundary or migrated to APK-safe components. An externally installed Python runtime is not required.
- AI/media providers may be optional integrations. Their absence must not prevent base application launch.

## Proven evidence already retained

The LuHm-native Android identity forge has machine GREEN evidence from the ULTIMA lane recorded by the repository promotion history, including PR #30 / PR #31 and workflow evidence for:

- package `art.eggiebagelface.luhmos`;
- LuHm OS 1.0.0 / version code 100 identity gate;
- target SDK 36;
- `arm64-v8a`;
- 16 KiB alignment gate;
- successful Godot Android export;
- F-Droid binary staging gate;
- final ULTIMA compile gate.

This proves the canonical compile/identity forge. It does **not** by itself prove the new standalone physical-device milestone.

## Required evidence for `LUHMOS_S24FE_STANDALONE_APK_GREEN`

1. CI builds the canonical `art.eggiebagelface.luhmos` APK from the sealed source lineage.
2. APK signature verifies against the expected persistent release identity, not an ephemeral debug signer.
3. Artifact SHA-256 and provenance are recorded.
4. `arm64-v8a` and 16 KiB compatibility gates pass.
5. APK clean-installs on Samsung SM-S721U1 through normal Android package installation.
6. LuHm OS launches from its Android launcher icon after install.
7. Launch succeeds with Termux, Acode/AcodeX, VNC/websockify, and Secure Folder absent or stopped.
8. Core UI initializes without requiring an external localhost daemon.
9. A second release signed by the same key installs as an update over the first and preserves expected application continuity.
10. No signing secrets, private API credentials, or other secret material are present in Git or packaged assets.

Until all required evidence exists, the standalone APK milestone remains YELLOW even when compilation is GREEN.

## Source-of-Truth files updated by this seal

- `README.md`
- `ARCHITECTURE.md`
- `docs/LUHMOS_CANONICAL_DOCTRINE.md`
- `project/hydra/project.manifest.json`
- `project/hydra/samsung/android/apk/app.reference.json`
- this sealed milestone record

## Known migration note

`project/hydra/samsung/android/apk/testing-ingest.manifest.json` and older Samsung/Termux/AcodeX documentation may describe superseded development architecture. They remain historical evidence unless separately retired. Current authority is the canonical doctrine plus `app.reference.json` and this seal.

## Rollback anchor

If this doctrine mutation must be reverted, the pre-seal integration baseline is:

`c70de68a02136b3ea6a25c791f8744321d792f24`

Rollback does not erase this milestone record or historical evidence.

## Seal statement

**LuHm OS Android success is defined as a proper installable, launchable, updateable Samsung APK, not a terminal-hosted development stack.**

The forge may be GREEN while the standalone device gate remains YELLOW. Promotion to `LUHMOS_S24FE_STANDALONE_APK_GREEN` requires physical-device install, launch, persistent-signing, and update proof.
