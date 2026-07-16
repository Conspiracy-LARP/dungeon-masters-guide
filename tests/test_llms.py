"""Tests for the machine-readable surfaces (FR-005, FR-006, NFR-001/SC-006).

Three claims are worth more than the rest, and they are the three that would fail
silently in production:

1. **The bootstrap is first.** An index that lists ten chapters and puts the procedure
   among them satisfies llmstxt.org and defeats the mission. Nothing about the resulting
   file looks broken — a model reads the guide, asks the creator what they want, and the
   interview it was supposed to run never happens. No amount of link-checking catches
   that, so it is asserted by position here.
2. **The bootstrap is linked as `AGENTS.md`.** `start.md` is the source name; it is not
   the name the site publishes. A link to it is a 404 aimed at the single most important
   address in the project.
3. **Every address moves when the base moves** (SC-006). The failure is invisible until
   the day someone buys a domain, at which point a hard-coded host is a scavenger hunt
   through generated text. The base-swap test below is the cheap thing standing in
   front of that.

Everything runs against the temporary pack from `conftest.py`, never the live
`src/pack/` — the real guide's prose changes independently of this mission, and tests
that read it go red for reasons that have nothing to do with the code.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Callable

import pytest
from click.testing import CliRunner

from build.cli import guide
from build.config import BuildConfig
from build.llms import (
    FULL_FILENAME,
    INDEX_FILENAME,
    LlmsError,
    render_full,
    render_index,
    write_full,
    write_index,
)
from build.roles import Document, chapters, load_documents

#: Any absolute URL in generated text.
_URL = re.compile(r"https?://[^\s)\]]+")

#: A markdown link bullet: `- [label](url)`.
_LINK = re.compile(r"^- \[([^\]]+)\]\(([^)]+)\)", re.MULTILINE)

#: Two bases that differ in host AND subpath, so a test cannot pass by accident on one
#: half of the address. Both hosts are reserved-for-testing names.
BASE_A = "https://example.test/guide/"
BASE_B = "https://other.example.com/somewhere-else/"


@pytest.fixture
def documents(pack_config: BuildConfig) -> list[Document]:
    return load_documents(pack_config.pack_dir, pack_config)


@pytest.fixture
def index_text(pack_config: BuildConfig, documents: list[Document]) -> str:
    return render_index(pack_config, documents)


@pytest.fixture
def full_text(pack_config: BuildConfig, documents: list[Document]) -> str:
    return render_full(pack_config, documents)


def _links(text: str) -> list[tuple[str, str]]:
    """Every `- [label](url)` bullet, in document order."""
    return [(m.group(1), m.group(2)) for m in _LINK.finditer(text)]


# --------------------------------------------------------------------------------------
# llms.txt — the shape (T023)
# --------------------------------------------------------------------------------------


def test_the_index_opens_with_the_h1_and_a_blockquote_summary(index_text: str) -> None:
    """llmstxt.org's required opening: an H1, then a blockquote."""
    lines = index_text.splitlines()
    assert lines[0] == "# The Dungeon Master's Guide"
    assert lines[1] == ""
    assert lines[2].startswith("> ")


def test_the_summary_tells_a_model_it_may_act_rather_than_read(index_text: str) -> None:
    """Contract rule 2 — the one sentence that stops a model reading ten chapters first.

    Asserted on meaning rather than wording: the summary must address an LLM, point it at
    the bootstrap, and say the rest can wait. If someone rewrites this paragraph into a
    neutral project description, the file still validates as llmstxt and the mission is
    lost, so the claim is pinned here rather than left to review.
    """
    quoted = [line for line in index_text.splitlines() if line.startswith(">")]
    summary = " ".join(" ".join(quoted).split()).lower()
    assert "llm" in summary, "the summary does not address the reader it is written for"
    assert "bootstrap" in summary, "the summary does not point at the procedure"
    assert "follow" in summary, "the summary does not tell the model to act"
    assert "do not need to read" in summary, (
        "the summary does not release the model from reading the guide first — which is "
        "the entire deviation from the convention"
    )


def test_the_bootstrap_is_the_first_link_in_the_index(index_text: str) -> None:
    """FR-005/FR-008, contract rule 1. The assertion the whole file exists for."""
    label, url = _links(index_text)[0]
    assert label == "AGENTS.md"
    assert url.endswith("/AGENTS.md")


def test_the_bootstrap_precedes_every_chapter(index_text: str, documents: list[Document]) -> None:
    """Not merely first among links — first in the text, before any chapter is mentioned.

    A `## The guide` section printed above `## Start here` would still leave the bootstrap
    "first" by some readings. Position in the byte stream is the thing a model actually
    experiences.
    """
    bootstrap_at = index_text.index("AGENTS.md")
    for chapter in chapters(documents):
        assert bootstrap_at < index_text.index(chapter.published_name), (
            f"{chapter.published_name} appears before the bootstrap; a model reading top "
            "to bottom meets a chapter before it meets the procedure"
        )


def test_the_bootstrap_lives_in_its_own_leading_section(index_text: str) -> None:
    """`## Start here` comes before `## The guide`, and holds exactly one entry."""
    start_here = index_text.index("## Start here")
    the_guide = index_text.index("## The guide")
    assert start_here < the_guide
    section = index_text[start_here:the_guide]
    assert len(_links(section)) == 1, (
        "`## Start here` lists more than the bootstrap — a second entry there is a "
        "second thing to do first, which means there is no first thing"
    )


def test_the_bootstrap_entry_is_described_as_a_procedure(index_text: str) -> None:
    """Contract rule 1: described as a procedure to follow, not a document to read."""
    start_here = index_text.index("## Start here")
    section = index_text[start_here : index_text.index("## The guide")].lower()
    # The entry wraps at ~100 characters like the rest of the guide; collapse the wrap
    # before matching, so a reflow does not read as a change of meaning.
    entry = " ".join(section.split())
    assert "procedure" in entry
    assert "follow this rather than reading the chapters first" in entry


def test_the_index_never_links_the_bootstraps_source_name(index_text: str) -> None:
    """FR-010: `start.md` is the source name. It is not what the site publishes."""
    for _, url in _links(index_text):
        assert not url.endswith("start.md"), f"{url} points at a name the site does not serve"


def test_the_index_lists_every_chapter_in_nav_order(
    index_text: str, documents: list[Document]
) -> None:
    """Contract rule 3 — generated from the declaration, in the declared order."""
    start = index_text.index("## The guide")
    section = index_text[start : index_text.index("## Everything")]
    listed = [label for label, _ in _links(section)]
    assert listed == [chapter.title for chapter in chapters(documents)]


def test_the_index_links_chapters_at_their_published_addresses(
    index_text: str, pack_config: BuildConfig, documents: list[Document]
) -> None:
    """Contract rule 5: raw `.md`, at the base-derived address (url-map C1, confirmed)."""
    start = index_text.index("## The guide")
    section = index_text[start : index_text.index("## Everything")]
    urls = [url for _, url in _links(section)]
    assert urls == [
        pack_config.absolute_url(chapter.published_name) for chapter in chapters(documents)
    ]
    assert all(url.endswith(".md") for url in urls)


def test_the_index_omits_documents_that_are_not_in_the_book(
    index_text: str, documents: list[Document]
) -> None:
    """`README.md` indexes the pack branch; it is not a chapter and is not a procedure."""
    the_guide = index_text[index_text.index("## The guide") :]
    assert "README.md" not in the_guide


def test_the_index_offers_the_full_text_last(index_text: str, pack_config: BuildConfig) -> None:
    label, url = _links(index_text)[-1]
    assert label == FULL_FILENAME
    assert url == pack_config.absolute_url(FULL_FILENAME)


def test_a_pack_without_a_bootstrap_fails_loudly(pack_factory: Callable[..., BuildConfig]) -> None:
    """If nothing publishes under a different name, there is no procedure to lead with.

    Rendering an index anyway would produce a valid-looking table of contents — exactly
    the artifact FR-008 exists to prevent — so this fails instead.
    """
    config = pack_factory(
        files={"ethics.md": "# Ethics\n"},
        nav=[("Ethics", "ethics.md")],
        not_in_book=[],
    )
    documents = load_documents(config.pack_dir, config)
    with pytest.raises(LlmsError, match="bootstrap"):
        render_index(config, documents)


# --------------------------------------------------------------------------------------
# llms-full.txt — the whole guide, once (T024)
# --------------------------------------------------------------------------------------


def test_the_full_text_contains_every_chapter_byte_for_byte(
    full_text: str, pack_config: BuildConfig, documents: list[Document]
) -> None:
    """FR-006. This is the guide's text, not a rendering of it.

    Substring containment, deliberately: it is the assertion that nothing was normalised,
    re-wrapped, or link-rewritten on the way through.
    """
    for chapter in chapters(documents):
        source = (pack_config.pack_dir / chapter.filename).read_text(encoding="utf-8")
        assert (
            source in full_text
        ), f"{chapter.filename} was altered on its way into {FULL_FILENAME}"


def test_the_full_text_holds_the_chapters_in_nav_order(
    full_text: str, documents: list[Document]
) -> None:
    """The same order as the book, from the same declaration.

    If the book and this file ever disagree, the declaration is not being used somewhere.
    """
    positions = [full_text.index(f"BEGIN chapter {c.position} of") for c in chapters(documents)]
    assert positions == sorted(positions)
    assert len(positions) == len(chapters(documents))


def test_the_full_text_delimits_each_chapter(full_text: str, documents: list[Document]) -> None:
    """A model must be able to tell where one chapter ends and the next begins."""
    for chapter in chapters(documents):
        marker = (
            f"chapter {chapter.position} of {len(chapters(documents))}: {chapter.published_name}"
        )
        assert f"<!-- BEGIN {marker}" in full_text
        assert f"<!-- END {marker} -->" in full_text


def test_the_full_text_excludes_documents_that_are_not_in_the_book(
    full_text: str, pack_config: BuildConfig, documents: list[Document]
) -> None:
    """T024 step 3: chapters only.

    `README.md` is the pack branch's front door and `start.md` is the bootstrap, which has
    its own address. Concatenating the procedure into the middle of the reference text is
    the same mistake as burying it in the index, committed at a different address.
    """
    excluded = [d for d in documents if not d.is_chapter]
    assert excluded, "sanity: the fixture pack has documents outside the book"
    for document in excluded:
        source = (pack_config.pack_dir / document.filename).read_text(encoding="utf-8")
        assert source not in full_text, f"{document.filename} is not_in_book but was concatenated"


def test_the_full_text_points_at_the_bootstraps_own_address(
    full_text: str, pack_config: BuildConfig
) -> None:
    """The model most at risk of reading everything is the one that fetched everything."""
    assert pack_config.absolute_url("AGENTS.md") in full_text


# --------------------------------------------------------------------------------------
# Every address derives from the base (T025, SC-006)
# --------------------------------------------------------------------------------------


def _render_both(config: BuildConfig) -> str:
    documents = load_documents(config.pack_dir, config)
    return render_index(config, documents) + render_full(config, documents)


def test_swapping_the_base_moves_every_address(pack_factory: Callable[..., BuildConfig]) -> None:
    """**The SC-006 test.** Build with base A, rebuild with base B, compare.

    This is the one that catches a hard-coded hostname. Not "some addresses changed" —
    every address, and not one retained trace of A anywhere in either file. A single
    f-string with a host in it survives every other test in this module and fails here.
    """
    text_a = _render_both(pack_factory(site_url=BASE_A))
    text_b = _render_both(pack_factory(site_url=BASE_B))

    urls_a = _URL.findall(text_a)
    urls_b = _URL.findall(text_b)
    assert urls_a, "sanity: the surfaces contain addresses at all"
    assert len(urls_a) == len(urls_b)

    for before, after in zip(urls_a, urls_b):
        assert before != after, f"{before} did not move when the base did"
        assert before.startswith(BASE_A)
        assert after.startswith(BASE_B)

    assert BASE_A not in text_b, "a trace of the old base survives the swap"
    assert "example.test" not in text_b


def test_every_address_carries_the_subpath(pack_factory: Callable[..., BuildConfig]) -> None:
    """C-003/url-map C2: this is a project site on a subpath, not a domain root.

    A root-relative address looks fine in review and 404s in production.
    """
    text = _render_both(pack_factory(site_url=BASE_A))
    for url in _URL.findall(text):
        assert url.startswith(BASE_A), f"{url} does not derive from the configured base"
    # The specific shape of the mistake: a root-relative link target.
    assert "](/" not in text


def test_the_real_bases_subpath_reaches_the_bootstrap(real_repo_config: BuildConfig) -> None:
    """Against today's real declaration: `…/dungeon-masters-guide/AGENTS.md`, not `…/AGENTS.md`."""
    documents = load_documents(real_repo_config.pack_dir, real_repo_config)
    text = render_index(real_repo_config, documents)
    assert real_repo_config.absolute_url("AGENTS.md") in text
    assert "/dungeon-masters-guide/AGENTS.md" in text


# --------------------------------------------------------------------------------------
# The commands
# --------------------------------------------------------------------------------------


def test_guide_llms_index_writes_the_file(
    pack_config: BuildConfig, documents: list[Document], tmp_path: Path
) -> None:
    output = tmp_path / "site"
    written = write_index(pack_config, documents, output)
    assert written == output / INDEX_FILENAME
    assert written.read_text(encoding="utf-8") == render_index(pack_config, documents)


def test_guide_llms_full_writes_the_file(
    pack_config: BuildConfig, documents: list[Document], tmp_path: Path
) -> None:
    output = tmp_path / "site"
    written = write_full(pack_config, documents, output)
    assert written == output / FULL_FILENAME
    assert written.read_text(encoding="utf-8") == render_full(pack_config, documents)


def test_the_commands_are_registered() -> None:
    """`guide llms index` and `guide llms full` exist and are documented."""
    runner = CliRunner()
    result = runner.invoke(guide, ["llms", "--help"])
    assert result.exit_code == 0, result.output
    assert "index" in result.output
    assert "full" in result.output
