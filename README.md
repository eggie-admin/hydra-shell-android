# LumH OS · Project Hydra

This repository's `main` branch is the canonical **LumH OS** source branch. **Project Hydra** lives beneath it at one singular project root, and Samsung Android APK is a Hydra platform.

```text
main (LumH OS)
└── project/
    └── hydra/
        ├── doctrine/
        ├── runtime/
        │   └── kai9000.reference.json
        ├── forge/
        │   └── hugging-face/
        └── samsung/
            └── android/
                └── apk/
                    └── app.reference.json
```

Canonical manifest: `project/hydra/project.manifest.json`  
Directory doctrine: `project/hydra/doctrine/directory-structure.json`

## Compatibility migration

The repository previously grew around implementation roots including `lumh-os/kai9000/`, `ultima/ollama-ffmpeg-antenna-v3/`, and `samsung-sm-x400/`. They remain valid compatibility sources during migration and are **referenced, not copied**, from `project/hydra`.

The obsolete plural tree `lumh-os/projects/hydra` is not canonical and must not be recreated. Legacy paths may be retired only after CI is green and an explicit migration approves the removal.

## Samsung Android APK

The canonical Hydra platform reference is:

`project/hydra/samsung/android/apk/app.reference.json`

The actual APK/cockpit source remains in `eggie-admin/vue-headless-cms` on the pinned `samsung-sm-x400-build-candidate` lane. Android GREEN requires an installable APK plus package/build evidence. The local operator lane remains loopback-first, no automatic root, no arbitrary model-authored shell, and no secrets in the APK or repository.

## KAI 9000 runtime

Hydra references KAI through:

`project/hydra/runtime/kai9000.reference.json`

Canonical implementation remains:

`ultima/ollama-ffmpeg-antenna-v3/`

Local Ollama, FFmpeg/ffprobe, and optional ComfyUI remain the live plane. GitHub is versioned source of truth and Google Drive is the recovery/artifact mirror.

## Hugging Face Forge

Hydra references the Hugging Face doctrine through:

`project/hydra/forge/hugging-face/reference.json`

Hugging Face is the Forge/model catalog, not runtime authority. No automatic model download or repository-code execution; promoted models require pinned revisions and license/attribution records.

## Samsung operator trust lane

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

## Status

Compatibility-first structural migration. Existing services must degrade gracefully when optional capabilities are unavailable.

## License

GNU General Public License v3.0
