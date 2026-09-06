# Project Hydra

Canonical project namespace inside the LumH OS `main` branch.

```text
main (LumH OS)
└── project/
    └── hydra/
        ├── doctrine/
        ├── runtime/
        ├── forge/
        └── samsung/
            └── android/
                └── apk/
```

## Doctrine

- `project/hydra` is singular and canonical.
- Existing roots such as `lumh-os/kai9000`, `ultima/ollama-ffmpeg-antenna-v3`, and `samsung-sm-x400` remain compatibility sources during migration.
- Integration is `reference_not_copy`; do not duplicate the KAI runtime or Android APK source tree.
- Runtime remains local-first and loopback-first.
- Hugging Face remains the Forge/model catalog, not runtime authority.
- Android APK completion requires an actual installable APK plus package/build evidence.
- No secrets belong in Git, manifests, Base64 envelopes, or Drive recovery metadata.

See `project.manifest.json` and `doctrine/directory-structure.json`.
