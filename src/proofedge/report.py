"""Render the auditable ProofEdge report and machine-readable ledger."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from html import escape
from pathlib import Path

from proofedge.models import AssuranceReport


@dataclass(frozen=True, slots=True)
class ReportPaths:
    markdown: Path
    json: Path


MARKDOWN_SPECIAL = re.compile(r"([\\`*_{\[\]}()#+.!|>~-])")


def _plain(value: object) -> str:
    single_line = " ".join(str(value).splitlines())
    return MARKDOWN_SPECIAL.sub(r"\\\1", escape(single_line, quote=False))


def _code(value: object) -> str:
    single_line = " ".join(str(value).splitlines())
    return f"`{escape(single_line, quote=False).replace('`', '&#96;')}`"


def _markdown(report: AssuranceReport) -> str:
    lines = [
        "# ProofEdge Migration Assurance Report",
        "",
        f"- Case: {_code(report.case_id)}",
        f"- Engine: {_code(report.engine)}",
        f"- Schema: {_code(report.schema_version)}",
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
                f"### [{finding.severity.upper()}] {_plain(finding.title)}",
                "",
                f"{_code(finding.id)} · {_code(finding.category)} · "
                f"confidence {finding.confidence:.2f}",
                "",
                _plain(finding.detail),
                "",
                "Evidence:",
                "",
            ]
        )
        for evidence in finding.evidence:
            line = f"- {_code(f'{evidence.repository}:{evidence.path}')}"
            if evidence.line_start:
                line += f" line {evidence.line_start}"
            if evidence.sha256:
                line += f" · SHA-256 `{evidence.sha256}`"
            lines.append(line)
        lines.extend(["", f"Recommended test: {_plain(finding.recommended_test)}", ""])
    lines.extend(["## Differential testing plan", ""])
    lines.extend(
        f"{index}. {_plain(step)}"
        for index, step in enumerate(report.differential_test_plan, 1)
    )
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {_plain(limitation)}" for limitation in report.limitations)
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
