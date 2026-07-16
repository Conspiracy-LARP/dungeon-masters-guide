"""Tests for reference rewriting (FR-010).

The first test in this file is the one that matters. `getting-started.md` contains the
substring `start.md`, and a naive `sed s/start.md/AGENTS.md/g` corrupts it into
`getting-AGENTS.md` — a broken link on the pack branch, shipped silently. That is not a
hypothetical: the pack branch was hand-built on 2026-07-16 and this exact case had to be
handled. Both WP03 and WP06 depend on this staying right.
"""

from __future__ import annotations

import pytest

from build.rename import PUBLISHED_NAME, SOURCE_NAME, published_name, rewrite_references

# --------------------------------------------------------------------------------------
# THE TRAP
# --------------------------------------------------------------------------------------


def test_getting_started_survives_the_rewrite() -> None:
    """`getting-started.md` must come through completely untouched."""
    text = "The on-ramp is [getting-started.md](getting-started.md)."
    assert rewrite_references(text) == text
    assert "getting-AGENTS.md" not in rewrite_references(text)


def test_getting_started_survives_alongside_a_real_reference() -> None:
    """The realistic case: one line mentions both, and only one may change."""
    text = "Point your model at [start.md](start.md), then read [getting-started.md](getting-started.md)."
    result = rewrite_references(text)
    assert result == (
        "Point your model at [AGENTS.md](AGENTS.md), then read "
        "[getting-started.md](getting-started.md)."
    )


def test_real_bootstrap_text_shape_is_rewritten_safely() -> None:
    """Mirrors src/pack/start.md, which references `getting-started.md` three times."""
    text = (
        "*(...the practical on-ramp is `getting-started.md`.)*\n"
        "Follow **`doc/core/getting-started.md`** (summarised in the kit's §3).\n"
        "- **`getting-started.md`** — the on-ramp expanded.\n"
        "The brief itself lives at `start.md`.\n"
    )
    result = rewrite_references(text)
    assert result.count("getting-started.md") == 3
    assert "getting-AGENTS.md" not in result
    assert "`AGENTS.md`" in result


@pytest.mark.parametrize(
    "text",
    [
        "see [on-ramp](getting-started.md)",
        "see `getting-started.md`",
        "see restart.md",
        "see quickstart.md",
        "see jumpstart.md",
        "a file named start.markdown",
        "a file named start.md.bak",
    ],
)
def test_names_that_merely_contain_start_md_are_untouched(text: str) -> None:
    """Anything that only ends with, or extends, `start.md` is a different file."""
    assert rewrite_references(text) == text


# --------------------------------------------------------------------------------------
# The rewrite it must actually do
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("[the brief](start.md)", "[the brief](AGENTS.md)"),
        ("see `start.md` first", "see `AGENTS.md` first"),
        ("start.md is the entry point", "AGENTS.md is the entry point"),
        ("read start.md.", "read AGENTS.md."),
        ("(start.md)", "(AGENTS.md)"),
        ("**start.md**", "**AGENTS.md**"),
        ("- start.md — the brief", "- AGENTS.md — the brief"),
        ("doc/core/start.md", "doc/core/AGENTS.md"),
    ],
)
def test_reference_rewriting(text: str, expected: str) -> None:
    """Link targets and inline mentions both get rewritten.

    The last case is deliberate. The guide's prose points readers at the file inside
    their own checkout (`doc/core/getting-started.md` appears in start.md today), and in
    a creator's checkout the bootstrap really is named `AGENTS.md` — that is the entire
    reason for the rename. So a path-qualified reference must rewrite too; leaving it as
    `doc/core/start.md` would tell the reader to open a file that is not there.
    """
    assert rewrite_references(text) == expected


def test_multiple_references_in_one_document() -> None:
    text = "start.md says X. Later, start.md says Y. See [it](start.md)."
    assert rewrite_references(text) == (
        "AGENTS.md says X. Later, AGENTS.md says Y. See [it](AGENTS.md)."
    )


def test_text_without_references_is_returned_unchanged() -> None:
    text = "# Ethics\n\nNo bootstrap references here.\n"
    assert rewrite_references(text) is not None
    assert rewrite_references(text) == text


def test_rewrite_is_idempotent() -> None:
    """Running it twice must not compound — the pack branch build may re-run."""
    once = rewrite_references("[the brief](start.md)")
    assert rewrite_references(once) == once


# --------------------------------------------------------------------------------------
# published_name
# --------------------------------------------------------------------------------------


def test_published_name_renames_only_the_bootstrap() -> None:
    assert published_name(SOURCE_NAME) == PUBLISHED_NAME
    assert published_name("start.md") == "AGENTS.md"


@pytest.mark.parametrize(
    "filename",
    [
        "README.md",
        "creator-kit.md",
        "getting-started.md",
        "ethics.md",
        "story-continuity-checker-prompt.md",
    ],
)
def test_published_name_leaves_every_other_document_alone(filename: str) -> None:
    assert published_name(filename) == filename
