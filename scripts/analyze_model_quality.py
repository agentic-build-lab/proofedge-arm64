#!/usr/bin/env python3
"""Summarize model-task latency and identity from a native evidence bundle."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from proofedge.benchmark_analysis import analyze_native_evidence


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--run-id", type=int, required=True)
    args = parser.parse_args()

    result = {
        "schema_version": "1.0.0",
        "benchmark": "proofedge-native-model-quality-request-comparison",
        "run_id": args.run_id,
        **analyze_native_evidence(args.evidence_dir),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(result["model_compute_latency_ms"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
