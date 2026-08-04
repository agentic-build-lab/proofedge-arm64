"""Stable report schema shared by deterministic and local-model engines."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

Severity = Literal["info", "low", "medium", "high", "critical"]


@dataclass(frozen=True, slots=True)
class EvidenceRef:
    repository: Literal["source", "target", "manifest"]
    path: str
    line_start: int | None = None
    line_end: int | None = None
    sha256: str | None = None


@dataclass(frozen=True, slots=True)
class Contract:
    kind: str
    name: str
    signature: str
    path: str
    line: int

    @property
    def key(self) -> tuple[str, str]:
        return (self.kind, self.name.casefold())


@dataclass(frozen=True, slots=True)
class Finding:
    id: str
    category: str
    severity: Severity
    title: str
    detail: str
    confidence: float
    evidence: tuple[EvidenceRef, ...]
    recommended_test: str


@dataclass(frozen=True, slots=True)
class RepositoryStats:
    files_scanned: int
    bytes_scanned: int
    files_skipped: int
    test_files: int
    public_contracts: int


@dataclass(frozen=True, slots=True)
class ReportSummary:
    contracts_source: int
    contracts_target: int
    missing_contracts: int
    unsupported_claims: int
    high_or_critical: int
    prompt_injection_markers: int


@dataclass(frozen=True, slots=True)
class AssuranceReport:
    schema_version: str
    engine: str
    case_id: str
    source_root: str
    target_root: str
    source_stats: RepositoryStats
    target_stats: RepositoryStats
    summary: ReportSummary
    findings: tuple[Finding, ...]
    differential_test_plan: tuple[str, ...]
    limitations: tuple[str, ...]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
