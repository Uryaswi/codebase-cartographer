"""Hotspot analysis (PRD F2). Pure: list[Commit] in, results out."""

from collections import Counter

from cartographer.models import Commit


def count_revisions(commits: list[Commit]) -> dict[str, int]:
    """Number of commits touching each file (each commit counted once per file)."""
    revisions: Counter[str] = Counter()
    for commit in commits:
        revisions.update({change.path for change in commit.changes})
    return dict(revisions)


def count_churn(commits: list[Commit]) -> dict[str, int]:
    """Total lines added + deleted per file across all commits."""
    churn: Counter[str] = Counter()
    for commit in commits:
        for change in commit.changes:
            churn[change.path] += change.added + change.deleted
    return dict(churn)
