# LuHm OS / KAI 9000 Overview

## Approach
LuHm OS means **Linux / Unix approach Hydra manifest**. KAI 9000 is the working title for the local-first AI, media, game, and Samsung Android stack.

The project favors boring, inspectable plumbing over opaque automation:

- GitHub stores doctrine, source references, CI evidence, and release checkpoints.
- Python 3 owns orchestration, policy, tests, RSS/feed normalization, and localhost services.
- Godot 4 owns the Android cockpit/game surface.
- Ollama owns local inference when available.
- OpenAI/Lum provides remote reasoning, coding assistance, agent orchestration, and typed tool requests.
- Samsung/Termux provides the mobile daemon/control plane.
- Secure Folder remains a protected client/cockpit.

## Mission
Build a reproducible Samsung Android cockpit that can combine:

- AI chat and coding assistance;
- local Ollama inference;
- Godot 4 UI/game systems;
- JRPG/social-link experiments;
- media/FFmpeg tooling;
- RSS/reference ingestion;
- Samsung Edge/Widget surfaces;
- controlled cloud AI lanes;
- deterministic Android APK builds.

The mission is not “maximum automation.” The mission is **maximum useful automation with checkpoints, evidence, and rollback**.

## AI doctrine
The canonical policy is `lumh-os/kai9000/AI_MAGIC_DOCTRINE.md`.

The model proposes intent. Policy resolves what tools are allowed. High-impact work requires exact approval. Generated text is never automatically equivalent to executable shell.

ULTIMA is the convergence spell: it means all required lanes have reached one verified final goal. For Android, that final goal is an actual installable APK with build evidence.

## Python 3
Python 3 is the common orchestration layer because it works across Linux, Termux, CI, feed processing, policy checks, tests, FastAPI/Flask-style services, FFmpeg wrappers, and device probes.

Python code should remain small, typed where practical, testable, and free of model-authored arbitrary shell execution.

## OpenAI / Lum
OpenAI is the remote reasoning and agent lane. Lum is the user-facing spell compiler/persona layer.

OpenAI responsibilities:
- coding/reasoning assistance;
- structured intent generation;
- typed function/tool requests;
- optional agent sessions and guardrails;
- review of complex plans.

Credentials remain server-side. The APK does not contain OpenAI API keys. The OpenAI lane is optional for local operation and cannot override repository policy.

## Ollama
Ollama is the local daemon at `127.0.0.1:11434`.

It provides offline/local chat and lightweight director tasks where device resources permit. It is not exposed publicly and does not receive unrestricted shell authority.

## Edge Gallery
**Edge Gallery** is the working name for the Samsung-facing local gallery/media surface used by the cockpit, widget, and creative lanes.

Its job is to surface approved local media, generated previews, reference cards, and status artifacts with touch-friendly Samsung UI. It is not a cloud hosting service and has no authority over Android build status.

## Godot 4
Godot 4 is the visual cockpit/game runtime. The pinned Samsung build candidate currently targets Godot 4.7.2 and contains:

- Android export presets;
- a Godot Android v2 plugin;
- WebView/CMS integration;
- Samsung widget support;
- local API bridges;
- room for JRPG/social-link and avatar layers.

## Samsung APK development
Canonical testing branch:
`testing/luhm-os-android`

Pinned APK donor:
`eggie-admin/vue-headless-cms@86507ed7c72650ff508eb9a1a9e52842eb50e821`

Trust boundary:
- ordinary Termux owns daemon processes;
- Secure Folder is a cockpit/client;
- Shizuku is explicit and scoped;
- no automatic root;
- local services bind to loopback;
- USB camera permission work remains isolated.

Canonical ports:
- AcodeX/AXS `127.0.0.1:8767`
- TigerVNC `127.0.0.1:5901`
- WebSocket `127.0.0.1:6080`
- Hydra cockpit `127.0.0.1:8787`
- Ollama `127.0.0.1:11434`

## Build authority
Copilot writes code. Actions builds it. Android GREEN requires executed evidence from the repository build pipeline, not a chatbot claim and not an external hosting status.
