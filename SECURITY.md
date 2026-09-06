# Security Policy

## Scope
This policy covers LuHm OS / KAI 9000 Samsung Android testing code, local services, build workflows, manifests, and generated APK artifacts.

## Supported security lane
Current supported development lane:
`testing/luhm-os-android`

Testing artifacts are debug-signed and are not production releases.

## Report privately
Do not open a public issue containing:
- API keys or tokens;
- signing material;
- private user data;
- exploitable device details;
- credentials or recovery secrets.

Use GitHub's private security-reporting feature when available for the repository. If it is not available, contact the repository owner through a private channel rather than publishing secrets.

## Hard invariants
- local AI/control services bind to loopback by default;
- Secure Folder is a client/cockpit, not daemon owner;
- no automatic root;
- no arbitrary model-authored shell execution;
- privilege actions are typed and scoped;
- OpenAI credentials stay server-side;
- Base64 is never treated as encryption;
- release signing material is never committed;
- proprietary extracted game runtime assets are not bundled;
- external hosting statuses have no Android security/build authority.

## Build security
The testing workflow uses an ephemeral debug keystore created inside CI. Production signing requires a separate reviewed release process.

APK GREEN requires signature verification, package identity, SHA-256, 16 KiB alignment, architecture evidence, and executed CI.

## Dependency changes
Toolchain, donor, model, or third-party library upgrades are security-sensitive dependency promotions. Pin versions/revisions and record provenance.
