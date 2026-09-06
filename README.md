# LumH OS · Project Hydra

This repository's `main` branch **is LumH OS**. Project Hydra is the canonical project namespace beneath the branch root.

```text
main = LumH OS
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

Canonical manifests:

- `project/hydra/project.manifest.json`
- `project/hydra/doctrine/directory-structure.json`
- `project/hydra/runtime/kai9000.reference.json`
- `project/hydra/forge/hugging-face/reference.json`
- `project/hydra/samsung/android/apk/app.reference.json`

## Directory doctrine

Project Hydra uses a singular `project/` namespace. Runtime, forge integrations, and platform references live beneath `project/hydra/`. Implementations are referenced, not copied.

Compatibility implementation roots remain during migration:

- `lumh-os/kai9000/`
- `ultima/ollama-ffmpeg-antenna-v3/`
- `samsung-sm-x400/`

Those paths are not competing project roots. They remain implementation sources until CI is green and the legacy-prune gate is explicitly approved.

## Samsung Android APK

The Samsung APK/cockpit surface is registered at:

`project/hydra/samsung/android/apk/app.reference.json`

The forge source remains `eggie-admin/vue-headless-cms`, referenced rather than duplicated. APK milestones are not GREEN until an installable APK and package identity evidence exist.

Samsung local services remain loopback-first. Automatic root, arbitrary model-authored shell execution, public Ollama exposure, and secrets embedded in the APK/repository are forbidden.

## KAI 9000 runtime

KAI 9000 is Project Hydra's local-first AI/media runtime reference:

`project/hydra/runtime/kai9000.reference.json`

The live implementation remains `ultima/ollama-ffmpeg-antenna-v3/`, with local Ollama, FFmpeg/ffprobe, optional ComfyUI, and the KAI antenna. GitHub is source control; Google Drive is recovery/artifact mirror.

## Hugging Face Forge

Hugging Face is registered at `project/hydra/forge/hugging-face/reference.json` as Forge/model catalog only. It has no runtime authority, no automatic downloads, no automatic remote-code execution, and promoted models require pinned revisions plus license records.

## Status

Compatibility-first structural migration. Project Hydra is the canonical project root; legacy implementation roots remain until their retirement gate is satisfied.

## License

GNU General Public License v3.0
