"""Reproducible baseline and evidence-selected prompt construction."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from proofedge.contracts import extract_contracts, find_prompt_injections
from proofedge.security import FileRecord, RepositorySnapshot


@dataclass(frozen=True, slots=True)
class ContextBundle:
    profile: str
    text: str
    characters: int
    sha256: str
    files_included: int


def _numbered(record: FileRecord, start: int = 1, end: int | None = None) -> str:
    lines = record.text.splitlines()
    final = min(len(lines), end or len(lines))
    selected = [f"{index:05d}: {lines[index - 1]}" for index in range(max(1, start), final + 1)]
    return f"FILE {record.path}\n" + "\n".join(selected)


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
        for record in snapshot.files:
            part = f"REPOSITORY {repository}\n{_numbered(record)}"
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


def build_optimized_context(
    source: RepositorySnapshot,
    target: RepositorySnapshot,
    radius: int = 8,
    max_characters: int = 40_000,
) -> ContextBundle:
    parts: list[str] = []
    files = 0
    used = 0
    for repository, snapshot in (("SOURCE", source), ("TARGET", target)):
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
            excerpts = "\n...\n".join(_numbered(record, start, end) for start, end in ranges)
            part = f"REPOSITORY {repository}\n{excerpts}"
            if used + len(part) > max_characters:
                return _bundle("optimized", parts, files)
            parts.append(part)
            used += len(part)
            files += 1
    return _bundle("optimized", parts, files)
