from datetime import date

from cartographer.analysis.hotspots import count_churn, count_revisions
from cartographer.models import Commit, FileChange


def _commit(*changes: tuple[str, int, int]) -> Commit:
    """Build a commit from (path, added, deleted) tuples."""
    return Commit(
        hash="abc1234",
        date=date(2026, 1, 1),
        author="Ada",
        changes=tuple(
            FileChange(path, added, deleted) for path, added, deleted in changes
        ),
    )


def test_revisions_count_commits_touching_each_file() -> None:
    commits = [
        _commit(("a.py", 1, 0), ("b.py", 1, 0)),
        _commit(("a.py", 2, 1)),
        _commit(("a.py", 3, 3)),
    ]
    assert count_revisions(commits) == {"a.py": 3, "b.py": 1}


def test_revisions_count_a_file_once_per_commit() -> None:
    commits = [_commit(("a.py", 1, 0), ("a.py", 2, 0))]
    assert count_revisions(commits) == {"a.py": 1}


def test_churn_sums_added_and_deleted_lines() -> None:
    commits = [_commit(("a.py", 10, 2)), _commit(("a.py", 3, 5), ("b.py", 1, 1))]
    assert count_churn(commits) == {"a.py": 20, "b.py": 2}


def test_binary_file_has_zero_churn_but_counts_as_revision() -> None:
    commits = [_commit(("logo.png", 0, 0)), _commit(("logo.png", 0, 0))]
    assert count_churn(commits) == {"logo.png": 0}
    assert count_revisions(commits) == {"logo.png": 2}


def test_no_commits_yields_empty_counts() -> None:
    assert count_revisions([]) == {}
    assert count_churn([]) == {}
