from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from proofedge.product_benchmark import benchmark_local_model_tasks, describe


@dataclass(frozen=True)
class _Case:
    case_id: str
    passed: bool
    context_sha256: str
    response_sha256: str
    client_timings: dict[str, object]


@dataclass(frozen=True)
class _Result:
    passed: bool
    cases: tuple[_Case, ...]


def test_describe_reports_observed_nearest_rank_percentiles() -> None:
    result = describe([5.0, 1.0, 3.0, 2.0, 4.0])

    assert result == {"n": 5, "mean": 3.0, "p50": 3.0, "p95": 5.0, "min": 1.0, "max": 5.0}


def test_product_benchmark_requires_quality_gated_streams(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = 0

    def fake_evaluate(_cases: Path, _client: object, profile: str) -> _Result:
        nonlocal calls
        calls += 1
        assert profile == "optimized"
        return _Result(
            passed=True,
            cases=(
                _Case(
                    case_id="case-a",
                    passed=True,
                    context_sha256="context",
                    response_sha256="response",
                    client_timings={
                        "streaming": True,
                        "time_to_first_token_ms": 10.0 + calls,
                        "end_to_end_ms": 20.0 + calls,
                    },
                ),
            ),
        )

    monkeypatch.setattr("proofedge.product_benchmark.evaluate_local_model", fake_evaluate)
    result = benchmark_local_model_tasks(Path("cases"), object(), "optimized", 3)  # type: ignore[arg-type]

    assert result["passed"] is True
    assert result["quality"]["successful_runs"] == 3
    assert result["request_time_to_first_token_ms"]["p50"] == 12.0
    assert result["workload_identity"]["context_hashes_stable"] is True
    assert result["workload_identity"]["unique_response_counts"] == {"case-a": 1}


@pytest.mark.parametrize("repetitions", [0, 2, 21])
def test_product_benchmark_bounds_repetitions(repetitions: int) -> None:
    with pytest.raises(ValueError, match="between 3 and 20"):
        benchmark_local_model_tasks(Path("cases"), object(), "optimized", repetitions)  # type: ignore[arg-type]
