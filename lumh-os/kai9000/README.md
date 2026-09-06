# LumH OS : KAI 9000 Integration

This directory registers the KAI 9000 runtime as a subsystem of the Samsung development repository without duplicating its implementation.

## Canonical source

`ultima/ollama-ffmpeg-antenna-v3/`

That subsystem owns the local AI/video runtime contract:

- Ollama on loopback as the local AI boss.
- FFmpeg and ffprobe as local media workers.
- Optional ComfyUI on loopback for guided frame regeneration.
- Python 3 as the orchestration layer.
- npm only as a command front door.
- Google Drive as a recovery/artifact mirror.
- GitHub as the readable versioned source of truth.

## LumH OS ingestion rule

LumH OS should ingest the KAI 9000 manifest by reference instead of copying code into a second tree. This keeps one implementation, one update path, and one rollback boundary.

Runtime discovery order:

1. Read `lumh-os/kai9000/project.manifest.json`.
2. Resolve `source_path` to `ultima/ollama-ffmpeg-antenna-v3/`.
3. Read the subsystem manifest there.
4. Probe local Ollama, FFmpeg/ffprobe, and optional ComfyUI.
5. Degrade gracefully when any optional service is unavailable.
6. Never pull secrets from GitHub or Google Drive.

## Mutation doctrine

Mutations belong on feature branches first. Merge to `main` only after the diff is additive or explicitly reviewed.

Do not turn GitHub into a remote shell. Do not expose Ollama directly to the public Internet. Do not couple Android boot to remote availability.

## Authority

Professor = final authority.

KAI 9000 remains local-first and usable even when GitHub, Drive, or the Ubuntu worker is offline.
