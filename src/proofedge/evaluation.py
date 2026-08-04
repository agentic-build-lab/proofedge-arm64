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
    expected_unsupported_claims: int
    detected_unsupported_claims: int


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    schema_version: str
    engine: str
    cases_total: int
    cases_passed: int
    expected_categories: int
    matched_categories: int
    category_recall: float
    deterministic_case_pass_rate: float
    declared_claims: int
    expected_unsupported_claims: int
    detected_unsupported_claims: int
    unsupported_claim_recall: float
    false_unsupported_claims: int
    false_unsupported_claim_rate: float
    cases: tuple[CaseEvaluation, ...]


def evaluate_cases(cases_root: Path) -> EvaluationResult:
    evaluations: list[CaseEvaluation] = []
    total_expected = 0
    total_matched = 0
    declared_claims = 0
    expected_unsupported = 0
    detected_unsupported = 0
    false_unsupported = 0
    golden_files = sorted(cases_root.glob("*/golden.json"))
    if not golden_files:
        raise ValueError(f"No golden cases found below {cases_root}")
    for golden_path in golden_files:
        case_dir = golden_path.parent
        golden = json.loads(golden_path.read_text(encoding="utf-8"))
        manifest = case_dir / "manifest.json"
        manifest_document = (
            json.loads(manifest.read_text(encoding="utf-8")) if manifest.exists() else {}
        )
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
        expected_unsupported_for_case = int(golden.get("expected_unsupported_claims", 0))
        detected_unsupported_for_case = report.summary.unsupported_claims
        missing = expected - observed
        forbidden_seen = forbidden & observed
        total_expected += len(expected)
        total_matched += len(expected & observed)
        declared_claims += len(manifest_document.get("claims", []))
        expected_unsupported += expected_unsupported_for_case
        detected_unsupported += min(detected_unsupported_for_case, expected_unsupported_for_case)
        false_unsupported += max(0, detected_unsupported_for_case - expected_unsupported_for_case)
        evaluations.append(
            CaseEvaluation(
                case_id=report.case_id,
                passed=not missing and not forbidden_seen,
                expected_categories=tuple(sorted(expected)),
                observed_categories=tuple(sorted(observed)),
                missing_categories=tuple(sorted(missing)),
                forbidden_categories_seen=tuple(sorted(forbidden_seen)),
                high_or_critical=report.summary.high_or_critical,
                expected_unsupported_claims=expected_unsupported_for_case,
                detected_unsupported_claims=detected_unsupported_for_case,
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
        deterministic_case_pass_rate=passed / len(evaluations),
        declared_claims=declared_claims,
        expected_unsupported_claims=expected_unsupported,
        detected_unsupported_claims=detected_unsupported,
        unsupported_claim_recall=(
            detected_unsupported / expected_unsupported if expected_unsupported else 1.0
        ),
        false_unsupported_claims=false_unsupported,
        false_unsupported_claim_rate=(
            false_unsupported / declared_claims if declared_claims else 0.0
        ),
        cases=tuple(evaluations),
    )


def write_evaluation(result: EvaluationResult, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(asdict(result), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
