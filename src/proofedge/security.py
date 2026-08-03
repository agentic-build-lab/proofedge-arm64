"""Bounded, non-executing ingestion for untrusted repositories."""

from __future__ import annotations

import hashlib
import os
import stat
from dataclasses import dataclass
from pathlib import Path

DEFAULT_EXTENSIONS = frozenset(
    {
        ".c",
        ".cc",
        ".cpp",
        ".go",
        ".h",
        ".hpp",
        ".java",
        ".js",
        ".json",
        ".md",
        ".py",
        ".rs",
        ".toml",
        ".ts",
        ".tsx",
        ".yaml",
        ".yml",
    }
)
IGNORED_DIRECTORIES = frozenset(
    {
        ".git",
        ".hg",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".svn",
        ".venv",
        "build",
        "dist",
        "models",
        "node_modules",
        "target",
        "vendor",
    }
)
TEST_NAME_MARKERS = ("_test.", ".test.", ".spec.", "test_", "tests/", "test/")


class IngestionError(ValueError):
    """Raised when a repository violates a declared ingestion boundary."""


@dataclass(frozen=True, slots=True)
class ScanLimits:
    max_files: int = 2_000
    max_file_bytes: int = 512 * 1024
    max_total_bytes: int = 25 * 1024 * 1024
    max_entries: int = 20_000
    max_depth: int = 40
    max_relative_path_characters: int = 1_000


@dataclass(frozen=True, slots=True)
class FileRecord:
    path: str
    size: int
    sha256: str
    text: str
    is_test: bool


@dataclass(frozen=True, slots=True)
class RepositorySnapshot:
    root: Path
    files: tuple[FileRecord, ...]
    skipped: int

    @property
    def by_path(self) -> dict[str, FileRecord]:
        return {record.path: record for record in self.files}


def _is_ignored(relative: Path) -> bool:
    ignored = {name.casefold() for name in IGNORED_DIRECTORIES}
    return any(part.casefold() in ignored for part in relative.parts[:-1])


def _is_test_path(relative: str) -> bool:
    normalized = relative.replace("\\", "/").casefold()
    return any(marker in normalized for marker in TEST_NAME_MARKERS)


def _is_link_or_junction(path: Path) -> bool:
    is_junction = getattr(path, "is_junction", lambda: False)
    return path.is_symlink() or is_junction()


def _bounded_candidates(root: Path, limits: ScanLimits) -> tuple[list[Path], int]:
    """Walk without entering ignored/link directories and cap all visited entries."""
    ignored = {name.casefold() for name in IGNORED_DIRECTORIES}
    candidates: list[Path] = []
    skipped = 0
    entries_seen = 0
    stack: list[tuple[Path, int]] = [(root, 0)]
    while stack:
        directory, depth = stack.pop()
        try:
            with os.scandir(directory) as iterator:
                entries = sorted(iterator, key=lambda item: item.name.casefold())
        except OSError as exc:
            raise IngestionError(f"Unable to scan repository directory: {directory}") from exc
        for entry in entries:
            entries_seen += 1
            if entries_seen > limits.max_entries:
                raise IngestionError(f"Directory entries exceed limit ({limits.max_entries})")
            path = Path(entry.path)
            relative = path.relative_to(root)
            if len(relative.as_posix()) > limits.max_relative_path_characters:
                skipped += 1
                continue
            if entry.is_symlink() or _is_link_or_junction(path):
                skipped += 1
                continue
            if entry.is_dir(follow_symlinks=False):
                if entry.name.casefold() in ignored:
                    skipped += 1
                    continue
                if depth >= limits.max_depth:
                    raise IngestionError(f"Directory depth exceeds limit ({limits.max_depth})")
                stack.append((path, depth + 1))
            elif entry.is_file(follow_symlinks=False):
                candidates.append(path)
            else:
                skipped += 1
    return sorted(candidates, key=lambda item: item.relative_to(root).as_posix()), skipped


def _read_bounded(path: Path, max_bytes: int) -> bytes | None:
    """Open without following links where supported and never read past the cap."""
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError:
        return None
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_size > max_bytes:
            return None
        with os.fdopen(descriptor, "rb", closefd=True) as stream:
            descriptor = -1
            data = stream.read(max_bytes + 1)
        return data if len(data) <= max_bytes else None
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def scan_repository(root: Path, limits: ScanLimits | None = None) -> RepositorySnapshot:
    limits = limits or ScanLimits()
    resolved = root.expanduser().resolve(strict=True)
    if not resolved.is_dir():
        raise IngestionError(f"Repository root is not a directory: {resolved}")

    records: list[FileRecord] = []
    candidates, skipped = _bounded_candidates(resolved, limits)
    total_bytes = 0
    for path in candidates:
        relative = path.relative_to(resolved)
        if _is_ignored(relative):
            skipped += 1
            continue
        if path.suffix.casefold() not in DEFAULT_EXTENSIONS:
            skipped += 1
            continue
        if len(records) >= limits.max_files:
            raise IngestionError(f"File count exceeds limit ({limits.max_files})")
        data = _read_bounded(path, limits.max_file_bytes)
        if data is None:
            skipped += 1
            continue
        size = len(data)
        if total_bytes + size > limits.max_total_bytes:
            raise IngestionError(f"Total readable bytes exceed limit ({limits.max_total_bytes})")
        if b"\x00" in data:
            skipped += 1
            continue
        text = data.decode("utf-8", errors="replace")
        relative_text = relative.as_posix()
        records.append(
            FileRecord(
                path=relative_text,
                size=size,
                sha256=hashlib.sha256(data).hexdigest(),
                text=text,
                is_test=_is_test_path(relative_text),
            )
        )
        total_bytes += size
    return RepositorySnapshot(root=resolved, files=tuple(records), skipped=skipped)
