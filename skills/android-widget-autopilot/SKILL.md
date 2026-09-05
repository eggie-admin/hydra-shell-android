---
name: android-widget-autopilot
description: Use when inspecting, hardening, modifying, testing, or documenting Project Hydra's Android Termux widget supervisor branch.
---

# Hydra Android Widget Autopilot

Use this Skill for work on the Project Hydra Android widget/supervisor lane. The user's explicit instructions take precedence over this Skill.

## Mission

Keep the Android side thin, reproducible, localhost-first, and easy to move to a future HTTPS backend without rewriting the application architecture. Treat the current Termux widget supervisor behavior and state files as an existing contract unless the user explicitly requests a breaking mutation.

## Required discovery before mutation

1. Read `.github/copilot-instructions.md`.
2. Inspect the target branch and current commit before writing.
3. Read the specific files involved in the requested change.
4. Check the widget state contract, task paths, ports, process ownership, and localhost binding before editing service-control behavior.
5. Search for existing tests and repository-native validation commands before inventing new ones.

## Mutation boundary

Prefer focused patches over broad rewrites. Do not place API keys, signing keys, tokens, voice recordings, model weights, credentials, or secret-shaped configuration in source, tests, logs, examples, APK assets, or Git history.

Do not silently add root, unrestricted shell execution, arbitrary model-generated code execution, remote control, hidden telemetry, or a public network listener. Preserve typed and allow-listed tool execution. Keep `127.0.0.1:8787` as the development cockpit/backend contract unless the user explicitly changes it.

For Termux:Widget integration, preserve the existing ownership model around `$HOME/.shortcuts/tasks`, `$HOME/.local/state/hydra-services`, lock/state handling, and explicit service health checks. Avoid killing unrelated processes or trusting stale PIDs.

## Autopilot execution loop

1. **Discover**: establish repository, branch, head commit, relevant files, tests, and invariants.
2. **Plan**: define the smallest safe change and identify any compatibility risk.
3. **Mutate**: apply only the requested change plus necessary support changes.
4. **Validate**: run every available relevant test or static check. Do not claim a test ran unless execution evidence exists.
5. **Audit**: classify findings as GREEN, YELLOW, or RED. Remediate RED before declaring the requested milestone complete when the fix is within scope.
6. **Report**: provide changed files, commit SHA(s), executed checks, skipped checks, residual warnings, and whether the branch is merely updated, locally validated, PR-ready, or actually merged/released.

## Validation targets

When the corresponding components exist, prefer these repository gates:

```bash
python -m pytest backend/tests
./gradlew lintDebug testDebugUnitTest assembleDebug
python tools/test_hydra_cockpit.py
```

For the current widget-only lane, at minimum perform Python syntax/tests for changed Python files plus a focused review of process ownership, state-file safety, localhost ports, duplicate-action behavior, and error handling.

## Three-pass architecture audit

Before calling a large widget milestone complete, check:

1. **Architecture/security**: localhost binding, secret hygiene, typed tools, process ownership, WebView/origin policy when applicable, no arbitrary-code execution.
2. **Realtime/reliability**: duplicate taps, backend unavailable, restart behavior, stale PID handling, timeout/failure behavior, microphone/transcript duplicate-send protection when touched.
3. **Build/maintainability**: clean paths, deterministic tests, pinned toolchain where applicable, no generated secret artifacts, installable Android artifact when the Android application layer is present.

## Stop conditions

Do not claim public Plugin Directory submission, approval, publication, APK release, merge, or deployment unless that exact action occurred and evidence is available. Do not expose chain-of-thought. Operational evidence may include file paths, commands, statuses, timings, errors, diffs, commit IDs, and compact reasoning summaries.
