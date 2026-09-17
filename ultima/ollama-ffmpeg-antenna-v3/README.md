# KAI9000 Ultima Ollama + FFmpeg Antenna V3.1

Canonical split:

- jQuery cockpit: browser UI only; no credentials, filesystem authority, or approval authority.
- Python 3/FastAPI magic kernel: coding policy, OpenAI transport, typed spells, checkpoints, approvals, and rollback.
- Local live plane: Ollama on `127.0.0.1:11434`, FFmpeg/ffprobe local binaries, optional ComfyUI on `127.0.0.1:8188`.
- KAI antenna service: FastAPI on `127.0.0.1:8797`.
- GitHub remote plane: versioned readable source and fast-forward-only update metadata.
- Google Drive recovery plane: sealed manifests, hashes, and approved media artifacts.

Edge Gallery remains a Samsung-facing local UI/media surface. The antenna does not assume Google AI Edge Gallery exports an on-device HTTP API, and it does not scrape private app storage.

GitHub is not the AI runtime. Drive is not the execution plane. Local Ollama and FFmpeg stay the live services. OpenAI is a remote coding planner and does not receive shell authority.

## Install

```bash
python3 -m venv .venv
. .venv/bin/activate
npm run bootstrap
npm run doctor
npm run antenna:status
npm start
```

`npm run bootstrap` installs the Python package with pip, performs locked `npm ci`, and vendors jQuery 3.7.1 into `static/vendor/jquery.min.js`. The running application remains Python 3/FastAPI; Node/npm are build/front-door tooling only.

Preview:

```text
http://127.0.0.1:8797/preview
```

## OpenAI coding chat

Set `OPENAI_API_KEY` only in the server environment. Never place it in HTML, JavaScript, APK assets, Git, logs, or Drive manifests.

Optional model override:

```bash
export OPENAI_MODEL="gpt-5.6"
```

If `OPENAI_API_KEY` is absent, `/api/magic/chat` returns deterministic mock guidance so the cockpit remains testable without credentials.

## Hardened spell kernel

The browser can request casts, but Python owns the policy.

| Spell | Rank | Purpose | Approval |
|---|---:|---|---|
| `INSPECT` | 0 | list allow-listed source files | automatic |
| `READ_FILE` | 0 | bounded repository-relative read + SHA256 | automatic |
| `SEARCH_TEXT` | 0 | bounded source search | automatic |
| `PYTHON_CHECK` | 1 | `python3 -m py_compile` on one allow-listed `.py` file | automatic |
| `GIT_DIFF` | 1 | fixed `git diff --` invocation | automatic |
| `WRITE_FILE` | 2 | checkpointed optimistic-SHA write | human approval |
| `ULTIMA` | 4 | irreversible/publish class | disabled in-app |

Security properties:

- no arbitrary shell command endpoint;
- no absolute paths or path traversal;
- symlink scans are skipped;
- secret-shaped outbound chat and write content are rejected;
- writes are limited to allow-listed text/code suffixes and 256 KiB;
- existing-file writes require the exact prior SHA256;
- every accepted write creates a rollback checkpoint;
- approval casts expire after 180 seconds;
- `ULTIMA` cannot be self-enabled by the model or browser UI.

## Runtime endpoints

Media/local AI:

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

Coding cockpit:

- `GET /api/magic/spells`
- `POST /api/magic/chat`
- `POST /api/magic/cast/prepare`
- `POST /api/magic/cast/{cast_id}/approve`
- `POST /api/magic/cast/{cast_id}/execute`
- `POST /api/magic/cast/{cast_id}/rollback`

## Canonical remote branch

`main`

```bash
git fetch --prune origin main
git pull --ff-only origin main
```

Do not force-reset local work and do not commit secrets.

## Local antenna

The antenna probes local Ollama, FFmpeg, and ffprobe, and can send chat requests only to the configured local Ollama endpoint by default.

That Ollama compatibility facade is loopback-only and fail-closed: non-loopback endpoints are rejected instead of silently falling back to another model host.

Default model: `qwen2.5:3b`.

Future native LiteRT-LM or optional llama.cpp integration remains a separate explicit architecture change; this runtime does not enable either backend by default.

## Media lane

`MP4 → 24fps PNG → APNG preview → optional ComfyUI guided regeneration → H.264 MP4 → SHA-256 seal → Drive backup`

Drive backup uses `rclone copyto` and does not use destructive sync semantics.
