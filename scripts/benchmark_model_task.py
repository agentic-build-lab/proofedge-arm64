"""Run repeated quality-gated product-task measurements against local llama.cpp."""

from __future__ import annotations

import argparse
from pathlib import Path

from proofedge.engines import LlamaCppClient
from proofedge.product_benchmark import benchmark_local_model_tasks, write_product_benchmark


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, default=Path("evaluation/cases"))
    parser.add_argument("--endpoint", default="http://127.0.0.1:8080")
    parser.add_argument("--profile", choices=("baseline", "optimized"), default="optimized")
    parser.add_argument("--repetitions", type=int, default=5)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    result = benchmark_local_model_tasks(
        args.cases,
        LlamaCppClient(args.endpoint, stream=True),
        args.profile,
        args.repetitions,
    )
    write_product_benchmark(result, args.output)
    print(
        f"Product task: {result['quality']['successful_runs']}/{result['repetitions']} "
        f"runs passed; p50 {result['task_end_to_end_ms']['p50']:.2f} ms; "
        f"TTFT p50 {result['request_time_to_first_token_ms']['p50']:.2f} ms"
    )
    print(f"Product benchmark ledger: {args.output}")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
