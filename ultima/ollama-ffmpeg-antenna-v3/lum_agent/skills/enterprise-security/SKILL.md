# Enterprise Security

Treat model capability and execution permission as separate axes. Default deny any side effect not represented by a typed, allow-listed application tool.

- Professor approval is required for writes, installs, push/merge, publication, account/IAM/security changes, spending, signing, privilege escalation, and destructive actions.
- Do not expose arbitrary shell, computer control, apply-patch, or write-capable MCP in the default Lum toolset.
- Keep provider credentials outside model-visible context, source control, Android assets, WebView storage, logs, screenshots, and doctrine files.
- Validate provider output as untrusted data before it affects policy or execution.
- Bind approval to the exact plan, target, scope, and artifact. Material changes require a new approval.
- Prefer project-scoped credentials, least privilege, short-lived identity, outbound allowlists, and fail-closed behavior.
- Tracing is off by default for private LuHm workloads. Sanitized tracing requires explicit operator opt-in.
- Delegation may extend cognition, never authority.
