import subprocess
from pathlib import Path

import pytest

from cartographer.cli import main


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


def _commit(repo: Path, author: str, day: str, files: dict[str, str]) -> None:
    for name, content in files.items():
        path = repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    _git(repo, "add", ".")
    _git(
        repo,
        "-c",
        f"user.name={author}",
        "-c",
        "user.email=test@example.com",
        "commit",
        "-q",
        "-m",
        "change",
        f"--date={day}T12:00:00",
    )


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    _git(tmp_path, "init", "-q")
    _commit(tmp_path, "Ada", "2026-01-01", {"a.py": "1\n", "src/b.py": "1\n"})
    _commit(tmp_path, "Alan", "2026-02-01", {"a.py": "1\n2\n"})
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
