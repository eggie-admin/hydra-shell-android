# LuHm ChatGPT Companion 0.2.0 — Firefox / Android

Scope: fun ChatGPT-only Lum Roleplay companion.

## What it does
- Adds a floating 👹 button directly on chatgpt.com.
- Opens touch-sized buttons for the sealed Lum commands.
- Inserts the selected command into ChatGPT.
- Never presses Send.
- Never reads, stores, or transmits ChatGPT login credentials.
- Declares no data collection.

## Sealed commands
- PET LUM
- ROLL D20
- GACHA PULL
- DATE EVENT
- SUMMON IMAGE
- CAST ULTIMA
- SAVEPOINT

## Firefox Android
The manifest explicitly enables Android support through `browser_specific_settings.gecko_android`.

Standard Firefox release builds require Mozilla-signed add-ons. Build artifacts from this branch are signing-ready but must be signed through Mozilla before normal release-channel installation.

Once installed, sign into ChatGPT normally in Firefox. The add-on does not handle or proxy authentication.

## Safety
The extension only inserts a whitelisted command into the visible ChatGPT composer. It does not press Send, scrape credentials, read cookies, or execute arbitrary model-generated JavaScript.
