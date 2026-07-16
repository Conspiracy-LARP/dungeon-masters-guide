"""Tests for assembly and cross-reference flattening (T022).

The PDF itself is not unit-testable and this file does not pretend otherwise — its real
acceptance is SC-003, a human reading it on paper (WP09). What *is* testable is where the
logic lives: the order the chapters come out in, what is excluded, and the two transforms
that turn one intermediate into a printable book and a clickable one.

Everything here builds its own pack from the `pack_factory` fixture (WP02's conftest).
The live `src/pack/` is the product and changes independently of the build; a test that
asserted against it would go red because someone edited the guide.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, Callable

import pytest

from build.book import (
    COVERED_CHARACTERS,
    PINNED_PANDOC_IMAGE,
    PRINT_SUBSTITUTIONS,
    BookError,
    _report_missing_glyphs,
    assemble,
    chapter_anchor,
    check_emphasis_safety,
    check_font_coverage,
    check_print_ready,
    flatten_for_print,
    retarget_for_html,
    write_intermediates,
)
from build.config import BuildConfig


def _pandoc_ast(markdown: str, tmp_path: Path) -> dict[str, Any] | None:
    """Parse `markdown` with the real pandoc and return its AST, or None if absent.

    Prefers the pinned image — the reader whose answer the PDF actually depends on — and
    falls back to a local pandoc. Returns None rather than raising so the caller can skip
    cleanly on a machine with neither.
    """
    source = tmp_path / "fragment.md"
    source.write_text(markdown, encoding="utf-8")

    if shutil.which("docker"):
        command = [
            "docker",
            "run",
            "--rm",
            "--volume",
            f"{tmp_path}:/data",
            "--workdir",
            "/data",
            PINNED_PANDOC_IMAGE,
        ]
    elif shutil.which("pandoc"):
        command = ["pandoc"]
    else:
        return None

    result = subprocess.run(
        [*command, "fragment.md", "--from", "markdown", "--to", "json"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:  # pragma: no cover - no image pulled, no network
        return None
    parsed: dict[str, Any] = json.loads(result.stdout)
    return parsed


# --------------------------------------------------------------------------------------
# T017 — assembly
# --------------------------------------------------------------------------------------


def test_assembles_every_chapter(pack_config: BuildConfig) -> None:
    """All chapters are present. The one that matters: none silently missing (FR-011)."""
    assembled = assemble(pack_config)

    assert "# Creator Kit" in assembled
    assert "# Getting Started" in assembled
    assert "# Ethics" in assembled


def test_chapters_appear_in_nav_order(pack_config: BuildConfig) -> None:
    """The reading order is nav's order, and the book obeys it (FR-003)."""
    assembled = assemble(pack_config)

    positions = [
        assembled.index("# Creator Kit"),
        assembled.index("# Getting Started"),
        assembled.index("# Ethics"),
    ]
    assert positions == sorted(positions)


def test_reordering_nav_reorders_the_book(pack_factory: Callable[..., BuildConfig]) -> None:
    """The order is *derived*, not restated.

    The regression this exists for: someone hard-codes a chapter list in book.py "just
    to get it working". Then the nav says one thing, the book says another, and that is
    the exact drift contracts/roles-declaration.md was written to end. Reverse nav; if
    the book does not reverse with it, a second list has crept in somewhere.
    """
    config = pack_factory(
        nav=[
            ("Ethics", "ethics.md"),
            ("Getting Started", "getting-started.md"),
            ("Creator Kit", "creator-kit.md"),
        ]
    )
    assembled = assemble(config)

    assert assembled.index("# Ethics") < assembled.index("# Getting Started")
    assert assembled.index("# Getting Started") < assembled.index("# Creator Kit")


def test_not_in_book_documents_are_absent(pack_config: BuildConfig) -> None:
    """`README.md` and `start.md` are published, but never in the book's flow.

    `start.md`'s first instruction is `mkdir -p my-node/...`. A reader who reached page
    one of a printed book did not ask to be scaffolded, and the pack's front door is not
    a chapter.
    """
    assembled = assemble(pack_config)

    assert "# Start here" not in assembled
    assert "# The kit" not in assembled
    assert "The bootstrap." not in assembled


def test_chapter_headings_stay_at_level_one(pack_config: BuildConfig) -> None:
    """Each chapter contributes exactly one H1, which becomes a chapter in the book.

    Heading levels need no shifting: `--top-level-division=chapter` maps H1 to \\chapter
    and `##` to sections. This asserts the precondition that makes that true.
    """
    assembled = assemble(pack_config)
    h1s = [line for line in assembled.splitlines() if line.startswith("# ")]

    assert len(h1s) == 3
    assert all(not line.startswith("## ") for line in h1s)


def test_chapter_heading_carries_its_anchor(pack_config: BuildConfig) -> None:
    """One identifier serves the PDF's \\pageref and the HTML's href."""
    assembled = assemble(pack_config)

    assert "# Ethics {#ch-ethics}" in assembled
    assert chapter_anchor("ethics.md") == "ch-ethics"


def test_a_second_h1_fails_loudly(pack_factory: Callable[..., BuildConfig]) -> None:
    """A chapter with two H1s would silently become two chapters.

    The book would then have more chapters than the reading order declares — a document
    appearing in the book without being declared, which is FR-011's failure wearing a
    different hat. Loud, naming the file, like every other check in this build.
    """
    config = pack_factory(
        files={
            "creator-kit.md": "# Creator Kit\n\nThe kit.\n",
            "getting-started.md": "# Getting Started\n\nOn-ramp.\n\n# Sneaky Second\n\nNo.\n",
            "ethics.md": "# Ethics\n\nThe floor.\n",
            "README.md": "# The kit\n",
            "start.md": "# Start here\n",
        }
    )
    with pytest.raises(BookError, match="2 top-level headings"):
        assemble(config)


def test_a_hash_inside_a_code_fence_is_not_a_chapter(
    pack_factory: Callable[..., BuildConfig],
) -> None:
    """`# comment` in a shell block is a comment, not a heading.

    The pack's code fences are full of them. Counting one as an H1 would fail the build
    with a confident, wrong explanation — the worst kind.
    """
    config = pack_factory(
        files={
            "creator-kit.md": "# Creator Kit\n\nThe kit.\n",
            "getting-started.md": (
                "# Getting Started\n\n```bash\n# set up your workspace\nmkdir -p my-node\n```\n"
            ),
            "ethics.md": "# Ethics\n\nThe floor.\n",
            "README.md": "# The kit\n",
            "start.md": "# Start here\n",
        }
    )
    assembled = assemble(config)

    assert "# set up your workspace" in assembled  # survived, still a comment
    assert len([line for line in assembled.splitlines() if line.startswith("# Get")]) == 1


def test_running_head_uses_the_short_nav_title(pack_config: BuildConfig) -> None:
    """The H1s are sentences; the running head gets the declared short title."""
    assembled = assemble(pack_config)

    assert "\\chaptermark{Creator Kit}" in assembled


# --------------------------------------------------------------------------------------
# T018 — flattening for print. The subtask most likely to be skipped, so: tests.
# --------------------------------------------------------------------------------------


def test_a_bare_sibling_link_becomes_a_chapter_reference(pack_config: BuildConfig) -> None:
    """FR-004. `[ethics.md](ethics.md)` on paper is a dead end; a page number is not."""
    flattened = flatten_for_print("See [`ethics.md`](ethics.md) for the floor.", pack_config)

    assert "[`ethics.md`](ethics.md)" not in flattened
    assert "Chapter 3, \\emph{Ethics} (page \\pageref{ch-ethics})" in flattened


def test_a_prose_labelled_link_keeps_its_prose(pack_config: BuildConfig) -> None:
    """A label that says something is kept; the reference is appended, not substituted."""
    flattened = flatten_for_print("See [the moral floor](ethics.md).", pack_config)

    assert "the moral floor (Chapter 3, \\emph{Ethics}, page \\pageref{ch-ethics})" in flattened


def test_an_inline_code_filename_becomes_a_chapter_reference(pack_config: BuildConfig) -> None:
    """ "Companion to `ethics.md`" is as unfollowable on paper as a link is."""
    flattened = flatten_for_print("Companion to `ethics.md`, which sets the floor.", pack_config)

    assert "`ethics.md`" not in flattened
    assert "Companion to Chapter 3, \\emph{Ethics} (page \\pageref{ch-ethics})" in flattened


def test_an_inline_code_link_sample_is_left_alone(pack_config: BuildConfig) -> None:
    """THE exclusion (T018 step 4), and the one a naive regex gets wrong.

    The guide documents its own bare-sibling link convention (C-001) by showing it in
    inline code. Resolving the demonstration into the demonstration's own output would
    leave the guide unable to state the rule it exists to state. Same exclusion WP07 uses.
    """
    source = "Every link is a bare sibling — `[ethics.md](ethics.md)`, never `[ethics.md](src/pack/ethics.md)`."
    flattened = flatten_for_print(source, pack_config)

    assert flattened == source


def test_a_code_fence_is_left_alone(pack_config: BuildConfig) -> None:
    """Verbatim is verbatim. A filename in a tree diagram is the reader's own file."""
    source = "Your node:\n\n```text\n└─ ethics.md   ← notes\n```\n"
    flattened = flatten_for_print(source, pack_config)

    assert flattened == source


def test_a_path_qualified_link_is_not_a_pack_cross_reference(pack_config: BuildConfig) -> None:
    """Bare siblings only. A target with a path is links.py's business, not ours."""
    source = "See [the source](src/pack/ethics.md)."
    flattened = flatten_for_print(source, pack_config)

    assert flattened == source


def test_an_external_link_survives_print(pack_config: BuildConfig) -> None:
    """A URL is exactly as followable on paper as it ever was. Leave it."""
    source = "See [the site](https://example.test/guide/)."
    flattened = flatten_for_print(source, pack_config)

    assert flattened == source


def test_a_link_to_a_not_in_book_document_resolves_to_its_published_url(
    pack_config: BuildConfig,
) -> None:
    """No chapter, so no page to turn to — the reader gets an address they can type.

    And the bootstrap resolves under its *published* name: `start.md` is `AGENTS.md`
    once published (FR-010). A printed book pointing at `start.md` would be pointing at
    a URL that 404s.
    """
    flattened = flatten_for_print("Read [`start.md`](start.md) first.", pack_config)

    assert "https://example.test/guide/AGENTS.md" in flattened
    assert "start.md" not in flattened


def test_the_published_url_comes_from_the_configured_base(
    pack_factory: Callable[..., BuildConfig],
) -> None:
    """NFR-001/SC-006: move the domain, and the printed book moves with it.

    Paper is the least recoverable medium there is. A hand-composed URL that went to
    press is wrong forever.
    """
    config = pack_factory(site_url="https://guide.example.org/")
    flattened = flatten_for_print("Read [`start.md`](start.md).", config)

    assert "https://guide.example.org/AGENTS.md" in flattened


def test_flattening_leaves_no_survivors_in_the_real_shape(pack_config: BuildConfig) -> None:
    """The reviewer's own check, run by the build: no `.md` cross-reference survives."""
    flattened = flatten_for_print(assemble(pack_config), pack_config)

    check_print_ready(flattened, pack_config)  # does not raise


def test_check_print_ready_catches_a_survivor(pack_config: BuildConfig) -> None:
    """The guard has to actually bite, or it is decoration."""
    with pytest.raises(BookError, match="survived flattening"):
        check_print_ready("See [`ethics.md`](ethics.md).", pack_config)


# --------------------------------------------------------------------------------------
# T018 — the replacement must be well-formed WHERE IT LANDS, not merely in isolation
#
# Every flattening test above this line feeds the transform a bare sentence with no
# surrounding emphasis. That is why a replacement built from markdown `*` shipped: it is
# correct in a bare sentence and broken in the one construct the guide actually uses.
# A reference is not a document — it is a fragment spliced into prose the transform never
# parsed. These tests exercise the landing site, not the fragment.
# --------------------------------------------------------------------------------------

#: The real construct, verbatim in shape from `src/pack/getting-started.md:3-6`: an
#: italic preamble whose emphasis span contains an inline-code cross-reference. Eight of
#: the ten chapters open with one of these.
_ITALIC_PREAMBLE: str = (
    "*Companion to `ethics.md` (see §3). This is the practical on-ramp: how to set up a\n"
    "place to work, and the shortest path there.*"
)


def test_a_reference_inside_an_italic_preamble_keeps_the_italic(
    pack_config: BuildConfig,
) -> None:
    """The defect, at the source level: `*` cannot nest inside `*`.

    `*Companion to Chapter 3, *Ethics* (page ...) ...*` is not "emphasis containing
    emphasis" — markdown has no such reading. Pandoc closes the outer span at the second
    delimiter, the rest of the preamble goes upright, and the two orphaned delimiters
    typeset as literal asterisks. This asserts the shape that makes that impossible:
    exactly the two delimiters the source itself wrote, and no more.
    """
    flattened = flatten_for_print(_ITALIC_PREAMBLE, pack_config)

    assert "`ethics.md`" not in flattened  # the reference was resolved at all
    assert "\\emph{Ethics}" in flattened  # ...and the title is still italicised
    assert (
        flattened.count("*") == 2
    ), f"the emphasis span gained delimiters and will not survive pandoc: {flattened!r}"
    assert flattened.startswith("*") and flattened.endswith("*")


def test_no_reference_replacement_contains_a_markdown_delimiter(
    pack_config: BuildConfig,
) -> None:
    """The invariant stated directly, against every reference the pack can produce.

    Both kinds — a chapter, and a `not_in_book` document resolving to its URL — are
    spliced into prose whose emphasis state the transform cannot see. Neither may carry a
    delimiter whose meaning depends on that state. This is the property; the test above
    is one construct that demonstrates it mattering.
    """
    from build.book import _reference_index
    from build.roles import load_documents

    index = _reference_index(load_documents(pack_config.pack_dir, pack_config), pack_config)
    assert index  # guard the guard: an empty index would pass vacuously

    for filename, reference in index.items():
        for rendered in (reference.standalone, reference.parenthetical):
            assert "*" not in rendered, f"{filename} → {rendered!r} carries a markdown '*'"
            assert "_" not in rendered, f"{filename} → {rendered!r} carries a markdown '_'"


def test_check_emphasis_safety_catches_an_introduced_delimiter() -> None:
    """The guard has to bite. Hand it the exact string the old code produced."""
    source = "*Companion to `ethics.md`, the floor.*"
    broken = "*Companion to Chapter 3, *Ethics* (page \\pageref{ch-ethics}), the floor.*"

    with pytest.raises(BookError, match="introduced 2 markdown"):
        check_emphasis_safety(source, broken)


def test_check_emphasis_safety_allows_delimiters_to_fall(pack_config: BuildConfig) -> None:
    """The invariant is an inequality, not an equality, and this is why.

    `[**ethics.md**](ethics.md)` resolves to a standalone reference and the label's `**`
    goes with the label. Delimiters legitimately *fall*; only a rise is the defect. An
    equality here would fail on the pack's own house style and be switched off.
    """
    flattened = flatten_for_print("See [**ethics.md**](ethics.md).", pack_config)

    assert "*" not in flattened  # four delimiters fell, and that is correct
    check_emphasis_safety("See [**ethics.md**](ethics.md).", flattened)  # does not raise


def test_the_whole_assembled_book_flattens_emphasis_safely(pack_config: BuildConfig) -> None:
    """End to end, on the real assembled shape: flattening never raises the count."""
    assembled = assemble(pack_config)
    flattened = flatten_for_print(assembled, pack_config)

    check_emphasis_safety(assembled, flattened)  # does not raise
    assert flattened.count("*") <= assembled.count("*")


def test_pandoc_reads_the_flattened_preamble_as_one_emphasis_span(
    pack_config: BuildConfig, tmp_path: Path
) -> None:
    """The claim, settled by the only authority that counts: pandoc's own reader.

    The tests above assert a delimiter count, which is a proxy for this. This asserts the
    thing itself — that the flattened preamble parses to a **single `Emph` node spanning
    the whole sentence**, with no literal `*` reaching the page. It is the check that
    would have failed on day one, because it asks what the reader will see rather than
    what the transform meant.

    Skipped without the pinned toolchain, deliberately: the answer has to come from the
    real markdown reader. Hand-rolling a parser here to avoid the skip would be the same
    mistake this test exists to catch, one level down.
    """
    flattened = flatten_for_print(_ITALIC_PREAMBLE, pack_config)
    document = _pandoc_ast(flattened, tmp_path)
    if document is None:
        pytest.skip("neither the pinned pandoc image nor a local pandoc is available")

    blocks = document["blocks"]
    assert len(blocks) == 1 and blocks[0]["t"] == "Para", f"unexpected shape: {blocks}"

    children = blocks[0]["c"]
    assert len(children) == 1 and children[0]["t"] == "Emph", (
        "the preamble is not one emphasis span — the flattening broke the span it landed "
        f"in and part of the sentence escaped the italic: {children}"
    )

    span = children[0]["c"]
    literals = [node["c"] for node in span if node["t"] == "Str"]
    assert not [
        text for text in literals if "*" in text
    ], f"a literal asterisk was typeset on the page: {literals}"
    assert {"t": "RawInline", "c": ["tex", "\\emph{Ethics}"]} in span
    # The tail of the sentence is inside the span, not stranded outside it.
    assert "there." in literals


# --------------------------------------------------------------------------------------
# T019 — characters
# --------------------------------------------------------------------------------------


def test_emoji_are_substituted_before_xelatex_sees_them(pack_config: BuildConfig) -> None:
    """The pinned fonts carry no ✅/❌, and XeLaTeX would drop them without failing."""
    flattened = flatten_for_print("| ✅ Good tell | ❌ Bad tell |", pack_config)

    assert "✅" not in flattened
    assert "❌" not in flattened
    assert "\\ding{51}" in flattened
    assert "\\ding{55}" in flattened


def test_covered_characters_pass(pack_config: BuildConfig) -> None:
    """The guide's real punctuation — 489 em-dashes, arrows, box-drawing — is fine."""
    check_font_coverage("An em-dash — an arrow →, a tree └─, a § and a ç.")


def test_an_uncovered_character_fails_loudly() -> None:
    """The silent failure this whole guard exists for.

    XeLaTeX's answer to a missing glyph is a log line and a gap on the page: a green
    build and a book with words missing from it. Better a red build with the code point
    in the message.
    """
    with pytest.raises(BookError, match=r"U\+1F916"):
        check_font_coverage("Ask the model 🤖 about it.")


def test_every_substitution_target_is_not_itself_a_covered_character() -> None:
    """A character in both lists would mean the substitution was never needed."""
    assert not set(PRINT_SUBSTITUTIONS) & COVERED_CHARACTERS


# --------------------------------------------------------------------------------------
# T019 — the post-render guard, which had no test and therefore did not work
#
# `check_font_coverage` (above) fires, and is tested. It reads the *source* against a
# hand-maintained allow-list. `_report_missing_glyphs` reads the *log*, from XeLaTeX, on
# the fonts it really loaded — it exists precisely to catch the allow-list being wrong,
# which is the one thing `check_font_coverage` structurally cannot do. It shipped with a
# regex anchored at `^Missing character:` while pandoc prefixes every such line with
# `[WARNING] `, so it matched nothing it would ever be handed. Live call site, dead
# effect, green build, missing glyph.
#
# These lines are CAPTURED, not composed. That distinction is the whole value of this
# block: a test written against an invented log line passes against the broken regex too,
# which is exactly how a guard gets a green test and no teeth.
# --------------------------------------------------------------------------------------

#: Captured from `pandoc --to pdf --pdf-engine xelatex` in the pinned image
#: (PANDOC_IMAGE_DIGEST), rendering a document containing 🤖. Reproduce with:
#:
#:   printf '# Ethics \U0001F916\n' > /tmp/g.md && docker run --rm -v /tmp:/data -w /data \
#:     pandoc/extra:3.8-ubuntu@sha256:21ce... g.md -t pdf --pdf-engine xelatex -o g.pdf
#:
#: Note the `[WARNING] ` prefix, and note that pandoc exited **0**.
_REAL_MISSING_CHARACTER_LOG: str = (
    "[WARNING] Missing character: There is no \U0001f916 (U+1F916) (U+1F916) in font "
    "[lmroman12-bold]:mapping=tex\n"
)

#: The same warning from the book's own template, which loads the DejaVu family.
#: Captured by the cycle-1 reviewer against the same image.
_REAL_MISSING_CHARACTER_LOG_DEJAVU: str = (
    "[WARNING] Missing character: There is no \U0001f916 (U+1F916) (U+1F916) in font "
    "DejaVu Serif Bold/OT:script=\n"
    "[WARNING] Missing character: There is no \U0001f916 (U+1F916) (U+1F916) in font "
    "DejaVu Sans Bold/OT:script=l\n"
)


@pytest.mark.parametrize(
    "log",
    [_REAL_MISSING_CHARACTER_LOG, _REAL_MISSING_CHARACTER_LOG_DEJAVU],
    ids=["default-fonts", "dejavu-template"],
)
def test_report_missing_glyphs_fires_on_real_pandoc_output(log: str) -> None:
    """The guard must see the log it is actually handed — prefix and all.

    This is the test whose absence was the defect. Feed it the bytes pandoc really
    writes; if the pattern is ever re-anchored to the start of the line, this goes red
    instead of the book quietly losing a character.
    """
    with pytest.raises(BookError, match="Missing character"):
        _report_missing_glyphs(log, "Rendering the PDF")


def test_report_missing_glyphs_names_every_warning_it_found() -> None:
    """A count and the offending lines, or the reader has to go find the log themselves."""
    with pytest.raises(BookError) as raised:
        _report_missing_glyphs(_REAL_MISSING_CHARACTER_LOG_DEJAVU, "Rendering the PDF")

    message = str(raised.value)
    assert "2 'Missing character' warning(s)" in message
    assert "DejaVu Serif Bold" in message  # the actual line, not a summary of it


def test_report_missing_glyphs_is_quiet_on_a_clean_log() -> None:
    """Guard the guard from the other side: it must not fire on a healthy render.

    A check that fails on everything gets switched off just as fast as one that fails on
    nothing. This log is a real successful render's output, warnings and all — pandoc
    says plenty that is not this.
    """
    clean = (
        "[WARNING] This document format requires a nonempty <title> element.\n"
        "  Defaulting to 'book.print' as the title.\n"
        "  To specify a title, use 'title' in metadata.\n"
    )
    _report_missing_glyphs(clean, "Rendering the PDF")  # does not raise


def test_the_missing_character_pattern_is_not_anchored_past_pandocs_prefix() -> None:
    """The regression, named at the level it actually happened.

    `^Missing character:` is the spelling a careful person writes and it matches zero of
    pandoc's real lines. The test above proves the guard fires today; this one says *why*
    it used to not, so the next person to tidy this regex sees the trap before they set
    it again.
    """
    from build.book import _MISSING_CHARACTER

    assert _MISSING_CHARACTER.findall(_REAL_MISSING_CHARACTER_LOG), (
        "the pattern does not match pandoc's real output. It is relayed with a "
        "'[WARNING] ' prefix, so the pattern must not anchor at 'Missing character:'."
    )
    assert not re.compile(r"^Missing character:.*$", re.MULTILINE).findall(
        _REAL_MISSING_CHARACTER_LOG
    ), "sanity: the old anchored pattern really did match nothing"


def test_the_missing_glyph_guard_fires_against_the_real_toolchain(tmp_path: Path) -> None:
    """End to end: pandoc renders, drops a glyph, exits 0, and the build fails anyway.

    Everything above this feeds `_report_missing_glyphs` a string. This one does not know
    what the log says — it makes the real toolchain produce one and asserts the guard
    turns a silent, successful, wrong render into a red build.

    It goes through `_run`, so it covers the whole path that failed: pandoc's exit code
    (zero!), the stdout/stderr capture, the pattern, and the raise. `check_font_coverage`
    is bypassed on purpose — this is the guard that catches the allow-list being wrong,
    so a test that let the allow-list stop it first would be testing the other guard.
    """
    from build.book import _run, resolve_runner

    try:
        runner = resolve_runner("auto", tmp_path)
    except BookError:
        pytest.skip("neither the pinned pandoc image nor a local pandoc is available")

    source = tmp_path / "glyph.md"
    source.write_text("# Ethics \U0001f916 and satire\n\nSome text.\n", encoding="utf-8")

    with pytest.raises(BookError, match="characters silently dropped"):
        _run(
            runner,
            [
                "glyph.md",
                "--from",
                "markdown",
                "--to",
                "pdf",
                "--pdf-engine",
                "xelatex",
                "--pdf-engine-opt=-interaction=nonstopmode",
                "--output",
                "glyph.pdf",
            ],
            what="Rendering the PDF",
        )


# --------------------------------------------------------------------------------------
# T021 — the HTML book: same links, opposite treatment
# --------------------------------------------------------------------------------------


def test_html_keeps_links_clickable(pack_config: BuildConfig) -> None:
    """The deliberate decision: T018's flattening is NOT applied here.

    On screen a link is the best affordance available, and "page 88" is a fiction — the
    HTML book has no pages.
    """
    retargeted = retarget_for_html("See [`ethics.md`](ethics.md).", pack_config)

    assert "Chapter" not in retargeted
    assert "pageref" not in retargeted
    assert "[`ethics.md`](#ch-ethics)" in retargeted


def test_html_retargets_siblings_to_internal_anchors(pack_config: BuildConfig) -> None:
    """The subtlety: a single-file book has no siblings, so the href must change.

    `[ethics.md](ethics.md)` resolves in the pack because `ethics.md` sits next to the
    file naming it (C-001). From `book.html` that same href points at a file that was
    never published there.
    """
    retargeted = retarget_for_html(assemble(pack_config), pack_config)

    assert "](ethics.md)" not in retargeted
    assert "](#ch-ethics)" in retargeted


def test_html_leaves_inline_code_readable(pack_config: BuildConfig) -> None:
    """On screen `ethics.md` reads fine, and the reader has links, a ToC and find-in-page."""
    retargeted = retarget_for_html("Companion to `ethics.md`.", pack_config)

    assert retargeted == "Companion to `ethics.md`."


def test_html_sends_not_in_book_documents_to_their_published_url(
    pack_config: BuildConfig,
) -> None:
    """They are not in this file, so an internal anchor would be a broken promise."""
    retargeted = retarget_for_html("Read [`start.md`](start.md).", pack_config)

    assert "](https://example.test/guide/AGENTS.md)" in retargeted


def test_html_leaves_a_link_sample_alone(pack_config: BuildConfig) -> None:
    """The same exclusion as print: an illustration is not a link."""
    source = "A bare sibling — `[ethics.md](ethics.md)`."

    assert retarget_for_html(source, pack_config) == source


def test_both_renderings_derive_from_one_intermediate(
    pack_config: BuildConfig, tmp_path: Path
) -> None:
    """FR-003/FR-004 must agree about what the book says and what order it says it in.

    Two claims, and the second is the load-bearing one:

    1. The print intermediate is *derived* from the shared one, not assembled separately.
    2. Every chapter the PDF points at by page is a chapter the HTML points at by anchor,
       and vice versa — because both are reading the same identifier out of the same
       string. That is what makes "the two cannot disagree" a fact about the code rather
       than a hope.
    """
    intermediate, print_intermediate = write_intermediates(pack_config, tmp_path / "out")

    shared = intermediate.read_text(encoding="utf-8")
    printed = print_intermediate.read_text(encoding="utf-8")
    assert printed == flatten_for_print(shared, pack_config)

    for anchor in ("ch-creator-kit", "ch-getting-started", "ch-ethics"):
        assert f"{{#{anchor}}}" in shared

    referenced_in_print = set(re.findall(r"\\pageref\{(ch-[\w-]+)\}", printed))
    referenced_in_html = set(
        re.findall(r"\]\(#(ch-[\w-]+)\)", retarget_for_html(shared, pack_config))
    )

    assert referenced_in_print  # the fixture pack does cross-reference; guard the guard
    assert referenced_in_print == referenced_in_html


# --------------------------------------------------------------------------------------
# The constraints (C-002, C-006, T020)
# --------------------------------------------------------------------------------------


def test_building_the_book_never_writes_to_the_pack(
    pack_config: BuildConfig, tmp_path: Path
) -> None:
    """C-002/C-006. The transforms run on the intermediate; the pack is read-only.

    Content is the product and out of scope for this mission. If the build seems to need
    a prose change, that is a finding to escalate, not a fix to make.
    """
    pack_dir = pack_config.pack_dir
    before = {path.name: path.read_bytes() for path in sorted(pack_dir.glob("*.md"))}

    write_intermediates(pack_config, tmp_path / "out")

    after = {path.name: path.read_bytes() for path in sorted(pack_dir.glob("*.md"))}
    assert after == before


def test_the_live_pack_is_unmodified_in_git(repo_root: Path) -> None:
    """`git diff --stat src/pack/` must be empty — the reviewer's check, automated.

    The temporary-pack tests above prove the transforms do not write to *a* pack. This
    proves nothing has written to *the* pack: a stray `Path.write_text` against
    `config.pack_dir` in some future refactor would sail past them.
    """
    result = subprocess.run(
        ["git", "diff", "--stat", "--", "src/pack/"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:  # pragma: no cover - no git, e.g. a source tarball
        pytest.skip("git is unavailable")

    assert result.stdout.strip() == "", (
        "src/pack/ has been modified. The guide's prose is the product and the build "
        "never edits it (C-002, C-006).\n" + result.stdout
    )


def test_the_pandoc_image_is_pinned_by_digest() -> None:
    """T020. A tag moves; "the PDF changed and nobody touched the pack" is the drift.

    Guarding the property rather than the value: the digest may legitimately change, but
    it must never become a bare tag.
    """
    assert "@sha256:" in PINNED_PANDOC_IMAGE
    assert len(PINNED_PANDOC_IMAGE.split("@sha256:")[1]) == 64


def test_the_book_module_hard_codes_no_chapter_list() -> None:
    """The rule the whole roles declaration exists to enforce (contract rule 4).

    There is exactly one list of chapters in this repository and it is `mkdocs.yml`'s
    `nav`. A convenience copy in book.py would be a fifth hand-maintained list — the
    problem this design was built to end.
    """
    source = Path(__file__).resolve().parents[1] / "src" / "build" / "book.py"
    text = source.read_text(encoding="utf-8")

    # The real chapter filenames must not appear as data. They may appear in prose —
    # docstrings name `ethics.md` to explain the transform — so this looks for the shape
    # of a list literal, which is what a hard-coded order would have to be.
    for chapter in ("philosophy.md", "improvisation.md", "worked-example.md"):
        assert f'"{chapter}"' not in text, (
            f"{chapter} appears as a string literal in book.py. The reading order comes "
            "from roles.load_documents() and nowhere else."
        )
