# LuHm Cathedral source layout

The live Cathedral runtime remains in the folder root for compatibility with the Godot Android donor forge. The `source/` directory adds the reproducible source contract around it without breaking the current green runtime.

## Source contract

- `source/source-manifest.json` declares runtime files, templates, language lanes, vendor profiles and source-bundle policy.
- `source/toolchain-manifest.yaml` is the human-readable pinned toolchain contract.
- `source/templates/` contains reusable LuHm-owned HTML templates.
- `config/luhm.example.yaml` is the non-secret YAML configuration template.
- `python/` is the Python 3.14 automation/service/AI-adapter lane.
- `java/` is the Java 17 Android and optional AI-adapter lane.
- `vendor/vendor-catalog.json` records optional browser-side third-party libraries and their packaging status.
- `tools/validate-source.py` rejects missing assets, unresolved enabled vendors, unsafe runtime dependencies and stale toolchain markers.
- `tools/package-source.py` builds a deterministic source archive with normalized ownership, modes and timestamps.

## Language lanes

Python is pinned to the stable CPython 3.14 line. PyYAML validates configuration, Pydantic provides strict typed models, FastAPI is available for local service endpoints, and the OpenAI and Google GenAI Python SDKs are optional extras rather than mandatory APK dependencies.

Java remains on Java 17 to match the Android forge. The Java lane records exact optional OpenAI Java and Google GenAI SDK versions plus SnakeYAML Engine for YAML 1.2 processing. Provider code is separate from Android packaging unless explicitly enabled by a later source mutation.

## AI authority boundary

AI provider clients are advisory by default. Credentials come from environment variables only. Browser secrets and direct model-to-shell execution are forbidden. Any consequential execution remains outside the provider adapter and subject to the LuHm Crown/human approval boundary.

## Vendor profiles

The default browser vendor profile is `minimal`, so unused libraries do not inflate the APK. `cockpit` and `3d` are capability profiles, not automatic dependency installs. Optional vendor bytes are packaged only after an explicit version/integrity mutation records local targets and SHA-256 values.
