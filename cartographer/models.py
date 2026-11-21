"""Immutable data models shared across the package."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class FileChange:
    path: str
    added: int
    deleted: int


@dataclass(frozen=True)
class Commit:
    hash: str
    date: date
    author: str
    changes: tuple[FileChange, ...]


@dataclass(frozen=True)
class HotspotResult:
    path: str
    revisions: int
    churn: int
    size: int
    score: int
