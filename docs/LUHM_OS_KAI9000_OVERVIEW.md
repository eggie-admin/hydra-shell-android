# LuHm OS / KAI 9000 Overview

## Approach
LuHm OS means **Linux / Unix approach Hydra manifest**. KAI 9000 is the working title for the local-first AI, media, game, and Samsung Android stack.

The project favors boring, inspectable plumbing over opaque automation:

- GitHub stores doctrine, source references, CI evidence, and release checkpoints.
- Python 3 owns orchestration, policy, tests, feed normalization, and localhost services.
- Godot 4 owns the Android cockpit/game surface.
- Ollama owns optional local inference when available.
- OpenAI/Lum provides remote reasoning, coding assistance, agent orchestration, and typed tool requests.
- Samsung Android is the primary physical target.

## Mission
Build a reproducible Samsung Android cockpit that combines AI assistance, local inference where useful, Godot UI/game systems, media tooling, deterministic Android builds, and bounded cloud lanes without giving models unrestricted shell, signing, release, or deployment authority.

## Runtime authority
The Android production target is a self-contained APK. External development editors and their localhost bridges are retired from active runtime authority. They may remain in Git history only as migration evidence.

Current localhost development services:

```text
Mutation gateway  127.0.0.1:8790
Hydra cockpit     127.0.0.1:8787
TigerVNC          127.0.0.1:5901   optional
Ollama            127.0.0.1:11434  optional
```

The mutation gateway is the only active repository-write surface in the local development lane and requires explicit human approval.

## AI doctrine
The model proposes intent. Policy resolves allowed tools. High-impact work requires exact human approval. Generated text is never equivalent to executable shell.

## Python 3
Python 3 is the reference orchestration layer for policy checks, tests, bounded services, media wrappers, and device probes. Code should remain small, inspectable, testable, and free of model-authored arbitrary shell execution.

## OpenAI / Lum
OpenAI is the primary remote reasoning lane. Lum is the user-facing agent/persona layer. Credentials remain server-side and never belong in APK assets, Git, logs, or prompts.

## Ollama
Ollama is an optional loopback-only local inference provider. It is not public, is not release authority, and receives no unrestricted shell authority.

## Godot 4 and Samsung APK
Godot 4 is the visual cockpit/game runtime. Android GREEN requires executed build evidence plus physical-device install/launch evidence. Canonical production package identity remains `art.eggiebagelface.luhmos`; candidate install probes may use a collision-free package identity without changing release identity.

## Build authority
GitHub Actions is the deterministic build forge. External hosting statuses are not build authority. A build is GREEN only when bound to exact source with executed CI, artifact provenance, hash/signature readback, and any required device evidence.

## Source law

> AI proposes. Policy authorizes. CI proves. Android confirms. The human promotes.
