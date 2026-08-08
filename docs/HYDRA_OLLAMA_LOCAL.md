# HYDRA_OLLAMA_LOCAL_001

Project Hydra local-agent milestone for Android/Termux.

## Shape

```text
Android browser / future APK WebView
        |
        | http://127.0.0.1:8787
        v
Hydra Python gateway
        |
        | http://127.0.0.1:11434/api/chat
        v
Ollama local model
```

No OpenAI key is required for this local path. The frontend contract remains replaceable so the same UI can later point at a remote TLS backend.

## One-command start

From Termux:

```bash
git clone https://github.com/eggie-admin/hydra-shell-android.git
cd hydra-shell-android
git fetch origin hydra-ollama-local-001
git checkout hydra-ollama-local-001
chmod +x tools/hydra-ollama-up.sh
./tools/hydra-ollama-up.sh
```

The helper:

1. checks Python, curl and git
2. verifies Ollama is already installed
3. creates a Python venv
4. installs Flask
5. starts `ollama serve` if needed
6. pulls the configured model if missing
7. starts Hydra on `127.0.0.1:8787`

Then open:

```text
http://127.0.0.1:8787/ui/index.html
```

## Model

Default:

```bash
HYDRA_OLLAMA_MODEL=qwen2.5:3b
```

Override before starting:

```bash
export HYDRA_OLLAMA_MODEL='your-model'
./tools/hydra-ollama-up.sh
```

## API

```text
GET  /health
GET  /v1/agents
GET  /v1/tools
POST /v1/hydra/turn
POST /v1/audio/speak
POST /v1/conversations/{id}/reset
```

Example:

```bash
curl -s \
  -H 'Content-Type: application/json' \
  -d '{"conversation_id":"professor","message":"What model are you using?","speak":false}' \
  http://127.0.0.1:8787/v1/hydra/turn
```

## Safe tool broker

The model is not allowed to execute arbitrary shell commands. Tools are hard-coded Python functions. Initial tools are:

- `get_local_time`
- `get_device_status`

The Ollama request uses native function-tool definitions with `stream: false`. Tool arguments are accepted only for registered functions. Tool results are injected back as trusted JSON rather than executing model-produced code.

## Voice

If the Termux:API app and the `termux-api` package are installed, Hydra exposes a single acoustic identity through Android system TTS using `termux-tts-speak`.

```bash
pkg install termux-api
```

The Termux:API companion app must also be installed from a compatible source. If TTS is unavailable, chat still works and `/health` reports `tts: false`.

## Security boundary

- gateway binds only to `127.0.0.1`
- Ollama is expected on `127.0.0.1:11434`
- no API key is embedded
- no arbitrary shell execution tool exists
- conversation memory is process-local and bounded
- logs are written under `$HOME/.hydra/logs`

## Stop

```bash
kill "$(cat ~/.hydra/run/hydra-gateway.pid)" 2>/dev/null || true
kill "$(cat ~/.hydra/run/ollama.pid)" 2>/dev/null || true
```

Only stop the Ollama PID if this helper started it and no other local service depends on it.
