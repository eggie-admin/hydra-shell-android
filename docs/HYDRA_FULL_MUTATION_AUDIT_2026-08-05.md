# Hydra Samsung Secure Folder Kiosk

## Full Mutation Architecture Audit

**Date:** 2026-08-05  
**Status:** AMBER / GREEN_WITH_GATES  
**Authority:** Professor remains final authority.

## Executive finding

The repository is not yet a complete kiosk or agent runtime. It is an early Android shell probe with one Termux-specific Shizuku installer. The correct mutation path is to preserve the public repository as presentation and bootstrap code while keeping credentials, durable memory, privileged execution, and provider routing outside the web root and outside the public repository.

## Current-state findings

1. The current README identifies an early Knox-aware shell probe, not a bundled Linux runtime or production kiosk.
2. The current installer hardcodes Termux paths and package commands. It does not match the current Acode Alpine / BusyBox environment.
3. Shizuku installation is fetched from the latest GitHub release without checksum or signer verification.
4. The installer calls `adb install -r` after listing devices but does not require exactly one authorized target.
5. There is no kiosk application manifest, service worker, CSP, origin allowlist, bridge authentication, health check, audit log, rollback procedure, or release pipeline.
6. The repository is public. No secrets, personal memory, private doctrine, tokens, or privileged runtime configuration belong here.

## Required architecture

```text
Samsung Secure Folder
  WebView/PWA kiosk shell
        |
        | HTTPS loopback only
        v
  Hydra API boundary
        |
        +-- approval gate
        +-- model router
        +-- audit logger
        +-- GitHub adapter
        +-- local Ollama adapter
        +-- optional OpenAI adapter
        +-- scoped Shizuku adapter

External services and privileged Android operations are never called directly from browser JavaScript.
```

## Trust boundaries

### Presentation boundary

The kiosk UI may render status, submit requests, display diffs, and collect explicit approvals. It may not hold provider keys or invoke ADB, Shizuku, package installation, GitHub writes, publishing, deployment, or filesystem mutation directly.

### API boundary

All state-changing requests must include:

- authenticated local session
- explicit operation identifier
- declared capability
- preview or diff
- Professor approval token
- expiration
- append-only audit record

### Privilege boundary

Shizuku and ADB are adapters of last resort. Every command must be allowlisted, parameter validated, logged without secrets, and reversible where practical. No arbitrary shell bridge is permitted from the WebView.

## Mutation milestone gates

### Gate A: Reproducible operator environment

- Detect Acode Alpine, Termux, and unsupported shells.
- Refuse to use Termux paths in Alpine.
- Report Android profile/user ID and Secure Folder context.
- Confirm loopback networking and writable private workspace.
- Export a redacted diagnostic seal.

### Gate B: Hardened kiosk shell

- Mobile-first 9:16 layout with large touch targets.
- PWA manifest and offline shell.
- Strict Content Security Policy.
- No remote JavaScript execution.
- Explicit origin allowlist.
- Full-screen mode remains optional and reversible.
- Visible connection, model, approval, and privilege state.

### Gate C: Hydra API boundary

- Bind to `127.0.0.1` only by default.
- Browser communicates only with the Hydra API.
- CSRF-resistant session or signed local request protocol.
- Typed request schemas and response validation.
- Rate limits, timeouts, cancellation, and health endpoints.
- Secrets loaded from a private environment file outside the web root.

### Gate D: Lum orchestrator

- Persona instructions are separate from authority policy.
- Durable memory is explicit, audited, and editable.
- Capability does not equal authority.
- Read and draft actions may be automatic.
- Write, publish, merge, deploy, credentials, network exposure, and privileged Android actions require explicit approval.
- No agent may approve its own action.

### Gate E: Provider routing

- Local Ollama remains the default private provider.
- OpenAI is an optional adapter behind the API boundary.
- Keys never enter browser storage, source control, screenshots, logs, or chat transcripts.
- Per-provider budgets and kill switches are required.

### Gate F: Release and rollback

- Draft pull request required for mutation changes.
- CI performs shell linting, secret scanning, dependency checks, and static web security checks.
- Signed release artifacts and checksums.
- Documented uninstall and rollback.
- Main branch merge remains a Professor-approved action.

## Immediate blockers

- No actual kiosk source is present in this repository.
- No current device diagnostic bundle was supplied for this audit.
- No private runtime repository or encrypted configuration location is identified.
- The existing Shizuku installer is unsafe for unattended automation until provenance verification and exact-target checks are added.
- A public repository cannot be the canonical home for full personal doctrine or durable Lum memory.

## Recommended repository split

```text
hydra-shell-android       public kiosk/bootstrap, no secrets
hydra-runtime             private API, adapters, approvals, audit policy
hydra-doctrine-private    private canonical doctrine and character bible
hydra-deploy-private      private device-specific configuration and seals
```

## Green definition

The kiosk reaches FULL MUTATION only when all gates A through F pass on the actual Secure Folder device, the runtime is loopback-only, the browser holds no secrets, privileged commands are allowlisted, the audit log is working, rollback is tested, and Professor performs the final merge and activation approval.

Until then, the honest state is **GREEN_WITH_GATES**, not unrestricted green.
