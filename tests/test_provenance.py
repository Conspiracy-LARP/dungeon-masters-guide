"""Tests for the provenance check (NFR-003, T045).

NFR-003 is the mechanism by which SC-004 ("no two surfaces can disagree") is true by
construction. The test that matters is the one asserting a hand-authored page FAILS.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import pytest
from click.testing import CliRunner

from build.cli import guide
from build.config import BuildConfig
from build.provenance import (
    ALLOWED_GENERATED_FILES,
    ALLOWED_GENERATED_PREFIXES,
    ProvenanceError,
    find_unaccounted,
    verify_provenance,
)


def _build_output(root: Path, extra: dict[str, str] | None = None) -> Path:
    """A plausible built output for the default temporary pack."""
    output = root / "site"
    files = {
        "index.html": "<html>landing</html>",
        "creator-kit/index.html": "<html>kit</html>",
        "getting-started/index.html": "<html>on-ramp</html>",
        "ethics/index.html": "<html>ethics</html>",
        "creator-kit.md": "# Creator Kit",
        "getting-started.md": "# Getting Started",
        "ethics.md": "# Ethics",
        "README.md": "# The kit",
        "AGENTS.md": "# Start here",
        "llms.txt": "index",
        "llms-full.txt": "everything",
        ".nojekyll": "",
        "assets/stylesheets/main.css": "body{}",
        "search/search_index.json": "{}",
    }
    files.update(extra or {})
    for relative, content in files.items():
        path = output / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return output


# --------------------------------------------------------------------------------------
# THE CHECK
# --------------------------------------------------------------------------------------


def test_a_hand_authored_page_fails(tmp_path: Path, pack_config: BuildConfig) -> None:
    """The whole point. NFR-003 forbids published content with no source in the pack."""
    output = _build_output(tmp_path, extra={"about.html": "<html>hand-written</html>"})
    with pytest.raises(ProvenanceError, match=r"about\.html"):
        verify_provenance(output, pack_config)


def test_the_failure_names_the_file_and_says_what_to_do(
    tmp_path: Path, pack_config: BuildConfig
) -> None:
    output = _build_output(tmp_path, extra={"secret-page.html": "<html>x</html>"})
    with pytest.raises(ProvenanceError) as excinfo:
        verify_provenance(output, pack_config)
    message = str(excinfo.value)
    assert "secret-page.html" in message
    assert "NFR-003" in message
    assert "provenance.py" in message  # tells you where to record a real exception


def test_a_hand_authored_markdown_file_fails(tmp_path: Path, pack_config: BuildConfig) -> None:
    """A stray .md is the likeliest form of this mistake: it looks like a pack document."""
    output = _build_output(tmp_path, extra={"extra-notes.md": "# Notes"})
    unaccounted = find_unaccounted(output, pack_config)
    assert [u.relative_path for u in unaccounted] == ["extra-notes.md"]


def test_a_stray_file_in_a_nested_directory_fails(tmp_path: Path, pack_config: BuildConfig) -> None:
    """The allow-list prefixes must not become a hole for arbitrary subdirectories."""
    output = _build_output(tmp_path, extra={"private/notes.html": "<html>x</html>"})
    unaccounted = find_unaccounted(output, pack_config)
    assert [u.relative_path for u in unaccounted] == ["private/notes.html"]


def test_a_clean_output_passes(tmp_path: Path, pack_config: BuildConfig) -> None:
    output = _build_output(tmp_path)
    assert find_unaccounted(output, pack_config) == []
    verify_provenance(output, pack_config)


# --------------------------------------------------------------------------------------
# What legitimately traces back
# --------------------------------------------------------------------------------------


def test_the_bootstrap_is_accounted_for_under_its_published_name(
    tmp_path: Path, pack_config: BuildConfig
) -> None:
    """`AGENTS.md` traces to `start.md` — provenance follows published_name (FR-010)."""
    output = _build_output(tmp_path)
    assert (output / "AGENTS.md").exists()
    assert find_unaccounted(output, pack_config) == []


def test_the_bootstrap_under_its_source_name_is_still_accounted_for(
    tmp_path: Path, pack_config: BuildConfig
) -> None:
    """On main the raw markdown may publish as start.md; both names trace to a document."""
    output = _build_output(tmp_path, extra={"start.md": "# Start here"})
    accounted = [u.relative_path for u in find_unaccounted(output, pack_config)]
    assert "start.md" not in accounted


@pytest.mark.parametrize("filename", sorted(ALLOWED_GENERATED_FILES))
def test_each_allow_listed_artifact_passes(
    filename: str, tmp_path: Path, pack_config: BuildConfig
) -> None:
    output = _build_output(tmp_path, extra={filename: "generated"})
    assert find_unaccounted(output, pack_config) == []


@pytest.mark.parametrize("prefix", ALLOWED_GENERATED_PREFIXES)
def test_each_allow_listed_prefix_passes(
    prefix: str, tmp_path: Path, pack_config: BuildConfig
) -> None:
    output = _build_output(tmp_path, extra={f"{prefix}generated-thing.bin": "x"})
    assert find_unaccounted(output, pack_config) == []


# --------------------------------------------------------------------------------------
# The allow-list itself
# --------------------------------------------------------------------------------------


def test_the_allow_list_contains_no_wildcards() -> None:
    """A wildcard entry defeats the check while looking like one."""
    for entry in ALLOWED_GENERATED_FILES:
        assert "*" not in entry and "?" not in entry, entry
    for prefix in ALLOWED_GENERATED_PREFIXES:
        assert "*" not in prefix and prefix.endswith("/"), prefix


def test_the_allow_list_stays_small() -> None:
    """A guard against the slow slide from 'explicit exception' to 'anything goes'.

    If you are adding the tenth entry, ask whether the artifact should derive from the
    pack instead.
    """
    assert len(ALLOWED_GENERATED_FILES) <= 12
    assert len(ALLOWED_GENERATED_PREFIXES) <= 4


def test_the_allow_list_does_not_swallow_the_output_root() -> None:
    """`""` or `"/"` as a prefix would allow everything."""
    assert "" not in ALLOWED_GENERATED_PREFIXES
    assert "/" not in ALLOWED_GENERATED_PREFIXES
    assert "./" not in ALLOWED_GENERATED_PREFIXES


# --------------------------------------------------------------------------------------
# The CLI
# --------------------------------------------------------------------------------------


def test_verify_provenance_cli_fails_on_a_hand_authored_page(tmp_path: Path) -> None:
    """Against the real declaration: WP08 wires exactly this into CI's verify job."""
    output = tmp_path / "site"
    (output / "assets").mkdir(parents=True)
    (output / "about.html").write_text("<html>hand-written</html>", encoding="utf-8")
    result = CliRunner().invoke(guide, ["verify", "provenance", "--output", str(output)])
    assert result.exit_code == 1
    assert "about.html" in result.output


def test_verify_provenance_cli_rejects_a_missing_output_dir(tmp_path: Path) -> None:
    result = CliRunner().invoke(guide, ["verify", "provenance", "--output", str(tmp_path / "nope")])
    assert result.exit_code != 0


def test_verify_provenance_cli_passes_on_a_clean_output(
    tmp_path: Path, pack_factory: Callable[..., BuildConfig]
) -> None:
    output = tmp_path / "out"
    output.mkdir()
    (output / "llms.txt").write_text("index", encoding="utf-8")
    (output / ".nojekyll").write_text("", encoding="utf-8")
    result = CliRunner().invoke(guide, ["verify", "provenance", "--output", str(output)])
    assert result.exit_code == 0, result.output
    assert "OK" in result.output
