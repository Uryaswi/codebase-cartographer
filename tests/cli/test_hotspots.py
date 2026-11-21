import json
from pathlib import Path

import pytest

from cartographer.cli import main
from tests.cli.gitrepo import commit_files, git


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """Scores (revisions x size):
    - big.py: 2 x 4 lines = 8 (churn 1 + 3)
    - small.py: 3 x 1 line = 3 (no trailing newline)
    - docs/notes.md: 1 x 2 lines = 2
    - gone.py: deleted, so skipped
    """
    git(tmp_path, "init", "-q")
    commit_files(tmp_path, "Ada", "2026-01-01", {"small.py": "a", "gone.py": "x\n"})
    commit_files(tmp_path, "Ada", "2026-01-02", {"small.py": "b", "big.py": "1\n"})
    commit_files(
        tmp_path,
        "Ada",
        "2026-01-03",
        {"small.py": "c", "big.py": "1\n2\n3\n4\n", "docs/notes.md": "x\ny\n"},
    )
    (tmp_path / "gone.py").unlink()
    commit_files(tmp_path, "Ada", "2026-01-04", {})
    return tmp_path


def _run(capsys: pytest.CaptureFixture[str], *args: str) -> str:
    assert main(["hotspots", *args]) == 0
    return capsys.readouterr().out


def _json(capsys: pytest.CaptureFixture[str], *args: str) -> list[dict[str, object]]:
    return json.loads(_run(capsys, *args, "--json"))


def test_table_lists_hotspots_by_score(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    lines = _run(capsys, "--repo", str(repo)).splitlines()
    assert lines[0].split() == ["PATH", "REVISIONS", "CHURN", "SIZE", "SCORE"]
    assert [line.split()[0] for line in lines[1:]] == [
        "big.py",
        "small.py",
        "docs/notes.md",
    ]


def test_json_reports_all_fields(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    data = _json(capsys, "--repo", str(repo))
    assert data[0] == {
        "path": "big.py",
        "revisions": 2,
        "churn": 4,
        "size": 4,
        "score": 8,
    }


def test_deleted_files_are_skipped(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    paths = [item["path"] for item in _json(capsys, "--repo", str(repo))]
    assert "gone.py" not in paths


def test_top_limits_results(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert len(_json(capsys, "--repo", str(repo), "--top", "1")) == 1


def test_exclude_accepts_multiple_globs(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    data = _json(capsys, "--repo", str(repo), "--exclude", "docs/*", "big.*")
    assert [item["path"] for item in data] == ["small.py"]


def test_repo_subdirectory_reads_sizes_from_root(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    data = _json(capsys, "--repo", str(repo / "docs"))
    assert [item["path"] for item in data] == ["big.py", "small.py", "docs/notes.md"]


def test_top_must_be_positive(repo: Path) -> None:
    with pytest.raises(SystemExit):
        main(["hotspots", "--repo", str(repo), "--top", "0"])
