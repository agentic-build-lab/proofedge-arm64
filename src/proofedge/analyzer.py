"""Deterministic migration-assurance engine."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from proofedge.context import build_baseline_context, build_optimized_context
from proofedge.contracts import extract_contracts, find_prompt_injections
from proofedge.engines import LlamaCppClient
from proofedge.models import (
    AssuranceReport,
    EvidenceRef,
    Finding,
    ReportSummary,
    RepositoryStats,
)
from proofedge.security import FileRecord, RepositorySnapshot, scan_repository


@dataclass(frozen=True, slots=True)
class AnalysisConfig:
    source: Path
    target: Path
    manifest: Path | None = None


def _stats(snapshot: RepositorySnapshot, contracts: int) -> RepositoryStats:
    return RepositoryStats(
        files_scanned=len(snapshot.files),
        bytes_scanned=sum(record.size for record in snapshot.files),
        files_skipped=snapshot.skipped,
        test_files=sum(record.is_test for record in snapshot.files),
        public_contracts=contracts,
    )


def _load_manifest(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError("Manifest must be a JSON object")
    return document


def _finding_id(category: str, identity: str) -> str:
    digest = hashlib.sha256(f"{category}:{identity}".encode()).hexdigest()[:8].upper()
    return f"PE-{digest}"


def _evidence(record: FileRecord, repository: str, line: int | None = None) -> EvidenceRef:
    return EvidenceRef(
        repository=repository,  # type: ignore[arg-type]
        path=record.path,
        line_start=line,
        line_end=line,
        sha256=record.sha256,
    )


def _claim_findings(
    manifest: dict[str, Any], source: RepositorySnapshot, target: RepositorySnapshot
) -> list[Finding]:
    findings: list[Finding] = []
    repositories = {"source": source.by_path, "target": target.by_path}
    claims = manifest.get("claims", [])
    if not isinstance(claims, list):
        raise ValueError("manifest.claims must be a list")
    for index, claim in enumerate(claims):
        if not isinstance(claim, dict):
            continue
        claim_id = str(claim.get("id", f"claim-{index + 1}"))
        statement = str(claim.get("statement", "Unlabelled claim"))
        references = claim.get("evidence", [])
        valid: list[EvidenceRef] = []
        invalid_reasons: list[str] = []
        if not isinstance(references, list) or not references:
            invalid_reasons.append("no evidence references were supplied")
        else:
            for reference in references:
                if not isinstance(reference, dict):
                    invalid_reasons.append("an evidence reference is not an object")
                    continue
                repository = str(reference.get("repository", "target"))
                path = str(reference.get("path", ""))
                record = repositories.get(repository, {}).get(path)
                if record is None:
                    invalid_reasons.append(f"{repository}:{path} does not exist in the scan")
                    continue
                expected = reference.get("sha256")
                if expected and expected != record.sha256:
                    invalid_reasons.append(f"{repository}:{path} hash does not match")
                    continue
                line = reference.get("line")
                if line is not None and (
                    not isinstance(line, int) or line < 1 or line > len(record.text.splitlines())
                ):
                    invalid_reasons.append(f"{repository}:{path} line is outside the file")
                    continue
                valid.append(_evidence(record, repository, line))
        if invalid_reasons:
            findings.append(
                Finding(
                    id=_finding_id("unsupported-claim", claim_id),
                    category="unsupported_claim",
                    severity="high",
                    title=f"Claim lacks valid evidence: {claim_id}",
                    detail=f"{statement}. Evidence validation failed because "
                    + "; ".join(invalid_reasons)
                    + ".",
                    confidence=1.0,
                    evidence=tuple(valid) or (EvidenceRef("manifest", "manifest.json"),),
                    recommended_test=(
                        "Attach a pinned file, line, and optional SHA-256 that directly "
                        f"supports {claim_id}."
                    ),
                )
            )
    return findings


def analyze_migration(config: AnalysisConfig) -> AssuranceReport:
    source = scan_repository(config.source)
    target = scan_repository(config.target)
    manifest = _load_manifest(config.manifest)
    source_contracts = extract_contracts(source)
    target_contracts = extract_contracts(target)
    target_by_key = {contract.key: contract for contract in target_contracts}
    aliases = {
        str(key).casefold(): str(value).casefold()
        for key, value in manifest.get("contract_aliases", {}).items()
    }
    findings: list[Finding] = []
    plan: list[str] = []

    for contract in source_contracts:
        lookup_name = aliases.get(contract.name.casefold(), contract.name.casefold())
        peer = target_by_key.get((contract.kind, lookup_name))
        source_record = source.by_path[contract.path]
        if peer is None:
            findings.append(
                Finding(
                    id=_finding_id("missing-contract", f"{contract.kind}:{contract.name}"),
                    category="contract_gap",
                    severity="high",
                    title=f"Public {contract.kind} is absent from the target: {contract.name}",
                    detail=(
                        f"The source exposes `{contract.signature}` but no mapped target "
                        "contract was found."
                    ),
                    confidence=0.82,
                    evidence=(_evidence(source_record, "source", contract.line),),
                    recommended_test=(
                        f"Add a differential test for `{contract.name}` covering valid, "
                        "boundary, and invalid inputs."
                    ),
                )
            )
            plan.append(
                f"Exercise `{contract.name}` against both implementations with boundary "
                "and error inputs."
            )
        elif peer.signature != contract.signature:
            target_record = target.by_path[peer.path]
            findings.append(
                Finding(
                    id=_finding_id("signature-change", f"{contract.kind}:{contract.name}"),
                    category="signature_change",
                    severity="medium",
                    title=f"Contract shape changed: {contract.name}",
                    detail=f"Source `{contract.signature}` differs from target `{peer.signature}`.",
                    confidence=0.74,
                    evidence=(
                        _evidence(source_record, "source", contract.line),
                        _evidence(target_record, "target", peer.line),
                    ),
                    recommended_test=(
                        "Verify argument defaults, required fields, and error behavior for "
                        f"`{contract.name}`."
                    ),
                )
            )
            plan.append(f"Compare defaults and failure behavior for `{contract.name}`.")

    source_tests = sum(record.is_test for record in source.files)
    target_tests = sum(record.is_test for record in target.files)
    if source_tests and target_tests == 0:
        first_test = next(record for record in source.files if record.is_test)
        findings.append(
            Finding(
                id=_finding_id("test-loss", "all-target-tests"),
                category="test_weakening",
                severity="high",
                title="Target contains no detectable tests",
                detail=f"The source has {source_tests} test files; the target scan has none.",
                confidence=0.95,
                evidence=(_evidence(first_test, "source"),),
                recommended_test=(
                    "Port the behavioral tests before claiming migration completeness."
                ),
            )
        )
        plan.append("Recreate the source behavioral test matrix in the target test harness.")

    for repository_name, snapshot in (("source", source), ("target", target)):
        for record, line, marker in find_prompt_injections(snapshot):
            findings.append(
                Finding(
                    id=_finding_id("prompt-injection", f"{repository_name}:{record.path}:{line}"),
                    category="prompt_injection",
                    severity="high",
                    title="Repository contains an instruction-like prompt injection marker",
                    detail=(
                        f"`{marker}` is treated as untrusted repository content and was "
                        "not followed."
                    ),
                    confidence=0.99,
                    evidence=(_evidence(record, repository_name, line),),
                    recommended_test=(
                        "Keep this marker in the adversarial corpus and assert that no tool "
                        "or secret access occurs."
                    ),
                )
            )
            plan.append(f"Run the prompt-injection isolation test for `{record.path}`.")

    findings.extend(_claim_findings(manifest, source, target))
    findings.sort(
        key=lambda finding: (
            {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}[finding.severity],
            finding.id,
        )
    )
    unique_plan = tuple(dict.fromkeys(plan)) or (
        "Run identical valid, boundary, and invalid inputs through both implementations.",
    )
    missing = sum(finding.category == "contract_gap" for finding in findings)
    unsupported = sum(finding.category == "unsupported_claim" for finding in findings)
    injections = sum(finding.category == "prompt_injection" for finding in findings)
    summary = ReportSummary(
        contracts_source=len(source_contracts),
        contracts_target=len(target_contracts),
        missing_contracts=missing,
        unsupported_claims=unsupported,
        high_or_critical=sum(finding.severity in {"high", "critical"} for finding in findings),
        prompt_injection_markers=injections,
    )
    return AssuranceReport(
        schema_version="1.0.0",
        engine="deterministic",
        case_id=str(manifest.get("case_id", "ad-hoc")),
        source_root=str(source.root),
        target_root=str(target.root),
        source_stats=_stats(source, len(source_contracts)),
        target_stats=_stats(target, len(target_contracts)),
        summary=summary,
        findings=tuple(findings),
        differential_test_plan=unique_plan,
        limitations=(
            "Static contract matching is a risk signal, not proof of semantic equivalence.",
            "Cross-language name changes require explicit contract_aliases in the case manifest.",
            "Repository code was not executed; runtime evidence must be attached separately.",
        ),
        metadata={"manifest": str(config.manifest) if config.manifest else None},
    )


def augment_with_local_model(
    report: AssuranceReport,
    config: AnalysisConfig,
    client: LlamaCppClient,
    profile: str,
) -> AssuranceReport:
    source = scan_repository(config.source)
    target = scan_repository(config.target)
    context = (
        build_baseline_context(source, target)
        if profile == "baseline"
        else build_optimized_context(source, target)
    )
    response = client.generate_plan(context.text)
    repositories = {"source": source.by_path, "target": target.by_path}
    accepted: list[str] = []
    rejected: list[Finding] = []
    for index, proposal in enumerate(response.document.get("tests", [])):
        if not isinstance(proposal, dict):
            continue
        repository = str(proposal.get("repository", ""))
        path = str(proposal.get("path", ""))
        line = proposal.get("line")
        record = repositories.get(repository, {}).get(path)
        valid_line = (
            isinstance(line, int) and record is not None and line <= len(record.text.splitlines())
        )
        if not valid_line:
            rejected.append(
                Finding(
                    id=_finding_id(
                        "unsupported-model-proposal", f"{index}:{repository}:{path}:{line}"
                    ),
                    category="unsupported_claim",
                    severity="high",
                    title="Local-model test proposal rejected by evidence validation",
                    detail=(
                        "The model cited an absent repository path or line. The proposal was "
                        "excluded from the differential test plan."
                    ),
                    confidence=1.0,
                    evidence=(EvidenceRef("manifest", "local-model-output"),),
                    recommended_test="Regenerate with visible, numbered evidence only.",
                )
            )
            continue
        name = str(proposal.get("name", "Unnamed test"))
        purpose = str(proposal.get("purpose", ""))
        relation = str(proposal.get("expected_relation", "investigate"))
        accepted.append(
            f"[{proposal.get('priority', 'medium')}] {name}: {purpose} "
            f"({repository}:{path}:{line}; relation={relation})"
        )
    findings = tuple(
        sorted(
            (*report.findings, *rejected),
            key=lambda finding: (
                {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}[finding.severity],
                finding.id,
            ),
        )
    )
    summary = replace(
        report.summary,
        unsupported_claims=report.summary.unsupported_claims + len(rejected),
        high_or_critical=report.summary.high_or_critical + len(rejected),
    )
    metadata = {
        **report.metadata,
        "local_model": {
            "profile": profile,
            "context_characters": context.characters,
            "context_sha256": context.sha256,
            "files_included": context.files_included,
            "accepted_tests": len(accepted),
            "rejected_tests": len(rejected),
            "timings": response.timings,
            "usage": response.usage,
        },
    }
    return replace(
        report,
        engine="llama.cpp",
        summary=summary,
        findings=findings,
        differential_test_plan=tuple(accepted) or report.differential_test_plan,
        metadata=metadata,
    )
