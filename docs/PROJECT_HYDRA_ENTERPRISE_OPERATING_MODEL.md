# Project Hydra Enterprise Operating Model

Status: **CROWNED SOURCE GOVERNANCE / ENTERPRISE FULL-GREEN GATES STILL OPEN**

This is an enterprise-style operating target for Project Hydra. It is not a compliance certification or regulatory attestation.

## Goal

Operate LuHm OS / Project Hydra as a controlled product system with fast feedback, immutable evidence, deterministic promotion, bounded AI authority, recoverability, and clear separation between proposal, canonical source, release candidate, and public production states.

## Operating sequence

```text
WHISPER: inspect / benchmark / audit
  ↓
CROSSING: proposal branch + draft PR + focused tests
  ↓
EXACT-HEAD CI + immutable evidence
  ↓
HUMAN PROMOTION
  ↓
CANONICAL SOURCE
  ↓
RELEASE-CANDIDATE BUILD ONCE
  ↓
SBOM + PROVENANCE + HASH + SIGNER + DEVICE PROOF
  ↓
SEPARATE HUMAN RELEASE GATE
```

No helper, model consensus, workflow, or document grants promotion authority.

## Enterprise controls

### Source governance

- `luhmos-main` remains canonical.
- Enterprise GREEN requires server-side branch protection/ruleset, exact-head required checks, and verified merge provenance.
- CODEOWNERS is repository evidence, not a substitute for server-side enforcement.
- Direct canonical writes, force pushes, and history rewrites are off by default.

### Supply chain

- Pin external Actions and toolchains to immutable versions or SHAs where practical.
- Verify downloaded tool hashes where a trusted digest is available.
- Release candidates require SHA-256, package identity, signer fingerprint, SBOM, provenance receipt, and immutable source SHA.
- Build once, then promote the same digest. Rebuilding after approval creates a new candidate.

### Runtime and performance

- Base launch must remain network-independent.
- Cloud AI and admin surfaces are lazy and degradable.
- Performance claims require equivalent-input measurements on the relevant runner/device.
- Mobile benchmark receipts include startup/TTFT where applicable, throughput where applicable, memory, and thermal notes.
- No speed optimization may remove security, provenance, physical proof, or required CI.

### AI governance

- Lum Fast is the default parent route.
- Helpers are read/search only unless an explicit current scope says otherwise.
- No AI self-approval, no AI-to-shell, and no consensus-created authority.
- Retrieved content is untrusted input until reconciled against Crowned source-of-truth.

### Secrets and identity

- No secrets in Git, APK assets, HTML, chat receipts, or logs.
- Prefer OIDC or short-lived platform identity over long-lived cloud credentials.
- Persistent APK signing remains a separate authority and must not be inferred from build success.

### Observability and recovery

- Use bounded structured events, correlation IDs, secret redaction, and hash-addressed evidence.
- Consequential mutations preserve preimage/checkpoint and have a rollback path.
- Enterprise GREEN requires evidence of a backup/restore drill, not merely a backup claim.

## Current known gaps

At Crown promotion, no repository ruleset was observed for canonical `luhmos-main`; branch-protection visibility remains limited by integration permissions. Runtime benchmark proof, final-candidate SBOM/provenance binding, backup/restore drill evidence, and persistent release signing remain open gates.

## Promotion boundary

This proposal authorizes no canonical merge, Crown mutation, persistent signing, APK install, public publish, deployment, DNS mutation, or billing mutation. Those remain separate Professor-controlled gates.
