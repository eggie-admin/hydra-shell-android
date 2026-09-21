# HYDRA_PROFESSOR_GREEN_FULL_GREEN_001

Status: **HISTORICAL BASELINE · SUPERSEDED FOR ACTIVE RUNTIME**

This document is retained as lineage for an earlier localhost Android workstation milestone. The retired external editor bridge is no longer part of active LuHm OS runtime authority. Its implementation details remain recoverable through Git history rather than being repeated as current instructions.

## Current service map

| Service | Local endpoint | Purpose |
|---|---:|---|
| Mutation gateway | `127.0.0.1:8790` | human-approved repository mutation surface |
| Hydra | `127.0.0.1:8787` | Lum UI + agent API |
| TigerVNC | `127.0.0.1:5901` / display `:1` | optional local graphical desktop |
| Ollama | `127.0.0.1:11434` | optional local model runtime |

The mutation gateway is the only active repository-write surface in this localhost lane and still requires explicit human approval.

## Model modes

```text
FAST / CHAT   qwen3:0.6b
DEEP / BUILD  qwen2.5:3b
```

## Current launcher behavior

`tools/hydra-full-green.sh` now:

1. starts or reuses the gated mutation service on `8790`;
2. preserves or starts the optional VNC desktop;
3. starts/reuses Hydra and Ollama;
4. prints the current localhost health/status surfaces;
5. does not start, probe, or depend on the retired editor bridge.

## Expected current banner

```text
HYDRA PROFESSOR GREEN FULL GREEN
Mutation   : 127.0.0.1:8790
VNC        : :1 / 127.0.0.1:5901
Hydra UI   : http://127.0.0.1:8787/ui/index.html
Hydra API  : http://127.0.0.1:8787
Ollama     : http://127.0.0.1:11434
```

## Authority boundary

Lum is the user-facing persona. Tool calls, model selection, service probes, and remote providers remain bounded implementation details. No model-generated output receives direct shell or repository-write authority.

Historical implementation detail belongs in Git history and sealed receipts, not in active setup instructions.
