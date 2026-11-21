"""Command-line entry point. Thin: parse args -> load commits -> report."""

import argparse
import subprocess
import sys
from collections.abc import Iterable, Sequence
from pathlib import Path

from cartographer import gitlog, report
from cartographer.analysis.hotspots import rank_hotspots
from cartographer.models import Commit


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="carto", description="Map hidden risk in a git repository."
    )
    sub = parser.add_subparsers(dest="command", required=True)
    summary = sub.add_parser("summary", help="Overview of the git history.")
    _add_repo(summary)
    hotspots = sub.add_parser("hotspots", help="Large, frequently changed files.")
    _add_repo(hotspots)
    hotspots.add_argument("--top", type=_positive_int, default=10)
    hotspots.add_argument(
        "--exclude", nargs="+", action="extend", default=[], metavar="GLOB"
    )
    hotspots.add_argument("--json", action="store_true", help="Output JSON.")
    return parser


def _add_repo(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--repo", default=".", help="Path to the git repository.")


def _positive_int(value: str) -> int:
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        commits = gitlog.load_commits(args.repo)
        if args.command == "hotspots":
            return _run_hotspots(args, commits)
    except subprocess.CalledProcessError as exc:
        print(f"error: git failed: {exc.stderr.strip()}", file=sys.stderr)
        return 1
    print(report.format_summary(commits))
    return 0


def _run_hotspots(args: argparse.Namespace, commits: list[Commit]) -> int:
    root = gitlog.repo_root(args.repo)
    paths = {change.path for commit in commits for change in commit.changes}
    sizes = _read_sizes(root, paths)
    results = rank_hotspots(commits, sizes, top=args.top, exclude=args.exclude)
    if args.json:
        print(report.format_hotspots_json(results))
    else:
        print(report.format_hotspots_table(results))
    return 0


def _read_sizes(root: Path, paths: Iterable[str]) -> dict[str, int]:
    """Line counts of files that still exist under root; others are omitted."""
    return {
        path: _count_lines((root / path).read_bytes())
        for path in paths
        if (root / path).is_file()
    }


def _count_lines(data: bytes) -> int:
    lines = data.count(b"\n")
    return lines + 1 if data and not data.endswith(b"\n") else lines
