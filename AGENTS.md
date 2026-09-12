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
- Never place secrets, signing material, private tokens, model weights, voice recordings, proprietary game assets, or proprietary browser binaries in the repository or APK.
- Keep local Android services loopback-only.
- Treat Samsung Secure Folder as cockpit/client, not daemon owner.
- No automatic root. Privilege-changing tools are manual and typed.

## Donor quarantine doctrine
- Chrome Dev and Chrome Canary are test/behavior harnesses only, never APK source donors.
- Upstream Chromium source may be consulted only when license/provenance is recorded.
- Legacy donor code is reference-only and must not be packaged into new APKs unless a later explicit reviewed mutation says otherwise.
- Donor trees, donor APKs, `.aar`, `.jar`, `.so`, browser bundles, extracted assets, and quarantine folders must remain outside release inputs.
- Any retained idea must be reimplemented in the KAI 9000 tree with provenance/license notes where required.
- Release preflight must treat `DONOR_PURGED_BEFORE_APK=true` as a required gate.
- Final APK evidence must demonstrate that donor/quarantine payloads are absent.

## Copilot Git handoff
- GitHub Copilot is an implementation and repo-handoff assistant: code repair, focused edits, tests, documentation, commit-message drafts, PR descriptions, CI fixes, and reviewer-ready change summaries.
- When the Professor explicitly says `push`, `ship`, `set sail`, or otherwise authorizes a repository mutation, Copilot may prepare the bounded change for `testing/luhm-os-android` and provide the exact commit/PR handoff.
- Before any push-ready handoff, run or request donor-quarantine preflight plus the normal test/build gates.
- Never auto-promote to `luhmos-main` or `main`.
- Never auto-merge, release, publish, delete branches, or bypass branch/CI protections.
- Preserve rollback points and report repository, branch, commit SHA, CI state, and artifact state separately.

## Build source
KAI 9000 owns the future APK implementation. Historical donor repositories and prior pinned donor commits remain reference/provenance material only and are not authoritative release inputs.

Do not copy donor trees into this repository merely to make a build pass. New APK work must converge on KAI-owned implementation plus explicitly licensed dependencies.

## Fast verification order
1. `python -m compileall -q backend tools ultima/ollama-ffmpeg-antenna-v3`
2. `python -m pytest -q backend/tests`
3. `bash tests/hydra-sanity-audit-test.sh`
4. donor/quarantine preflight with `DONOR_PURGED_BEFORE_APK=true`
5. `.github/workflows/oni-ultima-debug-apk.yml`

## Agent roles
- Copilot: code repair, implementation, tests, documentation, commit/PR preparation, and CI repair under the Professor's push authority.
- Lum/OpenAI: remote reasoning/spell compiler and typed tool-request layer.
- Ollama: local inference daemon.
- Python 3: policy/orchestration/test clergy.
- GitHub Actions: deterministic compile oracle.
- Professor: final authority.
