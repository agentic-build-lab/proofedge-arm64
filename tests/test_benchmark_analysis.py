from __future__ import annotations

import json
from pathlib import Path

import pytest

from proofedge.benchmark_analysis import compare_quality_ledgers, parse_process_measurements


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
