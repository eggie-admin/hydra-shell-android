# Hydra Shell Android

Project Hydra Android-side development repository.

## Current KAI 9000 integration

The canonical KAI 9000/LumH OS integration lives under:

- `lumh-os/kai9000/`
- `ultima/ollama-ffmpeg-antenna-v3/`

GitHub is the versioned source of truth; Google Drive is used as a sealed recovery/artifact mirror. The runtime remains local-first with Ollama and media services bound to loopback.

## Plugin Autopilot

This repository also contains a skills-only ChatGPT/Codex Plugin at `.codex-plugin/plugin.json` and the Android widget workflow under `skills/android-widget-autopilot/`.

## Safety boundaries

- No secrets or model weights in source or APK assets.
- No public Ollama exposure.
- No GitHub remote-shell behavior.
- Prefer feature branches and validation before merge.
