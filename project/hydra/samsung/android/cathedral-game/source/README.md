# LuHm Cathedral source layout

The live Cathedral runtime remains in the folder root for compatibility with the Godot Android donor forge. The `source/` directory adds the reproducible source contract around it without breaking the current green runtime.

- `source/source-manifest.json` declares runtime files, templates, vendor profiles and source-bundle policy.
- `source/templates/` contains reusable LuHm-owned HTML templates.
- `vendor/vendor-catalog.json` records optional third-party libraries and their packaging status.
- `tools/validate-source.py` rejects missing assets, unresolved enabled vendors and external runtime script/style dependencies.
- `tools/package-source.py` builds a deterministic source archive with normalized ownership, modes and timestamps.

The default vendor profile is `minimal`, so unused libraries do not inflate the APK. `cockpit` and `3d` are capability profiles, not automatic dependency installs.
