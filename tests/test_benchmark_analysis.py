from __future__ import annotations

import json
from pathlib import Path

import pytest

from proofedge.benchmark_analysis import (
    compare_product_benchmarks,
    compare_quality_ledgers,
    parse_process_measurements,
    parse_server_process_measurements,
    parse_startup_measurements,
)


def _write_ledger(path: Path, prompt_ms: float, generation_ms: float, response_hash: str) -> None:
    path.write_text(
        json.dumps(
            {
                "passed": True,
                "cases": [
                    {
                        "case_id": "case-a",
                        "passed": True,
                        "context_sha256": "context-hash",
                        "response_sha256": response_hash,
                        "usage": {"prompt_tokens": 100, "completion_tokens": 20},
                        "timings": {"prompt_ms": prompt_ms, "predicted_ms": generation_ms},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def test_compare_quality_ledgers_requires_identical_outputs(tmp_path: Path) -> None:
    baseline = tmp_path / "baseline.json"
    kleidiai = tmp_path / "kleidiai.json"
    _write_ledger(baseline, 1000, 1000, "same")
    _write_ledger(kleidiai, 900, 900, "different")

    with pytest.raises(ValueError, match="Workload or output mismatch"):
        compare_quality_ledgers(baseline, kleidiai)


def test_compare_quality_ledgers_reports_latency_and_throughput(tmp_path: Path) -> None:
    baseline = tmp_path / "baseline.json"
    kleidiai = tmp_path / "kleidiai.json"
    _write_ledger(baseline, 1000, 1000, "same")
    _write_ledger(kleidiai, 900, 900, "same")

    result = compare_quality_ledgers(baseline, kleidiai)

    assert result["model_compute_latency_ms"]["aggregate_change_percent"] == pytest.approx(-10)
    assert result["weighted_throughput_tokens_per_second"]["prompt_processing"][
        "kleidiai"
    ] == pytest.approx(111.111111)
    assert result["workload_identity"]["byte_identical_responses"] is True


def test_parse_process_measurements(tmp_path: Path) -> None:
    evidence = tmp_path / "time.txt"
    evidence.write_text(
        "Percent of CPU this job got: 387%\n"
        "Elapsed (wall clock) time (h:mm:ss or m:ss): 1:49.44\n"
        "Maximum resident set size (kbytes): 2012040\n",
        encoding="utf-8",
    )

    result = parse_process_measurements([evidence])

    assert result["cpu_utilization_percent"]["mean"] == 387
    assert result["elapsed_seconds"]["mean"] == pytest.approx(109.44)
    assert result["peak_rss_kib"]["mean"] == 2012040


def _write_product(path: Path, scale: float) -> None:
    metric = {"n": 5, "mean": 100 * scale, "p50": 100 * scale, "p95": 110 * scale}
    path.write_text(
        json.dumps(
            {
                "passed": True,
                "profile": "optimized",
                "scope": "complete task",
                "repetitions": 5,
                "task_end_to_end_ms": metric,
                "request_time_to_first_token_ms": metric,
                "request_end_to_end_ms": metric,
                "workload_identity": {
                    "context_hashes_stable": True,
                    "response_hashes_per_case": {"case-a": ["same"]},
                },
            }
        ),
        encoding="utf-8",
    )


def test_compare_product_benchmarks_requires_identical_quality_outputs(tmp_path: Path) -> None:
    baseline = tmp_path / "baseline.json"
    kleidiai = tmp_path / "kleidiai.json"
    _write_product(baseline, 1.0)
    _write_product(kleidiai, 0.9)

    result = compare_product_benchmarks(baseline, kleidiai)

    assert result["task_end_to_end_ms"]["mean_change_percent"] == pytest.approx(-10)
    assert result["workload_identity"]["responses_identical_across_configurations"] is True


def test_parse_startup_measurements(tmp_path: Path) -> None:
    startup = tmp_path / "startup.jsonl"
    startup.write_text(
        '{"trial":1,"startup_ms":1000}\n'
        '{"trial":2,"startup_ms":900}\n'
        '{"trial":3,"startup_ms":1100}\n',
        encoding="utf-8",
    )

    result = parse_startup_measurements(startup)

    assert result["n"] == 3
    assert result["p50"] == 1000
    assert result["p95"] == 1100


def test_parse_server_process_measurements(tmp_path: Path) -> None:
    status = tmp_path / "status.txt"
    ps = tmp_path / "ps.txt"
    status.write_text("VmHWM:\t2012040 kB\nVmRSS:\t1999000 kB\n", encoding="utf-8")
    ps.write_text(
        "    PID ELAPSED     TIME %CPU %MEM   RSS    VSZ COMMAND\n"
        "   1234     180 00:02:58  98.5 12.3 1999000 2200000 llama-server\n",
        encoding="utf-8",
    )

    result = parse_server_process_measurements(status, ps)

    assert result["peak_rss_kib"] == 2012040
    assert result["average_cpu_utilization_percent_at_capture"] == 98.5
    assert result["process"] == "llama-server"
