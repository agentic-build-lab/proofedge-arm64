from __future__ import annotations

from pathlib import Path

import pytest

from proofedge.security import IngestionError, ScanLimits, scan_repository


def test_enforces_total_byte_limit(tmp_path: Path) -> None:
    (tmp_path / "large.py").write_text("x" * 128, encoding="utf-8")
    with pytest.raises(IngestionError, match="Total readable bytes"):
        scan_repository(
            tmp_path, ScanLimits(max_files=10, max_file_bytes=1_000, max_total_bytes=32)
        )


def test_skips_binary_and_dependency_directories(tmp_path: Path) -> None:
    (tmp_path / "safe.py").write_text("def visible():\n    pass\n", encoding="utf-8")
    (tmp_path / "image.json").write_bytes(b"abc\x00def")
    dependency = tmp_path / "node_modules"
    dependency.mkdir()
    (dependency / "ignored.js").write_text("export const ignored = 1", encoding="utf-8")

    snapshot = scan_repository(tmp_path)
    assert [record.path for record in snapshot.files] == ["safe.py"]
    assert snapshot.skipped >= 1
