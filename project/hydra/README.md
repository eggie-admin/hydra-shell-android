# Project Hydra

Canonical LuHm OS project namespace on the `luhmos-main` integration branch.

```text
LuHm OS (`luhmos-main`)
└── project/
    └── hydra/
        ├── doctrine/
        ├── runtime/
        ├── forge/
        ├── openai/
        ├── ubuntu-debian/
        ├── source-of-truth/
        ├── inbox-unsorted/
        └── samsung/
            └── android/
                └── apk/
```

## Doctrine

- `project/hydra` is singular and canonical.
- `LuHm OS` is the canonical product spelling. `LumH OS` is stale.
- `luhmos-main` is the canonical integration branch. Repository default branch `main` is not integration authority.
- Existing roots such as `lumh-os/kai9000`, `ultima/ollama-ffmpeg-antenna-v3`, root `integrations/`, and `samsung-sm-x400` are compatibility/implementation sources during migration.
- Integration is `reference_not_copy`; do not duplicate runtime or Android APK source trees merely to satisfy directory aesthetics.
- `project/hydra/openai` is the canonical OpenAI/Lum project index. Root `integrations/openai` remains the implementation adapter path until a tested relocation is explicitly promoted.
- Canonical filesystem provider slugs: `openai`, `huggingface`, `google-cloud`, `cloudflare`.
- Canonical provider IDs in machine events: `openai`, `huggingface`, `google_cloud`, `cloudflare`.
- Primary saved/custom Lum agent identity: `KAI9000-Lum`. Historical names such as `KAI9000-Lum-InApp` remain compatibility/history only.
- Runtime remains local-first and loopback-first where a local service exists, but the production Android APK must not require Termux, Acode/AcodeX, VNC, Secure Folder, or another development daemon to launch.
- OpenAI/Hugging Face/Google/Cloudflare remain provider adapters, not policy, signing, build, release, root, or Crown authority.
- Android APK completion requires an actual installable APK plus package, signer, ABI/alignment, provenance, and physical-device evidence.
- No secrets belong in Git, manifests, Base64 envelopes, Drive recovery metadata, prompts, screenshots, WebView assets, or APK resources.

See `project/hydra/doctrine/directory-structure.json`, `lumh-os/kai9000/project.manifest.json`, `docs/API_TRINITY_DOCTRINE.md`, and the current sealed private Crown source of truth.
