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


def test_prunes_ignored_directories_case_insensitively(tmp_path: Path) -> None:
    dependency = tmp_path / "NODE_MODULES"
    dependency.mkdir()
    for index in range(20):
        (dependency / f"ignored-{index}.js").write_text("ignored", encoding="utf-8")
    (tmp_path / "safe.py").write_text("visible = True\n", encoding="utf-8")

    snapshot = scan_repository(tmp_path, ScanLimits(max_entries=3))

    assert [record.path for record in snapshot.files] == ["safe.py"]


def test_limits_all_directory_entries_not_only_source_files(tmp_path: Path) -> None:
    for index in range(4):
        (tmp_path / f"ignored-{index}.bin").write_bytes(b"not source")

    with pytest.raises(IngestionError, match="Directory entries"):
        scan_repository(tmp_path, ScanLimits(max_entries=3))


def test_skips_file_and_directory_symlinks(tmp_path: Path) -> None:
    outside = tmp_path.parent / f"{tmp_path.name}-outside"
    outside.mkdir()
    (outside / "secret.py").write_text("secret = True\n", encoding="utf-8")
    try:
        (tmp_path / "linked.py").symlink_to(outside / "secret.py")
        (tmp_path / "linked-dir").symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("This platform does not permit creating test symlinks")

    snapshot = scan_repository(tmp_path)

    assert snapshot.files == ()
    assert snapshot.skipped == 2
