# Support

## What this repository supports
This repository coordinates LuHm OS source, doctrine, bounded AI/tool contracts, build gates, Android packaging goals, and public-beta release evidence.

KAI 9000 is donor/reference material only. Project Hydra is historical compatibility and repository lineage only.

## Before asking for help
Include:
- exact branch and commit SHA;
- platform, device/model, and OS version when relevant;
- exact failing workflow, job, step, command, or screen;
- sanitized output with secrets removed;
- whether the problem is source/CI, build, signing, install, runtime, provider integration, Godot/UI, media, distribution, or recovery related.

## Fast triage
Use the smallest relevant check first. For repository-wide Python 3 validation, prefer the existing deterministic project guards and focused tests instead of running unrelated legacy KAI paths by habit.

The vendor/API spine is guarded by:

```bash
python3 tools/vendor_api_pipeline_audit.py
```

For Android release failures, identify the exact artifact, package identity, signer, hash, architecture evidence, workflow run, and device result being discussed. A debug artifact or successful compile is not automatically public-release GREEN.

## Public beta feedback
Non-sensitive beta reports should include:
- what you expected;
- what happened;
- exact reproduction steps;
- the relevant commit/ref;
- sanitized logs, screenshots, or receipts when useful.

Do not include API keys, signing material, recovery secrets, private provider identifiers, or private user information.

## Historical / donor material
Legacy Termux, VNC, Secure Folder, KAI 9000, and old Hydra control-plane material may remain in the repository as donor code, migration evidence, or historical reference. Do not assume those paths are required by the current LuHm OS runtime unless the current source-of-truth explicitly says so.

## Security reports
Do not paste secrets or exploit details into public support threads. Follow `SECURITY.md` and use private reporting for sensitive findings.
