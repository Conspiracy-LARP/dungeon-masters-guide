"""The `pack` branch: an orphan mirror of ``src/pack/``, flat, renamed and rewritten.

The branch creators attach to their own project::

    git submodule add -b pack git@github.com:Conspiracy-LARP/dungeon-masters-guide.git doc/core

A submodule cannot take a subdirectory, hence a branch whose root *is* the pack. It is a
**generated artifact, not a history**: an orphan commit, force-pushed on every push to
``main``. That is why R4 rejected `git subtree split` — a split preserves per-file history
that no consumer reads, and it cannot do the half of the job that matters here: the
**rename and the reference rewrite** (FR-010).

Three properties this module exists to hold:

**The tree is exactly the pack's markdown, flat.** No ``src/``, no ``doc/``, no
``.github/``, no ``mkdocs.yml``, no build files (contract, Producer table). Creators asked
for the markdown and none of the machinery; anything extra that leaks in is a defect, not
a convenience. The file list comes from :func:`roles.load_documents` and never from a
glob, so a document nobody declared fails the build here too rather than being silently
mirrored (FR-011).

**The rename is two jobs, always both.** ``start.md`` publishes as ``AGENTS.md`` — the
name models look for — and every reference to it is rewritten to match. Renaming without
rewriting ships a ``README.md`` linking to a file that does not exist on the branch. Both
halves come from :mod:`build.rename`, which WP03 also uses: one definition, so the site
and the branch cannot disagree, and so the ``getting-started.md`` trap is defused once.

**Someone is already depending on this branch.** It was built by hand on 2026-07-16 as
``d024682`` to unblock a real consumer, whose ``doc/core`` submodule points at it now, and
the guide already publishes the `submodule add` command above to readers. Automation that
produced a different tree would make the guide lie to people who followed its published
instructions (R-002). Hence :func:`compare_against_ref` — the reproduction gate (C-005).

Building and pushing are kept apart on purpose: a pure builder is testable, and the tree
is the contract. Pushing is the thin wrapper.
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Sequence

from build.config import BuildConfig
from build.rename import rewrite_references
from build.roles import load_documents

#: The published branch. Consumers pin a submodule to it.
BRANCH_NAME: Final[str] = "pack"

#: The only branch the pack may be published from. The branch mirrors `main`; publishing
#: from anywhere else would ship unreviewed prose to every consumer tracking it.
PUBLISH_SOURCE_BRANCH: Final[str] = "main"

#: The hand-built tip the automation must reproduce before it takes over (C-005).
REFERENCE_COMMIT: Final[str] = "d024682"

#: The generating commit message — the branch's own statement of its contract.
#:
#: This is the text on ``d024682`` and it is reproduced verbatim, because it is the only
#: place the rules are visible to the person who is about to break them: whoever clones
#: the branch, commits a fix directly to it, and would otherwise lose that work at the
#: next force-push. Say it on the branch itself.
COMMIT_MESSAGE: Final[
    str
] = """Publish the creator kit

Generated mirror of src/pack/ from the dungeon-masters-guide repo: the kit's
markdown documents, flat, with no build machinery or meta-documentation.

start.md is published here as AGENTS.md, the name models look for, and
references to it are rewritten to match.

This branch is generated and force-pushed. Do not commit to it directly;
edit src/pack/ on main instead.
"""


class PackBranchError(RuntimeError):
    """The branch tree cannot be built, verified, or published."""


@dataclass(frozen=True)
class BuiltFile:
    """One file as it appears on the branch."""

    #: The name on the branch — ``start.md`` arrives here as ``AGENTS.md``.
    published_name: str
    #: The document it came from, in ``src/pack/``.
    source_name: str
    #: The exact bytes published, after the reference rewrite.
    content: bytes

    @property
    def was_renamed(self) -> bool:
        return self.published_name != self.source_name


def render_documents(pack_dir: Path, config: BuildConfig) -> list[BuiltFile]:
    """Render the branch's files: the pack's markdown, renamed and rewritten.

    Pure: reads ``src/pack/``, writes nothing (C-002, C-006). The file list is derived
    from the declaration via :func:`roles.load_documents`, so an undeclared document
    fails here rather than being mirrored unnoticed.

    The rewrite is applied to **every** document, not only to the one that needs it
    today. ``README.md`` is currently the sole file referencing the bootstrap, but
    special-casing it would mean the next document to link there quietly ships a broken
    link. The rewrite is a no-op on a document with no reference, so applying it
    everywhere costs nothing and cannot be forgotten.

    Returns:
        The branch's files, sorted by published name.

    Raises:
        PackBranchError: two documents would publish under one name.
        RoleError: a document resolves to no role, or the pack is not flat.
    """
    documents = load_documents(pack_dir, config)

    files: list[BuiltFile] = []
    seen: dict[str, str] = {}
    for document in documents:
        collision = seen.get(document.published_name)
        if collision is not None:
            raise PackBranchError(
                f"{collision} and {document.filename} both publish as "
                f"{document.published_name}; one would silently overwrite the other on "
                "the branch. Rename one of them in src/pack/."
            )
        seen[document.published_name] = document.filename

        source = pack_dir / document.filename
        if not source.is_file():
            raise PackBranchError(f"{document.filename} is declared but not present in {pack_dir}.")

        text = source.read_text(encoding="utf-8")
        files.append(
            BuiltFile(
                published_name=document.published_name,
                source_name=document.filename,
                content=rewrite_references(text).encode("utf-8"),
            )
        )

    return sorted(files, key=lambda f: f.published_name)


def _clean_output_dir(out_dir: Path) -> None:
    """Empty ``out_dir`` of a previous build, refusing anything we did not put there.

    Rebuilding into the same directory must be idempotent, so the previous tree goes.
    But this function deletes, so it deletes only what this builder produces: top-level
    ``.md`` files. Anything else — a subdirectory, a non-markdown file — means the path
    is not one of our output trees, and the right response is to stop rather than to
    recursively remove a directory the caller may have meant something else by.
    """
    if not out_dir.exists():
        return
    if not out_dir.is_dir():
        raise PackBranchError(f"{out_dir} exists and is not a directory.")

    unexpected = sorted(p.name for p in out_dir.iterdir() if p.is_dir() or p.suffix != ".md")
    if unexpected:
        raise PackBranchError(
            f"{out_dir} holds entries this builder did not create: {', '.join(unexpected)}. "
            "The pack branch tree is flat markdown and nothing else; refusing to delete "
            "an unrecognised directory. Point --out at a new or previously-built path."
        )
    for path in out_dir.iterdir():
        path.unlink()


def build_tree(out_dir: Path, config: BuildConfig, pack_dir: Path | None = None) -> list[BuiltFile]:
    """Materialise the branch tree into ``out_dir``.

    The tree that becomes the branch, as a pure function of ``src/pack/``. Nothing else
    reaches it: the exclusion of the build machinery is not a filter applied afterwards
    but a consequence of only ever writing the files the declaration names.

    Args:
        out_dir: where to write the tree. Created if absent; a previous build is cleared.
        config: the declaration.
        pack_dir: the pack. Defaults to ``config.pack_dir``.

    Returns:
        The files written, sorted by published name.
    """
    resolved_pack = config.pack_dir if pack_dir is None else pack_dir
    files = render_documents(resolved_pack, config)

    _clean_output_dir(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for built in files:
        (out_dir / built.published_name).write_bytes(built.content)
    return files


# --------------------------------------------------------------------------------------
# The reproduction gate (T029, C-005).
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Difference:
    """One file that differs between the generated tree and the reference commit."""

    published_name: str
    kind: str  # "only_generated" | "only_reference" | "content"

    def describe(self) -> str:
        if self.kind == "only_generated":
            return (
                f"{self.published_name}: generated, but absent from the reference commit. "
                "The automation would add a file the hand build did not publish."
            )
        if self.kind == "only_reference":
            return (
                f"{self.published_name}: on the reference commit, but not generated. "
                "The automation would DELETE a file consumers currently have."
            )
        return (
            f"{self.published_name}: present on both, with different bytes. "
            "Either the hand build or the automation is wrong about this file's content."
        )


@dataclass(frozen=True)
class ComparisonResult:
    """The reproduction gate's verdict."""

    ref: str
    differences: tuple[Difference, ...]
    file_count: int

    @property
    def matches(self) -> bool:
        return not self.differences

    def describe(self) -> str:
        if self.matches:
            return (
                f"Reproduction gate GREEN: the generated tree is byte-identical to {self.ref} "
                f"across all {self.file_count} files. The automation reproduces the hand "
                "build; taking over the branch is safe."
            )
        return (
            f"Reproduction gate RED: the generated tree differs from {self.ref} in "
            f"{len(self.differences)} file(s):\n"
            + "\n".join(f"  - {d.describe()}" for d in self.differences)
            + "\n\nDo NOT force-push. A live consumer tracks this branch. Establish which "
            "side is wrong first: if src/pack/ has legitimately changed since the hand "
            "build, regenerate from that commit's inputs and compare again; if it has "
            "not, the automation has a bug."
        )


def _git(args: Sequence[str], repo_root: Path | None = None) -> str:
    """Run git, returning stdout. Raises PackBranchError on failure."""
    try:
        result = subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            check=True,
            cwd=repo_root,
        )
    except FileNotFoundError as exc:  # pragma: no cover - git is a hard prerequisite
        raise PackBranchError("git is not on PATH.") from exc
    except subprocess.CalledProcessError as exc:
        raise PackBranchError(f"git {' '.join(args)} failed: {exc.stderr.strip()}") from exc
    return result.stdout


def read_ref_tree(ref: str, repo_root: Path | None = None) -> dict[str, bytes]:
    """The flat tree of ``ref``, as published name to bytes.

    Reads the commit out of the object database rather than checking it out: the gate
    must not disturb the working tree it is comparing against.
    """
    listing = _git(["ls-tree", "-r", "--name-only", ref], repo_root=repo_root)
    names = [line for line in listing.splitlines() if line]

    tree: dict[str, bytes] = {}
    for name in names:
        blob = subprocess.run(
            ["git", "cat-file", "blob", f"{ref}:{name}"],
            capture_output=True,
            check=True,
            cwd=repo_root,
        )
        tree[name] = blob.stdout
    return tree


def compare_against_ref(
    files: Sequence[BuiltFile],
    ref: str = REFERENCE_COMMIT,
    repo_root: Path | None = None,
) -> ComparisonResult:
    """Compare a generated tree against the hand-built reference, byte for byte (C-005).

    The gate that stands between this automation and a branch someone's submodule
    already tracks. It compares content, not commit identity: the orphan commit's own
    hash embeds a timestamp and can never match, but the *tree* must.

    A mismatch is a serious finding, not a formality to re-baseline. The hand build was a
    real deployment to a real consumer.
    """
    generated = {built.published_name: built.content for built in files}
    reference = read_ref_tree(ref, repo_root=repo_root)

    differences: list[Difference] = []
    for name in sorted(set(generated) - set(reference)):
        differences.append(Difference(published_name=name, kind="only_generated"))
    for name in sorted(set(reference) - set(generated)):
        differences.append(Difference(published_name=name, kind="only_reference"))
    for name in sorted(set(generated) & set(reference)):
        if generated[name] != reference[name]:
            differences.append(Difference(published_name=name, kind="content"))

    return ComparisonResult(
        ref=ref,
        differences=tuple(differences),
        file_count=len(set(generated) | set(reference)),
    )


# --------------------------------------------------------------------------------------
# The publisher (T030).
# --------------------------------------------------------------------------------------


def _current_branch(repo_root: Path | None = None) -> str:
    return _git(["rev-parse", "--abbrev-ref", "HEAD"], repo_root=repo_root).strip()


def _is_ci() -> bool:
    """Whether we are running in CI. GitHub Actions sets both; ``CI`` is the convention."""
    return os.environ.get("GITHUB_ACTIONS") == "true" or os.environ.get("CI") == "true"


def check_publish_allowed(repo_root: Path | None = None) -> None:
    """Refuse to publish from anywhere but CI on ``main`` (T030).

    Force-pushing this branch is safe *only* because it is a read-only mirror of `main`.
    From a laptop it stops being that: a developer mid-edit publishes their working tree
    to every consumer tracking the branch, and the guide's published `submodule add`
    command starts serving unreviewed prose. The failure is silent to the person who
    caused it and visible only to consumers.

    Raises:
        PackBranchError: not in CI, or not on ``main``.
    """
    if not _is_ci():
        raise PackBranchError(
            "Refusing to publish: the pack branch is force-pushed to every consumer that "
            "tracks it, and this is not CI. Run `guide pack build --out <dir>` to inspect "
            "the tree locally; publishing happens from CI on main only."
        )
    branch = _current_branch(repo_root=repo_root)
    if branch != PUBLISH_SOURCE_BRANCH:
        raise PackBranchError(
            f"Refusing to publish from {branch!r}: the pack branch mirrors "
            f"{PUBLISH_SOURCE_BRANCH!r}, and publishing from anywhere else would ship "
            "unreviewed prose to every consumer tracking it."
        )


def _write_tree(files: Sequence[BuiltFile], repo_root: Path | None = None) -> str:
    """Write ``files`` into the object database and return the flat tree's hash."""
    entries: list[str] = []
    for built in sorted(files, key=lambda f: f.published_name):
        blob = subprocess.run(
            ["git", "hash-object", "-w", "--stdin"],
            input=built.content,
            capture_output=True,
            check=True,
            cwd=repo_root,
        )
        entries.append(f"100644 blob {blob.stdout.decode().strip()}\t{built.published_name}")

    tree = subprocess.run(
        ["git", "mktree"],
        input=("\n".join(entries) + "\n").encode("utf-8"),
        capture_output=True,
        check=True,
        cwd=repo_root,
    )
    return tree.stdout.decode().strip()


def _remote_tree(remote: str, repo_root: Path | None = None) -> str | None:
    """The tree hash currently published on the branch, or None if it has no tip."""
    try:
        return _git(["rev-parse", f"{remote}/{BRANCH_NAME}^{{tree}}"], repo_root=repo_root).strip()
    except PackBranchError:
        return None


def publish(
    files: Sequence[BuiltFile],
    remote: str = "origin",
    repo_root: Path | None = None,
    dry_run: bool = False,
) -> tuple[str, bool]:
    """Force-push an orphan commit carrying ``files`` to the pack branch.

    Idempotent in the sense that matters: the tree is a pure function of ``src/pack/``,
    so an unchanged pack yields an identical tree, and this function then does **not**
    push. Skipping the no-op push is what keeps the branch stable — a fresh orphan commit
    every CI run would give consumers a new tip, and a spurious submodule diff, for a
    tree that never changed.

    Returns:
        The commit hash, and whether it was pushed (False means already current).
    """
    check_publish_allowed(repo_root=repo_root)

    tree = _write_tree(files, repo_root=repo_root)
    if _remote_tree(remote, repo_root=repo_root) == tree:
        return tree, False

    # No `-p`: an orphan commit. The branch carries no history because it has none to
    # carry — it is a mirror, regenerated from `main` every time (R4).
    commit = (
        subprocess.run(
            ["git", "commit-tree", tree, "-m", COMMIT_MESSAGE],
            capture_output=True,
            check=True,
            cwd=repo_root,
        )
        .stdout.decode()
        .strip()
    )

    if not dry_run:
        _git(
            ["push", "--force", remote, f"{commit}:refs/heads/{BRANCH_NAME}"],
            repo_root=repo_root,
        )
    return commit, True
