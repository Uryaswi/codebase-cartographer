"""Run and parse `git log`. The ONLY module allowed to call subprocess."""

import re
import subprocess
from datetime import date
from pathlib import Path

from cartographer.models import Commit, FileChange

GIT_LOG_ARGS = (
    "log",
    "--no-merges",
    "--numstat",
    "--date=short",
    "--pretty=format:--%h--%ad--%aN",
)

_BRACE_RENAME = re.compile(r"\{([^{}]*) => ([^{}]*)\}")


def load_commits(repo_path: str | Path = ".") -> list[Commit]:
    """Run git log in repo_path and parse the output into commits."""
    result = subprocess.run(
        ["git", "-C", str(repo_path), *GIT_LOG_ARGS],
        capture_output=True,
        text=True,
        check=True,
    )
    return parse_log(result.stdout)


def parse_log(text: str) -> list[Commit]:
    """Parse git log output (see architecture.md) into Commit objects."""
    commits: list[Commit] = []
    header: tuple[str, date, str] | None = None
    changes: list[FileChange] = []
    for line in text.splitlines():
        if line.startswith("--"):
            if header is not None:
                commits.append(Commit(*header, changes=tuple(changes)))
            header, changes = _parse_header(line), []
        elif line.strip() and header is not None:
            changes.append(_parse_numstat(line))
    if header is not None:
        commits.append(Commit(*header, changes=tuple(changes)))
    return commits


def _parse_header(line: str) -> tuple[str, date, str]:
    _, sha, day, author = line.split("--", maxsplit=3)
    return sha, date.fromisoformat(day), author


def _parse_numstat(line: str) -> FileChange:
    added, deleted, path = line.split("\t", maxsplit=2)
    return FileChange(
        path=resolve_rename(path),
        added=_count(added),
        deleted=_count(deleted),
    )


def _count(value: str) -> int:
    """Numstat counts; `-` marks a binary file and counts as 0."""
    return 0 if value == "-" else int(value)


def resolve_rename(path: str) -> str:
    """Return the NEW path for rename notation, else the path unchanged.

    Handles `old => new` and `dir/{old => new}/file`.
    """
    if _BRACE_RENAME.search(path):
        new_path = _BRACE_RENAME.sub(lambda m: m.group(2), path)
        return new_path.replace("//", "/").lstrip("/")
    if " => " in path:
        return path.split(" => ", maxsplit=1)[1]
    return path


def repo_root(repo_path: str | Path = ".") -> Path:
    """Top-level directory of the repository containing repo_path.

    git log paths are relative to this root, not to repo_path.
    """
    result = subprocess.run(
        ["git", "-C", str(repo_path), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(result.stdout.strip())
