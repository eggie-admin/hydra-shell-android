# Google AI Edge Gallery deployment-help lane

Status: **PROPOSED / LOCAL TEST ONLY**

Google AI Edge Gallery is used here as a separate on-device evaluation sandbox for model and skill experiments. It is not the LuHm OS production runtime, source of truth, release channel, or public deployment target.

## Why this lane exists

The goal is to answer one practical question with evidence: for a narrow task, is a local Android model fast and capable enough to remove a remote round trip?

Use the Gallery lane for:

- local/offline model trials;
- model management and benchmark comparison;
- read-only helper-skill prototypes;
- latency and memory measurements;
- validating candidate on-device task classes before any direct LuHm runtime integration.

Do not use it to bypass Project Hydra authority, APK signing, Android install confirmation, or the bounded mutation gateway.

## Deployment help

For current Project Hydra doctrine, "deploy to Edge Gallery" means **prepare and test a local model/skill inside the separate Gallery app or compatible local harness**. It does not mean publish LuHm OS or upload user data to Google.

Recommended test sequence:

1. Install the official Google AI Edge Gallery application through its supported channel.
2. Choose an upstream-supported model or manually import an approved local model artifact when the Gallery version supports it.
3. Keep the first benchmark task tiny and deterministic enough to compare against the existing LuHm fast route.
4. Record exact device/profile, model identity/hash, runtime, task class, startup/TTFT, decode throughput, memory if available, and thermal note.
5. Save the result as a read-only evaluation receipt.
6. Only propose direct LuHm on-device integration if the measured result is useful and the model/runtime license and hardware behavior are acceptable.

## Fast-system routing doctrine

Use the lowest-cost/lowest-latency lane that still satisfies correctness and evidence requirements:

```text
deterministic local code
  -> bounded on-device helper
  -> fast OpenAI parent route
  -> deep OpenAI route
```

On-device is not automatically faster. Model load time, memory pressure, thermal throttling, prompt length, and device accelerator support can dominate. Measure before promoting.

## Security and authority

- Google AI Edge Gallery has no source-of-truth authority.
- A Gallery skill or model cannot approve a mutation.
- No direct AI-to-shell path.
- No silent install.
- No public publish.
- No secrets in model assets, skills, examples, or benchmark receipts.
- No automatic upload of private prompts or files.
- Historical and upstream code remain external references unless explicitly reviewed and promoted.

## Upstream references

Primary upstream project: `google-ai-edge/gallery`.

Current upstream documentation describes the Gallery as an experimental on-device AI application with local model execution, LiteRT, model management/benchmarking, agent skills, and Hugging Face integration. Treat those capabilities as upstream facts, not LuHm runtime proof.
