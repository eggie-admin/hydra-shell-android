# Support

## What this repository supports
This repository coordinates the LuHm OS / KAI 9000 Samsung Android testing lane, including doctrine, local Python/Ollama services, build gates, and APK orchestration.

## Before asking for help
Include:
- branch and commit SHA;
- Samsung device/model and Android version when relevant;
- exact failing workflow/job/step;
- command output with secrets removed;
- whether the problem is build, install, runtime, Secure Folder, Shizuku, Ollama, AcodeX/VNC, Godot, or media related.

## Fast triage
Run:

```bash
python -m compileall -q backend tools ultima/ollama-ffmpeg-antenna-v3
python -m pytest -q backend/tests
bash tests/hydra-sanity-audit-test.sh
```

For APK failures, attach the relevant `Oni Summoning - Ultima Debug APK` job name and error summary.

## Known separate lane
USB/UVC camera access on Samsung/Knox is a separate Android permission problem. Do not tear down a green localhost control plane solely to debug camera permissions.

## Security reports
Do not paste secrets or exploit details into public support threads. Follow `SECURITY.md`.
