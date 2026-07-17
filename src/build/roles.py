"""Documents, roles, and the checks that keep the declaration honest.

The entity the whole build reasons about. Every `.md` in ``src/pack/`` resolves to
exactly one role — ``chapter`` (in the book's reading flow, at a position) or
``not_in_book`` (published, but outside it). A file that resolves to neither is a
**build failure**, not a warning (FR-011).

That loudness is the feature. The failure it prevents is silent: a new document that is
neither declared nor noticed simply never appears in the book, and nobody finds out
(R-003). A warning in a CI log is indistinguishable from silence.
"""

from __future__ import annotations

import enum
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Iterable, Final

from build.config import BuildConfig, load_config
from build.rename import published_name


class RoleError(RuntimeError):
    """A document's role cannot be resolved, or a declaration is inconsistent."""


class Role(enum.Enum):
    """What a document is for."""

    CHAPTER = "chapter"
    NOT_IN_BOOK = "not_in_book"


@dataclass(frozen=True)
class Document:
    """One markdown file in ``src/pack/``. See data-model.md."""

    filename: str
    role: Role
    #: 1-based position in the reading order; ``None`` for ``not_in_book``.
    position: int | None
    title: str
    #: Same as ``filename``, except the bootstrap — ``start.md`` → ``AGENTS.md``.
    published_name: str

    @property
    def is_chapter(self) -> bool:
        return self.role is Role.CHAPTER


def _first_h1(path: Path) -> str | None:
    """The document's first H1, used as a title when nav does not declare one."""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


def _pack_files(pack_dir: Path) -> list[str]:
    """Every markdown file in the pack.

    ``glob`` rather than ``rglob``: the pack is flat (C-001). A nested `.md` is caught
    below and failed rather than quietly included.
    """
    _assert_flat(pack_dir)
    return sorted(p.name for p in pack_dir.glob("*.md"))


def _assert_flat(pack_dir: Path) -> None:
    """The pack has no subdirectories. Shared by the document and asset scans."""
    if not pack_dir.is_dir():
        raise RoleError(f"No pack directory at {pack_dir}.")

    nested = [p for p in pack_dir.rglob("*") if p.is_file() and p.parent != pack_dir]
    if nested:
        listed = ", ".join(sorted(str(p.relative_to(pack_dir)) for p in nested))
        raise RoleError(
            f"The pack is not flat — found {listed}. Every cross-link between pack "
            "documents is a bare sibling (`[ethics.md](ethics.md)`), which is the "
            "single property that lets one set of bytes serve the site, the book, the "
            "pack branch and GitHub's rendering with no rewrite step (C-001)."
        )


#: Asset extensions the pack may hold alongside its markdown.
#:
#: The pack is flat (C-001), and "flat" forbids *subdirectories*, not non-markdown files.
#: ``![...](hansard-1926.svg)`` is a bare sibling link exactly like ``[ethics.md](ethics.md)``,
#: so an asset beside the prose obeys the invariant rather than breaking it, and resolves on
#: the site, the pack branch and GitHub's own rendering alike.
#:
#: Two kinds, for two jobs. ``.svg`` is for art the guide draws itself (the Ceefax teletext,
#: the duty roster) — text, so it diffs and reviews in git. ``.png`` is for *screenshots of the
#: guide's own live exhibit pages*: a fake web page is a real web page (hosted with the org-root
#: site), and the guide shows a photograph of it, because a photograph of a web page is a raster
#: image, not a diagram. Widening this set is a decision, not a convenience: every surface in
#: :mod:`build` must carry whatever is listed here (verified: the site copies both; the book
#: leaves image refs unembedded, as it already does for the SVGs; the pack branch takes neither).
ASSET_SUFFIXES: Final[frozenset[str]] = frozenset({".svg", ".png"})


def load_assets(pack_dir: Path) -> list[str]:
    """Every asset in the pack, sorted.

    Assets are declared by *extension* rather than by nav entry: they are not documents,
    have no role, and appear in no reading order. This is the explicit exemption. A stray
    file the pack should not hold (a ``.png``, a ``.docx``, an editor backup) is not
    silently tolerated by a glob that happens not to match it — it fails
    :func:`check_pack_contents` by name.

    Raises:
        RoleError: the pack is not flat.
    """
    _assert_flat(pack_dir)
    return sorted(p.name for p in pack_dir.glob("*") if p.suffix.lower() in ASSET_SUFFIXES)


def check_pack_contents(pack_dir: Path) -> None:
    """Fail on any pack file that is neither a document nor a permitted asset.

    Without this, the pack's contract is enforced by omission: ``_pack_files`` globs
    ``*.md`` and :func:`load_assets` globs the asset suffixes, and anything else simply
    goes unmentioned by both — present in the tree, absent from every surface. That is a
    check reporting success without looking, which is the defect this build keeps
    producing. Name the strays instead.

    Raises:
        RoleError: the pack holds a file of an unrecognised kind.
    """
    _assert_flat(pack_dir)
    permitted = {".md", *ASSET_SUFFIXES}
    strays = sorted(
        p.name for p in pack_dir.glob("*") if p.is_file() and p.suffix.lower() not in permitted
    )
    if strays:
        raise RoleError(
            f"The pack holds files that are neither documents nor permitted assets: "
            f"{', '.join(strays)}. src/pack/ is the product: markdown, plus assets in "
            f"{sorted(ASSET_SUFFIXES)}. Anything else belongs in src/build/ or doc/. If a "
            "new asset kind is genuinely needed, add it to ASSET_SUFFIXES and teach every "
            "surface (site, book, llms.txt, pack branch) to carry it — in that order."
        )


def load_documents(pack_dir: Path, config: BuildConfig) -> list[Document]:
    """Resolve every document in the pack to exactly one role.

    The declaration (``config``) is authoritative; the filesystem is checked against it.

    Args:
        pack_dir: the pack directory, normally ``config.pack_dir``.
        config: the parsed declaration.

    Returns:
        Chapters first in reading order, then ``not_in_book`` documents.

    Raises:
        RoleError: a document resolves to no role, or to two, or a declaration names a
            file that is not there, or the pack is not flat.
    """
    check_declaration(pack_dir, config)

    documents: list[Document] = []
    for position, filename in enumerate(config.nav, start=1):
        title = config.nav_titles.get(filename) or _first_h1(pack_dir / filename) or filename
        documents.append(
            Document(
                filename=filename,
                role=Role.CHAPTER,
                position=position,
                title=title,
                published_name=published_name(filename),
            )
        )

    for filename in config.not_in_book:
        title = _first_h1(pack_dir / filename) or filename
        documents.append(
            Document(
                filename=filename,
                role=Role.NOT_IN_BOOK,
                position=None,
                title=title,
                published_name=published_name(filename),
            )
        )

    _validate_positions(documents)
    return documents


def _validate_positions(documents: Iterable[Document]) -> None:
    """Chapter positions are contiguous from 1 (data-model.md)."""
    positions = [d.position for d in documents if d.is_chapter]
    expected = list(range(1, len(positions) + 1))
    if positions != expected:
        raise RoleError(f"Chapter positions are not contiguous from 1: got {positions}.")


def chapters(documents: Iterable[Document]) -> list[Document]:
    """The reading order: chapters, in nav order.

    What the book, `llms.txt` and `llms-full.txt` consume. Derived — never re-declared.
    """
    return sorted(
        (d for d in documents if d.is_chapter),
        key=lambda d: d.position or 0,
    )


def check_declaration(pack_dir: Path, config: BuildConfig) -> None:
    """The role lint (FR-011). Raise on any violation of the contract's rules 1–3.

    Also asserts that ``not_in_nav`` and ``extra.pack.not_in_book`` list the same files:
    two lists that can disagree is precisely the drift the declaration exists to end
    (contract § "The `--strict` interaction", point 3).
    """
    errors: list[str] = []

    on_disk = set(_pack_files(pack_dir))
    nav = list(config.nav)
    not_in_book = list(config.not_in_book)
    declared = nav + not_in_book

    # Rule 2 — no file in both lists.
    both = sorted(set(nav) & set(not_in_book))
    for name in both:
        errors.append(
            f"{name}: declared in BOTH `nav` and `extra.pack.not_in_book`. "
            "A document has exactly one role; pick one."
        )

    # A file declared twice within one list is the same class of mistake.
    for name in sorted(set(declared)):
        if declared.count(name) > 1 and name not in both:
            errors.append(f"{name}: declared more than once in mkdocs.yml.")

    # Rule 3 — no declaration names a file that does not exist.
    for name in sorted(set(declared)):
        if name not in on_disk:
            errors.append(
                f"{name}: declared in mkdocs.yml but not present in {pack_dir}. "
                "Remove the declaration, or restore the file."
            )

    # Rule 1 — every file on disk is declared. THE one that matters.
    for name in sorted(on_disk - set(declared)):
        errors.append(
            f"{name}: present in {pack_dir} but declared in neither `nav` nor "
            "`extra.pack.not_in_book`. Add it to `nav` (with its title, in reading "
            "order) if it is a chapter, or to `extra.pack.not_in_book` if it is not. "
            "An undeclared document would silently never appear in the book."
        )

    # not_in_nav must mirror not_in_book.
    if set(config.not_in_nav) != set(config.not_in_book):
        only_nav = sorted(set(config.not_in_nav) - set(config.not_in_book))
        only_book = sorted(set(config.not_in_book) - set(config.not_in_nav))
        detail = []
        if only_nav:
            detail.append(f"only in `not_in_nav`: {', '.join(only_nav)}")
        if only_book:
            detail.append(f"only in `extra.pack.not_in_book`: {', '.join(only_book)}")
        errors.append(
            "`not_in_nav` and `extra.pack.not_in_book` disagree (" + "; ".join(detail) + "). "
            "They must list the same files: `not_in_nav` keeps `mkdocs build --strict` "
            "from failing on the intentional omission, and `not_in_book` is what the "
            "build reads. If they can disagree, they will."
        )

    if errors:
        raise RoleError(
            "The roles declaration in mkdocs.yml does not match src/pack/:\n"
            + "\n".join(f"  - {e}" for e in errors)
        )


# --------------------------------------------------------------------------------------
# Prose drift (T011). Report; never fix.
# --------------------------------------------------------------------------------------

#: The prose lists that repeat the document set, and which we keep honest.
#:
#: These are checked by SET MEMBERSHIP, not order. The subtask asks for "missing or
#: extra", and the two lists legitimately order their entries differently from `nav`
#: for their own rhetorical reasons — README leads with the kit, the quick-read box
#: leads with the on-ramp. Comparing order would report drift against prose that is
#: not wrong, and a check that cries wolf gets switched off.
#:
#: Each list has a scope, because each is doing a different job:
#:  - README.md is the pack branch's front door: it indexes every published document
#:    except itself.
#:  - creator-kit.md's quick-read box is a reading guide: the chapters, except itself.
README_FILENAME: Final[str] = "README.md"
CREATOR_KIT_FILENAME: Final[str] = "creator-kit.md"

#: A markdown link target ending in `.md`, from a list bullet.
_BULLET_LINK: Final[re.Pattern[str]] = re.compile(r"^\s*>?\s*[-*]\s+.*?\]\(([^)]+\.md)\)")


@dataclass(frozen=True)
class DriftFinding:
    """One mismatch between a prose list and the declaration."""

    prose_file: str
    filename: str
    kind: str  # "missing" | "extra"

    def describe(self) -> str:
        if self.kind == "missing":
            return (
                f"{self.prose_file}: does not list {self.filename}, which the "
                "declaration says is published. A reader of the prose would never "
                "learn the document exists."
            )
        return (
            f"{self.prose_file}: lists {self.filename}, which the declaration does "
            "not include. The prose points at a document that is not published."
        )


def _extract_section_bullets(text: str, heading: str) -> list[str]:
    """Link targets from the bullets under ``heading``, up to the next heading."""
    found: list[str] = []
    in_section = False
    for line in text.splitlines():
        if line.startswith("## "):
            in_section = line[3:].strip().lower() == heading.lower()
            continue
        if in_section:
            match = _BULLET_LINK.match(line)
            if match:
                found.append(match.group(1))
    return found


def _extract_blockquote_bullets(text: str) -> list[str]:
    """Link targets from the blockquote bullets — creator-kit's quick-read box."""
    return [
        match.group(1)
        for line in text.splitlines()
        if line.lstrip().startswith(">")
        for match in [_BULLET_LINK.match(line)]
        if match
    ]


def check_drift(pack_dir: Path, config: BuildConfig) -> list[DriftFinding]:
    """Compare the guide's prose lists against the declaration.

    **Reports only.** Never writes to ``src/pack/`` (C-002, C-006). The guide's wording
    is the product; a script rewording it is exactly the failure C-002 exists to
    prevent. If the prose is wrong, a human fixes the prose.
    """
    documents = load_documents(pack_dir, config)
    all_declared = {d.filename for d in documents}
    chapter_names = {d.filename for d in chapters(documents)}

    findings: list[DriftFinding] = []

    readme_path = pack_dir / README_FILENAME
    if readme_path.is_file():
        listed = set(
            _extract_section_bullets(readme_path.read_text(encoding="utf-8"), "The documents")
        )
        # The pack's index lists everything published except itself.
        expected = all_declared - {README_FILENAME}
        findings.extend(_compare(README_FILENAME, listed, expected))

    kit_path = pack_dir / CREATOR_KIT_FILENAME
    if kit_path.is_file():
        listed = set(_extract_blockquote_bullets(kit_path.read_text(encoding="utf-8")))
        # The quick-read box is a guide to the chapters, and does not list itself.
        expected = chapter_names - {CREATOR_KIT_FILENAME}
        findings.extend(_compare(CREATOR_KIT_FILENAME, listed, expected))

    return findings


def _compare(prose_file: str, listed: set[str], expected: set[str]) -> list[DriftFinding]:
    findings = [
        DriftFinding(prose_file=prose_file, filename=name, kind="missing")
        for name in sorted(expected - listed)
    ]
    findings.extend(
        DriftFinding(prose_file=prose_file, filename=name, kind="extra")
        for name in sorted(listed - expected)
    )
    return findings


def current_branch() -> str:
    """The checked-out branch, or "" if git cannot say."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""
    return result.stdout.strip()


def drift_is_fatal(branch: str) -> bool:
    """Whether drift should fail the build on ``branch``.

    The decision, already made and not ours to re-litigate: drift **warns** on feature
    branches and **fails** on ``main``. Prose and config drift naturally while someone
    is mid-edit and a hard failure would punish the writer — but drift must never reach
    ``main``, where the prose is what creators read.
    """
    return branch == "main"


def default_config() -> BuildConfig:
    """The repository's own declaration."""
    return load_config()
