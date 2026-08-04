"""Objective local-model quality gate over predeclared evidence anchors."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from proofedge.context import build_baseline_context, build_optimized_context
from proofedge.engines import LlamaCppClient, LlamaCppError
from proofedge.model_gate import RejectedProposal, gate_model_proposals
from proofedge.security import RepositorySnapshot, scan_repository


@dataclass(frozen=True, slots=True)
class ModelCaseEvaluation:
    case_id: str
    passed: bool
    schema_valid: bool
    profile: str
    context_characters: int
    context_sha256: str
    proposals_total: int
    accepted_proposals: int
    rejected_proposals: int
    raw_reference_validity: float
    published_reference_validity: float
    objectives_total: int
    evidence_objectives_matched: int
    objectives_matched: int
    matched_objective_ids: tuple[str, ...]
    risk_evidence_coverage: float
    semantic_objective_coverage: float
    gold_target_density: float
    canary_leakage: tuple[str, ...]
    fallback_used: bool
    response_sha256: str | None
    response: dict[str, Any] | None
    rejected: tuple[dict[str, Any], ...]
    timings: dict[str, Any]
    usage: dict[str, Any]
    error: str | None


@dataclass(frozen=True, slots=True)
class ModelEvaluationResult:
    schema_version: str
    engine: str
    profile: str
    passed: bool
    cases_total: int
    cases_passed: int
    schema_completion_rate: float
    proposals_total: int
    accepted_proposals: int
    rejected_proposals: int
    raw_reference_validity: float
    published_reference_validity: float
    objectives_total: int
    evidence_objectives_matched: int
    objectives_matched: int
    risk_evidence_coverage: float
    semantic_objective_coverage: float
    canary_leakage_count: int
    fallback_count: int
    thresholds: dict[str, float | int]
    cases: tuple[ModelCaseEvaluation, ...]


THRESHOLDS: dict[str, float | int] = {
    "schema_completion_rate": 1.0,
    "minimum_case_raw_reference_validity": 0.75,
    "minimum_case_risk_evidence_coverage": 0.75,
    "minimum_case_semantic_objective_coverage": 0.75,
    "minimum_case_gold_target_density": 0.40,
    "maximum_canary_leakage_count": 0,
    "maximum_fallback_count": 0,
}


def _validate_oracle_files(
    oracle: dict[str, Any], source: RepositorySnapshot, target: RepositorySnapshot
) -> None:
    repositories = {"source": source.by_path, "target": target.by_path}
    for expected in oracle.get("files", []):
        repository = expected.get("repository")
        path = expected.get("path")
        record = repositories.get(repository, {}).get(path)
        if record is None or record.sha256 != expected.get("sha256"):
            raise ValueError(f"Frozen model oracle file changed: {repository}:{path}")


def _proposal_candidates(
    proposals: tuple[dict[str, Any], ...],
    objectives: list[dict[str, Any]],
    *,
    semantic: bool,
) -> list[list[int]]:
    candidates: list[list[int]] = []
    for objective in objectives:
        matches: list[int] = []
        for proposal_index, proposal in enumerate(proposals):
            for evidence in objective.get("acceptable_evidence", []):
                if (
                    proposal["repository"] == evidence.get("repository")
                    and proposal["path"] == evidence.get("path")
                    and evidence.get("line_start", 1)
                    <= proposal["line"]
                    <= evidence.get("line_end", evidence.get("line_start", 1))
                ):
                    if semantic and not _semantic_match(proposal, objective):
                        continue
                    matches.append(proposal_index)
                    break
        candidates.append(sorted(set(matches)))
    return candidates


def _semantic_match(proposal: dict[str, Any], objective: dict[str, Any]) -> bool:
    relation = proposal["expected_relation"]
    allowed_relations = objective.get("allowed_expected_relations", [])
    if allowed_relations and relation not in allowed_relations:
        return False
    content = " ".join([proposal["name"], proposal["purpose"], *proposal["inputs"]]).casefold()
    required_content = objective.get("required_content_any", [])
    if required_content and not any(str(term).casefold() in content for term in required_content):
        return False
    input_content = " ".join(proposal["inputs"]).casefold()
    required_inputs = objective.get("required_input_any", [])
    return not required_inputs or any(
        str(term).casefold() in input_content for term in required_inputs
    )


def _maximum_objective_matching(candidates: list[list[int]]) -> frozenset[int]:
    proposal_owner: dict[int, int] = {}

    def assign(objective_index: int, seen: set[int]) -> bool:
        for proposal_index in candidates[objective_index]:
            if proposal_index in seen:
                continue
            seen.add(proposal_index)
            owner = proposal_owner.get(proposal_index)
            if owner is None or assign(owner, seen):
                proposal_owner[proposal_index] = objective_index
                return True
        return False

    for objective_index in range(len(candidates)):
        assign(objective_index, set())
    return frozenset(proposal_owner.values())


def _rejected_dict(rejected: RejectedProposal) -> dict[str, Any]:
    return {
        "index": rejected.index,
        "repository": rejected.repository,
        "path": rejected.path,
        "line": rejected.line,
        "reason": rejected.reason,
    }


def evaluate_model_case(
    case_dir: Path, client: LlamaCppClient, profile: str
) -> ModelCaseEvaluation:
    oracle = json.loads((case_dir / "model-golden.json").read_text(encoding="utf-8"))
    source = scan_repository(case_dir / "source")
    target = scan_repository(case_dir / "target")
    _validate_oracle_files(oracle, source, target)
    context = (
        build_baseline_context(source, target)
        if profile == "baseline"
        else build_optimized_context(source, target)
    )
    try:
        response = client.generate_plan(context.text)
    except LlamaCppError as exc:
        return ModelCaseEvaluation(
            case_id=oracle["case_id"],
            passed=False,
            schema_valid=False,
            profile=profile,
            context_characters=context.characters,
            context_sha256=context.sha256,
            proposals_total=0,
            accepted_proposals=0,
            rejected_proposals=0,
            raw_reference_validity=0.0,
            published_reference_validity=0.0,
            objectives_total=len(oracle["objectives"]),
            evidence_objectives_matched=0,
            objectives_matched=0,
            matched_objective_ids=(),
            risk_evidence_coverage=0.0,
            semantic_objective_coverage=0.0,
            gold_target_density=0.0,
            canary_leakage=(),
            fallback_used=True,
            response_sha256=None,
            response=None,
            rejected=(),
            timings={},
            usage={},
            error=str(exc),
        )

    gate = gate_model_proposals(response.document, source, target, context.text)
    objectives = oracle["objectives"]
    evidence_indexes = _maximum_objective_matching(
        _proposal_candidates(gate.accepted, objectives, semantic=False)
    )
    semantic_indexes = _maximum_objective_matching(
        _proposal_candidates(gate.accepted, objectives, semantic=True)
    )
    matched_ids = tuple(objectives[index]["id"] for index in sorted(semantic_indexes))
    proposals_total = len(response.document["tests"])
    accepted_total = len(gate.accepted)
    objective_total = len(objectives)
    serialized = json.dumps(response.document, sort_keys=True, separators=(",", ":"))
    canaries = tuple(
        canary
        for canary in oracle.get("forbidden_output_substrings", [])
        if canary.casefold() in serialized.casefold()
    )
    raw_validity = accepted_total / proposals_total
    evidence_coverage = len(evidence_indexes) / objective_total if objective_total else 1.0
    semantic_coverage = len(semantic_indexes) / objective_total if objective_total else 1.0
    density = len(matched_ids) / accepted_total if accepted_total else 0.0
    passed = (
        raw_validity >= THRESHOLDS["minimum_case_raw_reference_validity"]
        and evidence_coverage >= THRESHOLDS["minimum_case_risk_evidence_coverage"]
        and semantic_coverage >= THRESHOLDS["minimum_case_semantic_objective_coverage"]
        and density >= THRESHOLDS["minimum_case_gold_target_density"]
        and not canaries
        and accepted_total > 0
    )
    return ModelCaseEvaluation(
        case_id=oracle["case_id"],
        passed=passed,
        schema_valid=True,
        profile=profile,
        context_characters=context.characters,
        context_sha256=context.sha256,
        proposals_total=proposals_total,
        accepted_proposals=accepted_total,
        rejected_proposals=len(gate.rejected),
        raw_reference_validity=raw_validity,
        published_reference_validity=1.0 if accepted_total else 0.0,
        objectives_total=objective_total,
        evidence_objectives_matched=len(evidence_indexes),
        objectives_matched=len(matched_ids),
        matched_objective_ids=matched_ids,
        risk_evidence_coverage=evidence_coverage,
        semantic_objective_coverage=semantic_coverage,
        gold_target_density=density,
        canary_leakage=canaries,
        fallback_used=not gate.accepted,
        response_sha256=hashlib.sha256(serialized.encode()).hexdigest(),
        response=response.document,
        rejected=tuple(_rejected_dict(item) for item in gate.rejected),
        timings=response.timings,
        usage=response.usage,
        error=None,
    )


def evaluate_local_model(
    cases_root: Path, client: LlamaCppClient, profile: str
) -> ModelEvaluationResult:
    oracle_paths = sorted(cases_root.glob("*/model-golden.json"))
    if not oracle_paths:
        raise ValueError(f"No model golden cases found below {cases_root}")
    cases = tuple(evaluate_model_case(path.parent, client, profile) for path in oracle_paths)
    proposals_total = sum(case.proposals_total for case in cases)
    accepted_total = sum(case.accepted_proposals for case in cases)
    objectives_total = sum(case.objectives_total for case in cases)
    evidence_objectives_matched = sum(case.evidence_objectives_matched for case in cases)
    objectives_matched = sum(case.objectives_matched for case in cases)
    schema_valid = sum(case.schema_valid for case in cases)
    return ModelEvaluationResult(
        schema_version="1.0.0",
        engine="llama.cpp",
        profile=profile,
        passed=all(case.passed for case in cases),
        cases_total=len(cases),
        cases_passed=sum(case.passed for case in cases),
        schema_completion_rate=schema_valid / len(cases),
        proposals_total=proposals_total,
        accepted_proposals=accepted_total,
        rejected_proposals=sum(case.rejected_proposals for case in cases),
        raw_reference_validity=accepted_total / proposals_total if proposals_total else 0.0,
        published_reference_validity=1.0 if accepted_total else 0.0,
        objectives_total=objectives_total,
        evidence_objectives_matched=evidence_objectives_matched,
        objectives_matched=objectives_matched,
        risk_evidence_coverage=(
            evidence_objectives_matched / objectives_total if objectives_total else 1.0
        ),
        semantic_objective_coverage=(
            objectives_matched / objectives_total if objectives_total else 1.0
        ),
        canary_leakage_count=sum(len(case.canary_leakage) for case in cases),
        fallback_count=sum(case.fallback_used for case in cases),
        thresholds=THRESHOLDS,
        cases=cases,
    )


def write_model_evaluation(result: ModelEvaluationResult, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(asdict(result), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
