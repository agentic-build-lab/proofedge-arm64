"""Aggregate product-task evidence without overstating benchmark scope."""

from __future__ import annotations

import json
import re
import statistics
from pathlib import Path
from typing import Any

_MODEL_SIZE_PATTERN = re.compile(r"\s(\d+) bytes\s*$")
_RSS_PATTERN = re.compile(r"Maximum resident set size \(kbytes\):\s+(\d+)")
_CPU_PATTERN = re.compile(r"Percent of CPU this job got:\s+(\d+)%")
_ELAPSED_PATTERN = re.compile(r"Elapsed \(wall clock\) time \(h:mm:ss or m:ss\):\s+([0-9:.]+)")


def _percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, round((len(ordered) - 1) * fraction)))
    return ordered[index]


def _describe(values: list[float]) -> dict[str, float | int]:
    return {
        "n": len(values),
        "mean": statistics.fmean(values),
        "p50": statistics.median(values),
        "p95": _percentile(values, 0.95),
        "min": min(values),
        "max": max(values),
    }


def _load_quality(path: Path) -> dict[str, Any]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict) or not isinstance(document.get("cases"), list):
        raise ValueError(f"Expected a model-evaluation ledger in {path}")
    if not document.get("passed"):
        raise ValueError(f"Quality gate did not pass in {path}")
    return document


def _case_map(document: dict[str, Any]) -> dict[str, dict[str, Any]]:
    cases: dict[str, dict[str, Any]] = {}
    for case in document["cases"]:
        case_id = case.get("case_id")
        if not isinstance(case_id, str) or case_id in cases:
            raise ValueError("Case identifiers must be unique strings")
        cases[case_id] = case
    return cases


def compare_quality_ledgers(baseline_path: Path, kleidiai_path: Path) -> dict[str, Any]:
    """Compare native product-task timings only when the workload and outputs match."""

    baseline_document = _load_quality(baseline_path)
    kleidiai_document = _load_quality(kleidiai_path)
    baseline_cases = _case_map(baseline_document)
    kleidiai_cases = _case_map(kleidiai_document)
    if baseline_cases.keys() != kleidiai_cases.keys():
        raise ValueError("Baseline and KleidiAI ledgers do not contain the same cases")

    per_case: list[dict[str, Any]] = []
    model_compute_ms = {"baseline": [], "kleidiai": []}
    prompt_tokens = {"baseline": 0, "kleidiai": 0}
    completion_tokens = {"baseline": 0, "kleidiai": 0}
    prompt_ms = {"baseline": 0.0, "kleidiai": 0.0}
    generation_ms = {"baseline": 0.0, "kleidiai": 0.0}

    for case_id in sorted(baseline_cases):
        baseline = baseline_cases[case_id]
        kleidiai = kleidiai_cases[case_id]
        matching_fields = {
            "context_sha256": baseline.get("context_sha256") == kleidiai.get("context_sha256"),
            "prompt_tokens": baseline["usage"]["prompt_tokens"]
            == kleidiai["usage"]["prompt_tokens"],
            "completion_tokens": baseline["usage"]["completion_tokens"]
            == kleidiai["usage"]["completion_tokens"],
            "response_sha256": baseline.get("response_sha256") == kleidiai.get("response_sha256"),
        }
        if not all(matching_fields.values()):
            raise ValueError(f"Workload or output mismatch for {case_id}: {matching_fields}")
        if not baseline.get("passed") or not kleidiai.get("passed"):
            raise ValueError(f"Case quality gate did not pass for {case_id}")

        baseline_total = float(baseline["timings"]["prompt_ms"]) + float(
            baseline["timings"]["predicted_ms"]
        )
        kleidiai_total = float(kleidiai["timings"]["prompt_ms"]) + float(
            kleidiai["timings"]["predicted_ms"]
        )
        model_compute_ms["baseline"].append(baseline_total)
        model_compute_ms["kleidiai"].append(kleidiai_total)

        for label, case in (("baseline", baseline), ("kleidiai", kleidiai)):
            prompt_tokens[label] += int(case["usage"]["prompt_tokens"])
            completion_tokens[label] += int(case["usage"]["completion_tokens"])
            prompt_ms[label] += float(case["timings"]["prompt_ms"])
            generation_ms[label] += float(case["timings"]["predicted_ms"])

        per_case.append(
            {
                "case_id": case_id,
                "baseline_model_compute_ms": baseline_total,
                "kleidiai_model_compute_ms": kleidiai_total,
                "model_compute_latency_change_percent": (kleidiai_total / baseline_total - 1) * 100,
                "prompt_tokens": baseline["usage"]["prompt_tokens"],
                "completion_tokens": baseline["usage"]["completion_tokens"],
                "response_sha256": baseline["response_sha256"],
                "byte_identical_response": True,
                "quality_gate_passed": True,
            }
        )

    baseline_total_ms = sum(model_compute_ms["baseline"])
    kleidiai_total_ms = sum(model_compute_ms["kleidiai"])
    return {
        "scope": "llama-server model compute inside complete frozen ProofEdge quality requests",
        "cases": per_case,
        "model_compute_latency_ms": {
            "baseline": _describe(model_compute_ms["baseline"]),
            "kleidiai": _describe(model_compute_ms["kleidiai"]),
            "aggregate_change_percent": (kleidiai_total_ms / baseline_total_ms - 1) * 100,
        },
        "weighted_throughput_tokens_per_second": {
            "prompt_processing": {
                "baseline": prompt_tokens["baseline"] / (prompt_ms["baseline"] / 1000),
                "kleidiai": prompt_tokens["kleidiai"] / (prompt_ms["kleidiai"] / 1000),
            },
            "token_generation": {
                "baseline": completion_tokens["baseline"] / (generation_ms["baseline"] / 1000),
                "kleidiai": completion_tokens["kleidiai"] / (generation_ms["kleidiai"] / 1000),
            },
        },
        "workload_identity": {
            "same_case_ids": True,
            "same_context_hashes": True,
            "same_prompt_token_counts": True,
            "same_completion_token_counts": True,
            "byte_identical_responses": True,
        },
        "quality_gate": {
            "baseline_passed": True,
            "kleidiai_passed": True,
            "cases_per_configuration": len(per_case),
        },
    }


def _parse_elapsed_seconds(value: str) -> float:
    pieces = [float(piece) for piece in value.split(":")]
    if len(pieces) == 2:
        return pieces[0] * 60 + pieces[1]
    if len(pieces) == 3:
        return pieces[0] * 3600 + pieces[1] * 60 + pieces[2]
    raise ValueError(f"Unsupported elapsed time: {value}")


def parse_process_measurements(paths: list[Path]) -> dict[str, Any]:
    rss: list[float] = []
    cpu: list[float] = []
    elapsed: list[float] = []
    for path in paths:
        content = path.read_text(encoding="utf-8")
        rss_match = _RSS_PATTERN.search(content)
        cpu_match = _CPU_PATTERN.search(content)
        elapsed_match = _ELAPSED_PATTERN.search(content)
        if not rss_match or not cpu_match or not elapsed_match:
            raise ValueError(f"Incomplete /usr/bin/time evidence in {path}")
        rss.append(float(rss_match.group(1)))
        cpu.append(float(cpu_match.group(1)))
        elapsed.append(_parse_elapsed_seconds(elapsed_match.group(1)))
    return {
        "processes": len(paths),
        "peak_rss_kib": _describe(rss),
        "cpu_utilization_percent": _describe(cpu),
        "elapsed_seconds": _describe(elapsed),
    }


def analyze_native_evidence(evidence_dir: Path) -> dict[str, Any]:
    quality_dir = evidence_dir / "quality"
    raw_dir = evidence_dir / "raw"
    product = compare_quality_ledgers(
        quality_dir / "baseline-optimized.json",
        quality_dir / "kleidiai-optimized.json",
    )
    model_match = _MODEL_SIZE_PATTERN.search(
        (evidence_dir / "model-size.txt").read_text(encoding="utf-8")
    )
    if not model_match:
        raise ValueError("Could not parse model-size.txt")

    product["runtime_process_measurements"] = {
        label: parse_process_measurements(sorted(raw_dir.glob(f"*-{label}-time.txt")))
        for label in ("baseline", "kleidiai")
    }
    product["model"] = {
        "size_bytes": int(model_match.group(1)),
        "quantization": "Q4_0",
    }
    product["explicitly_unmeasured"] = {
        "time_to_first_token": (
            "Not observed: the safety-gated ProofEdge client uses non-streaming responses."
        ),
        "full_product_end_to_end_latency": (
            "Not claimed for the local-model path: server timings exclude scanning, HTTP, "
            "validation, and report rendering."
        ),
        "server_startup_time": "Not timestamped in this confirmation run.",
        "energy_or_power": (
            "Not measured because the hosted VM exposes no calibrated power telemetry."
        ),
    }
    product["limitations"] = [
        "Only one response per frozen case and configuration was captured; per-case latency is "
        "descriptive rather than a repeated-trial estimate.",
        "The two-case quality corpus is intentionally small and is not a claim of broad "
        "migration accuracy.",
        "Runtime process resource measurements come from llama-bench, not the full product path.",
    ]
    return product
