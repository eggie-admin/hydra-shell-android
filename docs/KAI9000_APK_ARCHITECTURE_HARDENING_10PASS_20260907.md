# KAI 9000 Private APK Architecture Hardening: 10 Pass

Date: 2026-09-07
Branch: `testing/luhm-os-android`

## Passes

1. **Authority boundary**: ordinary Termux remains daemon/control-plane owner; Samsung Secure Folder/AcodeX remains cockpit/client only.
2. **CI least privilege**: APK workflow token permission remains `contents: read`; no deploy/write permission is required for building.
3. **Supply-chain provenance**: Samsung donor is consumed by full commit SHA. Godot editor/templates and the Android Gradle distribution are checksum verified before execution.
4. **Action immutability target**: all reusable GitHub Actions in the APK workflow must be pinned to full commit SHAs before release promotion. Mutable major-version tags are testing-only debt.
5. **Secret isolation**: release keys, private keys, API keys, OAuth material and provider credential files are forbidden from source/APK assets. `.secrets/`, keystores and common private-key formats must remain ignored.
6. **Android component boundary**: widget/control receiver must be non-exported; external apps must not be able to invoke KAI control verbs.
7. **Network boundary**: cleartext is denied globally; testing-only cleartext is restricted to loopback. Public/provider traffic must use HTTPS/TLS.
8. **WebView boundary**: app file/content access and third-party cookies are disabled; appassets origin is authoritative. Testing currently requires loopback mixed-content compatibility and must migrate to typed native proxy or localhost TLS before release.
9. **Artifact proof**: green requires package identity, signature verification, SHA-256, ARM64 library presence, bundled CMS evidence, 16 KiB zip alignment, Python/tests and Samsung architecture sanity.
10. **Promotion separation**: debug signing is ephemeral; testing never auto-promotes. Release requires persistent protected signing identity, device validation, secret scan and explicit reviewed promotion.

## Status semantics

`TESTING_GREEN` means reproducible debug APK plus all testing gates. It is not a production-signing or publication claim.

`RELEASE_GREEN` additionally requires a private/restricted source-of-truth repository, immutable Actions, persistent protected release signing, device validation, and removal of stale external hosting checks from required status authority.
