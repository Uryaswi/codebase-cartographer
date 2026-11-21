# Plan: F2 Hotspots (`carto hotspots`)

## Context
PRD F2: find files that are both large and frequently changed. This is HW4 Part 2
(Explore → Plan → Implement → Commit), so the git history must show the plan
committed first, then small feature commits. The work is tracked by GitHub issues
#1 (plan), #2 (revisions + churn), #3 (scoring), and #4 (CLI).

Constraints from the PRD, architecture.md, and CLAUDE.final.md:
- `cartographer/analysis/` is pure: no subprocess, no file I/O.
- `gitlog.py` is the only module that may call subprocess.
- The CLI reads file sizes and passes a `dict[str, int]` into analysis.
- Integer math, keyword-only options, type hints everywhere, and functions under
  about 30 lines.

## Design

### `cartographer/models.py`
Add `HotspotResult(path: str, revisions: int, churn: int, size: int, score: int)`
as a frozen dataclass.

### `cartographer/analysis/hotspots.py` (pure)
- `count_revisions(commits: list[Commit]) -> dict[str, int]`: count each commit
  once per distinct path, using a set of paths per commit.
- `count_churn(commits: list[Commit]) -> dict[str, int]`: sum of added + deleted.
  Binary files are already 0/0 from the parser.
- `rank_hotspots(commits, sizes: Mapping[str, int], *, top: int = 10,
  exclude: Sequence[str] = ()) -> list[HotspotResult]`
  - Drop paths that match any `exclude` glob (`fnmatch`).
  - Skip paths missing from `sizes`, meaning deleted files or paths only seen
    before a rename.
  - `score = revisions * size`. Sort by `(-score, path)` and return the first
    `top` results.
  - Helper: `_is_excluded(path, patterns) -> bool`.

### `cartographer/gitlog.py`
- `repo_root(repo_path) -> Path`: runs `git -C <repo> rev-parse --show-toplevel`.
  Git reports paths relative to the repo root, so sizes must be read from the
  root even when `--repo` points at a subdirectory.

### `cartographer/cli.py`
- `hotspots` subcommand with these options:
  - `--repo` (default `.`)
  - `--top` (positive int, default 10)
  - `--exclude` (`nargs="+"`, `action="extend"`, default `[]`, so both
    `--exclude a b` and repeated flags work)
  - `--json`
- `_read_sizes(root: Path, paths: Iterable[str]) -> dict[str, int]`: for each
  path that is a regular file under the root, count lines by reading bytes and
  counting `b"\n"`, plus 1 if the file is non-empty and has no trailing newline.
  Reading bytes avoids decode errors on binary files.
- Split dispatch into `_run_summary(args)` and `_run_hotspots(args)` so `main`
  stays short.

### `cartographer/report.py`
- `format_hotspots_table(results) -> str`: aligned columns PATH, REVISIONS,
  CHURN, SIZE, SCORE. Prints "No hotspots found." when the list is empty.
- `format_hotspots_json(results) -> str`: `json.dumps([asdict(r) ...], indent=2)`.

## Edge cases → tests
| Case | Expected |
|---|---|
| File touched in 3 commits | revisions 3 |
| Binary file (0/0 numstat) | churn 0, still counts as a revision |
| File in history but not on disk | skipped |
| Equal scores | ordered by path ascending |
| `--top 2` with 5 candidates | 2 results |
| `exclude=("*.lock", "docs/*")` | matching paths removed, including nested `a/b.lock` (fnmatch `*` matches `/`) |
| No commits / no surviving files | empty list; table says "No hotspots found."; JSON prints `[]` |
| File with no trailing newline | line count includes the last line |
| `--repo` points at a subdirectory | sizes are still resolved from the repo root |

## Tests
- `tests/unit/test_hotspots.py` (new). Commits are built by hand with a local
  `_commit(*paths)` helper. The shared `make_commit` helper is left for the
  coupling TDD refactor step.
- `tests/unit/test_report.py` (new): checks table columns, ordering, and that
  the JSON round-trips.
- `tests/cli/gitrepo.py` (new): move the `_git` and `_commit` helpers out of
  `test_summary.py` so both CLI test files share them.
- `tests/cli/test_hotspots.py` (new): runs against a temp git repo and covers
  the table output, `--top`, `--exclude`, `--json`, a deleted file, and
  `--repo` set to a subdirectory.

## Commits
0. `docs: add implementation plan for hotspots feature`. Save this plan to
   `docs/plans/hotspots.md`. Refs #1.
1. `feat(hotspots): compute per-file revisions and churn`. Adds
   `count_revisions`, `count_churn`, and unit tests. Closes #2.
2. `feat(hotspots): score and rank hotspots with excludes and tie-breaking`.
   Adds `HotspotResult` and `rank_hotspots` with unit tests. Closes #3.
3. `test: share temp git repo helpers across CLI tests`. A pure move; tests
   stay green.
4. `feat(cli): add carto hotspots command with --top, --exclude, --json`. Adds
   `repo_root`, `_read_sizes`, the report formatters, and CLI and report tests.
   Closes #4 and #1.

Run `pytest -q`, `ruff check .`, and `ruff format --check .` before every commit.

## Verification
- `pytest -q` passes, and `ruff check .` and `ruff format --check .` are clean.
- `carto hotspots --top 5` on this repo shows a sensible table.
- `carto hotspots --json | python -m json.tool` produces valid JSON.
- `carto hotspots --exclude "docs/*" "*.md"` hides the doc files.
- `carto hotspots --repo cartographer` (a subdirectory) gives the same paths as
  running from the repo root.
- `grep -rn "subprocess\|open(\|read_" cartographer/analysis` returns nothing,
  which confirms analysis stays pure.
- After the user pushes, the CI run is green.
