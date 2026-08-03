"""Command-line entry point for ProofEdge."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from proofedge import __version__
from proofedge.analyzer import AnalysisConfig, analyze_migration
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
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "analyze":
        if args.engine != "deterministic":
            parser.error("The llama.cpp adapter is not enabled yet; use deterministic mode.")
        report = analyze_migration(
            AnalysisConfig(
                source=Path(args.source),
                target=Path(args.target),
                manifest=args.manifest,
            )
        )
        output = Path(args.output)
        paths = write_report(report, output)
        print(f"ProofEdge report: {paths.markdown}")
        print(f"Evidence ledger: {paths.json}")
        print(f"Findings: {len(report.findings)} ({report.summary.high_or_critical} high/critical)")
    return 0
