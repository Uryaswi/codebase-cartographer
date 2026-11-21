from datetime import date

from cartographer.analysis.hotspots import count_churn, count_revisions, rank_hotspots
from cartographer.models import Commit, FileChange, HotspotResult


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


def _touch(*paths: str) -> Commit:
    """A commit adding one line to each path."""
    return _commit(*((path, 1, 0) for path in paths))


def test_score_is_revisions_times_size() -> None:
    commits = [_touch("a.py"), _touch("a.py"), _touch("b.py")]
    results = rank_hotspots(commits, {"a.py": 10, "b.py": 50})
    assert results == [
        HotspotResult(path="b.py", revisions=1, churn=1, size=50, score=50),
        HotspotResult(path="a.py", revisions=2, churn=2, size=10, score=20),
    ]


def test_files_missing_from_sizes_are_skipped() -> None:
    commits = [_touch("kept.py", "deleted.py")]
    results = rank_hotspots(commits, {"kept.py": 5})
    assert [r.path for r in results] == ["kept.py"]


def test_equal_scores_are_ordered_by_path() -> None:
    commits = [_touch("c.py", "a.py", "b.py")]
    results = rank_hotspots(commits, {"a.py": 4, "b.py": 4, "c.py": 4})
    assert [r.path for r in results] == ["a.py", "b.py", "c.py"]


def test_top_limits_number_of_results() -> None:
    paths = [f"f{i}.py" for i in range(5)]
    commits = [_touch(*paths)]
    results = rank_hotspots(commits, dict.fromkeys(paths, 1), top=2)
    assert len(results) == 2


def test_default_top_is_ten() -> None:
    paths = [f"f{i:02}.py" for i in range(12)]
    results = rank_hotspots([_touch(*paths)], dict.fromkeys(paths, 1))
    assert len(results) == 10


def test_exclude_globs_remove_matching_files() -> None:
    paths = ["src/app.py", "poetry.lock", "vendor/deps.lock", "docs/guide.md"]
    commits = [_touch(*paths)]
    results = rank_hotspots(
        commits, dict.fromkeys(paths, 1), exclude=("*.lock", "docs/*")
    )
    assert [r.path for r in results] == ["src/app.py"]


def test_no_commits_yields_no_hotspots() -> None:
    assert rank_hotspots([], {"a.py": 3}) == []
