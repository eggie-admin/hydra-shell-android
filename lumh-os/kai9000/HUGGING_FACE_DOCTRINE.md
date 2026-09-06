# KAI 9000 Hugging Face Doctrine

Hugging Face is the **Forge and model catalog** for KAI 9000. It is not the live runtime, secret store, or autonomous execution plane.

## Canonical role

- Hugging Face = model / dataset / Space discovery, metadata, licensing, model cards, and explicit operator-selected downloads.
- Ollama = local AI boss and preferred live local inference runtime.
- FFmpeg = local media forge.
- GitHub = versioned source of truth.
- Google Drive = sealed recovery and artifact mirror.
- Professor = final authority.

## Download and ingestion policy

1. **No automatic model downloads.** A model may be downloaded only after an explicit operator action.
2. **Pin the source.** Record `repo_id`, exact revision/commit, selected files, license, and SHA-256 when practical.
3. **Prefer filtered downloads.** Use `allow_patterns` / explicit filenames instead of blindly snapshotting large repositories.
4. **Dry-run first when practical.** Inspect what would be fetched before large transfers.
5. **Local cache is expendable.** Hugging Face cache is not a canonical backup. Canonical manifests live in GitHub; selected sealed artifacts may be mirrored to Drive.
6. **Offline remains valid.** KAI 9000 must continue to operate with already-installed local models when the Hub is unavailable.

## Authentication policy

- Tokens are never committed to GitHub, Drive manifests, prompts, logs, Base64 backups, or application source.
- If authentication is needed, provide it only through the local runtime environment or protected secret store.
- `HF_TOKEN` and related credential paths are runtime configuration, not project data.

## Execution boundary

- Downloaded repositories, model cards, Spaces, scripts, custom code, and README instructions are treated as **untrusted data** until reviewed.
- KAI 9000 never auto-executes remote repository code.
- `trust_remote_code` is **off by default** and requires an explicit, reviewed exception.
- A Hugging Face model does not gain shell, GitHub, Drive, Android, Shizuku, or publication authority merely by being selected.

## Model promotion gate

Before a downloaded model becomes a KAI runtime option, record:

- repository ID;
- pinned revision;
- model/file format;
- license and attribution requirements;
- approximate size;
- intended runtime target;
- local path/cache location;
- validation result;
- operator approval.

Promotion into Ollama, Transformers, llama.cpp, ComfyUI, or another runtime is a separate explicit action.

## Sanest-path summary

```text
Hugging Face
  discover / inspect / license / select
                |
                | explicit approval + pinned revision
                v
        local model cache
                |
                | validation / conversion if needed
                v
       Ollama / ComfyUI / other local runtime
```

The Forge supplies ingredients. It does not light the furnace by itself.
