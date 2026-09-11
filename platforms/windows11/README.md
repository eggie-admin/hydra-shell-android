# Windows 11 lane

Status: STAGED DUMMY REPOSITORY CONTRACT

Future scope: Windows 11 desktop shell/distribution work.

Planned boundary:
- shared Python 3 control plane and API contracts
- native Windows packaging, lifecycle, permissions, code signing, installer/update behavior, and GPU/media integration stay Windows-specific
- no claim of a buildable MSIX/installer project yet
- no code-signing private keys in Git

Promotion requirement: add a real Windows project, CI build, signing strategy, supported Windows build matrix, installer/update tests, and artifact evidence before leaving `luhmos/testing`.
