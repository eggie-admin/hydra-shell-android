# KAI 9000 runtime mutations

## 1 — Google Drive artifact mirror

The runtime uses `rclone copyto` through `drive_backup.py`.

Why `copyto` instead of destructive sync:
- no remote deletion semantics;
- each output is copied to an explicit destination;
- SHA-256 remains in `OUTPUT_SEAL.json`;
- rclone credentials/config stay outside Git and outside the project tree.

Configure on the host, then set:

```text
RCLONE_REMOTE=drive:
RCLONE_DEST=PRIVATE - Eggie Lum Forge/20_PROJECTS/KAI9000_ULTIMA_OLLAMA_FFMPEG_ANTENNA_V3
```

## 2 — FOSS AI guided batch image regeneration

Adapter target: ComfyUI native HTTP API on loopback by default.

Export a ComfyUI workflow in API format and POST it to `/api/comfy/configure`. Supported neighboring frame roles are `current`, `previous`, and `next`. Generated frames are written back to `frames_ai` with the exact original filename so FFmpeg remux remains deterministic.

## 3 — Seal + preview + backup

- `/api/apng` creates source/AI APNG previews.
- `/api/remux` makes H.264 24 fps MP4.
- `/api/seal` writes `OUTPUT_SEAL.json` with byte sizes + SHA-256.
- `/api/backup` copies sealed artifacts to Drive.
- `/preview` is the local in-app preview UI.

The source MP4 is not mirrored by default. Set `include_source_mp4=true` only when explicitly needed.

## Local antenna

- `/api/antenna/status` probes Ollama, FFmpeg, and ffprobe.
- `/api/antenna/ollama/chat` talks only to the configured local Ollama endpoint by default.

GitHub remains source control, not a remote command shell.
