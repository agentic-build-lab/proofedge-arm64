from __future__ import annotations

from pathlib import Path

from proofedge.evaluation import evaluate_cases


def test_frozen_golden_cases_pass() -> None:
    root = Path(__file__).parents[1] / "evaluation" / "cases"
    result = evaluate_cases(root)
    assert result.cases_total == 2
    assert result.cases_passed == 2
    assert result.category_recall == 1.0
    assert result.task_success_rate == 1.0
