# Samsung SM-X400 Shizuku integration rules

Apply these rules to work under `samsung-sm-x400/frontend/widget/**` and `tools/sm_x400_shizuku_sanity.py`.

- Keep Shizuku optional and external to the APK dependency graph.
- For the stock Knox/Secure Folder development target, prefer Shizuku via ADB or Android wireless debugging.
- Do not enable root or Sui in the trusted Secure Folder lane.
- Root/Sui belongs only to an explicitly separate laboratory target and must not claim Secure Folder or Knox trust.
- Keep privileged actions typed and allow-listed. Never execute arbitrary model-authored shell commands.
- Preserve the existing Termux:Widget state contract, localhost service bindings, and owned-PID shutdown behavior.
- Missing Shizuku, AXS, VNC, websockify, Ollama, or Termux:API must degrade capability instead of making the ordinary Android build fail.
- Do not introduce HiddenApiBypass by default.
- Preserve provenance back to `eggie-admin/vue-headless-cms` branch `samsung-sm-x400-build-candidate` head `215310cff47d65311d6e7ff60eb63d6f176a444b`.
- Do not claim device validation, Secure Folder runtime success, root success, or CI success without evidence.
