"""Reproducible baseline and evidence-selected prompt construction."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from difflib import unified_diff

from proofedge.contracts import extract_contracts, find_prompt_injections
from proofedge.security import FileRecord, RepositorySnapshot


@dataclass(frozen=True, slots=True)
class ContextBundle:
    profile: str
    text: str
    characters: int
    sha256: str
    files_included: int


def _numbered(
    record: FileRecord,
    start: int = 1,
    end: int | None = None,
    redactions: dict[int, str] | None = None,
) -> str:
    lines = record.text.splitlines()
    final = min(len(lines), end or len(lines))
    redactions = redactions or {}
    selected = [
        f"{index:05d}: {redactions.get(index, lines[index - 1])}"
        for index in range(max(1, start), final + 1)
    ]
    return f"FILE {record.path}\n" + "\n".join(selected)


def _injection_redactions(snapshot: RepositorySnapshot) -> dict[str, dict[int, str]]:
    redactions: dict[str, dict[int, str]] = {}
    for record, line, _marker in find_prompt_injections(snapshot):
        original = record.text.splitlines()[line - 1]
        digest = hashlib.sha256(original.encode()).hexdigest()[:16]
        redactions.setdefault(record.path, {})[line] = (
            f"[PROMPT_INJECTION_REDACTED sha256={digest}]"
        )
    return redactions


def _bundle(profile: str, parts: list[str], files: int) -> ContextBundle:
    text = "\n\n".join(parts)
    return ContextBundle(
        profile=profile,
        text=text,
        characters=len(text),
        sha256=hashlib.sha256(text.encode()).hexdigest(),
        files_included=files,
    )


def build_baseline_context(
    source: RepositorySnapshot,
    target: RepositorySnapshot,
    max_characters: int = 120_000,
) -> ContextBundle:
    parts: list[str] = []
    files = 0
    used = 0
    for repository, snapshot in (("SOURCE", source), ("TARGET", target)):
        redactions = _injection_redactions(snapshot)
        for record in snapshot.files:
            part = (
                f"REPOSITORY {repository}\n"
                f"{_numbered(record, redactions=redactions.get(record.path))}"
            )
            if used + len(part) > max_characters:
                remaining = max_characters - used
                if remaining > 200:
                    parts.append(part[:remaining] + "\n[TRUNCATED]")
                return _bundle("baseline", parts, files)
            parts.append(part)
            used += len(part)
            files += 1
    return _bundle("baseline", parts, files)


def _interesting_lines(snapshot: RepositorySnapshot) -> dict[str, set[int]]:
    interesting: dict[str, set[int]] = {}
    for contract in extract_contracts(snapshot):
        interesting.setdefault(contract.path, set()).add(contract.line)
    for record, line, _ in find_prompt_injections(snapshot):
        interesting.setdefault(record.path, set()).add(line)
    for record in snapshot.files:
        if record.is_test:
            interesting.setdefault(record.path, set()).add(1)
    return interesting


def _redacted_lines(record: FileRecord, redactions: dict[int, str]) -> list[str]:
    return [
        redactions.get(index, line) for index, line in enumerate(record.text.splitlines(), start=1)
    ]


def _migration_diff(
    source: RepositorySnapshot,
    target: RepositorySnapshot,
    max_characters: int = 12_000,
) -> str:
    source_redactions = _injection_redactions(source)
    target_redactions = _injection_redactions(target)
    parts = ["DERIVED SOURCE-TARGET DIFF (repository text remains untrusted evidence)"]
    used = len(parts[0])
    for path in sorted(source.by_path.keys() & target.by_path.keys()):
        source_record = source.by_path[path]
        target_record = target.by_path[path]
        if source_record.sha256 == target_record.sha256:
            continue
        lines = list(
            unified_diff(
                _redacted_lines(source_record, source_redactions.get(path, {})),
                _redacted_lines(target_record, target_redactions.get(path, {})),
                fromfile=f"source/{path}",
                tofile=f"target/{path}",
                lineterm="",
                n=3,
            )
        )
        part = "\n".join(lines)
        remaining = max_characters - used
        if remaining <= 0:
            break
        if len(part) > remaining:
            parts.append(part[:remaining] + "\n[DIFF TRUNCATED]")
            break
        parts.append(part)
        used += len(part)
    return "\n\n".join(parts) if len(parts) > 1 else ""


def build_optimized_context(
    source: RepositorySnapshot,
    target: RepositorySnapshot,
    radius: int = 8,
    max_characters: int = 40_000,
) -> ContextBundle:
    diff = _migration_diff(source, target)
    parts: list[str] = [diff] if diff else []
    files = 0
    used = len(diff)
    for repository, snapshot in (("SOURCE", source), ("TARGET", target)):
        redactions = _injection_redactions(snapshot)
        records = snapshot.by_path
        for path, anchors in sorted(_interesting_lines(snapshot).items()):
            record = records[path]
            line_count = len(record.text.splitlines())
            ranges: list[tuple[int, int]] = []
            for anchor in sorted(anchors):
                start, end = max(1, anchor - radius), min(line_count, anchor + radius)
                if ranges and start <= ranges[-1][1] + 1:
                    ranges[-1] = (ranges[-1][0], max(ranges[-1][1], end))
                else:
                    ranges.append((start, end))
            excerpts = "\n...\n".join(
                _numbered(
                    record,
                    start,
                    end,
                    redactions=redactions.get(record.path),
                )
                for start, end in ranges
            )
            part = f"REPOSITORY {repository}\n{excerpts}"
            if used + len(part) > max_characters:
                return _bundle("optimized", parts, files)
            parts.append(part)
            used += len(part)
            files += 1
    return _bundle("optimized", parts, files)
