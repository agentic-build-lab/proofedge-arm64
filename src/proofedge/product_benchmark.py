"""Repeated client-side measurements for the complete local-model quality task."""

from __future__ import annotations

import json
import statistics
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

from proofedge.engines import LlamaCppClient
from proofedge.model_evaluation import evaluate_local_model


def _percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, round((len(ordered) - 1) * fraction)))
    return ordered[index]


def describe(values: list[float]) -> dict[str, float | int]:
    if not values:
        raise ValueError("At least one measurement is required")
    return {
        "n": len(values),
        "mean": statistics.fmean(values),
        "p50": statistics.median(values),
        "p95": _percentile(values, 0.95),
        "min": min(values),
        "max": max(values),
    }


def benchmark_local_model_tasks(
    cases_root: Path,
    client: LlamaCppClient,
    profile: str,
    repetitions: int,
) -> dict[str, Any]:
    """Measure complete two-case evaluations with quality-gated streamed responses."""
    if repetitions < 3 or repetitions > 20:
        raise ValueError("repetitions must be between 3 and 20")

    task_latency_ms: list[float] = []
    ttft_ms: list[float] = []
    request_latency_ms: list[float] = []
    runs: list[dict[str, Any]] = []
    response_hashes: dict[str, set[str]] = {}
    raw_response_hashes: dict[str, set[str]] = {}
    context_hashes: dict[str, set[str]] = {}

    for repetition in range(1, repetitions + 1):
        started_ns = time.perf_counter_ns()
        result = evaluate_local_model(cases_root, client, profile)
        completed_ns = time.perf_counter_ns()
        elapsed_ms = (completed_ns - started_ns) / 1_000_000
        task_latency_ms.append(elapsed_ms)
        for case in result.cases:
            if not case.client_timings.get("streaming"):
                raise ValueError("Product benchmark requires streaming client measurements")
            ttft = case.client_timings.get("time_to_first_token_ms")
            request_latency = case.client_timings.get("end_to_end_ms")
            if not isinstance(ttft, (int, float)) or not isinstance(request_latency, (int, float)):
                raise ValueError("Product benchmark received incomplete client timings")
            ttft_ms.append(float(ttft))
            request_latency_ms.append(float(request_latency))
            if case.response_sha256 is not None:
                response_hashes.setdefault(case.case_id, set()).add(case.response_sha256)
            if case.raw_response_sha256 is not None:
                raw_response_hashes.setdefault(case.case_id, set()).add(case.raw_response_sha256)
            context_hashes.setdefault(case.case_id, set()).add(case.context_sha256)
        runs.append(
            {
                "repetition": repetition,
                "task_end_to_end_ms": elapsed_ms,
                "evaluation": asdict(result),
            }
        )

    all_passed = all(run["evaluation"]["passed"] for run in runs)
    return {
        "schema_version": "1.1.0",
        "scope": (
            "Complete ProofEdge local-model quality task over the frozen two-case corpus in a "
            "persistent Python process: bounded scans, context construction, streamed local "
            "inference, schema/citation/semantic gates, and ledger construction"
        ),
        "profile": profile,
        "repetitions": repetitions,
        "passed": all_passed,
        "task_end_to_end_ms": describe(task_latency_ms),
        "request_time_to_first_token_ms": describe(ttft_ms),
        "request_end_to_end_ms": describe(request_latency_ms),
        "quality": {
            "successful_runs": sum(run["evaluation"]["passed"] for run in runs),
            "total_runs": repetitions,
            "all_schema_and_semantic_gates_passed": all_passed,
        },
        "workload_identity": {
            "context_hashes_stable": all(len(values) == 1 for values in context_hashes.values()),
            "response_hashes_per_case": {
                case_id: sorted(values) for case_id, values in sorted(response_hashes.items())
            },
            "raw_response_hashes_per_case": {
                case_id: sorted(values) for case_id, values in sorted(raw_response_hashes.items())
            },
            "unique_response_counts": {
                case_id: len(values) for case_id, values in sorted(response_hashes.items())
            },
            "unique_raw_response_counts": {
                case_id: len(values) for case_id, values in sorted(raw_response_hashes.items())
            },
        },
        "runs": runs,
        "limitations": [
            "Task latency excludes Python interpreter startup and the final JSON file write.",
            (
                "TTFT is client-observed first non-empty streamed content, not a "
                "server-internal proxy."
            ),
            "Energy is not reported because the hosted runner exposes no calibrated power data.",
        ],
    }


def write_product_benchmark(result: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
