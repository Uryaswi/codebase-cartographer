from datetime import date
from pathlib import Path

import pytest

from cartographer.gitlog import parse_log, resolve_rename
from cartographer.models import Commit, FileChange

FIXTURE = Path(__file__).parent.parent / "fixtures" / "sample_log.txt"


@pytest.fixture
def commits() -> list[Commit]:
    return parse_log(FIXTURE.read_text())


def test_parses_every_commit_in_order(commits: list[Commit]) -> None:
    assert [c.hash for c in commits] == ["a1b2c3d", "e4f5a6b", "c7d8e9f", "0a1b2c3"]


def test_parses_header_fields(commits: list[Commit]) -> None:
    first = commits[0]
    assert first.date == date(2026, 11, 20)
    assert first.author == "Ada Lovelace"


def test_parses_numstat_counts(commits: list[Commit]) -> None:
    assert commits[0].changes[0] == FileChange("src/app.py", 12, 3)


def test_binary_file_counts_as_zero_lines(commits: list[Commit]) -> None:
    assert commits[0].changes[1] == FileChange("assets/logo.png", 0, 0)


def test_brace_rename_recorded_under_new_path(commits: list[Commit]) -> None:
    assert commits[0].changes[2].path == "src/new/util.py"


def test_plain_rename_recorded_under_new_path(commits: list[Commit]) -> None:
    assert commits[1].changes[1].path == "docs/manual.md"


def test_commit_without_file_changes(commits: list[Commit]) -> None:
    assert commits[3].changes == ()


def test_empty_input_returns_no_commits() -> None:
    assert parse_log("") == []


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("src/app.py", "src/app.py"),
        ("old.py => new.py", "new.py"),
        ("src/{old => new}/util.py", "src/new/util.py"),
        ("lib/{ => core}/helpers.py", "lib/core/helpers.py"),
        ("lib/{core => }/helpers.py", "lib/helpers.py"),
        ("{a => b}/x.py", "b/x.py"),
    ],
)
def test_resolve_rename(raw: str, expected: str) -> None:
    assert resolve_rename(raw) == expected
