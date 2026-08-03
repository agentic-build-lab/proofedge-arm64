"""Command-line entry point for ProofEdge."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from proofedge import __version__
from proofedge.analyzer import AnalysisConfig, analyze_migration, augment_with_local_model
from proofedge.engines import LlamaCppClient
from proofedge.evaluation import evaluate_cases, write_evaluation
from proofedge.model_evaluation import evaluate_local_model, write_model_evaluation
from proofedge.report import write_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="proofedge",
        description="Evidence-driven migration assurance for private Arm64 inference.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze = subparsers.add_parser("analyze", help="Compare source and target repositories.")
    analyze.add_argument("--source", required=True)
    analyze.add_argument("--target", required=True)
    analyze.add_argument("--output", default="reports/latest")
    analyze.add_argument("--manifest", type=Path)
    analyze.add_argument(
        "--engine",
        choices=("deterministic", "llama.cpp"),
        default="deterministic",
    )
    analyze.add_argument("--endpoint", default="http://127.0.0.1:8080")
    analyze.add_argument("--profile", choices=("baseline", "optimized"), default="optimized")
    evaluate = subparsers.add_parser("evaluate", help="Run the frozen golden evaluation set.")
    evaluate.add_argument("--cases", type=Path, default=Path("evaluation/cases"))
    evaluate.add_argument("--output", type=Path, default=Path("evaluation/results/latest.json"))
    evaluate_model = subparsers.add_parser(
        "evaluate-model", help="Run the frozen local-model evidence quality gate."
    )
    evaluate_model.add_argument("--cases", type=Path, default=Path("evaluation/cases"))
    evaluate_model.add_argument(
        "--output", type=Path, default=Path("evaluation/results/local-model.json")
    )
    evaluate_model.add_argument("--endpoint", default="http://127.0.0.1:8080")
    evaluate_model.add_argument("--profile", choices=("baseline", "optimized"), default="optimized")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "analyze":
        config = AnalysisConfig(
            source=Path(args.source),
            target=Path(args.target),
            manifest=args.manifest,
        )
        report = analyze_migration(config)
        if args.engine == "llama.cpp":
            report = augment_with_local_model(
                report,
                config,
                client=LlamaCppClient(args.endpoint),
                profile=args.profile,
            )
        output = Path(args.output)
        paths = write_report(report, output)
        print(f"ProofEdge report: {paths.markdown}")
        print(f"Evidence ledger: {paths.json}")
        print(f"Findings: {len(report.findings)} ({report.summary.high_or_critical} high/critical)")
        local_model = report.metadata.get("local_model", {})
        if args.engine == "llama.cpp" and local_model.get("fallback_used"):
            print("Local-model quality gate: failed; deterministic fallback was used")
            return 2
    elif args.command == "evaluate":
        result = evaluate_cases(args.cases)
        write_evaluation(result, args.output)
        print(
            f"Deterministic golden evaluation: {result.cases_passed}/"
            f"{result.cases_total} cases passed; "
            f"category recall {result.category_recall:.1%}"
        )
        print(f"Evaluation ledger: {args.output}")
        return 0 if result.cases_passed == result.cases_total else 1
    elif args.command == "evaluate-model":
        result = evaluate_local_model(
            args.cases,
            LlamaCppClient(args.endpoint),
            args.profile,
        )
        write_model_evaluation(result, args.output)
        print(
            f"Local-model evidence gate: {result.cases_passed}/{result.cases_total} "
            f"cases passed; risk coverage {result.risk_evidence_coverage:.1%}; "
            f"raw reference validity {result.raw_reference_validity:.1%}"
        )
        print(f"Model evaluation ledger: {args.output}")
        return 0 if result.passed else 1
    return 0
