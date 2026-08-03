"""Render the auditable ProofEdge report and machine-readable ledger."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from proofedge.models import AssuranceReport


@dataclass(frozen=True, slots=True)
class ReportPaths:
    markdown: Path
    json: Path


def _markdown(report: AssuranceReport) -> str:
    lines = [
        "# ProofEdge Migration Assurance Report",
        "",
        f"- Case: `{report.case_id}`",
        f"- Engine: `{report.engine}`",
        f"- Schema: `{report.schema_version}`",
        f"- Source contracts: {report.summary.contracts_source}",
        f"- Target contracts: {report.summary.contracts_target}",
        f"- High/critical findings: {report.summary.high_or_critical}",
        f"- Unsupported claims: {report.summary.unsupported_claims}",
        "",
        "## Findings",
        "",
    ]
    if not report.findings:
        lines.extend(["No deterministic risk signals were found.", ""])
    for finding in report.findings:
        lines.extend(
            [
                f"### [{finding.severity.upper()}] {finding.title}",
                "",
                f"`{finding.id}` · `{finding.category}` · confidence {finding.confidence:.2f}",
                "",
                finding.detail,
                "",
                "Evidence:",
                "",
            ]
        )
        for evidence in finding.evidence:
            line = f"- `{evidence.repository}:{evidence.path}`"
            if evidence.line_start:
                line += f" line {evidence.line_start}"
            if evidence.sha256:
                line += f" · SHA-256 `{evidence.sha256}`"
            lines.append(line)
        lines.extend(["", f"Recommended test: {finding.recommended_test}", ""])
    lines.extend(["## Differential testing plan", ""])
    lines.extend(f"{index}. {step}" for index, step in enumerate(report.differential_test_plan, 1))
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {limitation}" for limitation in report.limitations)
    lines.append("")
    return "\n".join(lines)


def write_report(report: AssuranceReport, output: Path) -> ReportPaths:
    output.mkdir(parents=True, exist_ok=True)
    markdown_path = output / "report.md"
    json_path = output / "evidence-ledger.json"
    markdown_path.write_text(_markdown(report), encoding="utf-8", newline="\n")
    json_path.write_text(
        json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return ReportPaths(markdown=markdown_path, json=json_path)
