# LuHm ChatGPT Companion Copilot Instructions

Scope: `browser/firefox/luhm-chatgpt-companion/**`

This lane is a **private-first Firefox Android ChatGPT companion**. It is a stylish roleplay/voice/audio overlay for ChatGPT, not a LuHm OS, APK, terminal, Edge Gallery, or Ollama lane.

Rules:

1. Preserve the canonical sealed commands exactly: `PET LUM`, `ROLL D20`, `GACHA PULL`, `DATE EVENT`, `SUMMON IMAGE`, `CAST ULTIMA`, `SAVEPOINT`.
2. Never auto-submit ChatGPT prompts. The extension may insert text, but the Professor chooses Send.
3. Never store OpenAI API keys, cookies, OAuth/session tokens, ChatGPT credentials, AMO credentials, Google Drive credentials, or Hugging Face tokens in the extension.
4. Do not scrape conversation history or transmit chat contents to third-party services.
5. Japanese voice mode may read only the newest assistant turn, locally, and only after the user explicitly enables voice mode for the current page session.
6. Keep Firefox Android Manifest V3 permissions minimal and fail closed if ChatGPT's DOM changes.
7. Runtime network access is limited to ChatGPT plus the loopback asset cache on `127.0.0.1:8799` / `localhost:8799`.
8. Remote executable code is forbidden. Localhost may provide private data/assets, but all JavaScript executed by the extension must be packaged with the extension.
9. Third-party copyrighted sprites, Live2D models, textures, motions, audio, game packages, and private adult reward assets are local runtime/reference material only. Never commit, mirror, publish, or bundle those bytes into public Git or the XPI.
10. Voice direction must remain original. Do not imitate a specific copyrighted character voice or identifiable performer.
11. Google Drive via the user's private `rclone` connection is the canonical asset vault. Local phone storage is a TTL cache, not a second source of truth.
12. Hugging Face TTS is optional and cache-producing only. `HF_TOKEN` stays in the private Termux environment. Failure must fall back to Web Speech or subtitles.
13. The deterministic local forge is `browser/firefox/luhm-chatgpt-companion/forge.py`. Keep it stdlib-only for package builds and use the same ten-pass logic locally and in CI.
14. Firefox signing is required for normal Firefox. Private/unlisted signing is preferred. Never claim silent installation; Android requires explicit Add approval.
15. Human final authority remains Professor.

Definition of green:
- `forge.py` returns `WITCHING_HOUR_GREEN` with all 10 passes PASS;
- manifest is MV3, version-aligned, and Firefox Android enabled;
- runtime hosts are only ChatGPT and localhost asset cache;
- sealed command whitelist is intact;
- no prompt auto-send path;
- no credentials/cookies/chat exfil path;
- Japanese voice mode is explicit and session-only;
- TTL cache expiry is enforced;
- no private/game binary asset bytes are present in the extension tree or XPI;
- terminal/Edge Gallery/Ollama/APK runtime code is absent;
- JSON/Python/bash/JavaScript syntax checks pass;
- deterministic unsigned XPI and SHA-256 are produced.
