---
name: google-ai-edge-gallery
description: Use for bounded Google AI Edge Gallery model benchmarking, local helper-skill experiments, and evidence handoff into Project Hydra without granting runtime or mutation authority.
---

# Google AI Edge Gallery Evaluation

Use this Skill only for the experimental on-device evaluation lane. Google AI Edge Gallery is a separate sandbox and benchmark harness, not a LuHm OS source donor, production dependency, or authority surface.

## Fast evaluation loop

1. Resolve the exact crowned Project Hydra source state and current Professor scope.
2. Define one bounded task class such as short classification, rewrite, extraction, summarization, or local image prompt analysis.
3. Record the exact device/profile, model name, model file hash when available, runtime/backend, and task input shape.
4. Run the task locally in Google AI Edge Gallery.
5. Capture comparable latency evidence such as TTFT/startup latency, decode throughput, peak memory when available, and a thermal-state note.
6. Compare against the current LuHm fast route only with equivalent inputs and success criteria.
7. Return a compact JSON receipt to parent Lum. Do not mutate canonical source from this Skill.

## Acceptance receipt

```json
{
  "lane": "GOOGLE_AI_EDGE_GALLERY",
  "authority": "READ_ONLY_EVALUATION",
  "device_profile": "...",
  "model": "...",
  "model_sha256": "...",
  "runtime": "...",
  "task_class": "...",
  "metrics": {
    "startup_or_ttft_ms": null,
    "decode_tokens_per_second": null,
    "peak_memory_mb": null,
    "thermal_note": "..."
  },
  "baseline": "...",
  "result": "FASTER|SLOWER|INCONCLUSIVE|FUNCTIONAL_ONLY",
  "promotion": "NONE"
}
```

## Hard boundaries

- No shell execution or privileged Android actions.
- No self-approval, signing, install automation, release, public publishing, billing, DNS, or crown authority.
- No API keys, private account tokens, signing secrets, or sensitive user data in model assets, skills, logs, or receipts.
- Do not claim a speedup without comparable measurements.
- Do not copy upstream Gallery application code into LuHm OS merely to accelerate integration.
- If LuHm later integrates LiteRT or another on-device runtime directly, that is a separate implementation proposal with its own CI and physical-device proof.
