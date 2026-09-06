# Contributing to LuHm OS / KAI 9000

Thank you for helping with the Samsung Android testing forge.

## Start here
Read:
- `README.md`
- `AGENTS.md`
- `lumh-os/kai9000/AI_MAGIC_DOCTRINE.md`
- `docs/ULTIMA_BUILD_ALTAR.md`

## Branch and patch policy
- Target `testing/luhm-os-android` for current Android integration work.
- Keep changes small and reviewable.
- Do not silently change the pinned Samsung donor or toolchain.
- Do not promote/merge automatically.

## Required local checks

```bash
python -m compileall -q backend tools ultima/ollama-ffmpeg-antenna-v3
python -m pytest -q backend/tests
bash tests/hydra-sanity-audit-test.sh
```

For Android-affecting changes, run or request the `Oni Summoning - Ultima Debug APK` workflow.

## Pull requests
A PR should state:
- mission/problem;
- files changed;
- doctrine/security impact;
- tests executed;
- APK workflow result when relevant;
- rollback path;
- known limitations.

## Secrets and assets
Never commit API keys, OAuth tokens, release signing keys, private voice recordings, model weights, proprietary extracted game assets, or user-private data.

Reference third-party assets and models with license/provenance metadata instead of copying them when rights are unclear.

## Agent-generated changes
AI assistance is welcome. Generated code is held to the same standards as human-authored code. The author must still provide executed test/build evidence and review the patch.
