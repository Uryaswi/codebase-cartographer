"""Hotspot analysis (PRD F2). Pure: list[Commit] in, results out."""

from collections import Counter
from collections.abc import Mapping, Sequence
from fnmatch import fnmatch

from cartographer.models import Commit, HotspotResult


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


def rank_hotspots(
    commits: list[Commit],
    sizes: Mapping[str, int],
    *,
    top: int = 10,
    exclude: Sequence[str] = (),
) -> list[HotspotResult]:
    """Top files by revisions * current size, ties broken by path.

    Files missing from `sizes` (deleted or renamed away) are skipped.
    """
    revisions = count_revisions(commits)
    churn = count_churn(commits)
    results = [
        HotspotResult(
            path=path,
            revisions=revs,
            churn=churn[path],
            size=sizes[path],
            score=revs * sizes[path],
        )
        for path, revs in revisions.items()
        if path in sizes and not _is_excluded(path, exclude)
    ]
    results.sort(key=lambda r: (-r.score, r.path))
    return results[:top]


def _is_excluded(path: str, patterns: Sequence[str]) -> bool:
    return any(fnmatch(path, pattern) for pattern in patterns)
