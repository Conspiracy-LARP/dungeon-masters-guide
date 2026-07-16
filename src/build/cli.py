"""The `guide` command line: checks now, generators as later work packages land."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from build.book import (
    DEFAULT_OUTPUT_DIR,
    EXPECTED_PDF_SECONDS,
    PINNED_PANDOC_IMAGE,
    BookError,
    render_html,
    render_pdf,
    resolve_runner,
    write_intermediates,
)
from build.config import BuildConfig, ConfigError, load_config
from build.provenance import ProvenanceError, verify_provenance
from build.roles import (
    RoleError,
    check_declaration,
    check_drift,
    chapters,
    current_branch,
    drift_is_fatal,
    load_documents,
)


def _config() -> BuildConfig:
    try:
        return load_config()
    except ConfigError as exc:
        raise click.ClickException(str(exc)) from exc


@click.group()
@click.version_option()
def guide() -> None:
    """Build the Dungeon Master's Guide from src/pack/.

    Every surface derives from the pack. Nothing here ever writes to it.
    """


@guide.group()
def roles() -> None:
    """The roles declaration: the single source of chapter order and document roles."""


@roles.command("lint")
def roles_lint() -> None:
    """Check every document in src/pack/ has exactly one declared role (FR-011).

    Fails — loudly, naming the file — on a document declared in neither list, one
    declared in both, or a declaration naming a file that is not there.
    """
    config = _config()
    try:
        check_declaration(config.pack_dir, config)
        documents = load_documents(config.pack_dir, config)
    except RoleError as exc:
        click.secho(str(exc), fg="red", err=True)
        sys.exit(1)

    book = chapters(documents)
    click.secho(
        f"OK: {len(documents)} documents, all declared "
        f"({len(book)} chapters, {len(documents) - len(book)} not in the book).",
        fg="green",
    )


@roles.command("list")
def roles_list() -> None:
    """Show the reading order and the roles as declared."""
    config = _config()
    try:
        documents = load_documents(config.pack_dir, config)
    except RoleError as exc:
        raise click.ClickException(str(exc)) from exc

    for document in documents:
        position = f"{document.position:>2}." if document.position else "  -"
        published = (
            f"  (published as {document.published_name})"
            if document.published_name != document.filename
            else ""
        )
        click.echo(
            f"{position} [{document.role.value}] {document.filename} — {document.title}{published}"
        )


@roles.command("check-drift")
@click.option(
    "--branch",
    default=None,
    help="Branch to judge strictness against. Defaults to the checked-out branch.",
)
def roles_check_drift(branch: str | None) -> None:
    """Compare the guide's prose lists against the declaration. Reports; never fixes.

    Drift WARNS (exit 0) on feature branches and FAILS (non-zero) on main: prose and
    config drift naturally mid-edit and a hard failure would punish the writer, but
    drift must never reach main, where the prose is what creators read.
    """
    config = _config()
    try:
        findings = check_drift(config.pack_dir, config)
    except RoleError as exc:
        raise click.ClickException(str(exc)) from exc

    resolved_branch = branch if branch is not None else current_branch()

    if not findings:
        click.secho("OK: the prose lists agree with the declaration.", fg="green")
        return

    fatal = drift_is_fatal(resolved_branch)
    label = "DRIFT" if fatal else "WARNING: drift"
    click.secho(
        f"{label} ({len(findings)} finding(s)) on branch {resolved_branch or '?'}:",
        fg="red" if fatal else "yellow",
        err=True,
    )
    for finding in findings:
        click.secho(f"  - {finding.describe()}", fg="red" if fatal else "yellow", err=True)

    if fatal:
        click.secho(
            "Drift must not reach main: the prose is what creators read. "
            "Fix the prose by hand — the build never edits src/pack/ (C-002).",
            fg="red",
            err=True,
        )
        sys.exit(1)

    click.secho(
        "Warning only on a feature branch; this WILL fail on main. Fix the prose by hand.",
        fg="yellow",
        err=True,
    )


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


@guide.group()
def book() -> None:
    """The cover-to-cover book: one document, two renderings (FR-003, FR-004).

    Every chapter, in the order mkdocs.yml declares, assembled once into an
    intermediate that both the HTML book and the PDF derive from — so the two
    cannot disagree about what the book says or what order it says it in.
    """


_runner_option = click.option(
    "--runner",
    type=click.Choice(["auto", "container", "local"]),
    default="auto",
    show_default=True,
    help=(
        "Where pandoc runs. `container` is the pinned toolchain and the reproducible "
        "answer; `local` uses this machine's pandoc, whose fonts and TeX are not CI's."
    ),
)

_output_option = click.option(
    "--output",
    "output_dir",
    type=click.Path(file_okay=False, path_type=Path),
    default=None,
    help=f"Where to write the book. [default: {DEFAULT_OUTPUT_DIR}]",
)


def _resolve_output(output_dir: Path | None) -> Path:
    return output_dir if output_dir is not None else _repo_root() / DEFAULT_OUTPUT_DIR


@book.command("assemble")
@_output_option
def book_assemble(output_dir: Path | None) -> None:
    """Assemble the chapters into the intermediate both renderings derive from (T017).

    Writes the shared intermediate and its print transform, and nothing else — no
    pandoc, no TeX. This is the command to run when you want to read what the
    cross-reference flattening actually did.
    """
    config = _config()
    target = _resolve_output(output_dir)
    try:
        intermediate, print_intermediate = write_intermediates(config, target)
    except (BookError, RoleError) as exc:
        click.secho(str(exc), fg="red", err=True)
        sys.exit(1)

    documents = load_documents(config.pack_dir, config)
    book_chapters = chapters(documents)
    click.secho(
        f"OK: {len(book_chapters)} chapters assembled in reading order.\n"
        f"  intermediate : {intermediate}\n"
        f"  for print    : {print_intermediate}  (cross-references flattened)",
        fg="green",
    )


@book.command("html")
@_output_option
@_runner_option
def book_html(output_dir: Path | None, runner: str) -> None:
    """Render the single-file HTML book (FR-003).

    Links stay links here and are repointed at the book's own anchors — the print
    flattening is deliberately not applied, because on screen a link is the best
    thing available and a page number is a fiction.
    """
    config = _config()
    target = _resolve_output(output_dir)
    try:
        resolved = resolve_runner(runner, _repo_root())
        html = render_html(config, target, _repo_root(), resolved)
    except (BookError, RoleError) as exc:
        click.secho(str(exc), fg="red", err=True)
        sys.exit(1)
    click.secho(f"OK: {html} ({resolved.kind} runner).", fg="green")


@book.command("pdf")
@_output_option
@_runner_option
def book_pdf(output_dir: Path | None, runner: str) -> None:
    """Render the printable book (FR-004).

    Title page, a table of contents with page numbers, real pagination, and every
    cross-reference resolved to a chapter and a page — because the reader is holding
    paper and cannot click.
    """
    config = _config()
    target = _resolve_output(output_dir)
    try:
        resolved = resolve_runner(runner, _repo_root())
        pdf, elapsed = render_pdf(config, target, _repo_root(), resolved)
    except (BookError, RoleError) as exc:
        click.secho(str(exc), fg="red", err=True)
        sys.exit(1)

    click.secho(f"OK: {pdf} in {elapsed:.1f}s ({resolved.kind} runner).", fg="green")
    if elapsed > EXPECTED_PDF_SECONDS * 2:
        click.secho(
            f"Slower than the {EXPECTED_PDF_SECONDS}s this is budgeted at (NFR-005 gives "
            "the whole pipeline 5 minutes). If the image was cold, that is the pull; if "
            "it was warm, tell WP08.",
            fg="yellow",
            err=True,
        )


@book.command("image")
def book_image() -> None:
    """Print the pinned pandoc/XeLaTeX image (T020), for WP08 to wire into CI.

    Pinned by digest, not by tag: a tag is a moving target, and "the PDF changed and
    nobody touched the pack" is the drift NFR-003 exists to make impossible.
    """
    click.echo(PINNED_PANDOC_IMAGE)


@guide.group()
def verify() -> None:
    """Checks over built output."""


@verify.command("provenance")
@click.option(
    "--output",
    "output_dir",
    required=True,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="The built output directory to verify.",
)
def verify_provenance_command(output_dir: Path) -> None:
    """Assert every published file traces back to a pack document (NFR-003).

    A file that is neither derived from a src/pack/ document nor a known generated
    artifact is hand-authored published content, which NFR-003 forbids — and which is
    how a surface starts disagreeing with the guide's own text.
    """
    config = _config()
    try:
        verify_provenance(output_dir, config)
    except (ProvenanceError, RoleError) as exc:
        click.secho(str(exc), fg="red", err=True)
        sys.exit(1)
    click.secho(f"OK: every file in {output_dir} traces back to src/pack/.", fg="green")


if __name__ == "__main__":  # pragma: no cover
    guide()
