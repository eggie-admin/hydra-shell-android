# KAI9000 Ultima Ollama + FFmpeg Antenna V3

Canonical split:

- Local live plane: Ollama on `127.0.0.1:11434`, FFmpeg/ffprobe local binaries, optional ComfyUI on `127.0.0.1:8188`.
- GitHub remote plane: versioned readable antenna source and fast-forward-only update metadata.
- Google Drive recovery plane: sealed ZIP, manifest, SHA-256 ledger, and approved media artifacts.

GitHub is not the AI runtime. Drive is not the execution plane. Local Ollama and FFmpeg stay the live services.

## Remote branch

`feature/ultima-ollama-ffmpeg-antenna-v3`

## Update rule

```bash
git fetch --prune origin feature/ultima-ollama-ffmpeg-antenna-v3
git pull --ff-only origin feature/ultima-ollama-ffmpeg-antenna-v3
```

Do not force-reset local work and do not commit secrets.

## Local antenna

The antenna probes local Ollama, FFmpeg, and ffprobe, and can send chat requests only to the configured local Ollama endpoint.

Default model: `qwen2.5:3b`.
