---
affected_files: []
cycle_number: 2
mission_slug: guide-site-build-01KXP76R
reproduction_command:
reviewed_at: '2026-07-16T22:20:00Z'
reviewer_agent: reviewer-renata
verdict: approved
wp_id: WP02
---

# WP02 — Review cycle 2 (re-review of the cycle-1 fix)

**Verdict**: approved. The blocking finding is resolved, the guard demonstrably fires, and
nothing regressed. Scope was the cycle-1 finding only; the previously adjudicated items were
not relitigated.

---

## The blocking finding is resolved — the black gate is live

`[tool.black] exclude` now replaces black's `DEFAULT_EXCLUDES`, and `src/build/` is no longer
skipped. I verified the file count **independently rather than asking black**:

```
git ls-files '*.py' | wc -l   → 12
find . -name '*.py' -not -path './.git/*' -not -path './.venv/*' \
  -not -path '*/__pycache__/*' -not -path './site/*' | wc -l   → 12
poetry run black --check .    → "12 files would be left unchanged", exit 0
```

12 = the 11 files of cycle 1 plus the new `tests/test_toolchain.py`. The tool's count matches
the tree walk exactly. `black --check . --verbose` now ignores only `.pytest_cache`,
`.mypy_cache` and `.venv` — `src/build` no longer appears in the ignore list.

## The guard fires — both re-exclusion routes reproduced

This was the heart of the re-review, and I reproduced **both** routes myself rather than
accepting the report.

**Route 1 — delete the `exclude` key.** Black silently drops to **6 files and still exits 0**
(precisely the original defect). Three tests fail:

```
AssertionError: black inspected 6 files but the repo has 12. Something is being silently
skipped — check `exclude` in [tool.black]. Files found: ['src/build/__init__.py', ...]

AssertionError: [tool.black] has no `exclude` key. Black then falls back to DEFAULT_EXCLUDES,
which contains 'build' and silently skips src/build/ — the whole package. The gate would exit
0 having inspected almost nothing. Restore the key.
```

**Route 2 — narrow the pattern to re-add `build`.** Same three tests fail, naming the pattern
and the module it swallows:

```
AssertionError: the [tool.black] exclude pattern '/(\\.git|...|site|build)/' skips
src/build/__init__.py — src/build/ is the code the formatter exists to format
```

A missing key is handled as a *finding* rather than a `KeyError` at whoever deleted the line —
the right call, since the missing key IS the regression.

## The count test is genuinely non-circular

Confirmed by reading `_first_party_python_files`: it `rglob`s the tree and filters against a
hand-maintained `_NOT_SOURCE` frozenset. It never asks black or mypy what they saw, and its
docstring says so explicitly. The comparison is therefore tool-report vs. independent walk —
the one shape that cannot pass vacuously. Had it asked black how many files black checked, it
would have reproduced the exact defect under repair.

`_NOT_SOURCE` is maintained by hand, so someone could in principle silence the test by adding a
directory to both it and the exclude pattern — but that is a deliberate, visible act, and the
mypy guard's failure message names it as the legitimate escape hatch ("add it to `exclude` and
to `_NOT_SOURCE` here to say so deliberately — but do not leave Python sitting outside the gate
by accident"). That is the correct trade.

## The guard's own diagnostic is fixed

The reported `NameError` in the wildcard test's failure message is gone. Making the guard fire
(route 2) yields a clean `AssertionError` naming the pattern and the swallowed path —
`'/(...|build)/' swallows /src/build/roles.py` — not a traceback. Verified, not taken on report.
The message is the value of a guard, and this one now delivers one.

## Everything else — re-verified, green

| Check | Result |
|---|---|
| `poetry run pytest` | **91 passed** (85 + 6 new), as reported |
| `poetry run mypy .` | `Success: no issues found in 12 source files` |
| `poetry run black --check .` | 12 files, exit 0 |
| `poetry run guide roles lint` (real pack) | `OK: 12 documents, all declared (10 chapters, 2 not in the book)`, exit 0 |
| `poetry run guide roles check-drift` (real pack) | `OK: the prose lists agree with the declaration`, exit 0 |
| `git diff --stat src/pack/` + `git status --porcelain src/pack/` | both empty — the pack is untouched |
| Reformatting semantics | `cli.py`, `config.py`, `roles.py`: pure line-wraps. Verified line by line in the diff — one `click.echo`, one `click.secho`, one `ConfigError` and one `set(...)` call wrapped across lines. No logic, no identifiers, no control flow touched. |
| mypy symmetry | Confirmed: `files = ["src/build", "tests"]` is explicit, `exclude = "^(src/pack|src/theme)/"` matches no build module. No `DEFAULT_EXCLUDES` trap exists for mypy; the guard pins that claim down rather than assuming it. |

## The mkdocs.yml comment corrections are accurate

Both cycle-1 overstatements are fixed, and I verified the underlying claim rather than the
prose. `_pack_files` (src/build/roles.py:62) globs `*.md` only — it `rglob`s `*.md` to reject
nesting, then returns `sorted(p.name for p in pack_dir.glob("*.md"))`. A stray `.css` under
`src/pack/` is invisible to the lint. The comment now correctly states that `extra_css` naming
a missing file exits 0 with a silent 404, and that nothing downstream catches it. The rewrite
also makes the right point: the two hooks fail in *different* ways, and the quiet one is the
dangerous one.

## `tests/test_toolchain.py` outside `owned_files` — accepted

Same basis on which `tests/__init__.py` was accepted in cycle 1: it is inside the lane's
`tests/` scope and it is the guard the review explicitly asked for. The implementer flagged it
rather than passing over it, which is the behaviour I want. Not a finding.

---

The fix is proportionate, the reasoning in the new test module's docstring is honest about what
it does and does not pin down, and the guard was verified to fire before being trusted. The
gate that WP03–WP06 inherit is now a real one.

## Note on the cycle-1 artifact

`review-cycle-1.md` in the repo had lost its YAML frontmatter (verdict in prose only), which
made the transition guard refuse the move with "no parseable review verdict". Repaired by
restoring the harness-written frontmatter (`verdict: rejected`) from the coord worktree copy.
The record of cycle 1 is unchanged in substance.
