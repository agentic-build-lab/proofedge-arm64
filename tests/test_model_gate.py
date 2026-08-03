from __future__ import annotations

from pathlib import Path

from proofedge.context import build_optimized_context
from proofedge.model_gate import gate_model_proposals, visible_evidence
from proofedge.security import scan_repository

CASES = Path("evaluation/cases/python-refund-v2")


def _proposal(path: str, line: int) -> dict:
    return {
        "name": "Refund reason boundary",
        "purpose": "Compare the optional reason across implementations",
        "repository": "source",
        "path": path,
        "line": line,
        "inputs": ["order-1", "duplicate"],
        "expected_relation": "equal",
        "priority": "high",
    }


def test_visible_evidence_index_is_repository_scoped() -> None:
    source = scan_repository(CASES / "source")
    target = scan_repository(CASES / "target")
    context = build_optimized_context(source, target)
    visible = visible_evidence(context.text)
    assert ("source", "pricing.py", 8) in visible
    assert ("target", "pricing.py", 11) in visible
    assert ("source", "REPOSITORY_NOTE.md", 3) not in visible


def test_gate_rejects_absent_out_of_range_and_hidden_references() -> None:
    source = scan_repository(CASES / "source")
    target = scan_repository(CASES / "target")
    context = build_optimized_context(source, target)
    document = {
        "tests": [
            _proposal("pricing.py", 8),
            _proposal("../../.ssh/id_rsa", 1),
            _proposal("pricing.py", 999),
        ],
        "limitations": [],
    }
    gate = gate_model_proposals(document, source, target, context.text)
    assert len(gate.accepted) == 1
    assert [item.reason for item in gate.rejected] == [
        "path was not present in the bounded repository scan",
        "line was outside the bounded repository scan",
    ]
