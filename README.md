# LuHm OS

**Public beta candidate: The Witching Hour / Final Form**

LuHm OS is a local-first, Unix-shaped creative and AI operating environment built around one visible Lum assistant, bounded tools, explicit human authority, reproducible evidence, and portable application/runtime components.

The public repository is `eggie-admin/hydra-shell-android`. The canonical integration branch is `luhmos-main`.

KAI 9000 is donor/reference/archaeology only. Project Hydra is historical compatibility and repository lineage only. They may remain in paths, receipts, donor code, or old documentation, but they do not define the current product or authority model.

## Public beta status

The source project is public and entering public beta through the reviewed branch and pull-request lane.

Current beta law:

- **LuHm OS stays LuHm OS.**
- `luhm_os` is the established internal project identifier.
- VOWEL_RIP is optional shorthand for shortened internal Python 3 identifiers, helper/stub names, and coding-doctrine artifact IDs. It is not a product, provider, repository, FQDN, release, or human-facing naming law.
- Professor is final human authority.
- Lum is the user-facing Boss.
- Oni/helper agents are bounded, do not recursively recruit, and cannot self-approve consequential work.
- Normal administrator context is the default. Privilege is exact, temporary, explicitly authorized, and immediately returns to normal administration.
- No model receives unrestricted shell, persistent root, signing keys, or automatic publication authority.
- Evidence comes before GREEN.

A public source beta is not automatically a signed Android beta. Signed APK publication, GitHub Release assets, IzzyOnDroid acceptance, F-Droid distribution, app-store publication, DNS changes, and production deployment remain separately evidenced and Crown-gated.

See `release/LUHM_OS_PUBLIC_BETA_NOTICE.txt` for the current beta notice.

## What LuHm OS is building

The first production target is a self-contained Samsung Android application that installs through the normal Android package installer, launches without a development terminal, and updates under one persistent signing identity.

The target architecture includes:

- one visible Lum agent with typed, policy-gated actions;
- Python 3 as the reference orchestration, policy, audit, and tooling layer;
- packaged/local and authorized remote AI providers behind explicit contracts;
- Godot 4 plus bundled web/Vue surfaces for the interactive application cockpit;
- optional media/FFmpeg capabilities where packaged safely or delegated through explicit providers;
- deterministic GitHub CI for testing, build evidence, provenance, and artifacts;
- persistent Android signing identity for update continuity;
- public Android distribution through immutable GitHub Releases and IzzyOnDroid when the release gates are satisfied;
- staged platform homes for Android, Apple, Windows, and Ubuntu/Debian;
- no requirement for a model to receive root, unrestricted shell, signing material, or production authority.

## One LuHm OS project, many provider bindings

LuHm OS uses one logical project identity across multiple provider/transport lanes:

- OpenAI: organization **Pirate Daddy Film**, canonical project **LuHm OS**;
- Google: LuHm OS project/recovery lane, with provider IDs treated as transport identifiers;
- GitHub: `eggie-admin/hydra-shell-android`, canonical integration branch `luhmos-main`;
- Cloudflare: public edge/DNS lane for `eggiebagelface.art`;
- Hugging Face: model catalog and alternate inference transport.

The deterministic source contract for this spine lives in:

- `integrations/vendor-apis.manifest.json`
- `docs/API_TRINITY_DOCTRINE.md`
- `tools/vendor_api_pipeline_audit.py`
- `.github/workflows/luhmos-vendor-api-pipeline-audit.yml`

Historical exact-head receipts record prior internal CI success for the vendor pipeline and unified-project guards. Those receipts remain evidence for the exact heads they tested. They are not silently promoted into fresh live-provider or later-head GREEN.

## Authority model

```text
Professor
   │ final human authority
   ▼
Lum
   │ Boss / planner / synthesizer
   ├── bounded Oni helpers when useful
   │
   ▼
Crown Gate
   │ only when action is consequential
   ▼
Edge Gallery Antenna
   │ local policy / capability gateway
   ▼
Deterministic Tool Executor
   │ bounded execution
   ▼
Evidence receipt
   │
   ▼
Lum → Professor
```

Direct questions bypass the helper mesh. Helpers report to Lum, cannot recursively recruit, and cannot create authority by consensus.

## Security model

Core invariants:

1. **Human authority wins.** AI can propose, inspect, explain, and execute only within explicit capability and approval boundaries.
2. **Normal admin first.** Persistent root is forbidden. Privilege escalation is an exact operation, for the minimum duration, followed by immediate return to normal admin.
3. **Typed actions, not model shell.** Remote/model output never becomes unrestricted shell authority.
4. **Secrets stay outside source.** API credentials, signing material, recovery secrets, and private identifiers never belong in Git, APK assets, frontend bundles, screenshots, logs, or model prompts.
5. **Fail closed.** Missing evidence, unknown commands, ambiguous targets, invalid schemas, missing approvals, or missing signing identity stop promotion.
6. **Evidence before GREEN.** Documentation intent is not execution proof.

See `SECURITY.md` for reporting and release-security details.

## Android target

Current canonical Android identity:

```text
Application:            LuHm OS
Package ID:             art.eggiebagelface.luhmos
Release signing alias:  luhmos-release
Target SDK:             API 36
Primary ABI:            arm64-v8a
Reference device:       Samsung Galaxy S24 FE / SM-S721U1
Android reference:      16
```

A signed Android beta is not GREEN until the applicable evidence exists, including package identity, signer, artifact hash, architecture/native compatibility, executed CI, and physical install/launch evidence where claimed.

The current publication contract is in `fdroid/publication.manifest.json` and the canonical Android reference is `project/hydra/samsung/android/apk/app.reference.json`.

## Release path

```text
feature / bounded work branch
          │
          ▼
      PR + CI
          │
          ▼
     luhmos-main
          │
          ▼
 public-beta candidate
          │
          ├── exact-head tests / provenance
          ├── persistent release signer
          ├── immutable GitHub Release artifact
          ├── device install + launcher proof
          └── same-signer update proof where required
          │
          ▼
 external distribution / IzzyOnDroid
```

The existing public-release and Izzy workflows intentionally fail safe and do not publish by themselves. Publication requires a separately reviewed publisher path with explicit Crown authorization and verified signing/provenance inputs.

## LuHm magic automation

The Final Fantasy-inspired command vocabulary is a typed automation language, not a shell language:

```text
LIBRA   read-only inspection
SCAN    deeper audit
CURE    smallest hotfix
CURA    bounded patch
CURAGA  full mutation, human approval required
ESUNA   hardening / cleanup
METEO   stage reviewed GREEN work into testing + CI
ULTIMA  invoke a verified compile forge on an explicit GREEN ref
PHOENIX rollback to an explicitly named sealed GREEN target
```

No spell overrides branch gates, CI, signing requirements, safety boundaries, or human approval.

## Definition of GREEN

GREEN is evidence, not mood lighting.

Depending on the lane, that means tests actually ran, builds completed, artifacts exist, package identity was checked, signing identity was verified, hashes/provenance were recorded, provider state was actually exercised, physical-device claims were physically proven, and the relevant policy gates passed.

A compile-GREEN artifact is not automatically install GREEN. Source-contract GREEN is not live-provider GREEN. Historical exact-head proof is not a fresh run for a later head.

## Contributing and support

- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `SECURITY.md`
- `SUPPORT.md`
- `ARCHITECTURE.md`
- `AGENTS.md`

For public-beta feedback, include the exact commit/ref, platform, reproduction steps, and sanitized evidence. Never post secrets or signing material publicly.

## Source of truth

The current crowned source-of-truth lane is under `project/hydra/source-of-truth/`.

The current identity/vendor/pipeline crown is `LUHM_OS_PIPELINE_UNIFICATION_CROWN_20260921.json` on `luhmos-main`. Beta-candidate promotion remains subject to PR/CI and release evidence.

## Development principle

> **AI proposes. Policy authorizes. CI proves. The human promotes.**

That is the center of LuHm OS.

## Copyright and licensing

Copyright © 2026 Eggie Bagelface in copyrightable original LuHm OS material, subject to `COPYRIGHT.md`.

This repository is multi-license by component. Material governed by the root `LICENSE` remains under that license; third-party material remains under its own license; separately owned branding, artwork, characters, and specifically marked material retain their applicable terms. Existing open-source rights are not revoked or narrowed.

See `COPYRIGHT.md`, `LICENSE`, and `release/LUHM_OS_PUBLIC_BETA_NOTICE.txt` for the controlling notices relevant to the beta candidate.
