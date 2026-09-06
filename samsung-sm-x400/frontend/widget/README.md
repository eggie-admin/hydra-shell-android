# Samsung SM-X400 / Android Dev / Widget

This branch is the Android-development fork of the Samsung SM-X400 widget + Shizuku lane from `eggie-admin/vue-headless-cms`.

## Provenance

- Cathedral source branch: `samsung-sm-x400-build-candidate`
- Cathedral source head: `215310cff47d65311d6e7ff60eb63d6f176a444b`
- Hydra supervisor merge baseline: `0f7a58a52a832a2eb04c24f45fde6ded4974ec43`
- Authoritative supervisor in this repo: `tools/hydra_widget_setup.py`

This fork deliberately does **not** duplicate the supervisor under this directory. The existing Hydra Android supervisor remains the code source of truth.

## Trust lanes

### Knox / Secure Folder development

Preferred capability path:

1. stock Samsung firmware
2. Developer Options enabled
3. USB or Wireless debugging enabled by the operator
4. Shizuku started through ADB / wireless debugging
5. explicit per-app Shizuku authorization

Root and Sui are not part of the trusted Secure Folder lane.

### Rooted laboratory target

Root / Sui may be used only as an explicitly separate laboratory mode. It must not claim Secure Folder or Knox trust.

## Widget runtime

Required:

- Termux
- Termux:Widget
- Python 3

Optional capabilities:

- Termux:API
- Shizuku
- AXS on `127.0.0.1:8767`
- TigerVNC on `127.0.0.1:5901`
- websockify on `127.0.0.1:6080`
- Hydra cockpit on `127.0.0.1:8787`
- local Ollama on `127.0.0.1:11434`

Missing optional capabilities are capability downgrades, not build failures.

## Safety contract

- localhost first
- no arbitrary model-authored shell execution
- typed and allow-listed privileged actions only
- stop only owned processes
- do not trust stale PIDs
- no secrets in source, logs, manifests, or APK assets
- Shizuku remains optional and external to the APK dependency graph
