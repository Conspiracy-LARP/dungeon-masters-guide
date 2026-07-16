"""The `guide` command line: checks now, generators as later work packages land."""

from __future__ import annotations

import sys
from pathlib import Path

import click

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
        click.echo(f"{position} [{document.role.value}] {document.filename} — {document.title}{published}")


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
    click.secho(f"{label} ({len(findings)} finding(s)) on branch {resolved_branch or '?'}:", fg="red" if fatal else "yellow", err=True)
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
