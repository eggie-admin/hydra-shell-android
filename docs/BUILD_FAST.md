# Fast Build Guide

## Goal
Get from a bounded patch to verified LuHm OS Samsung test evidence with the shortest safe feedback loop.

## Canonical integration lane

Canonical repository: `eggie-admin/hydra-shell-android`  
Canonical integration branch: `luhmos-main`

Use work branches and draft PRs for mutations. CI proves them before promotion.

## Cheap checks first

```bash
python -m compileall -q backend tools ultima/ollama-ffmpeg-antenna-v3
python -m pytest -q backend/tests
bash tests/hydra-sanity-audit-test.sh
```

If these fail, repair them before spending Android forge minutes.

## Remote compile lane

Use the LuHm contract forge:

`Actions → LuHm OS ULTIMA Debug Contract → Run workflow`

For production signing / release staging, use the separate manual workflow:

`Actions → LuHm OS Public F-Droid Release → Run workflow`

Debug CI cannot publish a production release. Production release publication remains an explicit human action.

## Samsung universal stock lane

The current testing mutation converges the Samsung development dungeon into one stock Samsung ARM64 package family:

- Galaxy S24 FE family (`SM-S721*`), including owner-profile and Secure Folder client testing;
- Samsung `SM-X400` tablet testing;
- Galaxy S10 Lite family (`SM-G770*`) as an older unrooted compatibility target.

The Android donor candidate is built as one package, `art.eggiebagelface.luhmos`, with `arm64-v8a`, explicit minimum API 24, target API 36, responsive small-through-xlarge screen support, and one persistent release signer for update continuity.

The current donor mutation lives on:

`eggie-admin/vue-headless-cms:luhmos/sm-x400-play-install-portal-20260915`

The branch adds the cockpit `INSTALL / UPDATE` portal, the universal Samsung compatibility contract, and CI checks for the stock install boundary.

## Install / update bootstrap

Inside the cockpit, `INSTALL / UPDATE` opens the canonical GitHub Releases `latest` page over HTTPS. Android keeps final package-install authority and asks the user to confirm installation or update.

The bootstrap design deliberately does not require root, a privileged installer service, or a broad package-install permission.

Secure Folder is treated as a separate protected client instance of the same signed APK. It does not own the build forge or signing material.

## Cache strategy

Cache only disposable build inputs:

- npm download cache;
- Gradle dependency/build cache through `gradle/actions/setup-gradle`;
- verified Godot editor/export-template archives.

Do not cache secrets, keystores, generated APK signatures, user data, or private model assets.

## Donor pin rule

The Android source currently lives in `eggie-admin/vue-headless-cms`. Pulling a fixed commit gives the compile bot a deterministic Android body while Hydra Shell stays focused on integration policy, CI and release contracts.

Changing the donor pin is a dependency promotion and must be reviewed like a source update.

## Evidence contract

Expected Android evidence includes:

- test and doctrine results;
- APK SHA-256;
- APK signature / signer fingerprint;
- package badging;
- `arm64-v8a` evidence;
- minimum/target SDK evidence;
- 16 KiB zipalign/native compatibility evidence;
- physical-device install and launch proof for every promoted Samsung family;
- same-signer update continuity proof before declaring the universal lane GREEN.

## Speed rules for agents

- inspect before editing;
- edit the smallest surface;
- do not regenerate lock files unless required;
- do not bump toolchains during unrelated fixes;
- do not disable tests to make a build pass;
- do not download model weights during APK compilation;
- do not start optional cloud providers during the compile path;
- cancel stale runs and repair the newest failure.
