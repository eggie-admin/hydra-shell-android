# LuHm Cathedral vendor boundary

This directory is a catalog and integrity gate for third-party code. It is not a dumping ground for downloaded SDKs or generated build output.

Rules:

1. Runtime CDN loading is forbidden. Production/candidate APKs must use packaged local bytes.
2. A catalog entry may stay optional with `enabled: false` and no SHA-256. In that state no vendor bytes are packaged.
3. Before a vendor becomes enabled, mirror the exact release into its `local_target`, record a 64-hex SHA-256, preserve its license notice, and run `python3 tools/validate-source.py .`.
4. Only enabled vendors belong in the runtime package. Large optional engines remain outside the APK until a feature actually uses them.
5. Version changes are source mutations. Update the catalog, integrity value, tests and build receipt together.

Current catalog intent:

- jQuery 4.0.0: optional cockpit DOM/event compatibility layer.
- jQuery UI 1.14.2: optional draggable/resizable widget layer; depends on jQuery.
- Babylon.js ES6 Core 9.26.1: optional 3D scene lane. Use a local ES-module bundle, not the Babylon learning CDN.

`vendor/dist/` and `vendor/cache/` are deliberately excluded from the deterministic source bundle until their bytes are explicitly approved and hash-locked.
