---
applyTo: "fdroid/**,release/**,.github/workflows/*fdroid*.yml,docs/FDROID_FINAL_FORM.md"
---

# KAI 9000 F-Droid Final Form Instructions

Final distribution goal: a signed custom F-Droid repository that can be added/imported into an F-Droid client.

Canonical DSL:

```text
AIRSHIP KAI9000
WARP GIT
BLACK_MAGIC FDROID
FINAL_FORM SIGNED_FDROID_REPOSITORY
```

Rules:

1. Treat the APK as an intermediate artifact. Final-form evidence is the signed repository, stable fingerprint, published HTTPS endpoint, successful F-Droid client import, and upgrade continuity.
2. Keep APK signing identity and F-Droid repository signing identity persistent and separate in purpose.
3. Never generate a new long-lived signing identity on every CI run.
4. Never commit keystores, key passwords, Base64-encoded keys, or raw signing credentials.
5. The existing Oni Summoning workflow may continue using ephemeral debug APK signing for smoke testing, but such APKs cannot prove final update continuity.
6. Use the donor metadata for `art.eggiebagelface.videoforge.dev` unless an explicit package-identity migration is approved.
7. `FDROID_STAGED` means APK + metadata staging only. It is not a signed or importable repository.
8. `FDROID_SIGNED` requires fdroidserver-generated signed indexes and recorded non-secret repo fingerprint.
9. `FDROID_PUBLISHED` requires a reachable HTTPS repository endpoint, conventionally ending `/fdroid/repo/`.
10. `FDROID_IMPORT_VERIFIED` requires an F-Droid client to add the repo and discover/install the package.
11. `FINAL_FORM_GREEN` additionally requires an upgrade-path test proving the next APK version installs without signing mismatch.

Read:
- `lumh-os/kai9000/AI_MAGIC_DOCTRINE.md`
- `docs/FDROID_FINAL_FORM.md`
- `fdroid/final-goal.manifest.json`
- `fdroid/config.template.yml`

Copilot may repair code and workflows. It may not fabricate signing evidence, generate or expose persistent secrets, publish without the required gate, or call final form GREEN without executed evidence.
