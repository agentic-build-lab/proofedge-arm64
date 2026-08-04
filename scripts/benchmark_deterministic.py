#!/usr/bin/env python3
"""Record repeatable application-pipeline timings without claiming model inference."""

from __future__ import annotations

import argparse
import json
import os
import platform
import resource
import statistics
import time
from pathlib import Path

from proofedge.evaluation import evaluate_cases


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int((len(ordered) * fraction) + 0.999999) - 1))
    return ordered[index]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, default=Path("evaluation/cases"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--runs", type=int, default=20)
    args = parser.parse_args()
    if args.runs < 5:
        parser.error("--runs must be at least 5")

    trials: list[dict[str, float | int]] = []
    for run in range(args.runs):
        started = time.perf_counter_ns()
        result = evaluate_cases(args.cases)
        elapsed_ms = (time.perf_counter_ns() - started) / 1_000_000
        trials.append(
            {
                "run": run + 1,
                "latency_ms": elapsed_ms,
                "cases_passed": result.cases_passed,
                "cases_total": result.cases_total,
                "category_recall": result.category_recall,
            }
        )
    latencies = [float(trial["latency_ms"]) for trial in trials]
    max_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    document = {
        "schema_version": "1.0.0",
        "benchmark": "deterministic-pipeline",
        "disclosure": "This measures static ProofEdge processing, not LLM inference.",
        "environment": {
            "architecture": platform.machine(),
            "platform": platform.platform(),
            "python": platform.python_version(),
            "cpu_count": os.cpu_count(),
            "github_run_id": os.environ.get("GITHUB_RUN_ID"),
            "github_sha": os.environ.get("GITHUB_SHA"),
        },
        "configuration": {"runs": args.runs, "cases": str(args.cases)},
        "summary": {
            "cold_latency_ms": latencies[0],
            "warm_p50_latency_ms": statistics.median(latencies[1:]),
            "warm_p95_latency_ms": percentile(latencies[1:], 0.95),
            "mean_latency_ms": statistics.fmean(latencies),
            "peak_rss_kib": max_rss,
            "task_success_rate": sum(
                int(trial["cases_passed"]) / int(trial["cases_total"]) for trial in trials
            )
            / len(trials),
        },
        "trials": trials,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(document, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(document["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
