# Ubuntu / Debian lane

Status: STAGED DUMMY REPOSITORY CONTRACT

Future scope: Ubuntu and Debian desktop/server packaging.

Planned boundary:
- Python 3 control plane is the preferred shared runtime
- Debian packaging, system integration, desktop entry, service units, sandboxing, permissions, update behavior, and GPU/media dependencies stay Linux-specific
- no claim of a buildable `.deb` package yet
- no repository signing private keys in Git

Promotion requirement: add a real Debian package definition, supported distro matrix, CI package build, lint/install tests, repository-signing plan, rollback notes, and artifact evidence before leaving `luhmos/testing`.
