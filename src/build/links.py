"""Cross-references between pack documents, and the three rules that keep them honest.

The load-bearing invariant of this whole architecture is one sentence: **every link
between pack documents is a bare sibling name with no path**. That single property is
why one set of bytes serves the site, the book, the ``pack`` branch and GitHub's
rendering with no rewrite step. Lose it and every surface needs its own link rewriter,
which is the design this project exists to avoid.

So the rules (data-model.md § Cross-reference, C-001, FR-013):

1. ``target`` contains no path separator.
2. ``target`` resolves on ``main``, where the bootstrap is ``start.md``.
3. ``target`` resolves on the pack branch, where the bootstrap is ``AGENTS.md``.

**Rule 3 is not redundant with rule 2.** They have already disagreed in this project's
history. On 2026-07-16 ``src/pack/README.md`` was written with a link to ``AGENTS.md``:
correct on the pack branch, a 404 on ``main``, where the file is ``start.md``. It was
caught only by an ad-hoc check that happened to be run. The two branches are the only
surfaces where the *same bytes* must resolve against *different filenames*, so they are
the only place this asymmetry can bite — and it has. See
``tests/test_links.py::test_the_2026_07_16_readme_regression``.

**Only prose counts.** A Cross-reference has ``context: prose | code_example``, and the
guide *teaches* the bare-sibling convention by showing examples in inline code —
``quickstart.md``, ``CLAUDE.md`` and ``doc/build.md`` all contain things like
``` `[ethics.md](ethics.md)` ``` as illustrations. A naive extractor treats those as
real links and flags the guide's own explanatory prose. The checker must distinguish a
link from a picture of a link, which is why code is blanked *before* extraction rather
than filtered afterwards. Get this wrong and every later rule fires on false positives
until someone switches the check off.

This module never writes to ``src/pack/`` (C-002, C-006). It reports; a human fixes.
"""

from __future__ import annotations

import enum
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from build.config import BuildConfig
from build.packbranch import build_tree
from build.rename import PUBLISHED_NAME, SOURCE_NAME
from build.roles import ASSET_SUFFIXES, load_assets, load_documents


class LinkError(RuntimeError):
    """The link check cannot be run at all."""


class Branch(enum.Enum):
    """A branch on which the same bytes must resolve against different filenames."""

    MAIN = "main"
    PACK = "pack"

    @property
    def bootstrap(self) -> str:
        """The bootstrap document's name on this branch (FR-010, C-004)."""
        return SOURCE_NAME if self is Branch.MAIN else PUBLISHED_NAME


class Rule(enum.Enum):
    """Which of the three rules a finding violates."""

    #: Rule 1 — a path separator in a link target (C-001).
    PATH_SEPARATOR = "path_separator"
    #: Rules 2 and 3 — the target names no document on that branch.
    UNRESOLVED = "unresolved"


# --------------------------------------------------------------------------------------
# T032 — extraction. The real links, and only the real links.
# --------------------------------------------------------------------------------------

#: An opening or closing fence: three or more backticks or tildes, indented at most 3.
_FENCE: Final[re.Pattern[str]] = re.compile(r"^ {0,3}(?P<ticks>`{3,}|~{3,})")

#: A code span: a run of backticks, matching body, matching run.
#:
#: The backreference — rather than a fixed count — is what makes the *documentation* of
#: this convention safe to write. The guide's own prompt shows a link sample as
#: ``` `` `[ethics.md](ethics.md)` `` ```: a two-tick span whose body legitimately
#: contains single ticks. A pattern hard-coded to one backtick would close early, spit
#: the sample back out as prose, and flag the sentence explaining the rule.
#:
#: The body may not contain a blank line: per CommonMark a code span does not span
#: paragraphs, and without that guard a single stray backtick in prose would blank the
#: rest of the document and hide every real link after it. Failing open like that is
#: worse than a false positive — the check would silently stop checking.
_CODE_SPAN: Final[re.Pattern[str]] = re.compile(
    r"(?P<ticks>`+)(?P<body>(?:(?!\n[ \t]*\n).)+?)(?P=ticks)",
    re.DOTALL,
)

#: An inline markdown link. The optional trailing group is a link title —
#: ``[x](ethics.md "The moral floor")`` — which is not part of the target.
_LINK: Final[re.Pattern[str]] = re.compile(
    r"\[(?P<text>[^\]]*)\]\(\s*(?P<target><[^>]*>|[^)\s]*)(?:\s+[\"'][^\"']*[\"'])?\s*\)"
)

#: A URI scheme (``http:``, ``https:``, ``mailto:``) or a protocol-relative ``//host``.
_EXTERNAL: Final[re.Pattern[str]] = re.compile(r"^(?:[A-Za-z][A-Za-z0-9+.\-]*:|//)")


@dataclass(frozen=True)
class Link:
    """One relative cross-reference, as written in prose.

    Never a code example: those are excluded before extraction, so a ``Link`` that
    exists at all is one a reader can click.
    """

    #: The target exactly as written, anchor and all — e.g. ``ethics.md#the-floor``.
    target: str
    #: 1-based line of the link's opening bracket.
    line: int
    #: 1-based column of the link's opening bracket.
    column: int

    @property
    def path(self) -> str:
        """The document part of the target: the anchor, if any, is not a filename."""
        return self.target.split("#", 1)[0]

    @property
    def has_separator(self) -> bool:
        """Whether the target carries a path — the one thing rule 1 forbids."""
        return "/" in self.path or "\\" in self.path


def _blank(text: str) -> str:
    """Replace ``text`` with spaces, keeping newlines so positions survive.

    Blanking rather than deleting is deliberate: every line and column reported to a
    human then refers to the file as they will open it, not to some stripped derivative
    whose numbers drift from the source the moment a code block appears above the link.
    """
    return "".join("\n" if character == "\n" else " " for character in text)


def strip_code(text: str) -> str:
    """Blank every fenced block and code span, leaving prose at its original offsets.

    The ``context: prose | code_example`` distinction from data-model.md, made
    operational. Fences go first and line-wise, because a code span pattern turned loose
    on a fenced block full of backticks pairs them arbitrarily across the fence.

    >>> strip_code("see [ethics.md](ethics.md)")
    'see [ethics.md](ethics.md)'
    >>> strip_code("write `[ethics.md](ethics.md)`").strip()
    'write'
    """
    lines = text.split("\n")
    result: list[str] = []
    fence: str | None = None

    for line in lines:
        match = _FENCE.match(line)
        if fence is None:
            if match is not None:
                fence = match.group("ticks")[0]
                result.append(_blank(line))
                continue
            result.append(line)
            continue
        # Inside a fence: a closing fence is one of the same character.
        if match is not None and match.group("ticks")[0] == fence:
            fence = None
        result.append(_blank(line))

    return _CODE_SPAN.sub(lambda m: _blank(m.group(0)), "\n".join(result))


def extract_links(text: str) -> list[Link]:
    """Every relative cross-reference in ``text``, with its position.

    Excluded, and each for its own reason:

    - **Code examples** (fences and spans) — illustrations, not links (T032). The guide
      documents this very convention in inline code.
    - **External links** (``http://``, ``https://``, ``mailto:``) — not ours to resolve.
    - **Pure anchors** (``#the-floor``) — a jump within one document, no filename.

    Args:
        text: the markdown source of one document.

    Returns:
        The prose links, in document order.
    """
    prose = strip_code(text)
    links: list[Link] = []

    for match in _LINK.finditer(prose):
        target = match.group("target").strip()
        if target.startswith("<") and target.endswith(">"):
            target = target[1:-1].strip()
        if not target or target.startswith("#") or _EXTERNAL.match(target):
            continue

        offset = match.start()
        line = prose.count("\n", 0, offset) + 1
        column = offset - (prose.rfind("\n", 0, offset) + 1) + 1
        links.append(Link(target=target, line=line, column=column))

    return links


# --------------------------------------------------------------------------------------
# Surfaces and findings.
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Surface:
    """One branch's documents: the names that exist, and the bytes that link to them.

    Both halves matter, and they differ between branches. ``main`` publishes
    ``start.md``; the pack branch renames it to ``AGENTS.md`` *and* rewrites the
    references pointing at it. Checking one branch's names against the other's bytes
    would be exactly the mistake this module exists to catch.
    """

    branch: Branch
    #: Published name → the document's text on that branch. Scanned for links.
    documents: dict[str, str]
    #: Published names of assets on this branch. A valid link target, never scanned.
    #:
    #: Two separate things are being tracked, and conflating them is a real bug rather
    #: than a tidiness point: an asset **exists** (so ``![...](hansard-1926.svg)``
    #: resolves) but is not prose (so its innards are not link-extracted). Fold assets
    #: into ``documents`` and the checker starts hunting for markdown links inside SVG
    #: markup, which is both meaningless and eventually a false positive.
    assets: frozenset[str] = frozenset()

    @property
    def names(self) -> set[str]:
        """Every filename that exists on this branch, prose and assets alike."""
        return set(self.documents) | set(self.assets)


@dataclass(frozen=True)
class Finding:
    """One violation, named precisely enough to act on without re-deriving it."""

    #: The file as a human would open it — ``src/pack/README.md``.
    source: str
    line: int
    target: str
    rule: Rule
    #: The branch the failure occurred on. ``None`` for rule 1, which is branch-agnostic.
    branch: Branch | None = None
    #: For an unresolved target: the branch it *does* resolve on, if any.
    resolves_on: Branch | None = None

    def describe(self) -> str:
        """The message. It explains *why*, because a rule whose point is invisible
        looks like pedantry, and pedantry gets disabled."""
        where = f"{self.source}:{self.line}"

        if self.rule is Rule.PATH_SEPARATOR:
            bare = self.target.split("/")[-1].split("\\")[-1]
            return (
                f"{where} — link target `{self.target}` contains a path separator. "
                f"Links must be bare sibling names (`{bare}`), because the same bytes "
                "are served from four different roots: the site, the book, the pack "
                "branch and GitHub's rendering. A path that is correct in one of them "
                "is a 404 in the other three, and no rewrite step exists to fix it — "
                "the flatness is what removes the need for one (C-001). This is "
                "load-bearing, not style."
            )

        branch = self.branch.value if self.branch else "?"
        bootstrap = self.branch.bootstrap if self.branch else "?"
        message = (
            f"{where} — link target `{self.target}` does not resolve on `{branch}`, "
            f"where the bootstrap is `{bootstrap}`."
        )
        if self.resolves_on is not None:
            message += (
                f" It DOES resolve on `{self.resolves_on.value}`, where the bootstrap "
                f"is `{self.resolves_on.bootstrap}`. The same bytes must resolve on "
                "both branches; one link cannot be right on only one of them."
            )
        else:
            message += " There is no such document on either branch."
        return message


# --------------------------------------------------------------------------------------
# T034 — the two surfaces.
# --------------------------------------------------------------------------------------


def main_surface(config: BuildConfig, pack_dir: Path | None = None) -> Surface:
    """The branch as ``main`` publishes it: ``src/pack/`` verbatim, bootstrap ``start.md``."""
    resolved = config.pack_dir if pack_dir is None else pack_dir
    documents = load_documents(resolved, config)
    return Surface(
        branch=Branch.MAIN,
        documents={
            document.filename: (resolved / document.filename).read_text(encoding="utf-8")
            for document in documents
        },
        assets=frozenset(load_assets(resolved)),
    )


def pack_surface(config: BuildConfig, pack_dir: Path | None = None) -> Surface:
    """The branch as the pack tip publishes it: bootstrap ``AGENTS.md``, references rewritten.

    Built by WP06's :func:`packbranch.build_tree` — the same code path as
    ``guide pack build``, whose tree is verified byte-identical to the live branch. The
    tree is materialised and read back rather than reasoned about, because the bytes on
    the branch are the thing under test; a checker with its own idea of what the branch
    contains is a checker that can be right about a branch nobody ships.
    """
    with tempfile.TemporaryDirectory() as directory:
        out_dir = Path(directory)
        files = build_tree(out_dir, config, pack_dir=pack_dir)
        asset_names = {
            built.published_name
            for built in files
            if Path(built.published_name).suffix.lower() in ASSET_SUFFIXES
        }
        return Surface(
            branch=Branch.PACK,
            documents={
                built.published_name: (out_dir / built.published_name).read_text(encoding="utf-8")
                for built in files
                if built.published_name not in asset_names
            },
            assets=frozenset(asset_names),
        )


def check_path_separators(surface: Surface, label: str = "src/pack") -> list[Finding]:
    """Rule 1 (T033, C-001): no link target may carry a path.

    Checked against ``main``'s bytes only, and that is not laziness: the pack branch
    carries the same links (the rewrite repoints the bootstrap, it never introduces a
    directory), so checking both would report every violation twice and say nothing new.

    This one rule is why the pack must stay flat. A helpful IDE "fix" turning
    ``ethics.md`` into ``src/pack/ethics.md`` breaks the site, the book, the branch and
    GitHub's rendering simultaneously, and each one fails somewhere else.
    """
    return [
        Finding(
            source=f"{label}/{name}",
            line=link.line,
            target=link.target,
            rule=Rule.PATH_SEPARATOR,
        )
        for name, text in sorted(surface.documents.items())
        for link in extract_links(text)
        if link.has_separator
    ]


def check_resolution(surface: Surface, other: Surface, label: str) -> list[Finding]:
    """Rules 2 and 3 (T034): every link resolves against ``surface``'s own filenames.

    ``other`` is consulted only to say *where else* a broken link resolves. That detail
    is the whole point: "link broken" sends someone reading; "resolves on `pack`, 404 on
    `main`" tells them they have hit the rename asymmetry and names both halves of it.

    Targets carrying a path are skipped — rule 1 has already reported them, with a
    better explanation than "not found" would be.
    """
    findings: list[Finding] = []
    for name, text in sorted(surface.documents.items()):
        for link in extract_links(text):
            if link.has_separator or link.path in surface.names:
                continue
            # Assets live on `main` only, by decision: the pack branch is markdown and
            # nothing else, because it exists to be read by a model that cannot see an
            # SVG anyway (see build.packbranch). An `![...](x.svg)` reference is therefore
            # *expected* to dangle there, and the both-branches rule does not apply to it.
            #
            # Exempted by name rather than by a glob that quietly fails to match it: the
            # asymmetry is deliberate, so it is stated here where someone will read it. A
            # broken link to a *document* is still caught exactly as before, and so is an
            # asset link on `main`, where the file must really exist.
            if surface.branch is Branch.PACK and Path(link.path).suffix.lower() in ASSET_SUFFIXES:
                continue
            findings.append(
                Finding(
                    source=f"{label}/{name}",
                    line=link.line,
                    target=link.target,
                    rule=Rule.UNRESOLVED,
                    branch=surface.branch,
                    resolves_on=other.branch if link.path in other.names else None,
                )
            )
    return findings


def check_links(config: BuildConfig, pack_dir: Path | None = None) -> list[Finding]:
    """All three rules, over both branches. The check ``guide links check`` runs.

    Returns:
        Every finding, rule 1 first. Empty means the pack's cross-references are sound
        on ``main`` and on the pack branch simultaneously — which is the only state in
        which one set of bytes can serve both.

    Raises:
        RoleError: a document resolves to no role, or the pack is not flat.
        PackBranchError: the pack branch tree cannot be built.
    """
    main = main_surface(config, pack_dir=pack_dir)
    pack = pack_surface(config, pack_dir=pack_dir)

    findings = check_path_separators(main)
    findings += check_resolution(main, other=pack, label="src/pack")
    findings += check_resolution(pack, other=main, label="pack branch")
    return findings
