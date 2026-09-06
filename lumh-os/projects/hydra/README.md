# Project Hydra

Project Hydra is the canonical project root inside LumH OS.

```text
lumh-os/projects/hydra/
├── doctrine/
│   └── directory.doctrine.json
├── subsystems/
│   └── kai9000/
│       └── reference.json
├── integrations/
│   └── hugging-face/
│       └── reference.json
└── platforms/
    └── samsung-android-apk/
        └── platform.manifest.json
```

## Doctrine

- Project code is grouped by project first, then by platform/subsystem/integration.
- Samsung Android APK belongs under `platforms/`.
- KAI 9000 belongs under `subsystems/`.
- Hugging Face belongs under `integrations/` as a Forge/model catalog.
- Existing implementation paths remain compatibility sources during migration.
- No implementation is duplicated merely to satisfy directory aesthetics.
- Old paths are retired only after CI, cross-repo references, and operator approval are green.
