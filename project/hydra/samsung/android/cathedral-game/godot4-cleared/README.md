# LuHm OS Godot4 Cleared Asset Lane

Seal: `KAI9000_GODOT4_CLEARED_PROMOTION_20260916`

This directory is the only Godot4 asset payload promoted into the LuHm OS 1.0.3 Samsung APK candidate from the 2026-09-16 asset pass.

## What is promoted

- A LuHm-authored secondary-motion runtime profile targeting Godot 4.7.2 and the engine-native `SpringBoneSimulator3D` baseline.
- A provenance manifest recording the reviewed community references and the exact reasons they are not bundled as runtime code in this candidate.
- Community source receipts as documentation only.

## What is deliberately not promoted

The multipart `Archive.z01..z05 + Archive.zip` payload passed CRC/integrity testing but remains mixed-provenance. It contains secret-like files, private/reference media, third-party binary material, unknown media, and project-generated candidates without per-file redistribution receipts. None of that raw multipart payload is copied into this APK candidate.

The curated community ZIP also contains selected MIT reference/plugin snippets. They remain reference material in Drive for now. This APK uses the Godot engine-native secondary-motion baseline instead of activating incomplete third-party plugin snapshots.

## Release law

Only `KAI_OWNED`, `ORIGINAL`, or explicitly `RIGHTS_CLEARED` material may enter the shippable Samsung APK path. Android package-installer confirmation remains mandatory. No silent install, root, or arbitrary shell bridge is introduced here.
