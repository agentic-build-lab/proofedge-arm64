#!/usr/bin/env python3
"""Aggregate complete llama-bench ABBA blocks without cherry-picking."""

from __future__ import annotations

import argparse
import json
import random
import re
import statistics
from pathlib import Path
from typing import Any

RSS_PATTERN = re.compile(r"Maximum resident set size \(kbytes\):\s+(\d+)")


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, round((len(ordered) - 1) * fraction)))
    return ordered[index]


def bootstrap_delta(
    baseline: list[float], optimized: list[float], samples: int, seed: int
) -> tuple[float, float]:
    rng = random.Random(seed)  # noqa: S311 - deterministic statistical resampling
    deltas: list[float] = []
    for _ in range(samples):
        baseline_draw = [rng.choice(baseline) for _ in baseline]
        optimized_draw = [rng.choice(optimized) for _ in optimized]
        deltas.append(
            (statistics.fmean(optimized_draw) / statistics.fmean(baseline_draw) - 1) * 100
        )
    return percentile(deltas, 0.025), percentile(deltas, 0.975)


def describe(values: list[float]) -> dict[str, float | int]:
    mean = statistics.fmean(values)
    return {
        "n": len(values),
        "mean": mean,
        "p50": statistics.median(values),
        "p95": percentile(values, 0.95),
        "min": min(values),
        "max": max(values),
        "coefficient_of_variation": statistics.pstdev(values) / mean,
    }


def _load_blocks(raw_dir: Path) -> list[tuple[str, str, list[dict[str, Any]]]]:
    blocks: list[tuple[str, str, list[dict[str, Any]]]] = []
    for path in sorted(raw_dir.glob("*.json")):
        configuration = "kleidiai" if "kleidiai" in path.stem else "baseline"
        rows = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(rows, list) or len(rows) != 2:
            raise ValueError(f"Expected prefill and decode rows in {path}")
        blocks.append((path.stem.split("-", 1)[0], configuration, rows))
    if [configuration for _, configuration, _ in blocks] != [
        "baseline",
        "kleidiai",
        "kleidiai",
        "baseline",
    ]:
        raise ValueError("Raw inputs do not form the required ABBA block order")
    return blocks


def analyze(raw_dir: Path, bootstrap_samples: int = 20_000) -> dict[str, Any]:
    blocks = _load_blocks(raw_dir)
    metrics: dict[str, Any] = {}
    for metric, selector in (
        ("prompt_processing_tokens_per_second", lambda row: row["n_prompt"] > 0),
        ("token_generation_tokens_per_second", lambda row: row["n_gen"] > 0),
    ):
        values = {"baseline": [], "kleidiai": []}
        block_means: list[dict[str, Any]] = []
        for block, configuration, rows in blocks:
            row = next(row for row in rows if selector(row))
            samples = [float(value) for value in row["samples_ts"]]
            values[configuration].extend(samples)
            block_means.append(
                {
                    "block": block,
                    "configuration": configuration,
                    "mean": statistics.fmean(samples),
                }
            )
        baseline_mean = statistics.fmean(values["baseline"])
        optimized_mean = statistics.fmean(values["kleidiai"])
        lower, upper = bootstrap_delta(
            values["baseline"], values["kleidiai"], bootstrap_samples, 424242
        )
        metrics[metric] = {
            "baseline": describe(values["baseline"]),
            "kleidiai": describe(values["kleidiai"]),
            "relative_mean_change_percent": (optimized_mean / baseline_mean - 1) * 100,
            "exploratory_sample_bootstrap_95ci_percent": [lower, upper],
            "block_means": block_means,
        }

    rss = {"baseline": [], "kleidiai": []}
    for path in sorted(raw_dir.glob("*-time.txt")):
        configuration = "kleidiai" if "kleidiai" in path.stem else "baseline"
        match = RSS_PATTERN.search(path.read_text(encoding="utf-8"))
        if match:
            rss[configuration].append(int(match.group(1)))
    prompt_change = metrics["prompt_processing_tokens_per_second"]["relative_mean_change_percent"]
    generation_change = metrics["token_generation_tokens_per_second"][
        "relative_mean_change_percent"
    ]
    both_positive = prompt_change > 0 and generation_change > 0
    status = "positive_runtime_result" if both_positive else "mixed_negative_result"
    claim = (
        f"KleidiAI changed mean prompt-processing throughput by {prompt_change:+.3f}% and "
        f"mean token-generation throughput by {generation_change:+.3f}% in this fixed "
        "same-host configuration."
    )
    return {
        "schema_version": "1.0.0",
        "benchmark": "same-host-llama-cpp-kleidiai-abba",
        "complete_blocks": 4,
        "block_order": [configuration for _, configuration, _ in blocks],
        "metrics": metrics,
        "peak_rss_kib_by_process": rss,
        "interpretation": {
            "status": status,
            "claim": claim,
            "quality_scope": (
                "This benchmark does not establish output-quality equivalence. Apply the "
                "separate frozen model-quality gate before making a product claim."
            ),
        },
        "limitations": [
            "The exploratory bootstrap treats within-process repetitions as samples; it is "
            "not a confidence interval across independent VMs.",
            "Only one native Neoverse-N2 VM and one thread/batch configuration were measured.",
            "llama-bench excludes tokenization and sampling and is not an end-to-end "
            "application benchmark.",
            "Energy was not measured because the cloud VM exposes no calibrated power telemetry.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--bootstrap-samples", type=int, default=20_000)
    args = parser.parse_args()
    result = analyze(args.raw_dir, args.bootstrap_samples)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(result["metrics"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
