# LuHm ChatGPT Companion 0.3.0 — Firefox Android / Private Runtime

Scope: fun ChatGPT-only Lum Roleplay companion with a private localhost asset and terminal bridge.

## What the Firefox shell does
- Adds a floating LuHm/JRPG-style control to `chatgpt.com`.
- Inserts only the sealed Lum commands into the visible ChatGPT composer.
- Never presses Send.
- Never handles ChatGPT passwords, cookies, session tokens, OpenAI API keys, Google Drive credentials, or AMO credentials.
- Declares no data collection.
- Can query a read-only private asset manifest from `http://127.0.0.1:8799/luhm-manifest.json`.
- Can open the private local asset vault and a user-controlled loopback terminal tab.

## Sealed commands
- PET LUM
- ROLL D20
- GACHA PULL
- DATE EVENT
- SUMMON IMAGE
- CAST ULTIMA
- SAVEPOINT

## Private copyrighted assets
Third-party game assets are **not** committed to this repository and are **not** bundled into the signed XPI. They stay on-device in the private asset cache. The cache index can include every file the user has access to, including Live2D models, textures, motions, PCK/data files, sprite sheets, audio, loading screens, and adult-labeled paths. The public shell only knows filenames/metadata requested from localhost.

Recommended private cache root:

```text
~/luhm-private/assets/
  DestinyChildMods/
  FinalFantasy/
  OtherPrivatePacks/
```

The included Termux bridge provides:
- `127.0.0.1:8799` — static private asset cache + manifest
- `127.0.0.1:7681` — optional `ttyd` terminal
- `sync-drive` — optional `rclone` copy of the user's shared `DestinyChildMods` folder after the user has configured their own private Google Drive remote

The extension never receives a shell API. It only opens the terminal page when the user taps **TERMINAL**.

## Firefox Android install reality
Firefox Android supports extensions, but standard Firefox requires Mozilla signing. For a private extension, use AMO **unlisted/self-distributed** signing. On Android, Mozilla's supported private path is a signed XPI installed from file: download/save the signed XPI, unlock `Install Extension from File` by tapping the Firefox logo five times under Settings → About Firefox, then select the XPI and approve Add.

This is not silent installation and should not be represented as such.

## Private bridge quick start in Termux

```bash
pkg install python rclone
# optional, if available in your configured Termux repositories:
pkg install ttyd

chmod +x termux/luhm-private-bridge
./termux/luhm-private-bridge sync-drive   # after rclone remote `gdrive` is configured
./termux/luhm-private-bridge start
./termux/luhm-private-bridge status
```

## Security model
- localhost only
- no remote executable code
- no prompt auto-send
- no credential scraping
- no copyrighted asset bytes in Git or AMO
- human final authority
