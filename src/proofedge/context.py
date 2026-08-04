"""Reproducible baseline and evidence-selected prompt construction."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from difflib import SequenceMatcher

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
    change_map = _migration_change_map(source, target)
    parts: list[str] = [change_map] if change_map else []
    files = 0
    used = len(change_map)
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


def _changed_excerpt(
    record: FileRecord,
    start: int,
    end: int,
    redactions: dict[int, str],
) -> str:
    if start == end:
        return "[no line on this side]"
    return _numbered(record, start + 1, end, redactions=redactions)


def _change_score(source_lines: list[str], target_lines: list[str]) -> int:
    """Put likely behavioral changes before metadata without claiming semantics."""

    text = "\n".join([*source_lines, *target_lines]).casefold()
    score = 0
    for marker, weight in (
        ("def ", 6),
        ("return", 6),
        ("responses", 6),
        ("assert", 5),
        ("round", 5),
        ("decimal", 4),
        ("status", 4),
        ("required", 3),
        ("schema", 3),
    ):
        if marker in text:
            score += weight
    if any(f'"{status}"' in text or f"'{status}'" in text for status in range(100, 600)):
        score += 6
    return score


def _migration_change_map(
    source: RepositorySnapshot,
    target: RepositorySnapshot,
    max_characters: int = 12_000,
) -> str:
    source_redactions = _injection_redactions(source)
    target_redactions = _injection_redactions(target)
    candidates: list[tuple[int, str, int, int, int, int]] = []
    for path in sorted(source.by_path.keys() & target.by_path.keys()):
        source_record = source.by_path[path]
        target_record = target.by_path[path]
        if source_record.sha256 == target_record.sha256:
            continue
        source_lines = _redacted_lines(source_record, source_redactions.get(path, {}))
        target_lines = _redacted_lines(target_record, target_redactions.get(path, {}))
        matcher = SequenceMatcher(None, source_lines, target_lines, autojunk=False)
        for tag, source_start, source_end, target_start, target_end in matcher.get_opcodes():
            if tag == "equal":
                continue
            score = _change_score(
                source_lines[source_start:source_end], target_lines[target_start:target_end]
            )
            candidates.append((score, path, source_start, source_end, target_start, target_end))

    if not candidates:
        return ""
    candidates.sort(key=lambda item: (-item[0], item[1], item[2], item[4]))
    heading = (
        "DERIVED SOURCE-TARGET CHANGE MAP\n"
        "Mechanical changed-line candidates, not semantic conclusions. Numbered lines below "
        "are valid citation anchors; inspect their text before proposing a test."
    )
    parts = [heading]
    used = len(heading)
    for index, (_score, path, source_start, source_end, target_start, target_end) in enumerate(
        candidates, start=1
    ):
        source_record = source.by_path[path]
        target_record = target.by_path[path]
        part = "\n".join(
            [
                f"CHANGE CANDIDATE {index}: {path}",
                "REPOSITORY SOURCE",
                _changed_excerpt(
                    source_record,
                    source_start,
                    source_end,
                    source_redactions.get(path, {}),
                ),
                "REPOSITORY TARGET",
                _changed_excerpt(
                    target_record,
                    target_start,
                    target_end,
                    target_redactions.get(path, {}),
                ),
            ]
        )
        remaining = max_characters - used
        if remaining <= 0:
            break
        if len(part) > remaining:
            parts.append(part[:remaining] + "\n[CHANGE MAP TRUNCATED]")
            break
        parts.append(part)
        used += len(part)
    return "\n\n".join(parts)


def build_optimized_context(
    source: RepositorySnapshot,
    target: RepositorySnapshot,
    radius: int = 8,
    max_characters: int = 40_000,
) -> ContextBundle:
    change_map = _migration_change_map(source, target)
    parts: list[str] = [change_map] if change_map else []
    files = 0
    used = len(change_map)
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
