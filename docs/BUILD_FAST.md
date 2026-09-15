# LuHm OS Fast Build + Install Guide

## Goal

Get from a reviewed patch to a verified, persistently signed Samsung Android artifact using the shortest safe feedback loop. Keep the tablet as an operator/cockpit surface and keep heavyweight Android compilation in deterministic remote CI.

## Canonical source of truth

- Integration branch: `luhmos-main`
- Production package: `art.eggiebagelface.luhmos`
- Android donor: pinned immutable commit from `eggie-admin/vue-headless-cms`
- Contract gate: `.github/workflows/luhmos-ultima-debug-apk.yml`
- Signed release + F-Droid forge: `.github/workflows/luhmos-fdroid-public-release.yml`
- Legacy `art.eggiebagelface.kai9000.dev` workflows are historical and must not be revived as the production package line.

AI proposes. Policy authorizes. CI proves. The Professor promotes.

## Cheap checks first

When a development terminal is available, run the inexpensive policy/test layer before Android build minutes are spent:

```bash
python -m compileall -q backend tools
python -m pytest -q backend/tests
bash tests/hydra-sanity-audit-test.sh
```

A tablet does not need to run these locally. GitHub Actions remains the deterministic build oracle.

## Remote contract gate

From GitHub Actions run:

`LuHm OS ULTIMA Debug Contract`

against the candidate branch or PR targeting `luhmos-main`.

This gate validates doctrine, Python tests, the pinned Samsung donor, package identity, API/ABI requirements, no-secret rules, and the standalone/no-Termux Android boundary. It deliberately cannot publish a production release.

## Signed installable build

For a real install/update artifact run:

`LuHm OS Public F-Droid Release`

Start with:

`publish_public_mirror = false`

That lane builds the non-debug APK with the persistent `luhmos-release` signing identity, verifies Android package identity, signature, SHA-256, arm64-v8a, target SDK 36 and 16 KiB alignment, then stages and signs F-Droid metadata/indexes. Publication of the custom F-Droid mirror remains an explicit separate choice.

Never use an ephemeral debug signer for update continuity.

## Current install surface

The robust bootstrap install surface is the repository's GitHub Releases page:

`https://github.com/eggie-admin/hydra-shell-android/releases/latest`

A signed `LuHm OS` APK and its checksum/signature evidence can be attached to the release by the remote pipeline. On stock Android, installation is always user-confirmed through Android's normal package installer.

The in-app Update Portal should hand the user to this trusted HTTPS release surface rather than requesting silent-install authority. The app itself does not need `REQUEST_INSTALL_PACKAGES` for this bootstrap design.

## SM-X400 Google Play test lane

The unrooted Samsung SM-X400 is a cockpit and compatibility target, not a second source of truth and not a build server. Its lane is defined in:

- `docs/SMX400_PLAY_TESTING_LANE.md`
- `project/hydra/samsung/android/apk/sm-x400-play-testing.manifest.json`

The tablet may use Google Play tooling, GitHub, ChatGPT, browser and other operator apps, but LuHm OS core launch must remain standalone and must not depend on Termux, Acode, VNC, Secure Folder, root or a localhost daemon.

## Remote services

- GitHub: canonical source history, CI, release artifacts and provenance.
- Google Cloud: optional keyless remote infrastructure through GitHub OIDC. Long-lived cloud keys do not belong in Git or the APK.
- OpenAI: remote reasoning/tool proposal behind policy gates.
- Hugging Face: model registry/forge with provenance and license gates.
- Google Drive: controlled recovery/artifact mirror where applicable, never a silent code-authority override.

Optional provider failure must not prevent the base Android application from launching.

## Promotion rules

- inspect before editing;
- change the smallest surface;
- keep donor revisions immutable once promoted;
- do not regenerate lock files unless required;
- do not bump toolchains during unrelated work;
- never disable tests to obtain GREEN;
- do not put private keys, API tokens or keystores in Git, APK assets, logs or prompts;
- no automatic root, silent package installation or unrestricted model shell;
- public publication, signer changes and production promotion remain human approval gates.

## GREEN means evidence

A release claim is GREEN only when the relevant CI actually ran and produced evidence: installable APK, expected package ID, persistent signing identity, SHA-256, ABI/SDK checks, 16 KiB alignment and required policy tests. Documentation alone is not build evidence.