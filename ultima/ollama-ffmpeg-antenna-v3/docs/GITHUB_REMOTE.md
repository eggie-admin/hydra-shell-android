# GitHub Remote Doctrine

Repository: `eggie-admin/hydra-shell-android`

Canonical branch: `main`

Recommended remote behavior:

```bash
git fetch --prune origin main
git pull --ff-only origin main
```

Do not:
- force-pull over local changes;
- store API keys or tokens in Git;
- use GitHub as a command-and-control shell;
- expose Ollama directly to the public Internet.

GitHub is the remote spellbook. Ollama and FFmpeg remain local runtime services.
