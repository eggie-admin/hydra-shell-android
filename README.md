# LumH OS · Project Hydra

This repository's `main` branch is the canonical **LumH OS** source branch. **Project Hydra** is the project root beneath LumH OS, and Samsung Android APK is a Hydra platform.

```text
main
└── lumh-os/
    └── projects/
        └── hydra/
            ├── doctrine/
            ├── subsystems/
            │   └── kai9000/
            ├── integrations/
            │   └── hugging-face/
            └── platforms/
                └── samsung-android-apk/
```

See `lumh-os/projects/hydra/project.manifest.json` and `lumh-os/projects/hydra/doctrine/directory.doctrine.json`.

## Compatibility migration

The repo previously grew around separate implementation roots including `lumh-os/kai9000/`, `ultima/ollama-ffmpeg-antenna-v3/`, and `samsung-sm-x400/`. They remain valid implementation sources during the migration and are referenced from the new Hydra tree rather than copied.

Old paths are retired only after CI, cross-repository references, and explicit operator approval are green.

## Samsung Android platform

The Samsung operator lane uses explicit trust and capability layers instead of treating root as a default requirement.

Trusted stock/Knox path:

1. stock Samsung firmware
2. Developer Options enabled
3. USB or Wireless debugging only when needed
4. Shizuku started through ADB / Wireless debugging
5. explicit per-app Shizuku authorization
6. Termux + Termux:Widget own the localhost control plane
7. optional Termux:X11 display transport
8. optional YagniLauncher front door

Root/Sui is a separate laboratory lane and must never claim Secure Folder/Knox trust.

Canonical localhost services:

- AXS `127.0.0.1:8767`
- TigerVNC `127.0.0.1:5901`
- WebSocket bridge `127.0.0.1:6080`
- Hydra cockpit `127.0.0.1:8787`
- Ollama `127.0.0.1:11434`

The platform manifest is `lumh-os/projects/hydra/platforms/samsung-android-apk/platform.manifest.json`. The Android APK/cockpit forge is `eggie-admin/vue-headless-cms`; this repository retains compatibility references under `samsung-sm-x400/` while the migration is active.

Privileged operations remain typed and allow-listed. No automatic root, arbitrary model-authored shell execution, public service binding, or secret storage belongs in the Samsung operator lane.

## KAI 9000

KAI 9000 is Project Hydra's local-first AI/media subsystem. Its Hydra reference is:

`lumh-os/projects/hydra/subsystems/kai9000/reference.json`

Compatibility registry/runtime sources remain:

- `lumh-os/kai9000/project.manifest.json`
- `ultima/ollama-ffmpeg-antenna-v3/`

Local Ollama, FFmpeg/ffprobe, and optional ComfyUI remain the live plane; GitHub is versioned source of truth and Google Drive is the recovery/artifact mirror.

## Hugging Face

Hugging Face is registered beneath Project Hydra as a Forge/model catalog integration. It is not runtime authority, does not auto-download models, does not auto-execute repository code, and requires pinned revisions plus license records before promotion.

## Status

Compatibility-first structural migration. Existing services must degrade gracefully when optional capabilities are unavailable.

## License

GNU General Public License v3.0
