# KAI 9000 In-App Lum Chat Cockpit

Milestone: `KAI9000_INAPP_LUM_CHAT_COCKPIT_20260907`

Status: `GREEN_ON_MUTATION_BRANCH`

## Crown

- Professor is final authority.
- KAI 9000 APK is the active mutation target.
- GitHub is canonical versioned source.
- Google Drive is recovery/artifact mirror.
- Cloudflare is the public edge.
- Vercel is retired and forbidden.
- Local Termux is retired from the active architecture.

## Visual mutation

The cockpit was redesigned from the supplied visual references:

- `Infernal Secretary Outfit Mutation Collection.png`
- `KAI 9000 Infernal Companion Cockpit.png`

The active UI uses the reference language rather than embedding unverified binary attachment paths: antique gold + electric blue + infernal red, Lum persona panel, active quests, rewards, command casts, bottom cockpit navigation, and a collapsible advanced Forge Bay.

## In-app chat

`/api/lum/chat` now accepts an opaque `session_id`. The browser creates and persists that ID in `localStorage`; the server validates it and uses OpenAI Agents SDK `SQLiteSession` when OpenAI is configured.

- Default route: GPT-5.6 Luna, reasoning `none`.
- Heavy route: GPT-5.6 Sol, reasoning `medium`.
- Transport: Responses API, configurable HTTP/WebSocket, WebSocket preferred by KAI doctrine.
- Provider credential remains server-side.
- A new UI session changes the conversation ID without granting any new authority.

## Open-license web ingest

Vendored under `static/vendor/kai-icons/`:

- `spell-book.svg` by Delapouite
- `jewel-crown.svg` by Delapouite
- `magic-swirl.svg` by Lorc
- `floating-crystal.svg` by Lorc

Source: Game-icons.net / `game-icons/icons`.
License: CC BY 3.0.
KAI mutation removes the solid black background rectangle for transparent cockpit compositing. Attribution is preserved in `static/vendor/kai-icons/ATTRIBUTION.md`.

Drive recovery metadata is stored in `KAI9000_SOURCE_OF_TRUTH/ASSETS/KAI9000_WEB_ASSET_INGEST_20260907`.

## CI evidence

GitHub Actions run `34166785699` completed successfully on both Python 3.11 and Python 3.14.

Verified gates:

- OpenAI/Hugging Face Lum tests
- Python compile
- JavaScript syntax
- session contract
- cockpit asset invariants
- current doctrine invariants
- secret-shape guard

This proves code/CI structure. It does not claim a live paid OpenAI request, APK install, Google Play release, Cloudflare deployment, or merge to the testing/main lineage.
