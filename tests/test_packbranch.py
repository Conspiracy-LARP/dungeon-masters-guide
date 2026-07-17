"""The pack branch tree: what consumers get when they attach the submodule.

These tests are about the **tree**, not the push. The tree is the contract — pushing is a
thin wrapper over `git push --force` and testing it would test git. What can actually
break here is the tree: a machinery file leaking in, the rename happening without the
rewrite, or `getting-started.md` being corrupted by a naive substring replace.

Most tests run against the temporary pack fixture (WP02's `conftest.py`) so that editing
the real guide cannot turn them red. The exceptions are the reproduction gate and the
consumer-path test, which are *about* the real repository and must hold against it.
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import replace
from pathlib import Path
from typing import Callable

import pytest

from build import packbranch
from build.roles import load_assets
from build.config import BuildConfig, load_config
from build.packbranch import (
    COMMIT_MESSAGE,
    REFERENCE_COMMIT,
    REFERENCE_INPUT_COMMIT,
    BuiltFile,
    PackBranchError,
    build_tree,
    check_publish_allowed,
    compare_against_ref,
    render_documents,
    verify_reproduction,
)
from build.roles import RoleError

#: Paths the branch must never carry. The exclusion list is the whole point of the
#: branch: creators asked for the markdown and none of the machinery.
FORBIDDEN_ENTRIES: tuple[str, ...] = ("src", "doc", ".github", "mkdocs.yml", "pyproject.toml")


@pytest.fixture
def tree_dir(tmp_path: Path) -> Path:
    return tmp_path / "packtree"


def _names(files: list[BuiltFile]) -> set[str]:
    return {f.published_name for f in files}


# --------------------------------------------------------------------------------------
# The rename, and both halves of it (T028).
# --------------------------------------------------------------------------------------


def test_bootstrap_is_published_as_agents_md(tree_dir: Path, pack_config: BuildConfig) -> None:
    """`start.md` is `AGENTS.md` on the branch — the name models look for (FR-010)."""
    build_tree(tree_dir, pack_config)

    assert (tree_dir / "AGENTS.md").is_file()


def test_start_md_does_not_exist_on_the_branch(tree_dir: Path, pack_config: BuildConfig) -> None:
    """It is a rename, not a copy. Both names present would be two bootstraps."""
    build_tree(tree_dir, pack_config)

    assert not (tree_dir / "start.md").exists()


def test_agents_md_carries_the_bootstrap_content(tree_dir: Path, pack_config: BuildConfig) -> None:
    """The rename moves the content, it does not invent a new file."""
    build_tree(tree_dir, pack_config)

    published = (tree_dir / "AGENTS.md").read_text(encoding="utf-8")
    assert "The bootstrap." in published


def test_references_to_the_bootstrap_are_rewritten(
    tree_dir: Path, pack_config: BuildConfig
) -> None:
    """The other half of the job: `README.md` must link to a file that exists here.

    Renaming without rewriting is the failure the contract warns about — a front door
    linking to `start.md`, which is not on this branch.
    """
    build_tree(tree_dir, pack_config)

    readme = (tree_dir / "README.md").read_text(encoding="utf-8")
    assert "](AGENTS.md)" in readme


def test_no_document_on_the_branch_references_start_md(
    tree_dir: Path, pack_config: BuildConfig
) -> None:
    """The invariant: every link resolves *on this branch* (FR-013)."""
    files = build_tree(tree_dir, pack_config)

    offenders = [
        built.published_name
        for built in files
        if "(start.md)" in built.content.decode("utf-8")
        or "`start.md`" in built.content.decode("utf-8")
    ]
    assert offenders == []


def test_rewrite_is_not_special_cased_to_readme(
    tree_dir: Path, pack_factory: Callable[..., BuildConfig]
) -> None:
    """A *new* document referencing the bootstrap is rewritten too.

    Today only `README.md` has such a reference. If the rewrite were special-cased to it,
    this would pass in production and ship a broken link the day someone adds the second
    reference — which is exactly the kind of latent break this branch cannot afford.
    """
    config = pack_factory(
        files={
            "creator-kit.md": "# Creator Kit\n\nSee [ethics.md](ethics.md).\n",
            "getting-started.md": "# Getting Started\n\nThe on-ramp.\n",
            "ethics.md": "# Ethics\n\nRead [start.md](start.md) first.\n",
            "README.md": "# The kit\n\n## The documents\n\n"
            "- **[`creator-kit.md`](creator-kit.md)** — the guide.\n"
            "- **[`getting-started.md`](getting-started.md)** — the on-ramp.\n"
            "- **[`ethics.md`](ethics.md)** — the floor.\n"
            "- **[`start.md`](start.md)** — the brief.\n",
            "start.md": "# Start here\n\nThe bootstrap.\n",
        }
    )
    build_tree(tree_dir, config)

    assert "](AGENTS.md)" in (tree_dir / "ethics.md").read_text(encoding="utf-8")


# --------------------------------------------------------------------------------------
# THE TRAP (T031).
# --------------------------------------------------------------------------------------


def test_getting_started_md_survives_the_rename(tree_dir: Path, pack_config: BuildConfig) -> None:
    """`getting-started.md` contains `start.md`. A naive replace corrupts it.

    WP02 tests this for the pure function; this asserts it at tree level, because the
    tree is what consumers get. `sed s/start.md/AGENTS.md/g` would rename this file to
    `getting-AGENTS.md` and no other test here would notice.
    """
    files = build_tree(tree_dir, pack_config)

    assert (tree_dir / "getting-started.md").is_file()
    assert "getting-AGENTS.md" not in _names(files)


def test_references_to_getting_started_are_left_alone(
    tree_dir: Path, pack_config: BuildConfig
) -> None:
    """The links *to* it must survive too, not merely the filename."""
    build_tree(tree_dir, pack_config)

    kit = (tree_dir / "creator-kit.md").read_text(encoding="utf-8")
    assert "](getting-started.md)" in kit
    assert "getting-AGENTS.md" not in kit


def test_no_file_on_the_branch_contains_the_corruption(
    tree_dir: Path, pack_config: BuildConfig
) -> None:
    """Belt and braces across the whole tree."""
    files = build_tree(tree_dir, pack_config)

    for built in files:
        assert "getting-AGENTS" not in built.content.decode("utf-8"), built.published_name


# --------------------------------------------------------------------------------------
# The exclusions (T027, T031).
# --------------------------------------------------------------------------------------


def test_the_tree_is_flat_markdown_only(tree_dir: Path, pack_config: BuildConfig) -> None:
    """Exactly the pack's `.md` files, flat. Nothing else (contract, Producer table)."""
    build_tree(tree_dir, pack_config)

    entries = sorted(p.name for p in tree_dir.iterdir())
    assert all(p.is_file() for p in tree_dir.iterdir())
    assert all(name.endswith(".md") for name in entries), entries


@pytest.mark.parametrize("forbidden", FORBIDDEN_ENTRIES)
def test_no_machinery_leaks_onto_the_branch(
    tree_dir: Path, pack_config: BuildConfig, forbidden: str
) -> None:
    """No `src/`, no `doc/`, no `.github/`, no `mkdocs.yml`, no build files."""
    build_tree(tree_dir, pack_config)

    assert not (tree_dir / forbidden).exists()


def test_the_file_list_comes_from_the_declaration_not_a_glob(
    tree_dir: Path, pack_factory: Callable[..., BuildConfig]
) -> None:
    """An undeclared document fails the branch build too (FR-011).

    A glob would mirror it silently, which is the drift the declaration exists to end:
    the file would reach consumers without ever being given a role.
    """
    config = pack_factory(
        files={
            "creator-kit.md": "# Creator Kit\n\nSee [ethics.md](ethics.md).\n",
            "getting-started.md": "# Getting Started\n\nThe on-ramp.\n",
            "ethics.md": "# Ethics\n\nThe floor.\n",
            "README.md": "# The kit\n",
            "start.md": "# Start here\n",
            "smuggled.md": "# Undeclared\n\nNobody gave me a role.\n",
        }
    )
    with pytest.raises(RoleError, match="smuggled.md"):
        build_tree(tree_dir, config)


def test_a_declared_document_is_not_silently_dropped(
    tree_dir: Path, pack_config: BuildConfig
) -> None:
    """Every declared document reaches the branch, under its published name."""
    files = render_documents(pack_config.pack_dir, pack_config)

    assert _names(files) == {
        "creator-kit.md",
        "getting-started.md",
        "ethics.md",
        "README.md",
        "AGENTS.md",
    }


# --------------------------------------------------------------------------------------
# Rebuilds and refusals.
# --------------------------------------------------------------------------------------


def test_rebuilding_into_the_same_directory_is_idempotent(
    tree_dir: Path, pack_config: BuildConfig
) -> None:
    """Same input, same tree — the property the force-push relies on."""
    first = build_tree(tree_dir, pack_config)
    first_bytes = {p.name: p.read_bytes() for p in tree_dir.iterdir()}

    second = build_tree(tree_dir, pack_config)
    second_bytes = {p.name: p.read_bytes() for p in tree_dir.iterdir()}

    assert _names(first) == _names(second)
    assert first_bytes == second_bytes


def test_a_stale_file_from_a_previous_build_is_cleared(
    tree_dir: Path, pack_config: BuildConfig
) -> None:
    """A document removed from the pack must not linger on the branch."""
    tree_dir.mkdir(parents=True)
    (tree_dir / "removed-last-week.md").write_text("# Gone\n", encoding="utf-8")

    build_tree(tree_dir, pack_config)

    assert not (tree_dir / "removed-last-week.md").exists()


def test_build_refuses_to_delete_an_unrecognised_directory(
    tree_dir: Path, pack_config: BuildConfig
) -> None:
    """`--out` is a path a human types; it must not become an rm -rf."""
    (tree_dir / "important").mkdir(parents=True)
    (tree_dir / "important" / "work.txt").write_text("not ours", encoding="utf-8")

    with pytest.raises(PackBranchError, match="did not create"):
        build_tree(tree_dir, pack_config)

    assert (tree_dir / "important" / "work.txt").is_file()


def test_two_documents_publishing_under_one_name_is_an_error(
    tree_dir: Path, pack_factory: Callable[..., BuildConfig]
) -> None:
    """An existing `AGENTS.md` in the pack would collide with the renamed bootstrap."""
    config = pack_factory(
        files={
            "creator-kit.md": "# Creator Kit\n",
            "getting-started.md": "# Getting Started\n",
            "ethics.md": "# Ethics\n",
            "README.md": "# The kit\n",
            "start.md": "# Start here\n",
            "AGENTS.md": "# Someone added this\n",
        },
        not_in_book=["README.md", "start.md", "AGENTS.md"],
    )
    with pytest.raises(PackBranchError, match="publish as"):
        render_documents(config.pack_dir, config)


# --------------------------------------------------------------------------------------
# The publish guard (T030).
# --------------------------------------------------------------------------------------


def test_publishing_from_a_laptop_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    """Not CI, no push. The branch force-pushes to every consumer that tracks it."""
    monkeypatch.delenv("CI", raising=False)
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)

    with pytest.raises(PackBranchError, match="not CI"):
        check_publish_allowed()


def test_publishing_from_ci_on_a_feature_branch_is_refused(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """CI is necessary but not sufficient: the branch mirrors `main`, only.

    The branch is created here rather than inherited from wherever the suite happens to
    run. The original relied on the ambient checkout ("a mission worktree, which is never
    `main`") — true on a laptop, false in CI, where the workflow checks out `main` and the
    guard then correctly allowed the publish. The test passed locally by accident and
    failed the moment it ran in the place it was written to describe.
    """
    subprocess.run(["git", "init", "-q", "-b", "not-main"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "commit", "-q", "--allow-empty", "-m", "x"],
        cwd=tmp_path,
        check=True,
        env={
            **os.environ,
            "GIT_AUTHOR_NAME": "t",
            "GIT_AUTHOR_EMAIL": "t@t",
            "GIT_COMMITTER_NAME": "t",
            "GIT_COMMITTER_EMAIL": "t@t",
        },
    )
    monkeypatch.setenv("CI", "true")
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)

    with pytest.raises(PackBranchError, match="Refusing to publish from"):
        check_publish_allowed(repo_root=tmp_path)


def test_the_commit_message_states_the_read_only_contract() -> None:
    """The rules must be readable by whoever is about to commit to the branch.

    They will lose that work at the next force-push, and this message is the only place
    they will find out why.
    """
    assert "generated and force-pushed" in COMMIT_MESSAGE
    assert "Do not commit to it directly" in COMMIT_MESSAGE
    assert "edit src/pack/ on main" in COMMIT_MESSAGE


# --------------------------------------------------------------------------------------
# The reproduction gate (T029, C-005) — against the real repository.
# --------------------------------------------------------------------------------------


def test_generated_tree_reproduces_the_hand_built_branch(
    real_repo_config: BuildConfig, repo_root: Path
) -> None:
    """C-005: the automation must reproduce `d024682` byte-for-byte before it takes over.

    The hand build was a real deployment to a real consumer — the `5g_arg` project's
    `doc/core` submodule points at this commit right now, and the guide already publishes
    the `submodule add` command to readers. A mismatch means either the hand build or the
    automation is wrong, and force-pushing before knowing which makes the guide lie to
    people who followed its published instructions (R-002).

    **Rendered from `39c2452`'s pack, not today's.** This test used to render from the
    live `src/pack/`, which made it assert that the guide's prose never changes: adding
    `premise.md` and rewriting the bootstrap turned it red, though the automation was
    entirely correct and the hand build was untouched. Editing the pack is the job — a
    gate that fires on it is a gate that gets re-baselined until it means nothing.

    Holding the inputs at the commit the hand build was rendered from makes this the claim
    C-005 asked for: *the generator* reproduces the hand build. It reds when the generator
    changes what it would ship to that submodule, and at no other time.
    """
    result = verify_reproduction(
        real_repo_config,
        ref=REFERENCE_COMMIT,
        input_ref=REFERENCE_INPUT_COMMIT,
        repo_root=repo_root,
    )

    assert result.matches, result.describe()


def test_the_reproduction_gate_is_not_coupled_to_live_pack_content(
    real_repo_config: BuildConfig, repo_root: Path, tmp_path: Path
) -> None:
    """The gate must survive an edit to the guide — the defect above, pinned open.

    Renders the reproduction with the live pack replaced by a mutilated copy. If the gate
    still consults `src/pack/` for any part of its answer, this reds; if it truly reads
    its inputs from `REFERENCE_INPUT_COMMIT`, the edit is invisible to it.
    """
    decoy = tmp_path / "decoy-pack"
    decoy.mkdir()
    (decoy / "wildly-undeclared.md").write_text("# Not in any declaration\n", encoding="utf-8")

    result = verify_reproduction(
        replace(real_repo_config, pack_dir=decoy),
        ref=REFERENCE_COMMIT,
        input_ref=REFERENCE_INPUT_COMMIT,
        repo_root=repo_root,
    )

    assert result.matches, (
        "The reproduction gate changed its answer when the live pack changed. It is "
        "still reading today's content instead of the hand build's inputs.\n" + result.describe()
    )


def test_the_reproduction_gate_reds_when_the_generator_changes(
    real_repo_config: BuildConfig, repo_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The gate must be able to fail — a repro gate that cannot fire is worse than none.

    Breaks the half of the rename that the hand build proved (FR-010: rename *and*
    rewrite) and asserts the gate notices. Without this, decoupling the gate from live
    content could quietly have decoupled it from everything.
    """
    monkeypatch.setattr(packbranch, "rewrite_references", lambda text: text)

    result = verify_reproduction(
        real_repo_config,
        ref=REFERENCE_COMMIT,
        input_ref=REFERENCE_INPUT_COMMIT,
        repo_root=repo_root,
    )

    assert not result.matches, (
        "The generator was mutated to skip the reference rewrite and the reproduction "
        "gate stayed green. The gate is not testing the generator."
    )
    assert "Do NOT force-push" in result.describe()


def test_every_consumer_path_from_the_contract_exists(
    tmp_path: Path, real_repo_config: BuildConfig
) -> None:
    """`doc/core/AGENTS.md`, `doc/core/creator-kit.md` and friends — the published promise."""
    out_dir = tmp_path / "real"
    build_tree(out_dir, real_repo_config)

    for promised in ("AGENTS.md", "README.md", "creator-kit.md", "getting-started.md", "ethics.md"):
        assert (out_dir / promised).is_file(), promised


def test_the_real_pack_is_never_written_to(tmp_path: Path, real_repo_config: BuildConfig) -> None:
    """C-002/C-006: the build reads the guide; it never edits it."""
    pack_dir = real_repo_config.pack_dir
    before = {p.name: p.read_bytes() for p in sorted(pack_dir.glob("*.md"))}

    build_tree(tmp_path / "out", real_repo_config)

    after = {p.name: p.read_bytes() for p in sorted(pack_dir.glob("*.md"))}
    assert before == after


def test_pack_assets_reach_the_branch_byte_for_byte(tmp_path: Path) -> None:
    """An asset the prose references must exist on the branch, unchanged.

    The trap this guards: `render_documents` derives its file list from the role
    declaration, which globs `*.md`. An asset is invisible to that glob, so the natural
    failure is a branch of markdown pointing at images that are not there — and consumers
    track this branch as a submodule, so the breakage lands in *their* checkout while our
    CI stays green. Asserted on the materialised tree rather than the returned list,
    because the bytes on disk are what a consumer gets.
    """
    config = load_config()
    assets = load_assets(config.pack_dir)
    assert assets, "guard the guard: no assets in the pack, so this proves nothing"

    files = build_tree(tmp_path, config)
    published = {built.published_name for built in files}

    for name in assets:
        assert name in published, f"{name} never reached the branch"
        assert (tmp_path / name).read_bytes() == (
            config.pack_dir / name
        ).read_bytes(), (
            f"{name} was altered on the way to the branch; an asset's bytes are the artifact"
        )
