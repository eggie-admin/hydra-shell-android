# LuHm ChatGPT Companion Copilot Instructions

Scope: `browser/firefox/luhm-chatgpt-companion/**`

This lane is a **private-first Firefox Android companion** for the sealed ChatGPT-only Lum Roleplay project.

Rules:

1. Preserve the canonical sealed commands exactly: `PET LUM`, `ROLL D20`, `GACHA PULL`, `DATE EVENT`, `SUMMON IMAGE`, `CAST ULTIMA`, `SAVEPOINT`.
2. Never auto-submit ChatGPT prompts. The extension may insert text, but the Professor chooses Send.
3. Never store OpenAI API keys, cookies, OAuth tokens, session tokens, ChatGPT credentials, AMO credentials, or Google Drive credentials.
4. Do not scrape conversation history or transmit chat contents to third-party services.
5. Keep Firefox Android Manifest V3 permissions minimal and fail closed if ChatGPT's DOM changes.
6. The signed Firefox shell may talk only to ChatGPT and explicit loopback services on `127.0.0.1` / `localhost`.
7. The extension itself never receives shell privileges. Terminal access is user-initiated by opening a loopback web terminal in a separate tab.
8. Remote executable code is forbidden. Localhost may provide private data/assets, but JavaScript executed by the extension must be packaged with the extension.
9. Third-party copyrighted assets, including game sprites, Live2D models, textures, motions, audio, and packaged game files, are private runtime/reference material only. Never commit, mirror, publish, or bundle them into this public repository or a public AMO listing.
10. Private asset indexing may include every file the user has access to, including adult-labeled paths, but the public shell must not embed or redistribute those files.
11. Firefox signing is required for normal release Firefox. Private/unlisted signing is preferred. Do not claim silent installation; Android requires the user to approve installation.
12. The core Lum roleplay remains usable directly inside ChatGPT even if the private asset cache or terminal bridge is offline.

Definition of green:
- manifest parses;
- Firefox Android target remains declared;
- no remote code;
- no third-party asset bytes in Git;
- only sealed commands accepted by the content script;
- selected commands insert into a ChatGPT composer;
- no code path submits a prompt automatically;
- localhost asset bridge is read-only from the extension's perspective;
- terminal launch opens a separate loopback page and grants no shell API to the extension.
