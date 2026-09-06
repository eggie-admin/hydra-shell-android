# AGENTS.md

This repository is the LuHm OS / KAI 9000 Samsung Android orchestration altar.

## Read first
- @lumh-os/kai9000/AI_MAGIC_DOCTRINE.md
- @lumh-os/kai9000/project.manifest.json
- @project/hydra/samsung/android/apk/testing-ingest.manifest.json
- @docs/ULTIMA_BUILD_ALTAR.md

## Operating rules
- Work in `testing/luhm-os-android` by default.
- Preserve current behavior unless the task explicitly requests a breaking mutation.
- Prefer small patches and deterministic tests.
- Use GitHub Actions as compile/build authority.
- Never claim GREEN without executed evidence.
- Never place secrets, signing material, private tokens, model weights, voice recordings, or proprietary game assets in the repository or APK.
- Keep local Android services loopback-only.
- Treat Samsung Secure Folder as cockpit/client, not daemon owner.
- No automatic root. Privilege-changing tools are manual and typed.

## Build source
The testing APK body is referenced from the pinned public donor:
`eggie-admin/vue-headless-cms@86507ed7c72650ff508eb9a1a9e52842eb50e821`.

Do not duplicate that tree here merely to make a build pass. The workflow checks out the donor at build time.

## Fast verification order
1. `python -m compileall -q backend tools ultima/ollama-ffmpeg-antenna-v3`
2. `python -m pytest -q backend/tests`
3. `bash tests/hydra-sanity-audit-test.sh`
4. `.github/workflows/oni-ultima-debug-apk.yml`

## Agent roles
- Copilot: code repair, implementation, tests, documentation.
- Lum/OpenAI: remote reasoning/spell compiler and typed tool-request layer.
- Ollama: local inference daemon.
- Python 3: policy/orchestration/test clergy.
- GitHub Actions: deterministic compile oracle.
- Professor: final authority.
