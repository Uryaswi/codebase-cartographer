# Codebase Cartographer — Product Requirements

## Problem
Every codebase has risk that's invisible in the code itself: files that secretly
depend on each other, files that change constantly, and areas only one person
understands. That information is sitting in the git history, but nobody reads
thousands of commits. Cartographer mines git history and maps that hidden risk.

## Users
- Developers joining an unfamiliar codebase ("where are the landmines?")
- Tech leads deciding what to refactor first
- Students and reviewers analyzing their own projects

## Interface
A command-line tool, run inside (or pointed at) any git repository:

```
carto summary   [--repo PATH]
carto hotspots  [--repo PATH] [--top N] [--exclude GLOB ...] [--json]
carto coupling  [--repo PATH] [--min-shared N] [--min-degree PCT]
                [--max-changeset N] [--exclude GLOB ...] [--json]
```

---

## F1 — Git history ingestion + `summary` (scaffold)
- Runs `git log` (format defined in architecture.md) and parses it into `Commit` objects.
- `carto summary` prints: total commits, number of distinct authors,
  number of distinct files touched, first and last commit date.
- Binary files (numstat `-`) count as 0 lines added/deleted.
- Renames (`old => new`, `dir/{old => new}/file`) are recorded under the NEW path.

## F2 — Hotspots (Part 2 feature: Explore → Plan → Implement → Commit)
A hotspot is a file that is both large and frequently changed; these are where
bugs concentrate.
- `revisions(f)` = number of commits touching file f.
- `churn(f)` = total lines added + deleted for f across all commits.
- `size(f)` = current number of lines of f in the working tree.
  Files that no longer exist are skipped.
- `score(f)` = `revisions(f) * size(f)`.
- Output: top N files (default 10) sorted by score desc, then path asc,
  showing path, revisions, churn, size, score.
- `--exclude` globs (e.g. `*.lock`, `docs/*`) remove matching files.
- `--json` outputs the same data as a JSON array.

## F3 — Change Coupling (Part 3 feature: strict TDD)
Files that repeatedly change in the same commits are coupled, even when no
import links them. Coupling across modules is the most dangerous kind,
because it's invisible when reading the code.

Definitions (computed AFTER exclusions and large-commit filtering):
- `revs(f)` = number of commits touching f.
- `shared(a, b)` = number of commits touching both a and b.
- `degree(a, b)` = `(200 * shared) // (revs(a) + revs(b))`
  (integer percent; shared divided by average revisions, rounded down).

Acceptance criteria:
- **AC1 — Pair counting.** For each commit, every unordered pair of distinct
  files is counted once. Pairs are stored with `file_a < file_b`
  (alphabetical). A file is never paired with itself. A commit touching
  one file produces no pairs.
- **AC2 — Coupling degree.** Each result reports `shared`, `revs_a`, `revs_b`,
  and `degree` using the formula above.
- **AC3 — Large commits ignored.** Commits touching more than
  `max_changeset_size` files (default 30) are excluded entirely, from both
  `revs` and `shared`. These are usually bulk reformatting or renames, not
  real coupling.
- **AC4 — Thresholds and ordering.** Only pairs with
  `shared >= min_shared` (default 3) AND `degree >= min_degree` (default 30)
  are returned, sorted by degree desc, then shared desc, then file_a asc,
  then file_b asc.
- **AC5 — Exclusions.** Files matching any `exclude` glob are removed from
  each commit BEFORE the changeset-size check and before counting.
- **AC6 — Cross-module flag.** Each result has `cross_module = True` when the
  two files have different top-level directories. Files at the repository
  root belong to module `"."`.
- **AC7 (CLI, not TDD-critical).** `carto coupling` prints results as a table
  (cross-module pairs marked with `⚠`) or JSON with `--json`.

## F4 — Knowledge risk / bus factor (future, out of scope for HW4)
Per file: share of commits by top author; flag files where one author
made ≥ 80% of commits.

## Non-goals
- No GUI or web UI.
- No network access, no GitHub API: local git history only.
- No language-specific parsing (size is plain line count).
