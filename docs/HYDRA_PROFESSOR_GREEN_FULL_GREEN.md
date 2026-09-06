# HYDRA_PROFESSOR_GREEN_FULL_GREEN_001

This milestone turns the outside-Secure-Folder Termux environment into a single localhost Android AI workstation for Project Hydra.

## Service map

| Service | Local endpoint | Purpose |
|---|---:|---|
| AcodeX / AXS | `127.0.0.1:8767` | AcodeX terminal backend |
| Hydra | `127.0.0.1:8787` | Lum UI + agent API |
| TigerVNC | `127.0.0.1:5901` / display `:1` | local graphical desktop |
| Ollama | `127.0.0.1:11434` | local model runtime |

The Android browser/AcodeX frontend does not need an OpenAI API key for this local path.

## AcodeX integration

AXS is considered GREEN when `127.0.0.1:8767` accepts a TCP connection. The Hydra backend also probes the AXS HTTP root and reports its status at:

```text
GET http://127.0.0.1:8787/v1/system/status
```

Configure the AcodeX terminal connection for:

```text
host: 127.0.0.1
port: 8767
```

Do not launch a second `axs` process when 8767 is already occupied by a working server. The full-green launcher preserves an existing AXS instance.

## Model modes

Hydra exposes two local modes behind the same Lum persona:

```text
FAST / CHAT   qwen3:0.6b
DEEP / BUILD  qwen2.5:3b
```

The frontend selects the mode, but the user-facing personality and canonical voice stay the same. Qwen3 runs with thinking disabled in this mobile latency path.

## One-command activation

From Termux outside Samsung Secure Folder:

```bash
cd ~/hydra-shell-android
git fetch origin hydra-ollama-local-001
git switch hydra-ollama-local-001
git pull --ff-only origin hydra-ollama-local-001
chmod +x tools/hydra-ollama-up.sh tools/hydra-full-green.sh
./tools/hydra-full-green.sh
```

The launcher:

1. preserves an existing AXS server on 8767 or starts one when available;
2. preserves a live TigerVNC `:1` session or cleans stale locks and starts one;
3. restarts only the Hydra Python gateway so code/persona/UI mutations become active;
4. starts/reuses Ollama;
5. ensures the FAST and DEEP models are present;
6. prints `/v1/system/status` as the final localhost audit.

## Expected final banner

```text
HYDRA PROFESSOR GREEN FULL GREEN
AcodeX/AXS : 127.0.0.1:8767
VNC        : :1 / 127.0.0.1:5901
Hydra UI   : http://127.0.0.1:8787/ui/index.html
Hydra API  : http://127.0.0.1:8787
Ollama     : http://127.0.0.1:11434
FAST       : qwen3:0.6b
DEEP       : qwen2.5:3b
```

## Lum persona boundary

Lum is the only user-facing persona. Tool calls, model selection, service probes and future remote providers remain internal implementation details. The persona must never claim an action succeeded without verified tool output and must never execute arbitrary model-generated shell code.

## Manual validation

```bash
curl -s http://127.0.0.1:8787/health | python -m json.tool
curl -s http://127.0.0.1:8787/v1/system/status | python -m json.tool
curl -s http://127.0.0.1:8787/v1/models | python -m json.tool
```

FAST chat test:

```bash
curl -s -H 'Content-Type: application/json' \
  -d '{"conversation_id":"professor","message":"Give me a smug but useful green systems report.","mode":"fast","speak":false}' \
  http://127.0.0.1:8787/v1/hydra/turn | python -m json.tool
```

DEEP build test:

```bash
curl -s -H 'Content-Type: application/json' \
  -d '{"conversation_id":"professor","message":"Outline the next Hydra architecture milestone.","mode":"deep","speak":false}' \
  http://127.0.0.1:8787/v1/hydra/turn | python -m json.tool
```

Open the mobile cockpit at:

```text
http://127.0.0.1:8787/ui/index.html
```

The UI should show independent GREEN/RED cards for Hydra, AXS/Acode, VNC, Ollama and TTS, plus FAST/DEEP mode buttons and optional browser/system dictation.
