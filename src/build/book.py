"""The book: one document assembled from the pack, rendered twice (FR-003, FR-004).

Ten chapters, in the one declared reading order, become **one intermediate markdown
file**. Both outputs derive from that intermediate — the single-file HTML book (FR-003)
and the printable PDF (FR-004) — so the two cannot disagree about what the book says or
what order it says it in. Nothing here is hand-authored (NFR-003) and nothing here ever
writes to ``src/pack/`` (C-002, C-006).

**One intermediate, two transforms.** The two renderings have opposite needs and this is
the whole design:

- **Print cannot click.** ``[ethics.md](ethics.md)`` on paper is a dead end (FR-004).
  :func:`flatten_for_print` resolves every cross-reference to a chapter number, a title,
  and a page number the reader can turn to.
- **HTML can click**, but a *single-file* book has no sibling files to link *to*.
  :func:`retarget_for_html` therefore does not flatten — it repoints the same links at
  the internal anchors of the same document. Same links, opposite treatment, one source.

**Why LaTeX at all.** Stakeholder decision ``01KXP7BCG6XFDHDRGZ57NXG90Q`` (research § R2):
print typography is the entire point of the PDF, so pandoc + XeLaTeX was chosen over an
HTML-to-PDF renderer that would have reused the site's stylesheet for free. The accepted
cost is recorded in plan.md § Complexity Tracking: two style systems that can drift, and
a TeX dependency. The template lives in ``src/theme/book/``; the site's CSS is WP03's.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Final, Iterable, Mapping

from build.config import BuildConfig
from build.rename import published_name
from build.roles import Document, chapters, load_documents

# --------------------------------------------------------------------------------------
# The toolchain, pinned (T020)
# --------------------------------------------------------------------------------------

#: The prebuilt pandoc + XeLaTeX image the PDF is rendered in.
#:
#: **Prebuilt, and pinned by digest.** NFR-005 budgets five minutes for the whole
#: pipeline; ``apt-get install texlive-*`` or ``tlmgr install`` on every run spends most
#: of that before pandoc has read a byte. The digest is what makes the render
#: reproducible — a tag is a moving target, and "the PDF changed and nobody touched the
#: pack" is precisely the failure NFR-003 exists to make impossible.
#:
#: The image also settles the font question (T020): it ships the DejaVu family, which is
#: what ``template.tex`` names and what :data:`COVERED_CHARACTERS` is verified against.
#: CI's system fonts are not this laptop's; neither is consulted.
#:
#: To move to a new image: pull it, re-verify glyph coverage against
#: :data:`COVERED_CHARACTERS` and :data:`PRINT_SUBSTITUTIONS`, update the digest, and
#: update ``src/theme/book/fonts/README.md``.
PANDOC_IMAGE: Final[str] = "pandoc/extra:3.8-ubuntu"
PANDOC_IMAGE_DIGEST: Final[str] = (
    "sha256:21ce6c5a9ce8311bdc257902811e794d66a585bc5da6d8df755f013a54695d69"
)
PINNED_PANDOC_IMAGE: Final[str] = f"{PANDOC_IMAGE}@{PANDOC_IMAGE_DIGEST}"

#: Measured wall-clock for `guide book pdf` on a warm image, for WP08's 5-minute line
#: (NFR-005). See `src/theme/book/fonts/README.md` for the measurement and its caveats.
#: The image pull is the expensive part and is cacheable; the render itself is seconds.
EXPECTED_PDF_SECONDS: Final[int] = 25

#: Published filenames. These are not free choices — `build.provenance` already names
#: both in its allow-list of legitimate generated artifacts (NFR-003). Renaming either
#: here without renaming it there turns the book into an unaccounted file.
HTML_BOOK_FILENAME: Final[str] = "book.html"
PDF_BOOK_FILENAME: Final[str] = "dungeon-masters-guide.pdf"
#: The shared intermediate, and the two transforms of it. Named as siblings because
#: that is what they are: `book.md` is the book, and the other two are it seen from
#: print and from the web. Reading all three side by side is the fastest way to see what
#: the cross-reference transforms actually did.
INTERMEDIATE_FILENAME: Final[str] = "book.md"
PRINT_INTERMEDIATE_FILENAME: Final[str] = "book.print.md"
WEB_INTERMEDIATE_FILENAME: Final[str] = "book.web.md"

#: Where the build puts its output. `dist/` is gitignored; `src/pack/` is untouchable.
DEFAULT_OUTPUT_DIR: Final[str] = "dist/book"

#: The template that justifies the toolchain choice (T019).
TEMPLATE_PATH: Final[str] = "src/theme/book/template.tex"


class BookError(RuntimeError):
    """The book cannot be assembled, transformed, or rendered."""


# --------------------------------------------------------------------------------------
# Characters (T019) — decided deliberately, not discovered at page 200
# --------------------------------------------------------------------------------------

#: Emoji, replaced with typeset marks before XeLaTeX ever sees them.
#:
#: **This is the substitution, chosen over an emoji font, and it is a deliberate
#: decision** (T019). The guide uses exactly two emoji — ✅ and ❌, in the good-tell /
#: bad-tell table in `storytelling.md` — and the pinned image's DejaVu family covers
#: neither (verified: `fc-list ":charset=2705"` is empty in the image). The options were
#: to add an emoji font or to substitute.
#:
#: Substitution wins for three reasons. The book is *printed*, so a colour emoji is
#: flattened to grey anyway. Pifont's dingbats are real typeset glyphs that sit on the
#: baseline with the surrounding serif text instead of riding above it like a sticker.
#: And it removes a font dependency from a decision (T020) whose whole purpose is to
#: remove font dependencies.
#:
#: The failure mode this replaces is the one the work package warned about: XeLaTeX does
#: not stop for a glyph it cannot find. It emits "Missing character" to the log and sets
#: *nothing*, so the tells table would print with two blank columns — a silent wrong
#: answer at the end of a green build. :func:`check_font_coverage` is what makes that
#: impossible for the *next* character, too.
#:
#: Raw inline LaTeX, so this applies to the print intermediate only; the HTML book keeps
#: the real emoji, which every browser renders.
PRINT_SUBSTITUTIONS: Final[Mapping[str, str]] = {
    "✅": r"\ding{51}",  # ✅ WHITE HEAVY CHECK MARK  → pifont heavy check
    "❌": r"\ding{55}",  # ❌ CROSS MARK              → pifont heavy ballot X
}

#: Every non-ASCII character the pinned image's fonts are *verified* to carry.
#:
#: Verified against the image, not assumed:
#: `fc-list ":charset=<cp>:family=DejaVu Serif"` and the same for `DejaVu Sans Mono`,
#: which is the font that matters for the box-drawing characters — they only ever appear
#: inside code fences, where no substitution can reach them because verbatim text is
#: verbatim.
#:
#: This list is an allow-list on purpose. :func:`check_font_coverage` fails on anything
#: absent from it, so a new character in the guide stops the build with a message naming
#: the character, rather than vanishing from a page nobody rereads.
COVERED_CHARACTERS: Final[frozenset[str]] = frozenset(
    "—"  # — em dash (489 of them; the guide's signature punctuation)
    "–"  # – en dash
    "§"  # § section sign
    "→"  # → rightwards arrow
    "←"  # ← leftwards arrow
    "≈"  # ≈ almost equal to
    "×"  # × multiplication sign
    "…"  # … horizontal ellipsis
    "·"  # · middle dot
    "ç"  # ç c with cedilla
    "─"  # ─ box drawings light horizontal   ┐
    "│"  # │ box drawings light vertical     ├ the directory trees in
    "├"  # ├ box drawings light vert+right   │ technical-suggestions.md
    "└"  # └ box drawings light up+right     ┘ and start.md, inside fences
    "‘’“”"  # curly quotes — DejaVu carries them; the guide may not
    " "  # non-breaking space
)


def check_font_coverage(text: str) -> None:
    """Fail on any character the pinned fonts cannot set (T019).

    Runs on the *print* intermediate, after :func:`flatten_for_print` has applied
    :data:`PRINT_SUBSTITUTIONS`. Anything non-ASCII still standing must be in
    :data:`COVERED_CHARACTERS`.

    This exists because XeLaTeX's own answer to a missing glyph is a log line and a gap
    on the page. A build that is green and a book that is wrong is the worst of the
    available outcomes; this makes it a loud red one instead.

    Raises:
        BookError: naming the character, its code point, and the two ways out.
    """
    offenders = {
        character
        for character in text
        if ord(character) > 127 and character not in COVERED_CHARACTERS
    }
    if not offenders:
        return

    detail = ", ".join(f"{character!r} (U+{ord(character):04X})" for character in sorted(offenders))
    raise BookError(
        f"The book contains {len(offenders)} character(s) the pinned fonts do not "
        f"carry: {detail}.\n"
        "XeLaTeX would NOT fail on these — it logs 'Missing character' and typesets "
        "nothing, so the text would silently vanish from the printed page. Choose "
        "deliberately, in src/build/book.py:\n"
        "  - add a substitution to PRINT_SUBSTITUTIONS (what ✅/❌ do), or\n"
        "  - add a font to src/theme/book/template.tex that covers it, verify with "
        '`fc-list ":charset=<cp>"` inside the pinned image, and add the character to '
        "COVERED_CHARACTERS.\n"
        "Do not fix this by editing src/pack/ — the prose is the product (C-002, C-006)."
    )


# --------------------------------------------------------------------------------------
# Anchors: one identifier, serving the PDF's \pageref and the HTML's href
# --------------------------------------------------------------------------------------

#: Prefix for chapter anchors. Namespaced so a chapter anchor cannot collide with an
#: identifier pandoc derives from some heading inside a chapter.
_ANCHOR_PREFIX: Final[str] = "ch-"


def chapter_anchor(filename: str) -> str:
    """The anchor for a chapter, derived from its filename.

    Written once into the assembled heading, then read twice: pandoc's LaTeX writer
    turns it into ``\\label{ch-ethics}`` (which :func:`flatten_for_print` points
    ``\\pageref`` at) and its HTML writer turns it into ``id="ch-ethics"`` (which
    :func:`retarget_for_html` points ``href`` at). The PDF's page numbers and the HTML's
    anchors therefore cannot drift apart: they are the same string.

    >>> chapter_anchor("ethics.md")
    'ch-ethics'
    """
    return _ANCHOR_PREFIX + filename.removesuffix(".md")


# --------------------------------------------------------------------------------------
# Segmenting markdown: what a transform may touch, and what it must not
# --------------------------------------------------------------------------------------

#: A fenced code block. Matched FIRST and never transformed.
_FENCE_PATTERN: Final[str] = r"(?P<fence>^(?P<ticks>```+|~~~+)[^\n]*\n.*?^(?P=ticks)[ \t]*$)"

#: An inline code span, backtick count matched so ``` ``a `b` c`` ``` behaves.
_CODE_PATTERN: Final[str] = r"(?P<code>(?P<bt>`+)(?P<inner>.+?)(?P=bt))"

#: A markdown inline link. The label may contain nested brackets one level deep, which
#: is what ``[**[`ethics.md`](ethics.md)**]`` style prose needs.
_LINK_PATTERN: Final[str] = (
    r"(?P<link>\[(?P<label>(?:[^\[\]]|\[[^\[\]]*\])*)\]\((?P<target>[^()\s]*)\))"
)

#: The order of these alternatives is load-bearing, but not in the way it looks.
#:
#: Python's alternation picks the alternative that matches at the *earliest position*,
#: and only breaks a tie at the same position by order. That is exactly the rule this
#: transform needs, and it is what keeps T018's exclusion honest:
#:
#:   ``[`ethics.md`](ethics.md)``   the `[` is first, so this is a LINK and gets
#:                                  flattened — backticks inside the label and all.
#:   `` `[ethics.md](ethics.md)` `` the backtick is first, so this is an inline code
#:                                  SPAN and is left exactly as written.
#:
#: The second is the guide documenting its own bare-sibling link convention (C-001) with
#: an example. A regex that rewrote it would replace an illustration of a rule with an
#: instance of the rule's output, and the guide would stop being able to explain itself.
#: This is the same exclusion WP07 applies.
_SEGMENT_PATTERN: Final[re.Pattern[str]] = re.compile(
    "|".join((_FENCE_PATTERN, _CODE_PATTERN, _LINK_PATTERN)),
    re.MULTILINE | re.DOTALL,
)


def _transform(
    text: str,
    *,
    on_link: Callable[[str, str], str | None],
    on_code: Callable[[str], str | None],
) -> str:
    """Walk ``text``, offering links and inline code spans to the callbacks.

    Fenced code blocks are handed to nobody. Prose between segments is copied verbatim.
    A callback returning ``None`` means "leave this exactly as it was".

    Args:
        text: markdown.
        on_link: called with ``(label, target)``; returns replacement markdown or None.
        on_code: called with the code span's *content*; returns replacement or None.
    """
    out: list[str] = []
    cursor = 0
    for match in _SEGMENT_PATTERN.finditer(text):
        out.append(text[cursor : match.start()])
        cursor = match.end()

        if match.group("fence") is not None:
            out.append(match.group("fence"))
        elif match.group("code") is not None:
            replacement = on_code(match.group("inner"))
            out.append(match.group("code") if replacement is None else replacement)
        else:
            replacement = on_link(match.group("label"), match.group("target"))
            out.append(match.group("link") if replacement is None else replacement)
    out.append(text[cursor:])
    return "".join(out)


# --------------------------------------------------------------------------------------
# T017 — assembly
# --------------------------------------------------------------------------------------

#: An ATX H1 at the very start of a line. Only ever applied to a line already known to
#: sit outside a fence (see :func:`_h1_lines`).
_H1: Final[re.Pattern[str]] = re.compile(r"^#\s+(?P<title>.+?)\s*$")

_FENCE_LINE: Final[re.Pattern[str]] = re.compile(r"^(```+|~~~+)")

#: TeX's ten special characters, for the one place the build hands a title to TeX
#: directly (the running head) rather than letting pandoc escape it.
_TEX_SPECIALS: Final[Mapping[str, str]] = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def _tex_escape(text: str) -> str:
    """Escape ``text`` for raw LaTeX. Backslash first, or the escapes escape each other."""
    out = text.replace("\\", "\x00")
    for character, replacement in _TEX_SPECIALS.items():
        if character != "\\":
            out = out.replace(character, replacement)
    return out.replace("\x00", _TEX_SPECIALS["\\"])


def _h1_lines(text: str) -> list[int]:
    """Indices of every top-level heading line, ignoring fenced code.

    Fence-aware because the pack's code blocks are full of shell comments — ``# a
    comment`` at the start of a line inside a fence is not a chapter heading, and
    counting it as one would be a wrong answer with a plausible-looking cause.
    """
    found: list[int] = []
    fence: str | None = None
    for index, line in enumerate(text.splitlines()):
        opener = _FENCE_LINE.match(line)
        if fence is None:
            if opener:
                fence = opener.group(1)[:3]
                continue
        else:
            if opener and line.strip().startswith(fence):
                fence = None
            continue
        if _H1.match(line):
            found.append(index)
    return found


def _chapter_body(document: Document, pack_dir: Path) -> str:
    """One chapter's source, with its H1 carrying the chapter anchor.

    The heading *text* is the document's own H1, verbatim. The guide's words are the
    product; the build adds an identifier and nothing else (C-002).
    """
    path = pack_dir / document.filename
    if not path.is_file():
        raise BookError(f"{document.filename}: declared as a chapter but not in {pack_dir}.")

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    headings = _h1_lines(text)

    if not headings:
        raise BookError(
            f"{document.filename}: no top-level heading. Every chapter opens with an H1, "
            "which is what becomes the chapter in the book."
        )
    if len(headings) > 1:
        extra = ", ".join(f"line {n + 1}" for n in headings[1:])
        raise BookError(
            f"{document.filename}: {len(headings)} top-level headings ({extra}). "
            "Each `#` becomes a chapter, so this document would silently become "
            f"{len(headings)} chapters and the book would have more chapters than the "
            "reading order declares. Demote the extras to `##`."
        )

    first = headings[0]
    if first != 0:
        raise BookError(
            f"{document.filename}: the H1 is on line {first + 1}, not line 1. "
            "Content above the chapter heading would be attributed to the previous "
            "chapter in the book."
        )

    match = _H1.match(lines[0])
    assert match is not None  # _h1_lines only reports lines that match.
    lines[0] = f"# {match.group('title')} {{#{chapter_anchor(document.filename)}}}"

    # The running head, and why it is set here rather than in the template.
    #
    # The chapter headings are sentences: "How we tell it — an alternate reality game,
    # told diegetically" is 56 characters and does not fit in a running head. LaTeX does
    # not complain — it overprints the margin. The short title the head needs is the nav
    # title, which the template cannot know and the guide's own H1 does not carry.
    #
    # A raw LaTeX block is invisible to pandoc's HTML writer, so it costs the HTML book
    # nothing and the intermediate stays genuinely shared.
    head = _tex_escape(document.title)
    lines.insert(1, f"\n```{{=latex}}\n\\chaptermark{{{head}}}\n```")

    return "\n".join(lines).strip("\n") + "\n"


def assemble(config: BuildConfig, documents: Iterable[Document] | None = None) -> str:
    """Assemble the chapters into one markdown document, in the declared order.

    The order is :func:`build.roles.chapters` — that is, ``mkdocs.yml``'s ``nav`` — and
    it is not restated here. **There is no chapter list in this module**, deliberately:
    a second list is the drift the roles declaration exists to end
    (contracts/roles-declaration.md). Add a chapter to ``nav`` and it appears in the
    book; there is nothing else to remember.

    ``not_in_book`` documents are excluded by construction rather than by filtering —
    ``chapters()`` never returns them. ``README.md`` is the pack branch's front door and
    ``start.md`` is a bootstrap whose first instruction is ``mkdir``; a reader who
    reaches page one of a book has consented to neither.

    Heading levels are already correct and need no shifting: each chapter's single H1
    becomes a chapter (via pandoc's ``--top-level-division=chapter``) and its ``##``
    become sections. :func:`_chapter_body` enforces the "single H1, on line 1"
    precondition that makes that true, rather than assuming it.

    Args:
        config: the parsed declaration.
        documents: pre-loaded documents; loaded from ``config`` when omitted.

    Returns:
        The intermediate markdown. Both renderings derive from this exact string.
    """
    resolved = list(documents) if documents is not None else load_documents(config.pack_dir, config)
    book_chapters = chapters(resolved)
    if not book_chapters:
        raise BookError("The declaration lists no chapters, so there is no book to build.")

    parts = [_chapter_body(document, config.pack_dir) for document in book_chapters]
    return "\n\n".join(parts)


# --------------------------------------------------------------------------------------
# T018 — flattening cross-references for paper
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class _Reference:
    """What a pack filename resolves to for a reader who cannot click."""

    document: Document
    #: Rendered as a standalone replacement, e.g. "Chapter 6, *Ethics* (page 88)".
    standalone: str
    #: Rendered as a parenthetical after a prose label, e.g. "(Chapter 6, ..., page 88)".
    parenthetical: str


def _reference_index(documents: Iterable[Document], config: BuildConfig) -> dict[str, _Reference]:
    """Map every pack filename to the print-safe reference that replaces it.

    Two kinds of target, two answers, because a paper reader needs different things:

    - **A chapter** resolves inside the book: chapter number, title, and a page number
      via LaTeX's ``\\pageref``. The reader turns to it.
    - **A ``not_in_book`` document** — ``README.md``, and ``start.md``, which publishes
      as ``AGENTS.md`` (FR-010) — is not in the book at all, so there is no page to turn
      to. It resolves to its published URL, composed by ``config.absolute_url`` and
      nothing else (NFR-001). The reader types it, which is the only thing paper affords.
    """
    index: dict[str, _Reference] = {}
    for document in documents:
        if document.is_chapter:
            anchor = chapter_anchor(document.filename)
            body = f"Chapter {document.position}, *{document.title}*"
            index[document.filename] = _Reference(
                document=document,
                standalone=f"{body} (page \\pageref{{{anchor}}})",
                parenthetical=f"({body}, page \\pageref{{{anchor}}})",
            )
        else:
            url = config.absolute_url(published_name(document.filename))
            body = f"*{document.title}*, published at <{url}>"
            index[document.filename] = _Reference(
                document=document,
                standalone=body,
                parenthetical=f"({body})",
            )
    return index


#: A link target that names a pack document: bare, no path, optionally with a fragment.
#: Bare-sibling is the invariant the whole architecture rests on (C-001), so a target
#: with a slash in it is not a pack cross-reference and is left for `links.py` to judge.
_PACK_TARGET: Final[re.Pattern[str]] = re.compile(r"^(?P<name>[\w.-]+\.md)(?P<fragment>#.*)?$")

#: An inline code span whose content is *exactly* a filename — nothing else.
#:
#: This is the line between a reference and an example, and it is the whole of T018's
#: exclusion rule. `` `ethics.md` `` is the guide naming a document: on paper that is a
#: dead end, so it is flattened. `` `src/pack/ethics.md` ``, `` `[e.md](e.md)` `` and
#: `` `mkdir -p my-node` `` are the guide showing you something; they are printed as
#: written, because a sample that has been "helpfully" resolved is no longer a sample.
_BARE_FILENAME: Final[re.Pattern[str]] = re.compile(r"^[\w.-]+\.md$")


def _link_target_document(target: str, index: Mapping[str, _Reference]) -> _Reference | None:
    match = _PACK_TARGET.match(target)
    if match is None:
        return None
    return index.get(match.group("name"))


def _label_is_just_the_filename(label: str, filename: str) -> bool:
    """Whether the link's label says nothing the reference will not say better.

    ``[`ethics.md`](ethics.md)`` and ``[**ethics.md**](ethics.md)`` are the guide's
    house style for a bare cross-link: the label *is* the target. Keeping it would print
    "ethics.md (Chapter 6, Ethics, page 88)", which re-introduces on paper the very
    filename the flattening exists to remove.
    """
    return label.strip().strip("`*_ ").strip() == filename


def flatten_for_print(
    text: str,
    config: BuildConfig,
    documents: Iterable[Document] | None = None,
) -> str:
    """Resolve every pack cross-reference to something a paper reader can act on (FR-004).

    **This is a requirement, not a finish (T018).** A PDF that still says "see
    `ethics.md`" is not a book; it is a website someone printed. It fails SC-003 at the
    only moment that matters — a human, holding paper, trying to follow a pointer that
    is not there.

    What it does:

    - ``[`ethics.md`](ethics.md)`` → ``Chapter 6, *Ethics* (page 88)``
    - ``[the moral floor](ethics.md)`` → ``the moral floor (Chapter 6, *Ethics*, page 88)``
    - `` `ethics.md` `` in running prose → ``Chapter 6, *Ethics* (page 88)``
    - ``[start.md](start.md)`` → the bootstrap's *published URL*, since it is not in the
      book and so has no page to point at.

    What it deliberately does not touch:

    - **Fenced code blocks** — every character is literal.
    - **Inline code that is not exactly a filename** — ``` `[e.md](e.md)` ```,
      ``` `src/pack/e.md` ```, ``` `mkdir -p my-node` ``` are illustrations. The guide
      documents its own link convention by showing it; resolving the demonstration into
      its own output would leave the guide unable to state its own rule.
    - **External links** — a URL is as followable on paper as it ever was.

    It runs on the assembled intermediate. ``src/pack/`` is never opened for writing
    (C-002, C-006): the guide's prose is correct for the web, and print is the build's
    problem to solve.

    The page numbers are ``\\pageref`` — resolved by LaTeX at the second pass, against
    the ``\\label`` that :func:`chapter_anchor` put on each chapter. The build does not
    guess a page; TeX knows.
    """
    resolved = list(documents) if documents is not None else load_documents(config.pack_dir, config)
    index = _reference_index(resolved, config)

    def on_link(label: str, target: str) -> str | None:
        reference = _link_target_document(target, index)
        if reference is None:
            return None  # An external URL, an anchor, or something links.py will judge.
        if _label_is_just_the_filename(label, reference.document.filename):
            return reference.standalone
        return f"{label} {reference.parenthetical}"

    def on_code(inner: str) -> str | None:
        if not _BARE_FILENAME.match(inner):
            return None  # An example, not a reference. Print it as written.
        reference = index.get(inner)
        return None if reference is None else reference.standalone

    flattened = _transform(text, on_link=on_link, on_code=on_code)
    for character, replacement in PRINT_SUBSTITUTIONS.items():
        flattened = flattened.replace(character, replacement)

    check_print_ready(flattened, config, resolved)
    check_font_coverage(flattened)
    return flattened


def check_print_ready(
    text: str,
    config: BuildConfig,
    documents: Iterable[Document] | None = None,
) -> None:
    """Assert no click-dependent cross-reference survived the flattening (FR-004).

    The reviewer's own check, run by the build instead of by hand: *"search the PDF for
    `.md` — any surviving click-dependent reference is an FR-004 failure."* Left to a
    human with a PDF viewer, this gets done once.

    Scoped to what FR-004 actually forbids, so that it can be enforced rather than
    negotiated: a **link** into the pack, and an **inline-code span that is exactly a
    pack filename**. A filename inside a fenced code block is a command someone types
    and stays; a URL prints fine. Those are not failures and a check that called them
    failures would be switched off within a week.

    Raises:
        BookError: naming every survivor.
    """
    resolved = list(documents) if documents is not None else load_documents(config.pack_dir, config)
    index = _reference_index(resolved, config)
    survivors: list[str] = []

    def on_link(label: str, target: str) -> None:
        if _link_target_document(target, index) is not None:
            survivors.append(f"[{label}]({target})")
        return None

    def on_code(inner: str) -> None:
        if _BARE_FILENAME.match(inner) and inner in index:
            survivors.append(f"`{inner}`")
        return None

    _transform(text, on_link=on_link, on_code=on_code)
    if survivors:
        listed = ", ".join(sorted(set(survivors)))
        raise BookError(
            f"{len(survivors)} cross-reference(s) survived flattening and would print as "
            f"un-followable pointers: {listed}. A reader holding paper cannot click "
            "them (FR-004). Fix flatten_for_print(); do not edit src/pack/."
        )


# --------------------------------------------------------------------------------------
# T021 — the single-file HTML book
# --------------------------------------------------------------------------------------


def retarget_for_html(
    text: str,
    config: BuildConfig,
    documents: Iterable[Document] | None = None,
) -> str:
    """Repoint the same cross-references at the single-file book's own anchors (FR-003).

    **T018's flattening is deliberately NOT applied here, and this is the decision the
    work package asked to be made on purpose.** Print and HTML have opposite needs. On
    paper a link is a dead end, so it must become a page number. On screen a link is the
    best thing available, so turning it into "Chapter 6, *Ethics* (page 88)" would take
    a working affordance away and replace it with a page number that does not exist —
    the HTML book has no pages.

    But the links cannot be left alone either, and that is the subtlety. In the pack,
    ``[ethics.md](ethics.md)`` resolves because ``ethics.md`` sits next to the file
    naming it (C-001). In a *single-file* book there are no siblings: the same href from
    ``book.html`` points at a file that was never published there, and 404s. So the
    links stay links and change destination — to ``#ch-ethics``, the same anchor
    :func:`flatten_for_print` gives ``\\pageref``.

    ``not_in_book`` documents are not in this file at all, so they resolve to their
    published URLs via ``config.absolute_url`` (NFR-001) — the same answer the print
    path gives them, for the same reason.

    Inline code is untouched: `` `ethics.md` `` is readable prose on screen, and here
    the reader has the chapter links, the ToC and a find-in-page.
    """
    resolved = list(documents) if documents is not None else load_documents(config.pack_dir, config)
    by_filename = {document.filename: document for document in resolved}

    def on_link(label: str, target: str) -> str | None:
        match = _PACK_TARGET.match(target)
        if match is None:
            return None
        document = by_filename.get(match.group("name"))
        if document is None:
            return None
        if document.is_chapter:
            return f"[{label}](#{chapter_anchor(document.filename)})"
        url = config.absolute_url(published_name(document.filename))
        return f"[{label}]({url})"

    def on_code(inner: str) -> None:
        return None

    return _transform(text, on_link=on_link, on_code=on_code)


# --------------------------------------------------------------------------------------
# Rendering: shelling out to the pinned toolchain
# --------------------------------------------------------------------------------------

BOOK_TITLE: Final[str] = "The Dungeon Master's Guide"
BOOK_SUBTITLE: Final[str] = (
    "The creator kit for a shared, permissionless world of diegetic conspiracy satire"
)


@dataclass(frozen=True)
class PandocRunner:
    """How to reach pandoc: inside the pinned image, or on this machine.

    ``container`` is the answer for CI and for anyone who wants the same PDF twice
    (T020). ``local`` exists because a two-second edit/render loop is worth having and
    because CI may already be *running inside* the image, where a nested ``docker run``
    is neither possible nor useful.
    """

    kind: str
    repo_root: Path

    def command(self, args: list[str]) -> list[str]:
        if self.kind == "container":
            return [
                "docker",
                "run",
                "--rm",
                "--volume",
                f"{self.repo_root}:/data",
                "--workdir",
                "/data",
                # Reproducible PDF metadata: without this XeLaTeX stamps wall-clock time
                # into the file and two builds of one pack differ byte for byte.
                "--env",
                "SOURCE_DATE_EPOCH=0",
                "--env",
                "FORCE_SOURCE_DATE=1",
                PINNED_PANDOC_IMAGE,
                *args,
            ]
        return ["pandoc", *args]

    @property
    def environment(self) -> dict[str, str]:
        env = dict(os.environ)
        if self.kind == "local":
            env.setdefault("SOURCE_DATE_EPOCH", "0")
            env.setdefault("FORCE_SOURCE_DATE", "1")
        return env


def resolve_runner(kind: str, repo_root: Path) -> PandocRunner:
    """Pick a runner, and refuse to pretend when the tool is not there.

    ``auto`` prefers the container: it is the pinned toolchain and the only one whose
    output is reproducible. It falls back to a local pandoc rather than failing, because
    a contributor without Docker should still be able to build a book — the typography
    may differ from CI's, which is exactly why CI does not use this path.
    """
    if kind not in {"auto", "container", "local"}:
        raise BookError(f"Unknown runner {kind!r}. Use auto, container, or local.")

    if kind in {"auto", "container"} and shutil.which("docker"):
        return PandocRunner(kind="container", repo_root=repo_root)
    if kind == "container":
        raise BookError(
            "The container runner needs docker on PATH, and it is not there. "
            f"The pinned toolchain is {PINNED_PANDOC_IMAGE}. Use --runner local to "
            "render with this machine's pandoc instead, accepting that its fonts and "
            "TeX are not the ones CI uses."
        )
    if not shutil.which("pandoc"):
        raise BookError(
            "Neither docker nor pandoc is on PATH, so there is no way to render the "
            f"book. Install docker (preferred — the toolchain is pinned to "
            f"{PINNED_PANDOC_IMAGE}) or install pandoc with a XeLaTeX distribution."
        )
    return PandocRunner(kind="local", repo_root=repo_root)


def _run(runner: PandocRunner, args: list[str], *, what: str) -> None:
    command = runner.command(args)
    result = subprocess.run(
        command,
        cwd=runner.repo_root,
        capture_output=True,
        text=True,
        env=runner.environment,
    )
    if result.returncode != 0:
        raise BookError(
            f"{what} failed (exit {result.returncode}).\n"
            f"  command: {' '.join(command)}\n"
            f"{result.stdout}\n{result.stderr}"
        )
    _report_missing_glyphs(result.stdout + result.stderr, what)


#: XeLaTeX's way of telling you a glyph is absent: a log line, and a gap on the page.
_MISSING_CHARACTER: Final[re.Pattern[str]] = re.compile(r"^Missing character:.*$", re.MULTILINE)


def _report_missing_glyphs(log: str, what: str) -> None:
    """Turn XeLaTeX's most dangerous warning into a failure.

    ``check_font_coverage`` catches this before the render, from the source. This is the
    belt to that braces, and it reads the one place that has the final say: XeLaTeX
    itself, on the actual fonts it actually loaded. A run that logs "Missing character"
    has produced a PDF with text missing from it and exited zero.
    """
    missing = _MISSING_CHARACTER.findall(log)
    if missing:
        detail = "\n  ".join(sorted(set(missing))[:10])
        raise BookError(
            f"{what} produced a PDF with characters silently dropped — XeLaTeX logged "
            f"{len(missing)} 'Missing character' warning(s) and exited 0:\n  {detail}\n"
            "The affected text is absent from the printed page. Add a substitution to "
            "PRINT_SUBSTITUTIONS or a font to src/theme/book/template.tex."
        )


def _relative(path: Path, root: Path) -> str:
    """A repo-root-relative POSIX path — what the container sees under /data."""
    return path.resolve().relative_to(root.resolve()).as_posix()


def write_intermediates(
    config: BuildConfig,
    output_dir: Path,
    documents: Iterable[Document] | None = None,
) -> tuple[Path, Path]:
    """Write the shared intermediate and its print transform.

    Returns:
        ``(intermediate, print_intermediate)``.
    """
    resolved = list(documents) if documents is not None else load_documents(config.pack_dir, config)
    output_dir.mkdir(parents=True, exist_ok=True)

    intermediate = output_dir / INTERMEDIATE_FILENAME
    intermediate.write_text(assemble(config, resolved), encoding="utf-8")

    print_intermediate = output_dir / PRINT_INTERMEDIATE_FILENAME
    print_intermediate.write_text(
        flatten_for_print(intermediate.read_text(encoding="utf-8"), config, resolved),
        encoding="utf-8",
    )
    return intermediate, print_intermediate


def render_pdf(
    config: BuildConfig,
    output_dir: Path,
    repo_root: Path,
    runner: PandocRunner,
    documents: Iterable[Document] | None = None,
) -> tuple[Path, float]:
    """Render the printable book (FR-004). Returns the PDF path and elapsed seconds."""
    resolved = list(documents) if documents is not None else load_documents(config.pack_dir, config)
    _, print_intermediate = write_intermediates(config, output_dir, resolved)

    template = repo_root / TEMPLATE_PATH
    if not template.is_file():
        raise BookError(f"No LaTeX template at {template}.")

    pdf = output_dir / PDF_BOOK_FILENAME
    started = time.monotonic()
    _run(
        runner,
        [
            _relative(print_intermediate, repo_root),
            "--from",
            "markdown",
            "--to",
            "pdf",
            "--pdf-engine",
            "xelatex",
            # Two passes minimum, or every \pageref from T018's flattening prints as
            # "??" — the cross-references would be flattened and then useless.
            "--pdf-engine-opt=-interaction=nonstopmode",
            "--template",
            _relative(template, repo_root),
            "--top-level-division=chapter",
            "--toc",
            "--toc-depth=2",
            "--number-sections",
            "--highlight-style=monochrome",
            "--metadata",
            f"title={BOOK_TITLE}",
            "--metadata",
            f"subtitle={BOOK_SUBTITLE}",
            # `lang` is deliberately NOT set. pandoc's common partial keys babel off it
            # and takes the language from a \documentclass option this template does not
            # have, which loads babel with no language and hyphenates as American
            # English — silently, on every page. template.tex requests British babel
            # itself and sets pdflang by hand.
            #
            # The title page prints the live address. Composed by absolute_url and
            # nowhere else (NFR-001) — a printed book carrying a stale hand-typed URL is
            # the domain switch (SC-006) failing in the least recoverable medium there is.
            "--metadata",
            f"base-url={config.absolute_url('')}",
            "--output",
            _relative(pdf, repo_root),
        ],
        what="Rendering the PDF",
    )
    return pdf, time.monotonic() - started


def render_html(
    config: BuildConfig,
    output_dir: Path,
    repo_root: Path,
    runner: PandocRunner,
    documents: Iterable[Document] | None = None,
) -> Path:
    """Render the single-file HTML book (FR-003)."""
    resolved = list(documents) if documents is not None else load_documents(config.pack_dir, config)
    output_dir.mkdir(parents=True, exist_ok=True)

    source = output_dir / WEB_INTERMEDIATE_FILENAME
    source.write_text(
        retarget_for_html(assemble(config, resolved), config, resolved),
        encoding="utf-8",
    )

    html = output_dir / HTML_BOOK_FILENAME
    _run(
        runner,
        [
            _relative(source, repo_root),
            "--from",
            "markdown",
            "--to",
            "html5",
            "--standalone",
            # FR-003 says "one single-file HTML document", so the stylesheet is inlined
            # rather than linked: a book.html that needs a sibling .css to be readable
            # is two files wearing one name.
            "--embed-resources",
            "--toc",
            "--toc-depth=2",
            "--number-sections",
            "--section-divs",
            "--highlight-style=monochrome",
            "--css",
            _relative(repo_root / "src/theme/book/book.css", repo_root),
            "--metadata",
            f"title={BOOK_TITLE}",
            "--metadata",
            f"subtitle={BOOK_SUBTITLE}",
            "--metadata",
            "lang=en-GB",
            "--output",
            _relative(html, repo_root),
        ],
        what="Rendering the HTML book",
    )
    return html
