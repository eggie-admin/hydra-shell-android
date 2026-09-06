# KAI9000 Ultima Ollama + FFmpeg Antenna V3

Canonical split:

- Local live plane: Ollama on `127.0.0.1:11434`, FFmpeg/ffprobe local binaries, optional ComfyUI on `127.0.0.1:8188`.
- KAI antenna service: FastAPI on `127.0.0.1:8797`.
- GitHub remote plane: versioned readable source and fast-forward-only update metadata.
- Google Drive recovery plane: sealed manifests, hashes, and approved media artifacts.

GitHub is not the AI runtime. Drive is not the execution plane. Local Ollama and FFmpeg stay the live services.

## Install

```bash
python3 -m venv .venv
. .venv/bin/activate
npm run bootstrap
npm run doctor
npm run antenna:status
npm start
```

Preview:

```text
http://127.0.0.1:8797/preview
```

## Runtime endpoints

- `GET /health`
- `GET /api/antenna/status`
- `POST /api/antenna/ollama/chat`
- `POST /api/demux`
- `POST /api/apng`
- `POST /api/comfy/configure`
- `POST /api/comfy/regen`
- `POST /api/remux`
- `POST /api/seal`
- `POST /api/backup`
- `GET /api/jobs`

## Canonical remote branch

`main`

```bash
git fetch --prune origin main
git pull --ff-only origin main
```

Do not force-reset local work and do not commit secrets.

## Local antenna

The antenna probes local Ollama, FFmpeg, and ffprobe, and can send chat requests only to the configured local Ollama endpoint by default.

Default model: `qwen2.5:3b`.

## Media lane

`MP4 → 24fps PNG → APNG preview → optional ComfyUI guided regeneration → H.264 MP4 → SHA-256 seal → Drive backup`

Drive backup uses `rclone copyto` and does not use destructive sync semantics.
