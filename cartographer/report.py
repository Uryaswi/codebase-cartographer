"""Format results for the terminal."""

from cartographer.models import Commit


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
