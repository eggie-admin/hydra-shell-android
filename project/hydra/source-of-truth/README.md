# Source of Truth

This directory is the **crowned GitHub seal lane** for **LuHm OS**. The stable repository path remains `project/hydra/source-of-truth` for compatibility and historical lineage; that path does not make Project Hydra the current product identity.

GitHub owns software lineage, source, CI, and provenance. Owner-only Google Drive holds private recovery/source-of-truth documentation and staged private artifacts.

## Current crowns

Architecture/pipeline authority: `LUHM_OS_PIPELINE_UNIFICATION_CROWN_20260921.json`

Forward release floor / no-backtrack authority: `LUHM_OS_GOLDEN_BETA_NO_BACKTRACK_CROWN_20260922.json`

The release-floor crown does not replace the architecture crown. Together they define the current LuHm OS source contract: the 2026-09-21 crown defines identity, vendor/API pipeline, authority, privilege, and evidence boundaries; the 2026-09-22 crown freezes the first real public Android beta as the minimum forward release baseline.

- Canonical product name: **LuHm OS**
- Established internal project identifier: `luhm_os`
- Golden public beta: **1.0.10-beta.1**, Android versionCode **110**.
- Golden beta source: `luhmos/beta` at `a2243d68fa1aaa2f554ef74d9a1edd32530c12ac`.
- Next Android release versionCode must be **greater than 110**.
- Package lineage remains `art.eggiebagelface.luhmos` with the crowned release signer unless a separately crowned migration explicitly proves a safe Android upgrade path.
- `v1.0.10-beta.1` source and release assets are frozen; fixes ship as a new version rather than rewriting the golden beta.
- One logical project spans the OpenAI, Google, GitHub, Cloudflare, and Hugging Face transport bindings.
- OpenAI organization: **Pirate Daddy Film**
- Canonical OpenAI project: **LuHm OS**
- Legacy OpenAI **Project Hydra**: compatibility only; do not target it for new keys or new work.
- GitHub source binding: `eggie-admin/hydra-shell-android`, canonical branch `luhmos-main`.
- Google Drive human-facing project root: **LuHm OS**.
- Cloudflare public zone: `eggiebagelface.art`.
- Hugging Face account binding: `eggiebagelface`.
- KAI 9000: donor/reference/archaeology only; not current runtime authority, dependency authority, product name, or naming authority.
- Project Hydra: historical compatibility/repository lineage only.
- Vue is retired from the active Android release dependency chain.

## Naming doctrine

**VOWEL_RIP is a coding convention, not a product/platform naming law.**

It may be used for shortened internal Python3 identifiers, Python3 helper/stub names, and coding-doctrine artifact IDs when shortening is useful.

It does **not** rename LuHm OS, API project labels, organizations, Google Drive roots, GitHub owners/repos/branches, FQDNs/DNS zones, public release names, human-facing service names, or vendor transport identifiers.

The earlier `LUHM_OS_UNIFIED_NAMING_CANON_CROWN_20260921.json` is superseded because it incorrectly expanded VOWEL_RIP beyond the coding/stub scope.

## Vendor/API pipeline seal

The current crown preserves the already-proven pipeline contract rather than replacing it:

- `integrations/vendor-apis.manifest.json`
- `docs/API_TRINITY_DOCTRINE.md`
- `tools/vendor_api_pipeline_audit.py`
- `.github/workflows/luhmos-vendor-api-pipeline-audit.yml`

Historical proof receipts preserved by reference:

- `LUHM_OS_VENDOR_API_PIPELINE_SYNC_20260917.json`: source pipeline GREEN with `17/17` exact-head internal CI.
- `LUHM_OS_UNIFIED_PROJECT_20260917.json`: unified-project and vendor-pipeline guards GREEN with `18/18` exact-head internal CI.
- `LUHM_OS_SOURCE_OF_TRUTH_AUDIT_20260918.json`: LuHm OS identity and vendor bindings reconciled while keeping external provider debt explicit.

Historical CI proof remains historical evidence. A source-of-truth crown does not invent a fresh CI run or silently promote unverified live-provider state to GREEN.

## Golden beta release floor

The first real public Android beta is a permanent forward-only checkpoint:

- Version: `1.0.10-beta.1`
- versionCode: `110`
- Package: `art.eggiebagelface.luhmos`
- Source SHA: `a2243d68fa1aaa2f554ef74d9a1edd32530c12ac`
- Source tree: `fb6d8154c995666a42c01797ab6ebf03758a91df`
- APK SHA-256: `b4e162c41aacdf16d58c051b3251fc07306ffb3de6a057b9aecd6ea8f36f3754`
- Release tag: `v1.0.10-beta.1`

No later cleanup may silently regress product identity, package identity, signer continuity, versionCode, release evidence, exact-tree promotion, canonical Android forge ownership, or the KAI/Hydra/Vue retirement boundaries.

Human API cleanup starts **after** this checkpoint and must move forward from it. A universal APK is a possible next release direction, but it is not crowned yet and must use a new version above versionCode 110.

## Authority and privilege

- Professor is final human authority.
- Lum is Boss.
- Oni helpers are bounded, cannot recursively recruit, and cannot self-approve.
- Consequential actions remain Crown-gated.
- Normal admin is the default operating identity.
- Root is never a persistent login or agent identity.
- Privilege escalation is one exact Crown-approved operation for the minimum required duration, followed by immediate return to normal admin.
- Operator-facing doctrine uses names rather than literal network addresses.

## Crown rule

A file is authoritative here only when its own status/seal declares it crowned or sealed and it has not been superseded by a later applicable crown. Directory placement alone does not grant authority.

Proposals belong under:

`project/hydra/doctrine/proposed-source-of-truth/`

A proposed manifest has **zero automatic promotion authority**. It must never overwrite or impersonate a crowned seal.

## Evidence boundaries

- Source-contract GREEN is not fresh runtime GREEN.
- Historical exact-head CI proof remains valid historical evidence but is not a fresh run for a later head.
- Build/CI GREEN is not release authority.
- Release/build proof is not physical-device GREEN.
- Fresh physical evidence owns exact hardware/runtime claims.
- Historical cryptographic receipts remain historical evidence and are not rewritten during doctrine cleanup.
- External provider, DNS, repository, billing, deploy, signing, install, or release changes must not be inferred from a source-contract crown.
- Public beta GREEN does not mean stable GREEN; physical-device install/launch and upgrade proof remain separately required for stable.

Do not place serial numbers, IMEI/MEID, phone numbers, account identifiers, API keys, signing material, private keys, or private third-party payloads here.
