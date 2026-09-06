# Hydra Shell Android

A Knox-aware Android shell, terminal interface, and runtime probe for Project Hydra.

## Initial milestone

HYDRA_SHELL_KNOX_PROBE_001

- Detect the Android user/profile ID
- Display the private application data path
- Test private file creation
- Test executable/runtime capabilities
- Capture stdout and stderr
- Export a diagnostic report

## Samsung SM-X400 full mutation

The Samsung operator lane is now split into explicit trust and capability layers instead of treating root as a default requirement.

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

The authoritative service supervisor is `tools/hydra_widget_setup.py`. The multi-repository source of truth is `eggie-admin/vue-headless-cms` on branch `samsung-sm-x400-build-candidate`, file `samsung-sm-x400/samsung-dev-stack.manifest.json`. This repo keeps a compact pointer at `samsung-sm-x400/full-stack.reference.json`.

Privileged operations must remain typed and allow-listed. No automatic root, arbitrary model-authored shell execution, public service binding, or secret storage belongs in the Samsung operator lane.

## LumH OS : KAI 9000

KAI 9000 is registered as a local-first AI/media subsystem under `lumh-os/kai9000/`.

Canonical implementation:

`ultima/ollama-ffmpeg-antenna-v3/`

The integration uses a reference manifest rather than duplicating runtime code. Local Ollama, FFmpeg/ffprobe, and optional ComfyUI remain the live plane; GitHub is the versioned source of truth and Google Drive is the recovery/artifact mirror.

See:

- `lumh-os/kai9000/project.manifest.json`
- `lumh-os/kai9000/README.md`
- `ultima/ollama-ffmpeg-antenna-v3/README.md`

## Status

Early development. No bundled Linux distribution. KAI 9000 services are integrated as optional local-first subsystems and must degrade gracefully when unavailable.

## License

GNU General Public License v3.0
