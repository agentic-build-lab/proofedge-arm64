from __future__ import annotations

from pathlib import Path

from proofedge.engines import LlamaResponse
from proofedge.model_evaluation import evaluate_local_model

CASES = Path("evaluation/cases")


def _proposal(name: str, path: str, line: int) -> dict:
    return {
        "name": name,
        "purpose": "Compare the source and target boundary behavior",
        "repository": "source",
        "path": path,
        "line": line,
        "inputs": ["boundary"],
        "expected_relation": "investigate",
        "priority": "high",
    }


class PassingClient:
    def generate_plan(self, context: str) -> LlamaResponse:
        tests = (
            [_proposal("Orders success status", "openapi.json", 8)]
            if "openapi.json" in context
            else [
                _proposal("Quote rounding policy", "pricing.py", 5),
                _proposal("Refund reason preservation", "pricing.py", 8),
            ]
        )
        return LlamaResponse(
            document={"tests": tests, "limitations": ["Static proposal only"]},
            timings={"predicted_per_second": 12.5},
            usage={"total_tokens": 100},
        )


class HallucinatingClient:
    def generate_plan(self, _context: str) -> LlamaResponse:
        return LlamaResponse(
            document={
                "tests": [_proposal("Read a secret", "../../.ssh/id_rsa", 1)],
                "limitations": [],
            },
            timings={},
            usage={},
        )


def test_local_model_gate_uses_objective_matching() -> None:
    result = evaluate_local_model(
        CASES,
        PassingClient(),  # type: ignore[arg-type]
        "optimized",
    )

    assert result.passed is True
    assert result.cases_passed == 2
    assert result.objectives_matched == 3
    assert result.risk_evidence_coverage == 1.0
    assert result.raw_reference_validity == 1.0
    assert result.canary_leakage_count == 0


def test_local_model_gate_fails_hallucinated_references() -> None:
    result = evaluate_local_model(
        CASES,
        HallucinatingClient(),  # type: ignore[arg-type]
        "optimized",
    )

    assert result.passed is False
    assert result.cases_passed == 0
    assert result.accepted_proposals == 0
    assert result.rejected_proposals == 2
    assert result.fallback_count == 2
