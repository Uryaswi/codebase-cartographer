from pathlib import Path

import pytest

from cartographer.cli import main
from tests.cli.gitrepo import commit_files, git


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    git(tmp_path, "init", "-q")
    commit_files(tmp_path, "Ada", "2026-01-01", {"a.py": "1\n", "src/b.py": "1\n"})
    commit_files(tmp_path, "Alan", "2026-02-01", {"a.py": "1\n2\n"})
    return tmp_path


def test_summary_prints_totals(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["summary", "--repo", str(repo)]) == 0
    out = capsys.readouterr().out
    assert "Commits:      2" in out
    assert "Authors:      2" in out
    assert "Files:        2" in out
    assert "First commit: 2026-01-01" in out
    assert "Last commit:  2026-02-01" in out


def test_summary_reports_git_errors(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["summary", "--repo", str(tmp_path)]) == 1
    assert "error:" in capsys.readouterr().err
