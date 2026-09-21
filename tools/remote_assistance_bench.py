#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "ultima" / "ollama-ffmpeg-antenna-v3"
if str(RUNTIME) not in sys.path:
    sys.path.insert(0, str(RUNTIME))

assistance = importlib.import_module("assistance")

ITERATIONS = 5000
P95_BUDGET_MS = 2.0


def main() -> int:
    original = assistance._configured
    assistance._configured = lambda: {
        "openai": True,
        "google": True,
        "huggingface": True,
        "github": True,
    }
    timings: list[float] = []
    tasks = ("direct", "build", "research", "audit")
    try:
        for index in range(ITERATIONS):
            task = tasks[index % len(tasks)]
            started = time.perf_counter_ns()
            plan = assistance._plan(task, "auto", critic=(task == "audit"))
            assistance._github_context([
                "eggie-admin/hydra-shell-android@deadbeef:integrations/vendor-apis.manifest.json"
            ])
            elapsed_ms = (time.perf_counter_ns() - started) / 1_000_000
            timings.append(elapsed_ms)
            if len(plan["calls"]) > assistance.MAX_PARALLEL:
                raise SystemExit("REMOTE_ASSISTANCE_BENCH_RED: parallelism escaped budget")
    finally:
        assistance._configured = original

    ordered = sorted(timings)
    p50 = statistics.median(ordered)
    p95 = ordered[max(0, int(len(ordered) * 0.95) - 1)]
    p99 = ordered[max(0, int(len(ordered) * 0.99) - 1)]
    report = {
        "schema": "luhm-os.remote-assistance-dispatch-bench.v1",
        "iterations": ITERATIONS,
        "scope": "local routing_plus_github_reference_validation_only",
        "provider_network_latency_included": False,
        "p50_ms": round(p50, 4),
        "p95_ms": round(p95, 4),
        "p99_ms": round(p99, 4),
        "p95_budget_ms": P95_BUDGET_MS,
        "status": "GREEN" if p95 <= P95_BUDGET_MS else "RED",
    }
    Path("luhmos-remote-assistance-bench.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "GREEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
