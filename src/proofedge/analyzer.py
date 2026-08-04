"""Deterministic migration-assurance engine."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, replace
from pathlib import Path, PurePosixPath
from typing import Any

from proofedge.context import build_baseline_context, build_optimized_context
from proofedge.contracts import extract_contracts, find_prompt_injections
from proofedge.engines import LlamaCppClient, LlamaCppError
from proofedge.model_gate import gate_model_proposals
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


MAX_MANIFEST_BYTES = 262_144
_SHA256_PATTERN = re.compile(r"[0-9a-fA-F]{64}")


def _bounded_string(
    value: Any, field: str, maximum: int, *, allow_line_whitespace: bool = False
) -> str:
    permitted_controls = {"\n", "\r", "\t"} if allow_line_whitespace else set()
    if (
        not isinstance(value, str)
        or not value.strip()
        or len(value) > maximum
        or any(
            (ord(character) < 32 and character not in permitted_controls) or ord(character) == 127
            for character in value
        )
    ):
        raise ValueError(f"manifest.{field} must be a non-empty bounded string")
    return value


def _validate_manifest(document: dict[str, Any]) -> dict[str, Any]:
    if not set(document).issubset({"case_id", "claims", "contract_aliases"}):
        raise ValueError("Manifest contains unsupported top-level fields")
    if "case_id" in document:
        _bounded_string(document["case_id"], "case_id", 200, allow_line_whitespace=True)

    aliases = document.get("contract_aliases", {})
    if not isinstance(aliases, dict) or len(aliases) > 100:
        raise ValueError("manifest.contract_aliases must be an object with at most 100 entries")
    for key, value in aliases.items():
        _bounded_string(key, "contract_aliases key", 300)
        _bounded_string(value, "contract_aliases value", 300)

    claims = document.get("claims", [])
    if not isinstance(claims, list) or len(claims) > 100:
        raise ValueError("manifest.claims must be an array with at most 100 entries")
    for claim in claims:
        if not isinstance(claim, dict) or not set(claim).issubset({"id", "statement", "evidence"}):
            raise ValueError("Each manifest claim must be a bounded claim object")
        if "id" in claim:
            _bounded_string(claim["id"], "claims[].id", 200)
        if "statement" in claim:
            _bounded_string(
                claim["statement"],
                "claims[].statement",
                2_000,
                allow_line_whitespace=True,
            )
        evidence = claim.get("evidence", [])
        if not isinstance(evidence, list) or len(evidence) > 50:
            raise ValueError("manifest.claims[].evidence must contain at most 50 references")
        for reference in evidence:
            if not isinstance(reference, dict) or not set(reference).issubset(
                {"repository", "path", "line", "sha256"}
            ):
                raise ValueError("Each manifest evidence reference must be an object")
            repository = reference.get("repository", "target")
            if repository not in {"source", "target"}:
                raise ValueError("manifest evidence repository must be source or target")
            path = _bounded_string(reference.get("path"), "claims[].evidence[].path", 500)
            normalized = PurePosixPath(path.replace("\\", "/"))
            if normalized.is_absolute() or ".." in normalized.parts:
                raise ValueError("manifest evidence path must stay repository-relative")
            line = reference.get("line")
            if line is not None and (type(line) is not int or line < 1):
                raise ValueError("manifest evidence line must be a positive integer")
            sha256 = reference.get("sha256")
            if sha256 is not None and (
                not isinstance(sha256, str) or _SHA256_PATTERN.fullmatch(sha256) is None
            ):
                raise ValueError("manifest evidence sha256 must be 64 hexadecimal characters")
    return document


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
    raw = path.read_bytes()
    if len(raw) > MAX_MANIFEST_BYTES:
        raise ValueError(f"Manifest exceeds the {MAX_MANIFEST_BYTES}-byte limit")
    try:
        document = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Manifest must be valid UTF-8 JSON") from exc
    if not isinstance(document, dict):
        raise ValueError("Manifest must be a JSON object")
    return _validate_manifest(document)


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
        source_root="source",
        target_root="target",
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
        metadata={"manifest_attached": config.manifest is not None},
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
    try:
        response = client.generate_plan(context.text)
    except LlamaCppError as exc:
        metadata = {
            **report.metadata,
            "local_model": {
                "profile": profile,
                "context_characters": context.characters,
                "context_sha256": context.sha256,
                "files_included": context.files_included,
                "accepted_tests": 0,
                "rejected_tests": 0,
                "fallback_used": True,
                "error": str(exc),
            },
        }
        return replace(report, engine="deterministic-fallback", metadata=metadata)
    accepted: list[str] = []
    rejected: list[Finding] = []
    gate = gate_model_proposals(response.document, source, target, context.text)
    for decision in gate.rejected:
        rejected.append(
            Finding(
                id=_finding_id(
                    "unsupported-model-proposal",
                    f"{decision.index}:{decision.repository}:{decision.path}:{decision.line}",
                ),
                category="model_evidence_rejection",
                severity="high",
                title="Local-model test proposal rejected by evidence validation",
                detail=f"The model citation was rejected because the {decision.reason}.",
                confidence=1.0,
                evidence=(EvidenceRef("manifest", "local-model-output"),),
                recommended_test="Regenerate with visible, numbered evidence only.",
            )
        )
    for proposal in gate.accepted:
        repository = proposal["repository"]
        path = proposal["path"]
        line = proposal["line"]
        name = proposal["name"]
        purpose = proposal["purpose"]
        relation = proposal["expected_relation"]
        accepted.append(
            f"[{proposal['priority']}] {name}: {purpose} "
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
            "fallback_used": not accepted,
            "accepted_proposals": list(gate.accepted),
            "model_limitations": list(response.document["limitations"]),
            "timings": response.timings,
            "usage": response.usage,
        },
    }
    return replace(
        report,
        engine="llama.cpp" if accepted else "deterministic-fallback",
        summary=summary,
        findings=findings,
        differential_test_plan=tuple(accepted) or report.differential_test_plan,
        metadata=metadata,
    )
