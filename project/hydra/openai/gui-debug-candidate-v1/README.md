# LUHM GUI debug candidate

Open `index.html` in a browser. It runs locally without a server, network services, API keys, or build step.

- Preview scale starts at 150% (1.5× width and height). This controls this candidate only, not ChatGPT's pet renderer.
- Greet, Bounce, and Inspect queue local animation states, then return to idle. Stop clears current and queued events. Pause freezes playback; pending events are limited to four.
- Load an existing PNG/WebP sprite atlas, at most 20 MiB: v1 1536×1872 or v2 1536×2288. The loader checks format, decoding and geometry only. It does not certify artwork quality or validate transparency and every animation frame.
- The mesh panel simulates Context, Build, Research and Critic. Three slots, eight operations or 180 seconds per task. No real agents, tools, approvals or shell commands execute.
- Export receipt downloads a JSON record with truthful local state and recent events.
- No state persists after closing the page. Images remain local to the browser; exporting a receipt does not embed the artwork.

## Milestone boundary

This is a standalone GUI candidate. Tiny Lum's source download returned 403 in the preceding attempts; her artwork is intentionally absent. Her active ChatGPT pet has not been replaced. ChatGPT toy integration, live agent scheduling, physical-device testing and deployment are not claimed.

The Mesh v1 Crown approves the doctrine. It does not make this local simulator a production executor.

## Verification

`verification.json` records executed checks. `verify.cjs` is the browser check script. It requires Node.js, Playwright and its Chromium browser; set `CODEX_PRIMARY_RUNTIME_NODE_MODULES` to the directory containing Playwright, or install Playwright locally. Run `node verify.cjs`.

Executed here: 12 Node VM logic checks passed with minimal DOM test doubles (`node verify-logic.cjs`). Browser execution was blocked because Chromium was missing and download timed out. Visual rendering and mobile layout remain unverified.
