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
