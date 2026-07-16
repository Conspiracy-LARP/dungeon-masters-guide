"""The `guide` command line: checks now, generators as later work packages land."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from build.config import BuildConfig, ConfigError, load_config
from build.llms import DEFAULT_OUTPUT_DIR, LlmsError, write_full, write_index
from build.packbranch import (
    REFERENCE_COMMIT,
    PackBranchError,
    build_tree,
    compare_against_ref,
    publish,
    render_documents,
)
from build.links import LinkError, Rule, check_links
from build.provenance import ProvenanceError, verify_provenance
from build.roles import (
    Document,
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


@guide.group()
def llms() -> None:
    """The machine-readable surfaces: llms.txt and llms-full.txt.

    Both are generated from the declaration and the pack (NFR-003). Neither is ever
    hand-written: a hand-written index is a second copy of the reading order, and it
    starts lying the first time a chapter moves.
    """


def _documents() -> tuple[BuildConfig, list[Document]]:
    config = _config()
    try:
        return config, load_documents(config.pack_dir, config)
    except RoleError as exc:
        raise click.ClickException(str(exc)) from exc


@llms.command("index")
@click.option(
    "--output",
    "output_dir",
    default=DEFAULT_OUTPUT_DIR,
    show_default=True,
    type=click.Path(file_okay=False, path_type=Path),
    help="Directory to write llms.txt into. Created if absent.",
)
def llms_index(output_dir: Path) -> None:
    """Generate llms.txt — the machine index, with the bootstrap first (FR-005).

    Follows the llmstxt.org convention with one deliberate deviation: the first entry is
    not a document but a procedure. A model told to help someone build a node should
    follow the bootstrap, not read ten chapters and then ask what they want.
    """
    config, documents = _documents()
    try:
        written = write_index(config, documents, output_dir)
    except LlmsError as exc:
        raise click.ClickException(str(exc)) from exc
    click.secho(
        f"Wrote {written} ({len(chapters(documents))} chapters, bootstrap first).", fg="green"
    )


@llms.command("full")
@click.option(
    "--output",
    "output_dir",
    default=DEFAULT_OUTPUT_DIR,
    show_default=True,
    type=click.Path(file_okay=False, path_type=Path),
    help="Directory to write llms-full.txt into. Created if absent.",
)
def llms_full(output_dir: Path) -> None:
    """Generate llms-full.txt — every chapter concatenated, in reading order (FR-006).

    Chapters only, byte-for-byte. The bootstrap is not buried in here; it has its own
    address.
    """
    config, documents = _documents()
    try:
        written = write_full(config, documents, output_dir)
    except LlmsError as exc:
        raise click.ClickException(str(exc)) from exc
    click.secho(
        f"Wrote {written} ({len(chapters(documents))} chapters, in reading order).", fg="green"
    )


@guide.group()
def pack() -> None:
    """The pack branch: the flat markdown mirror creators attach as a submodule."""


@pack.command("build")
@click.option(
    "--out",
    "out_dir",
    required=True,
    type=click.Path(file_okay=False, path_type=Path),
    help="Directory to materialise the branch tree into.",
)
def pack_build(out_dir: Path) -> None:
    """Materialise the pack branch tree: src/pack/'s markdown, flat, renamed (FR-009).

    Builds only; never pushes. The tree is the contract, so it is inspectable on its own.
    """
    config = _config()
    try:
        files = build_tree(out_dir, config)
    except (PackBranchError, RoleError) as exc:
        click.secho(str(exc), fg="red", err=True)
        sys.exit(1)

    renamed = [f for f in files if f.was_renamed]
    click.secho(f"OK: {len(files)} documents written to {out_dir}.", fg="green")
    for built in renamed:
        click.echo(f"  renamed: {built.source_name} -> {built.published_name}")


@pack.command("verify-reproduction")
@click.option(
    "--ref",
    default=REFERENCE_COMMIT,
    show_default=True,
    help="The commit the generated tree must reproduce byte-for-byte.",
)
def pack_verify_reproduction(ref: str) -> None:
    """Compare the generated tree against the hand-built pack tip (C-005).

    The gate between this automation and a branch a live consumer's submodule tracks. A
    mismatch is a finding to investigate, not a baseline to update: either the hand build
    or the automation is wrong, and force-pushing before knowing which breaks the
    `submodule add` command the guide already publishes to readers (R-002).
    """
    config = _config()
    try:
        files = render_documents(config.pack_dir, config)
        result = compare_against_ref(files, ref=ref)
    except (PackBranchError, RoleError) as exc:
        click.secho(str(exc), fg="red", err=True)
        sys.exit(1)

    if not result.matches:
        click.secho(result.describe(), fg="red", err=True)
        sys.exit(1)
    click.secho(result.describe(), fg="green")


@pack.command("publish")
@click.option("--remote", default="origin", show_default=True, help="The remote to push to.")
@click.option(
    "--dry-run",
    is_flag=True,
    help="Build the tree and the commit, but do not push.",
)
def pack_publish(remote: str, dry_run: bool) -> None:
    """Force-push the pack branch as an orphan commit (FR-009). CI on main only.

    Idempotent: an unchanged src/pack/ yields an identical tree and no push at all, so
    consumers do not see a new tip for a tree that never moved.
    """
    config = _config()
    try:
        files = render_documents(config.pack_dir, config)
        commit, pushed = publish(files, remote=remote, dry_run=dry_run)
    except (PackBranchError, RoleError) as exc:
        click.secho(str(exc), fg="red", err=True)
        sys.exit(1)

    if not pushed:
        click.secho(f"OK: {remote}/pack already carries this tree; nothing to push.", fg="green")
        return
    action = "would push (dry run)" if dry_run else "pushed"
    click.secho(f"OK: {action} {commit[:7]} to {remote}/pack ({len(files)} documents).", fg="green")


@guide.group()
def links() -> None:
    """Cross-references: the bare-sibling invariant the whole architecture rests on."""


@links.command("check")
def links_check() -> None:
    """Check every cross-reference resolves on BOTH branches, with no paths (FR-013).

    Three rules, from data-model.md: no path separator (C-001); resolves on `main`,
    where the bootstrap is `start.md`; resolves on the pack branch, where it is
    `AGENTS.md`. The third is not redundant — a `README.md` link to `AGENTS.md` once
    resolved on the branch and 404'd on `main`, and only an ad-hoc check caught it.

    Reports; never fixes. The build does not write to src/pack/ (C-002).
    """
    config = _config()
    try:
        findings = check_links(config)
    except (LinkError, PackBranchError, RoleError) as exc:
        click.secho(str(exc), fg="red", err=True)
        sys.exit(1)

    if not findings:
        click.secho(
            "OK: every cross-reference is a bare sibling name, and resolves on both "
            "`main` (bootstrap start.md) and the pack branch (bootstrap AGENTS.md).",
            fg="green",
        )
        return

    paths = [f for f in findings if f.rule is Rule.PATH_SEPARATOR]
    unresolved = [f for f in findings if f.rule is Rule.UNRESOLVED]

    click.secho(f"Link check FAILED ({len(findings)} finding(s)):", fg="red", err=True)
    if paths:
        click.secho("\nLinks carrying a path (C-001):", fg="red", err=True)
        for finding in paths:
            click.secho(f"  - {finding.describe()}", fg="red", err=True)
    if unresolved:
        click.secho("\nLinks that do not resolve:", fg="red", err=True)
        for finding in unresolved:
            click.secho(f"  - {finding.describe()}", fg="red", err=True)

    click.secho(
        "\nFix the link by hand in src/pack/ — the build never edits it (C-002).",
        fg="red",
        err=True,
    )
    sys.exit(1)


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
