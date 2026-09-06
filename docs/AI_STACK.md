# AI Stack: Lum, OpenAI, Ollama, Python 3 and Edge Gallery

## Design principle
The AI stack is split by responsibility so no single model becomes the operating system.

```text
User / Samsung cockpit
        ↓
Lum intent layer
        ↓
Python policy + typed tools
   ↙                 ↘
OpenAI remote       Ollama local
   ↓                 ↓
reasoning            local inference
        \           /
         verified result
              ↓
       Godot / Edge Gallery
```

## Lum / OpenAI
Lum is the user-facing spell compiler/persona layer. OpenAI is the remote reasoning and agent lane.

Use OpenAI for:
- complex coding/review tasks;
- structured intent generation;
- typed function/tool requests;
- guardrailed agent workflows;
- optional session-based context.

OpenAI tool calls do not bypass KAI 9000 policy. Tool inputs and outputs are validated by application-owned code. High-impact actions require the doctrine's approval/checkpoint rules.

`OPENAI_API_KEY` is server-side only. It never belongs in Android resources, WebView JavaScript, source control, CI artifacts, Base64 manifests, or debug APKs.

The APK must still launch and expose useful local/offline state when the OpenAI lane is unavailable.

## Ollama
Ollama is the local inference daemon and first offline fallback.

Canonical endpoint:
`http://127.0.0.1:11434`

Ollama responsibilities:
- fast local chat;
- lightweight director/planner tasks;
- local tool-selection proposals when supported;
- offline fallback.

Ollama has no unrestricted shell authority and is not publicly exposed.

## Python 3
Python 3 is the policy and orchestration layer.

Responsibilities:
- localhost API services;
- typed tool dispatch;
- device/service probes;
- RSS/feed sanitation;
- SQLite state where appropriate;
- FFmpeg wrappers;
- build/test sanity;
- OpenAI/Ollama routing;
- release evidence generation.

Prefer explicit functions and data structures over generated shell strings.

## Godot 4
Godot 4 owns the user-visible Android runtime, game systems, JRPG/social-link experiments, avatar/UI state, and WebView/plugin integration.

Godot talks to approved localhost APIs or typed Android plugin surfaces. It does not become a credential vault or arbitrary shell host.

## Edge Gallery
Edge Gallery is the Samsung-facing media/status surface.

It may show:
- generated previews;
- local image/video cards;
- build artifacts and status summaries;
- avatar/character references;
- approved gallery items;
- widget/edge-panel state.

It does not ingest secrets and does not decide build/release status.

## Failure behavior
OpenAI unavailable → fall back to local/mock/Ollama behavior where possible.  
Ollama unavailable → UI remains responsive and reports offline state.  
Optional media service unavailable → chat/build shell still launches.  
Secure Folder cannot inspect daemon PIDs → probe localhost endpoints instead.

## Final authority
The Professor defines the goal. Policy defines the allowed actions. Models propose. Tools execute. CI verifies builds.
