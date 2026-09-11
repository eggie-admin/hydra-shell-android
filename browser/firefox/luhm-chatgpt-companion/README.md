# LuHm ChatGPT Companion 0.3.3 — Witching Hour

Scope: **private Firefox Android ChatGPT companion only**. This is a stylish Lum/JRPG overlay for `chatgpt.com`, not an APK, local-LLM operating system, terminal shell, or daemon-control project.

## What the Firefox shell does
- Adds a floating Lum/JRPG control surface to ChatGPT.
- Inserts only the sealed Lum commands into the visible ChatGPT composer.
- Never presses Send; the Professor remains final authority.
- Offers Japanese voice mode with English subtitle overlay.
- Reads only the newest assistant turn, locally, and only while voice mode is explicitly enabled for the current page session.
- Uses private Destiny Child audio as local event cues when available.
- Queries a read-only private asset cache at `http://127.0.0.1:8799`.
- Never handles ChatGPT passwords, cookies, session tokens, OpenAI API keys, Google Drive credentials, AMO credentials, or Hugging Face tokens.
- Declares no data collection.

## Sealed commands
- PET LUM
- ROLL D20
- GACHA PULL
- DATE EVENT
- SUMMON IMAGE
- CAST ULTIMA
- SAVEPOINT

## Japanese voice + English subtitles
Voice mode asks ChatGPT for three explicit markers:

```text
LUM-JP: <natural Japanese line>
LUM-EN: <faithful concise English subtitle>
LUM-EMOTION: <neutral|happy|teasing|annoyed|excited|soft>
```

Playback order:
1. local generated-TTS TTL cache;
2. Firefox/Android `ja-JP` Web Speech voice;
3. subtitles only.

The direction is original playful goth-alt oni/JRPG heroine energy. It does **not** imitate a specific character or performer.

## Google Drive source of truth + local TTL cache
Google Drive is the canonical private asset vault. It is SFTP-like in workflow when used through `rclone`, but it is not literal SFTP.

Recommended local cache:

```text
~/luhm-private/assets/
  DestinyChildMods/
  private-gacha/
  voice-cache/
  destiny-audio-index.json
  luhm-manifest.json
```

Defaults:
- Drive/audio refresh TTL: 6 hours (`21600` seconds)
- generated Japanese TTS TTL: 7 days (`604800` seconds)

Third-party sprites, Live2D files, audio, game packages, and adult/private reward assets stay outside GitHub and outside the signed XPI.

## Optional Hugging Face
`termux/hf-tts-cache.py` can pre-generate an original Japanese TTS clip into the local cache. It is optional and fail-soft.

Private environment only:

```bash
export HF_TOKEN='...'
export LUHM_HF_TTS_MODEL='model-id-you-selected'
python termux/hf-tts-cache.py --ja '日本語の台詞' --en 'English subtitle'
```

If Hugging Face is unavailable, the extension falls back to local Web Speech and then subtitles.

## Private asset bridge

```bash
pkg install python rclone
chmod +x termux/luhm-private-bridge termux/sync-voice-cache
./termux/luhm-private-bridge sync-voice
./termux/luhm-private-bridge start
./termux/luhm-private-bridge status
```

The bridge binds only to `127.0.0.1:8799` and serves the private local cache read-only from the extension's point of view.

## Witching Hour forge
One deterministic entry point is used locally and in GitHub Actions:

```bash
python3 forge.py
```

It runs the same **10 hard passes** for manifest/scope, permissions, command seal, auto-send guard, credential/exfil guard, voice privacy, TTL cache, copyright isolation, scope pruning, and syntax/package integrity. It then emits a deterministic unsigned XPI plus audit report under `dist/`.

The forge is Python-stdlib-only. No npm or pip install is required for packaging. If `node` and `bash` are present, it additionally runs `node --check` and `bash -n`.

## Firefox Android install reality
Standard Firefox requires a Mozilla-signed XPI. For this private extension use AMO **unlisted/self-distributed** signing. Android still requires the user to select the signed XPI and approve **Add**; this project never claims silent installation.

## Security doctrine
- Firefox companion only
- localhost asset cache only
- no remote executable code
- no prompt auto-send
- no credential or cookie access
- no chat-history upload
- no copyrighted asset bytes in Git or XPI
- no terminal launcher
- no Edge Gallery / Ollama / APK mutation
- human final authority
