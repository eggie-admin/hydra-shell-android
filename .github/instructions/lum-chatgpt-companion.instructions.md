# LuHm ChatGPT Companion Copilot Instructions

Scope: `tools/lum-chatgpt-companion/**`

This lane is a **desktop Chrome convenience helper** for the sealed ChatGPT-only Lum Roleplay project.

Rules:

1. Preserve the canonical sealed commands exactly: `PET LUM`, `ROLL D20`, `GACHA PULL`, `DATE EVENT`, `SUMMON IMAGE`, `CAST ULTIMA`, `SAVEPOINT`.
2. Never auto-submit ChatGPT prompts. The extension may insert text, but the Professor chooses Send.
3. Never store OpenAI API keys, cookies, OAuth tokens, session tokens, or ChatGPT credentials.
4. Do not scrape conversation history or transmit chat contents to third-party services.
5. Do not mutate Android/KAI9000 production code from this lane.
6. Keep Manifest V3 permissions minimal and justify any new permission.
7. Prefer resilient DOM discovery over brittle generated CSS class names.
8. If ChatGPT DOM changes, fail closed with a visible error instead of clicking unknown elements.
9. Do not claim one-click silent installation. Chrome requires Web Store or managed policy for normal streamlined installation; developer builds use Load unpacked.
10. Chrome Android is not a supported runtime for normal extensions. The core roleplay must remain usable directly inside ChatGPT without this helper.

Definition of green:
- manifest parses;
- no remote code;
- only sealed commands accepted by content script;
- selected command inserts into a ChatGPT composer;
- no code path submits the prompt automatically.
