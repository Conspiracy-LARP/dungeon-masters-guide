"""The machine-readable surfaces: `llms.txt` and `llms-full.txt` (FR-005, FR-006).

Follows the llmstxt.org convention — an H1, a blockquote summary, then link sections —
with **one deliberate deviation**, and the deviation is the entire point of the file.

The convention is designed for models that want to **read** a project. This guide wants
models to **act**: a creator's whole interaction with it is "read this URL and do what it
says." An index that dutifully listed ten chapters and left the bootstrap among them
would satisfy the convention and defeat the mission (FR-008) — a model would read the
guide cover to cover and then ask the creator what they wanted, having never learned that
a scripted interview exists and is what it was supposed to run.

So the bootstrap leads, alone, in its own `## Start here` section, described as a
procedure to follow rather than a document to read; and the blockquote says, in as many
words, that the rest can wait. That sentence is not decoration — it is the one line
standing between a model and ten chapters of preamble.

Two rules this module never bends:

* **The chapter list is derived, never written here.** It comes from the nav declaration
  via `roles.load_documents()`. A second copy of the reading order is the exact drift the
  declaration exists to end (contract rule 3), and `test_the_reading_order_is_declared_
  exactly_once` fails anyone who adds one.
* **Every address goes through `config.absolute_url()`.** Not one f-string with a host in
  it (NFR-001, contract rule 4). The site lives on a subpath (C-003), so a hand-composed
  `/AGENTS.md` would 404, and a hard-coded host turns the future domain switch into a
  scavenger hunt through generated text. The base-swap test in `tests/test_llms.py` is
  what catches it.

Link targets point at raw `.md` (contract rule 5). That rests on url-map condition **C1**
— that the host serves `.md` as readable text rather than a download — which WP01
confirmed against the real deployment: `text/markdown; charset=utf-8`, no
`Content-Disposition`. No fallback is in play.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final

from build.config import BuildConfig, project_version
from build.roles import Document, chapters


class LlmsError(RuntimeError):
    """The machine surfaces cannot be rendered from the pack as declared."""


#: The two generated filenames. `provenance.py` allow-lists both by these exact names.
INDEX_FILENAME: Final[str] = "llms.txt"
FULL_FILENAME: Final[str] = "llms-full.txt"

#: Where the surfaces are written by default. Mirrors `site_dir:` in mkdocs.yml — the
#: two are written next to MkDocs' own output because they publish from the same tree.
#: `config.py` is the only reader of mkdocs.yml and does not expose `site_dir`, so this
#: default is stated here rather than parsed twice; `--output` overrides it.
DEFAULT_OUTPUT_DIR: Final[Path] = Path("site")

#: The H1 of both surfaces.
TITLE: Final[str] = "# The Dungeon Master's Guide"

#: **The load-bearing prose.** Rule 2 of the contract: the summary must tell a model it
#: may act rather than read. Everything else in this file is generated; this paragraph is
#: the mission's own voice, and it is the reason the file is not a table of contents.
#:
#: Read it as a model would. By the third line it has been told that there is a procedure,
#: where it is, and that the chapters are not a prerequisite. That is the whole job.
SUMMARY: Final[str] = (
    "The contributor's guide to a distributed alternate reality game of diegetic conspiracy\n"
    "satire. If you are an LLM and someone asked you to help them build a node: read the\n"
    "bootstrap below and follow it. It sets up their workspace, attaches the kit, and starts\n"
    "the interview. You do not need to read the rest of the guide first — the chapters are\n"
    "reference for when the procedure sends you to them."
)

#: The bootstrap's entry. Described as a *procedure*, not a document — a model skimming
#: link text decides from this line whether to follow or to file.
BOOTSTRAP_DESCRIPTION: Final[str] = (
    "**The bootstrap. A complete procedure, not a document to read.** Scaffold the creator's\n"
    "  workspace, attach the kit, and open the interview. Follow this rather than reading the\n"
    "  chapters first."
)

#: `llms-full.txt`'s own summary. It says where the procedure went, because a model that
#: fetched the whole guide in one request is exactly the model at risk of reading all of
#: it and then asking the creator what they want.
FULL_SUMMARY_TEMPLATE: Final[str] = (
    "Every chapter of the guide, concatenated in reading order, as the source markdown.\n"
    "> This is the reference text. The bootstrap procedure is deliberately not buried in here;\n"
    "> it has its own address: {bootstrap_url}\n"
    "> If someone asked you to help them build a node, follow that instead of reading this."
)


def _subtitle(pack_dir: Path, document: Document) -> str:
    """The gloss after the em dash in a chapter's H1, if it has one.

    The pack's own one-line description of itself: `# Ethics — what we satirise, and what
    we never do` yields "what we satirise, and what we never do". Derived, so it cannot
    disagree with the chapter (NFR-003); a hand-written blurb here would be a second
    description of the document, drifting quietly from the first.

    Returns "" when the H1 carries no gloss, in which case the entry is title-only —
    a bare link is honest, an invented summary is not.
    """
    path = pack_dir / document.filename
    if not path.is_file():
        return ""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            heading = line[2:].strip()
            _, separator, gloss = heading.partition("—")
            return gloss.strip() if separator else ""
    return ""


def _link(label: str, url: str, description: str = "") -> str:
    """One llmstxt link bullet: `- [label](url): description`."""
    bullet = f"- [{label}]({url})"
    return f"{bullet}: {description}" if description else bullet


def render_index(config: BuildConfig, documents: list[Document]) -> str:
    """Render `llms.txt` (FR-005).

    Shape, in order, per `contracts/llms-txt.md`:

    1. the H1;
    2. the blockquote summary that tells a model it may act;
    3. `## Start here` — the bootstrap, alone, described as a procedure. **First.**
    4. `## The guide` — the chapters, generated in nav order with their declared titles;
    5. `## Everything` — `llms-full.txt`.

    Args:
        config: the declaration; the sole source of the base URL.
        documents: every pack document, from `roles.load_documents()`.

    Returns:
        The complete text of `llms.txt`.
    """
    bootstrap = _bootstrap(documents)
    lines: list[str] = [TITLE, ""]
    lines.extend(f"> {line}" if line else ">" for line in SUMMARY.splitlines())
    lines.extend(["", f"Version {project_version()}", "", "## Start here", ""])
    lines.append(
        _link(
            bootstrap.published_name,
            config.absolute_url(bootstrap.published_name),
            BOOTSTRAP_DESCRIPTION,
        )
    )
    lines.extend(["", "## The guide", ""])
    for chapter in chapters(documents):
        lines.append(
            _link(
                chapter.title,
                config.absolute_url(chapter.published_name),
                _subtitle(config.pack_dir, chapter),
            )
        )
    lines.extend(["", "## Everything", ""])
    lines.append(
        _link(
            FULL_FILENAME,
            config.absolute_url(FULL_FILENAME),
            "The entire guide concatenated, in reading order, for a model that wants all of it.",
        )
    )
    return "\n".join(lines) + "\n"


def _bootstrap(documents: list[Document]) -> Document:
    """The bootstrap document — the one whose published name differs from its source name.

    Identified through `published_name` (WP02/FR-010) rather than by naming `start.md`
    here: the rename rule is defined once, in `build.rename`, and this module asks it
    rather than restating it. That is also what guarantees the link says `AGENTS.md` —
    the only name that exists on the site — and never `start.md`.
    """
    for document in documents:
        if document.published_name != document.filename:
            return document
    raise LlmsError(
        "No bootstrap document found: every document publishes under its source name. "
        "llms.txt's first entry is the bootstrap (FR-005/FR-008); without it the index "
        "is a table of contents and a model will read the guide instead of running the "
        "interview."
    )


def render_full(config: BuildConfig, documents: list[Document]) -> str:
    """Render `llms-full.txt` (FR-006): every chapter, in nav order, byte-for-byte.

    **Chapters only.** `README.md` and `start.md` are `not_in_book`
    (`contracts/roles-declaration.md`): the pack's index is about the pack branch, and the
    bootstrap has its own address — burying the procedure in the middle of a
    hundred-kilobyte concatenation is the same mistake as burying it in the index.

    **Source bytes, unmodified.** This is the guide's text, not a rendering of it. The
    chapters are delimited with HTML comments rather than markdown headings so that the
    delimiter cannot be mistaken for the guide's own structure, and so that nothing is
    inserted into a chapter's own heading tree.

    Args:
        config: the declaration; the sole source of the base URL.
        documents: every pack document, from `roles.load_documents()`.

    Returns:
        The complete text of `llms-full.txt`.
    """
    bootstrap_url = config.absolute_url(_bootstrap(documents).published_name)
    book = chapters(documents)

    header = (
        f"{TITLE} — the complete text\n\n"
        "> " + FULL_SUMMARY_TEMPLATE.format(bootstrap_url=bootstrap_url) + "\n"
    )

    sections: list[str] = [header]
    for chapter in book:
        marker = f"chapter {chapter.position} of {len(book)}: {chapter.published_name}"
        url = config.absolute_url(chapter.published_name)
        # Read and emitted verbatim — no rstrip, no normalisation, no reference rewriting.
        # The delimiters are wrapped around the source, never applied to it, so the
        # chapter's exact bytes stay a contiguous substring of the output. That is what
        # "byte-preserved" means and how the test asserts it.
        source = (config.pack_dir / chapter.filename).read_text(encoding="utf-8")
        sections.append(f"<!-- BEGIN {marker} — {url} -->\n\n{source}\n<!-- END {marker} -->\n")
    return "\n".join(sections)


def write_index(config: BuildConfig, documents: list[Document], output_dir: Path) -> Path:
    """Write `llms.txt` into ``output_dir``. Returns the path written."""
    return _write(output_dir / INDEX_FILENAME, render_index(config, documents))


def write_full(config: BuildConfig, documents: list[Document], output_dir: Path) -> Path:
    """Write `llms-full.txt` into ``output_dir``. Returns the path written."""
    return _write(output_dir / FULL_FILENAME, render_full(config, documents))


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path
