"""Frozen, auditable selection rules for llama.cpp tuning evidence."""

from __future__ import annotations

import json
import re
import statistics
from pathlib import Path
from typing import Any

RSS_PATTERN = re.compile(r"Maximum resident set size \(kbytes\):\s+(\d+)")
STAGE_1_PATTERN = re.compile(r"^t(?P<threads>\d+)-c(?P<chunk>\d+)$")
STAGE_2_PATTERN = re.compile(r"^b(?P<batch>\d+)-u(?P<ubatch>\d+)$")


def _mean_samples(row: dict[str, Any]) -> float:
    samples = row.get("samples_ts")
    if not isinstance(samples, list) or not samples:
        raise ValueError("llama-bench row has no samples_ts")
    return statistics.fmean(float(value) for value in samples)


def _rss(path: Path) -> int:
    match = RSS_PATTERN.search(path.read_text(encoding="utf-8"))
    if not match:
        raise ValueError(f"Missing maximum RSS in {path}")
    return int(match.group(1))


def _rows(path: Path) -> list[dict[str, Any]]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, list) or not document:
        raise ValueError(f"Expected a non-empty llama-bench array in {path}")
    return document


def _stage_1_candidates(raw_dir: Path) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for path in sorted(raw_dir.glob("*.json")):
        match = STAGE_1_PATTERN.fullmatch(path.stem)
        if not match:
            continue
        rows = _rows(path)
        prompt = next((row for row in rows if row.get("n_prompt", 0) > 0), None)
        generation = next((row for row in rows if row.get("n_gen", 0) > 0), None)
        if prompt is None or generation is None:
            raise ValueError(f"Expected prompt and generation rows in {path}")
        candidates.append(
            {
                "threads": int(match.group("threads")),
                "chunk_multiplier": int(match.group("chunk")),
                "batch_size": int(prompt["n_batch"]),
                "ubatch_size": int(prompt["n_ubatch"]),
                "prompt_tokens_per_second": _mean_samples(prompt),
                "generation_tokens_per_second": _mean_samples(generation),
                "peak_rss_kib": _rss(path.with_suffix(".time.txt")),
                "source_file": path.name,
            }
        )
    if not candidates:
        raise ValueError(f"No stage-1 tuning results found in {raw_dir}")
    return candidates


def select_stage_1(raw_dir: Path, prefill_floor: float) -> dict[str, Any]:
    candidates = _stage_1_candidates(raw_dir)
    best_prompt = max(item["prompt_tokens_per_second"] for item in candidates)
    for item in candidates:
        item["eligible"] = item["prompt_tokens_per_second"] >= best_prompt * prefill_floor
    eligible = [item for item in candidates if item["eligible"]]
    selected = max(
        eligible,
        key=lambda item: (
            item["generation_tokens_per_second"],
            -item["peak_rss_kib"],
            -item["threads"],
            -item["chunk_multiplier"],
        ),
    )
    return {
        "schema_version": "1.0.0",
        "stage": "threads-and-chunk",
        "exploratory": True,
        "selection_rule": (
            "maximum tg128 among candidates within 2% of best pp512; "
            "then lower RSS, fewer threads, lower chunk multiplier"
        ),
        "prefill_floor_relative_to_best": prefill_floor,
        "selected": selected,
        "candidates": sorted(
            candidates, key=lambda item: (item["threads"], item["chunk_multiplier"])
        ),
    }


def _stage_2_candidates(
    raw_dir: Path, fixed_threads: int, fixed_chunk: int
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for path in sorted(raw_dir.glob("*.json")):
        match = STAGE_2_PATTERN.fullmatch(path.stem)
        if not match:
            continue
        rows = _rows(path)
        prompt = next((row for row in rows if row.get("n_prompt", 0) > 0), None)
        if prompt is None:
            raise ValueError(f"Expected a prompt row in {path}")
        candidates.append(
            {
                "threads": fixed_threads,
                "chunk_multiplier": fixed_chunk,
                "batch_size": int(match.group("batch")),
                "ubatch_size": int(match.group("ubatch")),
                "prompt_tokens_per_second": _mean_samples(prompt),
                "peak_rss_kib": _rss(path.with_suffix(".time.txt")),
                "source_file": path.name,
            }
        )
    if not candidates:
        raise ValueError(f"No stage-2 tuning results found in {raw_dir}")
    return candidates


def select_stage_2(raw_dir: Path, fixed_threads: int, fixed_chunk: int) -> dict[str, Any]:
    candidates = _stage_2_candidates(raw_dir, fixed_threads, fixed_chunk)
    selected = max(
        candidates,
        key=lambda item: (
            item["prompt_tokens_per_second"],
            -item["peak_rss_kib"],
            -item["batch_size"],
            -item["ubatch_size"],
        ),
    )
    return {
        "schema_version": "1.0.0",
        "stage": "batch-and-ubatch",
        "exploratory": True,
        "selection_rule": "maximum pp1024; then lower RSS, smaller batch, smaller ubatch",
        "selected": selected,
        "candidates": sorted(
            candidates, key=lambda item: (item["batch_size"], item["ubatch_size"])
        ),
    }
