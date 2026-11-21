"""Format results for the terminal."""

import json
from dataclasses import asdict

from cartographer.models import Commit, HotspotResult

_HOTSPOT_COLUMNS = ("PATH", "REVISIONS", "CHURN", "SIZE", "SCORE")


def format_summary(commits: list[Commit]) -> str:
    """Totals for commits, authors, files, and the date range."""
    if not commits:
        return "No commits found."
    authors = {c.author for c in commits}
    files = {fc.path for c in commits for fc in c.changes}
    dates = [c.date for c in commits]
    lines = [
        f"Commits:      {len(commits)}",
        f"Authors:      {len(authors)}",
        f"Files:        {len(files)}",
        f"First commit: {min(dates).isoformat()}",
        f"Last commit:  {max(dates).isoformat()}",
    ]
    return "\n".join(lines)


def format_hotspots_table(results: list[HotspotResult]) -> str:
    """Aligned table: path left-aligned, numbers right-aligned."""
    if not results:
        return "No hotspots found."
    rows = [
        (r.path, str(r.revisions), str(r.churn), str(r.size), str(r.score))
        for r in results
    ]
    widths = [max(len(row[i]) for row in [_HOTSPOT_COLUMNS, *rows]) for i in range(5)]
    return "\n".join(_table_line(row, widths) for row in [_HOTSPOT_COLUMNS, *rows])


def _table_line(cells: tuple[str, ...], widths: list[int]) -> str:
    first, *numbers = cells
    parts = [first.ljust(widths[0])]
    parts += [
        cell.rjust(width) for cell, width in zip(numbers, widths[1:], strict=True)
    ]
    return "  ".join(parts)


def format_hotspots_json(results: list[HotspotResult]) -> str:
    return json.dumps([asdict(r) for r in results], indent=2)
