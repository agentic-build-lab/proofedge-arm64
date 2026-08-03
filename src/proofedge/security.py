"""Bounded, non-executing ingestion for untrusted repositories."""

from __future__ import annotations

import hashlib
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
    return any(part in IGNORED_DIRECTORIES for part in relative.parts[:-1])


def _is_test_path(relative: str) -> bool:
    normalized = relative.replace("\\", "/").casefold()
    return any(marker in normalized for marker in TEST_NAME_MARKERS)


def scan_repository(root: Path, limits: ScanLimits | None = None) -> RepositorySnapshot:
    limits = limits or ScanLimits()
    resolved = root.expanduser().resolve(strict=True)
    if not resolved.is_dir():
        raise IngestionError(f"Repository root is not a directory: {resolved}")

    records: list[FileRecord] = []
    skipped = 0
    total_bytes = 0
    for path in sorted(resolved.rglob("*"), key=lambda item: item.as_posix()):
        relative = path.relative_to(resolved)
        if path.is_symlink() or _is_ignored(relative) or not path.is_file():
            if path.is_symlink():
                skipped += 1
            continue
        if path.suffix.casefold() not in DEFAULT_EXTENSIONS:
            skipped += 1
            continue
        if len(records) >= limits.max_files:
            raise IngestionError(f"File count exceeds limit ({limits.max_files})")
        size = path.stat().st_size
        if size > limits.max_file_bytes:
            skipped += 1
            continue
        if total_bytes + size > limits.max_total_bytes:
            raise IngestionError(f"Total readable bytes exceed limit ({limits.max_total_bytes})")
        data = path.read_bytes()
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
