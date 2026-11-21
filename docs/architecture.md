# Architecture — Codebase Cartographer

## Layout
```
cartographer/
  __init__.py
  __main__.py       # enables `python -m cartographer`
  models.py         # dataclasses: FileChange, Commit, HotspotResult, CouplingResult
  gitlog.py         # ONLY module that runs subprocess; runs + parses git log
  analysis/
    __init__.py
    hotspots.py     # pure functions
    coupling.py     # pure functions
  report.py         # formats results as table text or JSON
  cli.py            # argparse; thin: parse args -> gitlog -> analysis -> report
tests/
  fixtures/         # sample git log text files
  unit/             # pure function tests (no git, no filesystem)
  cli/              # end-to-end tests using a temp git repo (tmp_path)
```

## Data flow
```
git log (subprocess)  ->  parse_log(text) -> list[Commit]
                                    |
                     analysis.* (pure: list[Commit] in, results out)
                                    |
                     report.* (table / JSON)  ->  stdout
```

## Git log format
```
git log --no-merges --numstat --date=short --pretty=format:'--%h--%ad--%aN'
```
Example output:
```
--a1b2c3d--2026-11-20--Ada Lovelace
12	3	src/app.py
-	-	assets/logo.png
4	0	src/{old => new}/util.py

--e4f5a6b--2026-11-19--Alan Turing
1	1	README.md
```
- Header lines start with `--`; split with `maxsplit=3`.
- Numstat lines: `added<TAB>deleted<TAB>path`; `-` means binary -> 0.
- Blank lines separate commits.

## Models
```python
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
class CouplingResult:
    file_a: str
    file_b: str
    shared: int
    revs_a: int
    revs_b: int
    degree: int
    cross_module: bool
```

## Key decisions
1. **Analysis functions are pure.** They take `list[Commit]` and return results.
   No subprocess, no file reads, no clock. This keeps them fast and trivially
   testable, which is what makes TDD practical here.
2. **One I/O boundary.** Only `gitlog.py` shells out to git. Hotspots needs
   current file sizes, so the CLI reads sizes and passes a `dict[str, int]`
   into the pure hotspot function.
3. **Standard library only at runtime** (argparse, subprocess, dataclasses,
   fnmatch, json). Dev dependencies: pytest, ruff. No GitPython.
4. **Integer math for scores** to avoid float rounding surprises in tests.
