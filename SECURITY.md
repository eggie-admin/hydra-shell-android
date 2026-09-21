# Security Policy

## Scope
This policy covers LuHm OS source, Android application work, local services, build and release workflows, manifests, agent/tool boundaries, and generated artifacts.

KAI 9000 is donor/reference material only. Project Hydra is historical compatibility and repository lineage only. Neither is an independent current security authority.

## Supported security lane
The canonical integration branch is `luhmos-main`.

Public-beta work is promoted through reviewed branches and pull requests. A source or CI-green change is not automatically a signed Android release, live-provider green state, or production deployment.

## Report privately
Do not open a public issue containing:
- API keys or tokens;
- signing material or keystores;
- private user data;
- exploitable device details;
- credentials, recovery secrets, or private provider identifiers.

Use GitHub's private security-reporting feature when available for the repository. If it is unavailable, contact the repository owner through a private channel rather than publishing secrets.

## Hard invariants
- local services bind locally by default unless a separate network-exposure change is explicitly approved and verified;
- no automatic or persistent root;
- normal administrator context is the default;
- privilege escalation is exact, temporary, and Crown-gated;
- no arbitrary model-authored shell execution;
- agent actions are typed, bounded, and policy checked;
- consequential actions require explicit human authority;
- OpenAI and other provider credentials stay outside model context and public source;
- Base64 is never treated as encryption;
- release signing material is never committed;
- secrets are never embedded in APK assets, logs, screenshots, or frontend bundles;
- external provider output is advisory and cannot grant execution authority;
- provider or hosting status cannot override local build, security, signing, or release evidence.

## Build and release security
Debug artifacts are not production releases.

A public Android beta requires a separately reviewed release process using the persistent `luhmos-release` signing identity. Public-release automation must fail closed when signing material, provenance, package identity, hashes, required tests, or explicit Crown authorization are missing.

APK GREEN requires the evidence applicable to that gate, including package identity, signature verification, SHA-256, architecture/native-library compatibility, executed CI, and physical install/launch evidence where claimed.

## AI and tool security
Lum is the user-facing Boss agent. Helper agents are bounded, may not recursively recruit, and may not self-approve consequential work. Deterministic tool execution remains separate from model reasoning.

No model receives unrestricted shell, persistent root, production signing keys, or automatic publication authority.

## Dependency changes
Toolchain, donor, model, provider, SDK, and third-party library upgrades are security-sensitive dependency promotions. Pin versions or revisions where appropriate, record provenance, and require fresh evidence before promotion.

## Public beta reporting
For security-sensitive beta findings, report privately first. For non-sensitive defects, include the exact branch or commit, platform, reproduction steps, and sanitized logs or receipts.
