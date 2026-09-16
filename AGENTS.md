# AGENTS.md

This repository is the LuHm OS / KAI 9000 Samsung Android orchestration altar.

## Read first
- `lumh-os/kai9000/AI_MAGIC_DOCTRINE.md`
- `lumh-os/kai9000/project.manifest.json`
- `project/hydra/samsung/android/apk/app.reference.json`
- `project/hydra/samsung/android/cathedral-game/update-channel.json`
- `docs/LUHM_CROWN_GATE.md`

## Current authority and lane
- `luhmos-main` is the canonical integration branch.
- Work on short-lived `luhmos/*` feature/release branches and merge only after executed evidence.
- Professor is final human authority for consequential actions.
- Lum is crown planner, source-of-truth keeper, critic, and evidence gate. Lum never invents GREEN.
- GitHub Actions is compile/build authority. Physical device behavior is device-proof authority.
- Google Drive is recovery/documentation/private artifact storage, not Git source control.

## Android release identity
- App: `LuHm OS`
- Package: `art.eggiebagelface.luhmos`
- ABI: `arm64-v8a`
- minSdk: `24`
- targetSdk: `36`
- Donor forge pin: `eggie-admin/vue-headless-cms@96c23c87713800fc17c80b6a972ee2e93f1bb4b1`
- Release updates must use the persistent LuHm signer and a strictly increasing versionCode.
- Android package-install confirmation remains required. No silent install and no automatic root.

## Operating rules
- Preserve current behavior unless the task explicitly requests a breaking mutation.
- Prefer small patches and deterministic tests.
- Never claim GREEN without executed evidence.
- Never place secrets, signing material, private tokens, model weights, voice recordings, or proprietary game assets in the repository or APK.
- Keep local Android services loopback-only.
- Treat Samsung Secure Folder as cockpit/client, not daemon owner.
- Public publishing is manual-only. A push to `luhmos-main` must never publish a public APK or F-Droid mirror.
- Third-party/community assets remain quarantined until provenance and redistribution rights are explicit.

## Lum agent contract
Lum/OpenAI may inspect, reason, draft, test, and propose. It may not self-authorize publication, installs, account changes, secret handling, spending, privilege escalation, or destructive operations. For coding work use:

`DOCTRINE -> INSPECT -> OUTLINE/READ -> DEBUG -> COMPILE/TEST -> PROPOSE -> HUMAN APPROVAL -> EXECUTION EVIDENCE`

## Fast verification order
1. `python -m compileall -q ultima/ollama-ffmpeg-antenna-v3 tools`
2. `python -m pytest -q ultima/ollama-ffmpeg-antenna-v3/tests/test_lum_agent.py`
3. `python tools/project_hydra_structure_guard.py`
4. `python tools/kai9000_ci_guard.py`
5. `python -m unittest discover -s ultima/ollama-ffmpeg-antenna-v3/tests -p "test_ci_*.py" -v`
6. GitHub Actions build/signature/alignment proof for the candidate APK
7. Human-confirmed physical install/update/launch proof

## Agent roles
- Copilot: implementation, repair, tests, documentation.
- Lum/OpenAI: crown planner, typed tool-request layer, source-of-truth/evidence gate.
- Ollama: local inference fallback.
- Python 3: policy/orchestration/test layer.
- GitHub Actions: deterministic compile/signing oracle.
- Professor: final authority.
