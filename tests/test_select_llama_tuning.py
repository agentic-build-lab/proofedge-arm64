from __future__ import annotations

import json
from pathlib import Path

from proofedge.tuning import select_stage_1, select_stage_2


def _write_run(
    root: Path,
    name: str,
    prompt_speed: float,
    generation_speed: float | None,
    rss: int,
    batch: int = 2048,
    ubatch: int = 512,
) -> None:
    rows = [
        {
            "n_prompt": 512,
            "n_gen": 0,
            "n_batch": batch,
            "n_ubatch": ubatch,
            "samples_ts": [prompt_speed - 1, prompt_speed + 1],
        }
    ]
    if generation_speed is not None:
        rows.append(
            {
                "n_prompt": 0,
                "n_gen": 128,
                "n_batch": batch,
                "n_ubatch": ubatch,
                "samples_ts": [generation_speed - 0.1, generation_speed + 0.1],
            }
        )
    (root / f"{name}.json").write_text(json.dumps(rows), encoding="utf-8")
    (root / f"{name}.time.txt").write_text(
        f"Maximum resident set size (kbytes): {rss}\n", encoding="utf-8"
    )


def test_stage_1_applies_prefill_floor_before_decode_selection(tmp_path: Path) -> None:
    _write_run(tmp_path, "t2-c1", 100.0, 40.0, 1000)
    _write_run(tmp_path, "t4-c2", 97.0, 50.0, 1100)
    _write_run(tmp_path, "t3-c4", 99.0, 45.0, 900)

    result = select_stage_1(tmp_path, 0.98)

    assert result["selected"]["threads"] == 3
    assert result["selected"]["chunk_multiplier"] == 4
    assert next(item for item in result["candidates"] if item["threads"] == 4)["eligible"] is False


def test_stage_2_selects_fastest_prefill_pair(tmp_path: Path) -> None:
    _write_run(tmp_path, "b512-u128", 120.0, None, 900, 512, 128)
    _write_run(tmp_path, "b1024-u256", 130.0, None, 1000, 1024, 256)

    result = select_stage_2(tmp_path, fixed_threads=4, fixed_chunk=2)

    assert result["selected"]["batch_size"] == 1024
    assert result["selected"]["ubatch_size"] == 256
    assert result["selected"]["threads"] == 4
