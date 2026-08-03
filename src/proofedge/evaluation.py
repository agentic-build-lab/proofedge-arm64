"""Golden-set evaluation established before inference optimization."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from proofedge.analyzer import AnalysisConfig, analyze_migration


@dataclass(frozen=True, slots=True)
class CaseEvaluation:
    case_id: str
    passed: bool
    expected_categories: tuple[str, ...]
    observed_categories: tuple[str, ...]
    missing_categories: tuple[str, ...]
    forbidden_categories_seen: tuple[str, ...]
    high_or_critical: int


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    schema_version: str
    engine: str
    cases_total: int
    cases_passed: int
    expected_categories: int
    matched_categories: int
    category_recall: float
    task_success_rate: float
    unsupported_claim_rate: float
    cases: tuple[CaseEvaluation, ...]


def evaluate_cases(cases_root: Path) -> EvaluationResult:
    evaluations: list[CaseEvaluation] = []
    total_expected = 0
    total_matched = 0
    unsupported = 0
    findings = 0
    golden_files = sorted(cases_root.glob("*/golden.json"))
    if not golden_files:
        raise ValueError(f"No golden cases found below {cases_root}")
    for golden_path in golden_files:
        case_dir = golden_path.parent
        golden = json.loads(golden_path.read_text(encoding="utf-8"))
        manifest = case_dir / "manifest.json"
        report = analyze_migration(
            AnalysisConfig(
                source=case_dir / "source",
                target=case_dir / "target",
                manifest=manifest if manifest.exists() else None,
            )
        )
        observed = {finding.category for finding in report.findings}
        expected = set(golden.get("expected_categories", []))
        forbidden = set(golden.get("forbidden_categories", []))
        missing = expected - observed
        forbidden_seen = forbidden & observed
        total_expected += len(expected)
        total_matched += len(expected & observed)
        unsupported += report.summary.unsupported_claims
        findings += len(report.findings)
        evaluations.append(
            CaseEvaluation(
                case_id=report.case_id,
                passed=not missing and not forbidden_seen,
                expected_categories=tuple(sorted(expected)),
                observed_categories=tuple(sorted(observed)),
                missing_categories=tuple(sorted(missing)),
                forbidden_categories_seen=tuple(sorted(forbidden_seen)),
                high_or_critical=report.summary.high_or_critical,
            )
        )
    passed = sum(case.passed for case in evaluations)
    return EvaluationResult(
        schema_version="1.0.0",
        engine="deterministic",
        cases_total=len(evaluations),
        cases_passed=passed,
        expected_categories=total_expected,
        matched_categories=total_matched,
        category_recall=total_matched / total_expected if total_expected else 1.0,
        task_success_rate=passed / len(evaluations),
        unsupported_claim_rate=unsupported / findings if findings else 0.0,
        cases=tuple(evaluations),
    )


def write_evaluation(result: EvaluationResult, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(asdict(result), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
