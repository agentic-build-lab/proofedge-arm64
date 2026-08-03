"""Command-line entry point for ProofEdge."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from proofedge import __version__


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
        parser.error("The analysis engine is landing in the next implementation commit.")
    return 0
