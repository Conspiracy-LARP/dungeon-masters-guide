"""Guards on the formatter and type-checker gates themselves — that they are not vacuous.

WP08 wires `black --check .` and `mypy .` into CI's verify job, and WP03-WP06 inherit
this repo's `pyproject.toml`. A gate that inspects nothing still exits 0, so CI stays
green while the code rots behind it. That is worse than having no gate, because it looks
like one.

This is not hypothetical. Black's `DEFAULT_EXCLUDES` regex contains `build`, so with a
default configuration `black --check .` silently skipped `src/build/` — every module in
the only Python package in the repo — reported "5 files would be left unchanged", and
exited 0 while three of the skipped files genuinely violated black. The `[tool.black]
exclude` key in `pyproject.toml` overrides that default. These tests exist so that if
anyone removes or narrows it, a test fails and names the files that fell out, rather than
the gate quietly re-hollowing.

The same guard is applied to mypy for symmetry. Mypy has no such trap today — it takes an
explicit `files = ["src/build", "tests"]` rather than walking the tree with a default
exclude list — but "has no trap today" is exactly the claim worth pinning down.

These mirror `test_the_allow_list_contains_no_wildcards` and
`test_the_allow_list_does_not_swallow_the_output_root` in test_provenance.py: same job,
one layer up. Those keep the provenance check honest; these keep the toolchain honest.
"""

from __future__ import annotations

import re
import subprocess
import sys
import tomllib
from pathlib import Path

#: Directories that legitimately hold no first-party source. Everything else under the
#: repo root that ends in `.py` is code a gate is supposed to look at.
_NOT_SOURCE = frozenset({".git", ".venv", ".mypy_cache", ".pytest_cache", "site", "__pycache__"})


def _first_party_python_files(repo_root: Path) -> set[Path]:
    """Every Python file in the repo that a gate ought to inspect, found independently.

    Deliberately does NOT ask black or mypy what they see — that would be circular. This
    walks the tree itself, so it can be compared against what the tools report.
    """
    return {
        path.relative_to(repo_root)
        for path in repo_root.rglob("*.py")
        if not (_NOT_SOURCE & set(path.relative_to(repo_root).parts))
    }


def _black_exclude(repo_root: Path) -> str:
    """The `[tool.black] exclude` pattern, or a clear failure if it is gone.

    A *missing* key is the regression, not an error condition: black then falls back to
    DEFAULT_EXCLUDES and silently skips src/build/. Say so, rather than raising KeyError
    at whoever deleted the line.
    """
    with (repo_root / "pyproject.toml").open("rb") as handle:
        black_config = tomllib.load(handle)["tool"].get("black", {})

    exclude = black_config.get("exclude")
    assert exclude is not None, (
        "[tool.black] has no `exclude` key. Black then falls back to DEFAULT_EXCLUDES, "
        "which contains 'build' and silently skips src/build/ — the whole package. The "
        "gate would exit 0 having inspected almost nothing. Restore the key."
    )
    assert isinstance(exclude, str)
    return exclude


def _run(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Run a tool from this interpreter's environment, from the repo root."""
    return subprocess.run(
        [sys.executable, "-m", *args],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )


# --------------------------------------------------------------------------------------
# The formatter gate
# --------------------------------------------------------------------------------------


def test_the_black_gate_inspects_every_python_file(repo_root: Path) -> None:
    """The regression guard: `black --check .` must count every file we can find.

    This is the test that catches a re-exclusion. If someone drops the `exclude` key from
    `[tool.black]`, black's DEFAULT_EXCLUDES swallows `src/build/` and the count drops
    from 11 to 5 — while the command still exits 0.
    """
    expected = _first_party_python_files(repo_root)
    assert len(expected) > 5, "sanity: the repo has more than the non-src/build files"

    result = _run(repo_root, "black", "--check", ".")
    # Black writes its summary to stderr, in the shape
    # "3 files would be reformatted, 8 files would be left unchanged."
    counts = [int(n) for n in re.findall(r"(\d+) files? would be", result.stderr)]
    assert counts, f"could not parse a file count from black's summary: {result.stderr!r}"

    assert sum(counts) == len(expected), (
        f"black inspected {sum(counts)} files but the repo has {len(expected)}. "
        f"Something is being silently skipped — check `exclude` in [tool.black]. "
        f"Files found: {sorted(str(p) for p in expected)}"
    )


def test_the_black_exclude_does_not_skip_the_build_package(repo_root: Path) -> None:
    """The config-level guard: the exclude regex must not match the authoritative surface.

    Fails fast and names the pattern, where the count test above only reports a number.
    """
    pattern = _black_exclude(repo_root)
    compiled = re.compile(pattern)
    build_modules = sorted(
        p for p in _first_party_python_files(repo_root) if p.parts[:2] == ("src", "build")
    )
    assert build_modules, "sanity: src/build/ contains Python modules"

    for module in build_modules:
        # Black matches its exclude regex against the "/"-prefixed posix path.
        assert not compiled.search(f"/{module.as_posix()}"), (
            f"the [tool.black] exclude pattern {pattern!r} skips {module} — "
            f"src/build/ is the code the formatter exists to format"
        )


def test_the_black_exclude_is_not_a_wildcard(repo_root: Path) -> None:
    """An exclude that matches everything is the same vacuity by the opposite route."""
    pattern = _black_exclude(repo_root)
    compiled = re.compile(pattern)
    for benign in ("/src/build/roles.py", "/tests/test_roles.py", "/src/build/cli.py"):
        assert not compiled.search(benign), f"{pattern!r} swallows {benign}"


def test_the_repo_is_black_clean(repo_root: Path) -> None:
    """T005's success criterion, asserted rather than assumed.

    Meaningful only because the tests above prove the gate is looking at something.
    """
    result = _run(repo_root, "black", "--check", ".")
    assert result.returncode == 0, f"black --check . failed:\n{result.stderr}"


# --------------------------------------------------------------------------------------
# The type-checker gate
# --------------------------------------------------------------------------------------


def test_the_mypy_gate_covers_the_build_package(repo_root: Path) -> None:
    """Mypy takes an explicit `files=`, so it has no DEFAULT_EXCLUDES trap. Pin that down."""
    with (repo_root / "pyproject.toml").open("rb") as handle:
        mypy_config = tomllib.load(handle)["tool"]["mypy"]

    assert "src/build" in mypy_config["files"], (
        "mypy's `files` must name src/build explicitly — that explicitness is precisely "
        "what keeps it clear of the trap black fell into"
    )
    compiled = re.compile(mypy_config["exclude"])
    for module in ("src/build/roles.py", "src/build/cli.py", "src/build/provenance.py"):
        assert not compiled.match(module), f"mypy's exclude skips {module}"


def test_the_mypy_gate_inspects_every_python_file(repo_root: Path) -> None:
    """Mypy must report the same file count we found ourselves.

    Today every Python file in the repo lives under `src/build/` or `tests/`, so mypy's
    explicit `files` happens to cover all of them. If that stops being true this test
    fires — which is the point: Python that no type-checker looks at is the same vacuity
    in a different costume.
    """
    expected = _first_party_python_files(repo_root)
    result = _run(repo_root, "mypy", ".")

    found = re.search(r"(\d+) source files?", result.stdout)
    assert found, f"could not parse a file count from mypy's summary: {result.stdout!r}"

    assert int(found.group(1)) == len(expected), (
        f"mypy inspected {found.group(1)} files but the repo has {len(expected)}. "
        f"Either add the new location to `files` in [tool.mypy] so it is checked, or "
        f"add it to `exclude` and to _NOT_SOURCE here to say so deliberately — but do "
        f"not leave Python sitting outside the gate by accident.\n"
        f"Files found: {sorted(str(p) for p in expected)}"
    )
