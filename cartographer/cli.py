"""Command-line entry point. Thin: parse args -> load commits -> report."""

import argparse
import subprocess
import sys
from collections.abc import Sequence

from cartographer import gitlog, report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="carto", description="Map hidden risk in a git repository."
    )
    sub = parser.add_subparsers(dest="command", required=True)
    summary = sub.add_parser("summary", help="Overview of the git history.")
    summary.add_argument("--repo", default=".", help="Path to the git repository.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        commits = gitlog.load_commits(args.repo)
    except subprocess.CalledProcessError as exc:
        print(f"error: git log failed: {exc.stderr.strip()}", file=sys.stderr)
        return 1
    if args.command == "summary":
        print(report.format_summary(commits))
    return 0
