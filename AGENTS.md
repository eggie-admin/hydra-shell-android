# AGENTS.md

This repository is the LuHm OS / KAI 9000 Samsung Android orchestration altar.

## Read first
- `project/hydra/source-of-truth/KAI9000_CROWN_CATHEDRAL_FOUNDATION_SEAL_20260918.json`
- `project/hydra/source-of-truth/LUHM_CODING_ROLEPLAY_THWTCHNGHR_GREEN_RECONCILIATION_20260918.json`
- `project/hydra/source-of-truth/KAI9000_FULL_DOCTRINE_MUTATION_SEAL_20260917.json`
- `project/hydra/source-of-truth/KAI9000_SEAL_OF_TRUTH_CROWN_20260917.json`
- `project/hydra/source-of-truth/LUHMOS_HYDRA_DIRECTORY_CROWN_20260916.json`
- `project/hydra/source-of-truth/LUHM_M1_SIGNED_SECURE_WEBVIEW_SOCKET_20260916.json`
- `project/hydra/doctrine/directory-structure.json`
- `project/hydra/project.manifest.json`
- `project/hydra/runtime/performance.policy.json` when present on the current candidate/source branch
- `.github/copilot-instructions.md`
- The exact workflow, manifest, and tests for the lane being changed

Legacy trees such as `lumh-os/kai9000/**`, `ultima/**`, ULTIMA-named workflows/scripts/docs, and retired editor-bridge material remain compatibility/history unless a current crowned contract explicitly re-promotes them. Their presence does not make them active authority.

## Current authority and lane
- `luhmos-main` is the canonical integration branch.
- Work on short-lived `luhmos/*` branches and merge only after executed evidence plus explicit current Professor authorization.
- Professor is final human authority for consequential actions.
- Lum is crown planner, source-of-truth keeper, critic, and evidence gate. Lum never invents GREEN.
- GitHub Actions is compile/build authority. Fresh physical device behavior is device-proof authority.
- Google Drive is private recovery/source-of-truth documentation and private artifact staging, not Git source control.
- Resolve conflicts in this order: exact current Professor instruction, fresh physical/runtime proof when applicable, newest applicable crowned source-of-truth contract, Project Hydra directory/project manifests, these agent instructions plus the exact lane workflow, proposed doctrine, then legacy/history.

## Fast-path law
Speed means less repeated work, not fewer proof or authority gates.

- Resolve authority once per exact repository/branch/head and carry compact `path@sha` references forward.
- Reuse immutable Git evidence. Refresh mutable branch, PR, Drive-revision, runtime, and device state immediately before a mutation or claim that depends on it.
- Deterministic local validation comes before remote AI when it can answer the question completely.
- Default helper count is zero. Use at most two parallel helpers, and only for independent read/search work.
- Delegation depth is at most one. Helpers do not delegate to helpers.
- Keep one Lum parent and one serialized write sequence. Never race competing writes.
- Do not race providers or duplicate model calls to manufacture confidence.
- Use the fast OpenAI route for ordinary classification, structured transforms, source triage, small coding assistance, and proof summaries. Escalate to the deep route only when complexity materially warrants it.
- Run the smallest relevant deterministic/focused test first, then exact-head CI for claims that require repository-wide evidence.
- Base Android launch and first render must remain network-independent. Cloud AI, ADMIN surfaces, and optional helpers are lazy/on-demand.
- One verified proof payload may render as JSON, scriptless HTML, and chat-safe text. Do not recompute or duplicate large evidence bodies when a hash or immutable ID is sufficient.
- A performance improvement is `PROPOSED_NOT_PROVEN_FASTER` until measured against a comparable baseline on the relevant runner/device.
- Never weaken Crown Law, provenance, signing continuity, secret handling, physical-device proof, or required CI merely to reduce latency.

Machine enforcement lives in `project/hydra/runtime/performance.policy.json` and `tools/project_hydra_fastpath_guard.py` when those candidate files are present.

## Android release identity
- App: `LuHm OS`
- Package: `art.eggiebagelface.luhmos`
- ABI: `arm64-v8a`
- minSdk: `24`
- targetSdk: `36`
- Release updates require the persistent LuHm signer and a strictly increasing versionCode.
- Android package-install confirmation remains required. No silent install and no automatic root.
- Forge/donor/reference pins are lane-specific provenance inputs only. Never treat a historical donor pin as global release authority.

## Operating rules
- Preserve current behavior unless the task explicitly requests a breaking mutation.
- Prefer small, reversible patches and deterministic tests.
- Never claim GREEN without executed evidence.
- Never place secrets, signing material, private tokens, model weights, voice recordings, or proprietary game assets in the repository or APK.
- Keep local Android services loopback-only unless a later crowned contract explicitly changes the boundary.
- Samsung Secure Folder is a protected cockpit/client boundary where used, not automatic daemon/build authority.
- Retired Acode/AcodeX/AXS/VNC/WebSocket/8767 bridge evidence is historical compatibility proof, not a current required runtime/editor/admin dependency.
- Public publishing is manual-only. A push to `luhmos-main` must never publish a public APK or F-Droid mirror by itself.
- Third-party/community assets remain quarantined until provenance and redistribution rights are explicit.
- `POWER LEVEL != PERMISSION LEVEL` is absolute.

## Lum agent contract
Lum/OpenAI may inspect, reason, draft, test, and propose. It may not self-authorize publication, installs, account changes, secret handling, spending, privilege escalation, destructive operations, canonical merge, signing, or release promotion.

Canonical tiers:
- `WHISPER / GREEN`: read-only inspect/research/explain/provenance.
- `CROSSING / AMBER`: reversible staging with origin, delta, rollback, lineage, and proof.
- `RECKONING / RED`: real mutation. Exact current Professor authorization is required.

For coding work use:

`DOCTRINE -> INSPECT -> OUTLINE/READ -> DEBUG -> COMPILE/TEST -> PROPOSE -> HUMAN APPROVAL -> EXECUTION EVIDENCE`

## Fast verification order
1. Resolve the newest applicable crowned contract, exact current source ref, and performance policy if the branch contains one.
2. `python tools/project_hydra_fastpath_guard.py` when present.
3. `python tools/project_hydra_structure_guard.py`.
4. `python tools/kai9000_ci_guard.py`.
5. Run the exact current focused tests/workflow for the lane being changed. Do not route new verification through `ultima/**` merely because legacy tests still exist.
6. When runtime environment state matters, run the read-only `sh tools/hydra-sanity-audit.sh` and review its report before mutation.
7. Require exact-head GitHub Actions evidence for build/signature/alignment or other lane-specific candidate claims.
8. For APK claims, bind source commit, workflow/run ID, artifact ID/hash, APK hash, and signer fingerprint.
9. For hardware/runtime completion, require fresh human-observed physical install/update/launch proof. CI cannot close device gates.

## Agent roles
- Copilot: implementation, repair, tests, documentation.
- Lum/OpenAI: crown planner, typed tool-request layer, source-of-truth/evidence gate.
- Ollama: optional local inference fallback.
- Python 3: policy/orchestration/test layer.
- GitHub Actions: deterministic compile/build evidence oracle.
- Professor: final authority.
