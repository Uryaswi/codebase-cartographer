"""Helpers for building real git repositories in CLI tests."""

import subprocess
from pathlib import Path


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


def commit_files(repo: Path, author: str, day: str, files: dict[str, str]) -> None:
    """Write files (relative path -> content) and commit them as author on day."""
    for name, content in files.items():
        path = repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    git(repo, "add", "-A")
    git(
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
