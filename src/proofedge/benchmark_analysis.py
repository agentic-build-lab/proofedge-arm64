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
_VM_HWM_PATTERN = re.compile(r"^VmHWM:\s+(\d+)\s+kB$", re.MULTILINE)
_VM_RSS_PATTERN = re.compile(r"^VmRSS:\s+(\d+)\s+kB$", re.MULTILINE)


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
    """Compare model compute only when the raw token workload matches exactly."""

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
    exact_workload = True

    for case_id in sorted(baseline_cases):
        baseline = baseline_cases[case_id]
        kleidiai = kleidiai_cases[case_id]
        matching_fields = {
            "context_sha256": baseline.get("context_sha256") == kleidiai.get("context_sha256"),
            "prompt_tokens": baseline["usage"]["prompt_tokens"]
            == kleidiai["usage"]["prompt_tokens"],
            "completion_tokens": baseline["usage"]["completion_tokens"]
            == kleidiai["usage"]["completion_tokens"],
            "published_response_sha256": baseline.get("response_sha256")
            == kleidiai.get("response_sha256"),
            "raw_response_sha256": baseline.get(
                "raw_response_sha256", baseline.get("response_sha256")
            )
            == kleidiai.get("raw_response_sha256", kleidiai.get("response_sha256")),
        }
        if not baseline.get("passed") or not kleidiai.get("passed"):
            raise ValueError(f"Case quality gate did not pass for {case_id}")
        case_exact = all(matching_fields.values())
        exact_workload = exact_workload and case_exact

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

        case_result: dict[str, Any] = {
            "case_id": case_id,
            "matching_fields": matching_fields,
            "baseline_prompt_tokens": baseline["usage"]["prompt_tokens"],
            "kleidiai_prompt_tokens": kleidiai["usage"]["prompt_tokens"],
            "baseline_completion_tokens": baseline["usage"]["completion_tokens"],
            "kleidiai_completion_tokens": kleidiai["usage"]["completion_tokens"],
            "published_response_sha256": baseline["response_sha256"],
            "quality_gate_passed": True,
            "model_compute_comparison_eligible": case_exact,
        }
        if case_exact:
            case_result.update(
                {
                    "baseline_model_compute_ms": baseline_total,
                    "kleidiai_model_compute_ms": kleidiai_total,
                    "model_compute_latency_change_percent": (kleidiai_total / baseline_total - 1)
                    * 100,
                }
            )
        per_case.append(case_result)

    baseline_total_ms = sum(model_compute_ms["baseline"])
    kleidiai_total_ms = sum(model_compute_ms["kleidiai"])
    result: dict[str, Any] = {
        "scope": "llama-server model compute inside complete frozen ProofEdge quality requests",
        "cases": per_case,
        "model_compute_comparison_eligible": exact_workload,
        "workload_identity": {
            "same_case_ids": True,
            "all_exact_workload_fields_match": exact_workload,
        },
        "quality_gate": {
            "baseline_passed": True,
            "kleidiai_passed": True,
            "cases_per_configuration": len(per_case),
        },
    }
    if exact_workload:
        result["model_compute_latency_ms"] = {
            "baseline": _describe(model_compute_ms["baseline"]),
            "kleidiai": _describe(model_compute_ms["kleidiai"]),
            "aggregate_change_percent": (kleidiai_total_ms / baseline_total_ms - 1) * 100,
        }
        result["weighted_throughput_tokens_per_second"] = {
            "prompt_processing": {
                "baseline": prompt_tokens["baseline"] / (prompt_ms["baseline"] / 1000),
                "kleidiai": prompt_tokens["kleidiai"] / (prompt_ms["kleidiai"] / 1000),
            },
            "token_generation": {
                "baseline": completion_tokens["baseline"] / (generation_ms["baseline"] / 1000),
                "kleidiai": completion_tokens["kleidiai"] / (generation_ms["kleidiai"] / 1000),
            },
        }
    else:
        result["model_compute_comparison_exclusion_reason"] = (
            "Raw model responses or token counts differed across configurations; model compute "
            "timings are retained in the case ledgers but are not compared as an identical "
            "workload."
        )
    return result


def compare_product_benchmarks(baseline_path: Path, kleidiai_path: Path) -> dict[str, Any]:
    """Compare repeated complete product tasks with workload and quality controls."""
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    kleidiai = json.loads(kleidiai_path.read_text(encoding="utf-8"))
    for label, document in (("baseline", baseline), ("kleidiai", kleidiai)):
        if not isinstance(document, dict) or not document.get("passed"):
            raise ValueError(f"{label} repeated product benchmark did not pass")
        if document.get("repetitions", 0) < 3:
            raise ValueError(f"{label} product benchmark has too few repetitions")
        identity = document.get("workload_identity", {})
        if not identity.get("context_hashes_stable"):
            raise ValueError(f"{label} context hashes changed between product runs")
    if baseline["profile"] != kleidiai["profile"]:
        raise ValueError("Product benchmark profiles do not match")
    baseline_hashes = baseline["workload_identity"]["response_hashes_per_case"]
    kleidiai_hashes = kleidiai["workload_identity"]["response_hashes_per_case"]
    if baseline_hashes != kleidiai_hashes:
        raise ValueError("Product benchmark responses differ between configurations")
    baseline_raw_hashes = baseline["workload_identity"].get("raw_response_hashes_per_case")
    kleidiai_raw_hashes = kleidiai["workload_identity"].get("raw_response_hashes_per_case")
    raw_responses_identical = (
        baseline_raw_hashes == kleidiai_raw_hashes
        if baseline_raw_hashes is not None and kleidiai_raw_hashes is not None
        else None
    )

    metrics: dict[str, Any] = {}
    for key in (
        "task_end_to_end_ms",
        "request_time_to_first_token_ms",
        "request_end_to_end_ms",
    ):
        baseline_metric = baseline[key]
        kleidiai_metric = kleidiai[key]
        metrics[key] = {
            "baseline": baseline_metric,
            "kleidiai": kleidiai_metric,
            "mean_change_percent": (kleidiai_metric["mean"] / baseline_metric["mean"] - 1) * 100,
            "p50_change_percent": (kleidiai_metric["p50"] / baseline_metric["p50"] - 1) * 100,
            "p95_change_percent": (kleidiai_metric["p95"] / baseline_metric["p95"] - 1) * 100,
        }
    return {
        "scope": baseline["scope"],
        "profile": baseline["profile"],
        "quality_gate": {
            "baseline_all_runs_passed": True,
            "kleidiai_all_runs_passed": True,
            "baseline_runs": baseline["repetitions"],
            "kleidiai_runs": kleidiai["repetitions"],
        },
        "workload_identity": {
            "contexts_stable": True,
            "published_responses_identical_across_configurations": True,
            "published_response_hashes_per_case": baseline_hashes,
            "raw_model_responses_identical_across_configurations": raw_responses_identical,
            "baseline_raw_model_response_hashes_per_case": baseline_raw_hashes,
            "kleidiai_raw_model_response_hashes_per_case": kleidiai_raw_hashes,
        },
        "attribution": (
            "TTFT compares the same prompts before response divergence. End-to-end task changes "
            "are descriptive product observations, not an isolated kernel effect, when raw model "
            "responses differ."
        ),
        **metrics,
    }


def parse_startup_measurements(path: Path) -> dict[str, float | int]:
    values: list[float] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        document = json.loads(line)
        value = document.get("startup_ms")
        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError(f"Invalid startup measurement in {path}")
        values.append(float(value))
    if len(values) < 3:
        raise ValueError(f"Expected at least three startup measurements in {path}")
    return _describe(values)


def parse_server_process_measurements(status_path: Path, ps_path: Path) -> dict[str, Any]:
    status = status_path.read_text(encoding="utf-8")
    high_water = _VM_HWM_PATTERN.search(status)
    resident = _VM_RSS_PATTERN.search(status)
    if not high_water or not resident:
        raise ValueError(f"Incomplete server /proc status evidence in {status_path}")
    ps_lines = [line for line in ps_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(ps_lines) != 2:
        raise ValueError(f"Expected one server process row in {ps_path}")
    fields = ps_lines[1].split()
    if len(fields) < 8:
        raise ValueError(f"Incomplete server ps evidence in {ps_path}")
    return {
        "peak_rss_kib": int(high_water.group(1)),
        "rss_at_capture_kib": int(resident.group(1)),
        "elapsed_seconds_at_capture": int(fields[1]),
        "cpu_time_at_capture": fields[2],
        "average_cpu_utilization_percent_at_capture": float(fields[3]),
        "ps_rss_kib": int(fields[5]),
        "ps_vsz_kib": int(fields[6]),
        "process": fields[7],
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
    baseline_product = quality_dir / "baseline-product.json"
    kleidiai_product = quality_dir / "kleidiai-product.json"
    if baseline_product.exists() and kleidiai_product.exists():
        product["repeated_product_task"] = compare_product_benchmarks(
            baseline_product,
            kleidiai_product,
        )
        product["server_startup_ms"] = {
            label: parse_startup_measurements(quality_dir / f"{label}-startup.jsonl")
            for label in ("baseline", "kleidiai")
        }
        product["product_resource_measurements"] = {
            label: {
                "server": parse_server_process_measurements(
                    quality_dir / f"{label}-server-proc-status.txt",
                    quality_dir / f"{label}-server-ps.txt",
                ),
                "client": parse_process_measurements(
                    [quality_dir / f"{label}-product-client-time.txt"]
                ),
            }
            for label in ("baseline", "kleidiai")
        }
        product["explicitly_unmeasured"] = {
            "energy_or_power": (
                "Not measured because the hosted VM exposes no calibrated power telemetry."
            ),
            "whole_system_peak_rss": (
                "Server and client were separate processes; server and client resource records "
                "are published separately rather than summed into a false instantaneous peak."
            ),
        }
        product["limitations"] = [
            "The fixed quality corpus has two deliberately compact migration cases.",
            "Five repeated task trials support descriptive p50/p95, not population inference.",
            "Startup has three observed trials per configuration on one hosted Arm64 VM.",
            "Raw model output identity is reported separately from compiled published-plan "
            "identity.",
        ]
        return product
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
