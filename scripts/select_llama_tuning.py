#!/usr/bin/env python3
"""CLI wrapper for ProofEdge's frozen llama.cpp tuning selection rules."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from proofedge.tuning import select_stage_1, select_stage_2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("stage1", "stage2"), required=True)
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--prefill-floor", type=float, default=0.98)
    parser.add_argument("--fixed-threads", type=int)
    parser.add_argument("--fixed-chunk", type=int)
    args = parser.parse_args()
    if args.stage == "stage1":
        result = select_stage_1(args.raw_dir, args.prefill_floor)
    else:
        if args.fixed_threads is None or args.fixed_chunk is None:
            parser.error("stage2 requires --fixed-threads and --fixed-chunk")
        result = select_stage_2(args.raw_dir, args.fixed_threads, args.fixed_chunk)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(result["selected"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
