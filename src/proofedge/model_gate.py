"""Evidence validation for local-model test proposals."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from proofedge.security import RepositorySnapshot


@dataclass(frozen=True, slots=True)
class RejectedProposal:
    index: int
    repository: str
    path: str
    line: Any
    reason: str


@dataclass(frozen=True, slots=True)
class ProposalGateResult:
    accepted: tuple[dict[str, Any], ...]
    rejected: tuple[RejectedProposal, ...]


def visible_evidence(context: str) -> frozenset[tuple[str, str, int]]:
    """Index only path/line triples actually shown in a numbered model context."""
    repository = ""
    path = ""
    visible: set[tuple[str, str, int]] = set()
    for text_line in context.splitlines():
        if text_line.startswith("REPOSITORY "):
            repository = text_line.removeprefix("REPOSITORY ").strip().lower()
            path = ""
        elif text_line.startswith("FILE "):
            path = text_line.removeprefix("FILE ").strip()
        elif len(text_line) >= 7 and text_line[:5].isdigit() and text_line[5:7] == ": ":
            if repository in {"source", "target"} and path:
                visible.add((repository, path, int(text_line[:5])))
    return frozenset(visible)


def gate_model_proposals(
    document: dict[str, Any],
    source: RepositorySnapshot,
    target: RepositorySnapshot,
    context: str,
) -> ProposalGateResult:
    """Accept proposals only when the cited repository line exists and was visible."""
    repositories = {"source": source.by_path, "target": target.by_path}
    visible = visible_evidence(context)
    accepted: list[dict[str, Any]] = []
    rejected: list[RejectedProposal] = []
    for index, proposal in enumerate(document["tests"]):
        repository = proposal["repository"]
        path = proposal["path"]
        line = proposal["line"]
        record = repositories[repository].get(path)
        if record is None:
            reason = "path was not present in the bounded repository scan"
        elif line > len(record.text.splitlines()):
            reason = "line was outside the bounded repository scan"
        elif (repository, path, line) not in visible:
            reason = "line was not included in the model-visible context"
        else:
            accepted.append(proposal)
            continue
        rejected.append(RejectedProposal(index, repository, path, line, reason))
    return ProposalGateResult(tuple(accepted), tuple(rejected))
